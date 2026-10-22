"""Reusable UI components (HTML blocks, charts, panels)."""
from __future__ import annotations

from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

from . import config as cfg
from .predictor import PredictionResult
from .styles import CSS

# --- inline SVG icons (Lucide-style paths) -----------------------------------
ICONS = {
    "check": '<circle cx="12" cy="12" r="9"/><polyline points="8 12 11 15 16 9"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
    "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/>',
    "trend": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "scale": '<line x1="12" y1="3" x2="12" y2="21"/><path d="M5 7h14"/><path d="M5 7l-3 7a3 3 0 0 0 6 0z"/><path d="M19 7l-3 7a3 3 0 0 0 6 0z"/>',
}


def svg(name: str) -> str:
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def usd(value: float) -> str:
    """Dollar amount using an HTML entity so Markdown never treats '$' as math."""
    return f"&#36;{value:,.0f}"


def html(block: str) -> None:
    """Render an HTML block. Indentation/blank lines are stripped so Markdown can't turn it into a code block."""
    cleaned = "\n".join(line.strip() for line in block.strip().splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


# --- page chrome -------------------------------------------------------------
def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def render_topbar() -> None:
    html(f'<div class="ip-topbar"><div class="ip-brand"><div class="ip-logo">{svg("check")}</div>{cfg.APP_NAME}</div></div>')


def render_hero() -> None:
    star = '<svg viewBox="0 0 24 24"><path d="M12 2l2.2 6.3L21 10l-6.8 1.7L12 18l-2.2-6.3L3 10l6.8-1.7z"/></svg>'
    features = [
        ("zap", "Instant Results", "Estimates in seconds"),
        ("shield", "Secure &amp; Private", "Nothing is stored"),
        ("trend", "Accurate Predictions", "ML-powered analysis"),
        ("scale", "Plan Ahead", "Explore what-if scenarios"),
    ]
    cards = "".join(
        f'<div class="ip-feature"><div class="ip-icon">{svg(icon)}</div><div><b>{title}</b><small>{sub}</small></div></div>'
        for icon, title, sub in features)
    html(f"""
    <div class="ip-hero">
      <div class="ip-badge">{star} AI-Powered Predictions</div>
      <h1 class="ip-h1">Get Your Insurance <span>Price Prediction</span></h1>
      <p class="ip-lead">Use our machine-learning model to estimate your insurance premium based on your personal
      information. Get an instant estimate in seconds, together with a likely range and what-if scenarios.</p>
      <div class="ip-features">{cards}</div>
    </div>
    """)


def render_form_header() -> None:
    html(f"""
    <div class="ip-card-icon">{svg("file")}</div>
    <p class="ip-card-title">Calculate Premium</p>
    <p class="ip-card-sub">Enter your details to get started</p>
    """)


def render_footer() -> None:
    html("""
    <div class="ip-footer">
      Educational estimate only &mdash; not an insurance quote, medical advice or a guarantee of price.<br>
      Amounts are annual charges in US dollars, learned from a historical sample of records.
    </div>
    """)


# --- results -----------------------------------------------------------------
def _scenario_chart(result: PredictionResult) -> alt.Chart:
    df = pd.DataFrame({"Scenario": [s.label for s in result.scenarios], "Estimate": [s.estimate for s in result.scenarios]})
    top = max(df["Estimate"].max(), 1) * 1.28
    base = alt.Chart(df).encode(
        y=alt.Y("Scenario:N", sort=None, title=None, axis=alt.Axis(labelFontSize=12, labelLimit=240, ticks=False, domain=False)),
        x=alt.X("Estimate:Q", title=None, scale=alt.Scale(domain=[0, top]),
                axis=alt.Axis(format="$,.0f", grid=True, gridColor="#e9efec", domain=False, labelFontSize=11)))
    bars = base.mark_bar(cornerRadiusEnd=6, size=24).encode(
        color=alt.condition(alt.datum.Scenario == "Your profile", alt.value("#0f9d6c"), alt.value("#9fd8c1")),
        tooltip=[alt.Tooltip("Scenario:N"), alt.Tooltip("Estimate:Q", format="$,.0f")])
    labels = base.mark_text(align="left", dx=6, fontSize=12, fontWeight=600, color="#10231e").encode(
        text=alt.Text("Estimate:Q", format="$,.0f"))
    return (bars + labels).properties(height=max(90, 46 * len(df))).configure_view(strokeWidth=0).configure(background="transparent")


def render_results(result: PredictionResult, metadata: dict) -> None:
    ref = metadata.get("reference_charges", {})
    p = result.person
    group_avg = ref.get("smoker_mean") if p.smoker == "yes" else ref.get("nonsmoker_mean")
    overall = ref.get("mean")

    html(f"""
    <div class="ip-eyebrow">YOUR ESTIMATE</div>
    <div class="ip-result">
      <div class="ip-result-label">Estimated annual premium</div>
      <div class="ip-result-value">{usd(result.estimate)}</div>
      <div class="ip-result-range">Likely range {usd(result.low)} &ndash; {usd(result.high)}
        <span>({result.interval_coverage:.0%} prediction interval)</span></div>
    </div>
    """)

    stats = [("BMI category", result.bmi_category, f"BMI {p.bmi:.1f}")]
    if group_avg:
        stats.append(("Group average", usd(group_avg), "smokers" if p.smoker == "yes" else "non-smokers"))
    if overall:
        diff = (result.estimate / overall - 1) * 100
        stats.append(("Vs. overall average", f"{diff:+.0f}%", f"average {usd(overall)}"))
    cells = "".join(f'<div class="ip-stat"><small>{a}</small><b>{b}</b><i>{c}</i></div>' for a, b, c in stats)
    html(f'<div class="ip-stats">{cells}</div>')

    html('<div class="ip-section-title">What-if scenarios</div>')
    if len(result.scenarios) > 1:
        st.altair_chart(_scenario_chart(result), width="stretch")
        notes = []
        for s in result.scenarios[1:]:
            delta = s.estimate - result.estimate
            notes.append(f"<b>{s.label}</b>: {usd(abs(delta))} {'lower' if delta < 0 else 'higher'}")
        html(f'<p class="ip-note">{" &nbsp;·&nbsp; ".join(notes)}.<br>'
             'These compare historical records with different profiles; they are associations, not guarantees.</p>')
    else:
        html('<p class="ip-note">No what-if scenarios apply: you are already a non-smoker with a BMI in the healthy range.</p>')

    html(f'<p class="ip-note">The range is a typical error band around the estimate. About {result.interval_coverage:.0%} of past cases fell inside such a band, '
         'so some real charges will still land outside it.</p>')


def record_history(result: PredictionResult) -> None:
    history = st.session_state.setdefault("history", [])
    p = result.person
    history.insert(0, {
        "Time": datetime.now().strftime("%H:%M:%S"), "Age": p.age, "Gender": p.sex.title(), "BMI": p.bmi,
        "Children": p.children, "Smoker": p.smoker.title(), "Region": p.region.title(),
        "Estimate ($)": round(result.estimate), "Low ($)": round(result.low), "High ($)": round(result.high)})
    del history[cfg.HISTORY_LIMIT:]


def render_history() -> None:
    history = st.session_state.get("history", [])
    if not history:
        return
    df = pd.DataFrame(history)
    with st.expander(f"Session history ({len(df)})"):
        st.dataframe(df, hide_index=True, width="stretch")
        c1, c2 = st.columns(2)
        c1.download_button("Download CSV", df.to_csv(index=False).encode(), "insurepredict_session.csv", "text/csv", width="stretch")
        if c2.button("Clear history", width="stretch"):
            st.session_state["history"] = []
            st.rerun()


def render_model_card(metadata: dict, version_warning: str | None) -> None:
    m = metadata.get("test_metrics", {})
    itv = metadata.get("interval", {})
    with st.expander("About this model & its limitations"):
        if version_warning:
            st.warning(version_warning)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Test R²", f"{m.get('r2', 0):.2f}")
        c2.metric("Avg. error (MAE)", f"${m.get('mae', 0):,.0f}")
        c3.metric("RMSE", f"${m.get('rmse', 0):,.0f}")
        c4.metric("Training records", f"{metadata.get('n_train', 0):,}")
        st.markdown(
            f"""
**Model:** {metadata.get('model_name', 'n/a')}, trained {metadata.get('trained_at', 'n/a')[:10]} (scikit-learn {metadata.get('sklearn_version', 'n/a')}).
Cross-validated RMSE on the training data was about \\${metadata.get('cv_rmse', 0):,.0f}; the metrics above come from a test set used once.

**Prediction interval:** {itv.get('method', 'n/a')}, a constant band of ±\\${itv.get('halfwidth', 0):,.0f}, aiming for {itv.get('coverage', 0):.0%} coverage
({itv.get('test_coverage', 0):.1%} on the test set).

**Inputs used:** age, gender, BMI, number of children, smoking status and region. Smoking status is by far the strongest factor, followed by BMI and age;
gender and region have almost no effect.

**Limitations**
- Trained on about 1,300 historical records, so estimates for unusual profiles (for example, ages above 64) are less reliable.
- No medical history or plan details are used, so rare very expensive cases will be under-predicted.
- The data may reflect historical pricing bias, and the results show associations, not causes.
- Amounts are in US dollars; this is not an insurance quote.
""")
