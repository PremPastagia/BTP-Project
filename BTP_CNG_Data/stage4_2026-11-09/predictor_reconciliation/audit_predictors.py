"""Stage 4 predictor/corpus reconciliation; no outcome statistics or models."""
from pathlib import Path
from collections import defaultdict,Counter
from decimal import Decimal,InvalidOperation
from datetime import datetime,timezone
import argparse,subprocess,csv,io,json,hashlib,re,ast,urllib.parse

TARGETS={'cng_price_monthend','cng_price_twap','min_price_month','max_price_month','revisions_in_month','days_observed','days_in_month','is_complete_month','target_status'}
META={'year_month','city','state','cgd_operator','observation_date','publication_release_date','publication_verification_status','extraction_timestamp','gdp_representation','apm_pricing_regime','ppac_notification_reference','ppac_notification_date','vahan_data_status','vahan_source','observation_year','frequency','unit','source_id','source_name','release_lag_days','data_status'}
DIRS=['numerical_factors','policy_events','news','corporate_disclosures']
def digest(b):return hashlib.sha256(b).hexdigest()
def parse(b):
    s=b.decode('utf-8-sig');rd=csv.DictReader(io.StringIO(s))
    # Strip outcome-valued fields before storing or comparing audit records.
    return rd.fieldnames or [],[{k:v for k,v in row.items() if k not in TARGETS} for row in rd]
def read(p):return parse(p.read_bytes())[1]
def write(p,rs,fields):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs)
def urlkey(u):
    p=urllib.parse.urlsplit(u);return urllib.parse.urlunsplit((p.scheme.lower(),p.netloc.lower().removeprefix('www.'),p.path.rstrip('/'),p.query,''))
def number(v):
    try:return Decimal(v)
    except (InvalidOperation,TypeError):return None

def audit(a):
    out=a.output;registry=out/'registry/S4-PRED-RECON-20261109-001.json';assert registry.is_file(),'Preregister before executing audit'
    inputs=[];versions={};schemas=[];filegroups=defaultdict(list);availability=[]
    def add_input(version,name,b,locator):
        h=digest(b);inputs.append({'version':version,'path':name,'locator':locator,'sha256':h,'bytes':len(b)});filegroups[h].append(version+':'+name)
        if name.endswith('.csv'):
            columns,rs=parse(b);versions.setdefault(version,{})[name]=rs
            schemas.append({'version':version,'path':name,'rows':len(rs),'columns':json.dumps(columns),'duplicate_nonoutcome_record_rows':len(rs)-len({json.dumps(x,sort_keys=True) for x in rs}),'data_role':'audit_only_not_analysis_input'})
        return b
    # Frozen commits remain distinguished from modified local copies.
    for version,ref in [('git_6b08b99','6b08b99666ef2b08605c63499418503a4d666c3b'),('git_2c2e3b9','2c2e3b9a582b978a40575756e1aa94199bc1f5b9'),('git_4d4959c','4d4959cc5659c34989a32cc1902622b28a47e429')]:
        tree=subprocess.check_output(['git','-C',str(a.repo),'ls-tree','-r','--name-only',ref],text=True).splitlines()
        for name in tree:
            if any(name.startswith('BTP_CNG_Data/structured/'+d+'/') for d in DIRS) and name.endswith('.csv'):
                b=subprocess.check_output(['git','-C',str(a.repo),'show',ref+':'+name]);add_input(version,name,b,'git:'+ref+':'+name)
    for version,base in [('modified_desktop_legacy',a.desktop_legacy),('working_repository_legacy',a.repo/'BTP_CNG_Data'),('quarantined_repository_legacy',a.repo/'BTP_CNG_Data/quarantine/legacy_main'),('pr1_snapshot',a.pr1)]:
        if not base.exists():availability.append({'version':version,'status':'inaccessible','path':str(base)});continue
        availability.append({'version':version,'status':'accessible','path':str(base)})
        for d in DIRS:
            for p in sorted((base/'structured'/d).glob('*.csv')):add_input(version,'BTP_CNG_Data/'+str(p.relative_to(base)),p.read_bytes(),str(p))
    candidate=a.repo/'BTP_CNG_Data/consolidated_2026-11-06';accepted=a.repo/'BTP_CNG_Data/accepted_stage3_2026-11-06_restricted_v1';prior=a.repo/'BTP_CNG_Data/stage4_2026-11-06/integration'
    for version,base,patterns in [('accepted_reference',accepted,['reference/*.csv']),('consolidated',candidate,['structured/numerical_factors/*.csv','structured/news/*.csv','structured/corporate_disclosures/*.csv']),('prior_stage4_integration',prior,['*.csv'])]:
        for pattern in patterns:
            for p in sorted(base.glob(pattern)):add_input(version,str(p.relative_to(base)),p.read_bytes(),str(p))
    # Input source code is evidence of transformations, never executed.
    code={}
    for n in ['02_extract_external_shocks.py','03_extract_domestic_factors.py','04_ingest_disclosures_and_news.py']:
        p=a.desktop_legacy/'scripts'/n
        if p.is_file():code[n]=add_input('modified_desktop_legacy','scripts/'+n,p.read_bytes(),str(p)).decode()
        else:
            b=subprocess.check_output(['git','-C',str(a.repo),'show','6b08b99666ef2b08605c63499418503a4d666c3b:BTP_CNG_Data/scripts/'+n])
            code[n]=add_input('git_6b08b99','scripts/'+n,b,'git:6b08b99666ef2b08605c63499418503a4d666c3b:BTP_CNG_Data/scripts/'+n).decode()
    native=read(accepted/'reference/native_numerical_observations.csv');candidate_news=read(accepted/'reference/news_metadata.csv');corpus=read(accepted/'reference/corporate_document_metadata.csv')
    # Per-column inventory deliberately excludes ALL outcome-valued columns.
    dictionary=[]
    mappings={'brent_crude_usd':('energy_benchmarks','Crude oil, Brent','monthly'),'dubai_crude_usd':('energy_benchmarks','Crude oil, Dubai','monthly'),'wti_crude_usd':('energy_benchmarks','Crude oil, WTI','monthly'),'henry_hub_usd':('energy_benchmarks','Natural gas, US','monthly'),'ttf_gas_usd':('energy_benchmarks','Natural gas, Europe','monthly'),'lng_japan_usd':('energy_benchmarks','Liquefied natural gas, Japan','monthly'),'gpr_index':('geopolitical_risk','GPR','monthly'),'gprt_index':('geopolitical_risk','GPRT','monthly'),'gpra_index':('geopolitical_risk','GPRA','monthly'),'cpi_index_imf':('macro_monthly','IMF_CPI_PCPI_IX','monthly'),'cpi_index':('macro_monthly','IMF_CPI_PCPI_IX','monthly'),'usd_inr_mean':('fx_monthly_proxy','Yahoo_USDINR_monthly_bar_close','monthly'),'usd_inr_monthend':('fx_monthly_proxy','Yahoo_USDINR_monthly_bar_close','monthly')}
    native_lookup=defaultdict(list)
    for r in native:native_lookup[(r['family'],r['series'],r['period'])].append(r)
    matches=[]
    for version,tables in versions.items():
        for name,rs in tables.items():
            if '/numerical_factors/' not in name or not rs or 'year_month' not in rs[0]:continue
            for col in rs[0]:
                if col in TARGETS or col in META:continue
                nonempty=sum(r.get(col,'') not in ['',None] for r in rs)
                if 'vahan' in col:classification='unobserved_or_synthetic_never_analysis_input';decision='Exclude. Audit existence only; no synthetic values or summaries used.'
                elif col.endswith('_lag1'):classification='already_lagged_derived_not_availability_proof';decision='Do not double-lag or admit based on shift alone; reconstruct only after verified native release rules.'
                elif 'gdp' in col:classification='annual_value_mapped_or_held_on_monthly_grid';decision='Preserve annual native GDP; reject manufactured May31/151day release dates and current-vintage historical timing.'
                elif col in ['usd_inr_mean','usd_inr_monthend']:classification='monthly_Yahoo_close_not_mean_with_UTC_month_bug';decision='Source timestamp and Europe/London month must be decoded; mean label unsupported; historical releases unknown.'
                elif col=='ttf_gas_usd':classification='WorldBank_Europe_benchmark_mislabeled_TTF';decision='Use source-defined Europe benchmark, not an unsupported TTF spot identity; release vintages remain unknown.'
                elif 'vat' in col:classification='hardcoded_statutory_history_unverified';decision='Exclude until dated legal/source records and applicability establish observed regimes.'
                elif 'apm' in col or 'ceiling' in col:classification='handcoded_or_calculated_gas_price_role_unverified';decision='Use only independently extracted notification roles; never substitute caps for company cost.'
                elif any(t in col for t in ['ratio','spread']):classification='derived_crossfuel_price_feature';decision='Depends on unverified input prices/timing and on differing kg/litre units; no empirical admission now.'
                elif col.startswith(('petrol','diesel')):classification='retrospective_secondary_fuel_values_no_saved_native_provenance';decision='No independent source row/release lineage; do not accept closing-price copy or fills as observed TWAP.'
                else:classification='latest_vintage_grid_value_release_unverified';decision='Native source value may match, but current vintage/ffill and generic publication date do not establish as-of availability.'
                dictionary.append({'version':version,'dataset':name,'variable':col,'nonempty_cells':nonempty,'classification':classification,'geographic_grain':'city/operator-labelled' if 'city' in rs[0] else 'national_or_international_shared','native_frequency_required':'annual' if 'gdp' in col else 'source_frequency_not_monthly_grid_by_default','strict_historical_eligible':'False','decision':decision})
            if name.endswith('external_shocks_monthly.csv'):
                for r in rs:
                    for col,(family,series,freq) in mappings.items():
                        value=number(r.get(col,''))
                        if value is None:continue
                        candidates=native_lookup.get((family,series,r['year_month']),[])
                        exact=[x for x in candidates if number(x['value'])==value]
                        matches.append({'version':version,'legacy_dataset':name,'period':r['year_month'],'legacy_variable':col,'legacy_predictor_value':r[col],'native_series':series,'native_candidate_records':len(candidates),'exact_value_matches':len(exact),'matched_native_ids':json.dumps([x['observation_id'] for x in exact]),'matched_source_hashes':json.dumps(sorted({x['raw_sha256'] for x in exact})),'decision':'exact_value_agreement_not_release_validation' if exact else 'no_same_period_exact_value_match' if candidates else 'no_native_period_record_latest_hold_or_gap_possible','strict_historical_eligible':'False'})
    # Establish the legacy GDP release bug and forward-holds from actual code.
    transform_evidence=[]
    for filename,text in code.items():
        for lineno,line in enumerate(text.splitlines(),1):
            if any(x in line for x in ['release_date =','release_lag_days','publication_release_date','ffill()','bfill()','shift(1)','15000','np.exp','vat_history','publication_timestamp','pageno=1','news_dt =','NEWS_DT','IGL_Reduction_Domestic']):
                transform_evidence.append({'script':filename,'line':lineno,'source_text':line.strip(),'role':'source_code_evidence_not_executed'})
    # Inspect manually seeded news and timestamp/hash provenance without claiming
    # that a hand-authored excerpt equals original publisher text.
    news_code=ast.parse(code.get('04_ingest_disclosures_and_news.py',''));seed=[]
    for node in ast.walk(news_code):
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='articles' for t in node.targets):
            try:seed=ast.literal_eval(node.value)
            except Exception:pass
    seedbyid={r['article_id']:r for r in seed};candidate_by_url=defaultdict(list)
    for r in candidate_news:candidate_by_url[urlkey(r['source_url'])].append(r)
    reported=versions['git_6b08b99']
    oldnews=reported.get('BTP_CNG_Data/structured/news/news_archive_metadata.csv',[]);news_reconciliation=[]
    for r in oldnews:
        s=seedbyid.get(r['article_id']);payload=r['headline']+' '+r['content_excerpt'];matches_news=candidate_by_url.get(urlkey(r['article_url']),[])
        news_reconciliation.append({'legacy_article_id':r['article_id'],'source_url':r['article_url'],'legacy_timestamp':r['publication_timestamp_verified'],'timestamp_is_code_literal':bool(s and s.get('publication_timestamp')==r['publication_timestamp_verified']),'hash_is_authored_headline_excerpt':digest(payload.encode())==r['content_sha256_hash'],'same_URL_candidate_article_ids':json.dumps([x['article_id'] for x in matches_news]),'candidate_publication_claims':json.dumps([x['publication_date'] for x in matches_news]),'decision':'legacy_verified_label_rejected_hardcoded_claim_not_original_text_or_date_verification','strict_H2_eligible':'False'})
    # Corporate identities, pagination and the known October/November attachment
    # mismatch are checked independently against original bytes.
    oldcorp=reported.get('BTP_CNG_Data/structured/corporate_disclosures/corporate_disclosures_metadata.csv',[])
    attachments=Counter(r['attachment_filename'] for r in oldcorp if r['attachment_filename']);corporate=[];pdf_date_evidence=''
    pdf=a.desktop_legacy/'documents/annual_reports/IGL_Reduction_Domestic_Gas_Allocation_Nov2024.pdf'
    if not pdf.is_file():
        h=next((r['file_sha256_hash'] for r in oldcorp if r['is_downloaded_local'].lower()=='true'),'')
        matches=list((candidate/'raw/objects').glob(h+'.*')) if h else []
        if matches:pdf=matches[0]
    if pdf.is_file():
        b=pdf.read_bytes();inputs.append({'version':'legacy_linked_original_PDF','path':pdf.name,'locator':str(pdf),'sha256':digest(b),'bytes':len(b)})
        text=subprocess.check_output(['pdftotext','-layout',str(pdf),'-'],text=True);pdf_date_evidence='; '.join(l.strip() for l in text.splitlines() if re.search(r'Nov|2024',l,re.I))[:800]
    corpus_by_hash={r['raw_sha256']:r for r in corpus};allurls=defaultdict(list)
    for r in corpus:
        for u in json.loads(r['source_urls']):allurls[urlkey(u)].append(r['document_id'])
    for r in oldcorp:
        h=r['file_sha256_hash'];same=corpus_by_hash.get(h);published=r['dissemination_timestamp']
        special=r['is_downloaded_local'].lower()=='true' and 'Nov2024' in r['local_file_path'] and r['publication_release_date'].startswith('2024-10')
        corporate.append({'legacy_disclosure_id':r['disclosure_id'],'company':r['company_name'],'timestamp_claim':published,'timestamp_timezone_explicit':bool(re.search(r'(Z|[+-]\d{2}:?\d{2})$',published)),'attachment_filename':r['attachment_filename'],'same_attachment_metadata_rows':attachments.get(r['attachment_filename'],0),'downloaded_flag':r['is_downloaded_local'],'raw_sha256':h,'matched_native_document_id':same['document_id'] if same else '','raw_PDF_date_evidence':pdf_date_evidence if special else '','decision':'reject_timestamp_to_document_link_October_row_points_to_November_letter' if special else 'metadata_only_no_preserved_BSE_JSON_or_independent_exchange_publication_validation','strict_H2_eligible':'False'})
    policy=[]
    for version,tables in versions.items():
        name='BTP_CNG_Data/structured/policy_events/regulatory_timeline.csv'
        for r in tables.get(name,[]):policy.append({'version':version,'event_id':r.get('event_id',''),'effective_date_claim':r.get('effective_date',''),'publication_date_claim':r.get('publication_release_date',''),'event_name':r.get('policy_event_name',''),'official_reference_claim':r.get('official_gazette_ref',''),'decision':'code_defined_event_seed_requires_primary_document_and_public_release_verification','strict_historical_eligible':'False'})
    corpus_dictionary=[]
    for version,tables in versions.items():
        for name,rs in tables.items():
            if not any('/'+d+'/' in name for d in ['news','corporate_disclosures','policy_events']):continue
            if 'archive_record_id' in (rs[0] if rs else {}):kind='Wayback_homepage_capture_not_article'
            elif version=='modified_desktop_legacy' and '/news/' in name:kind='ten_hand_authored_news_policy_seeds_not_verified_corpus'
            elif '/corporate_disclosures/' in name:kind='corporate_metadata_not_equivalent_to_downloaded_dated_text'
            elif '/policy_events/' in name:kind='regulatory_event_claims_not_verified_date_history'
            else:kind='selected_timestamp_claim_metadata_only'
            corpus_dictionary.append({'version':version,'dataset':name,'records':len(rs),'evidence_kind':kind,'historical_use_rule':'Preserve original source and prove relevant public release time/version before empirical inputs; no representative volume or zero-event claims.','strict_H2_eligible':'False'})
    out.mkdir(parents=True,exist_ok=True)
    write(out/'input_hashes.csv',inputs,['version','path','locator','sha256','bytes'])
    write(out/'schema_inventory.csv',schemas,['version','path','rows','columns','duplicate_nonoutcome_record_rows','data_role'])
    write(out/'artifact_accessibility.csv',availability,['version','status','path'])
    write(out/'variable_eligibility_dictionary.csv',dictionary,list(dictionary[0]))
    write(out/'legacy_native_value_matches.csv',matches,list(matches[0]))
    write(out/'source_transformation_evidence.csv',transform_evidence,['script','line','source_text','role'])
    write(out/'news_reconciliation.csv',news_reconciliation,list(news_reconciliation[0]))
    write(out/'corporate_reconciliation.csv',corporate,list(corporate[0]))
    write(out/'policy_reconciliation.csv',policy,list(policy[0]))
    write(out/'corpus_eligibility_dictionary.csv',corpus_dictionary,list(corpus_dictionary[0]))
    duplicate_files=[{'sha256':h,'aliases':json.dumps(ps),'decision':'same_bytes_not_additional_evidence'} for h,ps in filegroups.items() if len(ps)>1]
    write(out/'exact_file_aliases.csv',duplicate_files,['sha256','aliases','decision'])
    counts={v:{p:len(rs) for p,rs in tables.items()} for v,tables in versions.items()}
    external=reported['BTP_CNG_Data/structured/numerical_factors/external_shocks_monthly.csv'];annual=reported['BTP_CNG_Data/structured/numerical_factors/macro_annual_gdp.csv']
    after2024=[r for r in external if r['year_month']>='2025-01'];dec=next(r for r in external if r['year_month']=='2024-12');fx=[r for r in external if r['usd_inr_mean'] and r['usd_inr_monthend']]
    defects={'source_version':'git_6b08b99','grid_months':len(external),'grid_start':min(r['year_month'] for r in external),'grid_end':max(r['year_month'] for r in external),'post2024_month_rows':len(after2024),'post2024_equal_to_Dec2024_value':{c:sum(r[c]==dec[c] for r in after2024) for c in ['brent_crude_usd','dubai_crude_usd','wti_crude_usd','henry_hub_usd','ttf_gas_usd','lng_japan_usd']},'FX_nonmissing_paired_rows':len(fx),'FX_mean_equals_monthend_rows':sum(r['usd_inr_mean']==r['usd_inr_monthend'] for r in fx),'annual_GDP_rows':len(annual),'annual_GDP_assigned_release_before_observation_year_end':sum(r['publication_release_date']<r['observation_date'] for r in annual),'interpretation':'Repetition alone is not proof of fabrication; source code independently shows .ffill(), identical close assignment, fixed May31 and shift rules. No causal or forecasting claims.'}
    (out/'legacy_construction_findings.json').write_text(json.dumps(defects,indent=2))
    result={'executed_at_utc':datetime.now(timezone.utc).isoformat(),'preregistration_sha256':digest(registry.read_bytes()),'actual_counts_by_version':counts,'predictor_columns_audited':len(dictionary),'legacy_native_cells_compared':len(matches),'exact_same_period_matches':sum(int(x['exact_value_matches'])>0 for x in matches),'legacy_news_seed_count':len(seed),'news_code_literal_timestamps':sum(r['timestamp_is_code_literal'] for r in news_reconciliation),'news_authored_payload_hash_matches':sum(r['hash_is_authored_headline_excerpt'] for r in news_reconciliation),'corporate_metadata_count':len(oldcorp),'corporate_unique_ids':len({r['disclosure_id'] for r in oldcorp}),'corporate_unique_nonempty_attachments':len(attachments),'corporate_download_flag_true':sum(r['is_downloaded_local'].lower()=='true' for r in oldcorp),'corporate_rows_by_company_year':dict(Counter(r['stock_symbol']+'_'+r['publication_release_date'][:4] for r in oldcorp)),'source_code_only_page_one':bool('pageno=1' in code.get('04_ingest_disclosures_and_news.py','')),'strict_new_H1_admissions_from_legacy_grid':0,'strict_new_H2_admissions_from_legacy_claims':0,'quarantined_synthetic_used':False,'future_holdout_outcome_values_analyzed_or_disclosed':False,'models_or_statistical_tests_run':False,'stage5_started':False,'limitations':['Counts refer to explicitly named versions; modified Desktop legacy data is not claimed frozen.','Exact predictor value matches do not verify publication timing or historical vintage.','The metadata-only BSE records may be useful retrieval leads; their page-one sampling and attachment linkage require correction before text forecasting.','Outcome-valued CSV fields are stripped before audit storage and comparison.']}
    (out/'audit_results.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='actual_counts_by_version'},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--desktop-legacy',type=Path,required=True);p.add_argument('--pr1',type=Path,required=True);p.add_argument('--output',type=Path,required=True);audit(p.parse_args())
