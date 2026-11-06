# Stage 3 data recovery and collection — 6 November 2026

Stage 3 remains open. No Stage 4 work, EDA, feature selection, stationarity testing or model training has been performed. The finalized multi-city design, two monthly targets, 1/3/6-month horizons and separate H1/H2 evidence are preserved. City selection is provisional until historical coverage and GA boundaries are reviewed.

## Actual retained evidence

- Acquisition attempts in current manifest: 542. Status counts: {'downloaded': 473, 'failed': 69}.
- PNGRB CNG component snapshots: 10569. Reporting periods: 2025-03 to 2026-08. Arithmetic outcomes: {'pass_tolerance_0.05': 9346, 'missing_components': 1208, 'conflict': 15}.
- Native numerical observations: 9296, including original-frequency annual GDP, CPI source values, commodity benchmarks, GPR and separately labelled FX proxy bar closes.
- Corporate disclosure documents indexed: 4. Actual exchange dissemination timestamps remain largely unknown.
- IGL workbook source cells: 901 across 17 reported locations. Cell outcomes: {'positive_price_claim': 443, 'missing': 441, 'negative_delta_or_invalid_absolute_price': 17}. Revision-date claims are not automatically verified effective times.
- Same-date primary/secondary value comparisons: 34; matches: 33; conflicts: 1. These are single-observation checks, not proof of interval continuity.
- Inventory: 73 factors across all nine groups; see `metadata/factor_city_period_coverage.csv` for every factor and original city candidate. `metadata/alternative_ga_coverage.csv` preserves additional GA/operator/district candidates.
- Finalized monthly targets: zero pending defensible effective-price paths. Ten incomplete November 2026 targets remain quarantined.

## Next specific actions

Every factor has a status, missing-period description and next retrieval action in `metadata/data_inventory.csv`. Twenty-one manual source/export requests appear in `metadata/manual_collection_queue.csv`, covering institutional datasets, primary exports, licenses and ONOS supplements. Current attempted public links, exact failures and raw hashes are recorded in the acquisition manifest and append-only journal. A failed export or inaccessible document is not reported as collected data.

1. Resolve the IGL workbook's negative delta cells, missing geography cells and revision/effective-time distinction. Verify historical city prices against original notices and independent dated coverage.
2. Review PPAC notified domestic prices, nomination-block APM caps and difficult-field gas ceilings separately; OCR image-only notices and verify arithmetic/units. Do not restore assumed ceiling-as-price series.
3. Finish semantic table review of retained PNGRB/PPAC reports at their original national, state, GA or company grain. Native cells and PDF layout rows are evidence, not model-ready variables.
4. Obtain observed VAHAN/RTO exports, RBI reference rates, MoSPI CPI/GDP/PFCE vintages and city-relevant IMD data where public machine exports are unavailable. Keep missing observations missing.
5. Expand historical H2 article/report coverage and obtain original publication/dissemination timestamps, legal text access and event overlaps. No sentiment, POS/collocation, novelty or bias indicators have yet been computed.

## Review gate

Validation status counts: {'pass': 10, 'blocked': 5}. Passed repair checks and blocked collection checks are separate. `stage3_complete=false` and `model_ready_validated=false`. Accessible retained documents still requiring semantic extraction are explicitly partial; their limitations are not classified as irreducible access barriers. Completion requires review of coverage and remaining source limitations.
