"""Small plain-widget pieces used by more than one page."""
import streamlit as st

from recipe_gen.goals import GOALS

from . import state as S
from .i18n import t


def target_controls() -> None:
    """Calorie target controls (same state keys wherever they are shown)."""
    s = st.session_state
    g = S.get_goals()
    st.radio(t("Calorie target for each recipe"), ["From daily budget", "Custom", "Off"], key="target_mode",
             horizontal=True, format_func=t)
    if s.target_mode == "From daily budget":
        c1, c2 = st.columns(2)
        c1.number_input(t("Daily calories (kcal)"), 1000, 5000, step=50, key="daily_kcal")
        c2.radio(t("Meals per day"), [3, 4], key="meals_pd", horizontal=True)
    elif s.target_mode == "Custom":
        st.slider(t("Target energy per serving (kcal)"), 250, 1000, step=10, key="custom_kcal")
        cols = st.columns(3)
        for col, (kcal, label) in zip(cols, ((300, "Snack"), (500, "Lean cut"), (700, "Hearty"))):
            col.button(t("{kcal} kcal ({label})", kcal=kcal, label=t(label)), key=f"preset_kcal_{kcal}",
                       use_container_width=True, on_click=lambda k=kcal: s.update(custom_kcal=k))
    target = S.get_goals().target_kcal
    if target:
        st.slider(t("Tolerance (± kcal)"), 10, 100, step=10, key="tolerance")
        st.caption(t("Target: {target} kcal per serving (accepted range {lo} to {hi}).",
                     target=target, lo=target - g.tolerance, hi=target + g.tolerance))
    st.radio(t("Metabolic goal"), list(GOALS), key="goal", horizontal=True, format_func=t)


def macro_metrics(ps: dict, key: str = "x") -> None:
    with st.container(key=f"macros_{key}"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t("Energy"), f"{ps['kcal']:.0f} kcal")
        c2.metric(t("Protein"), f"{ps['protein_g']:.0f} g")
        c3.metric(t("Carbs"), f"{ps['carbs_g']:.0f} g")
        c4.metric(t("Fat"), f"{ps['fat_g']:.0f} g")


def micro_table(ps: dict) -> None:
    labels = {"Calcium (mg)": "calcium_mg", "Iron (mg)": "iron_mg", "Zinc (mg)": "zinc_mg",
              "Retinol (µg)": "retinol_ug", "Beta-carotene (µg)": "betacarotene_ug"}
    st.table({t(k): [f"{ps[v]:g}"] for k, v in labels.items()})
