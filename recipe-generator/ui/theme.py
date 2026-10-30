"""Visual theme: Vitality Kitchen palette (emerald, forest green, warm amber) applied with CSS.

Plain Streamlit widgets are restyled; no emoji anywhere. Fonts load from Google Fonts when online and
fall back to the system font otherwise.
"""
import streamlit as st

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@500;600;700&display=swap');

:root{
  --emerald:#059669; --emerald-deep:#047857; --forest:#064E3B; --amber:#EA580C; --amber-soft:#FFF7ED;
  --canvas:#F9FAFB; --card:#FFFFFF; --tint:#F1F5F9; --mint:#ECFDF5; --mint-line:#A7F3D0;
  --ink:#0F172A; --body:#334155; --muted:#64748B; --line:#E2E8F0;
  --protein-bg:#FFEDD5; --protein-fg:#C2410C; --carb-bg:#FEF3C7; --carb-fg:#B45309;
  --fat-bg:#D1FAE5; --fat-fg:#047857; --kcal-bg:#F1F5F9; --kcal-fg:#334155;
}

html, body, .stApp, .stApp :where(p, span, div, label, input, textarea, button, li, h1, h2, h3, h4, td, th, a){
  font-family:'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;}
.stApp [data-testid="stIconMaterial"], .stApp .material-icons, .stApp [class*="material-symbols"]{
  font-family:'Material Symbols Rounded' !important;}
.stApp{background:var(--canvas);}
[data-testid="stHeader"]{background:transparent;}
footer, [data-testid="stDecoration"]{display:none !important;}
[data-testid="stMainBlockContainer"]{max-width:880px;padding:2rem 1.25rem 4rem;}

/* ---------- headings and text ---------- */
h1,h2,h3,h4{color:var(--forest);font-family:'Plus Jakarta Sans',sans-serif;letter-spacing:-0.015em;}
h2{font-size:1.65rem !important;font-weight:700 !important;margin-top:.4rem;}
h3{font-size:1.2rem !important;font-weight:700 !important;margin-top:.8rem;}
p, li, label{color:var(--body);}
[data-testid="stCaptionContainer"], .stCaption{color:var(--muted) !important;}
hr{border-color:var(--line);}

/* ---------- brand header ---------- */
.brand{display:flex;align-items:center;gap:12px;margin:0 0 .6rem;}
.brand-mark{width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#064E3B,#10B981);color:#fff;
  display:flex;align-items:center;justify-content:center;font-weight:800;font-size:20px;letter-spacing:-0.02em;}
.brand-name{font-size:22px;font-weight:800;color:var(--forest);line-height:1.05;letter-spacing:-0.02em;}
.brand-sub{font-size:12.5px;font-weight:500;color:var(--muted);line-height:1.2;}

/* ---------- top navigation ---------- */
.st-key-nav{position:sticky;top:0;z-index:50;background:rgba(249,250,251,.92);backdrop-filter:blur(10px);
  padding:6px 0 8px;margin-bottom:.4rem;border-bottom:1px solid var(--line);}
.st-key-nav [data-testid="stHorizontalBlock"]{gap:.35rem;}
.st-key-nav button{border:0 !important;background:transparent !important;box-shadow:none !important;min-height:44px;
  border-radius:12px !important;color:var(--muted) !important;}
.st-key-nav button p{font-size:13.5px;font-weight:600;color:inherit !important;}
.st-key-nav button:hover{background:var(--tint) !important;color:var(--forest) !important;}
.st-key-nav button[data-testid="stBaseButton-primary"]{background:var(--mint) !important;color:var(--forest) !important;
  box-shadow:inset 0 -3px 0 var(--emerald) !important;}
.st-key-nav button[data-testid="stBaseButton-primary"] p{font-weight:700;}
@media (max-width:640px){ .st-key-nav button p{font-size:11px;} .st-key-nav [data-testid="stHorizontalBlock"]{gap:.15rem;} }

/* ---------- cards (bordered containers are given keys starting with card_) ---------- */
[class*="st-key-card_"]{border-color:var(--line) !important;border-radius:16px !important;background:var(--card);
  box-shadow:0 8px 24px -8px rgba(6,78,59,.08);padding:.25rem .35rem;}
.st-key-card_step{background:var(--mint);border-color:var(--mint-line) !important;box-shadow:none;}

/* ---------- buttons ---------- */
.stButton > button, .stDownloadButton > button, [data-testid^="stBaseButton-"]{border-radius:999px;font-weight:600;transition:transform .08s ease, box-shadow .15s ease;}
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-secondaryFormSubmit"]{background:#fff;border:1px solid var(--line);color:var(--forest);min-height:44px;}
[data-testid="stBaseButton-secondary"]:hover, [data-testid="stBaseButton-secondaryFormSubmit"]:hover{border-color:var(--emerald);color:var(--emerald-deep);background:var(--mint);}
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"]{background:linear-gradient(135deg,#047857,#059669);border:0;color:#fff;min-height:48px;
  box-shadow:0 10px 18px -10px rgba(5,150,105,.7);}
[data-testid="stBaseButton-primary"]:hover{filter:brightness(1.05);}
[data-testid="stBaseButton-primary"] p, [data-testid="stBaseButton-primaryFormSubmit"] p{color:#fff !important;font-weight:700;}
[data-testid^="stBaseButton-"]:active{transform:scale(.98);}
[data-testid^="stBaseButton-"]:disabled{opacity:.5;box-shadow:none;}

/* ---------- inputs ---------- */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="select"] > div, [data-baseweb="textarea"]{border-radius:12px !important;background:#fff !important;}
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within, [data-baseweb="textarea"]:focus-within{
  border-color:var(--emerald) !important;box-shadow:0 0 0 3px rgba(5,150,105,.15) !important;}
[data-testid="stWidgetLabel"] p{font-weight:600;color:var(--body);font-size:13.5px;}
[data-testid="stSlider"] [role="slider"]{background:var(--emerald);}
[data-testid="stExpander"]{border-radius:16px !important;border:1px solid var(--line) !important;background:#fff;}
[data-testid="stExpander"] summary p{font-weight:700;color:var(--forest);}
[data-testid="stForm"]{border:0;padding:0;}
[data-testid="stFileUploader"] section{border-radius:12px;}

/* ---------- pills (segmented choices) ---------- */
button[data-variant="pills"]{border-radius:999px !important;font-weight:600;border:1px solid var(--line) !important;background:#fff;}
button[data-variant="pills"][data-selected="true"]{background:var(--forest) !important;border-color:var(--forest) !important;}
button[data-variant="pills"][data-selected="true"] *{color:#fff !important;}

/* ---------- metrics: macro tiles ---------- */
[data-testid="stMetric"]{background:var(--tint);border-radius:14px;padding:10px 12px;min-height:74px;}
[data-testid="stMetricLabel"] p{font-family:'Inter',sans-serif;font-size:11px !important;font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);}
[data-testid="stMetricValue"]{font-family:'Inter',sans-serif;font-weight:700;font-size:1.25rem !important;color:var(--ink);letter-spacing:-0.02em;}
[class*="st-key-macros_"] [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"]{background:#E0E7FF;}
[class*="st-key-macros_"] [data-testid="stColumn"]:nth-child(1) [data-testid="stMetricValue"]{color:#3730A3;}
[class*="st-key-macros_"] [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"]{background:var(--protein-bg);}
[class*="st-key-macros_"] [data-testid="stColumn"]:nth-child(2) [data-testid="stMetricValue"]{color:var(--protein-fg);}
[class*="st-key-macros_"] [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"]{background:var(--carb-bg);}
[class*="st-key-macros_"] [data-testid="stColumn"]:nth-child(3) [data-testid="stMetricValue"]{color:var(--carb-fg);}
[class*="st-key-macros_"] [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"]{background:var(--fat-bg);}
[class*="st-key-macros_"] [data-testid="stColumn"]:nth-child(4) [data-testid="stMetricValue"]{color:var(--fat-fg);}
.st-key-macros3_day [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"]{background:var(--protein-bg);}
.st-key-macros3_day [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"]{background:var(--carb-bg);}
.st-key-macros3_day [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"]{background:var(--fat-bg);}

/* ---------- progress ---------- */
[data-testid="stProgress"] [role="progressbar"] > div{background:var(--line);border-radius:999px;height:10px;}
[data-testid="stProgress"] [role="progressbar"] > div > div{background:linear-gradient(90deg,#10B981,#059669);border-radius:999px;}

/* ---------- alerts ---------- */
[data-testid="stAlert"]{border-radius:14px;}
[data-testid="stAlertContainer"]{border-radius:14px;border:1px solid var(--line);}
[data-testid="stAlertContainer"] p{color:var(--body);}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]),
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]){background:var(--mint);border-color:var(--mint-line);}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]){background:var(--amber-soft);border-color:#FED7AA;}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]){background:#FEF2F2;border-color:#FECACA;}

/* ---------- tables ---------- */
[data-testid="stTable"] table{border-radius:12px;overflow:hidden;border:1px solid var(--line);}
[data-testid="stTable"] th{background:var(--tint);color:var(--forest);font-weight:700;font-size:12.5px;}
[data-testid="stTable"] td{font-size:13.5px;}
[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden;border:1px solid var(--line);}

/* ---------- week strip ---------- */
.wk{display:flex;flex-direction:column;align-items:center;gap:2px;background:#fff;border:1px solid var(--line);border-radius:14px;padding:10px 2px;font-size:12px;line-height:1.3;color:#64748B;}
.wk b{font-size:13px;color:#0F172A;}
.wk span{font-weight:600;color:#0F172A;}
.wk i{font-style:normal;font-size:11px;}
.wk-on{border-color:#059669;background:#ECFDF5;}
.st-key-weekstrip [data-testid="stHorizontalBlock"]{gap:6px;}
@media (max-width:640px){
  .st-key-nav [data-testid="stHorizontalBlock"],.st-key-weekstrip [data-testid="stHorizontalBlock"]{flex-wrap:nowrap !important;gap:2px;}
  .st-key-nav [data-testid="stColumn"],.st-key-weekstrip [data-testid="stColumn"]{min-width:0 !important;flex:1 1 0 !important;width:auto !important;}
  .st-key-nav button{padding:6px 2px !important;flex-direction:column;gap:2px;}
  .st-key-nav button p{display:none !important;}
  .st-key-weekstrip .wk{padding:8px 0;font-size:10px;}
  .st-key-weekstrip .wk b{font-size:11px;}
  .st-key-weekstrip .wk i{font-size:9px;}
}
"""


def apply() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def brand(demo: bool) -> None:
    badge = ("<span style='margin-left:auto;font-size:11px;font-weight:700;padding:5px 12px;border-radius:999px;"
             "background:#FEF3C7;color:#92400E;'>Demo mode</span>") if demo else ""
    st.markdown(
        "<div class='brand'><div class='brand-mark'>N</div><div><div class='brand-name'>NutriChef</div>"
        f"<div class='brand-sub'>AI recipes with real nutrition</div></div>{badge}</div>",
        unsafe_allow_html=True)
