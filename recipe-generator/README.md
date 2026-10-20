# AI Recipe Generator

Enter the ingredients you have, pick Indonesian or international cuisine, and get a recipe
with quantities, instructions, and estimated nutrition.

## How it works

1. User enters ingredients, preferences, cuisine, servings (`app.py`, Streamlit)
2. The LLM returns a recipe as JSON (`recipe_gen/llm.py`)
3. The JSON is validated with Pydantic and retried once if invalid (`recipe_gen/schema.py`)
4. Nutrition is calculated with pandas from a food-composition table (`recipe_gen/nutrition.py`)
   — the LLM's own nutrition numbers are never used
5. Recipe, quantities, steps, and nutrition are displayed

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # then add your API key
streamlit run app.py
pytest                   # tests run offline, no API key needed
```

## Important: replace the sample nutrition data

`data/food_composition.csv` is a small **sample** (~30 foods, approximate values per 100 g)
so the app runs out of the box. For real use, replace it with a proper dataset such as
TKPI (Tabel Komposisi Pangan Indonesia) or USDA FoodData Central, keeping the columns:
`name, aliases, kcal, protein_g, fat_g, carbs_g`. Add Indonesian and English names to `aliases`
(separated by `;`) to improve ingredient matching.

## Switching LLM provider

Only `call_llm()` in `recipe_gen/llm.py` talks to the provider. Replace its body with
your provider's call; it just needs to return the reply text.
