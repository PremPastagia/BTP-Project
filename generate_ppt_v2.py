"""
BTP Presentation v2 — Empirical Results Edition
Generates BTP_Presentation_v2.pptx with real model outputs from the agent swarm.
Action titles follow the action-title-writer skill: each title = full sentence, states the so-what.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

BASE = r"C:\Users\Prem Pastagia\Desktop\BTP"
FIGS = os.path.join(BASE, "paper", "figures")
OUTPUT = os.path.join(BASE, "BTP_Presentation_v2.pptx")

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

BLACK  = RGBColor(0x0A, 0x0A, 0x0A)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
ACCENT = RGBColor(0x1A, 0x1A, 0x2E)   # dark navy
LIGHT  = RGBColor(0xF5, 0xF5, 0xF5)

# ── helpers ───────────────────────────────────────────────────────────────────

def blank_slide():
    return prs.slides.add_slide(prs.slide_layouts[6])   # completely blank

def add_rect(slide, left, top, width, height, fill_rgb):
    shape = slide.shapes.add_shape(1, Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid(); shape.fill.fore_color.rgb = fill_rgb
    shape.line.fill.background()
    return shape

def add_text(slide, text, left, top, width, height,
             size=18, bold=False, color=BLACK, align=PP_ALIGN.LEFT, wrap=True):
    txb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    txb.word_wrap = wrap
    tf = txb.text_frame; tf.word_wrap = wrap
    p = tf.paragraphs[0]; p.alignment = align
    run = p.add_run(); run.text = text
    run.font.size = Pt(size); run.font.bold = bold; run.font.color.rgb = color
    return txb

def add_bullet_block(slide, lines, left, top, width, height, size=15, color=BLACK):
    txb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    txb.word_wrap = True; tf = txb.text_frame; tf.word_wrap = True
    first = True
    for line in lines:
        if first:
            p = tf.paragraphs[0]; first = False
        else:
            p = tf.add_paragraph()
        p.space_before = Pt(4)
        run = p.add_run(); run.text = line
        run.font.size = Pt(size); run.font.color.rgb = color
    return txb

def add_image(slide, path, left, top, width=None, height=None):
    if not os.path.exists(path):
        print(f"  [WARN] image not found: {path}")
        return
    kw = {}
    if width:  kw["width"]  = Inches(width)
    if height: kw["height"] = Inches(height)
    slide.shapes.add_picture(path, Inches(left), Inches(top), **kw)

def header_bar(slide, title_text, subtitle_text=""):
    """Dark navy top bar with white title."""
    add_rect(slide, 0, 0, 13.33, 1.4, ACCENT)
    add_text(slide, title_text, 0.4, 0.1, 12.5, 0.8,
             size=24, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    if subtitle_text:
        add_text(slide, subtitle_text, 0.4, 0.9, 12.5, 0.4,
                 size=13, bold=False, color=RGBColor(0xBB, 0xBB, 0xCC), align=PP_ALIGN.LEFT)

def footer(slide, page_num):
    add_rect(slide, 0, 7.15, 13.33, 0.35, ACCENT)
    add_text(slide, "IIT Kharagpur · BTP Mid-Semester Evaluation · Prem Pastagia (23IM10049)",
             0.3, 7.17, 11, 0.25, size=9, color=WHITE)
    add_text(slide, str(page_num), 12.8, 7.17, 0.4, 0.25,
             size=9, color=WHITE, align=PP_ALIGN.RIGHT)


# ── SLIDE 1 — Title ───────────────────────────────────────────────────────────
s = blank_slide()
add_rect(s, 0, 0, 13.33, 7.5, ACCENT)
add_rect(s, 0.4, 2.0, 12.5, 0.07, WHITE)   # rule

logo = r"C:\Users\Prem Pastagia\Desktop\WhatsApp_Image_2026-09-18_at_3.10.59_AM-removebg-preview.png"
if not os.path.exists(logo):
    # fallback: check BTP folder
    logo = r"C:\Users\Prem Pastagia\Desktop\BTP\WhatsApp_Image_2026-09-18_at_3.10.59_AM-removebg-preview.png"
add_image(s, logo, 0.5, 0.3, height=1.4)

add_text(s, "Modeling and Forecasting Natural Gas Prices in India",
         0.4, 1.7, 12.5, 0.9, size=30, bold=True, color=WHITE)
add_text(s, "using Generalized Additive Models",
         0.4, 2.55, 12.5, 0.6, size=22, bold=False, color=RGBColor(0xCC, 0xCC, 0xDD))

add_text(s, "B.Tech Project — Mid-Semester Evaluation",
         0.4, 3.4, 12.5, 0.45, size=15, color=RGBColor(0xAA, 0xAA, 0xBB))
add_text(s, "Prem Pastagia  |  23IM10049",
         0.4, 3.95, 8, 0.4, size=16, bold=True, color=WHITE)
add_text(s, "Supervisor: Prof. Balagopal G. Menon",
         0.4, 4.45, 8, 0.4, size=14, color=RGBColor(0xCC, 0xCC, 0xDD))
add_text(s, "Dept. of Industrial & Systems Engineering  ·  IIT Kharagpur",
         0.4, 4.95, 10, 0.35, size=12, color=RGBColor(0xAA, 0xAA, 0xBB))


# ── SLIDE 2 — Problem ─────────────────────────────────────────────────────────
s = blank_slide()
header_bar(s,
    "Linear models systematically fail on Indian CNG data because regulation creates step-functions, not slopes.",
    "Why ARIMA and OLS cannot forecast natural gas prices in India")
footer(s, 2)

bullets = [
    "📌  India distributes CNG to 6M+ vehicles across 100+ cities via private City Gas Distributors (IGL, MGL, etc.)",
    "📌  Prices are revised irregularly — not a smooth curve, but sharp regulatory step-changes.",
    "📌  Global shocks (Russia-Ukraine 2022) triggered sudden APM ceiling revisions that linear models cannot anticipate.",
    "📌  GDP and Household Income both drive demand but are collinear (VIF > 45) — standard OLS is invalid here.",
    "📌  Result: ARIMA(1,1,2) achieves RMSE = 28.07 INR/kg on out-of-sample data — a 33% average error rate.",
]
add_bullet_block(s, bullets, 0.4, 1.6, 7.8, 5.5, size=14)
add_image(s, os.path.join(FIGS, "fig_cng_historical.png"), 8.4, 1.5, width=4.7)


# ── SLIDE 3 — Data ────────────────────────────────────────────────────────────
s = blank_slide()
header_bar(s,
    "We assembled 1,080 real city-month observations from 6 distributors — zero synthetic data points generated.",
    "Data Architecture: CNG Panel + Macroeconomic Series")
footer(s, 3)

# Left column: CNG panel
add_rect(s, 0.3, 1.55, 5.9, 0.4, RGBColor(0xE8, 0xE8, 0xF0))
add_text(s, "CNG Price Panel", 0.35, 1.58, 5.8, 0.33, size=13, bold=True)
cng_rows = [
    "Cities:   Delhi (IGL), Mumbai (MGL), Noida, Ghaziabad, Ahmedabad, Pune",
    "Period:   April 2011 – December 2025   (14.5 years)",
    "Obs:      1,080 city-month records",
    "Method:   Step-function Zero-Order Hold + TWAP between revisions",
    "Policy:   Zero synthetic data generated",
]
add_bullet_block(s, cng_rows, 0.35, 2.05, 5.8, 2.5, size=13)

# Right column: Macro panel
add_rect(s, 6.6, 1.55, 6.4, 0.4, RGBColor(0xE8, 0xE8, 0xF0))
add_text(s, "Macroeconomic Panel", 6.65, 1.58, 6.3, 0.33, size=13, bold=True)
macro_rows = [
    "Variables: GDP (Monthly), CPI Index, PFCE Income",
    "Period:    April 2011 – December 2025",
    "Obs:       177 monthly rows",
    "Method:    UN SNA Ratio Linking (base-year splicing)",
    "           Denton-Cholette temporal disaggregation (quarterly→monthly)",
]
add_bullet_block(s, macro_rows, 6.65, 2.05, 6.3, 2.5, size=13)

add_image(s, os.path.join(FIGS, "fig_macro_spliced.png"), 0.3, 4.55, width=12.5)


# ── SLIDE 4 — Methodology ─────────────────────────────────────────────────────
s = blank_slide()
header_bar(s,
    "The GAM replaces rigid linear coefficients with smooth splines — letting the model bend with the data.",
    "Methodology: GLMGam · Fourier Seasonality · Gram-Schmidt Orthogonalization")
footer(s, 4)

add_text(s,
    "Ŷₜ  =  β₀  +  Pₐ(t)  +  f_season(t)  +  g₁(GDP̃ₜ)  +  g₂(CPIₜ)  +  g₃(Ĩncomeₜ)  +  εₜ",
    0.4, 1.55, 12.5, 0.65, size=17, bold=True, color=ACCENT)

cols = [
    ("Pₐ(t)\nSecular Trend", "Linear polynomial captures long-run upward price trajectory."),
    ("f_season(t)\nFourier Harmonics", "K=2 sine/cosine pairs isolate routine seasonal cycles."),
    ("g₁, g₂, g₃\nCubic B-Splines", "Penalized splines (df=5) let each macro driver curve non-linearly."),
    ("Gram-Schmidt\nOrthogonalization", "VIF detected: GDP=46.24, Income=45.38.\nApplied Modified Gram-Schmidt → all VIFs reduced to 1.00."),
]
box_w = 2.9
for i, (title, body) in enumerate(cols):
    x = 0.35 + i * 3.2
    add_rect(s, x, 2.35, box_w, 0.55, ACCENT)
    add_text(s, title, x+0.1, 2.38, box_w-0.2, 0.5, size=12, bold=True, color=WHITE)
    add_text(s, body, x+0.1, 2.97, box_w-0.2, 1.5, size=12, color=BLACK)

add_image(s, os.path.join(FIGS, "fig_residual_diagnostics.png"), 0.3, 4.65, width=12.7)


# ── SLIDE 5 — Results ─────────────────────────────────────────────────────────
s = blank_slide()
header_bar(s,
    "The GAM reduces forecast error by 28.38% — proving non-linear splines outperform ARIMA on Indian CNG data.",
    "Empirical Results: Out-of-Sample Walk-Forward Cross-Validation (54 test months)")
footer(s, 5)

# Metric boxes
metrics = [
    ("GAM\nRMSE", "20.10", "INR/kg"),
    ("ARIMA\nRMSE", "28.07", "INR/kg"),
    ("Improvement", "28.38%", "RMSE reduction"),
    ("MAE (GAM)", "18.74", "vs 26.50 ARIMA"),
    ("MAPE (GAM)", "23.57%", "vs 33.42% ARIMA"),
]
for i, (label, val, unit) in enumerate(metrics):
    x = 0.3 + i * 2.55
    bg = RGBColor(0x1A, 0x1A, 0x2E) if i == 2 else RGBColor(0xF0, 0xF0, 0xF5)
    tc = WHITE if i == 2 else BLACK
    vc = WHITE if i == 2 else ACCENT
    add_rect(s, x, 1.55, 2.35, 1.5, bg)
    add_text(s, label, x+0.1, 1.6, 2.15, 0.45, size=11, bold=True, color=tc, align=PP_ALIGN.CENTER)
    add_text(s, val,   x+0.1, 2.1, 2.15, 0.55, size=22, bold=True, color=vc, align=PP_ALIGN.CENTER)
    add_text(s, unit,  x+0.1, 2.7, 2.15, 0.28, size=10, color=tc, align=PP_ALIGN.CENTER)

add_image(s, os.path.join(FIGS, "fig_forecast_comparison.png"), 0.3, 3.2, width=6.5)
add_image(s, os.path.join(FIGS, "fig_gam_pdp.png"), 7.0, 3.2, width=6.0)


# ── SLIDE 6 — Multicollinearity proof ────────────────────────────────────────
s = blank_slide()
header_bar(s,
    "Gram-Schmidt orthogonalization collapsed all VIFs from 46→1, making the macro regressors statistically valid.",
    "Multicollinearity Diagnostic: Before vs After Orthogonalization")
footer(s, 6)

# VIF table
headers = ["Regressor", "VIF Before", "VIF After", "Status"]
rows_data = [
    ["GDP Monthly (Cr INR)", "46.24", "1.00", "✅ Fixed"],
    ["CPI Index (Base 2012=100)", "14.07", "1.00", "✅ Fixed"],
    ["Income / PFCE (Cr INR)", "45.38", "1.00", "✅ Fixed"],
]
col_widths = [4.0, 2.2, 2.2, 2.0]
col_x = [0.5, 4.6, 6.9, 9.2]
row_h = 0.52

# header row
for j, (h, w, x) in enumerate(zip(headers, col_widths, col_x)):
    add_rect(s, x, 1.6, w-0.05, row_h, ACCENT)
    add_text(s, h, x+0.1, 1.65, w-0.2, row_h-0.1, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

for i, row in enumerate(rows_data):
    y = 1.6 + (i+1) * (row_h + 0.06)
    bg = RGBColor(0xF5, 0xF5, 0xF5) if i % 2 == 0 else WHITE
    for j, (cell, w, x) in enumerate(zip(row, col_widths, col_x)):
        add_rect(s, x, y, w-0.05, row_h, bg)
        color = RGBColor(0xC0, 0x00, 0x00) if j == 1 else (RGBColor(0x00, 0x70, 0x00) if j == 2 else BLACK)
        add_text(s, cell, x+0.1, y+0.08, w-0.2, row_h-0.1, size=13, bold=(j==1 or j==2), color=color, align=PP_ALIGN.CENTER)

add_text(s, "Threshold for concern: VIF > 10   |   Threshold for severe multicollinearity: VIF > 40",
         0.5, 3.7, 12.0, 0.35, size=12, color=RGBColor(0x55, 0x55, 0x55))

add_text(s, "Modified Gram-Schmidt: construct orthonormal basis Q = [q₁, q₂, q₃] such that qᵢ · qⱼ = 0 ∀ i≠j",
         0.5, 4.15, 12.0, 0.4, size=13, bold=True, color=ACCENT)

add_image(s, os.path.join(FIGS, "fig_macro_spliced.png"), 0.5, 4.7, width=12.0)


# ── SLIDE 7 — Conclusions & Next Steps ───────────────────────────────────────
s = blank_slide()
header_bar(s,
    "GAM beats ARIMA by 28.38% — the next phase adds city fixed-effects and Vahan demand proxies.",
    "Conclusions and Execution Roadmap")
footer(s, 7)

conclusions = [
    "✅  1,080 real CNG city-month observations collected — zero synthetic points.",
    "✅  Gram-Schmidt orthogonalization: all VIFs collapsed from >40 to exactly 1.00.",
    "✅  GAM RMSE = 20.10 vs ARIMA RMSE = 28.07 — a confirmed 28.38% improvement.",
    "✅  52/60 automated E2E validation tests passing; 8 remaining = manuscript gates.",
]
add_bullet_block(s, conclusions, 0.4, 1.6, 7.8, 2.5, size=14)

nextsteps = [
    "🔜  Phase 4: City-level fixed effects to isolate distributor-specific pricing regimes.",
    "🔜  Phase 5: Integrate Vahan vehicle registration data as a demand-side proxy.",
    "🔜  Phase 6: Expand panel to 12+ cities; retrain and re-validate GAM.",
    "🔜  Phase 7: Final research manuscript submission.",
]
add_bullet_block(s, nextsteps, 0.4, 4.3, 7.8, 2.8, size=14)

# Mini scoreboard on the right
add_rect(s, 8.6, 1.55, 4.4, 5.6, RGBColor(0x1A, 0x1A, 0x2E))
add_text(s, "SCORECARD", 8.8, 1.65, 4.0, 0.4, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
scores = [
    ("Data", "1,080 obs", "6 cities · 14 yrs"),
    ("Macro", "177 months", "GDP · CPI · PFCE"),
    ("GAM RMSE", "20.10", "INR / kg"),
    ("ARIMA RMSE", "28.07", "INR / kg"),
    ("Δ Improvement", "28.38%", "RMSE reduction"),
    ("VIF (post)", "1.00", "all regressors"),
]
for i, (lbl, val, sub) in enumerate(scores):
    y = 2.2 + i * 0.82
    add_text(s, lbl, 8.75, y,     2.0, 0.35, size=10, color=RGBColor(0xAA, 0xAA, 0xCC))
    add_text(s, val, 10.8, y,     2.0, 0.35, size=14, bold=True, color=WHITE, align=PP_ALIGN.RIGHT)
    add_text(s, sub, 8.75, y+0.38, 4.0, 0.28, size=9, color=RGBColor(0x88, 0x88, 0xAA))


# ── Save ──────────────────────────────────────────────────────────────────────
prs.save(OUTPUT)
print(f"Saved: {OUTPUT}")
