"""Test UI styles and theme CSS generation."""
from recipe_gen.ui_styles import get_custom_css, get_macro_badge_html


def test_custom_css_contains_design_tokens():
    css = get_custom_css()
    assert "Plus Jakarta Sans" in css
    assert "Inter" in css
    assert "#006948" in css  # Primary green
    assert "#FAF8FF" in css or "#faf8ff" in css  # Surface canvas


def test_macro_badge_html():
    html = get_macro_badge_html(540, 44, 38, 16)
    assert "540" in html
    assert "44g" in html or "44 g" in html
    assert "38g" in html or "38 g" in html
    assert "16g" in html or "16 g" in html
