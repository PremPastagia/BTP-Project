STAGE 3 CONSOLIDATED REVIEW CANDIDATE — 6 NOVEMBER 2026

Status: Stage 3 NOT ACCEPTED. Stage 4 NOT STARTED.
This collection supersedes older active tables for review purposes. It is not a
model-ready dataset and does not establish complete historical price paths.

START HERE
STAGE3_CHECKPOINT_REPORT.txt: findings, validity failures and decisions required.
metadata/candidate_status.json: actual record counts and acceptance state.
metadata/acceptance_gates.csv: passing engineering checks and blocked science gates.
metadata/dataset_inventory.json: every active structured table.
metadata/raw_objects.csv: one content-addressed object per exact SHA256.
metadata/source_receipts.csv: distinct source versions, successes and unresolved hashes.
metadata/reviews/: module findings, conflicts, exclusions and independent checks.

STRUCTURE
raw/objects/: original downloads and explicitly preserved source-extraction text.
structured/price_revisions/: source claims and cost-component snapshots.
structured/numerical_factors/: native-frequency observations and separate candidates.
structured/news/: article metadata with raw/normalized date claims.
structured/corporate_disclosures/: exact-hash-deduplicated document metadata.
metadata/: definitions, inventory, aliases, limitations, gates and checksums.
scripts/: source-extraction and verification implementations used in the collection.
logs/: package verification results. No processed/model_ready output is claimed.

RAW EVIDENCE STORAGE
The 3.17GB raw-object collection is kept locally and in authenticated draft-release
assets. It is intentionally outside normal Git tracking. This avoids Git's file-size
limits and public redistribution of original articles/reports with unverified reuse
rights. Source facts, metadata, scripts and review reports are tracked in the branch.
metadata/evidence_archive_manifest.json identifies archive files and hashes.
Use authenticated GitHub CLI release download, then restore_raw.py; do not treat
missing draft assets or a successful HTTP HTML response as restored source data.

REPRODUCIBILITY
verify_candidate.py independently rehashes raw objects, checks table keys, price
component foreign keys and declared source lineage. It must fail when raw evidence
is absent or changed. Producer scripts are retained under scripts/modules/;
they document their source collection layouts and may require the original project
context. They are not claimed to be a single-command cold-start replay. Native
sources and locators permit independent extraction; exact end-to-end replay remains
an explicit limitation until tested in a fresh environment.

All originals remain in the Desktop ME BTP workspace. No synthetic observations,
interpolation, backward filling, sentiment features, EDA or models were generated.
Missing data remains missing. Source versions and source disagreements remain distinct.
