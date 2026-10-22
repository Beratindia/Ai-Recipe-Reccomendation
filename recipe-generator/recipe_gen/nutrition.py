"""Nutrition calculation from a food-composition table (values per 100 g)."""
import difflib
import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

NUTRIENT_COLS = ["kcal", "protein_g", "fat_g", "carbs_g"]
MICRO_COLS = ["calcium_mg", "iron_mg", "zinc_mg", "retinol_ug", "betacarotene_ug"]
DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "food_composition.csv"


def normalize(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"\([^)]*\)", " ", name)  # drop "(optional)" style notes
    name = re.sub(r"[^a-z0-9\s]", " ", name)
    return re.sub(r"\s+", " ", name).strip()


def load_food_db(path: Path | str = DEFAULT_DB) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = {"name", "aliases", *NUTRIENT_COLS} - set(df.columns)
    if missing:
        raise ValueError(f"Food database missing columns: {missing}")
    df["aliases"] = df["aliases"].fillna("")
    for c in MICRO_COLS:  # optional columns
        if c not in df.columns:
            df[c] = float("nan")
    return df


@dataclass
class NutritionResult:
    per_ingredient: pd.DataFrame
    total: dict
    per_serving: dict
    unmatched: list[str] = field(default_factory=list)


class NutritionCalculator:
    def __init__(self, df: pd.DataFrame, fuzzy_cutoff: float = 0.8):
        self.df = df.reset_index(drop=True)
        self.fuzzy_cutoff = fuzzy_cutoff
        self.lookup: dict[str, int] = {}
        for i, row in self.df.iterrows():
            self.lookup.setdefault(normalize(row["name"]), i)  # first entry wins on clashes
            for alias in str(row["aliases"]).split(";"):
                if alias.strip():
                    self.lookup.setdefault(normalize(alias), i)

    def match(self, ingredient_name: str) -> int | None:
        key = normalize(ingredient_name)
        if key in self.lookup:  # 1. exact name or alias
            return self.lookup[key]
        words = key.split()
        for n in range(len(words), 0, -1):  # 2. longest phrase inside the name
            for s in range(len(words) - n + 1):
                phrase = " ".join(words[s : s + n])
                if phrase in self.lookup:
                    return self.lookup[phrase]
        close = difflib.get_close_matches(key, list(self.lookup), n=1, cutoff=self.fuzzy_cutoff)
        return self.lookup[close[0]] if close else None  # 3. fuzzy

    def calculate(self, recipe) -> NutritionResult:
        cols = NUTRIENT_COLS + MICRO_COLS
        rows, unmatched = [], []
        for ing in recipe.ingredients:
            idx = self.match(ing.name)
            if idx is None:
                unmatched.append(ing.name)
                rows.append({"ingredient": ing.name, "grams": ing.quantity_g, "matched_to": None,
                             **{c: None for c in cols}})
                continue
            food = self.df.loc[idx]
            factor = ing.quantity_g / 100.0
            rows.append({"ingredient": ing.name, "grams": ing.quantity_g, "matched_to": food["name"],
                         **{c: round(float(food[c]) * factor, 1) for c in cols}})
        per_ingredient = pd.DataFrame(rows)
        total = {c: round(float(per_ingredient[c].sum(skipna=True)), 2) for c in cols}
        per_serving = {c: round(v / recipe.servings, 2) for c, v in total.items()}
        return NutritionResult(per_ingredient, total, per_serving, unmatched)
