STAGE 3 SOURCE EVIDENCE RECOVERY — 6 NOVEMBER 2026

Scope
Recovered missing public source bytes referenced by the pinned GitHub main and
open PR #1 receipts. Existing local originals were reused by exact SHA-256 and
were not overwritten. New files are content-addressed under objects/.

Pinned inputs
main: 4d4959cc5659c34989a32cc1902622b28a47e429
PR #1: 5e57b0ed4867bca25461c1e3211f11796a1c76f4
Source receipt copies are in the existing Stage3_GitHub_Audit_2026-11-06 snapshots.

Measured cumulative result
- 1,382 normalized receipt records: 831 PR #1 and 551 main/supplemental receipts.
- 856 distinct expected source hashes; 796 exact original source hashes available.
- All 761 distinct expected PDF hashes are available locally and independently
  readable using Poppler pdfinfo. No PDF hashes remain missing.
- All remaining 60 expected source hashes are older HTML versions. Fresh captures
  of all 60 source URLs are retained separately. Their old hashes are not claimed
  recovered and fresh HTML is not treated as historical publication evidence.
- All 185 distinct corporate PDF hashes representing 188 PR metadata rows are
  available with exact checksums. This includes all 65 previously missing hashes.
- Original expected workbooks are available, including the older IGL April-2019
  chronology workbook, without substituting its newer chronology version.
- New content-addressed files: 1,188, approximately 2.07 GB, including regenerated
  text and fresh HTML captures. File count is not a count of distinct observations.
- Every new object's filename hash was recomputed; zero mismatches.

Evidence bundle recovery
The 15 Library bundles themselves were not downloaded: the tested public Library
link returned an HTML page, not a ZIP. Original source URLs were used instead.
The PR bundle manifest has 1,453 distinct expected member hashes. Of these, 1,214
are now available locally; 239 expected old member hashes remain unavailable.
The remaining differences are older HTML captures and original extraction-text
versions. Underlying source PDF and spreadsheet bytes have been recovered.

Text reconstruction
Used the original repository's documented recipe, pdftotext -layout, without
executing any repository collection pipeline. Poppler version: 26.06.0.
709 raw PDF hashes were processed for 738 expected text member paths.
533 member checksums, representing 482 distinct original text hashes, reproduced
exactly. 205 members have a distinct fresh native-text extraction version.
640 PDFs yielded native text; 69 yielded no native text and need OCR/manual review.
Native text is not misclassified as OCR. Different extraction versions never
silently replace original expected text. No new numerical variables were inferred.

Three PDF parser disagreements
Three MoPNG originals contain a malformed "startref" trailer instead of the
standard "startxref" token. PyPDF rejects them, but independent Poppler reads
their 7, 3 and 1 pages respectively. The raw bytes match the historical hashes.
No source bytes or PDFs were repaired in place. Their registry rows are flagged
conditional_poppler_only_malformed_trailer. Use the Poppler path only after
explicit page review, or exclude these documents from substantive extraction.
Do not label these as fabricated data or silently normalize the originals.

Publication timing and scientific limits
No publication dates were inferred from file names, financial years, document
dates, PDF metadata, HTTP Last-Modified or retrieval dates. Recovery establishes
source identity and file readability, not the historical availability or truth of
every statement. Corporate public-release timestamps still require separate work.
Semantic table extraction, OCR review, model-ready integration and forecasting
were not performed by this recovery task. This task does not close Stage 3.

Main outputs
metadata/cumulative_source_registry.csv
  Normalized source receipts, original status, canonical exact local path,
  expected hash, byte availability, changed-capture reference and timing status.
metadata/canonical_source_objects.csv
  One canonical path per available expected hash, aliases and original source URLs.
metadata/cumulative_recovery_summary.json
  Final measured counts across both GitHub collections.
metadata/cumulative_pdf_verification.csv
  Independent Poppler checks for all 761 expected PDF hashes.
metadata/corporate_evidence_reconciled.csv
  All 188 corporate metadata rows with exact local references and PDF checks.
metadata/cumulative_unavailable_sources.csv
  61 alias rows representing 60 unavailable historical HTML hashes, each with a
  fresh capture reference. These are source-version gaps, not missing PDFs.
metadata/text_bundle_reconciliation.csv
  Every expected original text member versus the regenerated extraction checksum.
metadata/pdf_parser_disagreements.csv
  The three original malformed-trailer PDF records.
metadata/recovered_object_integrity.csv
  All new object hashes and sizes, recomputed independently of request receipts.
metadata/bundle_access_probe.json
  Recorded external Library ZIP probe and its HTML response classification.

Reproduction
recover.py                     Missing corporate source downloads.
recover_official_reports.py    Other missing official PR PDF sources.
recover_other_sources.py       Remaining non-PDF PR sources.
recover_main.py                Main acquisition manifest and supplemental receipts.
finalize.py                    PR reconciliation and independent PDF checks.
recreate_text.py               Original pdftotext-layout recipe, expected hash checks.
finalize_cumulative.py         Final combined registry, hashes and PDF checks.

Download scripts cache exact recovered files and use bounded concurrency,
timeouts and byte limits. Reruns may still contact a URL when the historical hash
was not reproducible. Original receipts and append-only request logs are retained.
Raw public access does not establish redistribution permission. Nothing from this
task was committed, pushed, or published; new raw evidence remains local.
