STAGE 3 NUMERICAL RECONCILIATION — 6 NOVEMBER 2026

This is a source-native evidence ledger, not an accepted analytical panel.
Stage 3 remains open. Stage 4 has not started in this folder.
Original files are preserved; source_registry.csv references their existing paths
and SHA-256 hashes rather than copying duplicate source bytes.

WHAT WAS DONE
1. Reconciled fresh numerical/supplemental CSVs with the GitHub PR #1 native
   tables. Unsafe legacy demand/macro joins, lag columns and synthetic VAHAN
   series were not imported.
2. Rechecked every referenced original source hash. Rows lacking exact raw-byte
   lineage are excluded and logged; fresh copies are not substituted for a
   different source vintage merely because a URL or document title matches.
3. Preserved native daily, monthly, quarterly, annual, snapshot and notified-
   interval grain. Different units, index bases, source vintages, national/state
   geography and company/CGD definitions remain separate.
4. Suppressed identical source-version/variable/geography/period/unit records
   while preserving every extraction origin in input_origins and duplicate_aliases.
   Source-vintage overlaps are retained; row totals are not unique economic facts.
   Numeric claim equality uses exact Decimal values, without rounding or
   precision tolerances. Representation-only differences such as1versus1.0
   compare equal; every differing reported digit remains a distinct claim.
5. Separated unverified gas-price and text-regex gas-supply transcriptions from
   ordinary native numerical observations. A ceiling is not substituted for a
   realized company procurement price. OCR values remain candidates.
6. Recovered official MoSPI CPI responses directly from the public API using
   TLS legacy-server-connect compatibility with certificate validation retained.
   Full original responses and failure/empty-response receipts are saved.

NEW CPI EVIDENCE AND SOURCE CONFLICT
The official All India / Combined / General / General-Overall CPI API returned
185 rows across 2011–2025 under its reported base 2012. The January–May 2013
response contains two different final values for each month, with identical
reported dimensions. All ten conflicting rows are preserved in conflicts.csv
and excluded from the canonical ledger. The remaining 175 months are retained.
No arbitrary first-row/final-row preference or interpolation was used.
Queries for 2026 base 2012 and 2025/2026 base 2024 returned no data. This is
documented as unavailable through these queries, not proof that the underlying
statistics do not exist elsewhere.
The API supplies current final/provisional status, not original publication or
revision dates. These observations are not certified real-time historical inputs.
The earlier IMF/DBnomics monthly CPI series is retained separately: 823 observed
values, January 1957–July 2025, with its source reference-period metadata.

REPAIRED FX SOURCE-PERIOD DECODING
The Yahoo JSON declares Europe/London as exchangeTimezoneName. Monthly bar
timestamps during British summer time occur on the previous UTC calendar day.
Using the old UTC date label incorrectly assigned April bars to March, etc.
The ledger decodes the native month from the original Unix timestamp using the
source-declared timezone. The original UTC-derived label remains in the notes.
There are 179 complete source bars; two November/current partial-bar records
are excluded. No monthly averages were constructed. Yahoo monthly closes and
Federal Reserve daily noon buying rates remain different series.

OTHER SOURCE CONFLICTS
The PPAC infrastructure workbook itself has repeated identical geography labels
with different counts, e.g. two Haryana rows (453 and 25 stations) on the same
snapshot date. The 34 affected numerical records remain in conflicts.csv.
They were not silently summed, reallocated, renamed or chosen by magnitude.

OUTPUTS
structured/native_numerical_observations.csv
  Native numerical source claims with raw hash, location, units, original period,
  timing flags, input-table hash/row lineage and explicit source-version keys.
  The word native does not imply source accuracy or researcher acceptance.
structured/unverified_transcription_candidates.csv
  PPAC clause/OCR/text candidates requiring role, unit, period and source review.
metadata/source_registry.csv
  Existing raw paths and independently rechecked hashes; multiple URL aliases
  can point to one original raw object.
metadata/source_tables.csv
  Input-table paths, hashes, row counts and evidence roles.
metadata/data_dictionary.csv
  Canonical field definitions and missing-value meaning.
metadata/coverage.csv
  Field-, geography-, unit- and vintage-specific first/last labels and missing
  publication counts. First/last labels do not establish continuous coverage.
metadata/duplicate_aliases.csv
  Source-version duplicates suppressed and their extraction origins.
metadata/conflicts.csv
  All contradictory same-key claims; neither side silently selected.
metadata/missing_raw_lineage.csv
  Records excluded because original bytes were absent or mismatched.
metadata/excluded_records.csv
  Nonfinite/invalid values or incomplete source bars excluded with reasons.
metadata/remaining_gaps.csv
  Specific missingness, source constraints and next retrieval/verification action.
logs/build_summary.json
  Actual latest counts and explicit not-complete/not-accepted status.
logs/independent_validation.json
  Independent source-decoding checks; does not import the builder.
logs/mospi_cpi_acquisition_manifest.json
  All bounded official CPI query receipts, including empty responses.

REPRODUCE
python3 scripts/collect_mospi_cpi.py
python3 scripts/build_numerical.py
python3 scripts/verify_numerical.py
Collection may retrieve a new API vintage; preserve this directory before a new
collection run. The builder and verifier work offline against saved sources.
Validation requires standard Python plus openpyxl. No models are trained.
The scripts infer the ME BTP project root from this folder's location; set
BTP_PROJECT_ROOT explicitly if using a different enclosing directory. Paths in
the source registry and input origins are relative to that root. Reproduction
requires retaining the referenced original project files and pinned snapshots.

INDEPENDENT CHECKS
The verifier rehashes raw files, independently decodes all 823 IMF CPI and 66
constant-dollar GDP values from original JSON, independently confirms official
CPI dimensions/values and conflicting periods, checks every one of the 6,940
fresh energy values against original Excel cells, independently decodes FX
bar months from source timezone metadata, and tests uniqueness, finite values,
candidate separation and conflict exclusions. This is not independent proof of
every source assertion or of real-time availability at every forecast origin.

REMAINING CRITICAL LIMITS
- Historical publication/revision vintages remain unknown for most series.
- Official CPI 2026/new-base retrieval and the conflicting 2013 values remain.
- Broad historical city CNG consumption, registrations, procurement costs and
  allocation/sourcing shares are not established by this ledger.
- Gas-price OCR candidates still need visual/role/period review; date and price
  clauses cannot be interpreted as company-level invoiced procurement costs.
- National PPAC provisional/estimated gas quantities are preserved as such.
- CGD sectoral gas includes PNG and CNG and is not CNG-only vehicle demand.
- Weather aggregates are national/regional, not local station/extreme-event data.
- Annual WDI consumption is not silently treated as quarterly PFCE; GDP bases
  and current/constant price series remain separate. No annual-to-monthly fill.
- World Bank Japan LNG is an import benchmark, not JKM; European natural gas
  is not automatically a TTF spot series. No licensed LNG spot history claimed.

The researcher must review remaining source gaps and the cumulative Stage 3
completion report before accepting any snapshot or starting Stage 4.
