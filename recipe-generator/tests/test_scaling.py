"""Test portion scaling logic for recipes."""
from recipe_gen.schema import Recipe, Ingredient


def scale_recipe_ingredients(recipe: Recipe, new_servings: int):
    """Scale ingredient gram weights according to new serving count."""
    ratio = new_servings / recipe.servings
    scaled = []
    for ing in recipe.ingredients:
        scaled_weight = round(ing.quantity_g * ratio, 1)
        scaled.append({
            "name": ing.name,
            "quantity_g": scaled_weight,
            "display_quantity": f"{scaled_weight:g} g"
        })
    return scaled


def test_scale_recipe_ingredients():
    recipe = Recipe(
        title="Sup Ayam",
        cuisine="Indonesian",
        servings=2,
        cook_time_minutes=25,
        ingredients=[
            Ingredient(name="ayam", quantity_g=200, display_quantity="200 g"),
            Ingredient(name="wortel", quantity_g=100, display_quantity="100 g")
        ],
        steps=["Potong ayam", "Rebus wortel"]
    )

    scaled_4 = scale_recipe_ingredients(recipe, 4)
    assert scaled_4[0]["quantity_g"] == 400.0
    assert scaled_4[1]["quantity_g"] == 200.0

    scaled_1 = scale_recipe_ingredients(recipe, 1)
    assert scaled_1[0]["quantity_g"] == 100.0
    assert scaled_1[1]["quantity_g"] == 50.0
