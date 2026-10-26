import streamlit as st

from recipe_gen.analysis import Analyzed, apply_adjustment, suggest_adjustment

from . import state as S
from .components import chip, esc, macro_strip, render, top_bar, visual, empty_state


def _apply(idx: int, adj) -> None:
    st.session_state.recipes[idx] = apply_adjustment(st.session_state.recipes[idx], adj)


def _sort_key(mode: str):
    return {
        "Best match": lambda a: (-a[1].match.percent, abs(a[1].delta or 0)),
        "Highest protein": lambda a: -a[1].per_serving["protein_g"],
        "Lowest calories": lambda a: a[1].kcal,
        "Closest to target": lambda a: abs(a[1].delta) if a[1].delta is not None else 9999,
    }[mode]


def _meta(a: Analyzed) -> str:
    r = a.recipe
    bits = []
    if r.cook_time_minutes:
        bits.append(f"⏱ {r.cook_time_minutes} min")
    bits.append(f"👩‍🍳 {esc(r.difficulty)} prep")
    bits.append(f"👥 {r.servings} serving{'s' if r.servings != 1 else ''}")
    return "".join(f"<span>{b}</span>" for b in bits)


def _target_chips(a: Analyzed, tol: int) -> str:
    if a.target_kcal is None:
        return ""
    ok = abs(a.delta) <= tol
    return (chip(f"{a.accuracy}% calorie accuracy", "match" if ok else "warn")
            + chip(f"{a.delta:+d} kcal vs {a.target_kcal}", "match" if ok else "warn"))


def _hero(idx: int, a: Analyzed, tol: int) -> None:
    r = a.recipe
    with st.container(border=True, key="hero"):
        badges = {"tl": f"✨ {a.match.percent}% Pantry Match" if S.pantry_names() else "✨ AI Curated"}
        if a.match.missing:
            miss = ", ".join(m.title() for m in a.match.missing[:2]) + (" +" + str(len(a.match.missing) - 2) if len(a.match.missing) > 2 else "")
            badges["bl"] = f"🛒 Missing: {miss}"
        render(visual(r.title, [i.name for i in r.ingredients], 190, badges))
        render(f'<div class="meta-row">{_meta(a)}</div>')
        render(f'<p class="h-md">{esc(r.title)}</p>')
        if r.description:
            render(f'<p class="sub">{esc(r.description)}</p>')
        render(macro_strip(a.per_serving))
        chips = _target_chips(a, tol) + "".join(chip(t, "info") for t in r.tags[:2])
        if chips:
            render(f'<div class="chip-row">{chips}</div>')
        if a.coverage < 85:
            st.caption(f"Nutrition covers {a.coverage}% of the ingredient weight; the rest is not in the food table.")
        if a.target_kcal is not None and abs(a.delta) > tol:
            adj = suggest_adjustment(r, a.nutrition, a.target_kcal, tol)
            if adj:
                with st.container(border=True):
                    render(f"""<p class="eyebrow">Calorie precision customizer</p>
                      <p style="margin:4px 0 0;font-size:14px;line-height:21px">{adj.verb} <b>{esc(adj.ingredient)}</b> from
                      {adj.old_g:g} g to {adj.new_g:g} g ({adj.kcal_change_per_serving:+.0f} kcal per serving)
                      to land at about <b>{adj.new_kcal_per_serving:.0f} kcal</b>.</p>""")
                    st.button("✔ Apply micro-adjustment", key="apply_adj", on_click=_apply, args=(idx, adj), use_container_width=True)
        c1, c2 = st.columns([4, 1])
        c1.button("📖 Start Cooking", key="hero_cook", type="primary", use_container_width=True, on_click=S.open_recipe, args=(r,))
        c2.button("🔖", key="hero_save", use_container_width=True, on_click=S.save_recipe, args=(r,), help="Save recipe")


def _row(idx: int, a: Analyzed, tol: int) -> None:
    r = a.recipe
    with st.container(border=True, key=f"row_{idx}"):
        c1, c2, c3 = st.columns([1.3, 3.6, 0.9])
        with c1:
            render(visual(r.title, [i.name for i in r.ingredients], 86))
        with c2:
            m = f'<span class="chip match">{a.match.percent}% match</span>' if S.pantry_names() else ""
            render(f"""{m}<div class="h-sm" style="margin:6px 0 4px;font-size:15px">{esc(r.title)}</div>
              <div class="chip-row">{chip(f"{a.per_serving['protein_g']:.0f}g protein", "protein")}{chip(f"{a.kcal:.0f} kcal", "kcal")}</div>""")
        with c3:
            st.button("›", key=f"open_{idx}", on_click=S.open_recipe, args=(r,), use_container_width=True)
        extra = _target_chips(a, tol)
        if extra:
            render(f'<div class="chip-row">{extra}</div>')


def show() -> None:
    s = st.session_state
    top_bar("Recipes", S.is_demo())
    g = S.get_goals()
    tol = g.tolerance

    if not s.recipes:
        empty_state("🍳", "No recipes yet", "Add ingredients in the Pantry tab and generate some ideas." if not s.pantry
                    else "Tap generate to get recipes from your pantry.")
        for note in s.removed_notes:
            st.warning(note)
        c1, c2 = st.columns(2)
        c1.button("Go to Pantry", on_click=S.go, args=("Pantry",), use_container_width=True)
        if s.pantry and c2.button("✨ Generate now", type="primary", use_container_width=True):
            if S.generate_for_recipes():
                st.rerun()
        return

    ctx = f"{len(s.pantry)} pantry item{'s' if len(s.pantry) != 1 else ''}" if s.pantry else "any ingredients"
    bits = [ctx, g.diet, f"{g.target_kcal} kcal target" if g.target_kcal else None, ", ".join(g.exclusions) or None,
            f"for {s.recipe_context}" if s.recipe_context else None]
    render(f"""<div class="card-tint"><span class="eyebrow">AI chef ●</span>
      <div style="font-size:14px;margin-top:2px">Based on {esc(' • '.join(b for b in bits if b))}</div></div>""")

    st.pills("Sort", S.SORTS, key="sort_by", label_visibility="collapsed")
    mode = s.sort_by or "Best match"
    items = [(i, S.analyzed(r)) for i, r in enumerate(s.recipes)]
    items.sort(key=_sort_key(mode))

    for note in s.removed_notes:
        st.warning(note + ". Try again for more options.")

    if not items:
        empty_state("🚫", "Nothing left after the dietary check",
                    "Every recipe broke one of your exclusions. Generate again or relax an exclusion.")
    else:
        _hero(*items[0], tol)
        if len(items) > 1:
            render(f'<div class="section-row"><p class="h-md">More chef pairings <span class="count-badge">{len(items) - 1}</span></p></div>')
            for idx, a in items[1:]:
                _row(idx, a, tol)
        top = items[0][1]
        if top.match.have:
            uses = ", ".join(h.title() for h in top.match.have[:4])
            render(f"""<div class="card-mint"><div class="insight"><div class="ic">💡</div><div>
              <div class="eyebrow">Zero food waste tip</div><p style="margin:2px 0 0;font-size:14px;line-height:21px">
              Cooking <b>{esc(top.recipe.title)}</b> today uses up your {esc(uses)}.</p></div></div></div>""")

    st.markdown('<div class="btn-amber">', unsafe_allow_html=True)
    if st.button("🪄 Regenerate with fresh ideas", key="regen", use_container_width=True):
        if S.generate_for_recipes(s.recipe_context or None):
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if s.saved:
        with st.expander(f"🔖 Saved recipes ({len(s.saved)})"):
            for i, r in enumerate(s.saved):
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{r.title}**")
                c2.button("Open", key=f"saved_{i}", on_click=S.open_recipe, args=(r,))
