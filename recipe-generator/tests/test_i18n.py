"""Language switch: Indonesian UI, Indonesian demo recipes, English internal values stay unchanged."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from recipe_gen.demo import demo_llm
from recipe_gen.llm import GenerationRequest, build_user_prompt, parse_recipes

APP = str(Path(__file__).resolve().parent.parent / "app.py")
PAGES = ["Pantry", "Goals", "Recipes", "Cook", "Plan", "Recovery"]


@pytest.fixture(autouse=True)
def no_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)


def test_prompt_carries_language():
    p = build_user_prompt(GenerationRequest(ingredients=["ayam"], language="English"), 1)
    assert "Language: English" in p
    p = build_user_prompt(GenerationRequest(ingredients=["ayam"], language="Indonesian"), 1)
    assert "Language: Indonesian" in p


def test_demo_recipes_follow_language():
    for lang, word in (("English", "Stir-Fried"), ("Indonesian", "Tumis")):
        req = GenerationRequest(ingredients=["ayam", "bayam"], language=lang)
        recipes, _ = parse_recipes(demo_llm("", build_user_prompt(req, 3)))
        assert word in recipes[0].title


def test_switching_to_indonesian_and_back():
    at = AppTest.from_file(APP, default_timeout=90).run()
    assert not at.exception
    at.radio(key="lang").set_value("Bahasa Indonesia").run()
    assert not at.exception
    assert any("Bahan" in b.label for b in at.button)
    # every page renders in Indonesian without errors
    for name in PAGES:
        at.session_state["page"] = name
        at.run()
        assert not at.exception, name
    at.session_state["page"] = "Pantry"
    at.radio(key="lang").set_value("English").run()
    assert not at.exception
    assert any(b.label.startswith("Pantry") for b in at.button)


def test_indonesian_flow_keeps_english_state():
    at = AppTest.from_file(APP, default_timeout=90).run()
    at.radio(key="lang").set_value("Bahasa Indonesia").run()
    box = next(x for x in at.text_input if x.label == "Tambah bahan")
    box.set_value("ayam 500g, bayam")
    next(b for b in at.button if b.label == "Tambah").click().run()
    assert [i["name"] for i in at.session_state["pantry"]] == ["ayam", "bayam"]
    next(b for b in at.button if b.label.startswith("Buat resep dari")).click().run()
    assert not at.exception
    assert at.session_state["page"] == "Recipes"
    assert "Tumis" in at.session_state["recipes"][0].title or "Panggang" in at.session_state["recipes"][0].title
    assert at.session_state["cuisine"] == "Indonesian"  # internal value unchanged
