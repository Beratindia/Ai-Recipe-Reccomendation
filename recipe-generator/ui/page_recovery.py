import streamlit as st

from recipe_gen.wellness import CONDITIONS, DISCLAIMER

from . import state as S
from .i18n import plural, t
from .shared import macro_metrics


def _generate(key: str) -> None:
    s = st.session_state
    try:
        with st.spinner(t("Preparing gentle meal ideas...")):
            kept, notes = S.generate(n=2, condition=key)
    except Exception as e:
        st.error(t("Could not generate meals: {e}", e=e))
        return
    s.recovery_meals, s.recovery_notes, s.recovery_for = kept, notes, key


def show() -> None:
    s = st.session_state
    st.header(t("Recovery: food for how you feel"))
    st.caption(t(DISCLAIMER))

    st.pills(t("Condition"), list(CONDITIONS), key="condition", label_visibility="collapsed", format_func=t)
    custom = st.text_input(t("Something else?"), key="custom_condition",
                           placeholder=t("e.g. sore throat, low appetite, recovering from a stomach bug"))
    key = custom.strip() or s.condition or "Flu & Cold"
    cond = None if custom.strip() else CONDITIONS.get(key)

    if cond:
        st.subheader(t(cond.name))
        st.info(t(cond.summary))
        st.markdown(t("**Foods that tend to help**"))
        for food, why in cond.gentle:
            st.markdown(f"- **{t(food)}**: {t(why)}")
        st.markdown(t("**Foods to go easy on**"))
        for food, why in cond.limit:
            st.markdown(f"- **{t(food)}**: {t(why)}")
    else:
        st.info(t("Meal ideas for “{key}” will be mild and simple. There is no fixed guidance list for custom needs.", key=key))

    pantry_note = (plural(len(s.pantry), "using your {n} pantry item", "using your {n} pantry items") if s.pantry
                   else t("from common ingredients"))
    if st.button(t("Generate gentle meals {note}", note=pantry_note), type="primary", use_container_width=True, key="rec_gen",
                 icon=":material/restaurant_menu:"):
        _generate(key)
        st.rerun()

    if s.recovery_meals:
        st.subheader(t("Targeted meals for {x}", x=t(s.recovery_for)))
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
                    st.caption(t("Missing: {items}", items=", ".join(m.title() for m in a.match.missing)))
                st.button(t("Cook recipe now"), key=f"rec_cook_{i}", on_click=S.open_recipe, args=(r,), use_container_width=True)
    elif s.recovery_notes:
        for note in s.recovery_notes:
            st.warning(note)
