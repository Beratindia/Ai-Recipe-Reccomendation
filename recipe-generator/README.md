# AI Recipe Generator

Enter the ingredients you have, pick Indonesian or international cuisine, and get a recipe
with quantities, instructions, and estimated nutrition.

## Features

| Page | What it does |
|---|---|
| **Pantry** | Add ingredients by typing, by category suggestions, or by photo ("Snap Fridge", needs the Gemini key). Pick equipment, max prep time, cuisine, servings. Shows a smart prediction (best pantry match so far). |
| **Goals** | Diet presets (Balanced, Lean Muscle, Clean Keto, Mediterranean, Heart Healthy) with macro split in grams, calorie budget or custom target with tolerance, metabolic goal, dietary and allergy exclusions, today's intake log. |
| **Recipes** | AI recipes with real nutrition from the food table, pantry match % and missing items, calorie accuracy vs target, one-click calorie micro-adjustment, sort and quick filters, save, log, zero-waste tip, regenerate, 7-day plan. |
| **Cook** | Servings control (quantities rescale), nutrition per serving, pantry checklist, step-by-step with countdown timers read from the step text, save, download as text. |
| **Plan** | Week view, daily calorie and macro progress, auto-fill a day or the week, per-slot swap, accept, ±50 kcal tweak, grocery list (minus your pantry) with download. |
| **Recovery** | Gentle-food guidance for flu and cold, reflux, sensitive gut, muscle recovery, or your own text, plus AI meal ideas that respect it. General guidance only, not medical advice. |

All numbers shown come from the food-composition table, never from the AI. Your data lives in the browser
session; use "Save or load my data" at the bottom to keep it.

Not included yet: voice input and voice-guided cooking, streaks, recipe photos and ratings, visual design.
`design_draft/` holds an earlier styled attempt that is not used.

## How it works

1. The app builds a prompt from your pantry, equipment, goals and exclusions (`recipe_gen/llm.py`)
2. The LLM returns recipes as JSON, validated with Pydantic and retried once if invalid (`recipe_gen/schema.py`)
3. Recipes that break an exclusion are dropped (`recipe_gen/goals.py`)
4. Nutrition is calculated with pandas from the food table (`recipe_gen/nutrition.py`)
5. Pantry matching, scaling, calorie adjustment, grocery list and timers are plain functions (`recipe_gen/analysis.py`)

Without an API key the app runs in demo mode with template recipes (`recipe_gen/demo.py`), so every page can be tried offline.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # then add your API key
streamlit run app.py
python -m pytest         # tests run offline, no API key needed
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
