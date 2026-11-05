"""
BTP Presentation v3 — Complete Narrative Edition
Combines v1 (theoretical framing) + v2 (empirical results) into one coherent deck.
Structure: Problem → Literature → Variable Design → Methodology → Progress (Data) → Results → Next Steps
Action titles follow action-title-writer skill: full sentence, states the so-what.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

BASE   = r"C:\Users\Prem Pastagia\Desktop\BTP"
FIGS   = os.path.join(BASE, "paper", "figures")
OUTPUT = os.path.join(BASE, "BTP_Presentation_v3.pptx")

BLACK  = RGBColor(0x0A, 0x0A, 0x0A)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
NAVY   = RGBColor(0x1A, 0x1A, 0x2E)
GREY   = RGBColor(0xF2, 0xF2, 0xF5)
DKGREY = RGBColor(0x55, 0x55, 0x66)
GREEN  = RGBColor(0x00, 0x70, 0x00)
RED    = RGBColor(0xC0, 0x00, 0x00)
MUTED  = RGBColor(0xBB, 0xBB, 0xCC)
ACCENT = RGBColor(0x22, 0x44, 0x88)   # secondary accent (blue)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)


# ── helpers ───────────────────────────────────────────────────────────────────

def blank():
    return prs.slides.add_slide(prs.slide_layouts[6])

def rect(slide, l, t, w, h, rgb):
    s = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = rgb; s.line.fill.background()
    return s

def txt(slide, text, l, t, w, h, size=14, bold=False, color=BLACK,
        align=PP_ALIGN.LEFT, italic=False):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tb.word_wrap = True
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = bold
    r.font.color.rgb = color; r.font.italic = italic
    return tb

def bullets(slide, lines, l, t, w, h, size=13, color=BLACK, bold_first=False):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tb.word_wrap = True; tf = tb.text_frame; tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_before = Pt(5)
        r = p.add_run(); r.text = line
        r.font.size = Pt(size); r.font.color.rgb = color
        r.font.bold = (bold_first and i == 0)

def img(slide, path, l, t, w=None, h=None):
    if not os.path.exists(path):
        print(f"  [WARN] missing: {path}"); return
    kw = {}
    if w: kw["width"]  = Inches(w)
    if h: kw["height"] = Inches(h)
    slide.shapes.add_picture(path, Inches(l), Inches(t), **kw)

def header(slide, title, subtitle=""):
    rect(slide, 0, 0, 13.33, 1.45, NAVY)
    rect(slide, 0, 1.45, 13.33, 0.06, ACCENT)
    txt(slide, title, 0.35, 0.08, 12.6, 0.85,
        size=20, bold=True, color=WHITE)
    if subtitle:
        txt(slide, subtitle, 0.35, 0.95, 12.6, 0.44,
            size=11, color=MUTED)

def footer(slide, n, total=9):
    rect(slide, 0, 7.18, 13.33, 0.32, NAVY)
    txt(slide, "IIT Kharagpur  ·  BTP Mid-Semester Evaluation  ·  Prem Pastagia (23IM10049)",
        0.3, 7.2, 11.5, 0.25, size=8, color=WHITE)
    txt(slide, f"{n} / {total}", 12.6, 7.2, 0.6, 0.25, size=8, color=WHITE, align=PP_ALIGN.RIGHT)

def section_divider(slide, section_label, slide_n, total=9):
    """Full-bleed dark section break."""
    rect(slide, 0, 0, 13.33, 7.5, NAVY)
    txt(slide, section_label.upper(), 1.0, 2.8, 11.0, 1.2,
        size=36, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(slide, f"Slide {slide_n} of {total}", 0.3, 7.1, 12.5, 0.3,
        size=9, color=MUTED, align=PP_ALIGN.RIGHT)

def metric_box(slide, l, t, w, h, label, value, unit, highlight=False):
    bg = NAVY if highlight else GREY
    tc = WHITE if highlight else DKGREY
    vc = WHITE if highlight else ACCENT
    rect(slide, l, t, w, h, bg)
    txt(slide, label, l+0.1, t+0.08, w-0.2, 0.35, size=10, color=tc, align=PP_ALIGN.CENTER)
    txt(slide, value, l+0.1, t+0.45, w-0.2, 0.55, size=20, bold=True, color=vc, align=PP_ALIGN.CENTER)
    txt(slide, unit,  l+0.1, t+1.05, w-0.2, 0.28, size=9,  color=tc, align=PP_ALIGN.CENTER)

LOGO_PATH = r"C:\Users\Prem Pastagia\Desktop\WhatsApp_Image_2026-09-18_at_3.10.59_AM-removebg-preview.png"
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = os.path.join(BASE, "WhatsApp_Image_2026-09-18_at_3.10.59_AM-removebg-preview.png")

# =============================================================================
# SLIDE 1 — Title
# =============================================================================
s = blank()
rect(s, 0, 0, 13.33, 7.5, NAVY)
rect(s, 0.4, 2.1, 12.5, 0.06, WHITE)

img(s, LOGO_PATH, 0.5, 0.3, h=1.4)

txt(s, "Modeling and Forecasting Natural Gas Prices in India",
    0.4, 1.75, 12.5, 0.85, size=28, bold=True, color=WHITE)
txt(s, "using Generalized Additive Models",
    0.4, 2.62, 12.5, 0.55, size=20, color=MUTED)

txt(s, "B.Tech Project  ·  Mid-Semester Evaluation Report",
    0.4, 3.45, 12.5, 0.4, size=13, color=MUTED)
txt(s, "Prem Pastagia   |   23IM10049",
    0.4, 4.0,  8.0, 0.42, size=16, bold=True, color=WHITE)
txt(s, "Supervisor: Prof. Balagopal G. Menon",
    0.4, 4.52, 8.0, 0.38, size=13, color=MUTED)
txt(s, "Department of Industrial and Systems Engineering  ·  Indian Institute of Technology Kharagpur",
    0.4, 5.0,  12.0, 0.35, size=11, color=RGBColor(0x88, 0x88, 0xAA))

# =============================================================================
# SLIDE 2 — Problem: Why forecasting matters & linear models fail
# =============================================================================
s = blank()
header(s,
    "India's CNG prices follow regulatory step-functions — ARIMA assumes smooth slopes and fails at every shock.",
    "Problem Statement  ·  Why standard time-series forecasting breaks on Indian energy data")
footer(s, 2)

# Left: narrative bullets from v1
bullets(s, [
    "🎯  Natural gas price forecasting is critical for India's energy transition and macroeconomic stability.",
    "",
    "⚠️  The Reality of Pricing Dynamics",
    "     CNG prices are revised irregularly — not gradual curves but abrupt step-changes by each distributor.",
    "     Global shocks (Russia-Ukraine 2022) triggered sudden APM ceiling revisions overnight.",
    "",
    "⚠️  The Discrepancy Between Demand and Consumption",
    "     Vehicle loan rate cuts → surge in actual CNG consumption far beyond theoretical demand projections.",
    "     Household gas connections growth → non-linear baseload shifts across cities.",
    "",
    "⚠️  Why ARIMA and OLS break here",
    "     Both assume proportional, linear responses — an assumption that shatters at regulatory discontinuities.",
    "     ARIMA(1,1,2) achieves RMSE = 28.07 INR/kg — a ~33% average forecast error.",
], 0.35, 1.6, 6.8, 5.6, size=12)

img(s, os.path.join(FIGS, "fig_cng_historical.png"), 7.3, 1.6, w=5.8)

# =============================================================================
# SLIDE 3 — Literature Review & Methodological Novelty
# =============================================================================
s = blank()
header(s,
    "Existing literature uses linear models that cannot capture India's regulatory discontinuities — GAMs fill this gap.",
    "Literature Review  ·  Methodological Novelty")
footer(s, 3)

# Two-column layout
rect(s, 0.3, 1.6, 6.0, 0.45, NAVY)
txt(s, "The Deficiency in Current Literature", 0.4, 1.65, 5.8, 0.35, size=13, bold=True, color=WHITE)
bullets(s, [
    "• Dominant papers employ Linear Regression, ARIMA, or Exponential Smoothing for energy forecasting.",
    "• These architectures enforce a strictly proportional relationship between drivers and price.",
    "• They cannot model: (a) regulatory step-changes, (b) demand saturation plateaus, (c) non-linear macro effects.",
    "• Seasonal decomposition (STL, X-13) is widely used but has no causal structure — it cannot extrapolate drivers.",
], 0.35, 2.15, 5.9, 3.2, size=12)

rect(s, 6.8, 1.6, 6.2, 0.45, ACCENT)
txt(s, "Our Novel Approach: Generalized Additive Models", 6.9, 1.65, 6.0, 0.35, size=13, bold=True, color=WHITE)
bullets(s, [
    "• Replace fixed linear coefficients with smooth, piecewise polynomial splines.",
    "• Mathematical form:  Ŷₜ = β₀ + Σ sᵢ(Xᵢₜ) + εₜ",
    "  where each sᵢ is a penalized cubic B-spline that can ascend, plateau, and descend organically.",
    "• Decompose the time-series into:",
    "     Polynomial trend  →  long-run price trajectory",
    "     Harmonic seasonality (Fourier)  →  routine cyclical fluctuations",
    "     Smooth splines per driver  →  non-linear macro effects",
], 6.85, 2.15, 6.1, 3.4, size=12)

# Bottom: The key insight box
rect(s, 0.3, 5.65, 12.7, 1.3, GREY)
txt(s, "The Key Insight:",
    0.5, 5.72, 3.0, 0.35, size=12, bold=True, color=NAVY)
txt(s, "A GAM equipped with B-splines and Fourier harmonics captures the non-linearity inherent in Indian CNG pricing while remaining interpretable — each smooth term shows exactly how a single economic driver contributes to price, independently of the others.",
    0.5, 6.1, 12.3, 0.8, size=12, color=BLACK)

# =============================================================================
# SLIDE 4 — Variable Selection & Data Architecture (from v1 table)
# =============================================================================
s = blank()
header(s,
    "We designed a MECE variable architecture covering demand, consumption, and macroeconomic drivers.",
    "Variable Selection  ·  Data Architecture  ·  Institutional Sources")
footer(s, 4)

# Build the table
col_widths = [3.0, 3.5, 5.5]
col_x      = [0.3, 3.4, 7.0]
headers_t  = ["Variable Classification", "Specific Factor", "Verified Institutional Source"]
rows_data  = [
    ["Dependent Variable (Y)",       "CNG / Natural Gas Price",          "Petroleum Planning & Analysis Cell (PPAC)"],
    ["Sectoral: Transportation (X₁)", "Vehicle Miles Traveled (VMT)",    "MoRTH — Vahan Dashboard"],
    ["Sectoral: Household (X₂)",      "Gas Connection Expansion",        "PNGRB (Petroleum & Natural Gas Regulatory Board)"],
    ["Macro Driver (X₃)",             "GDP (Monthly, Cr INR)",           "MoSPI — National Accounts Statistics"],
    ["Macro Driver (X₄)",             "Disposable Income / PFCE",        "RBI Handbook of Statistics on Indian Economy"],
    ["Macro Driver (X₅)",             "CPI Inflation Index",             "MoSPI — Consumer Price Index"],
    ["Exogenous Shock (X₆)",          "APM Gas Price Ceiling Revisions", "Ministry of Petroleum & Natural Gas"],
]
row_h = 0.56
for j, (h, w, x) in enumerate(zip(headers_t, col_widths, col_x)):
    rect(s, x, 1.6, w-0.06, 0.48, NAVY)
    txt(s, h, x+0.1, 1.65, w-0.2, 0.38, size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
for i, row in enumerate(rows_data):
    y = 2.15 + i * (row_h + 0.04)
    bg = GREY if i % 2 == 0 else WHITE
    for j, (cell, w, x) in enumerate(zip(row, col_widths, col_x)):
        rect(s, x, y, w-0.06, row_h, bg)
        txt(s, cell, x+0.1, y+0.08, w-0.2, row_h-0.12,
            size=11, color=(NAVY if j == 0 else BLACK), bold=(j == 0))

txt(s, "Architecture principle: Mutually Exclusive, Collectively Exhaustive (MECE) — every major demand and supply driver is covered without redundancy.",
    0.3, 7.0, 12.7, 0.3, size=9, color=DKGREY)

# =============================================================================
# SLIDE 5 — Methodology Deep-Dive (from both v1 and v2)
# =============================================================================
s = blank()
header(s,
    "The GAM decomposes price into trend, seasonality, and smooth macro splines after Gram-Schmidt orthogonalization.",
    "Methodology  ·  GLMGam · Fourier Harmonics · Penalized B-Splines · Gram-Schmidt")
footer(s, 5)

# Model equation
rect(s, 0.3, 1.58, 12.7, 0.72, GREY)
txt(s, "Ŷₜ  =  β₀  +  Pₐ(t)  +  f_season(t)  +  g₁(GDP̃ₜ)  +  g₂(CPIₜ)  +  g₃(Ĩncomeₜ)  +  εₜ",
    0.5, 1.65, 12.3, 0.58, size=18, bold=True, color=NAVY, align=PP_ALIGN.CENTER)

# Four component boxes
components = [
    ("Pₐ(t)\nPolynomial Trend",
     "Linear secular trend captures the long-term upward price trajectory driven by structural energy demand growth."),
    ("f_season(t)\nFourier Harmonics",
     "K=2 sine/cosine frequency pairs isolate routine seasonal cycles (e.g., winter heating demand peaks)."),
    ("g₁, g₂, g₃\nCubic B-Splines",
     "Penalized splines (df=5) let each macro driver curve non-linearly — GDP effect saturates at high levels; CPI effect steepens post-shock."),
    ("Gram-Schmidt\nOrthogonalization",
     "GDP & Income were collinear (VIF > 45). Applied Modified Gram-Schmidt → all post-orthogonalization VIFs = 1.00 before spline fitting."),
]
bw = 3.0
for i, (title, body) in enumerate(components):
    x = 0.3 + i * 3.26
    rect(s, x, 2.42, bw, 0.55, NAVY)
    txt(s, title, x+0.1, 2.45, bw-0.2, 0.48, size=11, bold=True, color=WHITE)
    rect(s, x, 2.98, bw, 2.0, GREY)
    txt(s, body,  x+0.1, 3.05, bw-0.2, 1.88, size=11, color=BLACK)

# Bottom row: implementation details
bullets(s, [
    "Implementation:  statsmodels.gam.api.GLMGam  ·  Identity link  ·  Python 3.12",
    "Train/Test Split:  Expanding walk-forward window  ·  123 months training (Apr 2011–Jun 2021)  ·  54 months held out (Jul 2021–Dec 2025)",
    "Baseline:  ARIMA(p,d,q) — order selected via AIC grid search  →  Best order: ARIMA(1,1,2)",
], 0.3, 5.12, 12.7, 1.3, size=12)

img(s, os.path.join(FIGS, "fig_residual_diagnostics.png"), 0.3, 6.25, w=12.7)

# =============================================================================
# SLIDE 6 — Mid-Semester Progress: Data Pipeline
# =============================================================================
s = blank()
header(s,
    "Mid-semester progress: we collected 1,080 real city-month CNG observations — zero synthetic data generated.",
    "Progress Report  ·  Data Engineering  ·  Verified Pipeline")
footer(s, 6)

# Progress badge
rect(s, 10.5, 1.58, 2.55, 1.05, RGBColor(0x00, 0x88, 0x44))
txt(s, "✅  MILESTONE 1", 10.6, 1.62, 2.35, 0.38, size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
txt(s, "COMPLETE", 10.6, 2.02, 2.35, 0.52, size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

bullets(s, [
    "📊  CNG Price Panel",
    "     Cities: Delhi (IGL), Mumbai (MGL), Noida, Ghaziabad, Ahmedabad, Pune",
    "     Period: April 2011 – December 2025   (14.5 years of real market data)",
    "     Observations: 1,080 city-month records   |   Method: Step-function Zero-Order Hold + TWAP",
    "     Integrity: Zero synthetic points — all data from verified distributor price-revision notifications",
    "",
    "📈  Macroeconomic Panel",
    "     Variables: GDP Monthly (Cr INR), CPI Index (Base 2012=100), PFCE Income",
    "     Observations: 177 continuous monthly rows  |  Period: April 2011 – December 2025",
    "     Splicing method: UN SNA Ratio Linking for base-year changes",
    "     Frequency conversion: Denton-Cholette temporal disaggregation (quarterly GDP → monthly)",
    "",
    "🔬  Verification Gate: 5-agent forensic audit passed (2 reviewers + 2 challengers + 1 auditor)",
    "     Denton-Cholette benchmark preservation error < 10⁻⁷",
], 0.35, 1.58, 10.0, 5.25, size=12)

img(s, os.path.join(FIGS, "fig_macro_spliced.png"), 0.3, 6.2, w=12.7)

# =============================================================================
# SLIDE 7 — Multicollinearity Proof (VIF table)
# =============================================================================
s = blank()
header(s,
    "Gram-Schmidt collapsed all VIFs from 46→1, making the macro regressors statistically valid for the GAM.",
    "Multicollinearity Diagnostics  ·  Before vs After Modified Gram-Schmidt Orthogonalization")
footer(s, 7)

# VIF Table
col_w2 = [4.2, 2.3, 2.3, 2.3]
col_x2 = [0.3, 4.6, 7.0, 9.4]
h2 = ["Regressor", "VIF Before", "VIF After", "Status"]
r2 = [
    ["GDP Monthly (Cr INR)",         "46.24", "1.00", "✅ Fixed"],
    ["CPI Index (Base 2012=100)",     "14.07", "1.00", "✅ Fixed"],
    ["Income / PFCE (Cr INR)",        "45.38", "1.00", "✅ Fixed"],
]
rh2 = 0.56
for j, (h, w, x) in enumerate(zip(h2, col_w2, col_x2)):
    rect(s, x, 1.6, w-0.06, 0.5, NAVY)
    txt(s, h, x+0.1, 1.65, w-0.2, 0.38, size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
for i, row in enumerate(r2):
    y = 2.18 + i * (rh2 + 0.06)
    bg = GREY if i % 2 == 0 else WHITE
    for j, (cell, w, x) in enumerate(zip(row, col_w2, col_x2)):
        rect(s, x, y, w-0.06, rh2, bg)
        clr = RED if j == 1 else (GREEN if j == 2 else BLACK)
        txt(s, cell, x+0.1, y+0.1, w-0.2, rh2-0.12, size=14,
            bold=(j in [1,2]), color=clr, align=PP_ALIGN.CENTER)

txt(s, "Threshold for concern: VIF > 10   |   Severe multicollinearity: VIF > 40",
    0.3, 3.75, 12.5, 0.35, size=11, color=DKGREY, italic=True)

rect(s, 0.3, 4.2, 12.7, 0.62, GREY)
txt(s, "Modified Gram-Schmidt:  Construct orthonormal basis Q = [q₁, q₂, q₃] such that  qᵢ · qⱼ = 0  ∀ i≠j",
    0.45, 4.28, 12.4, 0.45, size=14, bold=True, color=NAVY, align=PP_ALIGN.CENTER)

# Right-side implication bullets
bullets(s, [
    "Why this matters:",
    "• Without orthogonalization, the spline coefficients for GDP and Income are mathematically indeterminate.",
    "• After orthogonalization, each g(·) term captures a statistically independent marginal effect.",
    "• The Partial Dependence Plots on the next slide are valid only because VIF = 1.00.",
], 0.35, 5.0, 12.5, 2.1, size=12)

img(s, os.path.join(FIGS, "fig_gam_pdp.png"), 0.3, 6.2, w=12.7)

# =============================================================================
# SLIDE 8 — Empirical Results
# =============================================================================
s = blank()
header(s,
    "The GAM reduces forecast error by 28.38% over ARIMA — empirically confirming the theoretical hypothesis.",
    "Empirical Results  ·  Out-of-Sample Walk-Forward Cross-Validation  ·  54 Test Months")
footer(s, 8)

# Metric boxes (top row)
mets = [
    ("GAM\nRMSE",     "20.10", "INR/kg",        True),
    ("ARIMA\nRMSE",   "28.07", "INR/kg",         False),
    ("Improvement",   "28.38%", "RMSE reduction", True),
    ("MAE\nGAM",      "18.74", "vs 26.50 ARIMA", False),
    ("MAPE\nGAM",     "23.57%","vs 33.42% ARIMA",False),
]
for i, (lbl, val, unit, hi) in enumerate(mets):
    metric_box(s, 0.3 + i*2.55, 1.58, 2.4, 1.45, lbl, val, unit, highlight=hi)

# Two charts
img(s, os.path.join(FIGS, "fig_forecast_comparison.png"), 0.3,  3.18, w=6.6)
img(s, os.path.join(FIGS, "fig_gam_pdp.png"),             7.1,  3.18, w=5.9)

txt(s, "↑ Forecast comparison: GAM (solid) vs ARIMA (dashed) vs actual CNG price  |  Jul 2021–Dec 2025",
    0.3, 6.88, 6.6, 0.28, size=9, color=DKGREY, italic=True)
txt(s, "↑ Partial Dependence Plots: non-linear marginal effect of each macro driver on CNG price",
    7.1, 6.88, 5.9, 0.28, size=9, color=DKGREY, italic=True)

# =============================================================================
# SLIDE 9 — Conclusions & Next Steps
# =============================================================================
s = blank()
header(s,
    "We have proven the GAM framework works — the next phase adds city fixed-effects, Vahan data, and full paper.",
    "Conclusions  ·  Execution Roadmap  ·  Remaining Milestones")
footer(s, 9)

# Left: what we set out to do (v1 framing) → what we proved (v2 results)
rect(s, 0.3, 1.58, 12.7, 0.42, NAVY)
txt(s, "What We Set Out to Do  →  What We Proved", 0.4, 1.62, 12.5, 0.32, size=12, bold=True, color=WHITE)
bullets(s, [
    "Hypothesis: GAMs with B-splines outperform ARIMA on Indian CNG data.",
    "→  Confirmed: GAM RMSE = 20.10  vs  ARIMA RMSE = 28.07  (28.38% improvement).",
    "",
    "Hypothesis: GDP and Income collinearity requires Gram-Schmidt orthogonalization.",
    "→  Confirmed: VIF dropped from 46.24 → 1.00 across all macro regressors.",
    "",
    "✅  1,080 real CNG observations collected across 6 cities (2011–2025).",
    "✅  177-month macro panel assembled via Denton-Cholette temporal disaggregation.",
    "✅  52/60 automated E2E validation tests passing.",
], 0.35, 2.08, 12.5, 4.65, size=14)

# =============================================================================
# Save
# =============================================================================
prs.save(OUTPUT)
print(f"Saved: {OUTPUT}")
print(f"Slides: {len(prs.slides)}")
