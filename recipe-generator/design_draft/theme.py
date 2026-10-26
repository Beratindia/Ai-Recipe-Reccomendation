"""Vitality Kitchen design system (from the Stitch export) as CSS for Streamlit."""

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@500;600;700&display=swap');

:root{
  --primary:#059669; --primary-deep:#006948; --forest:#064E3B; --amber:#EA580C; --amber-soft:#FFF7ED;
  --surface:#FAF8FF; --card:#FFFFFF; --container:#F2F3FF; --container-hi:#EAEDFF;
  --ink:#0F172A; --body:#334155; --muted:#64748B; --line:#E2E8F0;
  --protein-bg:#FFEDD5; --protein-fg:#C2410C; --carb-bg:#FEF3C7; --carb-fg:#B45309;
  --fat-bg:#D1FAE5; --fat-fg:#047857; --kcal-bg:#F1F5F9; --kcal-fg:#334155;
  --mint:#ADEDD3; --mint-soft:#E6F7EF;
}

html, body, [class*="st-"], .stApp, button, input, textarea, select{font-family:'Plus Jakarta Sans',system-ui,sans-serif;}
.stApp{background:var(--surface);}
header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], footer, #MainMenu{display:none !important;}
[data-testid="stMainBlockContainer"], .block-container{max-width:520px !important;padding:0.75rem 1.25rem 11rem !important;}
[data-testid="stVerticalBlock"]{gap:0.9rem;}
h1,h2,h3,h4{font-family:'Plus Jakarta Sans',sans-serif;color:var(--ink);letter-spacing:-0.015em;}
p, li, label, span{color:inherit;}
.num{font-family:'Inter',sans-serif;font-variant-numeric:tabular-nums;}

[data-testid="stHorizontalBlock"]{flex-direction:row !important;flex-wrap:nowrap !important;gap:0.6rem;align-items:center;}
[data-testid="stColumn"]{min-width:0 !important;}

/* ---------- top bar ---------- */
.topbar{display:flex;align-items:center;justify-content:space-between;padding:6px 0 4px;}
.brand{display:flex;align-items:center;gap:10px;}
.brand-logo{width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg,#064E3B,#10B981);display:flex;align-items:center;justify-content:center;font-size:20px;}
.brand-name{font-weight:800;font-size:19px;color:var(--ink);line-height:1.05;letter-spacing:-0.02em;}
.brand-sub{font-size:12px;font-weight:600;color:var(--muted);line-height:1.1;}
.status-pill{font-family:'Inter',sans-serif;font-size:11px;font-weight:600;padding:6px 12px;border-radius:999px;background:var(--mint);color:var(--forest);}
.status-pill.demo{background:#FEF3C7;color:#92400E;}

/* ---------- typography helpers ---------- */
.h-lg{font-size:26px;line-height:32px;font-weight:700;color:var(--ink);letter-spacing:-0.02em;margin:0;}
.h-md{font-size:20px;line-height:26px;font-weight:700;color:var(--ink);margin:0;}
.h-sm{font-size:16px;font-weight:700;color:var(--ink);margin:0;}
.sub{font-size:14px;line-height:21px;color:var(--muted);margin:2px 0 0;}
.eyebrow{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--primary-deep);}
.section-row{display:flex;align-items:center;justify-content:space-between;margin:6px 0 0;}
.count-badge{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;background:var(--primary);color:#fff;border-radius:999px;padding:3px 10px;margin-left:8px;}

/* ---------- cards ---------- */
[data-testid="stVerticalBlockBorderWrapper"]{background:var(--card);border:1px solid var(--line) !important;border-radius:20px !important;box-shadow:0 8px 24px -4px rgba(6,78,59,.05);padding:2px;}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"]{box-shadow:none;border-radius:16px !important;}
.card-plain{background:var(--card);border:1px solid var(--line);border-radius:20px;box-shadow:0 8px 24px -4px rgba(6,78,59,.05);padding:16px;}
.card-tint{background:var(--container);border-radius:20px;padding:16px;}
.card-mint{background:linear-gradient(135deg,#B7F0D8,#D3F5E6);border-radius:20px;padding:16px;color:var(--forest);}
.card-hero{background:linear-gradient(135deg,#064E3B,#059669);border-radius:24px;padding:22px 20px;color:#fff;}
.card-hero .h-lg{color:#fff;} .card-hero .sub{color:#D1FAE5;}
.card-danger{background:#FFF1F0;border:1px solid #FECACA;border-radius:20px;padding:16px;}
.card-amber{background:var(--amber-soft);border:1px solid #FED7AA;border-radius:16px;padding:14px;color:#7C2D12;}
.pill-tag{display:inline-block;font-family:'Inter',sans-serif;font-size:11px;font-weight:700;letter-spacing:.03em;padding:4px 12px;border-radius:999px;background:rgba(255,255,255,.18);color:#fff;}

/* ---------- macro chips ---------- */
.chip{display:inline-flex;align-items:center;gap:4px;height:26px;padding:0 12px;border-radius:999px;font-family:'Inter',sans-serif;font-size:12px;font-weight:600;white-space:nowrap;}
.chip.protein{background:var(--protein-bg);color:var(--protein-fg);} .chip.carbs{background:var(--carb-bg);color:var(--carb-fg);}
.chip.fat{background:var(--fat-bg);color:var(--fat-fg);} .chip.kcal{background:var(--kcal-bg);color:var(--kcal-fg);}
.chip.match{background:#D1FAE5;color:#065F46;} .chip.warn{background:#FFEDD5;color:#9A3412;} .chip.info{background:var(--container-hi);color:#3730A3;}
.chip-row{display:flex;flex-wrap:wrap;gap:6px;}
.macro-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;}
.macro-cell{border-radius:14px;padding:10px 4px;text-align:center;}
.macro-cell .lab{font-family:'Inter',sans-serif;font-size:11px;font-weight:600;}
.macro-cell .val{font-family:'Inter',sans-serif;font-size:15px;font-weight:700;margin-top:2px;}
.macro-cell.kcal{background:var(--container-hi);color:var(--kcal-fg);} .macro-cell.protein{background:var(--protein-bg);color:var(--protein-fg);}
.macro-cell.carbs{background:var(--carb-bg);color:var(--carb-fg);} .macro-cell.fat{background:var(--fat-bg);color:var(--fat-fg);}

/* ---------- recipe visual ---------- */
.visual{position:relative;border-radius:20px;overflow:hidden;display:flex;align-items:center;justify-content:center;}
.visual .emoji{filter:drop-shadow(0 6px 10px rgba(0,0,0,.18));}
.visual .badge{position:absolute;font-family:'Inter',sans-serif;font-size:11px;font-weight:700;padding:5px 10px;border-radius:999px;}
.visual .badge.tl{top:10px;left:10px;background:rgba(255,255,255,.92);color:var(--forest);}
.visual .badge.bl{bottom:10px;left:10px;background:var(--amber);color:#fff;}
.visual .badge.br{bottom:10px;right:10px;background:rgba(15,23,42,.72);color:#fff;}
.visual .badge.tr{top:10px;right:10px;background:rgba(15,23,42,.72);color:#fff;}
.meta-row{display:flex;gap:14px;align-items:center;font-size:13px;color:var(--muted);font-weight:500;flex-wrap:wrap;}

/* ---------- progress ---------- */
.bar{height:8px;border-radius:999px;background:var(--line);overflow:hidden;}
.bar > span{display:block;height:100%;border-radius:999px;}
.ring-wrap{position:relative;display:inline-block;}
.ring-wrap .ring-text{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:'Inter',sans-serif;}
.ring-text b{font-size:15px;color:var(--ink);} .ring-text small{font-size:10px;font-weight:600;color:var(--muted);}

/* ---------- buttons ---------- */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button{border-radius:999px;font-weight:700;border:1px solid var(--line);background:#fff;color:var(--forest);min-height:44px;transition:transform .08s ease;}
.stButton > button:active, .stDownloadButton > button:active{transform:scale(.98);}
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"]{background:linear-gradient(135deg,#064E3B,#059669);color:#fff;border:0;min-height:52px;box-shadow:0 10px 20px -8px rgba(5,150,105,.6);}
.stButton > button[kind="primary"] p{color:#fff;}
.stButton > button p{font-weight:700;}
.btn-amber .stButton > button{background:linear-gradient(135deg,#C2410C,#EA580C);color:#fff;border:0;min-height:52px;}
.btn-amber .stButton > button p{color:#fff;}
.btn-soft .stButton > button{background:var(--mint-soft);border:0;color:var(--forest);}

/* ---------- inputs ---------- */
[data-testid="stTextInputRootElement"], [data-testid="stNumberInputContainer"]{border-radius:999px !important;background:#fff;border:1px solid var(--line);min-height:48px;}
[data-testid="stTextInputRootElement"]:focus-within{border-color:var(--primary);box-shadow:0 0 0 3px rgba(5,150,105,.15);}
[data-testid="stTextArea"] textarea{border-radius:16px;}
[data-testid="stPills"] button, [data-testid="stSegmentedControl"] button{border-radius:999px !important;font-weight:600;}
[data-testid="stWidgetLabel"] p{font-weight:600;color:var(--body);}
[data-testid="stExpander"]{border-radius:16px;border:1px solid var(--line);background:#fff;}
[data-testid="stForm"]{border:0;padding:0;}

/* ---------- pantry chips (buttons laid out as a wrapping row) ---------- */
.st-key-pantry_chips [data-testid="stVerticalBlock"], .st-key-suggest_chips [data-testid="stVerticalBlock"]{flex-direction:row !important;flex-wrap:wrap;gap:8px !important;}
.st-key-pantry_chips [data-testid="stElementContainer"], .st-key-suggest_chips [data-testid="stElementContainer"]{width:auto !important;}
.st-key-pantry_chips .stButton > button{min-height:36px;padding:0 14px;background:#fff;border:1px solid var(--line);box-shadow:0 1px 2px rgba(15,23,42,.06);font-size:13px;}
.st-key-suggest_chips .stButton > button{min-height:32px;padding:0 12px;background:var(--container);border:0;font-size:12px;}
.st-key-pantry_chips .stButton > button p, .st-key-suggest_chips .stButton > button p{font-size:13px;}

/* ---------- bottom navigation + floating CTA ---------- */
.st-key-bottomnav{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;max-width:520px;background:rgba(255,255,255,.93);backdrop-filter:blur(12px);border-top:1px solid var(--line);padding:6px 6px calc(6px + env(safe-area-inset-bottom));z-index:999;}
.st-key-bottomnav [data-testid="stHorizontalBlock"]{flex-direction:row !important;flex-wrap:nowrap !important;gap:0 !important;}
.st-key-bottomnav [data-testid="stColumn"]{min-width:0 !important;width:auto !important;flex:1 1 0 !important;}
.st-key-bottomnav button{border:0 !important;background:transparent !important;box-shadow:none !important;padding:2px 0;min-height:54px;color:var(--muted);line-height:1.15;}
.st-key-bottomnav button p{font-size:11px !important;font-weight:600 !important;white-space:pre-line;text-align:center;color:var(--muted) !important;}
.st-key-bottomnav button[kind="primary"] p{color:var(--forest) !important;font-weight:800 !important;}
.st-key-bottomnav button[kind="primary"]{background:var(--mint-soft) !important;border-radius:16px !important;}
.st-key-gen_cta{position:fixed;bottom:74px;left:50%;transform:translateX(-50%);width:100%;max-width:520px;padding:0 1.25rem;z-index:998;}
.st-key-gen_cta .stButton > button{width:100%;min-height:54px;font-size:15px;}

/* ---------- misc ---------- */
.step{display:flex;gap:12px;padding:12px;border-radius:16px;margin:6px 0;}
.step .n{flex:0 0 28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Inter',sans-serif;font-size:13px;font-weight:700;background:var(--container-hi);color:var(--forest);}
.step.done{opacity:.55;} .step.done .t{text-decoration:line-through;} .step.done .n{background:var(--mint);}
.step.active{background:var(--container);} .step.active .n{background:var(--primary);color:#fff;}
.step .t{font-size:15px;line-height:24px;color:var(--ink);}
.check-row{display:flex;justify-content:space-between;align-items:center;padding:11px 12px;border-radius:12px;background:var(--container);margin:6px 0;font-size:14px;}
.check-row.miss{background:#FFF1F0;} .check-row .q{font-family:'Inter',sans-serif;font-weight:600;color:var(--body);font-size:13px;}
.insight{display:flex;gap:12px;align-items:flex-start;}
.insight .ic{flex:0 0 36px;height:36px;border-radius:50%;background:rgba(255,255,255,.7);display:flex;align-items:center;justify-content:center;font-size:18px;}
.food-row{display:flex;gap:12px;padding:12px;background:#fff;border:1px solid var(--line);border-radius:16px;margin:6px 0;}
.food-row .ft{font-weight:700;font-size:14px;color:var(--ink);} .food-row .fd{font-size:13px;color:var(--muted);line-height:19px;}
.limit-row{display:flex;justify-content:space-between;gap:12px;padding:10px 12px;background:#fff;border-radius:12px;margin:6px 0;border:1px solid #FECACA;}
.limit-row b{font-size:14px;color:#7F1D1D;} .limit-row span{font-size:12.5px;color:#B91C1C;text-align:right;}
.day-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;}
.day{border-radius:16px;padding:8px 2px;text-align:center;background:#fff;border:1px solid var(--line);font-family:'Inter',sans-serif;}
.day .dn{font-size:11px;font-weight:600;color:var(--muted);} .day .dk{font-size:12px;font-weight:700;color:var(--ink);margin-top:2px;}
.day.sel{background:linear-gradient(135deg,#064E3B,#059669);border:0;} .day.sel .dn, .day.sel .dk{color:#fff;}
.slot-head{display:flex;justify-content:space-between;align-items:center;}
.slot-name{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--forest);}
.kcal-badge{font-family:'Inter',sans-serif;font-size:12px;font-weight:700;background:var(--container-hi);color:var(--ink);padding:4px 10px;border-radius:999px;}
.empty{text-align:center;padding:28px 12px;color:var(--muted);}
.empty .big{font-size:42px;}
@media (max-width:420px){ .h-lg{font-size:23px;line-height:29px;} }
"""
