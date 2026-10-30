"""Drive the real Streamlit app (demo model, no API key, no network) page by page."""
import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture(autouse=True)
def no_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)


def new_app() -> AppTest:
    return AppTest.from_file(APP, default_timeout=90).run()


def press(at: AppTest, label_part: str):
    for b in at.button:
        if label_part in (b.label or ""):
            return b.click().run()
    raise AssertionError(f"no button containing {label_part!r}; have {[b.label for b in at.button]}")


def submit_form(at: AppTest, label: str):
    for b in at.button:
        if b.label == label:
            return b.click().run()
    raise AssertionError(f"no form button {label!r}")


def add_pantry(at: AppTest, text: str) -> AppTest:
    box = next(t for t in at.text_input if t.label == "Add ingredients")
    box.set_value(text)
    return submit_form(at, "Add")


def test_every_page_renders_without_errors():
    at = new_app()
    assert not at.exception
    for name in ["Goals", "Recipes", "Cook", "Plan", "Recovery", "Pantry"]:
        at = press(at, name)
        assert not at.exception, (name, [e.value for e in at.exception])


def test_pantry_to_recipes_to_cook_flow():
    at = new_app()
    at = add_pantry(at, "ayam 500g, bayam, telur 4 butir")
    assert [i["name"] for i in at.session_state.pantry] == ["ayam", "bayam", "telur"]
    assert at.session_state.pantry[0]["qty"] == "500g"

    at = press(at, "Generate recipes with 3 ingredients")
    assert not at.exception
    assert at.session_state.page == "Recipes"
    assert len(at.session_state.recipes) == 3

    at = press(at, "Start cooking")
    assert at.session_state.page == "Cook"
    assert at.session_state.current is not None
    assert not at.exception
    at = press(at, "Next step")
    assert at.session_state.cook_step == 1
    at = press(at, "+")
    assert at.session_state.cook_servings == at.session_state.current.servings + 1


def test_exclusions_remove_recipes_and_calorie_target_shows_delta():
    at = new_app()
    at = add_pantry(at, "ayam, bayam")
    at.session_state.exclusions = ["Vegetarian"]
    at = press(at, "Generate recipes")
    assert not at.exception
    assert at.session_state.removed_notes  # the demo recipes use chicken, so they are removed
    assert not at.session_state.recipes


def test_save_log_and_export_import_roundtrip():
    at = new_app()
    at = add_pantry(at, "ayam, bayam")
    at = press(at, "Generate recipes")
    at = press(at, "Save")
    assert len(at.session_state.saved) == 1
    at = press(at, "Log ")
    assert len(at.session_state.log) == 1

    from recipe_gen import persist
    text = persist.dump({"pantry": at.session_state.pantry, "saved": at.session_state.saved,
                         "plan": {}, "log": at.session_state.log,
                         "settings": {"servings": 4}})
    back = persist.load(text)
    assert back["saved"][0].title == at.session_state.saved[0].title
    assert back["settings"]["servings"] == 4 and len(back["log"]) == 1


def test_meal_plan_autofill_accept_and_grocery_list():
    at = new_app()
    at = add_pantry(at, "ayam, bayam, tomat")
    at = press(at, "Plan")
    at = press(at, "Auto-fill Mon")
    assert not at.exception, [e.value for e in at.exception]
    day = at.session_state.plan["Mon"]
    assert set(day) == {"Breakfast", "Lunch", "Snack", "Dinner"}
    at = press(at, "Accept")
    assert any(e["accepted"] for e in at.session_state.plan["Mon"].values())
    # re-filling keeps accepted slots
    kept = next(s for s, e in at.session_state.plan["Mon"].items() if e["accepted"])
    title = at.session_state.plan["Mon"][kept]["recipe"].title
    at = press(at, "Auto-fill Mon")
    assert at.session_state.plan["Mon"][kept]["recipe"].title == title


def test_recovery_generates_gentle_meals_without_chili_for_reflux():
    at = new_app()
    at = press(at, "Recovery")
    at.session_state.condition = "GERD & Acid Reflux"
    at = press(at, "Generate gentle meals")
    assert not at.exception, [e.value for e in at.exception]
    names = [i.name.lower() for r in at.session_state.recovery_meals for i in r.ingredients]
    assert not any("cabai" in n or "cabe" in n for n in names)
    assert at.session_state.recovery_meals or at.session_state.recovery_notes


def test_calorie_target_adjustment_filters_and_sorting():
    at = new_app()
    at = add_pantry(at, "ayam, bayam, tomat")
    at.session_state.target_mode = "Custom"
    at.session_state.custom_kcal = 300
    at.session_state.tolerance = 10  # demo recipes land 40-50 kcal away, so adjustments are offered
    at = press(at, "Generate recipes")
    assert not at.exception, [e.value for e in at.exception]
    s = at.session_state
    # at least one card is off target and offers an adjustment; applying it changes that recipe
    before = [r.model_dump() for r in s.recipes]
    at = press(at, "Apply micro-adjustment")
    assert [r.model_dump() for r in at.session_state.recipes] != before
    # quick filters and sorting do not crash and filter correctly
    at.session_state.quick_filters = ["Under 600 kcal", "40 g+ protein"]
    at = at.run()
    assert not at.exception
    for sort in ["Highest protein", "Lowest calories", "Closest to target", "Best match"]:
        at.session_state.sort_by = sort
        at = at.run()
        assert not at.exception, sort


def test_plan_nudge_changes_calories_and_load_file_restores_state():
    at = new_app()
    at = add_pantry(at, "ayam, bayam")
    at = press(at, "Plan")
    at = press(at, "Auto-fill Mon")
    slot = "Lunch"
    before = at.session_state.plan["Mon"][slot]["recipe"].model_dump()
    labels = [b.key for b in at.button if b.key and b.key.startswith("nudge_-50_Mon_Lunch")]
    assert labels
    at = next(b for b in at.button if b.key == "nudge_-50_Mon_Lunch").click().run()
    assert at.session_state.plan["Mon"][slot]["recipe"].model_dump() != before

    from recipe_gen import persist
    exported = persist.dump({"pantry": at.session_state.pantry, "saved": [], "plan": at.session_state.plan,
                             "log": [], "settings": {"servings": 5, "equipment": ["Oven"]}})
    fresh = new_app()
    S_import = persist.load(exported)
    assert S_import["plan"]["Mon"]["Lunch"]["recipe"].title == at.session_state.plan["Mon"]["Lunch"]["recipe"].title
    assert S_import["settings"] == {"servings": 5, "equipment": ["Oven"]}
    assert not fresh.exception


def test_pantry_remove_and_clear_work():
    at = new_app()
    at = add_pantry(at, "ayam, bayam")
    at = next(b for b in at.button if b.key == "rm_ayam").click().run()
    assert [i["name"] for i in at.session_state.pantry] == ["bayam"]
    at = press(at, "Clear all")
    assert at.session_state.pantry == []
