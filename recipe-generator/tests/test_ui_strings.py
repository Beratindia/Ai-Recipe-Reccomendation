"""Test bilingual UI strings and translation helpers."""
import pytest
from recipe_gen.ui_strings import get_text, SUPPORTED_LANGUAGES


def test_supported_languages():
    assert "id" in SUPPORTED_LANGUAGES
    assert "en" in SUPPORTED_LANGUAGES


def test_get_text_indonesian():
    assert get_text("app_title", lang="id") == "Vitality Kitchen"
    assert get_text("pantry_title", lang="id") == "Dapur Saya"
    assert "bahan" in get_text("add_ingredients_placeholder", lang="id").lower()


def test_get_text_english():
    assert get_text("app_title", lang="en") == "Vitality Kitchen"
    assert get_text("pantry_title", lang="en") == "Pantry"
    assert "ingredients" in get_text("add_ingredients_placeholder", lang="en").lower()


def test_get_text_fallback():
    # Fallback to key or English if unknown
    assert get_text("non_existent_key", lang="id") == "non_existent_key"
