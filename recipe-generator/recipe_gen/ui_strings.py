"""Bilingual UI string definitions for Vitality Kitchen AI Recipe Generator.

Supports Indonesian ('id') as primary academic language and English ('en').
"""

from typing import Dict, Any

SUPPORTED_LANGUAGES = ["id", "en"]

STRINGS: Dict[str, Dict[str, str]] = {
    "app_title": {
        "id": "Vitality Kitchen",
        "en": "Vitality Kitchen",
    },
    "app_subtitle": {
        "id": "NutriChef AI • Dapur Cerdas & Gizi Presisi",
        "en": "NutriChef AI • Smart Kitchen & Precision Nutrition",
    },
    "pantry_title": {
        "id": "Dapur Saya",
        "en": "Pantry",
    },
    "streak_label": {
        "id": "7h aktif",
        "en": "7d streak",
    },
    "hero_question": {
        "id": "Bahan apa yang ada di dapurmu?",
        "en": "What's in your kitchen?",
    },
    "hero_sub": {
        "id": "Pilih bahan cepat atau ketik bahan yang tersedia untuk diracik oleh AI.",
        "en": "Tap quick ingredients or type what you have to generate a balanced recipe.",
    },
    "snap_fridge": {
        "id": "Foto Kulkas",
        "en": "Snap Fridge",
    },
    "add_ingredients_placeholder": {
        "id": "Tambahkan bahan (misal: ayam, tempe, bayam, telur, bawang)...",
        "en": "Add ingredients (e.g. chicken, quinoa, spinach, eggs, garlic)...",
    },
    "current_pantry_items": {
        "id": "Bahan Terpilih",
        "en": "Current Pantry",
    },
    "clear_all": {
        "id": "Hapus Semua",
        "en": "Clear all",
    },
    "no_ingredients_yet": {
        "id": "Belum ada bahan yang dipilih. Ketik atau klik chip di bawah.",
        "en": "No ingredients selected yet. Type above or tap chips below.",
    },
    "quick_categories_all": {"id": "Semua", "en": "All"},
    "quick_categories_proteins": {"id": "Protein", "en": "Proteins"},
    "quick_categories_veggies": {"id": "Sayuran", "en": "Veggies & Greens"},
    "quick_categories_carbs": {"id": "Karbohidrat", "en": "Carbs & Grains"},
    "quick_categories_spices": {"id": "Bumbu & Minyak", "en": "Spices & Oils"},
    "cuisine_label": {
        "id": "Kategori Masakan",
        "en": "Cuisine",
    },
    "cuisine_indonesian": {
        "id": "🇮🇩 Nusantara (Indonesia)",
        "en": "🇮🇩 Indonesian",
    },
    "cuisine_international": {
        "id": "🌎 Internasional",
        "en": "🌎 International",
    },
    "servings_label": {
        "id": "Jumlah Porsi",
        "en": "Servings",
    },
    "prep_time_label": {
        "id": "Waktu Masak Maksimal",
        "en": "Max Prep Time",
    },
    "equipment_label": {
        "id": "Peralatan Dapur yang Tersedia",
        "en": "Available Equipment",
    },
    "dietary_label": {
        "id": "Preferensi Diet / Alergi (Opsional)",
        "en": "Dietary Preferences / Restrictions (Optional)",
    },
    "dietary_placeholder": {
        "id": "Contoh: pedas, rendah minyak, bebas gluten, halal, tanpa kacang",
        "en": "e.g. spicy, low oil, gluten-free, halal, no peanuts",
    },
    "smart_prediction_badge": {
        "id": "PREDIKSI PINTAR",
        "en": "SMART PREDICTION",
    },
    "smart_prediction_title": {
        "id": "Mangkuk Seimbang Koki Nutrisi",
        "en": "Chef's Balanced Vitality Bowl",
    },
    "smart_prediction_desc": {
        "id": "Kombinasi optimal memaksimalkan bahan aktif tanpa sisa.",
        "en": "Optimized to utilize your active pantry with zero waste.",
    },
    "generate_cta": {
        "id": "✨ Racik Resep dengan {n} Bahan (AI)",
        "en": "✨ Generate Recipe with {n} Ingredients (AI)",
    },
    "generating_spinner": {
        "id": "Chef AI sedang meracik resep & menghitung gizi presisi...",
        "en": "AI Chef is crafting your recipe & calculating precision nutrition...",
    },
    "ai_sommelier_title": {
        "id": "AI CHEF SOMMELIER",
        "en": "AI SOMMELIER",
    },
    "pantry_match_badge": {
        "id": "{pct}% Cocok dengan Dapur",
        "en": "{pct}% Pantry Match",
    },
    "zero_waste_title": {
        "id": "Tips Hemat & Nol Sampah Pangan (Zero Waste)",
        "en": "Zero Food Waste Tip",
    },
    "zero_waste_desc": {
        "id": "Memasak resep ini menghabiskan bahan segar Anda tepat waktu sebelum melampaui masa simpan optimal.",
        "en": "Cooking this recipe today uses up your fresh ingredients right on time before expiry.",
    },
    "start_cooking": {
        "id": "📖 Mulai Memasak",
        "en": "📖 Start Cooking",
    },
    "back_to_pantry": {
        "id": "← Kembali ke Dapur",
        "en": "← Back to Pantry",
    },
    "portion_control": {
        "id": "KONTROL PORSI",
        "en": "PORTION CONTROL",
    },
    "pantry_checklist_title": {
        "id": "Daftar Bahan Terverifikasi",
        "en": "Pantry Checklist",
    },
    "interactive_prep_title": {
        "id": "Langkah Memasak Interaktif",
        "en": "Interactive Prep Flow",
    },
    "timer_label": {
        "id": "TIMER PERALATAN",
        "en": "APPLIANCE TIMER",
    },
    "timer_start": {
        "id": "Mulai Timer",
        "en": "Start Timer",
    },
    "chef_pro_tip": {
        "id": "Tips Rahasia Koki",
        "en": "Chef's Pro-Tip",
    },
    "voice_cooking": {
        "id": "Panduan Suara Bebas Tangan",
        "en": "Voice Guided Cooking",
    },
    "hands_free_badge": {
        "id": "Bebas Tangan",
        "en": "Hands-free",
    },
    "nutrition_header": {
        "id": "Perhitungan Gizi Mandiri (TKPI / USDA)",
        "en": "Estimated Nutrition (TKPI / USDA Reference)",
    },
    "nutrition_disclaimer": {
        "id": "Estimasi gizi dihitung secara independen berdasarkan data komposisi pangan terverifikasi (TKPI), bukan halusinasi LLM. Bukan saran medis.",
        "en": "Nutritional estimates calculated independently from food composition tables (TKPI/USDA). Not medical advice.",
    },
    "calories": {"id": "Kalori", "en": "Calories"},
    "protein": {"id": "Protein", "en": "Protein"},
    "fat": {"id": "Lemak", "en": "Fat"},
    "carbs": {"id": "Karbohidrat", "en": "Carbs"},
    "unmatched_warning": {
        "id": "Bahan belum terdaftar di database komposisi pangan (tidak dihitung dalam total gizi): ",
        "en": "Ingredients not found in the food composition database (excluded from totals): ",
    },
    "regen_cta": {
        "id": "🪄 Racik Ulang Resep dengan AI",
        "en": "🪄 Regenerate with AI",
    },
}


def get_text(key: str, lang: str = "id", **kwargs: Any) -> str:
    """Retrieve localized string with fallback and string formatting."""
    lang_key = lang if lang in SUPPORTED_LANGUAGES else "id"
    item = STRINGS.get(key)
    if not item:
        return key

    template = item.get(lang_key) or item.get("en") or key
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template
