import streamlit as st

from recipe_gen.analysis import apply_adjustment, grocery_list, suggest_adjustment
from recipe_gen.goals import SLOT_SHARES, macro_grams

from . import state as S

SLOT_TIMES = {"Breakfast": "08:30", "Lunch": "13:00", "Snack": "16:30", "Dinner": "19:00"}


def _run(fn, *args) -> None:
    try:
        with st.spinner("Your AI chef is planning..."):
            st.session_state.plan_notes = fn(*args)
    except Exception as e:
        st.error(f"Could not generate meals: {e}")


def _fill_week() -> list[str]:
    notes = []
    bar = st.progress(0.0, text="Planning the week...")
    for i, day in enumerate(S.DAYS):
        notes += S.fill_day(day)
        bar.progress((i + 1) / len(S.DAYS), text=f"Planned {day}")
    return notes


def _accept(day: str, slot: str) -> None:
    st.session_state.plan[day][slot]["accepted"] = True


def _nudge(day: str, slot: str, adj) -> None:
    e = st.session_state.plan[day][slot]
    e["recipe"] = apply_adjustment(e["recipe"], adj)
    e["accepted"] = False


def _slot(day: str, slot: str, target: int) -> None:
    s = st.session_state
    e = s.plan.get(day, {}).get(slot)
    with st.container(border=True, key=f"card_{day}_{slot}"):
        st.caption(f"**{slot.upper()}** · {SLOT_TIMES[slot]} · goal {target} kcal")
        if not e:
            st.write("Nothing planned yet.")
            if st.button("Generate this slot", key=f"gen_{day}_{slot}"):
                _run(S.fill_day, day, slot)
                st.rerun()
            return
        r = e["recipe"]
        a = S.analyzed(r, target)
        c1, c2 = st.columns([4, 1])
        c1.markdown(f"**{r.title}**" + ("  (accepted)" if e["accepted"] else ""))
        c2.metric("kcal", f"{a.kcal:.0f}", label_visibility="collapsed")
        if r.description:
            st.caption(r.description)
        bits = [f"{a.per_serving['protein_g']:.0f} g protein", f"{a.per_serving['carbs_g']:.0f} g carbs",
                f"{a.per_serving['fat_g']:.0f} g fat"]
        if r.cook_time_minutes:
            bits.append(f"{r.cook_time_minutes} min")
        st.write(" · ".join(bits))
        st.caption(f"Fits slot by {a.delta:+.0f} kcal" + (" (within range)" if abs(a.delta) <= max(S.get_goals().tolerance, 15) else ""))
        b = st.columns(5)
        b[0].button("Accept", icon=":material/check:", key=f"acc_{day}_{slot}", type="primary", disabled=e["accepted"],
                    on_click=_accept, args=(day, slot), use_container_width=True)
        if b[1].button("Swap", key=f"swap_{day}_{slot}", use_container_width=True, help="Generate a different meal"):
            _run(S.fill_day, day, slot)
            st.rerun()
        for col, delta in ((b[2], -50), (b[3], +50)):
            adj = suggest_adjustment(r, a.nutrition, round(a.kcal) + delta, 0)
            col.button(f"{delta:+d} kcal", key=f"nudge_{delta}_{day}_{slot}", disabled=adj is None,
                       on_click=_nudge, args=(day, slot, adj), use_container_width=True,
                       help="Tweak one calorie-dense ingredient")
        b[4].button("Cook", key=f"cook_{day}_{slot}", on_click=S.open_recipe, args=(r,), use_container_width=True)


def show() -> None:
    s = st.session_state
    st.header("Meal plan")
    g = S.get_goals()
    day = s.plan_day or "Mon"

    # week overview
    st.pills("Day", S.DAYS, key="plan_day", label_visibility="collapsed")
    day = s.plan_day or "Mon"
    with st.container(key="weekstrip"):
        cols = st.columns(7)
        for col, d in zip(cols, S.DAYS):
            slots = s.plan.get(d, {})
            if slots and len(slots) == len(SLOT_SHARES) and all(e["accepted"] for e in slots.values()):
                status = "Done"
            else:
                status = "Planned" if slots else "Empty"
            kcal = f"{S.day_totals(d)['kcal'] / 1000:.1f}k" if slots else "-"
            cls = "wk wk-on" if d == day else "wk"
            col.markdown(f"<div class='{cls}'><b>{d}</b><span>{kcal}</span><i>{status}</i></div>",
                         unsafe_allow_html=True)

    # daily nutrition engine
    tot = S.day_totals(day)
    daily = macro_grams(g.daily_kcal, g.p, g.c, g.f)
    st.subheader(f"{day} target: {g.daily_kcal:,} kcal")
    remaining = g.daily_kcal - tot["kcal"]
    st.progress(min(tot["kcal"] / g.daily_kcal, 1.0),
                text=f"{tot['kcal']:,} kcal planned · {remaining:,} remaining" if remaining >= 0 else
                f"{tot['kcal']:,} kcal planned · {-remaining:,} over budget")
    macro_box = st.container(key="macros3_day")
    m1, m2, m3 = macro_box.columns(3)
    for col, label, key, tkey in ((m1, "Protein", "protein_g", "protein_g"), (m2, "Carbs", "carbs_g", "carbs_g"),
                                  (m3, "Fats", "fat_g", "fat_g")):
        pct = round(100 * tot[key] / daily[tkey]) if daily[tkey] else 0
        col.metric(label, f"{tot[key]} g", f"{pct}% of {daily[tkey]} g", delta_color="off")

    # auto-fill
    st.subheader("AI calorie architect")
    st.caption("Plans meals that balance your calories and macros. Accepted meals are kept.")
    c1, c2 = st.columns(2)
    if c1.button(f"Auto-fill {day}", key="fill_day", type="primary", use_container_width=True):
        _run(S.fill_day, day)
        st.rerun()
    if c2.button("Auto-fill whole week", key="fill_week", use_container_width=True):
        _run(_fill_week)
        st.rerun()
    for note in s.plan_notes:
        st.warning(note)

    # timeline
    st.subheader(f"Daily timeline ({len(SLOT_SHARES)} slots)")
    for slot, kcal in S.slot_targets():
        _slot(day, slot, kcal)
    if s.plan.get(day):
        st.button("Clear this day", key="clear_day", on_click=lambda: s.plan.pop(day, None))

    # grocery list
    st.subheader("Grocery list")
    scope = st.radio("Show for", ["This day", "Whole week"], horizontal=True, key="grocery_scope", label_visibility="collapsed")
    recipes = [e["recipe"] for e in s.plan.get(day, {}).values()] if scope == "This day" else S.plan_recipes()
    items = grocery_list(recipes, S.pantry_names(), S.get_calc())
    if not recipes:
        st.caption("Plan some meals to see what you need to buy.")
    elif not items:
        st.success("You already have everything for these meals.")
    else:
        st.caption(f"{len(items)} ingredient{'s' if len(items) != 1 else ''} not in your pantry")
        st.table({"Ingredient": [n.title() for n, _ in items], "Amount": [f"{g_:g} g" for _, g_ in items]})
        text = "Grocery list\n" + "\n".join(f"- {n.title()}: {g_:g} g" for n, g_ in items)
        c1, c2 = st.columns(2)
        c1.download_button("Download list", text, file_name="grocery_list.txt", use_container_width=True,
                           icon=":material/download:")
        c2.button("I bought these: add to pantry", key="bought", use_container_width=True,
                  on_click=lambda: S.add_pantry(", ".join(n for n, _ in items)))
