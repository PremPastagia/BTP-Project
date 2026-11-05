# Stage 3 recovery, expansion and verification — 5 November 2026

**Status: Stage 3 OPEN. No Stage 4 work performed.** This is a substantial collection/recovery checkpoint, not an assertion that every accessible historical source has been exhausted. No data is declared model-ready. See STAGE3_SCOPE.md for the binding design.

## Actual collection

| Item | Recorded result |
|---|---:|
| HTTP retrieval attempts, including failures and one transient retry | 828 |
| Nonempty retrieved source IDs | 778 |
| Distinct nonempty response hashes | 769 |
| PDF source documents / distinct PDF hashes | 717 / 709 |
| PDF pages encountered, including image-only pages | 21072 |
| PNGRB CNG district/GA snapshot rows | 10,564 |
| PNGRB monthly tables | 18 (March 2025–August 2026) |
| Explicit primary historical price rows | 175 (Delhi and four Green Gas GAs, including not-commenced tokens) |
| MNGL historical source rows | 181 |
| Bounded primary-history monthly label candidates | 350; all remain provisional |
| PPAC gas-price/ceiling/PAF notification documents | 89 |
| Price notifications with readable currency transcriptions | 83; all require role/OCR/period review |
| Text-extracted gas-production/LNG-import facts | 150; provisional source transcriptions |
| Corporate source documents | 188; company/report type and publication timing require review |
| Actual independent article metadata records | 14; deliberately separate from 125 website captures |
| Stage 2 + macro candidate inventory | 69 factors; 690 factor/city coverage intervals |

World Bank energy records retain the entire retrieved monthly workbook history (1960M01 to 2024M12); GPR preserves all 1522 original rows/columns. GDP is annual, CPI remains at source monthly grain, and Yahoo FX bars are identified as monthly closes rather than monthly means. These latest-vintage series are **not** proven historically available at each past forecast origin.

PNGRB archive links include CGD/MIS/progress and pipeline documents back to 2010; PPAC discovered relevant archive references back to 2013. Document archive date coverage is not the same as continuous observation coverage. All discovered and unmatched candidates remain in retrieval queues and registries.

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

## Remaining collection by priority

| Priority | Status / next specific action |
|---|---|
| P0 historical targets | Reconcile metadata/price_crosschecks.csv, visually verify MNGL dates/subcities, obtain dated IGL/MGL/other operator revisions, establish bounded complete price paths and validate candidate labels independently. Keep city selection provisional. |
| P1 core H1 | Review PPAC transcriptions and table headers/units, obtain verified monthly APM roles and release dates, RBI FX, MoSPI period/vintage records; finish unextracted gas and LNG tables. |
| P2 regional factors | Extract/verify GA-specific consumption/stations/pipeline rows, statutory tax regimes and allocation/sourcing costs; obtain actual VAHAN registrations/stock. Do not allocate national/company values to cities automatically. |
| P3 H2 | Expand independently published historical articles and missing company quarterlies/calls; resolve exact publication dates, company/city relevance, duplication and permitted text use. |
| P4 experimental | Obtain historical IMD/global demand series and dated disruptions; preserve the research questions on source disagreement and tone without assuming dishonesty. |

metadata/manual_collection_queue.csv contains 21 precise retrieval tasks, including provider, dataset, search terms, fields, geography, maximum history and export instructions. IIT Kharagpur lists Bloomberg at VGSOM and CMIE/IndiaStat resources; active entitlement and bulk licences remain unverified. Capitaline and Passport were not found on the inspected financial-resource page. ONOS publisher coverage is not an entitlement to primary price records.

metadata/unresolved_retrievals.csv lists every latest failed/empty request (44). HTTP 403 and authentication/CAPTCHA boundaries were not bypassed. Further accessible sources may still exist; these gaps are not yet certified irreducible.

## Files and evidence

- source_registry.csv: actual response links/hashes/access state; public access is not presumed an open licence.
- data_inventory.csv and factor_document_evidence.csv: every factor, actual structured records versus keyword-only document candidates, remaining actions.
- city_coverage_matrix.csv and factor_city_period_coverage.csv: constructed continuity versus primary history and unresolved city attribution, with source grain preserved.
- data_dictionary.csv: all active structured fields, unit/definition/provenance guidance.
- original_file_audit.csv, price_crosschecks.csv, pngrb_quality_flags.csv, validation_results.csv: inspectable checks and conflicts.
- source_native/document_table_rows.parquet: raw table-cell transcriptions, with source/page/line references; their headers and semantic column alignment remain unverified. The large equivalent CSV is regenerated locally on replay.
- Large immutable raw responses and extracted document text are stored in downloadable evidence bundles, **outside git**. metadata/evidence_bundles.csv supplies bundle links and checksums; metadata/evidence_file_manifest.csv maps every original path to its bundle and hash. restore_evidence.py restores the exact raw/ and documents/ paths. Original pre-recovery raw files remain in git and quarantine.

Do not interpret file volume, table continuity, hosting on an official domain or engineering checks as independent authenticity or forecast readiness. Stage 3 remains open pending review of collected coverage, unresolved extractions, independent target checks and source limitations.

## Downloadable raw evidence

Restore these archives using `scripts/restore_evidence.py`; all original paths and SHA-256 checksums are in the manifest.

| Bundle | Size (MiB) | Files |
|---|---:|---:|
| [BTP_Stage3_Evidence_01.zip](https://chatgpt.com/library?file_id=libfile_9039c173bbc48191a386df93c15bb5ad&account_id=personal) | 80.2 | 744 |
| [BTP_Stage3_Evidence_02.zip](https://chatgpt.com/library?file_id=libfile_ace00c1d89448191a8a652c253dfe536&account_id=personal) | 179.8 | 8 |
| [BTP_Stage3_Evidence_03.zip](https://chatgpt.com/library?file_id=libfile_efb07a4bab6c81918299ecc370b14e36&account_id=personal) | 168.9 | 61 |
| [BTP_Stage3_Evidence_04.zip](https://chatgpt.com/library?file_id=libfile_eb3670dda7288191b7134d1b02d72c1b&account_id=personal) | 170.1 | 40 |
| [BTP_Stage3_Evidence_05.zip](https://chatgpt.com/library?file_id=libfile_714d360042708191842a3d816744aa8e&account_id=personal) | 180.5 | 99 |
| [BTP_Stage3_Evidence_06.zip](https://chatgpt.com/library?file_id=libfile_55c53e66ff248191a7e0f698d53f96d5&account_id=personal) | 186.3 | 5 |
| [BTP_Stage3_Evidence_07.zip](https://chatgpt.com/library?file_id=libfile_77afae0a8a7481918206133ed892807a&account_id=personal) | 171.0 | 72 |
| [BTP_Stage3_Evidence_08.zip](https://chatgpt.com/library?file_id=libfile_bc9a9d2cab788191977d206884182740&account_id=personal) | 158.8 | 33 |
| [BTP_Stage3_Evidence_09.zip](https://chatgpt.com/library?file_id=libfile_75045fa0471081919a4f37cc255e21ce&account_id=personal) | 132.3 | 103 |
| [BTP_Stage3_Evidence_10.zip](https://chatgpt.com/library?file_id=libfile_196b9193e0a48191b7cd4358a77d7e04&account_id=personal) | 170.7 | 90 |
| [BTP_Stage3_Evidence_11.zip](https://chatgpt.com/library?file_id=libfile_5539acf351f88191a35ec8800db53f9a&account_id=personal) | 174.9 | 83 |
| [BTP_Stage3_Evidence_12.zip](https://chatgpt.com/library?file_id=libfile_7edc9fd1b4c081919b0991b1e3cce43e&account_id=personal) | 172.2 | 13 |
| [BTP_Stage3_Evidence_13.zip](https://chatgpt.com/library?file_id=libfile_6a4c2422f4048191ae17bda67f880caf&account_id=personal) | 131.4 | 10 |
| [BTP_Stage3_Evidence_14.zip](https://chatgpt.com/library?file_id=libfile_64bc8de3606481918d4b9fc47d5220b6&account_id=personal) | 178.3 | 14 |
| [BTP_Stage3_Evidence_15.zip](https://chatgpt.com/library?file_id=libfile_9e00a6488c8c819196bf247db2821b73&account_id=personal) | 163.7 | 143 |
