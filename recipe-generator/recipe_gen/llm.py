"""LLM layer. To use a different provider, only change `call_llm`."""
import json
import os
import re

from pydantic import ValidationError

from .schema import Recipe

SYSTEM_PROMPT = """You are a professional chef specialising in Indonesian and international cuisine.
Create ONE recipe from the user's available ingredients and preferences.

Rules:
- Respond with a single JSON object only. No markdown, no commentary.
- Use mostly the ingredients provided; you may add common pantry staples (oil, salt, sugar, spices, water).
- Every ingredient needs "quantity_g": its total weight in grams for the whole recipe
  (estimate liquids as 1 ml = 1 g; estimate whole items, e.g. 1 egg = 50 g).
- "display_quantity" is a friendly measure, e.g. "2 butir" or "1 sdm".
- Write ingredient names in simple, common form (e.g. "bawang merah", "ayam", "telur").
- Steps must be clear, ordered, and complete.
- Do NOT include nutrition values; they are calculated separately.

JSON shape:
{
  "title": str,
  "cuisine": str,
  "servings": int,
  "cook_time_minutes": int,
  "ingredients": [{"name": str, "quantity_g": number, "display_quantity": str}],
  "steps": [str]
}"""


def build_user_prompt(ingredients: str, preferences: str, cuisine: str, servings: int) -> str:
    return (
        f"Cuisine: {cuisine}\n"
        f"Servings: {servings}\n"
        f"Available ingredients: {ingredients}\n"
        f"Preferences / restrictions: {preferences or 'none'}\n"
        "Write the recipe title and steps in the same language as the ingredients list "
        "(Indonesian if it is Indonesian, otherwise English)."
    )


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


def generate_recipe(
    ingredients: str,
    preferences: str,
    cuisine: str,
    servings: int,
    llm=call_llm,
    max_attempts: int = 2,
) -> Recipe:
    """Call the LLM, validate the structure, retry once with the error if invalid."""
    user = build_user_prompt(ingredients, preferences, cuisine, servings)
    last_error = None
    for _ in range(max_attempts):
        prompt = user if last_error is None else (
            f"{user}\n\nYour previous reply was invalid: {last_error}\nReturn corrected JSON only."
        )
        raw = llm(SYSTEM_PROMPT, prompt)
        try:
            return Recipe.model_validate(extract_json(raw))
        except (ValueError, ValidationError) as e:
            last_error = str(e)[:500]
    raise RuntimeError(f"Could not get a valid recipe after {max_attempts} attempts: {last_error}")
