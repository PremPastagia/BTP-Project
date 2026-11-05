# Stage 3 collection and recovery

Read `STAGE3_PROGRESS.md` first. The project remains in Stage 3. No preprocessing, EDA, features, stationarity tests or models are authorised. Engineering checks do not establish data readiness.

The separate branch preserves the original repository at `quarantine/original_fd4e65b/`, including scripts, logs, raw files and constructed tables. Active legacy scripts stop immediately rather than reproduce synthetic/filled values. Final monthly target values remain blank until verification. Explicitly provisional primary-history label candidates are stored separately.

## Reproduce collection and verification

Python 3.12 was used. Install `scripts/requirements-stage3.txt` and system Poppler (`pdftotext`, `pdftoppm`) plus Tesseract English for scan-only notifications. `metadata/python_environment.txt` records the exact observed environment.

1. Download the evidence bundles listed in `metadata/evidence_bundles.csv`, then restore them with `python scripts/restore_evidence.py /path/to/BTP_Stage3_Evidence_*.zip` from any working directory. Every member is checked against `metadata/evidence_file_manifest.csv`. Different existing bytes are never overwritten.
2. Run `python scripts/recover_repository.py` to rebuild source-native legacy records and disable unsafe old scripts. This resets active recovery outputs from preserved originals.
3. To collect fresh sources, run `python scripts/retrieve_sources.py metadata/retrieval_queue_NAME.csv` from `BTP_CNG_Data/` for the exact desired queue. Each run writes a new retrieval log and content-addressed raw response. Review HTTP/content/licensing failures. The retry queue is historical evidence of a single ordinary transient retry; do not repeatedly retry access-denied resources.
4. Run `python scripts/extract_verified_sources.py`, `python scripts/ocr_notifications.py` if scan-only notifications were added, `python scripts/reconstruct_primary_candidates.py`, and `python scripts/extract_document_tables.py`.
5. Run `python scripts/build_manual_queue.py`, `python scripts/build_stage3_metadata.py`, `python scripts/validate_stage3.py`, then `python scripts/write_progress_report.py`.

A new live run is a new vintage, not a byte-identical historical replay. Existing retrieval logs and raw hashes retain earlier responses. Restore the bundles for the exact captured run. `validate_stage3.py --require-ready` deliberately exits nonzero while Stage 3 is unresolved; its ordinary exit status reflects engineering checks only. Read the JSON's `stage3_ready` and per-check statuses.

## Storage and granularity

Large immutable responses and extracted document text are stored outside git in the downloadable evidence bundles; original paths are restored under `raw/` and `documents/`. Structured tables, source inventory, hashes, retrieval logs and reusable scripts are versioned in git. The 94 MB source-table CSV is generated locally; the equivalent Parquet is committed. Private newspaper full text is not republished in this public repository.

Global benchmarks, national statistics, company reports and district/GA snapshots retain their true grain. Keyword matches in document evidence are only retrieval candidates. Raw source-table cells need header, period, unit and semantic checks. They are not accepted forecasting variables. No original document was silently discarded; unmatched candidates and failures remain listed.

## Manual exports

Follow `metadata/manual_collection_queue.csv`. Save a JSON sidecar containing source_id, source_url, geographical_grain, units, frequency, licensing, observation_period_definition and publication_status. Unknown publication dates must remain unknown. A verified publication also requires publication_release_date and publication_evidence. Then run:

```bash
python scripts/import_manual_export.py /path/to/export.xlsx --metadata /path/to/source_metadata.json
```

The importer preserves original bytes and each source sheet, without monthly conversion or filling. It does not override licence restrictions or turn exports into verified data automatically.
