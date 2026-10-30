import streamlit as st
import streamlit.components.v1 as components

from recipe_gen.analysis import recipe_text, scale_recipe, step_minutes

from . import state as S
from .shared import macro_metrics, micro_table


def _timer(minutes: int, key: str) -> None:
    """A countdown that runs in the browser (no server round trips)."""
    components.html(f"""
    <div style="font-family:sans-serif">
      <b id="t{key}" style="font-size:28px">{minutes:02d}:00</b>
      <button onclick="go{key}()" style="margin-left:12px;padding:6px 14px">Start timer</button>
    </div>
    <script>
      let left = {minutes * 60}, h = null;
      function show(){{ const m=String(Math.floor(left/60)).padStart(2,'0'), s=String(left%60).padStart(2,'0');
        document.getElementById('t{key}').textContent = m+':'+s; }}
      function go{key}(){{ if(h) return; h=setInterval(()=>{{ left--; show();
        if(left<=0){{ clearInterval(h); h=null; document.getElementById('t{key}').textContent='Done!'; }} }},1000); }}
    </script>""", height=60)


def show() -> None:
    s = st.session_state
    st.header("Cook")
    if s.current is None:
        st.info("Pick a recipe from the Recipes tab (Start cooking) to open it here.")
        c1, c2 = st.columns(2)
        c1.button("Go to Recipes", on_click=S.go, args=("Recipes",), use_container_width=True)
        if s.saved:
            c2.selectbox("or open a saved recipe", [r.title for r in s.saved], index=None, key="open_saved",
                         on_change=lambda: S.open_recipe(next(r for r in s.saved if r.title == s.open_saved)))
        return

    base = s.current
    st.subheader(base.title)
    meta = [f"{base.cook_time_minutes} min" if base.cook_time_minutes else None, base.difficulty, ", ".join(base.tags[:3])]
    st.caption(" · ".join(m for m in meta if m))
    if base.description:
        st.write(base.description)

    # portion control
    s.cook_servings = max(1, min(int(s.cook_servings or base.servings), 50))
    c1, c2, c3 = st.columns([1, 2, 1])
    c1.button("−", key="srv_minus", on_click=lambda: s.update(cook_servings=max(1, s.cook_servings - 1)), use_container_width=True)
    c2.markdown(f"<p style='text-align:center;font-size:18px'><b>{s.cook_servings}</b> serving{'s' if s.cook_servings != 1 else ''}</p>",
                unsafe_allow_html=True)
    c3.button("+", key="srv_plus", on_click=lambda: s.update(cook_servings=min(50, s.cook_servings + 1)), use_container_width=True)
    recipe = scale_recipe(base, s.cook_servings)
    a = S.analyzed(recipe)

    st.subheader("Nutrition per serving")
    macro_metrics(a.per_serving, "cook")
    with st.expander("More nutrients and ingredient breakdown"):
        micro_table(a.per_serving)
        st.dataframe(a.nutrition.per_ingredient, use_container_width=True, hide_index=True)
        if a.nutrition.unmatched:
            st.caption("Not in the food table (left out): " + ", ".join(a.nutrition.unmatched))
    if a.target_kcal:
        st.caption(f"Your target: {a.target_kcal} kcal per serving.")

    # pantry checklist
    st.subheader("Pantry checklist")
    have = set(a.match.have)
    n_have = len(have)
    st.caption(f"{n_have} of {n_have + len(a.match.missing)} ingredients in your kitchen" if s.pantry else
               "Add items to your pantry to see what you already have.")
    for i, ing in enumerate(recipe.ingredients):
        in_pantry = ing.name in have
        label = f"{ing.name} — {ing.display_quantity or ''} ({ing.quantity_g:g} g)".replace(" —  (", " (")
        st.checkbox(label + ("" if in_pantry or not s.pantry else "  "), key=f"ck_{base.title}_{i}")

    # step by step
    st.subheader("Step by step")
    steps = recipe.steps
    s.cook_step = max(0, min(s.cook_step, len(steps) - 1))
    st.progress((s.cook_step + 1) / len(steps), text=f"Step {s.cook_step + 1} of {len(steps)}")
    for i, text in enumerate(steps):
        if i < s.cook_step:
            st.markdown(f"~~{i + 1}. {text}~~")
        elif i == s.cook_step:
            with st.container(border=True, key="card_step"):
                st.markdown(f"**Step {i + 1}.** {text}")
                mins = step_minutes(text)
                if mins:
                    _timer(mins, f"{abs(hash(base.title)) % 9999}_{i}")
        else:
            st.markdown(f"{i + 1}. {text}")
    b1, b2 = st.columns(2)
    b1.button("Previous step", icon=":material/arrow_back:", key="prev_step", disabled=s.cook_step == 0, use_container_width=True,
              on_click=lambda: s.update(cook_step=s.cook_step - 1))
    if s.cook_step < len(steps) - 1:
        b2.button("Next step", icon=":material/arrow_forward:", icon_position="right", key="next_step", type="primary", use_container_width=True,
                  on_click=lambda: s.update(cook_step=s.cook_step + 1))
    else:
        b2.button("Done cooking: log it", key="done_log", type="primary", use_container_width=True,
                  on_click=lambda: (S.log_meal(recipe, a.per_serving), st.toast("Logged to today's intake")))

    c1, c2 = st.columns(2)
    c1.button("Save recipe", icon=":material/bookmark:", key="cook_save", on_click=S.save_recipe, args=(base,), use_container_width=True)
    c2.download_button("Download as text", recipe_text(recipe, a.nutrition), file_name="recipe.txt", icon=":material/download:",
                       use_container_width=True)
