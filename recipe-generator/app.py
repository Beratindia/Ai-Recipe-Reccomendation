import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from ui import page_cook, page_goals, page_pantry, page_plan, page_recipes, page_recovery  # noqa: E402
from ui import state as S  # noqa: E402
from ui import theme  # noqa: E402

st.set_page_config(page_title="NutriChef", page_icon=":material/restaurant:", layout="centered")
S.init_state()
theme.apply()

PAGE_FUNCS = {"Pantry": page_pantry, "Goals": page_goals, "Recipes": page_recipes, "Cook": page_cook,
              "Plan": page_plan, "Recovery": page_recovery}


def _import() -> None:
    f = st.session_state.get("import_file")
    try:
        S.import_data(f.getvalue().decode("utf-8"))
        st.session_state.import_msg = "Your data was loaded."
    except Exception as e:
        st.session_state.import_msg = f"Could not load that file: {e}"


theme.brand(S.is_demo())
if S.is_demo():
    st.caption("Demo mode: no Gemini API key found, so recipes come from a simple built-in template. "
               "Add GEMINI_API_KEY to get real AI recipes.")

with st.container(key="nav"):
    cols = st.columns(len(S.PAGES))
    for col, (name, icon) in zip(cols, S.PAGES):
        col.button(name, icon=icon, key=f"nav_{name}", use_container_width=True, on_click=S.go, args=(name,),
                   type="primary" if st.session_state.page == name else "secondary")

PAGE_FUNCS[st.session_state.page].show()

st.divider()
with st.expander("Save or load my data"):
    st.caption("Your pantry, settings, saved recipes, meal plan and log live only in this browser session. "
               "Download them to keep them, and load the file next time.")
    st.download_button("Download my data", S.export_data(), file_name="nutrichef_data.json", key="dl_data",
                       icon=":material/download:")
    st.file_uploader("Load a saved file", type=["json"], key="import_file")
    if st.session_state.get("import_file") is not None:
        st.button("Load this file", key="do_import", on_click=_import)
    if st.session_state.get("import_msg"):
        st.caption(st.session_state.pop("import_msg"))
st.caption("Nutrition values are estimates from a food-composition table. Not medical advice.")
