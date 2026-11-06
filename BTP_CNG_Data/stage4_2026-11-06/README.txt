STAGE 4 — RESTRICTED, RESEARCHER-AUTHORIZED ANALYSIS

Start with STAGE4_CHECKPOINT_REPORT.txt. Stage 4 computation and independent
verification are complete. Researcher review is required before Stage 5.

Accepted inputs:
../accepted_stage3_2026-11-06_restricted_v1/
Snapshot manifest SHA256:
968d4ad2b34c444ab6e4c9da33eae5b0c9c14bde7c01d308084136874ce3cea3

The earlier consolidated_2026-11-06 candidate is preserved with its original
pre-acceptance flags. Current state is ../RESEARCH_STATUS.json. Acceptance applies
only to the explicit restricted scope, not the entire broad source collection.

OUTPUTS
targets/monthly_targets.csv: 645 calendar coverage rows, 566 month-end outcomes,
553 complete calendar-day averages and 551 conditional timing envelopes. Empty
outcomes are not zero prices or synthetic observations.
integration/: native-grain information states, source eligibility, exclusions,
schemas, transformations and independent release-date checks. Joined information
states are not additional independent national measurements.
eda/: exploratory tables and five PNG/SVG figure pairs. Reserved outcomes are
excluded from descriptive statistics and price plots.
independent_target_audit/: independent interval-overlap target calculations and
end-stage scientific review.
metadata/: experiment history, definitions, horizon coverage, limitations and
versioned output checksums.

QUALIFICATIONS
The monthly mean is the approved calendar-day-weighted mean of day-end quotes.
It is not an identified exact intraday integral. Sensitivity envelopes assume the
documented path and no unlisted intraday round-trip changes. They are not statistical
confidence or prediction intervals. Missing source coverage remains missing.

November 2025–October 2026 is provisionally reserved from EDA. Stage 6 must review
prior-study exposure and confirm a defensible final evaluation design.
No dated numerical factor covers the current exploratory origins. No H1/H2
forecasting performance, model superiority, causality or formal significance is claimed.

REPRODUCIBILITY
Python and package versions appear in EDA/integration provenance; source-extraction
requirements are retained in the earlier candidate. Poppler is needed for independent
PDF release verification. Raw objects are in the candidate's local store and authenticated
draft-release archives, with expected hashes and restore instructions there.

Use a separate checkout/output version for any consequential rerun. Preserve this
checkpoint and record the reason and output/code hashes in the append-only registry.
Do not rerun accept_stage3.py to replace an existing accepted snapshot.

From repository root, these deterministic commands reconstruct or verify the targets:
python BTP_CNG_Data/stage4_2026-11-06/scripts/build_targets.py
python BTP_CNG_Data/stage4_2026-11-06/independent_target_audit/verify_targets.py
python BTP_CNG_Data/stage4_2026-11-06/scripts/hand_check_targets.py
python BTP_CNG_Data/stage4_2026-11-06/scripts/horizon_coverage.py

The integration scripts expose --help for all pinned input/approval paths. EDA's
analyze.py uses paths relative to this collection and append-only run IDs. Original
source and statistical definitions, failures, documentation corrections and the minor
pre-fix visual-retention deviation are all retained in the experiment journals.

No Stage 5 stationarity tests, model fitting or forecasts have been run.
