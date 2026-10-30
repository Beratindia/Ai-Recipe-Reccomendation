"""LLM layer. To use a different provider, only change `call_llm`."""
import json
import os
import re
from dataclasses import dataclass, field

from pydantic import ValidationError

from .goals import EXCLUSIONS, GOALS
from .schema import Recipe

SYSTEM_PROMPT = """You are a professional chef and nutrition-aware recipe developer specialising in
Indonesian and international cuisine. Create recipes from the user's available ingredients and needs.

Rules:
- Respond with a single JSON object only. No markdown, no commentary.
- Use mostly the ingredients provided; you may add common pantry staples (oil, salt, sugar, spices, water).
- Every ingredient needs "quantity_g": its total weight in grams for the whole recipe
  (estimate liquids as 1 ml = 1 g; estimate whole items, e.g. 1 egg = 50 g).
- "display_quantity" is a friendly measure that starts with a number, e.g. "2 butir" or "1 sdm".
- Write ingredient names in simple, common form (e.g. "bawang merah", "ayam", "telur").
- Steps must be clear, ordered and complete. Put cooking durations in the step text
  (e.g. "masak 10 menit" / "cook for 10 minutes") so timers can be built from them.
- Respect every dietary restriction strictly. Never use an excluded ingredient.
- Do NOT include nutrition values; they are calculated separately.
- Recipes in one response must be clearly different dishes.

JSON shape:
{
  "recipes": [
    {
      "title": str,
      "cuisine": str,
      "servings": int,
      "cook_time_minutes": int,
      "difficulty": "Easy" | "Medium" | "Hard",
      "description": str (one appetising sentence),
      "tags": [str] (2-3 short tags, e.g. "High-Protein", "Air-Fryer Friendly"),
      "slot": str or null (meal slot if one was requested),
      "ingredients": [{"name": str, "quantity_g": number, "display_quantity": str}],
      "steps": [str]
    }
  ]
}"""


@dataclass
class GenerationRequest:
    ingredients: list[str]
    cuisine: str = "Indonesian"
    servings: int = 2
    preferences: str = ""
    exclusions: list[str] = field(default_factory=list)
    equipment: list[str] = field(default_factory=list)
    max_minutes: int | None = None
    target_kcal: int | None = None      # per serving
    tolerance_kcal: int = 50
    protein_g: int | None = None        # per serving
    diet_name: str = ""
    diet_notes: str = ""
    goal: str = ""
    condition_rules: str = ""
    slots: list[tuple[str, int]] = field(default_factory=list)   # (slot name, kcal per serving)


def build_user_prompt(req: GenerationRequest, n: int = 1) -> str:
    lines = [
        f"Number of recipes: {n}",
        f"Cuisine: {req.cuisine}",
        f"Servings: {req.servings}",
        f"Available ingredients: {', '.join(req.ingredients) if req.ingredients else 'any common ingredients'}",
        f"Preferences / restrictions: {req.preferences or 'none'}",
    ]
    if req.exclusions:
        rules = " ".join(EXCLUSIONS[e].prompt for e in req.exclusions if e in EXCLUSIONS)
        lines.append(f"Dietary exclusions (strict): {', '.join(req.exclusions)}. {rules}")
    if req.equipment:
        lines.append(f"Available equipment (use only these): {', '.join(req.equipment)}")
    if req.max_minutes:
        lines.append(f"Maximum total cooking time: {req.max_minutes} minutes")
    if req.diet_name:
        lines.append(f"Diet style: {req.diet_name}. {req.diet_notes}")
    if req.goal in GOALS:
        lines.append(f"Goal: {req.goal}. {GOALS[req.goal]}")
    if req.slots:
        slot_text = "; ".join(f"{name} about {kcal} kcal per serving" for name, kcal in req.slots)
        lines.append(f"Meal slots (one recipe per slot, set \"slot\" to the slot name): {slot_text}")
    elif req.target_kcal:
        lines.append(
            f"Calorie target: about {req.target_kcal} kcal per serving (within +/-{req.tolerance_kcal}); "
            "choose ingredient weights so the dish actually lands near this."
        )
    if req.protein_g:
        lines.append(f"Protein target: at least {req.protein_g} g per serving.")
    if req.condition_rules:
        lines.append(f"Special food needs: {req.condition_rules}")
    lines.append(
        "Write titles and steps in the same language as the ingredients list "
        "(Indonesian if it is Indonesian, otherwise English)."
    )
    return "\n".join(lines)


def get_api_key() -> str | None:
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def call_llm(system: str, user: str) -> str:
    """Send a prompt, return raw text. Swap this function for another provider."""
    from google import genai

    client = genai.Client()  # reads GEMINI_API_KEY from the environment
    interaction = client.interactions.create(
        model=os.getenv("LLM_MODEL", "gemini-3.8-flash"),
        input=f"{system}\n\n{user}",
    )
    return interaction.output_text


def extract_json(text: str) -> dict:
    """Pull a JSON object out of the reply, tolerating code fences or stray text."""
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON object found in model output")
        text = text[start : end + 1]
    return json.loads(text)


def parse_recipes(raw: str) -> tuple[list[Recipe], list[str]]:
    """Validate every recipe in the reply. Returns (valid recipes, error messages)."""
    data = extract_json(raw)
    items = data["recipes"] if isinstance(data.get("recipes"), list) else [data]
    recipes, errors = [], []
    for item in items:
        try:
            recipes.append(Recipe.model_validate(item))
        except ValidationError as e:
            errors.append(str(e)[:300])
    return recipes, errors


def generate_recipes(req: GenerationRequest, n: int = 3, llm=call_llm, max_attempts: int = 2) -> list[Recipe]:
    """Call the LLM, validate the structure, retry once with the error if nothing valid came back."""
    user = build_user_prompt(req, n)
    last_error = None
    for _ in range(max_attempts):
        prompt = user if last_error is None else (
            f"{user}\n\nYour previous reply was invalid: {last_error}\nReturn corrected JSON only."
        )
        raw = llm(SYSTEM_PROMPT, prompt)
        try:
            recipes, errors = parse_recipes(raw)
        except (ValueError, KeyError) as e:
            last_error = str(e)[:500]
            continue
        if recipes:
            return recipes
        last_error = "; ".join(errors)[:500] or "no recipes returned"
    raise RuntimeError(f"Could not get a valid recipe after {max_attempts} attempts: {last_error}")


def generate_recipe(
    ingredients: str,
    preferences: str,
    cuisine: str,
    servings: int,
    llm=call_llm,
    max_attempts: int = 2,
) -> Recipe:
    """Single-recipe convenience wrapper (comma-separated ingredient text)."""
    req = GenerationRequest(
        ingredients=[i.strip() for i in ingredients.split(",") if i.strip()],
        cuisine=cuisine, servings=servings, preferences=preferences,
    )
    return generate_recipes(req, n=1, llm=llm, max_attempts=max_attempts)[0]
