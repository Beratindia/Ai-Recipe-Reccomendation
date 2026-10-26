import streamlit as st

from . import state as S


def show() -> None:
    s = st.session_state
    st.header("Pantry")
    st.caption("What's in your kitchen? Quantities are optional, e.g. “ayam 500g”.")

    # ---- add ingredients: typing
    with st.form("add_item", clear_on_submit=True, border=False):
        c1, c2 = st.columns([4, 1])
        text = c1.text_input("Add ingredients", placeholder="e.g. ayam 500g, bayam, telur 4 butir")
        submitted = c2.form_submit_button("Add", use_container_width=True)
    if submitted and text.strip() and S.add_pantry(text) == 0:
        st.toast("Already in your pantry.")

    # ---- add ingredients: suggestions by category
    st.pills("Category", list(S.SUGGESTIONS), key="cat")
    cols = st.columns(4)
    for i, name in enumerate(n for n in S.SUGGESTIONS[s.cat or "Proteins"] if n not in S.pantry_names()):
        cols[i % 4].button(f"+ {name}", key=f"sg_{name}", on_click=S.add_pantry, args=(name,), use_container_width=True)

    # ---- add ingredients: photo ("Snap Fridge")
    with st.expander("📷 Snap Fridge: scan a photo for ingredients"):
        if S.is_demo():
            st.info("Photo scanning needs a Gemini API key (the offline demo model cannot read images).")
        photo = st.camera_input("Take a photo", key="cam") or st.file_uploader(
            "or upload one", type=["jpg", "jpeg", "png", "webp"], key="upload")
        if photo is not None and st.button("Scan photo", key="scan_btn", disabled=S.is_demo()):
            try:
                with st.spinner("Looking at your photo..."):
                    s.scan_found = S.scan_photo(photo.getvalue(), photo.type or "image/jpeg")
            except Exception as e:
                st.error(f"Could not scan the photo: {e}")
        if s.scan_found:
            picked = st.multiselect("Found. Untick anything wrong:", s.scan_found, default=s.scan_found, key="scan_pick")
            if st.button("Add to pantry", key="scan_add"):
                S.add_pantry(", ".join(picked))
                s.scan_found = []
                st.rerun()

    # ---- current pantry
    n = len(s.pantry)
    c1, c2 = st.columns([3, 1])
    c1.subheader(f"Current pantry ({n} item{'s' if n != 1 else ''})")
    if n:
        c2.button("Clear all", key="clear_pantry", on_click=lambda: s.pantry.clear(), use_container_width=True)
    if not n:
        st.caption("Your pantry is empty. Type an ingredient above or pick a suggestion.")
    for item in s.pantry:
        c1, c2 = st.columns([5, 1])
        label = item["name"].title() + (f" · {item['qty']}" if item["qty"] else "")
        c1.write(label)
        c2.button("✕", key=f"rm_{item['name']}", on_click=S.remove_pantry, args=(item["name"],), help="Remove")

    # ---- cooking setup
    st.subheader("Cooking setup")
    c1, c2 = st.columns([3, 1])
    c1.radio("Cuisine", ["Indonesian", "International"], key="cuisine", horizontal=True)
    c2.number_input("Servings", 1, 12, key="servings")
    st.text_input("Preferences (optional)", placeholder="e.g. spicy, low oil, kid-friendly", key="prefs")
    st.pills("Available equipment (select any)", S.EQUIPMENT, selection_mode="multi", key="equipment")
    st.radio("Max prep time", list(S.PREP_OPTIONS), key="prep_time", horizontal=True)

    # ---- smart prediction: best recipe from the last batch
    if s.recipes and s.pantry:
        best = max((S.analyzed(r) for r in s.recipes), key=lambda a: a.match.percent)
        total = len(best.match.have) + len(best.match.missing)
        st.info(f"**Smart prediction:** {best.recipe.title}. Matches {len(best.match.have)} of {total} ingredients.")

    if st.button(f"✨ Generate recipes with {n} ingredient{'s' if n != 1 else ''}", type="primary",
                 use_container_width=True, key="btn_generate"):
        if S.generate_for_recipes():
            st.rerun()
