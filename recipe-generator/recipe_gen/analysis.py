"""Pure helpers around recipes: pantry matching, scaling, calorie adjustment, grocery list."""
import re
from dataclasses import dataclass, field

from .nutrition import NutritionCalculator, NutritionResult, normalize
from .schema import Ingredient, Recipe

# assumed to be in every kitchen: not counted as "missing" and left out of grocery lists
STAPLES = {
    "garam", "salt", "air", "water", "minyak", "minyak goreng", "oil", "cooking oil", "vegetable oil",
    "gula", "gula pasir", "sugar", "merica", "lada", "pepper", "black pepper", "merica bubuk",
    "lada bubuk", "kaldu bubuk", "penyedap", "penyedap rasa", "air matang", "air panas", "es batu",
}

_UNIT_WORDS = (
    r"gram|gr|g|kg|kilo|ons|mg|ml|l|liter|buah|butir|siung|batang|lembar|ikat|bungkus|sdm|sdt|"
    r"ekor|potong|biji|cup|cups|pcs|piece|pieces|tbsp|tsp|oz|lb|left|sisa"
)


def clean_item(text: str) -> str:
    """'Chicken Breast 500g' -> 'chicken breast'; '2 ripe avocado' -> 'ripe avocado'."""
    t = text.lower()
    t = re.sub(r"\([^)]*\)", " ", t)
    t = re.sub(r"\b\d+([.,/]\d+)?\s*(" + _UNIT_WORDS + r")?\b", " ", t)
    t = re.sub(r"[^a-z\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _words_contain(hay: str, needle: str) -> bool:
    return bool(needle) and f" {needle} " in f" {hay} "


def is_staple(name: str) -> bool:
    return normalize(name) in STAPLES


def ingredient_in_pantry(name: str, pantry: list[str], calc: NutritionCalculator | None) -> bool:
    key = clean_item(name)
    if not key:
        return False
    idx = calc.match(key) if calc else None
    for item in pantry:
        p = clean_item(item)
        if not p:
            continue
        if p == key or _words_contain(key, p) or _words_contain(p, key):
            return True
        if calc and idx is not None and calc.match(p) == idx:
            return True
    return False


@dataclass
class PantryMatch:
    percent: int
    have: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)


def pantry_match(recipe: Recipe, pantry: list[str], calc: NutritionCalculator | None = None) -> PantryMatch:
    have, missing = [], []
    for ing in recipe.ingredients:
        if is_staple(ing.name):
            continue
        (have if ingredient_in_pantry(ing.name, pantry, calc) else missing).append(ing.name)
    total = len(have) + len(missing)
    percent = round(100 * len(have) / total) if total else 100
    return PantryMatch(percent, have, missing)


@dataclass
class Analyzed:
    recipe: Recipe
    nutrition: NutritionResult
    match: PantryMatch
    target_kcal: int | None = None

    @property
    def per_serving(self) -> dict:
        return self.nutrition.per_serving

    @property
    def kcal(self) -> float:
        return self.per_serving["kcal"]

    @property
    def delta(self) -> float | None:
        return None if self.target_kcal is None else round(self.kcal - self.target_kcal)

    @property
    def accuracy(self) -> int | None:
        if not self.target_kcal:
            return None
        return max(0, round(100 - abs(self.kcal - self.target_kcal) / self.target_kcal * 100))

    @property
    def coverage(self) -> int:
        """% of ingredient weight (excluding water) found in the food table."""
        rows = self.nutrition.per_ingredient
        rows = rows[rows["matched_to"] != "Water"]
        total = rows["grams"].sum()
        if not total:
            return 100
        return round(100 * rows.loc[rows["matched_to"].notna(), "grams"].sum() / total)


def analyze(recipe: Recipe, calc: NutritionCalculator, pantry: list[str], target_kcal: int | None = None) -> Analyzed:
    return Analyzed(recipe, calc.calculate(recipe), pantry_match(recipe, pantry, calc), target_kcal)


# ---------------------------------------------------------------- scaling

_NUM = re.compile(r"(\d+\s+\d+/\d+|\d+/\d+|\d+(?:[.,]\d+)?)")


def _to_float(token: str) -> float:
    token = token.replace(",", ".").strip()
    if " " in token:
        whole, frac = token.split(None, 1)
        a, b = frac.split("/")
        return int(whole) + int(a) / int(b)
    if "/" in token:
        a, b = token.split("/")
        return int(a) / int(b)
    return float(token)


def fmt_num(x: float) -> str:
    if abs(x - round(x)) < 0.05:
        return str(int(round(x)))
    return f"{x:.1f}".rstrip("0").rstrip(".") if x >= 1 else f"{x:.2f}".rstrip("0").rstrip(".")


def scale_display(text: str, factor: float) -> str:
    """Scale the first number in a human quantity: '2 butir' x1.5 -> '3 butir'."""
    m = _NUM.search(text or "")
    if not m or abs(factor - 1) < 1e-9:
        return text
    return text[: m.start()] + fmt_num(_to_float(m.group(1)) * factor) + text[m.end():]


def scale_recipe(recipe: Recipe, servings: int) -> Recipe:
    if servings == recipe.servings:
        return recipe
    f = servings / recipe.servings
    ings = [
        Ingredient(name=i.name, quantity_g=round(i.quantity_g * f, 1), display_quantity=scale_display(i.display_quantity, f))
        for i in recipe.ingredients
    ]
    return recipe.model_copy(update={"servings": servings, "ingredients": ings})


# ------------------------------------------------- calorie micro-adjustment

@dataclass
class Adjustment:
    ingredient: str
    old_g: float
    new_g: float
    kcal_change_per_serving: float
    new_kcal_per_serving: float

    @property
    def verb(self) -> str:
        return "Reduce" if self.new_g < self.old_g else "Add"


def suggest_adjustment(recipe: Recipe, nutrition: NutritionResult, target_kcal: int,
                       tolerance: int = 0) -> Adjustment | None:
    """Change the weight of one calorie-dense ingredient (oil, sugar, coconut milk...) so the recipe lands on
    the target. Bounded to 40%-200% of the original amount so the dish stays sensible, which means a large
    gap is only partly closed."""
    per_ing = nutrition.per_ingredient
    cur = nutrition.per_serving["kcal"]
    need_total = (target_kcal - cur) * recipe.servings
    if abs(target_kcal - cur) <= tolerance or not len(per_ing):
        return None
    best = None
    for ing, (_, row) in zip(recipe.ingredients, per_ing.iterrows()):
        kcal = row["kcal"]
        if kcal is None or kcal != kcal or ing.quantity_g <= 0 or row["matched_to"] in (None, "Water"):
            continue
        density = kcal / ing.quantity_g  # kcal per gram
        if density < 3.0:  # only oils, sugar, coconut milk, nuts, dry staples: never the main protein
            continue
        # prefer the ingredient that can absorb the change with the smallest relative move
        rel = abs(need_total / density) / ing.quantity_g
        if best is None or rel < best[0]:
            best = (rel, ing, density)
    if best is None:
        return None
    _, ing, density = best
    new_g = min(max(ing.quantity_g + need_total / density, ing.quantity_g * 0.4), ing.quantity_g * 2.0)
    new_g = round(new_g * 2) / 2  # nearest half gram
    change_total = (new_g - ing.quantity_g) * density
    if abs(change_total) < 1:
        return None
    return Adjustment(ing.name, ing.quantity_g, new_g, change_total / recipe.servings,
                      cur + change_total / recipe.servings)


def apply_adjustment(recipe: Recipe, adj: Adjustment) -> Recipe:
    ings = []
    for i in recipe.ingredients:
        if i.name == adj.ingredient:
            f = adj.new_g / i.quantity_g
            i = Ingredient(name=i.name, quantity_g=adj.new_g, display_quantity=scale_display(i.display_quantity, f) or f"{adj.new_g:g} g")
        ings.append(i)
    return recipe.model_copy(update={"ingredients": ings})


# ------------------------------------------------------------ grocery list

def grocery_list(recipes: list[Recipe], pantry: list[str], calc: NutritionCalculator | None = None) -> list[tuple[str, float]]:
    """Ingredients across recipes that are not in the pantry (staples excluded), totalled in grams."""
    totals: dict[str, list] = {}
    for r in recipes:
        for ing in r.ingredients:
            if is_staple(ing.name) or ingredient_in_pantry(ing.name, pantry, calc):
                continue
            key = clean_item(ing.name) or ing.name.lower()
            entry = totals.setdefault(key, [ing.name, 0.0])
            entry[1] += ing.quantity_g
    return sorted(((n, round(g)) for n, g in totals.values()), key=lambda x: x[0])


# --------------------------------------------------------------- cooking

_MIN = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:[-–]\s*(\d+(?:[.,]\d+)?)\s*)?(menit|mnt|minutes?|mins?|jam|hours?|hrs?)\b", re.I)


def step_minutes(step: str) -> int | None:
    """Longest duration mentioned in a step, in minutes (None if there is none)."""
    best = None
    for low, high, unit in _MIN.findall(step):
        v = float((high or low).replace(",", "."))  # "2-3 menit" -> use the upper end
        if unit.lower().startswith(("jam", "hour", "hr")):
            v *= 60
        best = max(best or 0, v)
    return int(round(best)) if best else None


_TEXT_LABELS = {
    "en": ("servings", "min", "Ingredients", "Steps", "Per serving (estimate)", "protein", "carbs", "fat"),
    "id": ("porsi", "mnt", "Bahan", "Langkah", "Per porsi (perkiraan)", "protein", "karbo", "lemak"),
}


def recipe_text(recipe: Recipe, nutrition: NutritionResult | None = None, lang: str = "en") -> str:
    sv, mn, ing, stp, per, pr, cb, ft = _TEXT_LABELS.get(lang, _TEXT_LABELS["en"])
    lines = [recipe.title, "=" * len(recipe.title)]
    meta = f"{recipe.servings} {sv}"
    if recipe.cook_time_minutes:
        meta += f" · {recipe.cook_time_minutes} {mn}"
    lines += [meta, ""]
    if recipe.description:
        lines += [recipe.description, ""]
    lines.append(ing)
    lines += [f"- {i.name}: {i.display_quantity or ''} ({i.quantity_g:g} g)".replace(":  (", ": (") for i in recipe.ingredients]
    lines += ["", stp] + [f"{n}. {s}" for n, s in enumerate(recipe.steps, 1)]
    if nutrition is not None:
        ps = nutrition.per_serving
        lines += ["", f"{per}: {ps['kcal']:g} kcal · {ps['protein_g']:g} g {pr} · "
                      f"{ps['carbs_g']:g} g {cb} · {ps['fat_g']:g} g {ft}"]
    return "\n".join(lines)
