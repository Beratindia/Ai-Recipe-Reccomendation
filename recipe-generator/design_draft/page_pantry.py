import streamlit as st

from recipe_gen.analysis import clean_item

from . import state as S
from .components import esc, render, top_bar


def _label(item: dict) -> str:
    name = item["name"][:1].upper() + item["name"][1:]
    return f"{name} · {item['qty']}  ✕" if item["qty"] else f"{name}  ✕"


def _generate() -> None:
    if S.generate_for_recipes():
        st.session_state._goto = True


def show() -> None:
    s = st.session_state
    top_bar("Pantry", S.is_demo())

    render("""<div><p class="h-lg">What's in your kitchen?</p>
      <p class="sub">Add what you have. Quantities are optional, e.g. “ayam 500g”.</p></div>""")

    with st.form("add_item", clear_on_submit=True, border=False):
        c1, c2 = st.columns([4, 1.4])
        text = c1.text_input("Add ingredient", placeholder="Add ingredients (e.g. ayam 500g, bayam)",
                             label_visibility="collapsed")
        submitted = c2.form_submit_button("Add", use_container_width=True)
    if submitted and text.strip():
        if S.add_pantry(text) == 0:
            st.toast("Already in your pantry.", icon="✔️")

    st.pills("Suggestions", list(S.SUGGESTIONS), key="cat", label_visibility="collapsed")
    cat = s.cat or "Proteins"
    with st.container(key="suggest_chips"):
        for name in S.SUGGESTIONS[cat]:
            if name not in S.pantry_names():
                st.button(f"+ {name}", key=f"sg_{name}", on_click=S.add_pantry, args=(name,))

    n = len(s.pantry)
    c1, c2 = st.columns([3, 1])
    c1.markdown(f'<p class="h-md" style="margin-top:6px">Current Pantry <span class="count-badge">{n} item{"s" if n != 1 else ""}</span></p>',
                unsafe_allow_html=True)
    if n:
        c2.button("Clear all", key="clear_pantry", on_click=lambda: s.pantry.clear(), use_container_width=True)
    with st.container(border=True, key="pantry_chips"):
        if not n:
            st.caption("Your pantry is empty. Type an ingredient above or tap a suggestion.")
        for item in s.pantry:
            st.button(_label(item), key=f"rm_{item['name']}", on_click=S.remove_pantry, args=(item["name"],))

    with st.container(border=True):
        render('<p class="h-sm">Cuisine & servings</p>')
        c1, c2 = st.columns([3, 1.4])
        c1.radio("Cuisine", ["Indonesian", "International"], key="cuisine", horizontal=True)
        c2.number_input("Servings", 1, 12, key="servings")
        st.text_input("Preferences (optional)", placeholder="e.g. spicy, low oil, kid-friendly", key="prefs")

    with st.container(border=True):
        render('<p class="h-sm">🍳 Available equipment</p>')
        st.pills("Equipment", S.EQUIPMENT, selection_mode="multi", key="equipment", label_visibility="collapsed")
        render('<p class="h-sm" style="margin-top:10px">⏱ Max prep time</p>')
        st.radio("Max prep time", list(S.PREP_OPTIONS), key="prep_time", horizontal=True, label_visibility="collapsed")

    with st.container(key="gen_cta"):
        label = f"✨ Generate Recipes with {n} Ingredient{'s' if n != 1 else ''}"
        if st.button(label, type="primary", use_container_width=True, key="btn_generate"):
            if S.generate_for_recipes():
                st.rerun()
