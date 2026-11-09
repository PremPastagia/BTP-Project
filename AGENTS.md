# Research acceptance workflow

For work on this CNG study, read `BTP_CNG_Data/RESEARCH_STATUS.json` first.
Use the user-supplied checklist saved at
`research_workflow/acceptance_2026-11-09/BTP_BTP2_STAGES4_9_ACCEPTANCE_CHECKLIST.txt`
as an additional output verification contract. Read its adjacent `README.txt`,
acceptance register, stage mapping and open issues before stage sign-off.

- Preserve the retrieved original nine-stage labels. Map imported requirement IDs
  through `requirement_stage_mapping.csv`; do not rename original Stage 5 diagnostics.
- Preserve accepted snapshots, previous outputs and failed runs. Do not restart
  successful analysis or adopt reported source counts without a specific evidence gap.
- Record actual requirement checks in the one acceptance register. Use
  `record_check.py` to preserve prior versions and the check history. Do not seed PASS,
  erase failure history, or change expected results merely to get a successful gate.
- Before sign-off, run `check_acceptance.py --original-stage N --gate`, inspect its
  receipt, and conduct the required independent scientific review. A structural gate,
  file hash, nonempty table or PASS marker does not prove scientific validity.
- Keep unknown source dates, missing observations, geographic differences and prior
  evaluation exposure explicit. Never create synthetic empirical observations.
- The saved original protocol requires researcher approval at stage boundaries.
  Record actual approval when received; saving a checklist does not grant approval.
- Treat unavailable fresh first-pass files as specific transfer dependencies. Do not
  claim to have inspected inaccessible reports, executed missing scripts or accepted
  the reported expanded market scope.

Follow the user's latest explicit instructions when they amend the research scope
or these workflow rules, and document consequential changes with their reasons.
