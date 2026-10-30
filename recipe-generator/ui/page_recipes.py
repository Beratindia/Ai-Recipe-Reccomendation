import streamlit as st

from recipe_gen.analysis import Analyzed, apply_adjustment, suggest_adjustment

from . import state as S
from .shared import macro_metrics, target_controls

FILTERS = {
    "Under 600 kcal": lambda a: a.kcal < 600,
    "40 g+ protein": lambda a: a.per_serving["protein_g"] >= 40,
    "Under 15 g fat": lambda a: a.per_serving["fat_g"] < 15,
}


def _sort_key(mode: str):
    return {
        "Best match": lambda a: (-a[1].match.percent, abs(a[1].delta or 0)),
        "Highest protein": lambda a: -a[1].per_serving["protein_g"],
        "Lowest calories": lambda a: a[1].kcal,
        "Closest to target": lambda a: abs(a[1].delta) if a[1].delta is not None else 9999,
    }[mode]


def _apply(idx: int, adj) -> None:
    st.session_state.recipes[idx] = apply_adjustment(st.session_state.recipes[idx], adj)


def _log(a: Analyzed) -> None:
    S.log_meal(a.recipe, a.per_serving)
    st.toast(f"Logged {a.kcal:.0f} kcal")


def _plan_week() -> None:
    s = st.session_state
    bar = st.progress(0.0, text="Building your 7-day plan...")
    notes = []
    try:
        for i, day in enumerate(S.DAYS):
            notes += S.fill_day(day)
            bar.progress((i + 1) / len(S.DAYS), text=f"Planned {day}")
    except Exception as e:
        st.error(f"Could not finish the plan: {e}")
        return
    s.plan_notes = notes
    S.go("Plan")


def _card(idx: int, a: Analyzed, tol: int) -> None:
    r = a.recipe
    with st.container(border=True, key=f"card_{idx}"):
        top = st.columns([4, 1])
        top[0].subheader(r.title)
        if S.pantry_names():
            top[1].metric("Pantry match", f"{a.match.percent}%")
        meta = [f"{r.cook_time_minutes} min" if r.cook_time_minutes else None, f"{r.difficulty} prep",
                f"{r.servings} serving{'s' if r.servings != 1 else ''}"]
        st.caption(" · ".join(m for m in meta if m) + ("  ·  " + ", ".join(r.tags[:3]) if r.tags else ""))
        if r.description:
            st.write(r.description)
        macro_metrics(a.per_serving, f"r{idx}")
        if a.target_kcal is not None:
            ok = abs(a.delta) <= tol
            (st.success if ok else st.warning)(
                f"{a.accuracy}% calorie accuracy · {a.delta:+.0f} kcal vs target {a.target_kcal}")
        if a.match.missing:
            st.caption("Missing: " + ", ".join(m.title() for m in a.match.missing))
        if a.coverage < 85:
            st.caption(f"Nutrition covers {a.coverage}% of the ingredient weight; the rest is not in the food table.")
        if a.target_kcal is not None and abs(a.delta) > tol:
            adj = suggest_adjustment(r, a.nutrition, a.target_kcal, tol)
            if adj:
                st.info(f"**Calorie precision customizer:** {adj.verb} **{adj.ingredient}** from {adj.old_g:g} g to "
                        f"{adj.new_g:g} g ({adj.kcal_change_per_serving:+.0f} kcal per serving) to land at about "
                        f"{adj.new_kcal_per_serving:.0f} kcal.")
                st.button("Apply micro-adjustment", key=f"adj_{idx}", on_click=_apply, args=(idx, adj))
        b1, b2, b3 = st.columns(3)
        b1.button("Start cooking", icon=":material/play_arrow:", key=f"cook_{idx}", type="primary", on_click=S.open_recipe, args=(r,),
                  use_container_width=True)
        b2.button("Save", icon=":material/bookmark:", key=f"save_{idx}", on_click=S.save_recipe, args=(r,), use_container_width=True)
        b3.button(f"Log {a.kcal:.0f} kcal", key=f"log_{idx}", on_click=_log, args=(a,), use_container_width=True)


def show() -> None:
    s = st.session_state
    st.header("Recipes")
    g = S.get_goals()
    tol = g.tolerance

    with st.expander("Precision matcher: calorie target", expanded=not s.recipes):
        target_controls()

    if not s.recipes:
        st.info("No recipes yet. " + ("Add ingredients in the Pantry tab first." if not s.pantry
                                       else "Generate some ideas from your pantry."))
        for note in s.removed_notes:
            st.warning(note)
        c1, c2 = st.columns(2)
        c1.button("Go to Pantry", on_click=S.go, args=("Pantry",), use_container_width=True)
        if s.pantry and c2.button("Generate now", type="primary", use_container_width=True):
            if S.generate_for_recipes():
                st.rerun()
        return

    bits = [f"{len(s.pantry)} pantry item{'s' if len(s.pantry) != 1 else ''}" if s.pantry else "any ingredients", g.diet,
            f"{g.target_kcal} kcal target" if g.target_kcal else None, ", ".join(g.exclusions) or None,
            f"for {s.recipe_context}" if s.recipe_context else None]
    st.caption("Based on " + " · ".join(b for b in bits if b))

    st.pills("Sort", S.SORTS, key="sort_by")
    st.pills("Quick filters", list(FILTERS), selection_mode="multi", key="quick_filters")
    items = [(i, S.analyzed(r)) for i, r in enumerate(s.recipes)]
    for name in s.quick_filters or []:
        items = [(i, a) for i, a in items if FILTERS[name](a)]
    items.sort(key=_sort_key(s.sort_by or "Best match"))

    for note in s.removed_notes:
        st.warning(note + ". Try again for more options.")
    if not items:
        st.info("No recipes match these filters. Clear a filter or generate again.")
    else:
        st.subheader(f"Matched recipes ({len(items)})")
        for idx, a in items:
            _card(idx, a, tol)
        top = items[0][1]
        if top.match.have:
            st.success(f"**Zero food waste tip:** cooking {top.recipe.title} today uses up your "
                       + ", ".join(h.title() for h in top.match.have[:4]) + ".")

    c1, c2 = st.columns(2)
    if c1.button("Regenerate with fresh ideas", icon=":material/refresh:", key="regen", use_container_width=True):
        if S.generate_for_recipes(s.recipe_context or None):
            st.rerun()
    if c2.button("Generate 7-day meal plan", icon=":material/calendar_month:", key="plan_week_btn", type="primary", use_container_width=True):
        _plan_week()
        st.rerun()

    if s.saved:
        with st.expander(f"Saved recipes ({len(s.saved)})"):
            for i, r in enumerate(s.saved):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{r.title}**")
                c2.button("Open", key=f"saved_{i}", on_click=S.open_recipe, args=(r,))
