import streamlit as st

from recipe_gen.goals import DIET_PRESETS, EXCLUSIONS

from . import state as S
from .i18n import t
from .shared import target_controls


def show() -> None:
    s = st.session_state
    st.header(t("Nutrition goals"))
    g = S.get_goals()
    target = g.target_kcal
    if target:
        head = t("**{diet}**: about {target} kcal per meal.", diet=t(g.diet), target=target)
    else:
        head = t("**{diet}**: no calorie target.", diet=t(g.diet))
    st.info(head + t(" Recipes are written to match this, then checked against your nutrition table."))

    st.subheader(t("Diet strategy preset"))
    names = list(DIET_PRESETS)
    for row in range(0, len(names), 3):
        for col, name in zip(st.columns(3), names[row:row + 3]):
            p, c, f, desc, _ = DIET_PRESETS[name]
            col.button(t("{name}\n{desc} · {p}% protein", name=t(name), desc=t(desc), p=p), key=f"preset_{name}",
                       use_container_width=True, type="primary" if g.diet == name else "secondary",
                       on_click=S.apply_preset, args=(name,))

    st.subheader(t("Calories"))
    target_controls()

    st.subheader(t("Macro split"))
    st.slider(t("Protein %"), 5, 70, key="p_pct")
    st.slider(t("Carbs %"), 5, 80, key="c_pct")
    st.slider(t("Fats %"), 5, 80, key="f_pct")
    total = s.p_pct + s.c_pct + s.f_pct
    m = g.macros
    st.table({t("Macro"): [t("Protein"), t("Carbohydrates"), t("Fats")],
              t("Share"): [f"{round(100 * x / total)}%" for x in (s.p_pct, s.c_pct, s.f_pct)],
              t("Grams per meal"): [m["protein_g"], m["carbs_g"], m["fat_g"]]})
    if total != 100:
        st.caption(t("The three values add up to {total}%, so they are scaled to 100%.", total=total))

    st.subheader(t("Dietary & allergy exclusions"))
    st.pills(t("Exclusions"), list(EXCLUSIONS), selection_mode="multi", key="exclusions", label_visibility="collapsed",
             format_func=t)
    if s.exclusions:
        st.caption(" · ".join(f"{t(e)}: {t(EXCLUSIONS[e].note)}" for e in s.exclusions))
    st.caption(t("After the AI writes a recipe, the app removes any that contain an excluded ingredient. "
                 "This keyword check is a safety net, not a guarantee: always read labels if you have a serious allergy."))

    st.subheader(t("Today's intake"))
    tot = S.today_totals()
    if S.today_log():
        budget = g.daily_kcal
        st.progress(min(tot["kcal"] / budget, 1.0),
                    text=t("{done} of {budget} kcal logged · {left} remaining", done=f"{tot['kcal']:.0f}", budget=budget,
                           left=f"{max(budget - tot['kcal'], 0):.0f}"))
        st.caption(t("Protein {p} g · Carbs {c} g · Fat {f} g", p=f"{tot['protein_g']:.0f}", c=f"{tot['carbs_g']:.0f}",
                     f=f"{tot['fat_g']:.0f}"))
        for e in S.today_log():
            st.markdown(f"- {e['title']}: {e['kcal']:.0f} kcal")
        st.button(t("Clear today's log"), key="clear_log", on_click=lambda: s.update(
            log=[e for e in s.log if e not in S.today_log()]))
    else:
        st.caption(t("Nothing logged today. Use “Log” on a recipe to track it here."))

    if st.button(t("Generate meals for this target"), type="primary", use_container_width=True, key="btn_goal_gen",
                 icon=":material/restaurant_menu:"):
        if S.generate_for_recipes():
            st.rerun()
