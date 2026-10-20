import streamlit as st
from dotenv import load_dotenv

from recipe_gen.llm import generate_recipe
from recipe_gen.nutrition import NutritionCalculator, load_food_db

load_dotenv()

st.set_page_config(page_title="AI Recipe Generator", page_icon="🍳", layout="centered")


@st.cache_resource
def get_calculator() -> NutritionCalculator:
    return NutritionCalculator(load_food_db())


st.title("🍳 AI Recipe Generator")
st.caption("Indonesian & international cuisine")

with st.form("inputs"):
    ingredients = st.text_area(
        "Available ingredients",
        placeholder="e.g. ayam, bawang merah, bawang putih, tomat, kecap manis",
    )
    preferences = st.text_input(
        "Preferences / restrictions (optional)",
        placeholder="e.g. spicy, no peanuts, low oil",
    )
    col1, col2 = st.columns(2)
    cuisine = col1.radio("Cuisine", ["Indonesian", "International"], horizontal=True)
    servings = col2.number_input("Servings", min_value=1, max_value=20, value=2)
    submitted = st.form_submit_button("Generate recipe", type="primary")

if submitted:
    if not ingredients.strip():
        st.warning("Please enter at least one ingredient.")
        st.stop()
    try:
        with st.spinner("Cooking up a recipe..."):
            recipe = generate_recipe(ingredients, preferences, cuisine, int(servings))
            nutrition = get_calculator().calculate(recipe)
    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.stop()

    st.header(recipe.title)
    meta = f"{recipe.cuisine} · {recipe.servings} servings"
    if recipe.cook_time_minutes:
        meta += f" · {recipe.cook_time_minutes} min"
    st.caption(meta)

    st.subheader("Ingredients")
    for ing in recipe.ingredients:
        st.markdown(f"- {ing.name} — {ing.display_quantity} ({ing.quantity_g:g} g)")

    st.subheader("Instructions")
    for i, step in enumerate(recipe.steps, 1):
        st.markdown(f"{i}. {step}")

    st.subheader("Estimated nutrition (per serving)")
    ps = nutrition.per_serving
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Calories", f"{ps['kcal']:g} kcal")
    c2.metric("Protein", f"{ps['protein_g']:g} g")
    c3.metric("Fat", f"{ps['fat_g']:g} g")
    c4.metric("Carbs", f"{ps['carbs_g']:g} g")

    if nutrition.unmatched:
        st.warning(
            "Not found in the food database (excluded from totals): "
            + ", ".join(nutrition.unmatched)
        )
    with st.expander("Nutrition breakdown by ingredient"):
        st.dataframe(nutrition.per_ingredient, use_container_width=True, hide_index=True)
    st.caption("Estimates only, based on a food-composition table. Not medical advice.")
