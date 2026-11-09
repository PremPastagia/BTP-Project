"""Audit-only core-calendar mapping. Target values are never selected or analyzed."""
from pathlib import Path
from collections import defaultdict,Counter
from datetime import datetime,timezone
import csv,json,hashlib,argparse

def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,rs,fields):
    with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs)
def run(a):
    out=a.output;assert (out/'registry/AMENDMENT_001_CORE_ORIGINS.json').is_file()
    # Only calendar/partition metadata is retained from the target file.
    core=[]
    with a.core.open(encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):core.append({'city':row['city'],'year_month':row['year_month'],'sample_period':row['sample_period']})
    keys={(r['city'],r['year_month']) for r in core};assert len(keys)==len(core)
    prior=a.repo/'BTP_CNG_Data/stage4_2026-11-06/integration';candidate=a.repo/'BTP_CNG_Data/consolidated_2026-11-06';accepted=a.repo/'BTP_CNG_Data/accepted_stage3_2026-11-06_restricted_v1'
    ledgerpath=prior/'asof_numerical_ledger.csv';ledger=read(ledgerpath);coremap={(r['city'],r['year_month']):r for r in core}
    subset=[]
    for r in ledger:
        k=(r['market'],r['month'])
        if k not in keys:continue
        row={**r,'redo_core_sample_period':coremap[k]['sample_period'],'previous_ledger_sha256':sha(ledgerpath),'mapping_rule':'exact_city_month_key_only_not_new_native_measurement'}
        assert datetime.fromisoformat(row['publication_timestamp_bound'])<=datetime.fromisoformat(row['forecast_origin'])
        subset.append(row)
    write(out/'strict_core_asof_ledger.csv',subset,list(subset[0]) if subset else list(ledger[0])+['redo_core_sample_period','previous_ledger_sha256','mapping_rule'])
    counts=Counter((r['market'],r['month']) for r in subset)
    originrows=[{**r,'strict_asof_factor_rows':counts[(r['city'],r['year_month'])],'historical_price_predictor_publication_certified':False,'decision':'documented_source_date_bound_with_preserved_vintage_qualification' if counts[(r['city'],r['year_month'])] else 'no_strict_dated_H1_factor_at_this_origin'} for r in core]
    write(out/'core_origin_availability.csv',originrows,list(originrows[0]))
    # The PPAC audit tier is separate and never modifies the strict ledger.
    ppac=read(out/'ppac_native_release_claims.csv');qualified=[r for r in ppac if r['sensitivity_eligible']=='True'];proxy=[]
    for origin in core:
        last=(datetime.fromisoformat(origin['year_month']+'-01').replace(day=28)+__import__('datetime').timedelta(days=4)).replace(day=1)-__import__('datetime').timedelta(days=1)
        d=last.date().isoformat()
        for r in qualified:
            if r['effective_start']<=d<=r['effective_end'] and r['official_archive_date_claim']<=d:
                proxy.append({'city':origin['city'],'year_month':origin['year_month'],'sample_period':origin['sample_period'],**r,'mapping_rule':'active_native_notified_interval_contains_monthend_and_official_date_claim_not_after_origin','held_past_expiry':False,'national_value_allocated_to_city':False})
    write(out/'qualified_PPAC_core_reference.csv',proxy,list(proxy[0]) if proxy else ['city','year_month','sample_period','candidate_observation_id'])
    # Native per-variable dictionary supplements, rather than overwrites, legacy audit.
    native=read(accepted/'reference/native_numerical_observations.csv');groups=defaultdict(list)
    for r in native:groups[tuple(r[k] for k in ['family','series','geography','frequency','unit','raw_sha256'])].append(r)
    vardict=[]
    for key,rs in groups.items():
        data=dict(zip(['family','series','geography','frequency','unit','raw_sha256'],key));known=sum(bool(r['publication_date']) for r in rs)
        data.update(native_rows=len(rs),publication_dates_recorded=known,publication_dates_unknown=len(rs)-known,first_native_period=min(r['period'] for r in rs),last_native_period=max(r['period'] for r in rs),availability_rule='No assumed one-month lag; preserve native period and exact source version.',eligibility='date_unknown_excluded' if not known else 'documented_June2026_GDP_release_with_source_vintage_qualification; no_exploratory_history',source_scope='national_shared_or_international_not_city_specific')
        vardict.append(data)
    write(out/'native_variable_eligibility_dictionary.csv',vardict,list(vardict[0]))
    # Selected text metadata is timed evidence, not a representative sentiment corpus.
    textdict=[]
    for name in ['news_metadata.csv','corporate_document_metadata.csv']:
        rows=read(accepted/'reference'/name)
        if name=='news_metadata.csv':
            for r in rows:
                value=r['publication_date'];aware=False
                try:aware=bool(datetime.fromisoformat(value.replace('Z','+00:00')).tzinfo)
                except ValueError:pass
                textdict.append({'dataset':name,'record_id':r['article_id'],'source_hash':r['sha256'],'publication_claim':value,'timestamp_timezone_aware':aware,'strict_predictor_eligible':False,'eligibility_rule':'selected_publisher_timestamp_claim_metadata_only; independent_vintage_city_relevance_coverage_and_license_not_established'})
        else:
            for r in rows:textdict.append({'dataset':name,'record_id':r['document_id'],'source_hash':r['raw_sha256'],'publication_claim':r['publication_date_claims'],'timestamp_timezone_aware':False,'strict_predictor_eligible':False,'eligibility_rule':'undated_or_unverified_corporate_release_excluded; exact_bytes_are_not_publication_evidence'})
    write(out/'native_corpus_eligibility_dictionary.csv',textdict,list(textdict[0]))
    provenance={'core_calendar_path':str(a.core),'core_file_sha256':sha(a.core),'previous_ledger_path':str(ledgerpath),'previous_ledger_sha256':sha(ledgerpath),'previous_verification_receipt_sha256':sha(prior/'metadata/independent_integration_validation.json'),'candidate_manifest_sha256':sha(candidate/'metadata/snapshot_checksums.json'),'accepted_manifest_sha256':sha(accepted/'metadata/snapshot_manifest.json'),'registered_core_mapping_amendment_sha256':sha(out/'registry/AMENDMENT_001_CORE_ORIGINS.json'),'ppac_source_audit_sha256':sha(out/'ppac_native_release_claims.csv')}
    (out/'core_input_hashes.json').write_text(json.dumps(provenance,indent=2))
    origins_with={(r['market'],r['month']) for r in subset};proxyorigins={(r['city'],r['year_month']) for r in proxy}
    summary={'executed_at_utc':datetime.now(timezone.utc).isoformat(),'primary_calendar_origins':len(core),'calendar_by_city':dict(Counter(r['city'] for r in core)),'calendar_by_partition':dict(Counter(r['sample_period'] for r in core)),'strict_ledger_rows':len(subset),'strict_origins_with_any_factor':len(origins_with),'strict_origins_by_partition':dict(Counter(r['sample_period'] for r in core if (r['city'],r['year_month']) in origins_with)),'strict_distinct_native_source_observations':len({r['source_observation_id'] for r in subset}),'strict_families':dict(Counter(r['family'] for r in subset)),'qualified_PPAC_reference_rows':len(proxy),'qualified_PPAC_origins':len(proxyorigins),'qualified_PPAC_origins_by_partition':dict(Counter(r['sample_period'] for r in core if (r['city'],r['year_month']) in proxyorigins)),'native_variable_vintage_groups':len(vardict),'native_corpus_records':len(textdict),'new_strict_H1_or_H2_admissions':0,'no_future_holdout_outcome_values_analyzed_or_disclosed':True,'no_models_or_inferential_tests':True,'stage5_started':False,'limitations':['Strict refers to the earlier documented-date filter, not independently archived historical source bytes; original qualifications remain in every row.','Qualified official-listing PPAC proxy records are sensitivity-only and do not enter strict coverage totals.','National source values repeated across city calendars are not independent city measurements.']}
    (out/'core_availability_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--core',type=Path,required=True);p.add_argument('--output',type=Path,required=True);run(p.parse_args())
