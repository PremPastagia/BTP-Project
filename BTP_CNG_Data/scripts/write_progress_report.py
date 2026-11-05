from pathlib import Path
import json,pandas as pd
from recover_repository import B

def run():
 v=json.loads((B/'logs/stage3_validation.json').read_text());a=pd.read_csv(B/'metadata/retrieval_attempts.csv');docs=pd.read_csv(B/'metadata/document_extraction_manifest.csv');corp=pd.read_csv(B/'structured/corporate_disclosures/corporate_disclosures_metadata.csv');n=pd.read_csv(B/'structured/news/actual_article_metadata.csv');p=pd.read_csv(B/'structured/price_revisions/primary_price_histories.csv');inventory=pd.read_csv(B/'metadata/data_inventory.csv');wb=pd.read_csv(B/'structured/numerical_factors/worldbank_energy_native_monthly.csv');gpr=pd.read_csv(B/'structured/numerical_factors/gpr_native_monthly.csv');price=pd.read_csv(B/'structured/numerical_factors/ppac_price_transcriptions.csv')
 latest=a.sort_values('extraction_timestamp').drop_duplicates('source_id',keep='last');fail=latest[latest.raw_path.isna() | latest.bytes.eq(0)]
 fail.to_csv(B/'metadata/unresolved_retrievals.csv',index=False)
 counts=dict(attempts=len(a),downloaded_source_ids=int(latest.raw_path.notna().sum()),nonempty_downloaded_source_ids=int((latest.raw_path.notna() & latest.bytes.gt(0)).sum()),unique_nonempty_raw_responses=int(latest.loc[latest.bytes.gt(0),'sha256'].nunique()),unresolved_latest_requests=len(fail),pdf_source_documents=len(docs),unique_pdf_hashes=docs.raw_sha256.nunique(),extracted_document_pages=int(docs.pages.sum()),corporate_documents=len(corp),independent_article_records=len(n),primary_price_rows=len(p),factor_candidates=len(inventory),stage3_complete=False,model_ready=False)
 (B/'metadata/progress_counts.json').write_text(json.dumps(counts,indent=2))
 text=f'''# Stage 3 recovery, expansion and verification — 5 November 2026

**Status: Stage 3 OPEN. No Stage 4 work performed.** This is a substantial collection/recovery checkpoint, not an assertion that every accessible historical source has been exhausted. No data is declared model-ready. See STAGE3_SCOPE.md for the binding design.

## Actual collection

| Item | Recorded result |
|---|---:|
| HTTP retrieval attempts, including failures and one transient retry | {len(a)} |
| Nonempty retrieved source IDs | {counts['nonempty_downloaded_source_ids']} |
| Distinct nonempty response hashes | {counts['unique_nonempty_raw_responses']} |
| PDF source documents / distinct PDF hashes | {len(docs)} / {counts['unique_pdf_hashes']} |
| PDF pages encountered, including image-only pages | {counts['extracted_document_pages']} |
| PNGRB CNG district/GA snapshot rows | 10,564 |
| PNGRB monthly tables | 18 (March 2025–August 2026) |
| Explicit primary historical price rows | {len(p)} (Delhi and four Green Gas GAs, including not-commenced tokens) |
| MNGL historical source rows | {len(pd.read_csv(B/'structured/price_revisions/mngl_historical_source_rows.csv'))} |
| Bounded primary-history monthly label candidates | 350; all remain provisional |
| PPAC gas-price/ceiling/PAF notification documents | {len(price)} |
| Price notifications with readable currency transcriptions | {int(price.parse_status.eq('transcribed_requires_review').sum())}; all require role/OCR/period review |
| Text-extracted gas-production/LNG-import facts | {len(pd.read_csv(B/'structured/numerical_factors/ppac_gas_supply_transcriptions.csv'))}; provisional source transcriptions |
| Corporate source documents | {len(corp)}; company/report type and publication timing require review |
| Actual independent article metadata records | {len(n)}; deliberately separate from 125 website captures |
| Stage 2 + macro candidate inventory | {len(inventory)} factors; 690 factor/city coverage intervals |

World Bank energy records retain the entire retrieved monthly workbook history ({wb.observation_period.min()} to {wb.observation_period.max()}); GPR preserves all {len(gpr)} original rows/columns. GDP is annual, CPI remains at source monthly grain, and Yahoo FX bars are identified as monthly closes rather than monthly means. These latest-vintage series are **not** proven historically available at each past forecast origin.

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

metadata/unresolved_retrievals.csv lists every latest failed/empty request ({len(fail)}). HTTP 403 and authentication/CAPTCHA boundaries were not bypassed. Further accessible sources may still exist; these gaps are not yet certified irreducible.

## Files and evidence

- source_registry.csv: actual response links/hashes/access state; public access is not presumed an open licence.
- data_inventory.csv and factor_document_evidence.csv: every factor, actual structured records versus keyword-only document candidates, remaining actions.
- city_coverage_matrix.csv and factor_city_period_coverage.csv: constructed continuity versus primary history and unresolved city attribution, with source grain preserved.
- data_dictionary.csv: all active structured fields, unit/definition/provenance guidance.
- original_file_audit.csv, price_crosschecks.csv, pngrb_quality_flags.csv, validation_results.csv: inspectable checks and conflicts.
- source_native/document_table_rows.parquet: raw table-cell transcriptions, with source/page/line references; their headers and semantic column alignment remain unverified. The large equivalent CSV is regenerated locally on replay.
- Large immutable raw responses and extracted document text are stored in downloadable evidence bundles, **outside git**. metadata/evidence_bundles.csv supplies bundle links and checksums; metadata/evidence_file_manifest.csv maps every original path to its bundle and hash. restore_evidence.py restores the exact raw/ and documents/ paths. Original pre-recovery raw files remain in git and quarantine.

Do not interpret file volume, table continuity, hosting on an official domain or engineering checks as independent authenticity or forecast readiness. Stage 3 remains open pending review of collected coverage, unresolved extractions, independent target checks and source limitations.
'''
 bundle_path=B/'metadata/evidence_bundles.csv'
 if bundle_path.exists():
  bundles=pd.read_csv(bundle_path)
  if 'download_url' in bundles:
   text+='\n## Downloadable raw evidence\n\nRestore with scripts/restore_evidence.py.\n\n| Bundle | Size (MiB) | Files |\n|---|---:|---:|\n'
   for row in bundles.itertuples():text+=f'| [{row.filename}]({row.download_url}) | {row.bytes/1048576:.1f} | {row.file_count} |\n'
 (B/'STAGE3_PROGRESS.md').write_text(text)
 (B/'metadata/data_quality_report.md').write_text('# Stage 3 data-quality report\n\n'+text[text.index('## Repairs completed'):text.index('## Remaining collection by priority')]+'\n## Acceptance\n\nStage 3 is not complete. See STAGE3_PROGRESS.md, validation_results.csv and manual_collection_queue.csv. No model-ready validation is claimed.\n')
 print(json.dumps(counts,indent=2))
if __name__=='__main__':run()
