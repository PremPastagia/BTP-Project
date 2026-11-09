STAGE 4 REDO — 9 NOVEMBER 2026

Read STAGE4_REDO_CHECKPOINT_REPORT.txt and DELIVERY_STATUS.txt first.
This is a new analysis version. The 6 November Stage 4 and the researcher-accepted
restricted Stage 3 snapshot remain preserved. The attached brief is retained as
EXECUTION_BRIEF.txt, with its workflow requirements mapped onto the original
nine-stage names in project_reconciliation/workflow_mapping.csv.

MAIN SAMPLE
Jan 2011–Oct 2026; intended ten cities. Accepted price paths currently support
Delhi, Noida and Lucknow: 424 month-end outcomes and 416 complete day-end monthly
means. Seven other intended cities remain unavailable under the accepted rules.
Agra and Unnao are auxiliary, with 128/125 outcomes separately preserved.
The 1,900-row primary calendar describes coverage slots, not a balanced set of
price observations. analysis_targets.csv contains only rows with a target.

TARGET INTERPRETATION
cng_price_twap is the calendar-day-weighted average of day-end quotes under the
approved bounded documentary path. Exact intraday TWAP is not identified. Timing
envelopes are conditional source-path sensitivity bounds, not statistical intervals.
Missing prices remain missing. Retrospective targets do not certify public
availability of lagged price predictors at past forecast origins.

EVIDENCE TIERS
Legacy unverified chart values, assumed release dates, authored news labels and
generated VAHAN remain excluded from the analysis. Dated national records from the
old integration supply only reserved origins. New PPAC source checks yield a
clearly separated retrospective-listing proxy tier for possible later sensitivity
analysis. No proxy is silently admitted as verified historical availability.

RESERVATION
November 2025–October 2026 was retained from the earlier Stage 4 reservation and
concealed from new numeric EDA. Date/configuration and checkpoint evidence shows
known related-study evaluation overlap in November–December 2025. The exact old
execution is not fully pinned to current inputs; 2026 evaluation exposure is unknown.
Never describe this whole window as an untouched final test. Stage 6 must define
and disclose a defensible evaluation strategy before fitting/scoring models.

REPRODUCING TARGETS AND DESCRIPTIVE TABLES
Use a fresh output directory; producers refuse to overwrite completed results.
From the repository root, with Python and the listed scientific dependencies:

python BTP_CNG_Data/stage4_2026-11-09/scripts/build_analysis.py --output /tmp/btp_stage4_redo
python BTP_CNG_Data/stage4_2026-11-09/scripts/profile_analysis.py --input /tmp/btp_stage4_redo --output /tmp/btp_stage4_redo
python BTP_CNG_Data/stage4_2026-11-09/scripts/horizon_coverage.py --input /tmp/btp_stage4_redo --output /tmp/btp_stage4_redo

The first producer uses only Python stdlib. The profile uses matplotlib/NumPy.
metadata/environment_versions.json and component receipts record executed versions.
The configured bundled Python lacked matplotlib, so the existing scientific Python
was used for figures; no dependency installation or clean-environment replay is
claimed. Audit tools additionally require Pandas, BeautifulSoup, pypdf and Poppler.

INDEPENDENT AUDIT AND ACCESS DEPENDENCIES
reconciliation_targets/reconcile_targets.py accepts --desktop-root. It independently
uses exact rational interval-prefix calculations and reproduces legacy arithmetic.
Saved immutable audit input copies and actual script versions are under its runs/.
predictor_reconciliation scripts expose explicit path arguments via --help.
project_reconciliation/reconcile_projects.py is a preserved historical local
inventory, with pinned paths and time-specific status readings. Its provenance
explicitly says not to replay it in place; it is not claimed to be a portable
collector. Its independent EDA script/receipts are separate.

The Desktop/[ME] BTP archive supplied original local evidence. Full raw sources are
the existing checksum-tracked consolidated collection, not copied into this output.
See ../consolidated_2026-11-06/ for authenticated draft-release archive delivery and
restoration instructions. PPAC raw object paths/hashes are in its source ledgers.
Legacy comparison requires the retained Git objects, notably 6b08b99, 2c2e3b9 and
4d4959c. Missing licensed/local sources remain explicit reproduction dependencies.
Do not rerun collection or execute the old modeling/ingestion scripts to recreate
verified inputs. Hash consistency does not establish factual or temporal validity.

HISTORY AND SCIENTIFIC GATE
metadata/experiment_registry.jsonl links the prospective audit specifications,
source journals, independent implementations, failed attempts and corrections.
The first new target run had incomplete predecessor lineage. Its exact code/data
and EDA are preserved in logs/versions/predecessor_lineage_v1; corrected outputs
have identical numeric targets/bounds. Reviewer schema failures are also retained.
No synthetic empirical data, model fitting, stationarity tests or forecasts were
created. Stage 4 is an outcome/source/EDA checkpoint; Stage 5 has not started.
