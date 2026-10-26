"""Offline demo 'LLM' so the app can be tried (and tested) without an API key.

It reads the same prompt the real model gets and returns template recipes in the same JSON shape.
Real recipes need a real model: set GEMINI_API_KEY.
"""
import json
import re

PROTEINS = ["ayam", "telur", "tahu", "tempe", "ikan", "udang", "daging sapi", "salmon"]


def _line(user: str, key: str, default: str = "") -> str:
    m = re.search(rf"^{re.escape(key)}[^:]*:\s*(.*)$", user, re.M)
    return m.group(1).strip() if m else default


def _pick(items: list[str]) -> tuple[str, str]:
    low = [i.lower() for i in items]
    main = next((i for p in PROTEINS for i in low if p in i), low[0] if low else "ayam")
    veg = next((i for i in low if i != main), "tomat")
    return main, veg


def _recipe(kind: int, main: str, veg: str, servings: int, cuisine: str, slot: str | None) -> dict:
    s = servings
    en = cuisine.lower().startswith("international")
    tmpl = [
        dict(
            title=f"Stir-Fried {main.title()} with Garlic" if en else f"Tumis {main.title()} Bumbu Bawang",
            time=25, tags=["High-Protein", "Stovetop"],
            desc="A quick, fragrant stir-fry with garlic, shallot and a touch of sweet soy.",
            ing=[(main, 130 * s, f"{130 * s} g"), ("bawang putih", 10 * s, f"{2 * s} siung"),
                 ("bawang merah", 20 * s, f"{2 * s} siung"), ("cabai merah", 15 * s, f"{s} buah"),
                 (veg, 60 * s, f"{60 * s} g"), ("kecap manis", 10 * s, f"{s} sdm"),
                 ("minyak goreng", 10 * s, f"{s} sdm"), ("garam", 2 * s, "secukupnya")],
            steps=[f"Iris {main}, bawang putih, bawang merah dan cabai.",
                   "Panaskan minyak, tumis bawang sampai harum, sekitar 2 menit.",
                   f"Masukkan {main} dan masak 8 menit sampai matang.",
                   f"Tambahkan {veg}, kecap manis dan garam, aduk 3 menit.",
                   "Sajikan hangat."]),
        dict(
            title=f"Lemon Herb {main.title()}" if en else f"{main.title()} Panggang Lemon",
            time=30, tags=["Air-Fryer Friendly", "Light"],
            desc="Tender and juicy with bright lemon and garlic, ready with almost no effort.",
            ing=[(main, 150 * s, f"{150 * s} g"), ("jeruk nipis", 15 * s, f"{s} buah"),
                 ("bawang putih", 8 * s, f"{s} siung"), ("minyak goreng", 6 * s, f"{s} sdt"),
                 ("merica", 1 * s, "secukupnya"), ("garam", 2 * s, "secukupnya"), (veg, 80 * s, f"{80 * s} g")],
            steps=[f"Lumuri {main} dengan jeruk nipis, bawang putih cincang, garam dan merica. Diamkan 10 menit.",
                   "Panaskan air fryer atau oven 190 derajat.",
                   f"Panggang {main} selama 15 menit sampai matang, balik di tengah waktu.",
                   f"Kukus atau tumis {veg} selama 4 menit sebagai pendamping.",
                   "Sajikan dengan perasan jeruk nipis."]),
        dict(
            title=f"Light {main.title()} & Vegetable Soup" if en else f"Sup {main.title()} Sayuran",
            time=35, tags=["Comforting", "Low-Fat"],
            desc="A warm, light soup with plenty of vegetables, good for any time of day.",
            ing=[(main, 110 * s, f"{110 * s} g"), ("wortel", 50 * s, f"{s} buah"), ("kentang", 70 * s, f"{s} buah"),
                 ("daun bawang", 8 * s, f"{s} batang"), ("bawang putih", 8 * s, f"{s} siung"),
                 ("air", 300 * s, f"{300 * s} ml"), ("garam", 2 * s, "secukupnya"), ("merica", 1 * s, "secukupnya")],
            steps=["Tumis bawang putih sampai harum, 1 menit.",
                   f"Masukkan air dan {main}, rebus 15 menit.",
                   "Tambahkan wortel dan kentang, masak 10 menit sampai empuk.",
                   "Bumbui dengan garam dan merica, taburi daun bawang."]),
        dict(
            title="Egg Scramble with Vegetables" if en else f"Orak-Arik Telur {veg.title()}",
            time=12, tags=["Quick", "Breakfast"],
            desc="Soft eggs with vegetables, done in minutes.",
            ing=[("telur", 55 * s, f"{s} butir"), (veg, 50 * s, f"{50 * s} g"), ("bawang merah", 10 * s, f"{s} siung"),
                 ("minyak goreng", 5 * s, f"{s} sdt"), ("garam", 1 * s, "secukupnya")],
            steps=["Kocok telur dengan garam.", "Tumis bawang merah dan sayuran 3 menit.",
                   "Tuang telur, aduk perlahan 3 menit sampai matang."]),
    ]
    t = tmpl[kind % len(tmpl)]
    return {
        "title": t["title"], "cuisine": cuisine, "servings": s, "cook_time_minutes": t["time"],
        "difficulty": "Easy", "description": t["desc"], "tags": t["tags"], "slot": slot,
        "ingredients": [{"name": n, "quantity_g": q, "display_quantity": d} for n, q, d in t["ing"]],
        "steps": t["steps"],
    }


def demo_llm(system: str, user: str) -> str:
    n = int(_line(user, "Number of recipes", "3") or 3)
    servings = int(_line(user, "Servings", "2") or 2)
    cuisine = _line(user, "Cuisine", "Indonesian")
    items = [i.strip() for i in _line(user, "Available ingredients").split(",") if i.strip() and "any common" not in i]
    main, veg = _pick(items)
    slots = re.findall(r"(\w+) about \d+ kcal", _line(user, "Meal slots"))
    if slots:
        order = {"Breakfast": 3, "Lunch": 0, "Snack": 1, "Dinner": 2}
        recipes = [_recipe(order.get(sl, i), main, veg, servings, cuisine, sl) for i, sl in enumerate(slots)]
    else:
        recipes = [_recipe(i, main, veg, servings, cuisine, None) for i in range(n)]
    return json.dumps({"recipes": recipes})
