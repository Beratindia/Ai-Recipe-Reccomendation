"""Check the nutrition calculator against the dataset's own recipes.

For every recipe, each ingredient's raw text (e.g. "bawang merah ukuran besar") and weight are
fed to the NutritionCalculator, and the result is compared with the dataset's ground truth:
  1. matching accuracy: did we pick the same food as the dataset (name_of_material)?
  2. calorie error per recipe: our total kcal vs the dataset's total_calories.

Usage: python scripts/validate_against_dataset.py path/to/data.json
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_food_db import load_records  # noqa: E402
from recipe_gen.nutrition import NutritionCalculator, load_food_db  # noqa: E402
from recipe_gen.schema import Ingredient, Recipe  # noqa: E402


def is_positive_number(x) -> bool:
    # a few rows in the dataset have text weights such as "65 ml"; skip those
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x > 0


def main(path: Path):
    calc = NutritionCalculator(load_food_db())
    n_items = n_correct = n_wrong = n_missed = 0
    wrong_examples, rows = [], []
    for r in load_records(path):
        items = [c for c in r["composition"] if c.get("name_of_material") and is_positive_number(c.get("weight_in_grams"))]
        if not items:
            continue
        recipe = Recipe(
            title=r["title"], cuisine="Indonesian", servings=1,  # only recipe totals are compared, so servings is irrelevant
            ingredients=[Ingredient(name=c["ingredient"], quantity_g=c["weight_in_grams"],
                                    display_quantity="") for c in items],
            steps=["-"],
        )
        res = calc.calculate(recipe)
        for c, (_, row) in zip(items, res.per_ingredient.iterrows()):
            n_items += 1
            if row["matched_to"] == c["name_of_material"]:
                n_correct += 1
            elif row["matched_to"] is None:
                n_missed += 1
            else:
                n_wrong += 1
                wrong_examples.append((c["ingredient"], c["name_of_material"], row["matched_to"]))
        truth = r.get("total_calories")
        if truth:
            rows.append({"id": r["id"], "title": r["title"][:40], "truth_kcal": truth,
                         "our_kcal": res.total["kcal"],
                         "err_%": round(100 * (res.total["kcal"] - truth) / truth, 1)})
    df = pd.DataFrame(rows)
    print(f"Ingredient matching over {n_items} ingredients with ground truth:")
    print(f"  correct {n_correct} ({100*n_correct/n_items:.1f}%) | wrong food {n_wrong} | not found {n_missed}")
    print(f"Calorie error over {len(df)} recipes (our kcal vs dataset total_calories):")
    print(f"  mean abs error {df['err_%'].abs().mean():.1f}% | median {df['err_%'].abs().median():.1f}% "
          f"| within 5%: {(df['err_%'].abs() <= 5).mean()*100:.0f}% | within 10%: {(df['err_%'].abs() <= 10).mean()*100:.0f}%")
    print("Worst recipes:\n", df.reindex(df["err_%"].abs().sort_values(ascending=False).index).head(5).to_string(index=False))
    print("Wrong-match examples (raw text, truth, ours):")
    for e in wrong_examples[:12]:
        print("  ", e)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
