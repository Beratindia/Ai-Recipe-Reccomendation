"""Save / load the user's data as one JSON file (the app has no accounts or database)."""
import json
from datetime import date

from .schema import Recipe

VERSION = 1


def _recipes(items) -> list[Recipe]:
    out = []
    for it in items or []:
        try:
            out.append(Recipe.model_validate(it))
        except Exception:
            continue  # skip anything damaged rather than failing the whole load
    return out


def dump(data: dict) -> str:
    """data keys: pantry, settings, saved (Recipes), plan {day: {slot: {recipe, accepted}}}, log."""
    plan = {
        day: {slot: {"recipe": e["recipe"].model_dump(), "accepted": bool(e.get("accepted"))}
              for slot, e in slots.items()}
        for day, slots in data.get("plan", {}).items()
    }
    return json.dumps({
        "version": VERSION,
        "pantry": data.get("pantry", []),
        "settings": data.get("settings", {}),
        "saved": [r.model_dump() for r in data.get("saved", [])],
        "plan": plan,
        "log": data.get("log", []),
    }, ensure_ascii=False, indent=1)


def load(text: str) -> dict:
    raw = json.loads(text)
    if not isinstance(raw, dict):
        raise ValueError("Not a NutriChef data file")
    plan = {}
    for day, slots in (raw.get("plan") or {}).items():
        for slot, e in (slots or {}).items():
            rs = _recipes([e.get("recipe")])
            if rs:
                plan.setdefault(day, {})[slot] = {"recipe": rs[0], "accepted": bool(e.get("accepted"))}
    return {
        "pantry": [i for i in raw.get("pantry", []) if isinstance(i, dict) and i.get("name")],
        "settings": raw.get("settings", {}) if isinstance(raw.get("settings"), dict) else {},
        "saved": _recipes(raw.get("saved")),
        "plan": plan,
        "log": [e for e in raw.get("log", []) if isinstance(e, dict) and "kcal" in e],
    }


def today() -> str:
    return date.today().isoformat()
