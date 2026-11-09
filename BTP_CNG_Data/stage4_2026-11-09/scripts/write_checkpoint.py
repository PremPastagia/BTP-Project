"""Assemble the redo checkpoint from executed outputs and independent receipts.

No new statistical calculation beyond labelled counts; original outputs preserved.
"""
from pathlib import Path
import csv,datetime,hashlib,json
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1]
def load(p):return json.loads((HERE/p).read_text())
def rows(p):return list(csv.DictReader((HERE/p).open()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    target=load('metadata/target_build_summary.json');eda=load('metadata/eda_summary.json')
    peer=load('reconciliation_targets/FINAL_RECONCILIATION_REVIEW.json')
    ea=load('project_reconciliation/independent_eda_audit/result.json')
    pred=load('predictor_reconciliation/core_availability_summary.json')
    pa=load('predictor_reconciliation/ppac_audit_results.json')
    if ea['failed'] or peer['legacy_revision_set_errors'] or peer['legacy_flag_errors'] or peer['legacy_panel_arithmetic_errors'] or peer['lineage_repair_numeric_errors']:
        raise ValueError('Independent review has unresolved failures')
    latest=load('reconciliation_targets/latest_run.json')
    rr=load(str(Path('reconciliation_targets/runs')/latest['run_id']/'reconciliation_summary.json'))
    if rr['producer_math_discrepancies'] or rr['producer_lineage_discrepancies'] or rr['excluded_intervals_used']:
        raise ValueError('Target reconciliation has unresolved failures')
    primary=rows('analysis/analysis_targets.csv');aux=rows('analysis/auxiliary_targets.csv')
    spec=load('metadata/analysis_specification.json')
    segments=[]
    for city in spec['primary_cities']+spec['auxiliary_markets']:
        rs=[r for r in primary+aux if r['city']==city]
        segments.append(dict(city=city,scope='primary_intended' if city in spec['primary_cities'] else 'auxiliary',
                             accepted_monthend=target['per_city'][city]['monthend'],accepted_day_end_mean=target['per_city'][city]['twap'],
                             first_available_month=min((r['year_month'] for r in rs),default=''),last_available_month=max((r['year_month'] for r in rs),default=''),
                             source_interval_count=len({i for r in rs for i in json.loads(r['source_interval_ids'])}),
                             source_quality='restricted_documentary_path_assumption' if rs else 'no_accepted_path',
                             historical_price_predictor_availability='not_certified' if rs else 'not_available',
                             decision='retain_qualified_outcomes' if rs else 'exclude_candidate_prices',missing_value_rule='no_backfill_or_interpolation',
                             source='accepted_stage3_2026-11-06_restricted_v1/data/price_intervals.csv'))
    with (HERE/'metadata/city_segment_eligibility.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(segments[0]),lineterminator='\n');w.writeheader();w.writerows(segments)
    lines=['STAGE 4 REDO CHECKPOINT — 9 NOVEMBER 2026',
           'Preprocessing, Integration and EDA','','OBJECTIVE',
           'Reconcile the accessible BTP/BTP2 collection generations, qualify the main',
           'analysis sample, reproduce monthly targets and inspect only development data.',
           'This checkpoint replaces the current Stage 4 delivery, not its preserved history.',
           '', 'WHAT WAS DEMONSTRABLY COMPLETED BEFORE THIS REDO',
           'The current worktree belongs to the CNG repository used under app project BTP 2',
           'at Desktop/[ME] BTP. That folder contains the legacy BTP collection, expanded',
           'recovery evidence, a researcher-accepted restricted Stage 3 snapshot, and executed',
           '6 November Stage 4 outputs with independent receipts. These are different versions',
           'of related evidence, not two automatically independent datasets.',
           'The app-local project named BTP at Desktop/BTP Project is an unrelated flight',
           'simulator and was excluded. The user confirmed Desktop/[ME] BTP as the location.',
           '', 'REPORTED LEGACY COMPLETION VERSUS ACTUAL EVIDENCE',
           'Legacy files match branch 6b08b99666ef2b08605c63499418503a4d666c3b and the modified',
           'Desktop BTP/BTP_CNG_Data copy: 1,503 finalized target rows; 2,293 sampled price',
           'observations; 275 selected revision records; 190 external-factor months;',
           '799 corporate metadata rows; 10 news/policy records; 8 regulatory records.',
           'Counts match the brief. Their scientific completion claims do not follow:',
           '- All 1,503 legacy target rows are flagged unverified_feed_proxy.',
           '- 275 revision records are 10 initial baselines plus 265 nonzero sampled changes',
           '  (213 increases and 52 decreases). The other 2,018 observations repeat a price.',
           '  Sampled changes do not prove the dates or completeness of official revisions.',
           '- 18 provisional target rows are 8 partially covered first historical months and',
           '  10 incomplete November 2026 months. November remains outside this envelope.',
           '- The examined chart builders forward-hold after the first sample. No examined',
           '  CNG builder backward-fills before its earliest observation. Unsupported tariff',
           '  continuity is rejected without inventing a claim that every hold was fabricated.',
           '- 799 corporate metadata records have 758 distinct nonempty attachment names,',
           '  with 798 not marked downloaded and one marked downloaded. That one row points',
           '  an October timestamp at a November allocation PDF; its date does not date the PDF.',
           '- All 10 news timestamps and headline/excerpt payloads are code literals. A hash',
           '  of authored text does not verify a publisher timestamp or original article.',
           '- Actual observed monthly VAHAN remains missing. The generated quarantine is excluded.',
           'The broader recovered corpus separately contains 251 unique corporate PDF objects',
           'and 24 article metadata records. Those are not the 799 downloaded documents or a',
           'representative historical sentiment corpus. Their origin-time rules remain qualified.',
           '', 'RECONCILIATION DECISIONS',
           'The inventory inspected 1,090 scientific files and 317 tables, identifying 119',
           'exact-byte copy groups. Copies do not add independent information. Different',
           'versions at the same relative path are kept separate. Original sources remain intact.',
           'The legacy finalized panel has no duplicate city-month keys. Its disagreement with',
           'accepted counterparts is a quality issue, not a duplicate-key repair: 216 month-end',
           'cells and 250 average cells conflict; 187 and 145 respectively agree including',
           'export-rounding tolerance. Agreement alone never promotes unverified source rows.',
           'The 275 accepted documentary intervals and the 275 legacy revision-list rows are',
           'different entities. They are never merged on their shared count.',
           '', 'ACCEPTED INPUTS AND MAIN SAMPLE',
           'Snapshot: stage3-restricted-2026-11-06-v1. Manifest SHA256:',
           '968d4ad2b34c444ab6e4c9da33eae5b0c9c14bde7c01d308084136874ce3cea3',
           'All accepted files and previous Stage 4 outputs are preserved. Twelve disputed',
           'intervals remain excluded. No new source observation or availability date was invented.',
           'Main intended geography remains the ten cities in the attachment; main calendar',
           'envelope is January 2011–October 2026. Only Delhi, Noida and Lucknow have accepted',
           'interval paths in that geography. Agra and Unnao are separately labelled auxiliary.',
           '', 'City             Month-end outcomes    Complete day-end monthly means']
    for c in ['Delhi','Noida','Lucknow']:
        n=target['per_city'][c];lines.append(f"{c:<17}{n['monthend']:>12}{n['twap']:>32}")
    lines += [f"TOTAL            {target['primary']['monthend']:>12}{target['primary']['twap']:>32}",
              '', 'Mumbai, Pune, Ahmedabad, Gurgaon, Kanpur, Hyderabad and Bengaluru have no',
              'retained accepted targets in this version. Legacy candidates are preserved as',
              'audit material, not silently substituted. There are 1,900 coverage-calendar rows',
              '(10 cities × 190 months), but only 424 primary analysis rows with a target.',
              'Empty coverage slots are missing records in a diagnostic grid, not invented prices.',
              'Auxiliary Agra/Unnao have 128 month-end outcomes and 125 complete averages.',
              'Removing pre-2011 months and separating auxiliary markets explains the change',
              'from the earlier 566/553 totals; it is not a new collection or outcome-driven cut.',
              '', 'METHODS AND DEFINITIONS',
              'Use only accepted half-open [start,end) intervals, rejecting overlap. A hold is',
              'conditional on the accepted official chronology within its bounded interval.',
              'There is no terminal extension, interpolation, backfill or missing-to-zero step.',
              'cng_price_monthend is the quote at the last calendar day end if covered.',
              'cng_price_twap is explicitly the calendar-day-weighted mean of day-end quotes,',
              'available only with every day covered. It is not an identified intraday integral.',
              'Conditional lower/upper timing envelopes use the previous/current quote extrema',
              'and require the predecessor day. They assume no unlisted intraday round trips;',
              'they are neither statistical confidence intervals nor forecast intervals.',
              'Lineage includes the exact source intervals, object hashes and cell locators',
              'supporting the monthly target or its timing predecessor. Original publication',
              'and extraction times remain unknown where absent; snapshot time is not substituted.',
              'Target/segment dictionaries document meaning, units, quality and availability.',
              'No imputer, scaler, outlier deletion or learned transformation was fitted.',
              '', 'DEVELOPMENT EDA — ACTUAL COMPUTED RESULTS',
              'The development sample has 394 month-end outcomes and 386 complete averages.',
              'The 120 reserved calendar slots are used for coverage only; 30 have each target.',
              'Reserved numeric targets are filtered out before EDA parsing. Gaps break lines.',
              'Month-end persistence conditional on adjacent known months:']
    for r in rows('eda/persistence.csv'):
        if r['target']=='cng_price_monthend':lines.append(f"{r['city']}: {r['flat_pairs']}/{r['adjacent_pairs']} unchanged ({float(r['flat_fraction']):.1%}); {r['nonzero_pairs']} nonzero changes.")
    lines += ['Average-target persistence differs: monthly averaging can spread a price change',
              'over adjacent outcomes. Both targets remain separate in every descriptive table.',
              'The profile includes six distributions, 759 adjacent changes, 12 matched-month',
              'correlations, annual change profiles and 54 retained Tukey flags across both targets.',
              'Flags identify unusual changes under a declared descriptive rule; none were deleted.',
              'Large aggregate movement in 2022 and the 2014 downward steps merit later regime',
              'review. Unequal valid pairs, gaps and shared national/operator conditions prevent',
              'attribution to a policy or a claim of a statistically identified break.',
              'Three core cities share only two operators. Levels and changes are dependent;',
              'unbalanced city means cannot establish a regional price premium or causal effect.',
              'No stationarity, seasonality, break, significance or forecast-performance test ran.',
              '', 'PREDICTOR AND TEXT AVAILABILITY',
              'Legacy predictor audit found 26 annual GDP release assignments preceding their',
              'own observation-year ends, 179 identical FX mean/close pairs from monthly closes,',
              'and four energy benchmark fields held at December 2024 values for 22 later months.',
              'These source/label/time problems are documented, not repaired by another shift.',
              'A Europe natural-gas benchmark is not silently relabelled as a pure TTF spot series.',
              f"The inherited documented-date filter supplies {pred['strict_ledger_rows']} core as-of references at {pred['strict_origins_with_any_factor']} origins,",
              f"using {pred['strict_distinct_native_source_observations']} distinct national source observations. All eligible origins are reserved.",
              'None of the 394 development origins has a factor under that filter. The word',
              'strict in the ledger name means the documented-date filter, not proof that every',
              'historical source vintage was archived. Original qualifications remain attached.',
              'Consequently no strict H1 development comparison is currently available. This',
              'is a feasibility limitation, not evidence that numerical factors lack predictive value.',
              f"A new source check finds {pa['passed_native_role_value_and_listing_interval_checks']}/{pa['fresh_monthly_candidates_audited']} PPAC candidates whose PDF value, monetary role,",
              'GCV basis and official listing interval agree. Forty have archive-day claims before',
              'November 2025. These remain an explicit sensitivity tier: 88 references across',
              '52 core origins (46 development, 6 reserved), not 88 new measurements.',
              'They are calculated domestic formula prices or explicit nomination-field ceilings,',
              'not actual blended CGD procurement costs. Thirteen candidates need manual review.',
              'The archive was captured retrospectively. No strict historical admission follows.',
              'A signed document date is not substituted for the archive release claim: January',
              '2025 is signed 31 December 2024 but listed 1 January 2025. Even a later approved',
              'proxy must obey its disclosed source-day bound and native effective interval.',
              'No expired hold, arbitrary one-month shift or national-to-city allocation is used.',
              'H2 remains unproven: hard-coded legacy labels, sparse selected articles and',
              'undated corporate records cannot establish a valid news/disclosure comparison.',
              'Retrospective target construction also does not certify price-lag availability.',
              '', 'KNOWN PRIOR EXPOSURE AND RESERVATION',
              'The provisional November 2025–October 2026 window is retained from the earlier',
              'Stage 4. Newly found date/configuration metadata show an earlier six-city aggregate',
              'study used April 2011–December 2025 data and a July 2021–December 2025 holdout.',
              'Its 177/123/54 sample counts reconcile. November–December 2025 is therefore',
              'known to overlap prior evaluation in a related study. Prior executed 2026 test',
              'exposure remains unknown. Current legacy input modification times postdate the',
              'saved result artifact, and executed input hashes/configuration receipts are absent.',
              'This is date/configuration and checkpoint evidence of related-study exposure,',
              'not exact reproduction of the historical run. No old score was used for selection.',
              'The reservation must never be called an untouched final test. Original Stage 6',
              'must predeclare an honest evaluation strategy and disclose this exposure.',
              '', 'INDEPENDENT VERIFICATION',
              'Target audit used rational interval-prefix arithmetic, distinct from daily expansion.',
              'All 3,256 exported rows, including calendar and split copies, reconcile in arithmetic',
              'and row-specific provenance. These are audit checks, not independent observations.',
              'All 12 disputed intervals are absent. The prior accepted Stage 4 matches within',
              'the new date envelope: 552 month-end values and 541 means including auxiliary.',
              f"Independent NumPy/Pandas EDA recalculation passes {ea['passed']}/{ea['checks']} checks, including",
              'all six summaries/persistence records, changes, flags and matched correlations.',
              'Three selected PPAC sources were independently decoded with pypdf, separate from',
              'the Poppler implementation. These examples check values/roles, not all vintages.',
              'Three figure pairs were visually reviewed for labels, gaps and reserved concealment.',
              'Final package and unchanged-snapshot verification is recorded in DELIVERY_STATUS.txt.',
              '', 'FAILURES AND RECOVERY',
              'The initial new run omitted a predecessor source interval from some timing-bound',
              'lineage. Its code, targets and EDA are preserved. The correction changes 69 export',
              'rows including split copies, with no changed prices or bounds. Dependent outputs',
              'were rebuilt and independently checked. The reviewer also corrected two enum/schema',
              'expectation errors; original failed attempts remain, with no source-data repair implied.',
              'Bundled Python lacks matplotlib; existing scientific Python produced the figures.',
              'Package versions and the dependency-probe limitation are documented. Earlier Stage 4',
              'artifact-retention/registration deviations remain in its preserved registry.',
              '', 'STATISTICAL RELIABILITY',
              'There are three supported core cities, two operators, gaps and only 18–55 nonzero',
              'adjacent month-end changes per development city. Row counts are not effective',
              'independent sample sizes. Formal power, autocorrelation and overlapping-horizon',
              'consequences belong to original Stage 5. No confirmatory inference, multiple-testing',
              'claim, model selection, H1/H2 verdict, GAM superiority or causal conclusion is made.',
              '', 'DECISION AND STAGE MAPPING',
              'Stage 4 outcome preprocessing and descriptive reconciliation are complete with',
              'the stated qualifications. The independent end-stage decision and package checks',
              'accompany this report; they do not constitute researcher approval.',
              'The original nine-stage workflow is retrieved and preserved. Attachment Stage 5',
              'design/features tasks map mainly to original Stage 6. Original Stage 5 remains',
              'Stationarity, Structural Breaks and Statistical Properties. Stage 5 has not begun.',
              'This redo does not make the unrestricted ten-city study or H1/H2 forecasts ready.',
              '', 'NEXT ACTION',
              'Researcher review should accept or revise the three-city qualified outcome scope,',
              'the explicit auxiliary distinction and the disclosed prior exposure. If accepted,',
              'original Stage 5 can assess supported contiguous segments, persistence, assumptions',
              'and effective information. Strict future forecasting still requires origin-time',
              'price availability and an honest Stage 6 design. A PPAC sensitivity specification',
              'would need explicit methodological approval; proxy dates must not silently replace',
              'verified historical availability. Additional seven-city price paths and a dated,',
              'representative text corpus remain evidence dependencies, not invented observations.',
              '', 'DELIVERABLE MAP',
              'analysis/analysis_targets.csv: qualified primary outcomes with unique city-month keys.',
              'analysis/development_targets.csv and reserved_targets.csv: separate partitions.',
              'analysis/coverage_calendar.csv: 1,900 coverage slots, never a fabricated balanced panel.',
              'analysis/auxiliary_targets.csv: Agra/Unnao retained separately.',
              'metadata/: dictionary, city-segment rules, transformations, horizons, stage tracker, registry.',
              'project_reconciliation/: file/version/claim reconciliation, workflow map and exposure proof.',
              'reconciliation_targets/: raw-feed/legacy and independent accepted-target audit.',
              'predictor_reconciliation/: native grain, release, vintage and text eligibility audits.',
              'eda/ and figures/: development-only tables and three standalone PNG/SVG pairs.',
              'logs/versions/: preserved pre-correction output/code; no failed analysis erased.']
    (HERE/'STAGE4_REDO_CHECKPOINT_REPORT.txt').write_text('\n'.join(lines)+'\n')
    # Preserve exact retrieved names, separating prior recorded completion from this redo.
    tracker=load('metadata/stage_tracker.json')
    names={int(r['original_stage']):r['retrieved_original_stage_name'] for r in rows('project_reconciliation/workflow_mapping.csv')}
    for r in tracker['stages']:r['name']=names[r['stage']]
    tracker['updated_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    s4=next(r for r in tracker['stages'] if r['stage']==4)
    s4.update(status='completed_qualified_pending_researcher_review',checks_executed='Independent target, source lineage, full legacy arithmetic and EDA checks passed; accepted snapshot and all91 prior Stage4 manifest entries unchanged; final end-stage/package receipts accompany the checkpoint',
              dependencies='Future forecasting availability/design decisions remain; seven-city paths/H2 still incomplete',evidence='STAGE4_REDO_CHECKPOINT_REPORT.txt and independent audit receipts')
    tracker['stage4_researcher_accepted']=False
    (HERE/'metadata/stage_tracker.json').write_text(json.dumps(tracker,indent=2))
    print('Checkpoint drafted from executed results; final scientific/delivery review pending')
if __name__=='__main__':main()
