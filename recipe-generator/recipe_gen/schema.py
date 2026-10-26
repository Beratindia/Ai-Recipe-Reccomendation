"""Recipe structure the LLM must return. Validation happens here."""
from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    name: str = Field(min_length=1)
    quantity_g: float = Field(gt=0, description="Amount in grams (use ml~g for liquids)")
    display_quantity: str = Field(default="", description='Human-friendly, e.g. "2 sendok makan"')


class Recipe(BaseModel):
    title: str = Field(min_length=1)
    cuisine: str = ""
    servings: int = Field(ge=1, le=50)
    cook_time_minutes: int | None = Field(default=None, ge=0)
    description: str = ""
    difficulty: str = "Easy"
    tags: list[str] = Field(default_factory=list)
    slot: str | None = None  # meal-plan slot, e.g. "Breakfast"
    ingredients: list[Ingredient] = Field(min_length=1)
    steps: list[str] = Field(min_length=1)
