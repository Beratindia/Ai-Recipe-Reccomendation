"""General food guidance for common situations. NOT medical advice."""
from dataclasses import dataclass

DISCLAIMER = (
    "General food guidance only, not medical advice. If symptoms are severe, last more than a few "
    "days, or you have a medical condition or take medication, please see a doctor or dietitian."
)


@dataclass(frozen=True)
class Condition:
    name: str
    summary: str
    gentle: tuple[tuple[str, str], ...]   # (food, why)
    limit: tuple[tuple[str, str], ...]    # (food, why)
    prompt_rules: str
    blocked_keywords: tuple[str, ...] = ()


CONDITIONS: dict[str, Condition] = {
    "Flu & Cold": Condition(
        "Flu & Cold",
        "Appetite is often low and fluids matter. Warm, soft, easy-to-eat food usually goes down best.",
        (("Warm broth & soups", "Fluids and salt, easy to sip when you don't feel like eating"),
         ("Ginger & garlic", "Traditionally used for a warming, soothing effect"),
         ("Bubur (rice porridge)", "Soft, gentle on the stomach, easy energy"),
         ("Citrus & other fruit", "Fluids and vitamin C")),
        (("Very oily or heavy dishes", "Can feel hard to digest when you're unwell"),
         ("Alcohol", "Dehydrates and can make you feel worse")),
        "Warm, soft and brothy; easy to digest; low in oil; include ginger and/or garlic; moderate portion size.",
    ),
    "GERD & Acid Reflux": Condition(
        "GERD & Acid Reflux",
        "Many people find smaller, lower-fat, non-spicy meals cause fewer symptoms. Triggers differ per person.",
        (("Oatmeal, rice, bubur", "Mild and filling"),
         ("Steamed, boiled or baked lean fish & chicken", "Low fat, little irritation"),
         ("Banana, papaya, melon", "Usually less acidic than citrus"),
         ("Cooked non-acidic vegetables", "Easy to digest")),
        (("Chili, sambal & very spicy food", "Common trigger"),
         ("Fried and fatty food", "Fat slows stomach emptying"),
         ("Coffee, chocolate, mint", "Can relax the valve at the top of the stomach"),
         ("Large or late meals", "Eat smaller portions and not right before lying down")),
        "No chili or sambal; no deep frying; low fat; avoid heavy tomato and citrus; steam, boil or bake; small portion.",
        ("cabai", "cabe", "rawit", "sambal", "chili", "chilli", "cayenne"),
    ),
    "Sensitive Gut (IBS)": Condition(
        "Sensitive Gut (IBS)",
        "Triggers vary a lot between people. Simple, lightly spiced, well-cooked meals are a common starting point.",
        (("White rice, potato, plain noodles", "Easy to digest"),
         ("Eggs, tofu, chicken, fish", "Simple proteins"),
         ("Well-cooked carrot, zucchini, pumpkin", "Gentler than raw vegetables"),
         ("Ginger", "Often well tolerated")),
        (("Very spicy or very oily food", "Common trigger"),
         ("Large amounts of beans, onion, garlic", "High in fermentable carbs for some people"),
         ("Milk-heavy dishes", "Lactose bothers some people"),
         ("Carbonated drinks", "Can cause bloating")),
        "Mild spice; low oil; simple well-cooked ingredients; avoid dairy and large amounts of beans; modest portion.",
    ),
    "Muscle Recovery": Condition(
        "Muscle Recovery",
        "After hard training the body needs protein to repair and carbohydrate to refill energy stores.",
        (("Eggs, chicken, fish", "Complete protein"),
         ("Tempe & tahu", "Plant protein that is easy to find in Indonesia"),
         ("Rice, potato, sweet potato", "Carbohydrate to restore energy"),
         ("Fruit & vegetables", "Vitamins, minerals and fluids")),
        (("Very fatty meals right after training", "Slow digestion"),
         ("Alcohol", "Gets in the way of recovery and hydration")),
        "At least 30 g protein per serving plus a carbohydrate source (rice, potato, noodles); moderate fat.",
    ),
}
