"""Custom CSS and HTML component generators for the Vitality Kitchen mobile design system.

Implements design tokens from vitality_kitchen/DESIGN.md:
- Colors: Primary #006948, Background #FAF8FF, Surface #FFFFFF, Border #E2E8F0
- Typography: Plus Jakarta Sans for titles, Inter for body and numeric metrics
- Radii: 16px for cards, 9999px for pills and CTAs
"""

def get_custom_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

:root {
    --vk-primary: #006948;
    --vk-primary-container: #00855d;
    --vk-surface: #FAF8FF;
    --vk-surface-card: #FFFFFF;
    --vk-on-surface: #131B2E;
    --vk-muted: #64748B;
    --vk-border: #E2E8F0;
    --vk-protein-bg: #FFEDD5;
    --vk-protein-txt: #C2410C;
    --vk-carbs-bg: #FEF3C7;
    --vk-carbs-txt: #B45309;
    --vk-fats-bg: #D1FAE5;
    --vk-fats-txt: #047857;
    --vk-kcal-bg: #F1F5F9;
    --vk-kcal-txt: #334155;
    --vk-orange: #EA580C;
}

/* Global Font & Canvas Background */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif !important;
    background-color: var(--vk-surface) !important;
    color: var(--vk-on-surface) !important;
}

/* Hide default streamlit excess chrome */
#MainMenu, footer, header {visibility: hidden !important; height: 0px !important;}
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    max-width: 480px !important;
    margin: 0 auto !important;
}

/* Mobile Frame simulation */
@media (min-width: 640px) {
    .block-container {
        box-shadow: 0 16px 40px -8px rgba(6, 78, 59, 0.08);
        border: 1px solid var(--vk-border);
        border-radius: 28px;
        background-color: var(--vk-surface);
        margin-top: 1.5rem !important;
        margin-bottom: 2rem !important;
        padding: 1.5rem !important;
    }
}

/* Vitality Kitchen App Header */
.vk-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--vk-border);
    margin-bottom: 16px;
}
.vk-logo-group {
    display: flex;
    align-items: center;
    gap: 8px;
}
.vk-logo-icon {
    width: 34px;
    height: 34px;
    background: #006948;
    color: white;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 18px;
}
.vk-title-wrap {
    display: flex;
    flex-direction: column;
}
.vk-app-name {
    font-size: 16px;
    font-weight: 700;
    color: var(--vk-on-surface);
    line-height: 1.2;
}
.vk-app-sub {
    font-size: 11px;
    color: var(--vk-muted);
}
.vk-streak-badge {
    background: #D1FAE5;
    color: #065F46;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Card Elements */
.vk-card {
    background: #FFFFFF;
    border: 1px solid var(--vk-border);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 14px;
    box-shadow: 0 4px 16px -2px rgba(6, 78, 59, 0.04);
}

.vk-hero-card {
    background: #FFFFFF;
    border: 1px solid var(--vk-border);
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 16px;
    box-shadow: 0 8px 24px -4px rgba(6, 78, 59, 0.06);
}

/* Macro Pills Grid */
.vk-macro-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin: 12px 0;
}
.vk-macro-item {
    border-radius: 12px;
    padding: 8px 4px;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.vk-macro-val {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 15px;
    line-height: 1.2;
}
.vk-macro-lbl {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    margin-top: 2px;
}

/* Ingredient Tag Chips */
.vk-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #FFFFFF;
    border: 1px solid var(--vk-border);
    border-radius: 9999px;
    padding: 4px 12px;
    font-size: 13px;
    font-weight: 500;
    margin: 3px;
    color: #1E293B;
}
.vk-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}
.vk-dot-protein { background-color: #EA580C; }
.vk-dot-veg { background-color: #10B981; }
.vk-dot-carb { background-color: #F59E0B; }
.vk-dot-spice { background-color: #64748B; }

/* Checklist Item */
.vk-check-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid #F1F5F9;
    font-size: 14px;
}
.vk-check-icon {
    width: 22px;
    height: 22px;
    background: #006948;
    color: white;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: bold;
}

/* Step Container */
.vk-step-box {
    background: #FFFFFF;
    border: 1px solid var(--vk-border);
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 10px;
    display: flex;
    gap: 12px;
}
.vk-step-num {
    width: 28px;
    height: 28px;
    background: #006948;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 13px;
    flex-shrink: 0;
}
.vk-step-text {
    font-size: 14px;
    line-height: 1.5;
    color: #334155;
}

/* Callout / Alert Box */
.vk-callout {
    background: #FFF7ED;
    border: 1px solid #FFEDD5;
    border-radius: 12px;
    padding: 12px;
    margin: 12px 0;
    display: flex;
    gap: 10px;
    font-size: 13px;
    color: #9A3412;
}

.vk-tip-box {
    background: #F0FDF4;
    border: 1px solid #DCFCE7;
    border-radius: 12px;
    padding: 12px;
    margin: 12px 0;
    display: flex;
    gap: 10px;
    font-size: 13px;
    color: #166534;
}

/* Full Width Primary Button */
div.stButton > button:first-child {
    background-color: var(--vk-primary) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    border-radius: 9999px !important;
    border: none !important;
    height: 48px !important;
    width: 100% !important;
    box-shadow: 0 4px 14px -2px rgba(0, 105, 72, 0.3) !important;
    transition: all 0.2s ease !important;
}
div.stButton > button:first-child:hover {
    background-color: var(--vk-primary-container) !important;
    box-shadow: 0 6px 20px -2px rgba(0, 105, 72, 0.4) !important;
    transform: translateY(-1px);
}
</style>
"""


def get_macro_badge_html(kcal: float, protein: float, carbs: float, fat: float) -> str:
    """Generate 4-column balanced pastel macro card strip."""
    return f"""
<div class="vk-macro-grid">
    <div class="vk-macro-item" style="background-color: var(--vk-kcal-bg); color: var(--vk-kcal-txt);">
        <span class="vk-macro-val">{round(kcal)}</span>
        <span class="vk-macro-lbl">kcal</span>
    </div>
    <div class="vk-macro-item" style="background-color: var(--vk-protein-bg); color: var(--vk-protein-txt);">
        <span class="vk-macro-val">{round(protein, 1)}g</span>
        <span class="vk-macro-lbl">Protein</span>
    </div>
    <div class="vk-macro-item" style="background-color: var(--vk-carbs-bg); color: var(--vk-carbs-txt);">
        <span class="vk-macro-val">{round(carbs, 1)}g</span>
        <span class="vk-macro-lbl">Carbs</span>
    </div>
    <div class="vk-macro-item" style="background-color: var(--vk-fats-bg); color: var(--vk-fats-txt);">
        <span class="vk-macro-val">{round(fat, 1)}g</span>
        <span class="vk-macro-lbl">Fat</span>
    </div>
</div>
"""
