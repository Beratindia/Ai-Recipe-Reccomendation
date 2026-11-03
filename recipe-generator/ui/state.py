"""Session state, goal snapshot and the generation pipeline shared by all pages."""
import os
import re
from dataclasses import dataclass

import streamlit as st

from recipe_gen import analysis
from recipe_gen.analysis import Analyzed, clean_item
from recipe_gen.demo import demo_llm
from recipe_gen.goals import DIET_PRESETS, EXCLUSIONS, blocked_by_keywords, macro_grams, next_meal_target, violations
from recipe_gen import persist
from recipe_gen.goals import SLOT_SHARES
from recipe_gen.llm import GenerationRequest, call_llm, generate_recipes, get_api_key
from recipe_gen.nutrition import NutritionCalculator, load_food_db
from recipe_gen.schema import Recipe
from recipe_gen.wellness import CONDITIONS

from .i18n import llm_language, t

PAGES = [("Pantry", ":material/kitchen:"), ("Goals", ":material/target:"), ("Recipes", ":material/restaurant_menu:"),
         ("Cook", ":material/skillet:"), ("Plan", ":material/calendar_month:"), ("Recovery", ":material/health_and_safety:")]
PREP_OPTIONS = {"Under 15 min": 15, "15-30 min": 30, "30-45 min": 45, "Any": None}
EQUIPMENT = ["Stovetop", "Air Fryer", "Oven", "Rice Cooker", "Blender", "Steamer", "Microwave"]
SORTS = ["Best match", "Highest protein", "Lowest calories", "Closest to target"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# widget keys whose values must survive switching pages (Streamlit drops widgets that are not rendered)
PERSIST = ["cuisine", "servings", "prefs", "equipment", "prep_time", "diet", "p_pct", "c_pct", "f_pct",
           "daily_kcal", "meals_pd", "target_mode", "custom_kcal", "tolerance", "goal", "exclusions",
           "condition", "plan_day", "sort_by", "cat", "quick_filters", "custom_condition", "lang"]

DEFAULTS = {
    "page": "Pantry", "pantry": [], "cuisine": "Indonesian", "servings": 2, "prefs": "",
    "equipment": ["Stovetop"], "prep_time": "Any", "diet": "Balanced", "p_pct": 25, "c_pct": 50, "f_pct": 25,
    "daily_kcal": 2000, "meals_pd": 3, "target_mode": "From daily budget", "custom_kcal": 500, "tolerance": 50,
    "goal": "Maintenance", "exclusions": [], "condition": "Flu & Cold", "plan_day": "Mon", "sort_by": "Best match",
    "cat": "Proteins", "recipes": [], "removed_notes": [], "current": None, "cook_servings": None,
    "cook_step": 0, "saved": [], "plan": {}, "recipe_context": "", "gen_error": "", "log": [],
    "quick_filters": [], "custom_condition": "", "plan_notes": [], "recovery_meals": [],
    "recovery_notes": [], "recovery_for": "", "lang": "English",
}

SUGGESTIONS = {
    "Proteins": ["ayam", "telur", "tahu", "tempe", "ikan tongkol", "udang", "daging sapi", "ikan bandeng"],
    "Veggies & Greens": ["bayam", "kangkung", "wortel", "tomat", "buncis", "kubis", "terong", "sawi"],
    "Carbs": ["nasi", "beras", "kentang", "mie", "jagung", "bihun"],
    "Aromatics": ["bawang merah", "bawang putih", "cabai merah", "jahe", "kunyit", "lengkuas", "kemiri"],
}


def init_state() -> None:
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v if not isinstance(v, (list, dict)) else type(v)(v)
    # re-assign so widget values are not garbage-collected when their page is not shown
    for k in PERSIST:
        if k in st.session_state:
            st.session_state[k] = st.session_state[k]
    try:  # Streamlit Cloud secrets -> env var, so the LLM layer finds the key
        for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            if key not in os.environ and key in st.secrets:
                os.environ[key] = st.secrets[key]
    except Exception:
        pass


def go(page: str) -> None:
    st.session_state.page = page


@st.cache_resource
def get_calc() -> NutritionCalculator:
    return NutritionCalculator(load_food_db())


def is_demo() -> bool:
    return not get_api_key()


def get_llm():
    return demo_llm if is_demo() else call_llm


# ------------------------------------------------------------------ pantry

def _title(name: str) -> str:
    return name[:1].upper() + name[1:]


def add_pantry(text: str) -> int:
    added = 0
    for part in re.split(r"[,\n;]+", text):
        part = part.strip()
        if not part:
            continue
        name = clean_item(part) or part.lower()
        qty_match = re.search(r"\d+(?:[.,/]\d+)?\s*[a-zA-Z]*", part)
        qty = qty_match.group(0).strip() if qty_match else ""
        if any(i["name"] == name for i in st.session_state.pantry):
            continue
        st.session_state.pantry.append({"name": name, "qty": qty})
        added += 1
    return added


def remove_pantry(name: str) -> None:
    st.session_state.pantry = [i for i in st.session_state.pantry if i["name"] != name]


def pantry_names() -> list[str]:
    return [i["name"] for i in st.session_state.pantry]


# ------------------------------------------------------------------- goals

@dataclass
class Goals:
    diet: str
    p: int
    c: int
    f: int
    daily_kcal: int
    meals: int
    mode: str
    custom_kcal: int
    tolerance: int
    goal: str
    exclusions: list[str]

    @property
    def meal_kcal(self) -> int:
        return next_meal_target(self.daily_kcal, self.meals)

    @property
    def target_kcal(self) -> int | None:
        if self.mode == "Off":
            return None
        return self.meal_kcal if self.mode == "From daily budget" else self.custom_kcal

    @property
    def macros(self) -> dict[str, int]:
        return macro_grams(self.target_kcal or self.meal_kcal, self.p, self.c, self.f)


def diet_name(p: int, c: int, f: int) -> str:
    for name, (pp, cc, ff, _, _) in DIET_PRESETS.items():
        if (pp, cc, ff) == (p, c, f):
            return name
    return "Custom"


def get_goals() -> Goals:
    s = st.session_state
    return Goals(diet_name(s.p_pct, s.c_pct, s.f_pct), s.p_pct, s.c_pct, s.f_pct, s.daily_kcal, s.meals_pd, s.target_mode, s.custom_kcal,
                 s.tolerance, s.goal, list(s.exclusions))


def apply_preset(name: str) -> None:
    p, c, f, _, _ = DIET_PRESETS[name]
    st.session_state.update(diet=name, p_pct=p, c_pct=c, f_pct=f)


# -------------------------------------------------------------- generation

def build_request(*, servings: int | None = None, slots: list[tuple[str, int]] | None = None,
                  condition: str | None = None) -> GenerationRequest:
    s, g = st.session_state, get_goals()
    cond = CONDITIONS.get(condition) if condition else None
    custom_rules = ""
    if condition and cond is None:  # free-text need typed by the user
        custom_rules = (f"The person wants food suited for: {condition}. Keep it mild, simple and low-risk, "
                        "with common ingredients. Do not make medical claims.")
    macros = g.macros
    base_notes = DIET_PRESETS[g.diet][4] if g.diet in DIET_PRESETS else "Custom macro split."
    diet_notes = (f"{base_notes} Approximate split per serving: {g.p}% protein / {g.c}% carbs / {g.f}% fat "
                  f"(about {macros['protein_g']} g protein, {macros['carbs_g']} g carbs, {macros['fat_g']} g fat).")
    return GenerationRequest(
        ingredients=pantry_names(), cuisine=s.cuisine, servings=servings or s.servings, preferences=s.prefs,
        exclusions=g.exclusions, equipment=list(s.equipment), max_minutes=PREP_OPTIONS.get(s.prep_time),
        target_kcal=None if slots else g.target_kcal, tolerance_kcal=g.tolerance,
        protein_g=None if slots or not g.target_kcal else round(macros["protein_g"] * 0.9),
        diet_name=g.diet, diet_notes=diet_notes, goal=g.goal, slots=slots or [],
        condition_rules=cond.prompt_rules if cond else custom_rules, language=llm_language(),
    )


def generate(*, n: int = 3, servings: int | None = None, slots: list[tuple[str, int]] | None = None,
             condition: str | None = None) -> tuple[list[Recipe], list[str]]:
    """Run the LLM, then drop recipes that break an exclusion. Returns (kept, notes about removed ones)."""
    g = st.session_state
    req = build_request(servings=servings, slots=slots, condition=condition)
    recipes = generate_recipes(req, n=n, llm=get_llm())
    cond = CONDITIONS.get(condition) if condition else None
    kept, notes = [], []
    for r in recipes:
        names = [i.name for i in r.ingredients]
        bad = violations(names, req.exclusions)
        if cond and cond.blocked_keywords:
            bad += [f"{cond.name}: {x}" for x in blocked_by_keywords(names, cond.blocked_keywords)]
        if bad:
            why = ", ".join(t(b.split(": ", 1)[0]) + (": " + b.split(": ", 1)[1] if ": " in b else "") for b in bad[:3])
            notes.append(t("Removed “{title}”: {why}", title=r.title, why=why))
        else:
            kept.append(r)
    return kept, notes


def analyzed(recipe: Recipe, target: int | None = None) -> Analyzed:
    return analysis.analyze(recipe, get_calc(), pantry_names(), target if target is not None else get_goals().target_kcal)


def generate_for_recipes(condition: str | None = None) -> bool:
    """Generate a fresh batch for the Recipes page. Returns True if the page should switch."""
    s = st.session_state
    if not s.pantry:
        st.toast(t("Add at least one ingredient to your pantry first."))
        return False
    try:
        with st.spinner(t("Your AI chef is cooking up ideas...")):
            kept, notes = generate(condition=condition)
    except Exception as e:  # network, quota, bad key, invalid JSON twice...
        st.error(t("Could not generate recipes: {e}", e=e))
        return False
    s.recipes, s.removed_notes, s.recipe_context, s.page = kept, notes, condition or "", "Recipes"
    return True


def open_recipe(recipe: Recipe) -> None:
    s = st.session_state
    s.current, s.cook_servings, s.cook_step, s.page = recipe, recipe.servings, 0, "Cook"


def save_recipe(recipe: Recipe) -> None:
    if all(r.title != recipe.title for r in st.session_state.saved):
        st.session_state.saved.append(recipe)


# --------------------------------------------------------------- daily log

def log_meal(recipe: Recipe, ps: dict) -> None:
    st.session_state.log.append({
        "date": persist.today(), "title": recipe.title, "kcal": ps["kcal"], "protein_g": ps["protein_g"],
        "carbs_g": ps["carbs_g"], "fat_g": ps["fat_g"],
    })


def today_log() -> list[dict]:
    d = persist.today()
    return [e for e in st.session_state.log if e.get("date") == d]


def today_totals() -> dict:
    keys = ("kcal", "protein_g", "carbs_g", "fat_g")
    return {k: round(sum(e.get(k, 0) for e in today_log()), 1) for k in keys}


# ----------------------------------------------------------------- meal plan

def slot_targets() -> list[tuple[str, int]]:
    d = get_goals().daily_kcal
    return [(name, int(round(d * share / 10) * 10)) for name, share in SLOT_SHARES.items()]


def plan_day(day: str) -> dict:
    return st.session_state.plan.setdefault(day, {})


def fill_day(day: str, only_slot: str | None = None) -> list[str]:
    """Generate recipes for the empty (non-accepted) slots of a day. Returns notes about removed recipes."""
    targets = [(n, k) for n, k in slot_targets() if (only_slot is None or n == only_slot)]
    entries = plan_day(day)
    if only_slot is None:
        targets = [(n, k) for n, k in targets if not entries.get(n, {}).get("accepted")]
    if not targets:
        return []
    kept, notes = generate(n=len(targets), servings=1, slots=targets)
    by_slot = {r.slot: r for r in kept if r.slot}
    leftovers = [r for r in kept if r.slot not in dict(targets)]
    for name, _ in targets:
        r = by_slot.get(name) or (leftovers.pop(0) if leftovers else None)
        if r is not None:
            entries[name] = {"recipe": r.model_copy(update={"slot": name}), "accepted": False}
    return notes


def day_totals(day: str) -> dict:
    keys = ("kcal", "protein_g", "carbs_g", "fat_g")
    tot = dict.fromkeys(keys, 0.0)
    for e in st.session_state.plan.get(day, {}).values():
        ps = analyzed(e["recipe"], 0).per_serving
        for k in keys:
            tot[k] += ps[k]
    return {k: round(v) for k, v in tot.items()}


def plan_recipes() -> list[Recipe]:
    return [e["recipe"] for day in DAYS for e in st.session_state.plan.get(day, {}).values()]


# --------------------------------------------------------------- save / load

def export_data() -> str:
    s = st.session_state
    return persist.dump({"pantry": s.pantry, "saved": s.saved, "plan": s.plan, "log": s.log,
                         "settings": {k: s[k] for k in PERSIST if k in s}})


def import_data(text: str) -> None:
    data = persist.load(text)
    s = st.session_state
    s.pantry, s.saved, s.plan, s.log = data["pantry"], data["saved"], data["plan"], data["log"]
    for k, v in data["settings"].items():
        if k in PERSIST and k in DEFAULTS and type(v) is type(DEFAULTS[k]):
            s[k] = v
