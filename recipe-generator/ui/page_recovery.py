import streamlit as st

from recipe_gen.wellness import CONDITIONS, DISCLAIMER

from . import state as S
from .shared import macro_metrics


def _generate(key: str) -> None:
    s = st.session_state
    try:
        with st.spinner("Preparing gentle meal ideas..."):
            kept, notes = S.generate(n=2, condition=key)
    except Exception as e:
        st.error(f"Could not generate meals: {e}")
        return
    s.recovery_meals, s.recovery_notes, s.recovery_for = kept, notes, key


def show() -> None:
    s = st.session_state
    st.header("Recovery: food for how you feel")
    st.caption(DISCLAIMER)

    st.pills("Condition", list(CONDITIONS), key="condition", label_visibility="collapsed")
    custom = st.text_input("Something else?", key="custom_condition",
                           placeholder="e.g. sore throat, low appetite, recovering from a stomach bug")
    key = custom.strip() or s.condition or "Flu & Cold"
    cond = None if custom.strip() else CONDITIONS.get(key)

    if cond:
        st.subheader(cond.name)
        st.info(cond.summary)
        st.markdown("**Foods that tend to help**")
        for food, why in cond.gentle:
            st.markdown(f"- **{food}**: {why}")
        st.markdown("**Foods to go easy on**")
        for food, why in cond.limit:
            st.markdown(f"- **{food}**: {why}")
    else:
        st.info(f"Meal ideas for “{key}” will be mild and simple. There is no fixed guidance list for custom needs.")

    pantry_note = f"using your {len(s.pantry)} pantry item{'s' if len(s.pantry) != 1 else ''}" if s.pantry else "from common ingredients"
    if st.button(f"Generate gentle meals {pantry_note}", type="primary", use_container_width=True, key="rec_gen",
                 icon=":material/restaurant_menu:"):
        _generate(key)
        st.rerun()

    if s.recovery_meals:
        st.subheader(f"Targeted meals for {s.recovery_for}")
        for note in s.recovery_notes:
            st.warning(note)
        for i, r in enumerate(s.recovery_meals):
            a = S.analyzed(r)
            with st.container(border=True, key=f"card_rec_{i}"):
                st.markdown(f"**{r.title}**")
                if r.description:
                    st.caption(r.description)
                macro_metrics(a.per_serving, f"rec{i}")
                if a.match.missing and s.pantry:
                    st.caption("Missing: " + ", ".join(m.title() for m in a.match.missing))
                st.button("Cook recipe now", key=f"rec_cook_{i}", on_click=S.open_recipe, args=(r,), use_container_width=True)
    elif s.recovery_notes:
        for note in s.recovery_notes:
            st.warning(note)
