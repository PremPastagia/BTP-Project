RESEARCH OUTPUT ACCEPTANCE MECHANISM — 9 NOVEMBER 2026

BTP_BTP2_STAGES4_9_ACCEPTANCE_CHECKLIST.txt is the exact user-supplied checklist.
It is an additional verification contract, not acceptance of Stage 4 or permission
to start Stage 5. It does not override the retrieved original stage labels.

USE BEFORE ANY STAGE SIGN-OFF
1. Read the original protocol, this checklist, and the current accepted data scope.
2. Map each requirement through requirement_stage_mapping.csv. The imported Stage 5
   design items mainly belong to original Stage 6; original Stage 5 diagnostics stay.
3. Inspect actual files, independently recompute critical quantities and inspect
   figures/reports. Existing receipts are inherited evidence until their scope and
   input identities are matched to the new requirement.
4. Record actual outcomes in acceptance_register.csv through record_check.py.
   Use automated:, manual:, or mixed: in the method. PASS needs actual evidence,
   timestamp, run ID, nonempty artifact and hash. N/A WITH REASON needs a rationale
   and impact/scope statement. Expected criteria cannot be changed by this recorder.
5. Run check_acceptance.py --original-stage N --gate. Exit0 means recorded items
   satisfy the mechanical gate; exit2 means pending/failing/blocked requirements;
   exit1 means a malformed/stale register. This never proves scientific validity.
6. Conduct independent scientific review, complete the stage handover record and
   obtain the researcher checkpoint approval required by the original protocol.

The recorder preserves the previous register in history/ and appends check_history.jsonl.
Never delete failed entries/history or revise expected criteria merely to get PASS.
A criteria change needs a dated design amendment with its scientific implications.

INITIAL STATE
98 requirements are indexed: 41 numbered output requirements, 34 stage safeguards,
7 universal procedure steps, 9 final handover checks, 6 original-stage handovers,
and the retained original Stage 5 diagnostic gate. All 98 start as NOT RUN against
this newly imported contract. Existing Stage 4 artifacts/hashes and independent
receipts are indexed; this is not 98 claims that previous work never happened.
The initial validator executed successfully as a structural check and correctly
withheld Stage 4 checklist acceptance. No successful scientific results were seeded.

SOURCE CONFLICTS AND DEPENDENCIES
The supplied document says the earlier nine-stage agreement was not found by its
author. This project did retrieve it, so requirement_stage_mapping.csv preserves it.
The supplied 26 operator markets/2,124 calendar rows/1,901 month-end/1,726 TWAP values
describe a different fresh first pass. Their counts are inherited claims, NOT this
project's accepted three-city outcomes. Keep market_id/geography if later supplied.

entrypoint_availability.csv checks the stated paths in the current worktree and
Desktop/[ME] BTP/BTP. The Desktop fresh Stage 3 files exist, but its referenced
stage4/ report, GATES, manifest, processed/ and audits/ are absent at those exact
paths. No claim of global absence is made. Obtain those specific files/dependencies
before cross-checking that first pass. Do not run a missing script or claim its
expected PASS markers were observed. Do not rebuild or adopt its prices silently.

The existing Stage 4 redo remains verified with limitations for its own scope:
424/416 primary outcomes, Agra/Unnao auxiliary, no strict-filter development H1
coverage, qualified PPAC proxy tier, and known related-study Nov-Dec2025 exposure.
The new checklist does not certify broader modeling readiness or an untouched test.

FILES
acceptance_register.csv: one authoritative requirement/verdict register.
requirement_stage_mapping.csv: stable supplied IDs mapped to original stages.
acceptance_policy.json: allowed statuses, schema and pinned original checklist hash.
stage_tracker.json: current evidence-backed status; future stages NOT STARTED.
open_issues.csv: precise dependencies and consequences.
initial_register_validation.json: actual initial structural/gating receipt.
mechanism_verification.json: executed controls, separate from empirical research.
initialization_manifest.json: hashes of the original saved mechanism version. This
is historical after later register updates, not a claim that the live register is
unchanged. Later register changes are versioned by record_check.py.

COMMANDS FROM REPOSITORY ROOT
python research_workflow/acceptance_2026-11-09/check_acceptance.py --original-stage 4 --gate
python research_workflow/acceptance_2026-11-09/record_check.py --help

No stationarity analysis, model training or forecasting is authorized by installing
this check mechanism. Continue only within the accepted scope and stage gates.
