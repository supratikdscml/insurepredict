"""Global CSS that gives the app its InsurePredict look (green, clean, card based)."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root{
  --ip-green:#0f9d6c; --ip-green-dark:#0b7f56; --ip-green-light:#e6f6ef; --ip-green-soft:#f1faf6;
  --ip-ink:#10231e; --ip-muted:#5d6e68; --ip-line:#e3e9e6;
}
html, body, [class*="css"], .stApp, .stMarkdown, button, input, textarea, select{
  font-family:'Inter', -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
}

/* ---- page chrome ------------------------------------------------------ */
.stApp{ background:linear-gradient(135deg,#f7fcf9 0%, #eaf7f0 55%, #f4fbf8 100%); color:var(--ip-ink); }
.stApp::before{
  content:""; position:fixed; top:-170px; right:-130px; width:560px; height:560px; border-radius:50%;
  background:radial-gradient(circle at 35% 35%, rgba(23,177,132,.20), rgba(23,177,132,0) 70%); pointer-events:none; z-index:0;
}
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer,
[data-testid="stSidebar"], [data-testid="collapsedControl"]{ display:none !important; }
.block-container{ max-width:1120px !important; padding-top:5.6rem !important; padding-bottom:3rem !important; position:relative; z-index:1; }

/* ---- top bar ---------------------------------------------------------- */
.ip-topbar{
  position:fixed; top:0; left:0; right:0; height:64px; z-index:999; display:flex; align-items:center; justify-content:center;
  background:rgba(255,255,255,.92); backdrop-filter:blur(8px); border-bottom:1px solid var(--ip-line);
}
.ip-brand{ display:flex; align-items:center; gap:10px; font-weight:700; font-size:19px; color:var(--ip-ink); letter-spacing:-.2px; }
.ip-logo{ width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center;
  background:linear-gradient(135deg,#17b184,#0b7f56); box-shadow:0 6px 16px rgba(15,157,108,.35); }
.ip-logo svg{ width:20px; height:20px; stroke:#fff; fill:none; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }

/* ---- hero ------------------------------------------------------------- */
.ip-hero{ padding-top:56px; }
.ip-badge{ display:inline-flex; align-items:center; gap:7px; padding:6px 12px; border-radius:999px; font-size:12px; font-weight:600;
  color:var(--ip-green-dark); background:var(--ip-green-light); border:1px solid rgba(15,157,108,.18); margin-bottom:18px; }
.ip-badge svg{ width:13px; height:13px; fill:var(--ip-green); }
.ip-h1{ font-size:46px; line-height:1.08; font-weight:800; letter-spacing:-1.2px; color:var(--ip-ink); margin:0 0 18px 0; }
.ip-h1 span{ color:var(--ip-green); display:block; }
.ip-lead{ font-size:15.5px; line-height:1.65; color:var(--ip-muted); margin:0 0 26px 0; max-width:520px; }
.ip-features{ display:grid; grid-template-columns:1fr 1fr; gap:12px; max-width:540px; }
.ip-feature{ display:flex; align-items:center; gap:12px; padding:13px 14px; border-radius:12px; background:rgba(255,255,255,.75);
  border:1px solid rgba(15,157,108,.10); box-shadow:0 2px 8px rgba(16,86,62,.04); }
.ip-icon{ flex:0 0 34px; height:34px; border-radius:9px; background:var(--ip-green-light); display:flex; align-items:center; justify-content:center; }
.ip-icon svg{ width:17px; height:17px; stroke:var(--ip-green-dark); fill:none; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }
.ip-feature b{ display:block; font-size:13px; font-weight:700; color:var(--ip-ink); }
.ip-feature small{ display:block; font-size:11.5px; color:var(--ip-muted); margin-top:1px; }

/* ---- form card -------------------------------------------------------- */
[data-testid="stForm"]{
  background:#fff; border:1px solid rgba(15,157,108,.08) !important; border-radius:18px; padding:30px 28px 26px 28px;
  box-shadow:0 22px 60px rgba(16,86,62,.13);
}
.ip-card-icon{ width:48px; height:48px; border-radius:50%; margin:0 auto 12px auto; display:flex; align-items:center; justify-content:center;
  background:linear-gradient(135deg,#17b184,#0b7f56); box-shadow:0 8px 20px rgba(15,157,108,.35); }
.ip-card-icon svg{ width:22px; height:22px; stroke:#fff; fill:none; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }
.ip-card-title{ text-align:center; font-size:19px; font-weight:700; color:var(--ip-ink); margin:0; }
.ip-card-sub{ text-align:center; font-size:12.5px; color:var(--ip-muted); margin:5px 0 12px 0; }

[data-testid="stWidgetLabel"] p{ font-size:12.5px !important; font-weight:600 !important; color:#1c2b27 !important; }
[data-testid="stForm"] [data-baseweb="input"], [data-testid="stForm"] [data-baseweb="select"] > div{
  border-radius:10px !important; border:1px solid var(--ip-line) !important; background:#fff !important; min-height:42px; }
[data-testid="stForm"] [data-baseweb="input"] > div{ background:transparent !important; }
[data-testid="stForm"] [data-baseweb="input"]:focus-within, [data-testid="stForm"] [data-baseweb="select"] > div:focus-within{
  border-color:var(--ip-green) !important; box-shadow:0 0 0 3px rgba(15,157,108,.15) !important; }
[data-testid="stForm"] input{ font-size:13.5px !important; }
[data-testid="stForm"] input::placeholder{ color:#9aa9a4 !important; opacity:1; }
[data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"]{ display:none !important; }

[data-testid="stFormSubmitButton"] button{
  width:100%; height:46px; border:0 !important; border-radius:10px; font-weight:600; color:#fff !important; margin-top:6px;
  background:linear-gradient(135deg,#19b487,#0c8a5f) !important; box-shadow:0 10px 24px rgba(15,157,108,.32); transition:transform .12s, box-shadow .12s; }
[data-testid="stFormSubmitButton"] button p{ color:#fff !important; font-weight:600; font-size:14.5px; }
[data-testid="stFormSubmitButton"] button:hover{ transform:translateY(-1px); box-shadow:0 14px 28px rgba(15,157,108,.38); }

/* secondary buttons (outside the form) */
.stButton > button{ border-radius:10px; border:1px solid var(--ip-line); background:#fff; color:var(--ip-ink); font-weight:600; }
.stButton > button:hover{ border-color:var(--ip-green); color:var(--ip-green-dark); }

/* ---- results ---------------------------------------------------------- */
.ip-eyebrow{ font-size:11.5px; font-weight:700; letter-spacing:1.4px; color:var(--ip-green-dark); margin:48px 0 10px 0; }
.ip-result{ border-radius:18px; padding:26px 28px; color:#fff; background:linear-gradient(135deg,#17b184 0%, #0b7f56 100%);
  box-shadow:0 18px 44px rgba(15,157,108,.30); }
.ip-result-label{ font-size:13px; font-weight:500; opacity:.9; }
.ip-result-value{ font-size:50px; font-weight:800; letter-spacing:-1.5px; line-height:1.1; margin:4px 0 8px 0; }
.ip-result-range{ font-size:13.5px; opacity:.95; }
.ip-result-range span{ opacity:.8; }
.ip-stats{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:14px 0 8px 0; }
.ip-stat{ background:rgba(255,255,255,.85); border:1px solid rgba(15,157,108,.10); border-radius:12px; padding:13px 14px; }
.ip-stat small{ display:block; font-size:11px; color:var(--ip-muted); font-weight:600; text-transform:uppercase; letter-spacing:.6px; }
.ip-stat b{ display:block; font-size:17px; color:var(--ip-ink); margin-top:3px; }
.ip-stat i{ display:block; font-style:normal; font-size:11.5px; color:var(--ip-muted); margin-top:1px; }
.ip-section-title{ font-size:15px; font-weight:700; color:var(--ip-ink); margin:20px 0 2px 0; }
.ip-note{ font-size:12px; color:var(--ip-muted); line-height:1.5; }
.ip-footer{ text-align:center; font-size:12px; color:var(--ip-muted); margin-top:34px; line-height:1.6; }

@media (max-width:900px){
  .ip-h1{ font-size:34px; } .ip-features{ grid-template-columns:1fr; } .ip-stats{ grid-template-columns:1fr; }
  .ip-hero{ padding-top:8px; } .ip-eyebrow{ margin-top:12px; } .ip-result-value{ font-size:40px; }
}
</style>
"""
