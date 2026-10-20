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
    calc = NutritionCalculator(load_food_db())
    result = calc.calculate(recipe)
    assert result.unmatched == ["saus rahasia"]
    # 300 g ayam @120 + 40 g shallot @72 + 30 g kecap @170 = 360 + 28.8 + 51
    assert result.total["kcal"] == pytest.approx(439.8, abs=0.2)
    assert result.per_serving["kcal"] == pytest.approx(219.9, abs=0.2)
