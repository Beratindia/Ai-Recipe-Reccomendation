import streamlit as st

from recipe_gen.analysis import Analyzed, apply_adjustment, suggest_adjustment

from . import state as S
from .i18n import plural, t
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
    st.toast(t("Logged {kcal} kcal", kcal=f"{a.kcal:.0f}"))


def _plan_week() -> None:
    s = st.session_state
    bar = st.progress(0.0, text=t("Building your 7-day plan..."))
    notes = []
    try:
        for i, day in enumerate(S.DAYS):
            notes += S.fill_day(day)
            bar.progress((i + 1) / len(S.DAYS), text=t("Planned {day}", day=t(day)))
    except Exception as e:
        st.error(t("Could not finish the plan: {e}", e=e))
        return
    s.plan_notes = notes
    S.go("Plan")


def _card(idx: int, a: Analyzed, tol: int) -> None:
    r = a.recipe
    with st.container(border=True, key=f"card_{idx}"):
        top = st.columns([4, 1])
        top[0].subheader(r.title)
        if S.pantry_names():
            top[1].metric(t("Pantry match"), f"{a.match.percent}%")
        meta = [t("{n} min", n=r.cook_time_minutes) if r.cook_time_minutes else None, t("{d} prep", d=t(r.difficulty)),
                plural(r.servings, "{n} serving", "{n} servings")]
        st.caption(" · ".join(m for m in meta if m) + ("  ·  " + ", ".join(r.tags[:3]) if r.tags else ""))
        if r.description:
            st.write(r.description)
        macro_metrics(a.per_serving, f"r{idx}")
        if a.target_kcal is not None:
            ok = abs(a.delta) <= tol
            (st.success if ok else st.warning)(
                t("{acc}% calorie accuracy · {delta} kcal vs target {target}", acc=a.accuracy, delta=f"{a.delta:+.0f}",
                  target=a.target_kcal))
        if a.match.missing:
            st.caption(t("Missing: {items}", items=", ".join(m.title() for m in a.match.missing)))
        if a.coverage < 85:
            st.caption(t("Nutrition covers {n}% of the ingredient weight; the rest is not in the food table.", n=a.coverage))
        if a.target_kcal is not None and abs(a.delta) > tol:
            adj = suggest_adjustment(r, a.nutrition, a.target_kcal, tol)
            if adj:
                st.info(t("**Calorie precision customizer:** {verb} **{ing}** from {old} g to {new} g ({chg} kcal per serving) "
                          "to land at about {kcal} kcal.", verb=t(adj.verb), ing=adj.ingredient, old=f"{adj.old_g:g}",
                          new=f"{adj.new_g:g}", chg=f"{adj.kcal_change_per_serving:+.0f}", kcal=f"{adj.new_kcal_per_serving:.0f}"))
                st.button(t("Apply micro-adjustment"), key=f"adj_{idx}", on_click=_apply, args=(idx, adj))
        b1, b2, b3 = st.columns(3)
        b1.button(t("Start cooking"), icon=":material/play_arrow:", key=f"cook_{idx}", type="primary", on_click=S.open_recipe,
                  args=(r,), use_container_width=True)
        b2.button(t("Save"), icon=":material/bookmark:", key=f"save_{idx}", on_click=S.save_recipe, args=(r,),
                  use_container_width=True)
        b3.button(t("Log {kcal} kcal", kcal=f"{a.kcal:.0f}"), key=f"log_{idx}", on_click=_log, args=(a,),
                  use_container_width=True)


def show() -> None:
    s = st.session_state
    st.header(t("Recipes"))
    g = S.get_goals()
    tol = g.tolerance

    with st.expander(t("Precision matcher: calorie target"), expanded=not s.recipes):
        target_controls()

    if not s.recipes:
        st.info(t("No recipes yet. ") + (t("Add ingredients in the Pantry tab first.") if not s.pantry
                                         else t("Generate some ideas from your pantry.")))
        for note in s.removed_notes:
            st.warning(note)
        c1, c2 = st.columns(2)
        c1.button(t("Go to Pantry"), on_click=S.go, args=("Pantry",), use_container_width=True)
        if s.pantry and c2.button(t("Generate now"), type="primary", use_container_width=True):
            if S.generate_for_recipes():
                st.rerun()
        return

    bits = [plural(len(s.pantry), "{n} pantry item", "{n} pantry items") if s.pantry else t("any ingredients"), t(g.diet),
            t("{kcal} kcal target", kcal=g.target_kcal) if g.target_kcal else None,
            ", ".join(t(e) for e in g.exclusions) or None,
            t("for {x}", x=t(s.recipe_context)) if s.recipe_context else None]
    st.caption(t("Based on {bits}", bits=" · ".join(b for b in bits if b)))

    st.pills(t("Sort"), S.SORTS, key="sort_by", format_func=t)
    st.pills(t("Quick filters"), list(FILTERS), selection_mode="multi", key="quick_filters", format_func=t)
    items = [(i, S.analyzed(r)) for i, r in enumerate(s.recipes)]
    for name in s.quick_filters or []:
        items = [(i, a) for i, a in items if FILTERS[name](a)]
    items.sort(key=_sort_key(s.sort_by or "Best match"))

    for note in s.removed_notes:
        st.warning(t("{note}. Try again for more options.", note=note))
    if not items:
        st.info(t("No recipes match these filters. Clear a filter or generate again."))
    else:
        st.subheader(t("Matched recipes ({n})", n=len(items)))
        for idx, a in items:
            _card(idx, a, tol)
        top = items[0][1]
        if top.match.have:
            st.success(t("**Zero food waste tip:** cooking {title} today uses up your {items}.", title=top.recipe.title,
                         items=", ".join(h.title() for h in top.match.have[:4])))

    c1, c2 = st.columns(2)
    if c1.button(t("Regenerate with fresh ideas"), icon=":material/refresh:", key="regen", use_container_width=True):
        if S.generate_for_recipes(s.recipe_context or None):
            st.rerun()
    if c2.button(t("Generate 7-day meal plan"), icon=":material/calendar_month:", key="plan_week_btn", type="primary",
                 use_container_width=True):
        _plan_week()
        st.rerun()

    if s.saved:
        with st.expander(t("Saved recipes ({n})", n=len(s.saved))):
            for i, r in enumerate(s.saved):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{r.title}**")
                c2.button(t("Open"), key=f"saved_{i}", on_click=S.open_recipe, args=(r,))
