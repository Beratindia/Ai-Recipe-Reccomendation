import streamlit as st
import streamlit.components.v1 as components

from recipe_gen.analysis import recipe_text, scale_recipe, step_minutes

from . import state as S
from .i18n import code, plural, t
from .shared import macro_metrics, micro_table


def _timer(minutes: int, key: str) -> None:
    """A countdown that runs in the browser (no server round trips)."""
    components.html(f"""
    <div style="font-family:sans-serif">
      <b id="t{key}" style="font-size:28px">{minutes:02d}:00</b>
      <button onclick="go{key}()" style="margin-left:12px;padding:6px 14px">{t("Start timer")}</button>
    </div>
    <script>
      let left = {minutes * 60}, h = null;
      function show(){{ const m=String(Math.floor(left/60)).padStart(2,'0'), s=String(left%60).padStart(2,'0');
        document.getElementById('t{key}').textContent = m+':'+s; }}
      function go{key}(){{ if(h) return; h=setInterval(()=>{{ left--; show();
        if(left<=0){{ clearInterval(h); h=null; document.getElementById('t{key}').textContent='{t("Done!")}'; }} }},1000); }}
    </script>""", height=60)


def show() -> None:
    s = st.session_state
    st.header(t("Cook"))
    if s.current is None:
        st.info(t("Pick a recipe from the Recipes tab (Start cooking) to open it here."))
        c1, c2 = st.columns(2)
        c1.button(t("Go to Recipes"), on_click=S.go, args=("Recipes",), use_container_width=True)
        if s.saved:
            c2.selectbox(t("or open a saved recipe"), [r.title for r in s.saved], index=None, key="open_saved",
                         on_change=lambda: S.open_recipe(next(r for r in s.saved if r.title == s.open_saved)))
        return

    base = s.current
    st.subheader(base.title)
    meta = [t("{n} min", n=base.cook_time_minutes) if base.cook_time_minutes else None, t(base.difficulty),
            ", ".join(base.tags[:3])]
    st.caption(" · ".join(m for m in meta if m))
    if base.description:
        st.write(base.description)

    # portion control
    s.cook_servings = max(1, min(int(s.cook_servings or base.servings), 50))
    c1, c2, c3 = st.columns([1, 2, 1])
    c1.button("−", key="srv_minus", on_click=lambda: s.update(cook_servings=max(1, s.cook_servings - 1)), use_container_width=True)
    label = plural(s.cook_servings, "{n} serving", "{n} servings").replace(str(s.cook_servings), f"<b>{s.cook_servings}</b>", 1)
    c2.markdown(f"<p style='text-align:center;font-size:18px'>{label}</p>", unsafe_allow_html=True)
    c3.button("+", key="srv_plus", on_click=lambda: s.update(cook_servings=min(50, s.cook_servings + 1)), use_container_width=True)
    recipe = scale_recipe(base, s.cook_servings)
    a = S.analyzed(recipe)

    st.subheader(t("Nutrition per serving"))
    macro_metrics(a.per_serving, "cook")
    with st.expander(t("More nutrients and ingredient breakdown")):
        micro_table(a.per_serving)
        st.dataframe(a.nutrition.per_ingredient, use_container_width=True, hide_index=True)
        if a.nutrition.unmatched:
            st.caption(t("Not in the food table (left out): {items}", items=", ".join(a.nutrition.unmatched)))
    if a.target_kcal:
        st.caption(t("Your target: {target} kcal per serving.", target=a.target_kcal))

    # pantry checklist
    st.subheader(t("Pantry checklist"))
    have = set(a.match.have)
    n_have = len(have)
    st.caption(t("{have} of {total} ingredients in your kitchen", have=n_have, total=n_have + len(a.match.missing)) if s.pantry
               else t("Add items to your pantry to see what you already have."))
    for i, ing in enumerate(recipe.ingredients):
        in_pantry = ing.name in have
        label = f"{ing.name} — {ing.display_quantity or ''} ({ing.quantity_g:g} g)".replace(" —  (", " (")
        st.checkbox(label + ("" if in_pantry or not s.pantry else "  "), key=f"ck_{base.title}_{i}")

    # step by step
    st.subheader(t("Step by step"))
    steps = recipe.steps
    s.cook_step = max(0, min(s.cook_step, len(steps) - 1))
    st.progress((s.cook_step + 1) / len(steps), text=t("Step {a} of {b}", a=s.cook_step + 1, b=len(steps)))
    for i, text in enumerate(steps):
        if i < s.cook_step:
            st.markdown(f"~~{i + 1}. {text}~~")
        elif i == s.cook_step:
            with st.container(border=True, key="card_step"):
                st.markdown(t("**Step {n}.** {text}", n=i + 1, text=text))
                mins = step_minutes(text)
                if mins:
                    _timer(mins, f"{abs(hash(base.title)) % 9999}_{i}")
        else:
            st.markdown(f"{i + 1}. {text}")
    b1, b2 = st.columns(2)
    b1.button(t("Previous step"), icon=":material/arrow_back:", key="prev_step", disabled=s.cook_step == 0, use_container_width=True,
              on_click=lambda: s.update(cook_step=s.cook_step - 1))
    if s.cook_step < len(steps) - 1:
        b2.button(t("Next step"), icon=":material/arrow_forward:", icon_position="right", key="next_step", type="primary",
                  use_container_width=True, on_click=lambda: s.update(cook_step=s.cook_step + 1))
    else:
        b2.button(t("Done cooking: log it"), key="done_log", type="primary", use_container_width=True,
                  on_click=lambda: (S.log_meal(recipe, a.per_serving), st.toast(t("Logged to today's intake"))))

    c1, c2 = st.columns(2)
    c1.button(t("Save recipe"), icon=":material/bookmark:", key="cook_save", on_click=S.save_recipe, args=(base,),
              use_container_width=True)
    c2.download_button(t("Download as text"), recipe_text(recipe, a.nutrition, code()), file_name="recipe.txt",
                       icon=":material/download:", use_container_width=True)
