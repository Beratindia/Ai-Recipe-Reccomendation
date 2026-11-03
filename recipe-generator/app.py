import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from ui import page_cook, page_goals, page_pantry, page_plan, page_recipes, page_recovery  # noqa: E402
from ui import state as S  # noqa: E402
from ui import theme  # noqa: E402
from ui.i18n import LANGUAGES, t  # noqa: E402

st.set_page_config(page_title="NutriChef", page_icon=":material/restaurant:", layout="centered")
S.init_state()
theme.apply()

PAGE_FUNCS = {"Pantry": page_pantry, "Goals": page_goals, "Recipes": page_recipes, "Cook": page_cook,
              "Plan": page_plan, "Recovery": page_recovery}


def _import() -> None:
    f = st.session_state.get("import_file")
    try:
        S.import_data(f.getvalue().decode("utf-8"))
        st.session_state.import_msg = t("Your data was loaded.")
    except Exception as e:
        st.session_state.import_msg = t("Could not load that file: {e}", e=e)


head_l, head_r = st.columns([5, 3])
with head_l:
    theme.brand(S.is_demo())
with head_r:
    st.radio("Language", LANGUAGES, key="lang", horizontal=True, label_visibility="collapsed")
if S.is_demo():
    st.caption(t("Demo mode: no Gemini API key found, so recipes come from a simple built-in template. "
                 "Add GEMINI_API_KEY to get real AI recipes."))

FEATURED = ["Pantry", "Recipes", "Plan"]          # big cards
TILES = ["Goals", "Cook", "Recovery"]             # small tiles, then "More"
ICONS = dict(S.PAGES)


def _nav_button(col, name: str, label: str) -> None:
    col.button(label, icon=ICONS[name], key=f"nav_{name}", use_container_width=True, on_click=S.go, args=(name,),
               type="primary" if st.session_state.page == name else "secondary")


with st.container(key="launch"):
    with st.container(key="launch_main"):
        for col, name in zip(st.columns(3), FEATURED):
            _nav_button(col, name, t(name))
    with st.container(key="launch_more"):
        cols = st.columns(len(TILES) + 1)
        for col, name in zip(cols, TILES):
            _nav_button(col, name, t(name))
        with cols[-1].popover(t("More"), icon=":material/apps:", use_container_width=True):
            st.caption(t("Your pantry, settings, saved recipes, meal plan and log live only in this browser session. "
                         "Download them to keep them, and load the file next time."))
            st.download_button(t("Download my data"), S.export_data(), file_name="nutrichef_data.json", key="dl_data",
                               icon=":material/download:")
            st.file_uploader(t("Load a saved file"), type=["json"], key="import_file")
            if st.session_state.get("import_file") is not None:
                st.button(t("Load this file"), key="do_import", on_click=_import)
            if st.session_state.get("import_msg"):
                st.caption(st.session_state.pop("import_msg"))

PAGE_FUNCS[st.session_state.page].show()

st.divider()
st.caption(t("Nutrition values are estimates from a food-composition table. Not medical advice."))
