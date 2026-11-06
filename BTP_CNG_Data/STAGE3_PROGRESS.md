# Stage 3 recovery — in progress

Stage 3 remains open. Stage 4 is not authorized. The research design remains multi-city, maximum reliable history, native-frequency retention, two future monthly targets (month end and time-weighted average), horizons 1/3/6 months, and separate H1/H2 evidence. No preprocessing, EDA, feature selection, stationarity tests or training is performed here.

The previous transient workspace reset before its repairs and acquisitions were persisted. Counts reported in that run are historical execution observations, not evidence that those files remain available. This run re-creates the repairs from immutable baseline `fd4e65ba762cb0acdc273ac9ad9e9f809e52e5b4`, then re-acquires sources and journals every completed attempt.

`scripts/stage3_recovery.py` supports `audit`, `collect`, `extract`, `catalogue`, `verify`, and `all`. Collection resumes without retrying failed endpoints unless `--retry-failed` is explicitly supplied. Individual downloaded files are content-addressed, and the acquisition journal is append-only. The audit copies originals into `quarantine/legacy_main/`; it must be run before collection, not after reviewed source tables have been added.

The validation report explicitly distinguishes passed repair checks from blocked source-quality/completion checks. Unknown public release timestamps stay missing. Empty finalized targets are deliberate until dated primary price paths establish continuity. No model-ready dataset is validated.
