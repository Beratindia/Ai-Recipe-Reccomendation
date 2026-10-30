import streamlit as st

from recipe_gen.goals import DIET_PRESETS, EXCLUSIONS

from . import state as S
from .shared import target_controls


def show() -> None:
    s = st.session_state
    st.header("Nutrition goals")
    g = S.get_goals()
    target = g.target_kcal
    st.info(f"**{g.diet}**: " + (f"about {target} kcal per meal." if target else "no calorie target.")
            + " Recipes are written to match this, then checked against your nutrition table.")

    st.subheader("Diet strategy preset")
    names = list(DIET_PRESETS)
    for row in range(0, len(names), 3):
        for col, name in zip(st.columns(3), names[row:row + 3]):
            p, c, f, desc, _ = DIET_PRESETS[name]
            col.button(f"{name}\n{desc} · {p}% protein", key=f"preset_{name}", use_container_width=True,
                       type="primary" if g.diet == name else "secondary", on_click=S.apply_preset, args=(name,))

    st.subheader("Calories")
    target_controls()

    st.subheader("Macro split")
    st.slider("Protein %", 5, 70, key="p_pct")
    st.slider("Carbs %", 5, 80, key="c_pct")
    st.slider("Fats %", 5, 80, key="f_pct")
    total = s.p_pct + s.c_pct + s.f_pct
    m = g.macros
    st.table({"Macro": ["Protein", "Carbohydrates", "Fats"],
              "Share": [f"{round(100 * x / total)}%" for x in (s.p_pct, s.c_pct, s.f_pct)],
              "Grams per meal": [m["protein_g"], m["carbs_g"], m["fat_g"]]})
    if total != 100:
        st.caption(f"The three values add up to {total}%, so they are scaled to 100%.")

    st.subheader("Dietary & allergy exclusions")
    st.pills("Exclusions", list(EXCLUSIONS), selection_mode="multi", key="exclusions", label_visibility="collapsed")
    if s.exclusions:
        st.caption(" · ".join(f"{e}: {EXCLUSIONS[e].note}" for e in s.exclusions))
    st.caption("After the AI writes a recipe, the app removes any that contain an excluded ingredient. "
               "This keyword check is a safety net, not a guarantee: always read labels if you have a serious allergy.")

    st.subheader("Today's intake")
    tot = S.today_totals()
    if S.today_log():
        budget = g.daily_kcal
        st.progress(min(tot["kcal"] / budget, 1.0), text=f"{tot['kcal']:.0f} of {budget} kcal logged · "
                    f"{max(budget - tot['kcal'], 0):.0f} remaining")
        st.caption(f"Protein {tot['protein_g']:.0f} g · Carbs {tot['carbs_g']:.0f} g · Fat {tot['fat_g']:.0f} g")
        for e in S.today_log():
            st.markdown(f"- {e['title']}: {e['kcal']:.0f} kcal")
        st.button("Clear today's log", key="clear_log", on_click=lambda: s.update(
            log=[e for e in s.log if e not in S.today_log()]))
    else:
        st.caption("Nothing logged today. Use “Log” on a recipe to track it here.")

    if st.button("Generate meals for this target", type="primary", use_container_width=True, key="btn_goal_gen",
                 icon=":material/restaurant_menu:"):
        if S.generate_for_recipes():
            st.rerun()
