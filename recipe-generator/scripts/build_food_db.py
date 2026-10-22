"""Build data/food_composition.csv from the recipe/nutrition JSON dataset.

Usage:
    python scripts/build_food_db.py path/to/data.json [--out data/food_composition.csv]

The JSON is expected to look like {"data": [ {recipe..., "composition": [...]}, ... ]}.
Truncated files are tolerated: every complete recipe record is used.

Values in the dataset are per gram of *as-purchased* weight (already adjusted for the
edible portion, "BDD"), so the CSV stores them per 100 g in the same convention.
"""
import argparse
import collections
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

# per-gram field in the JSON -> column in the CSV (values multiplied by 100)
FIELDS = {
    "calories_per_gram": "kcal",
    "protein_per_gram": "protein_g",
    "fat_per_gram": "fat_g",
    "carbohydrate_per_gram": "carbs_g",
    "calcium_per_gram": "calcium_mg",
    "iron_per_gram": "iron_mg",
    "zinc_per_gram": "zinc_mg",
    "retinol_per_gram": "retinol_ug",
    "betakaroten_per_gram": "betacarotene_ug",
}

# English names so international-style inputs match too
ENGLISH = {
    "Ayam, daging, segar": ["chicken", "chicken breast", "chicken meat"],
    "Bawang merah, segar": ["shallot", "shallots"],
    "Bawang putih, segar": ["garlic"],
    "Bawang bombay, segar": ["onion", "onions", "yellow onion"],
    "Cabai merah, segar": ["red chili", "red chilli", "chili", "chilli"],
    "Cabai rawit, segar": ["bird's eye chili", "bird eye chili"],
    "Cabai hijau, segar": ["green chili", "green chilli"],
    "Tomat merah, segar": ["tomato", "tomatoes"],
    "Kentang, segar": ["potato", "potatoes"],
    "Wortel, segar": ["carrot", "carrots"],
    "Bayam, segar": ["spinach"],
    "Jahe, segar": ["ginger"],
    "Jeruk nipis, segar": ["lime"],
    "Telur ayam ras, segar": ["egg", "eggs"],
    "Tempe kedelai murni, mentah": ["tempeh"],
    "Tahu goreng": ["tofu", "fried tofu"],
    "Santan murni": ["coconut milk"],
    "Minyak kelapa": ["oil", "cooking oil", "vegetable oil", "coconut oil"],
    "Gula putih": ["sugar", "white sugar"],
    "Gula aren": ["palm sugar"],
    "Kecap": ["soy sauce", "sweet soy sauce"],
    "Nasi": ["rice", "cooked rice", "steamed rice"],
    "Beras ladang, mentah": ["uncooked rice", "raw rice"],
    "Udang, segar": ["shrimp", "prawn", "prawns"],
    "Terong, segar": ["eggplant", "aubergine"],
    "Ketimun, segar": ["cucumber"],
    "Kacang tanah, kering": ["peanut", "peanuts"],
    "Kacang panjang, segar": ["long beans", "yardlong beans"],
    "Buncis, segar": ["green beans", "string beans"],
    "Jagung muda, rebus": ["corn", "sweet corn"],
    "Merica, kering": ["pepper", "black pepper"],
    "Ketumbar, kering": ["coriander"],
    "Kunyit, segar": ["turmeric"],
    "Boros laja (lengkuas), segar": ["galangal"],
    "Daun bawang merah, segar": ["spring onion", "scallion", "green onion"],
    "Seledri, segar": ["celery"],
    "Daun kubis, segar": ["cabbage"],
    "Sawi, segar": ["mustard greens"],
    "Selada, segar": ["lettuce"],
    "Saos tomat": ["ketchup", "tomato sauce"],
    "Ikan tongkol, segar": ["tuna", "skipjack tuna"],
    "Ikan teri, segar": ["anchovy", "anchovies"],
    "Terasi": ["shrimp paste"],
    "Tepung singkong/ Tapioka": ["tapioca flour", "tapioca starch"],
    "Bihun Jagung, mentah": ["rice vermicelli", "glass noodles"],
}


# short names too ambiguous to be an alias ("sapi" alone would mean beef, not liver sausage)
TOO_GENERIC = {"sapi"}


def load_records(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
        return data["data"] if isinstance(data, dict) else data
    except json.JSONDecodeError:
        print("Warning: file is not valid JSON (truncated?). Using complete records only.")
    dec, i, recs = json.JSONDecoder(), text.index("[") + 1, []
    while True:
        while text[i] in " \n\r\t,":
            i += 1
        try:
            obj, i = dec.raw_decode(text, i)
        except Exception:
            break
        recs.append(obj)
    return recs


def clean_alias(a: str) -> str | None:
    a = a.lower().strip()
    if not a or re.search(r"[\d()]", a) or len(a) > 35 or len(a.split()) > 4:
        return None
    return a


def build(recs: list[dict]) -> pd.DataFrame:
    foods: dict[str, dict] = {}
    alias_votes: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in recs:
        for c in r.get("composition", []):
            name = c.get("name_of_material")
            if not name:
                continue
            foods.setdefault(name, c)
            a = clean_alias(c.get("ingredient", ""))
            if a:
                alias_votes[a][name] += 1
    # an alias belongs to the food it was most often matched to
    aliases: dict[str, set] = collections.defaultdict(set)
    for a, votes in alias_votes.items():
        aliases[votes.most_common(1)[0][0]].add(a)
    # short name ("ayam" from "Ayam, daging, segar") is only a safe alias if no other food shares it
    shorts: dict[str, list] = collections.defaultdict(list)
    for name in foods:
        shorts[name.split(",")[0].strip().lower()].append(name)
    rows = []
    for name, c in sorted(foods.items()):
        short = name.split(",")[0].strip().lower()
        owners = shorts[short]
        short_ok = (len(owners) == 1 or short in aliases[name]) and short not in TOO_GENERIC
        al = aliases[name] | ({short} if short_ok else set()) | set(ENGLISH.get(name, []))
        al.discard(name.lower())
        row = {"name": name, "aliases": ";".join(sorted(al))}
        for src, dst in FIELDS.items():
            v = c.get(src)  # missing in the data -> blank, never a fake 0
            row[dst] = round(float(v) * 100, 2) if v is not None else float("nan")
        row["source"] = "dataset"
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path", type=Path)
    ap.add_argument("--out", type=Path, default=ROOT / "data" / "food_composition.csv")
    ap.add_argument("--sample", type=Path, default=ROOT / "data" / "food_composition_sample.csv",
                    help="approximate fallback foods, added only if not covered by the dataset")
    args = ap.parse_args()

    df = build(load_records(args.json_path))
    print(f"{len(df)} foods from dataset")

    if args.sample.exists():
        sample = pd.read_csv(args.sample)
        keys = set()
        for _, r in df.iterrows():
            keys |= {k.strip().lower() for k in [r["name"], *r["aliases"].split(";")] if k.strip()}
        keep = []
        for _, r in sample.iterrows():
            names = {r["name"].lower(), *[x.strip().lower() for x in str(r["aliases"]).split(";")]}
            if not names & keys:
                keep.append({**r.to_dict(), "source": "sample_approx"})
        print(f"+ {len(keep)} fallback foods from sample file")
        df = pd.concat([df, pd.DataFrame(keep)], ignore_index=True)

    df.to_csv(args.out, index=False)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
