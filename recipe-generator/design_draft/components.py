"""Small HTML building blocks for the Vitality Kitchen look."""
import html as _html

import streamlit as st

APP_NAME = "NutriChef"
APP_TAGLINE = "AI recipes with real nutrition"


def esc(x) -> str:
    return _html.escape(str(x), quote=True)


def h(s: str) -> str:
    """Collapse indentation/newlines so Markdown never turns the HTML into a code block."""
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


def render(s: str) -> None:
    st.markdown(h(s), unsafe_allow_html=True)


def top_bar(subtitle: str, demo: bool) -> None:
    pill = '<span class="status-pill demo">Demo mode</span>' if demo else '<span class="status-pill">AI: Gemini</span>'
    render(f"""
    <div class="topbar">
      <div class="brand"><div class="brand-logo">🥗</div>
        <div><div class="brand-name">{esc(APP_NAME)}</div><div class="brand-sub">{esc(subtitle)}</div></div></div>
      {pill}
    </div>""")


def chip(text: str, kind: str = "kcal") -> str:
    return f'<span class="chip {kind}">{esc(text)}</span>'


def fmt(x: float) -> str:
    return f"{x:,.0f}" if abs(x) >= 100 else f"{x:.0f}" if abs(x - round(x)) < 0.05 else f"{x:.1f}"


def macro_strip(ps: dict) -> str:
    cells = [("Energy", f"{fmt(ps['kcal'])} kcal", "kcal"), ("Protein", f"{fmt(ps['protein_g'])}g", "protein"),
             ("Carbs", f"{fmt(ps['carbs_g'])}g", "carbs"), ("Fats", f"{fmt(ps['fat_g'])}g", "fat")]
    inner = "".join(f'<div class="macro-cell {k}"><div class="lab">{l}</div><div class="val">{v}</div></div>' for l, v, k in cells)
    return f'<div class="macro-strip">{inner}</div>'


_EMOJI = [
    (("ayam", "chicken", "bebek", "duck"), "🍗"), (("udang", "shrimp", "prawn", "rebon"), "🦐"),
    (("salmon", "tuna", "tongkol", "ikan", "fish", "bandeng", "lele", "patin", "kakap", "teri"), "🐟"),
    (("sapi", "beef", "daging", "kambing", "lamb", "rendang"), "🥩"), (("telur", "egg", "omelet", "orak"), "🍳"),
    (("tahu", "tofu", "tempe", "tempeh"), "🥘"), (("soto", "sup", "soup", "bubur", "porridge", "kuah"), "🍲"),
    (("mie", "noodle", "pasta", "spaghetti", "bihun", "soun"), "🍜"), (("nasi", "rice", "goreng"), "🍚"),
    (("salad", "sayur", "bayam", "kangkung", "spinach", "vegetable", "brokoli", "broccoli"), "🥗"),
    (("sambal", "cabai", "pedas"), "🌶️"), (("alpukat", "avocado"), "🥑"), (("kentang", "potato"), "🥔"),
]
_GRADIENTS = ["linear-gradient(135deg,#D1FAE5,#6EE7B7)", "linear-gradient(135deg,#FEF3C7,#FCD34D)",
              "linear-gradient(135deg,#FFEDD5,#FDBA74)", "linear-gradient(135deg,#E0E7FF,#A5B4FC)",
              "linear-gradient(135deg,#FCE7F3,#F9A8D4)"]


def food_emoji(title: str, ingredients: list[str] | None = None) -> str:
    text = (title + " " + " ".join((ingredients or [])[:3])).lower()
    for keys, emo in _EMOJI:
        if any(k in text for k in keys):
            return emo
    return "🍽️"


def visual(title: str, ingredients: list[str], height: int = 150, badges: dict[str, str] | None = None) -> str:
    emo = food_emoji(title, ingredients)
    grad = _GRADIENTS[sum(map(ord, title)) % len(_GRADIENTS)]
    size = int(height * 0.5)
    b = "".join(f'<span class="badge {pos}">{esc(txt)}</span>' for pos, txt in (badges or {}).items() if txt)
    return f'<div class="visual" style="height:{height}px;background:{grad}"><span class="emoji" style="font-size:{size}px">{emo}</span>{b}</div>'


def ring(pct: float, color: str, value: str, unit: str, size: int = 78) -> str:
    pct = max(0, min(100, pct))
    return f"""<div class="ring-wrap" style="width:{size}px;height:{size}px">
      <svg viewBox="0 0 36 36" width="{size}" height="{size}">
        <circle cx="18" cy="18" r="15.9155" fill="none" stroke="#E2E8F0" stroke-width="3.2"/>
        <circle cx="18" cy="18" r="15.9155" fill="none" stroke="{color}" stroke-width="3.2" stroke-linecap="round"
          stroke-dasharray="{pct:.1f} {100 - pct:.1f}" stroke-dashoffset="25"/></svg>
      <div class="ring-text"><b>{esc(value)}</b><small>{esc(unit)}</small></div></div>"""


def bar(pct: float, color: str) -> str:
    return f'<div class="bar"><span style="width:{max(0, min(100, pct)):.0f}%;background:{color}"></span></div>'


def empty_state(emoji: str, title: str, text: str) -> None:
    render(f'<div class="empty"><div class="big">{emoji}</div><div class="h-sm">{esc(title)}</div><p class="sub">{esc(text)}</p></div>')
