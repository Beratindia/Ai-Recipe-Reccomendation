import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from ui import page_cook, page_goals, page_pantry, page_plan, page_recipes, page_recovery  # noqa: E402
from ui import state as S  # noqa: E402

st.set_page_config(page_title="Vitality Kitchen • NutriChef", page_icon="🥗", layout="centered")
S.init_state()

from recipe_gen.ui_strings import get_text
from recipe_gen.ui_styles import get_custom_css

# Inject Vitality Kitchen Mobile Design System CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

PAGE_FUNCS = {"Pantry": page_pantry, "Goals": page_goals, "Recipes": page_recipes, "Cook": page_cook,
              "Plan": page_plan, "Recovery": page_recovery}


def _import() -> None:
    f = st.session_state.get("import_file")
    try:
        S.import_data(f.getvalue().decode("utf-8"))
        st.session_state.import_msg = "Your data was loaded."
    except Exception as e:
        st.session_state.import_msg = f"Could not load that file: {e}"


# Vitality Kitchen Mobile App Bar & Bilingual Switcher
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    cur_lang = st.session_state.get("lang", "id")
    streak_text = get_text("streak_label", lang=cur_lang)
    sub_title = get_text("app_subtitle", lang=cur_lang)
    st.markdown(
        f"""
        <div class="vk-header">
            <div class="vk-logo-group">
                <div class="vk-logo-icon">🥗</div>
                <div class="vk-title-wrap">
                    <span class="vk-app-name">Vitality Kitchen</span>
                    <span class="vk-app-sub">{sub_title}</span>
                </div>
            </div>
            <div class="vk-streak-badge">🔥 {streak_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_col2:
    current_lang_idx = 0 if st.session_state.get("lang", "id") == "id" else 1
    selected_lang = st.radio(
        "Bahasa",
        options=["🇮🇩 ID", "🇬🇧 EN"],
        index=current_lang_idx,
        horizontal=True,
        key="lang_toggle",
        label_visibility="collapsed",
    )
    new_lang = "id" if "ID" in selected_lang else "en"
    if new_lang != st.session_state.get("lang"):
        st.session_state.lang = new_lang

if S.is_demo():
    demo_msg = (
        "⚠️ **Mode Demo Aktif**: Kunci API Gemini tidak ditemukan, sehingga resep menggunakan template cerdas bawaan tanpa biaya. "
        "Tambahkan `GEMINI_API_KEY` di `.env` untuk generasi AI langsung."
        if st.session_state.get("lang") == "id"
        else "⚠️ **Demo mode**: no Gemini API key found, so recipes come from a built-in offline template. "
        "Add `GEMINI_API_KEY` in `.env` to enable live generative AI."
    )
    st.warning(demo_msg)

cols = st.columns(len(S.PAGES))
for col, (name, icon) in zip(cols, S.PAGES):
    col.button(f"{icon} {name}", key=f"nav_{name}", use_container_width=True, on_click=S.go, args=(name,),
               type="primary" if st.session_state.page == name else "secondary")

PAGE_FUNCS[st.session_state.page].show()

st.divider()
with st.expander("💾 Save or load my data"):
    st.caption("Your pantry, settings, saved recipes, meal plan and log live only in this browser session. "
               "Download them to keep them, and load the file next time.")
    st.download_button("⬇ Download my data", S.export_data(), file_name="nutrichef_data.json", key="dl_data")
    st.file_uploader("Load a saved file", type=["json"], key="import_file")
    if st.session_state.get("import_file") is not None:
        st.button("Load this file", key="do_import", on_click=_import)
    if st.session_state.get("import_msg"):
        st.caption(st.session_state.pop("import_msg"))
st.caption("Nutrition values are estimates from a food-composition table. Not medical advice.")
