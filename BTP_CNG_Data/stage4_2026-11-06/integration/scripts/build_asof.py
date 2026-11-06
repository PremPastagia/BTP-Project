"""Release-constrained native-factor integration. No forecasts or statistical tests."""
from pathlib import Path
from decimal import Decimal
from collections import defaultdict,Counter
from datetime import datetime,date,time,timedelta,timezone
from zoneinfo import ZoneInfo
import argparse,csv,hashlib,json,calendar,re

IST=ZoneInfo('Asia/Kolkata')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(path,records,fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
def ident(xs):return hashlib.sha256(json.dumps(xs,sort_keys=True).encode()).hexdigest()[:24]
def publication(value,day_bound=True):
    if not value:return None,'unknown'
    try:
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
            if not day_bound:return None,'date_only_no_timezone_metadata'
            return datetime.combine(date.fromisoformat(value),time.max,IST),'end_of_documented_Indian_publication_day_not_exact_release_time'
        d=datetime.fromisoformat(value.replace('Z','+00:00'))
        if d.tzinfo is None:return None,'timezone_unknown'
        return d,'source_timestamp_with_timezone'
    except ValueError:return None,'invalid_date_or_time'

def run(a):
    out=a.output;out.mkdir(parents=True,exist_ok=True)
    assert a.accepted.is_dir() and a.approval_record.is_file(),'Accepted snapshot and approval record must exist'
    assert a.targets.is_file(),'No forecast origins without observed accepted target records'
    acceptance=json.loads(a.approval_record.read_text())
    assert acceptance['restricted_stage3_accepted'] is True and acceptance['stage4_authorized'] is True
    assert acceptance['candidate_manifest_sha256']==sha(a.candidate/'metadata/snapshot_checksums.json')
    accepted_manifest=a.accepted/'metadata/snapshot_manifest.json'
    assert sha(accepted_manifest)==a.accepted_manifest_sha256,'Accepted snapshot manifest does not match pinned version'
    accepted_files={r['path']:r['sha256'] for r in json.loads(accepted_manifest.read_text())}
    assert accepted_files['metadata/acceptance.json']==sha(a.approval_record)
    files={'native':'structured/numerical_factors/native_numerical_observations.csv','demand':'structured/numerical_factors/cng_reported_native.csv','candidates':'structured/numerical_factors/unverified_transcription_candidates.csv','news':'structured/news/news_metadata.csv','corporate':'structured/corporate_disclosures/corporate_document_metadata.csv'}
    frozen={r['path']:r['sha256'] for r in json.loads((a.candidate/'metadata/snapshot_checksums.json').read_text())}
    inputs={}
    for k,rel in files.items():
        if k=='candidates':p=a.candidate/rel
        else:
            record=next(x for x in acceptance['inputs'] if x['candidate_path']==rel)
            p=a.accepted/record['snapshot_path'];assert sha(p)==record['sha256']==accepted_files[record['snapshot_path']]
        h=sha(p);assert frozen.get(rel)==h,('Candidate differs from frozen manifest',rel)
        inputs[k]={'path':str(p),'sha256':h,'rows':read(p)}
    targetrows=read(a.targets);origins=[];seen=set()
    for r in targetrows:
        # Presence is checked without calculating or summarizing reserved outcome values.
        if not r.get('month_end_price_inr_kg','').strip():continue
        month=r['month'];d=date.fromisoformat(month+'-01');last=d.replace(day=calendar.monthrange(d.year,d.month)[1])
        assert month<'2026-11','Incomplete November cannot create an observed forecast origin'
        key=(r['market'],month)
        assert r['market'] in acceptance['scope']['markets']
        assert r['month_end']==last.isoformat()
        assert (r['provisional_reserved_period']=='True')==('2025-11'<=month<='2026-10')
        if key in seen:continue
        seen.add(key);oid=ident(key)
        origins.append({'origin_id':oid,'market':r['market'],'month':month,'forecast_origin':datetime.combine(last,time.max,IST).isoformat(),'reserved_final_evaluation':'2025-11'<=month<='2026-10','origin_basis':'complete_calendar_month_with_observed_month_end_target','lagged_price_predictor_availability':'not_certified_by_retrospective_outcome_acceptance'})
    origins.sort(key=lambda r:(r['market'],r['month']))
    assert origins
    release_check=json.loads(a.release_verification.read_text());assert release_check['all_checks_passed']
    assert release_check['native_table_sha256']==inputs['native']['sha256']
    verified_gdp={r['observation_id'] for r in release_check['value_checks']};gdp_hash=release_check['source_sha256'];gdp_release=datetime.fromisoformat(release_check['release_timestamp'])
    factors=[];excluded=[];inventory=defaultdict(list);duplicates=[];samekey=defaultdict(list)
    def reject(dataset,r,reason):
        excluded.append({'dataset':dataset,'observation_id':r.get('observation_id',r.get('document_id',r.get('article_id',''))),'family':r.get('family',''),'series':r.get('series',''),'source_id':r.get('source_id',''),'raw_sha256':r.get('raw_sha256',r.get('source_sha256',r.get('sha256',''))),'publication_claim':r.get('publication_date',''),'reason':reason})
    for dataset in ['native','demand']:
        for r in inputs[dataset]['rows']:
            family=r.get('family','demand_reported');series=r['series'];geo=r['geography'];freq=r['frequency'];unit=r['unit'];h=r.get('raw_sha256',r.get('source_sha256'))
            invkey=(dataset,family,series,geo,freq,unit,h)
            inventory[invkey].append(r)
            if not r.get('publication_date'):reject(dataset,r,'unknown_publication_date_no_assumed_lag');continue
            if dataset=='native':
                if r['observation_id'] not in verified_gdp or h!=gdp_hash:reject(dataset,r,'recorded_date_not_independently_verified_release_and_value');continue
                released=gdp_release;basis='independently_verified_explicit_PDF_embargo_vintage'
                start=r['period'];end=r['period_end'];verification='independent_PDF64cell_and_release_check'
            else:
                if series!='cng_sales_volume' or r.get('definition_status')!='CNG_only_not_PNG':reject(dataset,r,'station_flow_stock_or_nonCNG_definition_unresolved');continue
                if r.get('verification_status')!='table_cells_crosschecked_with_independent_pdf_text_engine':reject(dataset,r,'source_cell_meaning_check_not_recorded');continue
                released,basis=publication(r['publication_date']);start=r['period_start'];end=r['period_end'];verification=r['verification_status']
                basis+=';'+r['publication_date_basis']
            if released is None:reject(dataset,r,'publication_timestamp_invalid_or_ambiguous');continue
            try:startd=date.fromisoformat(start);endd=date.fromisoformat(end)
            except ValueError:reject(dataset,r,'native_reference_period_not_exactly_identified');continue
            if not startd<=endd:reject(dataset,r,'invalid_reference_period');continue
            relobj=r.get('raw_object_path',r.get('raw_file',r.get('source_path','')))
            raw=a.candidate/relobj
            assert raw.is_file() and sha(raw)==h,('Missing/mismatched source',relobj)
            semantic=[dataset,family,series,geo,freq,unit]
            namespace=ident(semantic)
            f={'namespace_id':namespace,'dataset':dataset,'family':family,'series':series,'geography':geo,'frequency':freq,'unit':unit,'native_period_start':start,'native_period_end':end,'value':r['value'],'source_observation_id':r['observation_id'],'raw_sha256':h,'raw_object_path':relobj,'publication_timestamp_bound':released.isoformat(),'publication_basis':basis,'source_scope':'national_shared_not_city_specific' if geo in ['India','global','International benchmark'] else 'not_mapped_to_target_market','verification':verification,'historical_vintage_status':'explicit_dated_release_not_independent_archive_proof' if dataset=='native' else 'source_upload_date_claim_current_download_not_independent_archive_proof','definition_note':r.get('definition_note',r.get('definition_status',''))}
            samekey[(namespace,h,start,end)].append(f)
    for key,rs in samekey.items():
        values={Decimal(r['value']) for r in rs}
        if len(values)>1:
            for r in rs:excluded.append({'dataset':r['dataset'],'observation_id':r['source_observation_id'],'family':r['family'],'series':r['series'],'source_id':'','raw_sha256':r['raw_sha256'],'publication_claim':r['publication_timestamp_bound'],'reason':'same_source_version_reference_period_conflicting_value'})
            continue
        factors.append(rs[0])
        for alias in rs[1:]:duplicates.append({'canonical_source_observation_id':rs[0]['source_observation_id'],'alias_source_observation_id':alias['source_observation_id'],'reason':'same_namespace_source_version_native_period_exact_value'})
    for r in inputs['candidates']['rows']:reject('candidates',r,'unverified_PPAC_transcription_excluded_from_historical_inputs')
    for r in inputs['corporate']['rows']:reject('corporate',r,'corporate_publication_availability_unverified_no_historical_input')
    namespaces=defaultdict(list)
    for f in factors:namespaces[f['namespace_id']].append(f)
    ledger=[];no_available=[];ties=[]
    for origin in origins:
        cutoff=datetime.fromisoformat(origin['forecast_origin']);origin_day=cutoff.date()
        for namespace,rs in namespaces.items():
            eligible=[r for r in rs if datetime.fromisoformat(r['publication_timestamp_bound'])<=cutoff and date.fromisoformat(r['native_period_end'])<=origin_day]
            if not eligible:
                no_available.append({'origin_id':origin['origin_id'],'market':origin['market'],'month':origin['month'],'namespace_id':namespace,'reason':'no_documented_released_native_observation_at_origin'});continue
            newest_period=max(r['native_period_end'] for r in eligible);eligible=[r for r in eligible if r['native_period_end']==newest_period]
            latest_release=max(datetime.fromisoformat(r['publication_timestamp_bound']) for r in eligible);eligible=[r for r in eligible if datetime.fromisoformat(r['publication_timestamp_bound'])==latest_release]
            if len({Decimal(r['value']) for r in eligible})>1:
                ties.append({'origin_id':origin['origin_id'],'namespace_id':namespace,'source_observation_ids':json.dumps([r['source_observation_id'] for r in eligible]),'reason':'same_latest_period_and_release_conflicting_values'});continue
            chosen=sorted(eligible,key=lambda r:(r['raw_sha256'],r['source_observation_id']))[0]
            ledger.append({**origin,**chosen,'asof_id':ident([origin['origin_id'],namespace,chosen['source_observation_id']]),'reference_age_days':(origin_day-date.fromisoformat(chosen['native_period_end'])).days,'release_age_days':(origin_day-latest_release.astimezone(IST).date()).days,'information_state':'last_known_released_native_observation_not_new_monthly_measurement','same_value_version_aliases':json.dumps([r['source_observation_id'] for r in eligible if r is not chosen])})
    # H2 remains a metadata feasibility inventory, never numeric sentiment/news features.
    news=[];news_asof=[]
    for r in inputs['news']['rows']:
        published,basis=publication(r['publication_date'],day_bound=False)
        reason='conditionally_timestamped_publisher_claim_only' if published else 'unknown_or_unresolvable_publication_time'
        row={'article_id':r['article_id'],'source_url':r['source_url'],'publisher':r['publisher'],'title':r['title'],'raw_sha256':r['sha256'],'publication_claim':r['publication_date'],'normalized_publication_timestamp':published.isoformat() if published else '', 'timestamp_basis':basis,'source_verification_status':r['publication_verification_status'],'asof_metadata_status':reason,'market_relevance':'not_verified_or_assigned','licensed_full_text_use':'not_established','predictor_eligible':'False'}
        news.append(row)
        if published:
            for origin in origins:
                if published<=datetime.fromisoformat(origin['forecast_origin']):news_asof.append({'origin_id':origin['origin_id'],'market':origin['market'],'month':origin['month'],'reserved_final_evaluation':origin['reserved_final_evaluation'],'article_id':r['article_id'],'publication_timestamp_claim':published.isoformat(),'eligibility':'metadata_time_claim_precedes_origin_only_not_validated_predictor','market_relevance':'unverified','sentiment_or_text_features_computed':'False'})
    inv=[]
    for key,rs in inventory.items():
        dataset,family,series,geo,freq,unit,h=key
        inv.append({'dataset':dataset,'family':family,'series':series,'geography':geo,'frequency':freq,'unit':unit,'raw_sha256':h,'native_rows':len(rs),'publication_date_missing':sum(not r.get('publication_date') for r in rs),'eligible_native_rows':sum(f['raw_sha256']==h and f['series']==series and f['geography']==geo and f['frequency']==freq and f['unit']==unit for f in factors),'integration_policy':'Native periods/vintages remain separate; no annual-to-monthly imputation.'})
    write(out/'forecast_origins.csv',origins,list(origins[0]))
    factorfields=list(factors[0]) if factors else ['namespace_id','series','value','publication_timestamp_bound']
    write(out/'eligible_native_factors.csv',factors,factorfields)
    ledgerfields=list(ledger[0]) if ledger else list(origins[0])+factorfields+['asof_id','reference_age_days','release_age_days','information_state','same_value_version_aliases']
    write(out/'asof_numerical_ledger.csv',ledger,ledgerfields)
    write(out/'factor_inventory.csv',inv,list(inv[0]))
    exfields=['dataset','observation_id','family','series','source_id','raw_sha256','publication_claim','reason']
    write(out/'excluded_availability.csv',excluded,exfields)
    write(out/'origin_factor_unavailable.csv',no_available,['origin_id','market','month','namespace_id','reason'])
    write(out/'source_version_aliases.csv',duplicates,['canonical_source_observation_id','alias_source_observation_id','reason'])
    write(out/'asof_conflicts.csv',ties,['origin_id','namespace_id','source_observation_ids','reason'])
    write(out/'news_time_claim_inventory.csv',news,list(news[0]))
    write(out/'news_asof_metadata.csv',news_asof,['origin_id','market','month','reserved_final_evaluation','article_id','publication_timestamp_claim','eligibility','market_relevance','sentiment_or_text_features_computed'])
    prov={'accepted_snapshot':str(a.accepted),'accepted_manifest_sha256':sha(accepted_manifest),'approval_record':str(a.approval_record),'approval_record_sha256':sha(a.approval_record),'targets':str(a.targets),'targets_sha256':sha(a.targets),'candidate_manifest_sha256':sha(a.candidate/'metadata/snapshot_checksums.json'),'input_tables':{k:{x:y for x,y in v.items() if x!='rows'} for k,v in inputs.items()},'source_release_verification_sha256':sha(a.release_verification)}
    (out/'metadata').mkdir(exist_ok=True);(out/'metadata/input_provenance.json').write_text(json.dumps(prov,indent=2))
    summary={'generated_at':datetime.now(timezone.utc).isoformat(),'forecast_origins':len(origins),'market_count':len({r['market'] for r in origins}),'eligible_native_factor_rows':len(factors),'eligible_namespaces':len(namespaces),'asof_rows':len(ledger),'origins_with_any_known_factor':len({r['origin_id'] for r in ledger}),'reserved_origin_rows':sum(r['reserved_final_evaluation'] for r in origins),'excluded_records':len(excluded),'exclusion_reasons':dict(Counter(r['reason'] for r in excluded)),'asof_conflicts':len(ties),'news_records':len(news),'news_timestamp_claims_parseable':sum(bool(r['normalized_publication_timestamp']) for r in news),'news_metadata_asof_rows':len(news_asof),'corporate_historical_inputs':0,'price_lag_availability_certified':False,'synthetic_research_observations_created':False,'annual_or_quarterly_values_disaggregated':False,'sentiment_features_computed':False,'models_trained':False,'stationarity_tests_run':False,'stage5_started':False,'reserved_outcomes_used_for_EDA_or_selection':False,'limits':['Sparse dated-factor coverage does not establish H1 or H2 forecasting feasibility.','Held known values are information-state records, never new monthly measurements.','Retrospective target acceptance does not certify historical price predictor publication.','Publisher timestamp metadata is not independent historical archive verification.']}
    (out/'metadata/integration_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--accepted',type=Path,required=True);p.add_argument('--accepted-manifest-sha256',required=True);p.add_argument('--approval-record',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--targets',type=Path,required=True);p.add_argument('--release-verification',type=Path,required=True);p.add_argument('--output',type=Path,required=True);run(p.parse_args())
