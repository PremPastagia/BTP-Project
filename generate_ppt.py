from pptx import Presentation
from pptx.util import Inches, Pt
import os

prs = Presentation()

# Title Slide
slide = prs.slides.add_slide(prs.slide_layouts[0])
title = slide.shapes.title
subtitle = slide.placeholders[1]
title.text = "Modeling and Forecasting Natural Gas Prices in India\nusing Generalized Additive Models"
subtitle.text = "Bachelor of Technology Project Mid-Term Presentation"

def add_slide_with_text(title_text, content_text):
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = title_text
    
    tf = slide.placeholders[1].text_frame
    tf.clear()  
    p = tf.paragraphs[0]
    p.text = content_text
    p.font.size = Pt(18)
    return slide

# Slide 1: Intro
s1_content = """Accurate forecasting of Compressed Natural Gas prices is critical for India's energy transition and macroeconomic stability.

Why is this forecasting imperative?
• The Reality of Pricing Dynamics: Natural gas prices are highly susceptible to non-linear fluctuations.
• The Discrepancy Between Demand and Consumption: A reduction in vehicle loan interest rates augments actual consumption significantly compared to theoretical demand.

The Substantial Impact We Can Generate:
• For Policymakers: Furnishes a rigorous mathematical foundation to comprehend economic augmentations.
• For City Gas Distribution Corporations: Facilitates robust revenue forecasting predicated upon actual consumption."""
add_slide_with_text("Introduction, Necessity, & Ramifications", s1_content)

# Slide 2: The Data Visualization (Image)
slide_2 = prs.slides.add_slide(prs.slide_layouts[5]) # Title only layout
slide_2.shapes.title.text = "The Forecasting Deficit: Linear Models vs Market Reality"
img_path = r"C:\Users\Prem Pastagia\.gemini\antigravity\brain\b173086f-b867-4117-8a19-b350560cedbd\cng_prices_bw.png"
if os.path.exists(img_path):
    # Add image centered
    left = Inches(1.0)
    top = Inches(1.8)
    height = Inches(5.0)
    slide_2.shapes.add_picture(img_path, left, top, height=height)

# Slide 3: Lit Review
s3_content = """Traditional modeling architectures fail to apprehend the complex, non-linear realities.

The Deficiency in Current Literature
• Predominant academic papers primarily employ Linear Regression or Exponential Smoothing.
• The Inherent Flaw: These models erroneously enforce a strictly proportional, linear relationship.

Our Novel Approach: Generalized Additive Models
• We circumvent strict linear coefficients by instituting smooth splines: y = α + f1(x1) + f2(x2).
• These mathematical splines calibrate the model to ascend, plateau, and descend organically."""
add_slide_with_text("Literature Review & Methodological Novelty", s3_content)

# Slide 4 (Table)
slide_4 = prs.slides.add_slide(prs.slide_layouts[5])
slide_4.shapes.title.text = "Variable Selection & Data Architecture"
rows, cols = 7, 3
left = Inches(0.5)
top = Inches(1.5)
width = Inches(9.0)
height = Inches(5.0)
table_shape = slide_4.shapes.add_table(rows, cols, left, top, width, height)
table = table_shape.table

data = [
    ["Variable Classification", "Specific Influencing Factor", "Verified Institutional Data Source"],
    ["Dependent Variable (Y)", "Natural Gas Price", "Petroleum Planning and Analysis Cell"],
    ["Independent Variable (X1)", "Theoretical Demand Estimates", "Ministry of Petroleum and Natural Gas"],
    ["Independent Variable (X2)", "Consumption: Vehicle Miles Traveled", "Ministry of Road Transport and Highways"],
    ["Independent Variable (X3)", "Consumption: Household Utility", "Petroleum and Natural Gas Regulatory Board"],
    ["Independent Variable (X4)", "Gross Domestic Product", "Ministry of Statistics and Programme Implementation"],
    ["Independent Variable (X5)", "Disposable Income", "Reserve Bank of India Database"]
]

for row_idx, row in enumerate(data):
    for col_idx, val in enumerate(row):
        cell = table.cell(row_idx, col_idx)
        cell.text = val
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(14)

# Slide 5: Methodology
s5_content = """Applying polynomial trends, harmonic bases, and mathematical orthogonalization.

The Foundational Generalized Additive Model Structure
1. Trend: Polynomial tracking of the long-term trajectory.
2. Seasonality: Harmonic-based cyclicity (routine fluctuations).
3. Holiday and Regulatory Events: Abrupt, localized shocks.

Resolving Multicollinearity (The Gram-Schmidt Process)
• The Statistical Jeopardy: Gross Domestic Product and Disposable Income generates severe multicollinearity.
• The Mathematical Resolution: Transform these into orthogonal polynomials utilizing the Gram-Schmidt process.
• Inner mathematical product equals absolute zero (v1 · v2 = 0)."""
add_slide_with_text("Methodology — GAM Framework & Gram-Schmidt Process", s5_content)

# Slide 6: Status
s6_content = """We have successfully established the theoretical framework; the subsequent phase encompasses computational modeling.

What we have accomplished thus far:
1. Finalized the overarching problem statement.
2. Identified and validated uninterrupted access to authentic Indian institutional datasets.
3. Selected the Generalized Additive Model incorporating smooth splines.
4. Defined the explicit mathematical resolution (Gram-Schmidt process).

Subsequent execution steps:
• Data Cleansing & Mathematical Normalization
• Gram-Schmidt Orthogonalization Implementation
• Program Generalized Additive Model Architecture
• Cross-Validation & Concurvity Diagnostics"""
add_slide_with_text("Current Status & Future Execution Blueprint", s6_content)

output_path = r"C:\Users\Prem Pastagia\Desktop\BTP\BTP_Presentation.pptx"
prs.save(output_path)
print(f"Presentation updated and saved as {output_path}")
