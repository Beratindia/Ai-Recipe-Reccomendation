"""Diet presets, calorie/macro targets and allergy / diet exclusions."""
import re
from dataclasses import dataclass

# name -> (protein %, carbs %, fat %, short description, prompt guidance)
DIET_PRESETS: dict[str, tuple[int, int, int, str, str]] = {
    "Balanced": (25, 50, 25, "Everyday balance",
                 "Balanced plate: lean protein, vegetables and a sensible portion of carbs."),
    "Lean Muscle": (35, 40, 25, "High protein",
                    "High protein with lean cuts (chicken breast, fish, egg, tempe, tofu); moderate carbs."),
    "Clean Keto": (20, 10, 70, "Low carb",
                   "Very low carbohydrate: no rice, noodles, flour, potato or sugar; use healthy fats and low-carb vegetables."),
    "Mediterranean": (20, 45, 35, "Wholesome, anti-inflammatory",
                      "Mediterranean style: vegetables, fish or legumes, olive oil, whole grains."),
    "Heart Healthy": (20, 55, 25, "Low sodium",
                      "Low sodium and low saturated fat: minimal salt/soy sauce, no deep frying, limit coconut milk."),
}

GOALS = {
    "Calorie Deficit": "The person wants to lose weight: keep calories controlled and protein and fibre high.",
    "Maintenance": "The person wants to maintain weight: balanced portions.",
    "Hypertrophy": "The person wants to build muscle: high protein and enough carbohydrate to fuel training.",
}

# slot name -> share of the daily calorie budget
SLOT_SHARES = {"Breakfast": 0.25, "Lunch": 0.35, "Snack": 0.10, "Dinner": 0.30}


def macro_grams(kcal: float, protein_pct: float, carbs_pct: float, fat_pct: float) -> dict[str, int]:
    """Grams of each macro for a calorie amount and a % split (4/4/9 kcal per gram)."""
    total = (protein_pct + carbs_pct + fat_pct) or 1
    return {
        "protein_g": round(kcal * protein_pct / total / 4),
        "carbs_g": round(kcal * carbs_pct / total / 4),
        "fat_g": round(kcal * fat_pct / total / 9),
    }


def next_meal_target(daily_kcal: int, meals_per_day: int) -> int:
    return int(round(daily_kcal / max(meals_per_day, 1) / 10) * 10)


@dataclass(frozen=True)
class Exclusion:
    label: str
    note: str
    keywords: tuple[str, ...]
    prompt: str


# Keyword lists are a safety net on top of the prompt, not a guarantee.
EXCLUSIONS: dict[str, Exclusion] = {
    "Gluten-Free": Exclusion("Gluten-Free", "Celiac safe", (
        "terigu", "gandum", "flour", "wheat", "roti", "bread", "pasta", "spaghetti", "mie", "mi",
        "noodle", "noodles", "macaroni", "couscous", "barley", "seitan", "breadcrumbs"),
        "No gluten: no wheat flour, bread, pasta, wheat noodles, couscous or seitan."),
    "Dairy-Free": Exclusion("Dairy-Free", "0% lactose", (
        "susu", "milk", "keju", "cheese", "mentega", "butter", "krim", "cream", "yogurt", "yoghurt",
        "whey", "ghee"),
        "No dairy: no milk, cheese, butter, cream or yogurt (coconut milk is fine)."),
    "Nut-Free": Exclusion("Nut-Free", "Tree nuts & peanuts", (
        "kacang tanah", "kacang mete", "kacang almond", "kacang kenari", "kacang", "peanut", "peanuts",
        "almond", "walnut", "cashew", "mete", "pistachio", "hazelnut", "kemiri", "pecan"),
        "No nuts or peanuts, including candlenut (kemiri) and peanut sauce."),
    "Egg-Free": Exclusion("Egg-Free", "No eggs", ("telur", "egg", "eggs", "mayones", "mayonnaise"),
                          "No eggs or egg-based sauces."),
    "Seed-Oil Conscious": Exclusion("Seed-Oil Conscious", "No canola / soy oil", (
        "canola", "minyak canola", "minyak kedelai", "soybean oil", "minyak jagung", "corn oil",
        "sunflower", "minyak bunga matahari", "minyak biji"),
        "Avoid canola, soybean, corn and sunflower oil; use olive, coconut or rice bran oil."),
    "Halal": Exclusion("Halal", "No pork or alcohol", (
        "babi", "pork", "bacon", "ham", "lard", "minyak babi", "wine", "anggur", "arak", "bir", "beer",
        "rum", "sake", "mirin", "brandy", "whisky", "angciu", "ang ciu"),
        "Halal: no pork, lard, alcohol, wine or mirin."),
    "Vegetarian": Exclusion("Vegetarian", "No meat or fish", (
        "ayam", "chicken", "daging", "beef", "sapi", "kambing", "lamb", "ikan", "fish", "udang", "shrimp",
        "prawn", "cumi", "squid", "bebek", "duck", "terasi", "ebi", "rebon", "kaldu ayam", "kaldu sapi",
        "gelatin", "bakso", "sosis", "sausage", "salmon", "tuna", "tongkol", "teri", "kerang"),
        "Vegetarian: no meat, poultry, fish, shrimp, shrimp paste or meat stock (eggs and dairy are fine)."),
}

# phrases that contain an excluded keyword but are not the allergen
_ALLOWED_PHRASES = (
    "kacang panjang", "kacang hijau", "kacang merah", "kacang polong", "kacang kapri", "kacang buncis",
    "kacang kedelai", "kacang edamame", "kacang arab", "kacang hitam", "kacang putih", "green beans",
    "santan", "coconut milk", "susu kelapa",
)


def _tokens(text: str) -> str:
    text = text.lower()
    for ph in _ALLOWED_PHRASES:
        text = text.replace(ph, " ")
    return " " + re.sub(r"[^a-z0-9]+", " ", text).strip() + " "


def violations(ingredient_names: list[str], exclusion_labels: list[str]) -> list[str]:
    """Return 'Label: ingredient' strings for ingredients that break any chosen exclusion."""
    found = []
    for label in exclusion_labels:
        ex = EXCLUSIONS.get(label)
        if not ex:
            continue
        for name in ingredient_names:
            hay = _tokens(name)
            if any(f" {kw} " in hay for kw in ex.keywords):
                found.append(f"{label}: {name}")
    return found


def blocked_by_keywords(ingredient_names: list[str], keywords: tuple[str, ...]) -> list[str]:
    out = []
    for name in ingredient_names:
        hay = _tokens(name)
        if any(f" {kw} " in hay for kw in keywords):
            out.append(name)
    return out
