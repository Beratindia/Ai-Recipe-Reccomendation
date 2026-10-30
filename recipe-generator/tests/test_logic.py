import json

import pytest

from recipe_gen import persist
from recipe_gen.analysis import (analyze, apply_adjustment, grocery_list, pantry_match, scale_recipe,
                                 step_minutes, suggest_adjustment)
from recipe_gen.goals import macro_grams, next_meal_target, violations
from recipe_gen.llm import GenerationRequest, build_user_prompt
from recipe_gen.nutrition import NutritionCalculator, load_food_db
from recipe_gen.schema import Recipe

RECIPE = Recipe.model_validate({
    "title": "Tumis Ayam", "servings": 2, "cook_time_minutes": 20,
    "ingredients": [
        {"name": "ayam", "quantity_g": 300, "display_quantity": "300 g"},
        {"name": "bayam", "quantity_g": 100, "display_quantity": "1 ikat"},
        {"name": "minyak goreng", "quantity_g": 30, "display_quantity": "2 sdm"},
        {"name": "garam", "quantity_g": 3, "display_quantity": "1/2 sdt"},
    ],
    "steps": ["Panaskan minyak.", "Masak ayam 10 menit.", "Tambah bayam, masak 2-3 menit.", "Diamkan 1 jam."],
})


@pytest.fixture(scope="module")
def calc():
    return NutritionCalculator(load_food_db())


def test_pantry_match_ignores_staples_and_quantities(calc):
    m = pantry_match(RECIPE, ["Ayam 500g", "tomat"], calc)
    assert m.have == ["ayam"] and m.missing == ["bayam"] and m.percent == 50  # oil + salt are staples
    assert pantry_match(RECIPE, ["chicken", "spinach"], calc).percent == 100  # English names match too


def test_scale_recipe_scales_grams_and_text():
    r = scale_recipe(RECIPE, 4)
    assert r.servings == 4 and r.ingredients[0].quantity_g == 600
    assert r.ingredients[2].display_quantity == "4 sdm"
    assert r.ingredients[3].display_quantity == "1 sdt"  # 1/2 x 2
    assert scale_recipe(RECIPE, 2) is RECIPE


def test_step_minutes_reads_durations():
    assert [step_minutes(s) for s in RECIPE.steps] == [None, 10, 3, 60]
    assert step_minutes("cook for 1.5 hours") == 90


def test_calorie_adjustment_hits_target_and_is_applied(calc):
    a = analyze(RECIPE, calc, [])
    target = round(a.kcal) - 40
    adj = suggest_adjustment(RECIPE, a.nutrition, target, 0)
    assert adj and adj.verb == "Reduce" and adj.ingredient == "minyak goreng"
    new = apply_adjustment(RECIPE, adj)
    after = calc.calculate(new).per_serving["kcal"]
    assert after == pytest.approx(target, abs=3)
    assert new.ingredients[0].quantity_g == 300  # protein untouched
    assert suggest_adjustment(RECIPE, a.nutrition, round(a.kcal), 10) is None  # already within tolerance


def test_grocery_list_skips_pantry_and_staples(calc):
    items = grocery_list([RECIPE, RECIPE], ["ayam"], calc)
    assert items == [("bayam", 200)]


def test_exclusion_keywords_do_not_flag_long_beans_or_coconut_milk():
    assert violations(["kacang panjang", "santan"], ["Nut-Free", "Dairy-Free"]) == []
    assert violations(["kacang tanah", "susu"], ["Nut-Free", "Dairy-Free"]) == ["Nut-Free: kacang tanah", "Dairy-Free: susu"]
    assert violations(["ayam", "bayam"], ["Vegetarian"]) == ["Vegetarian: ayam"]


def test_macro_math():
    assert macro_grams(2000, 30, 40, 30) == {"protein_g": 150, "carbs_g": 200, "fat_g": 67}
    assert next_meal_target(2150, 3) == 720


def test_prompt_carries_every_constraint():
    req = GenerationRequest(ingredients=["ayam"], exclusions=["Gluten-Free"], equipment=["Air Fryer"], max_minutes=30,
                            target_kcal=550, protein_g=40, slots=[], diet_name="Lean Muscle")
    p = build_user_prompt(req, 3)
    for needle in ("Number of recipes: 3", "Gluten-Free", "Air Fryer", "30 minutes", "550 kcal", "40 g", "Lean Muscle"):
        assert needle in p


def test_save_and_load_roundtrip_keeps_plan_and_survives_damage():
    data = {"pantry": [{"name": "ayam", "qty": "1kg"}], "saved": [RECIPE], "log": [{"kcal": 500, "title": "x"}],
            "plan": {"Mon": {"Lunch": {"recipe": RECIPE, "accepted": True}}}, "settings": {"servings": 3}}
    back = persist.load(persist.dump(data))
    assert back["plan"]["Mon"]["Lunch"]["accepted"] is True
    assert back["plan"]["Mon"]["Lunch"]["recipe"].title == "Tumis Ayam"
    raw = json.loads(persist.dump(data))
    raw["saved"].append({"title": "broken"})  # invalid recipe is skipped, not fatal
    assert len(persist.load(json.dumps(raw))["saved"]) == 1
    with pytest.raises(ValueError):
        persist.load("[1, 2]")
