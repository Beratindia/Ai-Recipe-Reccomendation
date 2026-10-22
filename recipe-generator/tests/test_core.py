import json

import pytest

from recipe_gen.llm import extract_json, generate_recipe
from recipe_gen.nutrition import NutritionCalculator, load_food_db

GOOD = {
    "title": "Ayam Kecap",
    "cuisine": "Indonesian",
    "servings": 2,
    "cook_time_minutes": 30,
    "ingredients": [
        {"name": "Daging ayam", "quantity_g": 300, "display_quantity": "300 g"},
        {"name": "bawang merah", "quantity_g": 40, "display_quantity": "4 siung"},
        {"name": "kecap manis", "quantity_g": 30, "display_quantity": "2 sdm"},
        {"name": "saus rahasia", "quantity_g": 10, "display_quantity": "1 sdm"},
    ],
    "steps": ["Tumis bawang.", "Masukkan ayam.", "Tambahkan kecap."],
}


def test_extract_json_handles_fences():
    assert extract_json("```json\n" + json.dumps(GOOD) + "\n```")["title"] == "Ayam Kecap"


def test_generate_recipe_retries_on_bad_output():
    replies = iter(["not json at all", json.dumps(GOOD)])
    recipe = generate_recipe("ayam", "", "Indonesian", 2, llm=lambda s, u: next(replies))
    assert recipe.title == "Ayam Kecap"


def test_generate_recipe_fails_after_retries():
    with pytest.raises(RuntimeError):
        generate_recipe("ayam", "", "Indonesian", 2, llm=lambda s, u: "{}")


def test_nutrition_matching_and_totals():
    recipe = generate_recipe("x", "", "Indonesian", 2, llm=lambda s, u: json.dumps(GOOD))
    df = load_food_db()
    calc = NutritionCalculator(df)
    result = calc.calculate(recipe)
    assert result.unmatched == ["saus rahasia"]

    def kcal(food_name):
        return float(df.loc[df["name"] == food_name, "kcal"].iloc[0])

    expected = (300 * kcal("Ayam, daging, segar") + 40 * kcal("Bawang merah, segar")
                + 30 * kcal("Kecap")) / 100
    assert result.total["kcal"] == pytest.approx(expected, abs=0.2)
    assert result.per_serving["kcal"] == pytest.approx(expected / 2, abs=0.2)


def test_ambiguous_short_names_resolve_to_meat_not_liver():
    calc = NutritionCalculator(load_food_db())
    assert calc.df.loc[calc.match("ayam"), "name"] == "Ayam, daging, segar"
    assert calc.df.loc[calc.match("chicken"), "name"] == "Ayam, daging, segar"
