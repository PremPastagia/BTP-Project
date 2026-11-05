# HANDOFF — Natural Gas GAM Paper

Full context for resuming this project in a fresh session. Root: `/Users/virajvekariya/Desktop/Natural Gas GAM Paper/`

Last updated: 2026-09-17

---

## 1. What this project is

**Title (fixed by the mentor, do not change):** *Modeling and Forecasting for Natural Gas Prices in India using Generalized Additive Models.*

**Current research scope (as of the latest pivot — see §3):** the paper predicts **CNG (Compressed Natural Gas) retail price** directly, using a Generalized Additive Model with a polynomial trend term, a harmonic (Fourier) seasonal basis, and smooth spline terms per demand driver. The earlier idea of separately modeling the Administered Pricing Mechanism (APM) domestic gas price and comparing it to CNG has been **dropped as a second modeled target** — APM price is retained only as one predictor (CNG's upstream cost input), not as its own forecasted series.

**Deliverables required:** a 2-page brief, a slide deck (currently 6 slides, PPTX), and a 5–7 minute presentation video. The originally-mentioned "1:30 PM next-day" deadline was explicitly waived by the user — full rigor over speed, no shortcuts.

## 2. Methodology, as currently specified

`Price(t) = polynomial trend + harmonic seasonality (sin/cos pairs) + Σ smooth(driver_i)`

- **Trend:** polynomial in time, not a spline — captures the slow structural climb, order to be selected via information criteria.
- **Seasonality:** harmonic/Fourier basis (k=1,2,3 sin/cos pairs at period 12), not exponential smoothing — chosen to capture both regulatory-style step changes and smoother seasonal consumption cycles.
- **Drivers:** each gets its own smooth spline term (GAM proper), not a linear coefficient — this is the whole point of choosing GAM over linear regression/ARIMA.
- **Multicollinearity:** if VIF/correlation flags a group of correlated predictors (GDP and disposable income are the prime suspects), those are transformed into **orthogonal polynomials via the Gram-Schmidt process** before/within the fit, so each effect stays separately interpretable. This has **not been executed yet** — it's Phase 5, not started.
- **Tooling:** Python (pyGAM / statsmodels), decided over R/mgcv per user's explicit choice.
- **Geographic scope:** all-India, national-level series (not city-specific), per user's explicit choice — *except* the CNG price target itself, which will necessarily be a multi-city panel (see §4).

## 3. Decision timeline (chronological — later decisions override earlier ones)

1. Target: model **both** APM and CNG, compared side by side (early decision).
2. Software: Python. Geographic scope: national. (locked, unchanged)
3. Phase 4 data health checkup found CNG retail price has **no real published time series** — only 9 scattered, secondary-sourced points. Recommendation at the time: drop CNG as a direct target, use landed international gas price as the "Non-Administered" comparator instead, keep CNG as a qualitative case study. **This recommendation was presented but not acted on.**
4. User asked for a "story" slide deck explaining the plan to the mentor; explicitly chose to **keep the original APM-vs-CNG framing** in that deck and not raise the CNG data problem yet.
5. **Latest pivot (supersedes #1 and #4):** user decided to drop APM as a second modeled target entirely and **predict CNG price directly**. APM price is kept only as a predictor. The slide deck was rewritten accordingly (see §6). **This does not resolve the Phase 4 finding — it makes it the central blocker**, since CNG is now the *only* target and still has only 9 real data points. See §7 for the resolution plan (not yet executed).

## 4. Phase 1 — Literature (done)

50 verified real sources across 4 tracks in `literature/`. Every source was cross-checked against a live URL/DOI at collection time; unverifiable candidates were dropped rather than guessed.

- `track_A_gam_energy_forecasting.md` — 12 sources, GAMs applied to energy/commodity forecasting.
- `track_B_gas_demand_modeling.md` — 12 sources, natural gas/CNG demand modeling (India + international). **Now the paper's primary literature pillar.** Key finding: the CNG-to-diesel/petrol price differential is the single strongest documented demand driver across the literature.
- `track_C_pricing_mechanisms.md` — 11 sources, APM vs Non-Administered pricing history in India (Rangarajan formula → April 2023 Kirit Parikh formula). Now background/motivating context only, not a modeling pillar. Contains a verified regime-change timeline (Jul 1975 APM introduced, Apr 2002 dismantled, Jun 2010/Nov 2014/Apr 2023 formula revisions, Jan 2027 targeted full deregulation).
- `track_D_gram_schmidt.md` — 15 sources, Gram-Schmidt/orthogonal-polynomial methodology and justification vs. ridge/PCA. Directly relevant to the not-yet-started Phase 5.

## 5. Phase 2/3 — Data collection (done, mixed quality)

All in `data/raw/` (24 CSV files) with sourcing manifests (`manifest_*.md`). Summary by quality:

**Strong (real, primary-sourced, long series):**
- Brent crude, Henry Hub, Asia-LNG (IMF proxy for JKM) — 356–472 monthly obs, 1987/1992/1997–2026.
- Petrol & diesel retail price, Delhi/Mumbai/Chennai/Kolkata — 3,381 **daily** obs, 2017–2026, from PPAC's own price-revision PDFs (also monthly-averaged versions).
- INR/USD exchange rate — 645 monthly obs, 1973–2026 (FRED series, since RBI stopped publishing its own reference rate after mid-2018).
- APM administered gas price — 60 real notifications, half-yearly through Mar 2023 then genuinely monthly from Apr 2023 onward (10%-of-crude-basket formula era). **Now a predictor, not the target.**
- National gas production/consumption — 40 monthly obs, Apr 2023–Jul 2026.

**Weak / needs work:**
- **CNG retail price** — only 9 scattered, secondary-sourced (news synthesis) points, 2017–2026. No primary PPAC/PNGRB series exists. **This is the target variable now — see §7, this is the blocker.**
- Vehicle registrations by fuel type — only annual snapshots (FY2022–24 + a few press data points), not monthly; Vahan's dashboard is a stateful JS app that resisted scraping.
- LPG retail price — real but secondary-sourced (bankbazaar.com compilation, spot-verified against 5 primary points); data.gov.in/sansad.in blocked direct access.
- GDP, PFCE (disposable income proxy), CPI, IIP — only 13–21 observations each, because the collecting agent pulled only current-vintage press notes, not the full legacy-base back-history that actually exists (RBI Handbook of Statistics, MoSPI NAS, legacy CPI 2012=100, legacy IIP 2011-12=100 all go back 10–15+ years). **Fixable, not yet fixed** — see §7.

## 6. Phase 4 — Data health checkup (done, verified via ledger)

Full statistical diagnostic pass in `diagnostics/`, run under a machine-checked completion ledger at `GATES.md` (unlazy skill) — **all 7 gates met with real, re-executable evidence** (re-run `node scripts/verify_*.mjs` from the project root to reproduce any of them; they re-execute `scripts/data_health_checkup.py` fresh each time, they don't just check stale files).

Tests run per series (where data length allowed): ADF + KPSS stationarity, linear trend significance, STL decomposition + harmonic-regression seasonality F-test (only for series with ≥24 monthly obs), Breusch-Pagan + ARCH-LM heteroskedasticity, and a Chow test + Welch's t-test structural-break check specifically on the APM price series around the April 2023 formula change.

**Headline finding:** APM price is non-stationary in levels (ADF p=0.46, KPSS p=0.03) and shows a highly significant structural break at April 2023 (Chow F(2,56)=24.5, p<0.0001; mean jumped $3.61→$7.96/MMBtu). This was the empirical justification for polynomial-trend-plus-explicit-break-handling over a plain smoothing constant — **still relevant even with APM demoted to a predictor**, since that same break may transmit into CNG price via cost pass-through and is worth testing for in the CNG series too, once real CNG data exists.

**G6 (manual judgment), `diagnostics/data_adequacy_summary.md`:** written analysis of the CNG (9-point) and macro-series (13–21 obs) problems, with recommended fixes. Partially overtaken by the pivot in §3.5 — the CNG resolution recommended there (drop CNG as target) is no longer the chosen path; the macro-series recommendation (re-collect full legacy-base back-history) still stands and is unexecuted.

**Environment note:** the system's Anaconda Python has an incompatible numpy 2.3.5 / pandas 2.2.2 pairing that **segfaults** on date parsing. A project-local venv was created at `.venv/` (numpy 2.5.3, pandas 3.0.5, scipy 1.18.1, statsmodels 0.15.0 — all mutually compatible, prebuilt wheels) specifically to work around this. **Use `.venv/bin/python`, not system `python3`, for anything in `scripts/`.**

## 7. Outstanding work (not started / not executed)

In priority order:

1. **Build a real CNG price panel.** This is the actual blocker for the whole paper now that CNG is the sole target. Plan (stated to the user, not yet executed): pull primary price-revision notifications directly from city-gas distributors — IGL (Delhi/NCR), MGL (Mumbai), Adani Total Gas, Gujarat Gas, and others — rather than relying on news synthesis. Pooling several cities' revision histories turns 9 isolated points into a real panel long enough to fit a GAM to (likely needs a city fixed-effect or factor-smooth term, since it becomes a panel rather than a single series).
2. **Re-collect full legacy-base back-history** for GDP, PFCE, CPI, IIP (RBI Handbook of Statistics, MoSPI National Accounts Statistics, legacy CPI 2012=100, legacy IIP 2011-12=100), then splice across the base-year rebasing points. Current 13–21-observation windows are unusable for the harmonic-seasonality GAM.
3. **Re-run the Phase 4 data health checkup** (`scripts/data_health_checkup.py`) on the new/extended CNG and macro series once collected.
4. **Phase 5 — multicollinearity screen + Gram-Schmidt orthogonalization.** Not started. VIF/correlation across the final driver set, then orthogonalize any confirmed collinear group (GDP/disposable income most likely).
5. **Phase 6/7 — fit the GAM, backtest.** Train/test split in time, report real forecast error, partial-dependence plots per driver.
6. **Final deliverables** — 2-page brief, finished slide deck, presentation video, physical report.

## 8. Deliverables produced so far

### Story/plan deck (for explaining the project to the mentor — not the final results deck)
`deliverables/story_deck/Natural_Gas_GAM_Story.pptx` — 6 slides, built with pptxgenjs (`build_deck.js`), QA-validated (structure + content + visual render checked slide-by-slide, all clean). Design system: **"Latent Isobar"** philosophy (`deliverables/visual_system/design_philosophy.md`), strict 3-color palette (navy `0F2E3D`, ivory `F4F1E9`, amber `C97A3D` — everything else is a tint/shade of these three), recurring harmonic-wave + instrument-calibration-tick motifs (`deliverables/story_deck/assets/`, regenerated via `make_assets.py` / `make_assets2.py`).

Current slide order: (1) Title, (2) Topic — "what we're actually predicting," visually contrasts de-emphasized APM context vs. emphasized CNG target, (3) Why CNG / why a non-linear model, (4) Factors (MECE driver map), (5) How we'll find the data (states the real primary-distributor-notification plan honestly), (6) What's next (roadmap).

**Note:** this deck's story is already aligned with the CNG-only pivot (§3.5) — it does NOT need another rewrite unless the plan changes again.

### Verification ledger
`GATES.md` — all 7 Phase-4 gates met. Checker scripts in `scripts/verify_*.mjs` + `scripts/_run_phase.mjs` (shared runner, spawns `.venv/bin/python`).

## 9. Full file map

```
Natural Gas GAM Paper/
├── HANDOFF.md                          ← this file
├── GATES.md                            ← Phase 4 verification ledger (7/7 met)
├── .venv/                              ← isolated Python env (numpy/pandas ABI fix)
├── literature/
│   ├── track_A_gam_energy_forecasting.md
│   ├── track_B_gas_demand_modeling.md
│   ├── track_C_pricing_mechanisms.md
│   └── track_D_gram_schmidt.md
├── data/raw/                           ← 24 CSVs + 4 manifest_*.md (see §5)
├── diagnostics/                        ← Phase 4 outputs (catalog, stationarity,
│                                          trend_seasonality, heteroskedasticity,
│                                          structural_break_apm, data_adequacy_summary,
│                                          phase4_consolidated_report) — .json + .md pairs
├── scripts/
│   ├── data_health_checkup.py          ← main Phase 4 diagnostic engine (phased CLI)
│   ├── _run_phase.mjs                  ← shared Node helper, spawns venv python
│   └── verify_*.mjs                    ← 6 gate-checker scripts
└── deliverables/
    ├── visual_system/design_philosophy.md   ← "Latent Isobar" design philosophy
    └── story_deck/
        ├── build_deck.js                    ← pptxgenjs generator (current version)
        ├── make_assets.py / make_assets2.py ← motif image generators
        ├── assets/                          ← wave + tick PNGs
        ├── Natural_Gas_GAM_Story.pptx        ← current deck (6 slides)
        ├── Natural_Gas_GAM_Story.pdf         ← rendered copy (for QA)
        └── slide-1.jpg … slide-6.jpg         ← QA renders
```

## 10. Things a fresh session should NOT redo

- Don't re-launch literature research — 50 sources across 4 tracks are done and verified.
- Don't re-collect Brent/Henry Hub/Asia-LNG/petrol/diesel/INR-USD/APM-price/gas-production data — already real, primary-sourced, long enough.
- Don't re-run Phase 4 diagnostics on unchanged series — only re-run on the CNG panel and macro series once those are actually extended (§7 items 1–2).
- Don't reintroduce APM as a second modeled target — that was explicitly reversed (§3.5).
- Don't rebuild the story deck from scratch — it already reflects the current plan; only touch it if the plan changes again.
