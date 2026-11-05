# BTP CNG research — Stage 3 recovery

This branch audits, preserves and expands the CNG data collection. **Stage 3 remains open.** No preprocessing, EDA, features, stationarity tests or model training has been performed.

Start with [the progress and verification report](BTP_CNG_Data/STAGE3_PROGRESS.md), [the binding research scope](BTP_CNG_Data/STAGE3_SCOPE.md), and [replay/export instructions](BTP_CNG_Data/README_STAGE3.md).

Source registries, factor/city/period coverage, quality flags, manual retrieval instructions and scripts are under `BTP_CNG_Data/`. Original dataset files and unsafe legacy scripts are preserved under `quarantine/original_fd4e65b/`. Large immutable source documents and extracted text are saved in 15 checksum-tracked evidence bundles, linked from the progress report, and can be restored to their original paths. Engineering checks passing does not mean forecasting data is validated.
