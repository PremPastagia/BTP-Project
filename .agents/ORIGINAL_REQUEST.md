# Original User Request

## Initial Request — 2026-09-17T22:08:44Z

End-to-end execution of the "Modeling and Forecasting Natural Gas Prices in India" research paper, including data scraping, model training, and final manuscript generation.

Working directory: `C:\Users\Prem Pastagia\Desktop\BTP`
Integrity mode: benchmark

## Requirements

### R1. Data Collection & Engineering
- Scrape historical CNG price changes for major distributors (e.g., IGL, MGL) from the web to construct a multi-city panel dataset.
- **CRITICAL CONSTRAINT:** Do NOT synthesize or fake data under any circumstances. Use only real scraped data. If only 9 points can be found, the team must figure out how to model it or fail.
- Extract historical macroeconomic data (GDP, CPI) from the `data.gov.in` API or `econpulse.io`, splicing legacy base-years into a continuous 10-year monthly timeline.

### R2. Model Training
- Train a Generalized Additive Model (GAM) using Python (`pyGAM` or `statsmodels`).
- The model must include a polynomial trend, a harmonic basis for seasonality, and smooth splines for macroeconomic demand drivers.
- **MULTICOLLINEARITY CONSTRAINT:** The pipeline must test for multicollinearity (e.g., between GDP and Income). If and only if multicollinearity is detected, the script must automatically implement Gram-Schmidt orthogonalization to resolve it before passing variables to the GAM.

### R3. Validation & Reporting
- Cross-validate the GAM against a baseline linear model (ARIMA) using Root Mean Square Error (RMSE).
- Generate a final academic manuscript (in LaTeX/PDF format) detailing the data collection, methodology, and empirical results.

## Acceptance Criteria

### Data Adequacy
- [ ] A generated CSV file exists containing at least 3 years of monthly CNG price data.
- [ ] A generated CSV file exists containing at least 10 years of monthly macroeconomic data, properly interpolated.

### Model Execution
- [ ] A Python script runs successfully, ingests the data, and outputs partial-dependence plots for the GAM.
- [ ] The Python script outputs a quantitative RMSE comparison between the GAM and ARIMA.

### Manuscript
- [ ] A `.tex` file is generated containing the actual empirical results, model plots, and a conclusive finding on model superiority.
