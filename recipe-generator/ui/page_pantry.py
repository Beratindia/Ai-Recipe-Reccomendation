import streamlit as st

from . import state as S
from .i18n import plural, t


def show() -> None:
    s = st.session_state
    st.header(t("Pantry"))
    st.caption(t("What's in your kitchen? Quantities are optional, e.g. “ayam 500g”."))

    # ---- add ingredients: typing
    with st.form("add_item", clear_on_submit=True, border=False):
        c1, c2 = st.columns([4, 1])
        text = c1.text_input(t("Add ingredients"), placeholder=t("e.g. ayam 500g, bayam, telur 4 butir"))
        submitted = c2.form_submit_button(t("Add"), use_container_width=True)
    if submitted and text.strip() and S.add_pantry(text) == 0:
        st.toast(t("Already in your pantry."))

    # ---- add ingredients: suggestions by category
    st.pills(t("Category"), list(S.SUGGESTIONS), key="cat", format_func=t)
    cols = st.columns(4)
    for i, name in enumerate(n for n in S.SUGGESTIONS[s.cat or "Proteins"] if n not in S.pantry_names()):
        cols[i % 4].button(f"+ {name}", key=f"sg_{name}", on_click=S.add_pantry, args=(name,), use_container_width=True)

    # ---- current pantry
    n = len(s.pantry)
    c1, c2 = st.columns([3, 1])
    c1.subheader(plural(n, "Current pantry ({n} item)", "Current pantry ({n} items)"))
    if n:
        c2.button(t("Clear all"), key="clear_pantry", on_click=lambda: s.pantry.clear(), use_container_width=True)
    if not n:
        st.caption(t("Your pantry is empty. Type an ingredient above or pick a suggestion."))
    for item in s.pantry:
        c1, c2 = st.columns([5, 1])
        label = item["name"].title() + (f" · {item['qty']}" if item["qty"] else "")
        c1.write(label)
        c2.button(t("Remove"), icon=":material/close:", key=f"rm_{item['name']}", on_click=S.remove_pantry, args=(item["name"],))

    # ---- cooking setup
    st.subheader(t("Cooking setup"))
    c1, c2 = st.columns([3, 1])
    c1.radio(t("Cuisine"), ["Indonesian", "International"], key="cuisine", horizontal=True, format_func=t)
    c2.number_input(t("Servings"), 1, 12, key="servings")
    st.text_input(t("Preferences (optional)"), placeholder=t("e.g. spicy, low oil, kid-friendly"), key="prefs")
    st.pills(t("Available equipment (select any)"), S.EQUIPMENT, selection_mode="multi", key="equipment", format_func=t)
    st.radio(t("Max prep time"), list(S.PREP_OPTIONS), key="prep_time", horizontal=True, format_func=t)

    # ---- smart prediction: best recipe from the last batch
    if s.recipes and s.pantry:
        best = max((S.analyzed(r) for r in s.recipes), key=lambda a: a.match.percent)
        total = len(best.match.have) + len(best.match.missing)
        st.info(t("**Smart prediction:** {title}. Matches {have} of {total} ingredients.",
                  title=best.recipe.title, have=len(best.match.have), total=total))

    if st.button(plural(n, "Generate recipes with {n} ingredient", "Generate recipes with {n} ingredients"), type="primary",
                 use_container_width=True, key="btn_generate", icon=":material/restaurant_menu:"):
        if S.generate_for_recipes():
            st.rerun()
