import streamlit as st

from recipe_gen.goals import DIET_PRESETS, EXCLUSIONS, GOALS

from . import state as S
from .components import bar, esc, render, top_bar

PRESET_ICONS = {"Balanced": "⚖️", "Lean Muscle": "💪", "Clean Keto": "🥑", "Mediterranean": "🫒", "Heart Healthy": "❤️"}


def _set(key: str, value) -> None:
    st.session_state[key] = value


def show() -> None:
    s = st.session_state
    top_bar("Nutrition goals", S.is_demo())
    g = S.get_goals()
    target = g.target_kcal

    sub = DIET_PRESETS[g.diet][3] if g.diet in DIET_PRESETS else "Your own macro split"
    headline = f"{g.diet} · about {target} kcal per meal" if target else f"{g.diet} · no calorie target"
    render(f"""<div class="card-hero"><span class="pill-tag">{'Target active' if target else 'Target off'}</span>
      <p class="h-lg" style="margin-top:12px">{esc(headline)}</p>
      <p class="sub" style="margin-top:8px">{esc(sub)}. Recipes are written to match this and then checked against your nutrition table.</p></div>""")

    render('<p class="h-md">Diet strategy preset</p>')
    names = list(DIET_PRESETS)
    for row in range(0, len(names), 2):
        cols = st.columns(2)
        for col, name in zip(cols, names[row:row + 2]):
            p, c, f, desc, _ = DIET_PRESETS[name]
            col.button(f"{PRESET_ICONS[name]} {name}\n{desc} · {p}% protein", key=f"preset_{name}",
                       type="primary" if g.diet == name else "secondary", use_container_width=True,
                       on_click=S.apply_preset, args=(name,))

    with st.container(border=True):
        render('<p class="h-sm">Daily budget & target</p>')
        c1, c2 = st.columns([3, 2])
        c1.number_input("Daily calories (kcal)", 1000, 5000, step=50, key="daily_kcal")
        c2.radio("Meals per day", [3, 4], key="meals_pd", horizontal=True)
        st.radio("Calorie target for each recipe", ["From daily budget", "Custom", "Off"], key="target_mode", horizontal=True)
        if s.target_mode == "Custom":
            st.slider("Target energy per serving (kcal)", 250, 1000, step=10, key="custom_kcal")
            b1, b2, b3 = st.columns(3)
            for col, (kcal, lab) in zip((b1, b2, b3), ((300, "Snack"), (500, "Lean"), (700, "Hearty"))):
                col.button(f"{kcal} {lab}", key=f"q_{kcal}", on_click=_set, args=("custom_kcal", kcal), use_container_width=True)
        if target:
            st.slider("Tolerance (± kcal)", 10, 100, step=10, key="tolerance")
            render(f"""<div class="card-tint" style="display:flex;justify-content:space-around;text-align:center">
              <div><div class="eyebrow">Daily budget</div><div class="num" style="font-size:24px;font-weight:700">{g.daily_kcal:,} <small>kcal</small></div></div>
              <div><div class="eyebrow">Meal target</div><div class="num" style="font-size:24px;font-weight:700;color:var(--primary-deep)">{target} <small>kcal</small></div>
              <div class="sub">{target - g.tolerance} to {target + g.tolerance}</div></div></div>""")

    with st.container(border=True):
        render('<p class="h-sm">Goal</p>')
        st.radio("Metabolic goal", list(GOALS), key="goal", horizontal=True, label_visibility="collapsed")

    with st.container(border=True):
        render('<p class="h-sm">Macro split</p>')
        st.slider("Protein %", 5, 70, key="p_pct")
        st.slider("Carbs %", 5, 80, key="c_pct")
        st.slider("Fats %", 5, 80, key="f_pct")
        total = s.p_pct + s.c_pct + s.f_pct
        m = g.macros
        rows = [("Protein", s.p_pct, m["protein_g"], "#EA580C"), ("Carbohydrates", s.c_pct, m["carbs_g"], "#F59E0B"),
                ("Healthy fats", s.f_pct, m["fat_g"], "#059669")]
        for lab, pct, grams, color in rows:
            share = round(100 * pct / total) if total else 0
            render(f"""<div style="margin-top:10px"><div style="display:flex;justify-content:space-between;align-items:baseline">
              <span style="font-weight:700">{lab} <span class="chip info">{share}%</span></span>
              <span class="num" style="font-size:22px;font-weight:700;color:{color}">{grams}<small style="font-size:12px"> g</small></span></div>
              {bar(share, color)}</div>""")
        if total != 100:
            st.caption(f"The three values add up to {total}%, so they are scaled to 100%.")

    with st.container(border=True):
        render('<p class="h-sm">Dietary & allergy exclusions</p>')
        st.pills("Exclusions", list(EXCLUSIONS), selection_mode="multi", key="exclusions", label_visibility="collapsed")
        if s.exclusions:
            st.caption(" · ".join(f"{e}: {EXCLUSIONS[e].note}" for e in s.exclusions))

    tip = (f"Each meal aims for about {target} kcal with roughly {m['protein_g']} g protein." if target
           else "Turn on a calorie target to get meals sized for your day.")
    render(f"""<div class="card-mint"><div class="insight"><div class="ic">💡</div><div>
      <div class="eyebrow">How this is used</div><p style="margin:2px 0 0;font-size:14px;line-height:21px">{esc(tip)}
      After the AI writes a recipe, the app removes any that contain an excluded ingredient. The keyword check is a safety net, not a guarantee, so always read labels if you have a serious allergy.</p></div></div></div>""")

    with st.container(key="gen_cta"):
        if st.button("✨ Generate Meals for This Target", type="primary", use_container_width=True, key="btn_goal_gen"):
            if S.generate_for_recipes():
                st.rerun()
