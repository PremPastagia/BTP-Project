# Architectural Specification Report: Academic Manuscript (.tex) & E2E Testing Track

**Agent**: `survey_explorer_3` (teamwork_preview_explorer)  
**Date**: 2026-09-18  
**Scope**: Requirement R3 (Academic Manuscript Generation) and Acceptance Criteria Verification via 4-Tier Testing Architecture  
**Working Directory**: `C:\Users\Prem Pastagia\Desktop\BTP\.agents\survey_explorer_3`  
**Target Workspace**: `C:\Users\Prem Pastagia\Desktop\BTP`  
**Reference Document**: `C:\Users\Prem Pastagia\Desktop\BTP\.agents\ORIGINAL_REQUEST.md`

---

## Executive Summary

This report establishes the technical and structural specifications for two core pillars of the "Modeling and Forecasting Natural Gas Prices in India" research project:
1. **Academic Manuscript Architecture (`.tex` file)**: A publication-grade LaTeX manuscript structure adhering strictly to peer-reviewed econometric and energy journal standards (e.g., *Energy Economics*, *International Journal of Forecasting*). It specifies the complete document layout, Section 1 through 7 content blueprints, empirical figure embedding specifications, and automated LaTeX table rendering protocols.
2. **E2E Testing Track & Acceptance Verification Architecture**: An independent, requirement-driven 4-tier testing hierarchy designed to rigorously verify all functional, statistical, and data-integrity criteria from `ORIGINAL_REQUEST.md` (zero data synthesis, 3-year CNG panel, 10-year spliced macro series, polynomial trend + harmonic seasonality + smooth splines GAM, conditional Gram-Schmidt orthogonalization, ARIMA benchmarking, RMSE comparison, and `.tex` generation).

An environment audit confirmed that Python 3.12 is installed with scientific libraries (`statsmodels`, `scipy`, `scikit-learn`, `matplotlib`, `seaborn`, `pandas`), while native LaTeX CLI binaries (`pdflatex`, `xelatex`, `tectonic`) are absent in the local Windows environment. Accordingly, a dual-mode strategy is defined: (i) strict automated validation of the standalone `.tex` artifact via an AST/regex validation engine, and (ii) portable compilation hooks for local and cloud environments.

---

# Part 1: Academic Manuscript (.tex File) Specification

## 1.1 Document Metadata & Typographic Standards

To guarantee universal compilation across standard TeX engines (`pdflatex`, `xelatex`, `lualatex`, Overleaf) without requiring obscure journal-specific style packages, the primary manuscript is architected on the standard `article` class with contemporary academic packages.

### Preamble Configuration
```latex
\documentclass[11pt,a4paper]{article}

% Core Typography & Geometry
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=1in]{geometry}
\usepackage{microtype}
\usepackage{setspace}
\onehalfspacing

% Mathematics & Econometrics
\usepackage{amsmath,amssymb,amsfonts,amsthm}
\usepackage{bm} % Bold math symbols

% Tables & Booktabs
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{multirow}
\usepackage{dcolumn} % Alignment on decimal point
\usepackage{caption}
\usepackage{subcaption}

% Graphics & Visuals
\usepackage{graphicx}
\usepackage{xcolor}
\graphicspath{{figures/}{../figures/}}

% Hyperlinks & Citations
\usepackage[numbers,sort&compress]{natbib}
\usepackage[colorlinks=true,linkcolor=blue!70!black,citecolor=blue!70!black,urlcolor=blue!70!black]{hyperref}

% Header / Footer
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\lhead{\small \textit{Natural Gas Price Modeling in India: A GAM Approach}}
\rhead{\small \thepage}
\renewcommand{\headrulewidth}{0.4pt}
```

### Paper Metadata
- **Title**: *Modeling and Forecasting Natural Gas Prices in India using Generalized Additive Models*
- **Authors**:
  - **Prem Pastagia** (Department of Industrial and Systems Engineering, Indian Institute of Technology Kharagpur, Roll No. 23IM10049)
  - **Balagopal G. Menon** (Department of Industrial and Systems Engineering, Indian Institute of Technology Kharagpur — Research Supervisor)
- **Keywords**: Generalized Additive Models (GAM), Natural Gas Pricing, Compressed Natural Gas (CNG), Gram-Schmidt Orthogonalization, ARIMA, Energy Forecasting, Administered Pricing Mechanism (APM), Splicing.

---

## 1.2 Section-by-Section Structural Breakdown

The manuscript is structured into seven primary sections, reflecting the rigor expected in top-tier energy economics journals:

```
manuscript.tex
├── Title & Author Affiliations
├── Abstract & Keywords
├── 1. Introduction
│   ├── 1.1 Energy Transition & Natural Gas in India
│   ├── 1.2 The Pricing Conundrum: Administrative vs. Market Forces
│   ├── 1.3 Methodological Gap: Beyond Rigid Linear Time-Series
│   └── 1.4 Research Contributions & Paper Organization
├── 2. Institutional Background of Indian Natural Gas & CNG Pricing
│   ├── 2.1 Historical Evolution: Pre-2014 to the 2014 Domestic Gas Formula
│   ├── 2.2 The 2021–2022 Global Energy Shock & Disconnect
│   ├── 2.3 The Kirit Parikh Committee Reforms (April 2023)
│   └── 2.4 Downstream Retailing Dynamics: City Gas Distribution (CGD) Pricing
├── 3. Data Engineering, Splicing & Empirical Diagnostics
│   ├── 3.1 Primary CNG Price Panel (Scraped Distributor Revisions)
│   ├── 3.2 Macroeconomic Demand Drivers: GDP & CPI Timeline
│   ├── 3.3 Legacy Base-Year Splicing Methodology
│   ├── 3.4 Temporal Disaggregation & Frequency Alignment
│   └── 3.5 Unit Root, Stationarity & Structural Break Diagnostics
├── 4. Econometric Methodology
│   ├── 4.1 Generalized Additive Model (GAM) Formulation
│   │   ├── 4.1.1 Polynomial Trend Specification
│   │   ├── 4.1.2 Harmonic Seasonal Basis (Fourier Series)
│   │   └── 4.1.3 Penalized Spline Estimation for Macro Drivers
│   ├── 4.2 Multicollinearity Diagnostics & Automated Gram-Schmidt Protocol
│   ├── 4.3 Benchmark Model: Seasonal ARIMA Specification
│   ├── 4.4 Model Selection & Information Criteria (AIC, BIC, GCV)
│   └── 4.5 Walk-Forward Out-of-Sample Cross-Validation Scheme
├── 5. Empirical Results & Diagnostics
│   ├── 5.1 Exploratory Data Analysis & Descriptive Statistics
│   ├── 5.2 Multicollinearity Screening & Orthogonalization Outcomes
│   ├── 5.3 Comparative Predictive Accuracy: GAM vs. ARIMA
│   ├── 5.4 Interpretation of Non-Linear Partial Dependence Splines
│   └── 5.5 Residual Diagnostics & Model Robustness Checks
├── 6. Discussion & Policy Implications
│   ├── 6.1 Economic Mechanics of Non-Linear Gas Demand Transmission
│   ├── 6.2 The Parikh Price Band and Downstream Price Pass-Through
│   └── 6.3 Strategic Implications for CGD Entities and Clean Fleet Adoption
├── 7. Conclusion & Future Research Directions
├── Acknowledgments
└── References
```

### Detailed Content Specification per Section

#### Section 1: Introduction
- **Context**: India's national goal of expanding natural gas share from ~6% to 15% of the primary energy basket by 2030.
- **Economic Significance**: Compressed Natural Gas (CNG) serves as the economic lifeblood for urban transport (buses, auto-rickshaws, commercial taxis) in major metropolises (Delhi-NCR, Mumbai, Ahmedabad).
- **Core Problem**: Natural gas prices in India exhibit sharp non-linearities: regulatory formula shifts, global LNG import parity spikes, and macroeconomic growth elasticities. Traditional econometric models (linear regressions, pure ARIMA) assume linear proportionalities or static stationarity, failing during regime shifts.
- **Contributions**:
  1. Development of an authentic multi-distributor panel dataset of Indian retail CNG prices without synthetic data imputation.
  2. Construction of a 10-year monthly spliced macroeconomic series reconciling multiple base-year revisions.
  3. Formulation of a Generalized Additive Model decomposing price dynamics into polynomial trends, harmonic seasonal cycles, and penalized splines.
  4. Integration of an automated Gram-Schmidt orthogonalization pipeline to resolve regressor collinearity before spline fitting.
  5. Empirical validation demonstrating significant forecast accuracy improvements (RMSE/MAE) over benchmark ARIMA models.

#### Section 2: Institutional Background of Indian Gas Pricing
- **Pre-2014 & Administered Pricing Mechanism (APM)**: Historical cost-plus pricing and the initial shift towards formula-based allocation.
- **2014 Domestic Gas Guidelines (Rangarajan Formula)**: Semi-annual pricing linked to trailing 4-hub international prices (Henry Hub, National Balancing Point, Russian gas, Alberta). Analysis of why this formula caused severe lag and divergence during the 2021-2022 global supply shocks.
- **Kirit Parikh Committee Recommendations (Implemented April 2023)**:
  - Transition to monthly price revisions.
  - Linkage to 10% of the Indian Crude Basket price.
  - Establishment of a floor ($4.00/MMBtu) and ceiling ($6.50/MMBtu, with a $0.25/year escalation) for legacy APM fields.
- **Downstream Retailing & City Gas Distribution (CGD)**: How retail distributors (IGL in Delhi-NCR, MGL in Mumbai, Gujarat Gas) blend domestic APM gas, high-pressure/high-temperature (HPHT) gas, and imported spot LNG (JKM/DES) to price CNG at the pump.

#### Section 3: Data Engineering, Splicing & Empirical Diagnostics
- **Primary Scraped Datasets**:
  - Panel of CNG retail prices (Rs./kg) across major distributors (IGL, MGL).
  - Explicit documentation of price change dates, effective periods, and city coverage.
- **Macroeconomic Predictors**:
  - Quarterly Real GDP (Rs. Crores) and Monthly Consumer Price Index (CPI General).
- **Base-Year Splicing**:
  - Mathematical formalization of the splicing factor at the overlapping year $T^*$:
    $$S = \frac{X_{T^*}^{\text{New Base}}}{X_{T^*}^{\text{Old Base}}}$$
    $$X_t^{\text{Spliced}} = X_t^{\text{Old Base}} \times S \quad (\forall t < T^*)$$
- **Temporal Disaggregation**: Interpolation of quarterly GDP to monthly frequency using quadratic / cubic spline and Denton-Cholette techniques preserving quarterly volume integrals.
- **Statistical Pre-tests**: Augmented Dickey-Fuller (ADF) test, KPSS test for stationarity, and Chow structural break test around the April 2023 policy intervention.

#### Section 4: Econometric Methodology
- **General GAM Formulation**:
  $$Y_t = \beta_0 + P_d(t) + \sum_{k=1}^K \left[ \alpha_k \sin\left(\frac{2\pi k t}{12}\right) + \beta_k \cos\left(\frac{2\pi k t}{12}\right) \right] + \sum_{j=1}^p s_j(X_{jt}) + \varepsilon_t$$
  Where:
  - $Y_t$ is the retail CNG price at month $t$.
  - $P_d(t) = \sum_{m=1}^d \gamma_m t^m$ is a polynomial deterministic trend of degree $d$.
  - $\sum_{k=1}^K [\dots]$ represents the Fourier harmonic basis capturing seasonal cyclicality of period 12 with $K$ harmonic frequencies.
  - $s_j(\cdot)$ are smooth, non-parametric spline functions (penalized B-splines / natural cubic splines) with roughness penalties $\lambda_j \int [s_j''(x)]^2 dx$.
- **Automated Gram-Schmidt Orthogonalization Protocol**:
  - Multi-stage detection: Compute Variance Inflation Factor (VIF) and pairwise Pearson correlation matrix $\mathbf{R}$.
  - Condition: If $\max(\text{VIF}_j) > 5.0$ or $|r_{ij}| > 0.80$ (e.g., between GDP and Income/CPI):
    - Let $u_1, u_2, \dots, u_m$ be the collinear regressors.
    - Set $v_1 = u_1$.
    - For $k = 2, \dots, m$:
      $$v_k = u_k - \sum_{j=1}^{k-1} \frac{\langle u_k, v_j \rangle}{\langle v_j, v_j \rangle} v_j$$
    - Pass normalized orthogonal components $v_k / \|v_k\|$ into the GAM smooth functions $s_k(v_k)$, preserving independent explanatory power without numerical instability.
- **Benchmark ARIMA Formulation**:
  - Seasonal $\text{ARIMA}(p, d, q) \times (P, D, Q)_{12}$ model estimated via maximum likelihood:
    $$\Phi_P(B^{12}) \phi_p(B) (1 - B)^d (1 - B^{12})^D Y_t = \Theta_Q(B^{12}) \theta_q(B) \varepsilon_t$$
- **Validation Scheme**: Walk-forward (rolling-origin) time-series cross-validation on out-of-sample data points. Metrics:
  $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{t=1}^N (Y_t - \hat{Y}_t)^2}, \quad \text{MAE} = \frac{1}{N} \sum_{t=1}^N |Y_t - \hat{Y}_t|$$

#### Section 5: Empirical Results & Diagnostics
- Full reporting of estimation parameters, effective degrees of freedom (EDF), and $p$-values.
- Rigorous comparative tables and empirical figures (detailed in §1.3).
- Model superiority evaluation proving lower out-of-sample RMSE and better residual diagnostics for GAM over ARIMA.

#### Section 6: Discussion & Policy Implications
- Analysis of how the Parikh committee's ceiling dampens retail volatility while shifting supply-deficit risk onto imported LNG spot exposures.
- Policy guidance for state road transport corporations and fleet transition economics.

#### Section 7: Conclusion
- Summary of empirical findings, confirmation of model superiority, caveats, and computational directions.

---

## 1.3 Empirical Figure & LaTeX Table Formatting Requirements

### Figure Requirements
All empirical figures must be exported in high-resolution format (300+ DPI PNG or vector PDF) to `paper/figures/` and referenced cleanly in `manuscript.tex`.

| Figure Label | Filename | Description / Content |
|---|---|---|
| `fig:cng_trajectories` | `fig_cng_historical.pdf` / `.png` | Multi-city historical CNG retail price trajectories (Delhi IGL, Mumbai MGL) with vertical marker at April 2023 (Parikh reform). |
| `fig:macro_spliced` | `fig_macro_spliced.pdf` / `.png` | 10-year monthly spliced macroeconomic timeline (Real GDP and CPI) showing seamless transition across base-year rebasing points. |
| `fig:gam_pdp` | `fig_gam_pdp.pdf` / `.png` | Multi-panel Partial Dependence Plots (PDPs) illustrating the non-linear relationship between CNG price and macroeconomic drivers (with 95% confidence bands). |
| `fig:forecast_comparison` | `fig_forecast_comparison.pdf` / `.png` | Out-of-sample forecast comparison: Actual CNG price vs. GAM forecast vs. ARIMA baseline forecast with prediction intervals. |
| `fig:residual_diagnostics` | `fig_residual_diagnostics.pdf` / `.png` | 4-panel residual diagnostic plot: Residual series over time, ACF of residuals, PACF of residuals, and Normal Q-Q plot. |

#### Standard Figure LaTeX Template
```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.92\textwidth]{fig_gam_pdp.pdf}
    \caption{Partial Dependence Plots (PDPs) for Non-Linear Macroeconomic Predictors in the GAM Framework. Shaded bands denote 95\% confidence intervals obtained via empirical Bayesian posterior simulation.}
    \label{fig:gam_pdp}
\end{figure}
```

### Table Requirements
All tables must use the `booktabs` package format (`\toprule`, `\midrule`, `\bottomrule`), never vertical rules (`|`), and report precise statistical metrics.

#### Table 1: Descriptive Statistics & Stationarity Pre-Tests
```latex
\begin{table}[htbp]
\centering
\caption{Descriptive Statistics and Unit Root Tests for Modeled Series}
\label{tab:descriptives}
\small
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrrrr@{}}
\toprule
\textbf{Variable} & \textbf{Mean} & \textbf{Std. Dev.} & \textbf{Min} & \textbf{Max} & \textbf{ADF Stat ($p$-val)} & \textbf{KPSS Stat} \\
\midrule
CNG Price (Delhi, Rs/kg)     & -- & -- & -- & -- & -- & -- \\
CNG Price (Mumbai, Rs/kg)    & -- & -- & -- & -- & -- & -- \\
Real GDP (Spliced, Rs. Cr.)  & -- & -- & -- & -- & -- & -- \\
CPI General (Spliced)        & -- & -- & -- & -- & -- & -- \\
APM Benchmark (\$/MMBtu)     & -- & -- & -- & -- & -- & -- \\
\bottomrule
\end{tabular*}
\begin{minipage}{\textwidth}
\vspace{1ex}\footnotesize
\textit{Notes:} ADF denotes the Augmented Dickey-Fuller test with constant and trend. KPSS denotes the Kwiatkowski-Phillips-Schmidt-Shin test for level stationarity.
\end{minipage}
\end{table}
```

#### Table 2: Model Performance Benchmarking (GAM vs. ARIMA)
```latex
\begin{table}[htbp]
\centering
\caption{Out-of-Sample Predictive Performance: Generalized Additive Model vs. ARIMA}
\label{tab:model_comparison}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrrr@{}}
\toprule
\textbf{Model Specification} & \textbf{In-Sample RMSE} & \textbf{Out-Sample RMSE} & \textbf{MAE} & \textbf{MAPE (\%)} & \textbf{AIC / GCV} \\
\midrule
ARIMA($p,d,q$) Baseline      & -- & -- & -- & -- & -- \\
SARIMA($p,d,q$)$(P,D,Q)_{12}$& -- & -- & -- & -- & -- \\
GAM (Linear Baseline)        & -- & -- & -- & -- & -- \\
GAM (Trend + Harmonics)      & -- & -- & -- & -- & -- \\
\textbf{Full GAM (Trend + Harmonics + Splines)} & \textbf{--} & \textbf{--} & \textbf{--} & \textbf{--} & \textbf{--} \\
\bottomrule
\end{tabular*}
\begin{minipage}{\textwidth}
\vspace{1ex}\footnotesize
\textit{Notes:} Out-of-sample metrics computed via rolling-origin walk-forward validation. Bold indicates the superior performing model architecture.
\end{minipage}
\end{table}
```

#### Table 3: GAM Component Significance and Effective Degrees of Freedom (EDF)
```latex
\begin{table}[htbp]
\centering
\caption{Generalized Additive Model Parametric and Smooth Term Estimates}
\label{tab:gam_estimates}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrr@{}}
\toprule
\textbf{Model Component} & \textbf{Coefficient / EDF} & \textbf{Std. Error / Ref. DF} & \textbf{$F$ / $t$-Statistic} & \textbf{$p$-value} \\
\midrule
\textit{Parametric Terms} & & & & \\
Intercept ($\beta_0$)                 & -- & -- & -- & -- \\
Linear Trend ($t$)                    & -- & -- & -- & -- \\
Quadratic Trend ($t^2$)               & -- & -- & -- & -- \\
Harmonic $\sin(2\pi t / 12)$          & -- & -- & -- & -- \\
Harmonic $\cos(2\pi t / 12)$          & -- & -- & -- & -- \\
\midrule
\textit{Smooth Spline Terms} & & & & \\
$s(\text{GDP Spliced})$               & -- & -- & -- & -- \\
$s(\text{CPI Spliced})$               & -- & -- & -- & -- \\
$s(\text{Orthogonal Macro Factor})$   & -- & -- & -- & -- \\
\bottomrule
\end{tabular*}
\begin{minipage}{\textwidth}
\vspace{1ex}\footnotesize
\textit{Notes:} EDF represents Effective Degrees of Freedom. For smooth spline terms, higher EDF indicates greater departure from strict linearity (EDF = 1 corresponds to a linear fit).
\end{minipage}
\end{table}
```

---

## 1.4 Local Environment Assessment & Automated Validation Engine

### Compiler Audit Findings
1. **Host Environment**: Windows 11 (OS Architecture: x64).
2. **Python Runtime**: Python 3.12.3 located at `C:\Users\Prem Pastagia\AppData\Local\Programs\Python\Python312\python.exe`.
3. **TeX Tooling Availability**:
   - `pdflatex`, `xelatex`, `lualatex`, `latexmk`: **NOT PRESENT** in PATH.
   - `tectonic`: **NOT PRESENT** in PATH; Winget package search for `tectonic` returned no matching package.
4. **PDF Inspection Libraries**: `pypdfium2` (v5.11.0) and `pdfminer.six` (v20260107) are installed in the Python environment.

### Architectural Solution: Pure-Python LaTeX Validator
Because a native LaTeX compiler is not pre-installed on the host OS, the delivery pipeline cannot rely exclusively on a background `pdflatex` call. We specify an automated validation script `scripts/validate_manuscript.py` that parses and verifies the `.tex` file for publication-readiness:

1. **Syntax & Delimiter Balance**:
   - Matches every `\begin{env}` with `\end{env}` (document, table, tabular*, figure, equation, align, itemize, enumerate).
   - Validates curly bracket `{}` and math delimiter `$` / `$$` matching.
2. **Asset Integrity Verification**:
   - Scans all `\includegraphics{...}` directives.
   - Asserts that every referenced image file physically exists in `paper/figures/` on disk with non-zero byte size.
3. **Table & Reference Auditing**:
   - Verifies all `\ref{fig:...}` and `\ref{tab:...}` have corresponding `\label{...}` declarations.
   - Ensures no raw unescaped LaTeX special characters (e.g., bare `%` instead of `\%`, bare `_` instead of `\_`, bare `&` outside tabular environments).
4. **Empirical Content Verification**:
   - Checks that placeholder text (`TODO`, `TBD`, `--`) has been replaced with actual empirical estimates, coefficients, and RMSE numbers.
5. **Portable Compilation Script (`scripts/build_paper.py`)**:
   - Checks for `pdflatex` or `tectonic` if installed in the future.
   - If present, executes 2-pass compilation with bibtex.
   - If absent, outputs clear instructions and produces a bundle zip ready for direct drop into Overleaf or arXiv.

---

# Part 2: E2E Testing Track & Acceptance Verification Architecture

## 2.1 Traceability Matrix: Acceptance Criteria to Test Verifications

Every verifiable requirement from `ORIGINAL_REQUEST.md` is mapped to an automated verification check:

| ID | Requirement from `ORIGINAL_REQUEST.md` | Category | Target Artifact / Script | Automated Verification Logic |
|---|---|---|---|---|
| **REQ-1** | Scrape historical CNG price changes for major distributors (IGL, MGL) into a multi-city panel dataset. | Data Adequacy | `data/cng_data.csv` | Verify file exists, contains columns `[date, city, distributor, price_inr_per_kg]`, covers at least 2 major distributors (IGL, MGL). |
| **REQ-2** | **CRITICAL CONSTRAINT:** Do NOT synthesize or fake data. Use only real scraped data. | Integrity Benchmark | `data/cng_data.csv`, `scripts/audit_provenance.py` | Run audit script: verify each price change matches verifiable historical price-revision notices (no continuous random/sinusoidal fake values). |
| **REQ-3** | CSV contains at least 3 years of monthly CNG price data. | Data Adequacy | `data/cng_data.csv` | Calculate `(max_date - min_date) >= 36 months` and count of distinct monthly periods $\ge 36$. |
| **REQ-4** | Extract historical macro data (GDP, CPI) from data.gov.in / econpulse / official sources, splicing legacy base-years. | Data Engineering | `data/macro_data.csv` | Verify file exists, columns `[date, gdp_spliced, cpi_spliced]`, continuous timeline across 2004-05 and 2011-12 rebasing points. |
| **REQ-5** | CSV contains at least 10 years of monthly macroeconomic data, properly interpolated. | Data Adequacy | `data/macro_data.csv` | Calculate `(max_date - min_date) >= 120 months`, zero missing/NaN values, smooth quarterly-to-monthly disaggregation. |
| **REQ-6** | Train Generalized Additive Model (GAM) with polynomial trend, harmonic basis, and smooth splines. | Model Execution | `models/gam_model.py`, `scripts/run_model.py` | Verify model object contains degree-$d$ polynomial trend, Fourier harmonic terms ($k=1,2$), and penalized spline terms for macro regressors. |
| **REQ-7** | **MULTICOLLINEARITY CONSTRAINT:** Test for multicollinearity; IF AND ONLY IF detected, automatically implement Gram-Schmidt orthogonalization. | Algorithmic Integrity | `models/multicollinearity.py` | Unit test with collinear data (triggers Gram-Schmidt) vs. orthogonal data (bypasses Gram-Schmidt). Confirm orthogonal vectors satisfy $\langle v_i, v_j \rangle \approx 0$. |
| **REQ-8** | Python script runs successfully, ingests data, and outputs Partial Dependence Plots (PDPs). | Model Execution | `paper/figures/fig_gam_pdp.png` | Script exit code == 0, generates valid multi-panel PDP image file on disk with non-empty byte size. |
| **REQ-9** | Quantitative RMSE comparison between GAM and baseline ARIMA. | Validation | `reports/metrics_comparison.json`, console output | Check quantitative metrics: $\text{RMSE}_{\text{GAM}} < \text{RMSE}_{\text{ARIMA}}$, output saved to JSON and formatted table. |
| **REQ-10**| Final academic manuscript generated (`.tex` file) detailing collection, methodology, empirical results, and superiority. | Manuscript Delivery | `paper/manuscript.tex` | Check `.tex` file exists, passes AST syntax validation, contains actual empirical figures, tables, and conclusive finding. |

---

## 2.2 The 4-Tier Testing Hierarchy

To guarantee zero regression and verify both scientific correctness and software quality, the test suite is formulated in 4 hierarchical tiers.

```
                  ┌──────────────────────────────────────────────┐
                  │ Tier 4: Real-World Workload Scenarios (5)    │
                  │  - Cold-Start Pipeline Execution             │
                  │  - Zero-Synthetic Cryptographic Audit       │
                  │  - Extreme Regime-Shift & Stress Simulation │
                  │  - Incremental Monthly Ingestion            │
                  │  - Publication Build & Package Verification  │
                  └──────────────────────┬───────────────────────┘
                                         │
                  ┌──────────────────────▼───────────────────────┐
                  │ Tier 3: Cross-Feature Interactions (5)       │
                  │  - Spliced Data -> Gram-Schmidt Gate -> GAM  │
                  │  - Collinear Regressors -> Spline Fitting    │
                  │  - Model Estimates -> LaTeX Table Generator  │
                  │  - Fitted GAM -> PDP Plot -> TeX Inclusion   │
                  │  - Metrics Output -> Conclusive Text Sync    │
                  └──────────────────────┬───────────────────────┘
                                         │
                  ┌──────────────────────▼───────────────────────┐
                  │ Tier 2: Boundary & Corner Cases (25 Tests)   │
                  │  - 5 tests per feature:                      │
                  │    F1: Data Engineering Boundary Cases       │
                  │    F2: GAM Model Boundary Cases              │
                  │    F3: Gram-Schmidt Edge Cases               │
                  │    F4: ARIMA & Cross-Validation Edge Cases   │
                  │    F5: LaTeX & Reporting Edge Cases          │
                  └──────────────────────┬───────────────────────┘
                                         │
                  ┌──────────────────────▼───────────────────────┐
                  │ Tier 1: Feature Coverage (25 Tests)          │
                  │  - 5 tests per feature:                      │
                  │    F1: Data Scraping & Splicing Ingestion    │
                  │    F2: GAM Architecture Components           │
                  │    F3: Multicollinearity Detection & Orthog. │
                  │    F4: Baseline ARIMA & RMSE Benchmarking    │
                  │    F5: Manuscript Generation & Formatting    │
                  └──────────────────────────────────────────────┘
```

---

### Tier 1: Feature Coverage (>=5 Tests Per Feature = 25 Tests)

#### Feature F1: Data Engineering & Scraping Integrity
- `test_f1_cng_data_schema`: Asserts `cng_data.csv` contains columns `[date, city, distributor, price_inr_per_kg]` with correct data types.
- `test_f1_cng_temporal_span`: Asserts `cng_data.csv` temporal span is $\ge 36$ calendar months (3 full years).
- `test_f1_macro_temporal_span`: Asserts `macro_data.csv` temporal span is $\ge 120$ calendar months (10 full years).
- `test_f1_macro_no_nans`: Asserts zero `NaN`, `null`, or infinite values in `macro_data.csv` across all monthly rows.
- `test_f1_base_year_continuity`: Asserts macroeconomic series is continuous without un-spliced step jumps at the 2011-12 rebasing junction.

#### Feature F2: Econometric GAM Architecture
- `test_f2_gam_polynomial_trend`: Asserts GAM model contains an explicit polynomial trend term $P_d(t)$ of order $d \ge 1$.
- `test_f2_gam_harmonic_seasonality`: Asserts inclusion of paired Fourier terms $\sin(2\pi k t/12)$ and $\cos(2\pi k t/12)$ for $k \in \{1, 2\}$.
- `test_f2_gam_smooth_splines`: Asserts macroeconomic regressors (GDP, CPI) are mapped to smooth spline terms ($s(\cdot)$).
- `test_f2_gam_fit_execution`: Asserts GAM model converges during training without numerical overflow or singular matrix errors.
- `test_f2_gam_prediction_shape`: Asserts out-of-sample predictions match the test set dimension and are strictly non-negative.

#### Feature F3: Multicollinearity Protocol & Gram-Schmidt Engine
- `test_f3_vif_calculation`: Asserts Variance Inflation Factor (VIF) function computes mathematically exact VIFs on known matrices.
- `test_f3_collinearity_detection_threshold`: Asserts trigger flag is set to `True` when $\text{VIF} > 5.0$ or correlation $|r| > 0.80$, and `False` otherwise.
- `test_f3_conditional_execution_gate`: Asserts Gram-Schmidt algorithm is invoked IF AND ONLY IF collinearity is detected.
- `test_f3_gram_schmidt_orthogonality`: Asserts resulting vectors $v_1, v_2$ have dot product $|\langle v_1, v_2 \rangle| < 10^{-7}$.
- `test_f3_gram_schmidt_span_preservation`: Asserts column space / variance span of orthogonalized vectors matches original regressor space.

#### Feature F4: Forecasting Benchmark & Validation Engine
- `test_f4_arima_estimation`: Asserts baseline ARIMA model fits on training data and estimates autoregressive parameters.
- `test_f4_walk_forward_cv`: Asserts walk-forward cross-validation splits maintain strict temporal ordering with no lookahead bias.
- `test_f4_rmse_calculation`: Asserts RMSE function matches standard formula $\sqrt{\frac{1}{N}\sum(y - \hat{y})^2}$.
- `test_f4_model_comparison_output`: Asserts model pipeline outputs a comparison dictionary containing both GAM and ARIMA RMSE values.
- `test_f4_pdp_generation`: Asserts partial dependence plot generation produces figure array with valid coordinate axes.

#### Feature F5: Academic Manuscript & Reporting Engine
- `test_f5_tex_file_generation`: Asserts `paper/manuscript.tex` exists and is non-empty (>5,000 bytes).
- `test_f5_tex_section_headers`: Asserts `.tex` contains all required sections (Abstract, Introduction, Background, Data, Methodology, Results, Discussion, Conclusion).
- `test_f5_tex_figure_inclusion`: Asserts `\includegraphics` commands reference valid figure files present in `paper/figures/`.
- `test_f5_tex_table_inclusion`: Asserts tables format numerical values (RMSE, AIC, EDF) using standard `booktabs` syntax.
- `test_f5_tex_conclusive_finding`: Asserts manuscript text includes explicit quantitative statements on model superiority ($\text{RMSE}_{\text{GAM}} < \text{RMSE}_{\text{ARIMA}}$).

---

### Tier 2: Boundary & Corner Cases (>=5 Tests Per Feature = 25 Tests)

#### Feature F1: Data Engineering Boundary Cases
- `test_b1_leap_year_handling`: Asserts date parsing correctly handles leap years (e.g. Feb 29, 2016, 2020, 2024) without calendar drift.
- `test_b1_unequal_distributor_revisions`: Asserts multi-city panel handles asynchronous price change dates (e.g. IGL updates on 1st, MGL updates on 15th).
- `test_b1_sparse_monthly_points`: Asserts interpolation functions correctly when a distributor has fewer revision announcements in a given year.
- `test_b1_extreme_macro_spike`: Asserts interpolation and splicing do not produce negative GDP or runaway values during the Q1 2020 lockdown dip.
- `test_b1_zero_negative_price_guard`: Asserts validation rejects or flags corrupted negative prices ($P \le 0$).

#### Feature F2: GAM Model Boundary Cases
- `test_b2_degree_zero_polynomial`: Asserts graceful handling/fallback if polynomial trend order is set to 0 (flat intercept).
- `test_b2_high_degree_polynomial_guard`: Asserts regularization or capping prevents Runge's phenomenon / catastrophic polynomial divergence at boundaries.
- `test_b2_extreme_smoothing_penalty`: Asserts that as smoothing penalty $\lambda \to \infty$, spline collapses to a linear slope.
- `test_b2_zero_smoothing_penalty`: Asserts pipeline prevents matrix singularity when smoothing penalty $\lambda \to 0$.
- `test_b2_short_time_series`: Asserts GAM model raises informative error or falls back gracefully if sample size $N < 20$.

#### Feature F3: Gram-Schmidt Edge Cases
- `test_b3_perfectly_collinear_vectors`: Asserts Gram-Schmidt detects and handles linearly dependent vectors ($u_2 = c \cdot u_1$) without division by zero.
- `test_b3_zero_collinearity_passthrough`: Asserts that when vectors are already orthogonal ($\langle u_1, u_2 \rangle = 0$), Gram-Schmidt leaves vectors unchanged.
- `test_b3_near_singular_matrix`: Asserts numerical stability when condition number $\kappa(\mathbf{X}) > 10^{12}$.
- `test_b3_vector_order_invariance`: Asserts orthogonal subspace span is invariant to the ordering of input variables.
- `test_b3_zero_variance_constant_regressor`: Asserts proper handling if one regressor is a constant vector.

#### Feature F4: Forecasting Boundary Cases
- `test_b4_single_step_vs_multi_step`: Asserts evaluation correctly separates 1-step-ahead rolling forecast from multi-step dynamic forecast.
- `test_b4_flat_price_regime`: Asserts ARIMA and GAM handle extended price freeze periods (e.g., administered freeze) without zero division in MAPE.
- `test_b4_identical_model_error`: Asserts tie-breaking logic if two model specifications produce identical RMSE.
- `test_b4_arima_unit_root_boundary`: Asserts ARIMA automated order selection avoids non-stationary or non-invertible parameter regions.
- `test_b4_minimal_train_split`: Asserts walk-forward validation minimum initial training window has sufficient degrees of freedom ($N_{\text{train}} \ge 24$).

#### Feature F5: Manuscript Boundary Cases
- `test_b5_missing_figure_detection`: Asserts validator catches missing image file before LaTeX compilation fails.
- `test_b5_special_character_escaping`: Asserts characters like `_`, `%`, `&`, `#` in variable names are properly escaped in `.tex`.
- `test_b5_extreme_coefficient_formatting`: Asserts very large or small numbers are formatted in scientific notation ($1.23 \times 10^{-4}$) rather than overflowing table columns.
- `test_b5_empty_table_cell_guard`: Asserts all table cells contain valid numerical or textual entries (no bare `NaN` or unclosed separators).
- `test_b5_nested_environment_balance`: Asserts deep subcaption and table environments close in correct reverse order.

---

### Tier 3: Cross-Feature Interactions (5 Tests)

- `test_x1_data_to_collinearity_to_gram_schmidt`: Ingests scraped CNG and spliced macro series, runs collinearity detection, verifies conditional Gram-Schmidt execution, and checks output dimensions match original sample.
- `test_x2_gram_schmidt_to_gam_spline`: Feeds orthogonalized regressors directly into the GAM fitting engine, verifying that spline convergence and EDF calculations succeed.
- `test_x3_gam_estimation_to_pdp_plot`: Fits GAM on historical data, generates Partial Dependence Plots, and verifies that the output plot captures non-linear turning points matching econometric expectations.
- `test_x4_walk_forward_to_latex_table`: Runs walk-forward cross-validation comparing GAM vs ARIMA, generates quantitative RMSE metrics, and verifies that the output LaTeX table snippet is dynamically generated with matching numerical values.
- `test_x5_end_to_end_pipeline_consistency`: Asserts that empirical numbers quoted in the manuscript abstract and conclusion exactly match the metrics computed by `scripts/run_model.py`.

---

### Tier 4: Real-World Workload Scenarios (5 Tests)

- `test_s1_cold_start_full_execution`: Executes the entire pipeline from scratch on a clean workspace:
  `data ingestion -> splicing -> collinearity check -> Gram-Schmidt -> GAM/ARIMA fit -> figure generation -> manuscript generation -> validation`.
  Asserts zero unhandled exceptions and all output artifacts generated within 60 seconds.
- `test_s2_zero_synthetic_data_audit`: Executes an automated cryptographic and historical plausibility audit across `data/cng_data.csv`. Asserts:
  1. Every record has an attributed primary source notice.
  2. Price series exhibit step-function behavior characteristic of retail fuel revisions (not Gaussian noise or artificial sinusoids).
  3. Hash digest match against verified collection ledger.
- `test_s3_regime_shift_stress_scenario`: Simulates the 2022 global energy crisis spike and the April 2023 Parikh price cap. Asserts that the GAM model with polynomial trend and harmonic seasonality captures structural inflection points without explosive forecast divergence.
- `test_s4_incremental_monthly_ingestion`: Ingests 12 additional months of newly announced CNG price revisions, verifies that models re-estimate smoothly, and confirms that LaTeX tables and plots update automatically without manual intervention.
- `test_s5_publication_package_verification`: Audits the final delivery directory (`paper/`), confirming that `manuscript.tex`, all embedded figures (`figures/*.pdf`, `*.png`), tables, references, and validation scripts form a self-contained, reproducible archive.

---

# Part 3: Implementation Architecture & File Layout

## 3.1 Recommended File Hierarchy

To enforce clean separation of concerns and maintain strict isolation between raw data, econometric models, and reporting artifacts:

```
C:\Users\Prem Pastagia\Desktop\BTP\
├── data/
│   ├── raw/                           # Authentic scraped notices & raw downloads
│   ├── processed/                     # Spliced and interpolated datasets
│   ├── cng_data.csv                   # Multi-city CNG panel (>= 3 years)
│   └── macro_data.csv                 # Spliced monthly macro series (>= 10 years)
├── models/
│   ├── __init__.py
│   ├── gam_pipeline.py                # GAM specification (trend, harmonics, splines)
│   ├── arima_baseline.py              # ARIMA benchmark and auto-order selection
│   ├── multicollinearity.py           # VIF test & Gram-Schmidt engine
│   └── evaluation.py                  # Walk-forward CV & RMSE comparison
├── paper/
│   ├── manuscript.tex                 # Master academic manuscript
│   ├── references.bib                 # BibTeX bibliography
│   ├── figures/                       # Generated empirical figures (PDF & PNG)
│   │   ├── fig_cng_historical.png
│   │   ├── fig_macro_spliced.png
│   │   ├── fig_gam_pdp.png
│   │   ├── fig_forecast_comparison.png
│   │   └── fig_residual_diagnostics.png
│   └── tables/                        # Generated LaTeX table snippets
│       ├── tab_descriptives.tex
│       ├── tab_model_comparison.tex
│       └── tab_gam_estimates.tex
├── scripts/
│   ├── run_pipeline.py                # End-to-end pipeline runner
│   ├── audit_provenance.py            # Zero-synthetic forensic verification
│   ├── generate_paper.py              # Assembles figures/tables into manuscript.tex
│   └── validate_manuscript.py         # Pure-Python LaTeX validator
├── tests/
│   ├── __init__.py
│   ├── test_tier1_feature.py          # Tier 1: 25 Feature coverage tests
│   ├── test_tier2_boundary.py         # Tier 2: 25 Boundary & corner cases
│   ├── test_tier3_interaction.py      # Tier 3: Cross-feature interaction tests
│   └── test_tier4_scenarios.py        # Tier 4: Real-world workload scenarios
├── run_tests.py                       # Automated test runner (unittest based)
├── TEST_READY.md                      # Test readiness declaration and audit log
└── README.md                          # Reproduction guide
```

## 3.2 Test Runner & Execution Protocol

In strict alignment with the **Ponytail** engineering rule (zero unnecessary dependencies, prefer standard library, boring over clever), the test suite will be implemented using Python's standard library `unittest` module:
- **Zero New Dependencies**: `unittest` is built into Python 3.12, requiring no third-party package installation (`pytest` is optional).
- **Execution Command**:
  ```powershell
  python -m unittest discover -s tests -p "test_*.py" -v
  ```
  Or via the centralized runner:
  ```powershell
  python run_tests.py
  ```
- **Execution Output**:
  - Console report displaying pass/fail counts per tier.
  - Updates `TEST_READY.md` with timestamped test execution results and coverage status.

---

# Part 4: Synthesis & Recommendations for Downstream Implementers

1. **For Milestone 1 (Data Scraping & Engineering)**:
   - Prioritize primary distributor revision dates (IGL Delhi and MGL Mumbai). Because CNG prices are set via formal public notices, pooling these two distributors easily yields a multi-city panel exceeding 3 years.
   - Splicing of GDP must use the official 2011-12 MoSPI back-series ratio or level splice at 2011-12 Q4 to ensure economic validity.
2. **For Milestone 2 (Econometric Modeling)**:
   - Use `statsmodels` (or `pygam` if installed; note `statsmodels.gam.api.GLMGam` is pre-installed in the Python environment, providing native B-splines and penalized additive modeling).
   - Ensure the Gram-Schmidt engine verifies the condition $\max(\text{VIF}) > 5.0$ before transforming features, logging the decision explicitly for verification.
3. **For Milestone 3 (Manuscript & Reporting)**:
   - Implement `scripts/generate_paper.py` to dynamically inject actual computed RMSE numbers, table contents, and figure paths into `paper/manuscript.tex`.
   - Run `scripts/validate_manuscript.py` as an automated gate before declaring milestone completion.
