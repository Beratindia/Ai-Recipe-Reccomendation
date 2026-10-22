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

## Nutrition data

`data/food_composition.csv` is generated from the project dataset (Indonesian recipes with
per-ingredient composition, values already adjusted for the edible portion / BDD).
Columns: `name, aliases, kcal, protein_g, fat_g, carbs_g, calcium_mg, iron_mg, zinc_mg,
retinol_ug, betacarotene_ug, source` (per 100 g; `source` is `dataset` or `sample_approx`).

```bash
python scripts/build_food_db.py path/to/data.json          # regenerate the CSV
python scripts/validate_against_dataset.py path/to/data.json  # accuracy check
```

`sample_approx` rows are rough fallback values for common foods the dataset does not cover
(e.g. daging sapi, kangkung, brokoli). Replace them as you get better data.

## Switching LLM provider

Only `call_llm()` in `recipe_gen/llm.py` talks to the provider. Replace its body with
your provider's call; it just needs to return the reply text.
