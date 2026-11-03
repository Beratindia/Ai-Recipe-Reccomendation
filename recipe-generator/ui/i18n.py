"""Display translations (English / Indonesian).

Internal values (cuisine names, diet names, page names, ...) always stay in English so saved data and logic do
not depend on the language. Only what the user sees goes through `t()`. Text with no Indonesian entry is shown
as written, so a missing translation never breaks the app.
"""
import streamlit as st

LANGUAGES = ["English", "Bahasa Indonesia"]


_last = "en"  # only read when no session is active (Streamlit's AppTest formats widget options outside a run)


def code() -> str:
    global _last
    try:
        has = "lang" in st.session_state
    except Exception:
        has = False
    if has:
        _last = "id" if str(st.session_state["lang"]).startswith("Bahasa") else "en"
    return _last


def llm_language() -> str:
    return "Indonesian" if code() == "id" else "English"


def t(_text: str, **kw) -> str:
    out = ID.get(_text, _text) if code() == "id" else _text
    return out.format(**kw) if kw else out


def plural(n: int, one: str, many: str) -> str:
    """t() of the singular or plural key, with {n} filled in."""
    return t(one if n == 1 else many, n=n)


ID = {
    # ---- app shell
    "Pantry": "Bahan", "Goals": "Target", "Recipes": "Resep", "Cook": "Masak", "Plan": "Rencana",
    "Recovery": "Pemulihan",
    "AI recipes with real nutrition": "Resep AI dengan gizi nyata",
    "Demo mode": "Mode demo",
    "Demo mode: no Gemini API key found, so recipes come from a simple built-in template. "
    "Add GEMINI_API_KEY to get real AI recipes.":
        "Mode demo: kunci API Gemini tidak ditemukan, jadi resep berasal dari templat sederhana. "
        "Tambahkan GEMINI_API_KEY untuk mendapatkan resep AI yang sebenarnya.",
    "Language": "Bahasa", "More": "Lainnya",
    "{n} item": "{n} item", "{n} items": "{n} item", "{n} idea": "{n} ide", "{n} ideas": "{n} ide",
    "New": "Baru", "{n}/7 days": "{n}/7 hari",
    "Save or load my data": "Simpan atau muat data saya",
    "Your pantry, settings, saved recipes, meal plan and log live only in this browser session. "
    "Download them to keep them, and load the file next time.":
        "Bahan, pengaturan, resep tersimpan, rencana makan, dan catatan Anda hanya ada di sesi browser ini. "
        "Unduh untuk menyimpannya, lalu muat file tersebut lain kali.",
    "Download my data": "Unduh data saya",
    "Load a saved file": "Muat file tersimpan",
    "Load this file": "Muat file ini",
    "Your data was loaded.": "Data Anda berhasil dimuat.",
    "Could not load that file: {e}": "File tidak dapat dimuat: {e}",
    "Nutrition values are estimates from a food-composition table. Not medical advice.":
        "Nilai gizi adalah perkiraan dari tabel komposisi pangan. Bukan saran medis.",

    # ---- pantry
    "What's in your kitchen? Quantities are optional, e.g. “ayam 500g”.":
        "Apa yang ada di dapur Anda? Jumlah boleh dikosongkan, misalnya “ayam 500g”.",
    "Add ingredients": "Tambah bahan",
    "e.g. ayam 500g, bayam, telur 4 butir": "mis. ayam 500g, bayam, telur 4 butir",
    "Add": "Tambah",
    "Already in your pantry.": "Sudah ada di daftar bahan Anda.",
    "Category": "Kategori",
    "Proteins": "Protein", "Veggies & Greens": "Sayuran", "Carbs": "Karbohidrat", "Aromatics": "Bumbu",
    "Current pantry ({n} item)": "Bahan saat ini ({n} item)",
    "Current pantry ({n} items)": "Bahan saat ini ({n} item)",
    "Clear all": "Hapus semua",
    "Your pantry is empty. Type an ingredient above or pick a suggestion.":
        "Daftar bahan masih kosong. Ketik bahan di atas atau pilih saran.",
    "Remove": "Hapus",
    "Cooking setup": "Pengaturan memasak",
    "Cuisine": "Masakan", "Indonesian": "Indonesia", "International": "Internasional",
    "Servings": "Porsi",
    "Preferences (optional)": "Preferensi (opsional)",
    "e.g. spicy, low oil, kid-friendly": "mis. pedas, sedikit minyak, ramah anak",
    "Available equipment (select any)": "Peralatan yang tersedia (pilih bebas)",
    "Stovetop": "Kompor", "Air Fryer": "Air Fryer", "Oven": "Oven", "Rice Cooker": "Penanak nasi",
    "Blender": "Blender", "Steamer": "Pengukus", "Microwave": "Microwave",
    "Max prep time": "Waktu masak maksimal",
    "Under 15 min": "Di bawah 15 mnt", "15-30 min": "15-30 mnt", "30-45 min": "30-45 mnt", "Any": "Bebas",
    "**Smart prediction:** {title}. Matches {have} of {total} ingredients.":
        "**Prediksi cerdas:** {title}. Cocok dengan {have} dari {total} bahan.",
    "Generate recipes with {n} ingredient": "Buat resep dari {n} bahan",
    "Generate recipes with {n} ingredients": "Buat resep dari {n} bahan",

    # ---- goals / shared
    "Nutrition goals": "Target gizi",
    "**{diet}**: about {target} kcal per meal.": "**{diet}**: sekitar {target} kcal per hidangan.",
    "**{diet}**: no calorie target.": "**{diet}**: tanpa target kalori.",
    " Recipes are written to match this, then checked against your nutrition table.":
        " Resep dibuat agar sesuai, lalu diperiksa dengan tabel gizi Anda.",
    "Diet strategy preset": "Pilihan strategi diet",
    "Balanced": "Seimbang", "Lean Muscle": "Otot Ramping", "Clean Keto": "Keto Bersih",
    "Mediterranean": "Mediterania", "Heart Healthy": "Sehat Jantung", "Custom": "Kustom",
    "Everyday balance": "Seimbang untuk sehari-hari", "High protein": "Tinggi protein", "Low carb": "Rendah karbo",
    "Wholesome, anti-inflammatory": "Menyehatkan, anti-radang", "Low sodium": "Rendah natrium",
    "{name}\n{desc} · {p}% protein": "{name}\n{desc} · {p}% protein",
    "Calories": "Kalori",
    "Macro split": "Pembagian makro",
    "Protein %": "Protein %", "Carbs %": "Karbo %", "Fats %": "Lemak %",
    "Macro": "Makro", "Share": "Porsi", "Grams per meal": "Gram per hidangan",
    "Protein": "Protein", "Carbohydrates": "Karbohidrat", "Fats": "Lemak", "Fat": "Lemak",
    "The three values add up to {total}%, so they are scaled to 100%.":
        "Ketiga nilai berjumlah {total}%, sehingga diskalakan menjadi 100%.",
    "Dietary & allergy exclusions": "Pantangan diet & alergi",
    "Exclusions": "Pantangan",
    "Gluten-Free": "Bebas Gluten", "Dairy-Free": "Bebas Susu", "Nut-Free": "Bebas Kacang", "Egg-Free": "Bebas Telur",
    "Seed-Oil Conscious": "Hindari Minyak Biji", "Halal": "Halal", "Vegetarian": "Vegetarian",
    "Celiac safe": "Aman untuk celiac", "0% lactose": "0% laktosa", "Tree nuts & peanuts": "Kacang pohon & kacang tanah",
    "No eggs": "Tanpa telur", "No canola / soy oil": "Tanpa minyak canola / kedelai",
    "No pork or alcohol": "Tanpa babi atau alkohol", "No meat or fish": "Tanpa daging atau ikan",
    "After the AI writes a recipe, the app removes any that contain an excluded ingredient. "
    "This keyword check is a safety net, not a guarantee: always read labels if you have a serious allergy.":
        "Setelah AI menulis resep, aplikasi membuang resep yang mengandung bahan terlarang. "
        "Pemeriksaan kata kunci ini hanya jaring pengaman, bukan jaminan: selalu baca label jika Anda punya alergi serius.",
    "Today's intake": "Asupan hari ini",
    "{done} of {budget} kcal logged · {left} remaining": "{done} dari {budget} kcal tercatat · sisa {left}",
    "Protein {p} g · Carbs {c} g · Fat {f} g": "Protein {p} g · Karbo {c} g · Lemak {f} g",
    "Clear today's log": "Hapus catatan hari ini",
    "Nothing logged today. Use “Log” on a recipe to track it here.":
        "Belum ada catatan hari ini. Gunakan “Catat” pada resep untuk melacaknya di sini.",
    "Generate meals for this target": "Buat hidangan untuk target ini",
    "Calorie target for each recipe": "Target kalori untuk setiap resep",
    "From daily budget": "Dari anggaran harian", "Off": "Nonaktif",
    "Daily calories (kcal)": "Kalori harian (kcal)",
    "Meals per day": "Jumlah makan per hari",
    "Target energy per serving (kcal)": "Target energi per porsi (kcal)",
    "Snack": "Camilan", "Lean cut": "Diet ringan", "Hearty": "Mengenyangkan",
    "{kcal} kcal ({label})": "{kcal} kcal ({label})",
    "Tolerance (± kcal)": "Toleransi (± kcal)",
    "Target: {target} kcal per serving (accepted range {lo} to {hi}).":
        "Target: {target} kcal per porsi (rentang diterima {lo} sampai {hi}).",
    "Metabolic goal": "Tujuan metabolik",
    "Calorie Deficit": "Defisit Kalori", "Maintenance": "Pemeliharaan", "Hypertrophy": "Pembesaran Otot",
    "Energy": "Energi",
    "Calcium (mg)": "Kalsium (mg)", "Iron (mg)": "Zat besi (mg)", "Zinc (mg)": "Seng (mg)",
    "Retinol (µg)": "Retinol (µg)", "Beta-carotene (µg)": "Beta-karoten (µg)",

    # ---- recipes
    "Under 600 kcal": "Di bawah 600 kcal", "40 g+ protein": "Protein 40 g+", "Under 15 g fat": "Lemak di bawah 15 g",
    "Best match": "Paling cocok", "Highest protein": "Protein tertinggi", "Lowest calories": "Kalori terendah",
    "Closest to target": "Paling dekat target",
    "Logged {kcal} kcal": "Tercatat {kcal} kcal",
    "Building your 7-day plan...": "Menyusun rencana 7 hari Anda...",
    "Planned {day}": "Direncanakan {day}",
    "Could not finish the plan: {e}": "Rencana tidak dapat diselesaikan: {e}",
    "Pantry match": "Kecocokan bahan",
    "{n} min": "{n} mnt",
    "{d} prep": "Persiapan {d}",
    "Easy": "Mudah", "Medium": "Sedang", "Hard": "Sulit",
    "{n} serving": "{n} porsi", "{n} servings": "{n} porsi",
    "{acc}% calorie accuracy · {delta} kcal vs target {target}":
        "{acc}% akurasi kalori · {delta} kcal dari target {target}",
    "Missing: {items}": "Kurang: {items}",
    "Nutrition covers {n}% of the ingredient weight; the rest is not in the food table.":
        "Gizi mencakup {n}% berat bahan; sisanya tidak ada di tabel pangan.",
    "**Calorie precision customizer:** {verb} **{ing}** from {old} g to {new} g ({chg} kcal per serving) "
    "to land at about {kcal} kcal.":
        "**Penyetel presisi kalori:** {verb} **{ing}** dari {old} g menjadi {new} g ({chg} kcal per porsi) "
        "agar mendekati {kcal} kcal.",
    "Reduce": "Kurangi",
    "Apply micro-adjustment": "Terapkan penyesuaian",
    "Start cooking": "Mulai memasak", "Save": "Simpan", "Log {kcal} kcal": "Catat {kcal} kcal",
    "Precision matcher: calorie target": "Pencocok presisi: target kalori",
    "No recipes yet. ": "Belum ada resep. ",
    "Add ingredients in the Pantry tab first.": "Tambahkan bahan di tab Bahan terlebih dahulu.",
    "Generate some ideas from your pantry.": "Buat beberapa ide dari bahan Anda.",
    "Go to Pantry": "Ke Bahan", "Generate now": "Buat sekarang",
    "{n} pantry item": "{n} bahan", "{n} pantry items": "{n} bahan", "any ingredients": "bahan apa saja",
    "{kcal} kcal target": "target {kcal} kcal", "for {x}": "untuk {x}", "Based on {bits}": "Berdasarkan {bits}",
    "Sort": "Urutkan", "Quick filters": "Filter cepat",
    "{note}. Try again for more options.": "{note}. Coba lagi untuk pilihan lain.",
    "No recipes match these filters. Clear a filter or generate again.":
        "Tidak ada resep yang cocok dengan filter ini. Hapus filter atau buat ulang.",
    "Matched recipes ({n})": "Resep yang cocok ({n})",
    "**Zero food waste tip:** cooking {title} today uses up your {items}.":
        "**Tips tanpa limbah makanan:** memasak {title} hari ini menghabiskan {items} Anda.",
    "Regenerate with fresh ideas": "Buat ulang dengan ide baru",
    "Generate 7-day meal plan": "Buat rencana makan 7 hari",
    "Saved recipes ({n})": "Resep tersimpan ({n})",
    "Open": "Buka",
    "Removed “{title}”: {why}": "“{title}” dihapus: {why}",
    "Add at least one ingredient to your pantry first.": "Tambahkan minimal satu bahan terlebih dahulu.",
    "Your AI chef is cooking up ideas...": "Koki AI Anda sedang menyiapkan ide...",
    "Could not generate recipes: {e}": "Resep tidak dapat dibuat: {e}",

    # ---- cook
    "Pick a recipe from the Recipes tab (Start cooking) to open it here.":
        "Pilih resep dari tab Resep (Mulai memasak) untuk membukanya di sini.",
    "Go to Recipes": "Ke Resep",
    "or open a saved recipe": "atau buka resep tersimpan",
    "Start timer": "Mulai timer", "Done!": "Selesai!",
    "Nutrition per serving": "Gizi per porsi",
    "More nutrients and ingredient breakdown": "Nutrisi lain dan rincian bahan",
    "Not in the food table (left out): {items}": "Tidak ada di tabel pangan (diabaikan): {items}",
    "Your target: {target} kcal per serving.": "Target Anda: {target} kcal per porsi.",
    "Pantry checklist": "Daftar periksa bahan",
    "{have} of {total} ingredients in your kitchen": "{have} dari {total} bahan ada di dapur Anda",
    "Add items to your pantry to see what you already have.":
        "Tambahkan bahan untuk melihat apa yang sudah Anda punya.",
    "Step by step": "Langkah demi langkah",
    "Step {a} of {b}": "Langkah {a} dari {b}",
    "**Step {n}.** {text}": "**Langkah {n}.** {text}",
    "Previous step": "Langkah sebelumnya", "Next step": "Langkah berikutnya",
    "Done cooking: log it": "Selesai memasak: catat",
    "Logged to today's intake": "Dicatat ke asupan hari ini",
    "Save recipe": "Simpan resep", "Download as text": "Unduh sebagai teks",

    # ---- plan
    "Meal plan": "Rencana makan",
    "Breakfast": "Sarapan", "Lunch": "Makan siang", "Dinner": "Makan malam",
    "Mon": "Sen", "Tue": "Sel", "Wed": "Rab", "Thu": "Kam", "Fri": "Jum", "Sat": "Sab", "Sun": "Min",
    "Done": "Selesai", "Planned": "Rencana", "Empty": "Kosong",
    "Day": "Hari",
    "{day} target: {kcal} kcal": "Target {day}: {kcal} kcal",
    "{done} kcal planned · {left} remaining": "{done} kcal direncanakan · sisa {left}",
    "{done} kcal planned · {over} over budget": "{done} kcal direncanakan · lebih {over}",
    "{pct}% of {g} g": "{pct}% dari {g} g",
    "AI calorie architect": "Perancang kalori AI",
    "Plans meals that balance your calories and macros. Accepted meals are kept.":
        "Merencanakan hidangan yang menyeimbangkan kalori dan makro Anda. Hidangan yang diterima dipertahankan.",
    "Auto-fill {day}": "Isi otomatis {day}", "Auto-fill whole week": "Isi otomatis seminggu",
    "Planning the week...": "Merencanakan seminggu...",
    "Your AI chef is planning...": "Koki AI Anda sedang merencanakan...",
    "Could not generate meals: {e}": "Hidangan tidak dapat dibuat: {e}",
    "Daily timeline ({n} slots)": "Jadwal harian ({n} waktu makan)",
    "{slot} · {time} · goal {kcal} kcal": "{slot} · {time} · target {kcal} kcal",
    "Nothing planned yet.": "Belum ada rencana.", "Generate this slot": "Buat untuk waktu ini",
    "(accepted)": "(diterima)",
    "{p} g protein": "{p} g protein", "{c} g carbs": "{c} g karbo", "{f} g fat": "{f} g lemak",
    "Fits slot by {d} kcal": "Selisih dengan target {d} kcal", " (within range)": " (dalam rentang)",
    "Accept": "Terima", "Swap": "Ganti", "Generate a different meal": "Buat hidangan yang berbeda",
    "Tweak one calorie-dense ingredient": "Sesuaikan satu bahan padat kalori",
    "Clear this day": "Hapus hari ini",
    "Grocery list": "Daftar belanja", "Show for": "Tampilkan untuk",
    "This day": "Hari ini", "Whole week": "Seminggu",
    "Plan some meals to see what you need to buy.": "Rencanakan hidangan untuk melihat apa yang perlu dibeli.",
    "You already have everything for these meals.": "Anda sudah punya semua bahan untuk hidangan ini.",
    "{n} ingredient not in your pantry": "{n} bahan belum ada di dapur Anda",
    "{n} ingredients not in your pantry": "{n} bahan belum ada di dapur Anda",
    "Ingredient": "Bahan", "Amount": "Jumlah",
    "Download list": "Unduh daftar", "I bought these: add to pantry": "Sudah dibeli: tambahkan ke bahan",

    # ---- recovery
    "Recovery: food for how you feel": "Pemulihan: makanan sesuai kondisi Anda",
    "Condition": "Kondisi", "Something else?": "Kondisi lain?",
    "e.g. sore throat, low appetite, recovering from a stomach bug":
        "mis. sakit tenggorokan, nafsu makan rendah, pulih dari sakit perut",
    "**Foods that tend to help**": "**Makanan yang cenderung membantu**",
    "**Foods to go easy on**": "**Makanan yang sebaiknya dikurangi**",
    "Meal ideas for “{key}” will be mild and simple. There is no fixed guidance list for custom needs.":
        "Ide hidangan untuk “{key}” akan ringan dan sederhana. Tidak ada daftar panduan tetap untuk kebutuhan khusus.",
    "using your {n} pantry item": "dengan {n} bahan Anda", "using your {n} pantry items": "dengan {n} bahan Anda",
    "from common ingredients": "dari bahan-bahan umum",
    "Generate gentle meals {note}": "Buat hidangan ringan {note}",
    "Preparing gentle meal ideas...": "Menyiapkan ide hidangan ringan...",
    "Targeted meals for {x}": "Hidangan khusus untuk {x}",
    "Cook recipe now": "Masak resep ini",

    # ---- wellness content
    "General food guidance only, not medical advice. If symptoms are severe, last more than a few "
    "days, or you have a medical condition or take medication, please see a doctor or dietitian.":
        "Hanya panduan makanan umum, bukan saran medis. Jika gejala berat, berlangsung lebih dari beberapa hari, "
        "atau Anda memiliki kondisi medis atau minum obat, silakan temui dokter atau ahli gizi.",
    "Flu & Cold": "Flu & Pilek", "GERD & Acid Reflux": "GERD & Asam Lambung",
    "Sensitive Gut (IBS)": "Pencernaan Sensitif (IBS)", "Muscle Recovery": "Pemulihan Otot",
    "Appetite is often low and fluids matter. Warm, soft, easy-to-eat food usually goes down best.":
        "Nafsu makan sering menurun dan cairan penting. Makanan hangat, lunak, dan mudah dimakan biasanya paling nyaman.",
    "Warm broth & soups": "Kaldu & sup hangat",
    "Fluids and salt, easy to sip when you don't feel like eating":
        "Cairan dan garam, mudah diminum saat tidak ingin makan",
    "Ginger & garlic": "Jahe & bawang putih", "Traditionally used for a warming, soothing effect":
        "Secara tradisional dipakai untuk efek menghangatkan dan menenangkan",
    "Bubur (rice porridge)": "Bubur", "Soft, gentle on the stomach, easy energy":
        "Lunak, lembut di lambung, sumber energi yang mudah",
    "Citrus & other fruit": "Jeruk & buah lain", "Fluids and vitamin C": "Cairan dan vitamin C",
    "Very oily or heavy dishes": "Makanan sangat berminyak atau berat",
    "Can feel hard to digest when you're unwell": "Bisa terasa sulit dicerna saat tidak enak badan",
    "Alcohol": "Alkohol", "Dehydrates and can make you feel worse": "Membuat dehidrasi dan bisa memperburuk kondisi",
    "Many people find smaller, lower-fat, non-spicy meals cause fewer symptoms. Triggers differ per person.":
        "Banyak orang merasa porsi lebih kecil, rendah lemak, dan tidak pedas mengurangi gejala. Pemicu berbeda pada tiap orang.",
    "Oatmeal, rice, bubur": "Oatmeal, nasi, bubur", "Mild and filling": "Ringan dan mengenyangkan",
    "Steamed, boiled or baked lean fish & chicken": "Ikan & ayam tanpa lemak yang dikukus, direbus, atau dipanggang",
    "Low fat, little irritation": "Rendah lemak, sedikit iritasi",
    "Banana, papaya, melon": "Pisang, pepaya, melon", "Usually less acidic than citrus": "Biasanya kurang asam dibanding jeruk",
    "Cooked non-acidic vegetables": "Sayuran matang yang tidak asam", "Easy to digest": "Mudah dicerna",
    "Chili, sambal & very spicy food": "Cabai, sambal & makanan sangat pedas", "Common trigger": "Pemicu umum",
    "Fried and fatty food": "Makanan goreng dan berlemak", "Fat slows stomach emptying": "Lemak memperlambat pengosongan lambung",
    "Coffee, chocolate, mint": "Kopi, cokelat, mint", "Can relax the valve at the top of the stomach":
        "Dapat mengendurkan katup di bagian atas lambung",
    "Large or late meals": "Makan besar atau terlambat",
    "Eat smaller portions and not right before lying down": "Makan lebih sedikit dan tidak tepat sebelum berbaring",
    "Triggers vary a lot between people. Simple, lightly spiced, well-cooked meals are a common starting point.":
        "Pemicu sangat beragam antar orang. Hidangan sederhana, bumbu ringan, dan matang sempurna adalah titik awal yang umum.",
    "White rice, potato, plain noodles": "Nasi putih, kentang, mi polos",
    "Eggs, tofu, chicken, fish": "Telur, tahu, ayam, ikan", "Simple proteins": "Protein sederhana",
    "Well-cooked carrot, zucchini, pumpkin": "Wortel, zukini, labu yang dimasak matang",
    "Gentler than raw vegetables": "Lebih lembut dibanding sayuran mentah",
    "Ginger": "Jahe", "Often well tolerated": "Biasanya ditoleransi dengan baik",
    "Very spicy or very oily food": "Makanan sangat pedas atau berminyak",
    "Large amounts of beans, onion, garlic": "Kacang-kacangan, bawang, bawang putih dalam jumlah besar",
    "High in fermentable carbs for some people": "Tinggi karbohidrat yang mudah difermentasi bagi sebagian orang",
    "Milk-heavy dishes": "Hidangan berbahan susu", "Lactose bothers some people": "Laktosa mengganggu sebagian orang",
    "Carbonated drinks": "Minuman berkarbonasi", "Can cause bloating": "Dapat menyebabkan kembung",
    "After hard training the body needs protein to repair and carbohydrate to refill energy stores.":
        "Setelah latihan berat, tubuh butuh protein untuk perbaikan dan karbohidrat untuk mengisi kembali energi.",
    "Eggs, chicken, fish": "Telur, ayam, ikan", "Complete protein": "Protein lengkap",
    "Tempe & tahu": "Tempe & tahu", "Plant protein that is easy to find in Indonesia":
        "Protein nabati yang mudah ditemukan di Indonesia",
    "Rice, potato, sweet potato": "Nasi, kentang, ubi", "Carbohydrate to restore energy": "Karbohidrat untuk memulihkan energi",
    "Fruit & vegetables": "Buah & sayur", "Vitamins, minerals and fluids": "Vitamin, mineral, dan cairan",
    "Very fatty meals right after training": "Makanan sangat berlemak tepat setelah latihan",
    "Slow digestion": "Memperlambat pencernaan",
    "Gets in the way of recovery and hydration": "Mengganggu pemulihan dan hidrasi",
}
