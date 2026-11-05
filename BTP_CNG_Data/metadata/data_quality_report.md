# Stage 3 data-quality report

## Repairs completed

- Preserved all 46 original BTP_CNG_Data files in quarantine/original_fd4e65b with checksums; original source scripts, malformed metadata and the misleading validation log remain auditable.
- Retained all 2,293 sampled CNG observations, distinguishing 2,018 repeats, 265 candidate changes and 10 initial observations. Candidate changes are not verified effective revisions.
- Removed 10 incomplete November 2026 rows from the active monthly target table. The remaining 1,511 rows have null final targets because their source price paths were not established. Original calculated numbers remain in quarantine.
- Quarantined synthetic VAHAN estimates, assumed APM/tax histories, backward-filled fuels, annual GDP expanded into monthly rows, undocumented extensions, lags and price-ratio features. Legacy scripts now stop before writing.
- Re-extracted source-native numerical files without fills, interpolation, date-grid extensions, lags or features. No annual-to-monthly conversion remains in the recovered GDP table.
- Downloaded official PPAC notifications and preserved calculated domestic price, nomination-block ceiling, difficult-field ceiling and PAF as distinct document categories. Transcriptions are not silently promoted to verified APM observations.
- Repaired corporate ingestion using the real IGL November 2024 allocation disclosure and downloaded MNGL, ATGL and Gujarat Gas documents. The IGL document date is not claimed as an exchange publication timestamp.
- Classified Wayback homepage records as captures, not articles. Actual article metadata uses publisher dates where available; no sentiment/collocation/bias features were generated.
- Rebuilt parseable source registry, dictionary, inventory, coverage and validation files from actual file contents.

## Verification findings

All engineering checks pass in logs/stage3_validation.json. The following are pending data issues, not passing authenticity checks:

- **124** PNGRB snapshot rows have revision dates after their stated month.
- **15** snapshot rows disagree with basic price plus taxes by more than INR 0.05/kg; **1,208** lack enough numeric components for that arithmetic check. The union of date/arithmetic flags is **136** rows. No conflicting figure was silently replaced.
- Primary/secondary exact-date reconciliation: **14 agree**, **6 conflict**, **155 have no matching secondary date**. Absence of a secondary record is not a failed primary record, and an agreeing secondary record is not proof of an exhaustive revision history.
- Primary-history monthly candidates use day weights, stop before the last listed revision month and retain retrospective publication and intraday timing limitations. They do not replace the unresolved final panel.
- Many actual publication dates, statistical vintages, company/GA boundary changes, subcity prices and source licences remain unresolved. MNGL's midnight labels and pre-2017 PMC/PCMC price differences need human review.
- Six PPAC notifications lack readable currency values after native extraction/OCR; other OCR values still require visual confirmation. Some PDFs are scans without searchable text.
- HTTP success is only retrieval success. Empty responses, JavaScript shells, 403/503 errors and unknown licensing are recorded explicitly.


## Acceptance

Stage 3 is not complete. See STAGE3_PROGRESS.md, validation_results.csv and manual_collection_queue.csv. No model-ready validation is claimed.
