# BTP: Forecasting Retail CNG Prices Across Indian Cities

## Dataset & Extraction Pipeline (`BTP_CNG_Data`)

This repository contains the dataset, extraction pipeline, and validation framework for the research project: **"Forecasting Retail CNG Prices Across Indian Cities Using Statistical and Machine Learning Models"**.

### Repository Structure
```text
BTP_CNG_Data/
├── raw/                         # Raw primary downloads and responses
│   ├── cng_prices/              # Raw discrete revision HTML responses per city
│   ├── energy_markets/          # World Bank Pink Sheet historical benchmarks
│   └── macro_weather/           # Caldara-Iacoviello GPR, IMF CPI, World Bank GDP
├── structured/                  # Normalized Parquet and CSV files
│   ├── price_revisions/         # Discrete revisions & monthly city panels (2011–2026)
│   ├── numerical_factors/       # Aligned external shocks & demand/fuel parity panels
│   ├── policy_events/           # Discrete policy shifts & APM price ceilings ($6.50/MMBTU)
│   ├── news/                    # Structured Wayback Machine archive metadata
│   └── corporate_disclosures/   # Statutory BSE corporate announcements
├── documents/                   # Primary source corporate filings (PDF)
├── metadata/                    # Data dictionary, source registry, coverage matrix
├── scripts/                     # Standalone Python extraction & validation modules
└── logs/                        # Timestamped execution run logs
```

### Extraction & Validation Pipeline
1. `01_extract_cng_panel.py`: Extracts discrete price revision points across 10 major Indian cities, applies calendar zero-order hold, and computes monthly Month-End & TWAP prices.
2. `02_extract_external_shocks.py`: Downloads World Bank commodity benchmarks (Brent, WTI, Dubai, Henry Hub, TTF, Japan LNG), Caldara-Iacoviello GPR index, USD/INR exchange rates, IMF CPI, and World Bank GDP.
3. `03_extract_domestic_factors.py`: Compiles PPAC APM pricing timeline, state VAT histories, petrol/diesel substitute retail prices, and VAHAN demand growth metrics.
4. `04_ingest_disclosures_and_news.py`: Ingests BSE regulatory filings and Wayback Machine historical snapshots with SHA-256 deduplication.
5. `05_validate_integrity.py`: Validates zero synthetic numbers, complete date continuity across target cities, and anti-lookahead lag alignment.
