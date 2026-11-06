"""Independent exhaustive selection/boundary checks; imports no integration helpers."""
from pathlib import Path
from decimal import Decimal
from datetime import datetime,date,timedelta
from collections import defaultdict,Counter
import csv,json,hashlib,argparse,calendar,copy

def rows(p):
    with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def evaluate(ledger,factors,origins):
    problems=[];byid={r['source_observation_id']:r for r in factors};ob={r['origin_id']:r for r in origins}
    byns=defaultdict(list)
    for r in factors:byns[r['namespace_id']].append(r)
    supplied={}
    for r in ledger:
        key=(r['origin_id'],r['namespace_id'])
        if key in supplied:problems.append('duplicate_origin_namespace')
        supplied[key]=r
        if r['source_observation_id'] not in byid or r['origin_id'] not in ob:problems.append('orphan_reference');continue
        source=byid[r['source_observation_id']];origin=ob[r['origin_id']];cutoff=datetime.fromisoformat(origin['forecast_origin']);release=datetime.fromisoformat(r['publication_timestamp_bound'])
        if release>cutoff:problems.append('future_release_leakage')
        if date.fromisoformat(r['native_period_end'])>cutoff.date():problems.append('future_reference_period')
        for k in ['value','unit','frequency','native_period_start','native_period_end','publication_timestamp_bound','raw_sha256']:
            if r[k]!=source[k]:problems.append('source_field_mismatch:'+k)
        if r['market']!=origin['market'] or r['month']!=origin['month']:problems.append('origin_mismatch')
        if r['reserved_final_evaluation']!=origin['reserved_final_evaluation']:problems.append('reserved_flag_mismatch')
        if r['information_state']!='last_known_released_native_observation_not_new_monthly_measurement':problems.append('held_native_value_mislabeled')
        if r['source_scope']!='national_shared_not_city_specific':problems.append('unverified_city_allocation')
        if int(r['reference_age_days'])!=(cutoff.date()-date.fromisoformat(r['native_period_end'])).days:problems.append('reference_age_error')
        if r['lagged_price_predictor_availability']!='not_certified_by_retrospective_outcome_acceptance':problems.append('unsupported_price_predictor_certification')
    expected=0
    for origin in origins:
        cutoff=datetime.fromisoformat(origin['forecast_origin'])
        for ns,candidates in byns.items():
            eligible=[]
            for source in candidates:
                release=datetime.fromisoformat(source['publication_timestamp_bound'])
                if release<=cutoff and date.fromisoformat(source['native_period_end'])<=cutoff.date():eligible.append(source)
            k=(origin['origin_id'],ns)
            if not eligible:
                if k in supplied:problems.append('manufactured_availability')
                continue
            # Independent lexicographic priority tuple: latest ended period, then
            # release moment among versions for that period. No producer function.
            priority=max((x['native_period_end'],datetime.fromisoformat(x['publication_timestamp_bound'])) for x in eligible)
            selected=[x for x in eligible if (x['native_period_end'],datetime.fromisoformat(x['publication_timestamp_bound']))==priority]
            if len({Decimal(x['value']) for x in selected})>1:
                if k in supplied:problems.append('conflicting_tie_selected')
                continue
            expected+=1
            if k not in supplied:problems.append('missing_eligible_asof_record');continue
            if supplied[k]['source_observation_id'] not in {x['source_observation_id'] for x in selected}:problems.append('wrong_reference_or_vintage_selected')
    return problems,expected

def run(a):
    b=a.integration;ledger=rows(b/'asof_numerical_ledger.csv');factors=rows(b/'eligible_native_factors.csv');origins=rows(b/'forecast_origins.csv');targets=rows(a.targets)
    problems,expected=evaluate(ledger,factors,origins);checks=[]
    def check(name,ok,detail):checks.append({'check':name,'passed':bool(ok),'detail':detail})
    check('all_asof_selections_independently_recomputed',not problems,{'asof_rows':len(ledger),'expected_rows':expected,'problems':dict(Counter(problems))})
    eligible_targets={(r['market'],r['month']) for r in targets if r['month_end_price_inr_kg'].strip()}
    actual_origins={(r['market'],r['month']) for r in origins}
    check('origins_exactly_observed_monthend_target_keys',eligible_targets==actual_origins,len(origins))
    origin_errors=[]
    for r in origins:
        d=datetime.fromisoformat(r['forecast_origin']);m=date.fromisoformat(r['month']+'-01')
        if d.date()!=m.replace(day=calendar.monthrange(m.year,m.month)[1]) or d.hour!=23 or d.minute!=59:origin_errors.append(r['origin_id'])
        if (r['reserved_final_evaluation']=='True')!=('2025-11'<=r['month']<='2026-10'):origin_errors.append(r['origin_id'])
    check('origin_calendar_and_reserved_boundary',not origin_errors,{'reserved_origins':sum(r['reserved_final_evaluation']=='True' for r in origins),'errors':len(origin_errors)})
    keyfields=['namespace_id','raw_sha256','native_period_start','native_period_end']
    check('eligible_source_version_period_keys_unique',len({tuple(r[c] for c in keyfields) for r in factors})==len(factors),len(factors))
    rawchecks={}
    for r in factors:
        if r['raw_sha256'] not in rawchecks:rawchecks[r['raw_sha256']]=digest(a.candidate/r['raw_object_path'])==r['raw_sha256']
    check('eligible_original_source_hashes',all(rawchecks.values()),len(rawchecks))
    native=rows(a.accepted/'reference/native_numerical_observations.csv');excluded=rows(b/'excluded_availability.csv')
    missing={r['observation_id'] for r in native if not r['publication_date']};excludedmissing={r['observation_id'] for r in excluded if r['reason']=='unknown_publication_date_no_assumed_lag'}
    check('all_unknown_release_numerical_records_excluded',missing==excludedmissing,len(missing))
    check('station_indicators_and_unverified_PPAC_absent',all(r['series']!='cng_station_reported_indicator' and not r['family'].endswith('_candidate') for r in factors),len(factors))
    corp=rows(a.accepted/'reference/corporate_document_metadata.csv');excludedcorp={r['observation_id'] for r in excluded if r['dataset']=='corporate'}
    check('all_corporate_metadata_excluded_as_historical_predictors',len(corp)==len(excludedcorp),len(corp))
    # A deliberately corrupted in-memory record tests a real leakage rejection.
    # This is an audit fixture and is never written as a research observation.
    if ledger:
        mutated=copy.deepcopy(ledger);cutoff=datetime.fromisoformat(mutated[0]['forecast_origin']);mutated[0]['publication_timestamp_bound']=(cutoff+timedelta(days=1)).isoformat();bad,_=evaluate(mutated,factors,origins)
        check('deliberately_future_release_rejected','future_release_leakage' in bad,'In-memory audit fixture, not research data')
    articles=rows(b/'news_time_claim_inventory.csv');newsrefs=rows(b/'news_asof_metadata.csv');ad={x['article_id']:x for x in articles};od={x['origin_id']:x for x in origins}
    news_errors=[]
    for r in newsrefs:
        if datetime.fromisoformat(r['publication_timestamp_claim'])>datetime.fromisoformat(od[r['origin_id']]['forecast_origin']):news_errors.append(r['article_id'])
        if r['sentiment_or_text_features_computed']!='False' or r['market_relevance']!='unverified':news_errors.append(r['article_id'])
    check('news_is_timestamp_claim_metadata_only_no_future_claims',not news_errors,{'articles':len(articles),'references':len(newsrefs)})
    check('no_text_predictor_eligibility_claim',all(r['predictor_eligible']=='False' for r in articles),len(articles))
    provenance=json.loads((b/'metadata/input_provenance.json').read_text());accept=json.loads((a.accepted/'metadata/acceptance.json').read_text())
    check('accepted_manifest_and_target_hash_binding',digest(a.accepted/'metadata/snapshot_manifest.json')==provenance['accepted_manifest_sha256'] and digest(a.targets)==provenance['targets_sha256'] and accept['restricted_stage3_accepted'] and accept['stage4_authorized'],provenance['accepted_manifest_sha256'])
    result={'verified_at':datetime.now().astimezone().isoformat(),'producer_helpers_imported':False,'checks':checks,'all_checks_passed':all(r['passed'] for r in checks),'stage5_started':False,'reserved_outcomes_used_for_statistical_selection':False,'limitations':['Independent checks validate release-constrained integration calculations, not every economic source assertion.','Source-upload timestamp claims and publisher metadata do not independently certify historical archived bytes.','No H1/H2 result or forecasting model was produced.']}
    (b/'metadata/independent_integration_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));raise SystemExit(0 if result['all_checks_passed'] else 1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--integration',type=Path,required=True);p.add_argument('--accepted',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--targets',type=Path,required=True);run(p.parse_args())
