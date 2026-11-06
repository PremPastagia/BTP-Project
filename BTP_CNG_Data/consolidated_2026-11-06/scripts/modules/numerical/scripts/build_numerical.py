"""Stage 3 native-frequency evidence ledger; no analytical joining or imputation."""
from pathlib import Path
import csv, json, hashlib, math, re, collections, datetime, functools, zoneinfo, os
from decimal import Decimal

OUT=Path(__file__).resolve().parents[1]
ROOT=Path(os.environ.get('BTP_PROJECT_ROOT',str(OUT.parents[1]))).resolve()
FRESH=ROOT/'BTP/BTP_CNG_Fresh_2026-11-06'
PR=ROOT/'Stage3_GitHub_Audit_2026-11-06/snapshots/github-pr1/BTP_CNG_Data'
for n in ['structured','metadata','logs']: (OUT/n).mkdir(parents=True,exist_ok=True)
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
@functools.lru_cache(maxsize=None)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,rs,fields=None):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    fields=fields or list(dict.fromkeys(k for r in rs for k in r))
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs)
def dump(name,x):(OUT/name).write_text(json.dumps(x,indent=2,ensure_ascii=False,default=str))

# Recheck bytes rather than trusting the prior audit as an authenticity oracle.
hashpaths=collections.defaultdict(list)
for r in json.loads((ROOT/'Stage3_GitHub_Audit_2026-11-06/local_inventory.json').read_text()):
    p=ROOT/r['path']
    if p.is_file():hashpaths[r['sha256']].append(p)
for base in [ROOT/'Stage3_Consolidated_2026-11-06/evidence',OUT/'raw']:
    if base.exists():
        for p in base.rglob('*'):
            if p.is_file() and p.suffix.lower() in ['.pdf','.xlsx','.xls','.json','.html','.response']:hashpaths[sha(p)].append(p)
verified={};source_registry=[]
def resolve(h):
    if h in verified:return verified[h]
    for p in hashpaths.get(h,[]):
        if sha(p)==h:verified[h]=str(p.relative_to(ROOT));return verified[h]
    verified[h]='';return ''

manifests={}
for leaf in ['numerical','supplemental']:
    manifests[leaf]={r['source_id']:r for r in json.loads((FRESH/leaf/'manifest.json').read_text()) if r.get('sha256')}
source_tables=[];ledger=[];missing=[];aliases=[];invalid=[]
def add(table,index,r,family,series,period,value,unit,geography,frequency,source=None,extra=None):
    if value in ('',None,'NA','nan'):return
    try:
        if not math.isfinite(float(value)):raise ValueError('nonfinite')
    except (ValueError,TypeError):invalid.append({'table':str(table.relative_to(ROOT)),'row':index,'field':series,'value':value});return
    source=source or {}
    h=source.get('sha256',r.get('raw_sha256',''))
    raw=resolve(h) if h else ''
    base={'family':family,'series':series,'geography':geography,'frequency':frequency,'period':period,'period_end':r.get('period_end',r.get('effective_end_date','')),'value':str(value),'unit':unit,'source_id':r.get('source_id',''),'source_url':source.get('url',r.get('source_url','')),'raw_sha256':h,'raw_file':raw,'source_locator':r.get('source_locator',r.get('source_page','')),'reference_period_raw':r.get('period_raw',r.get('period',r.get('observation_period',r.get('month',r.get('year',''))))),'effective_date':r.get('effective_date',''),'effective_end_date':r.get('effective_end_date',''),'publication_date':r.get('publication_date',r.get('publication_release_date','')),'publication_basis':r.get('publication_date_basis','unknown_unless_explicit'),'retrieved_at':r.get('retrieved_at',r.get('extraction_timestamp',source.get('retrieved_at',''))),'value_status':r.get('value_type',r.get('verified_status',r.get('value_class','source_claim'))),'availability_status':'historical_release_unknown','verification_status':r.get('verified_status',r.get('verification_status','source_table_extraction_not_independently_verified')),'definition_note':r.get('definition_note',r.get('notes',''))}
    if extra:base.update(extra)
    if base['publication_date']:base['availability_status']='publication_date_recorded_not_yet_independent_release_validation'
    origin={'input_table':str(table.relative_to(ROOT)),'input_table_sha256':sha(table),'input_row':index,'source_locator':base['source_locator']}
    base['input_origins']=json.dumps([origin],sort_keys=True)
    key=[h,series,geography,frequency,period,base['period_end'],unit,base['effective_date']]
    base['record_key']=hashlib.sha256(json.dumps(key).encode()).hexdigest()[:24]
    base['observation_id']=hashlib.sha256(json.dumps(key+[str(value)]).encode()).hexdigest()[:24]
    if not raw:
        missing.append({**origin,'raw_sha256':h,'source_url':base['source_url'],'series':series,'reason':'original_raw_bytes_not_present_or_hash_mismatch','value':value});return
    ledger.append(base)

fresh_tables=['energy_benchmarks_monthly','geopolitical_risk_monthly','india_macro_annual_wdi','usd_inr_daily_federal_reserve','gas_supply_monthly_ppac','gas_sectoral_monthly_ppac','cgd_infrastructure_snapshots_ppac','apm_notified_monthly','gas_notified_intervals']
families=['energy_benchmarks','geopolitical_risk','macro_annual','fx_daily','gas_supply','gas_sectoral_consumption','infrastructure_snapshots','gas_price_candidate','gas_price_candidate']
for name,family in zip(fresh_tables,families):
    table=FRESH/f'numerical/structured/{name}.csv';rs=rows(table)
    source_tables.append({'dataset':name,'path':str(table.relative_to(ROOT)),'sha256':sha(table),'rows':len(rs),'scope':'fresh','role':'native_observations_or_flagged_transcriptions'})
    for i,r in enumerate(rs,2):
        src=manifests['numerical'].get(r['source_id'],{})
        series=r['series'];period=r.get('period',r.get('observation_date',r.get('effective_date','')))
        unit=r['unit'];geo=r.get('geography','India');frequency=r['frequency'];note=r.get('definition_note','')
        if family=='gas_price_candidate':
            # Preserve the two parsers as role-specific candidates, not invoiced costs.
            series='fresh_monthly:'+series if name=='apm_notified_monthly' else 'fresh_interval:'+series+':clause_'+r['price_clause_index']
        if family=='gas_sectoral_consumption':series+=':'+r['sector']+':'+r['component']
        if family=='gas_supply':series+=':'+r['component']
        add(table,i,r,family,series,period,r['value'],unit,geo,frequency,src)
for name in ['weather_monthly','gdp_pfce_quarterly']:
    table=FRESH/f'supplemental/{name}.csv';rs=rows(table);source_tables.append({'dataset':name,'path':str(table.relative_to(ROOT)),'sha256':sha(table),'rows':len(rs),'scope':'fresh_supplemental','role':'native_observations'})
    for i,r in enumerate(rs,2):
        if name=='weather_monthly':family='weather_aggregates';series=r['series'];period=r['period'];geo=r['geography'];freq='monthly';extra={}
        else:family='national_accounts_quarterly';series=r['variable']+':'+r['price_basis'];period=r['period_start'];geo='India';freq='quarterly';extra={'definition_note':'Official June 2026 vintage, base '+r['base_year']+'; retrospective revisions are not earlier-quarter available predictors.'}
        add(table,i,r,family,series,period,r['value'],r['unit'],geo,freq,manifests['supplemental'].get(r['source_id'],{}),extra)

# PR1 native tables add genuine series and vintages, never unsafe legacy joins.
specs=[('cpi_source_records','cpi_source_value','IMF_CPI_PCPI_IX','period','index_2012_reference_period','macro_monthly'),('gdp_annual_source_records','gdp_constant_2015_usd','WorldBank_GDP_constant_2015_USD','year','constant_2015_USD','macro_annual'),('usdinr_source_bars','usd_inr_monthly_close','Yahoo_USDINR_monthly_bar_close','observation_date','INR_per_USD','fx_monthly_proxy')]
for name,value,series,date,unit,family in specs:
    table=PR/f'structured/numerical_factors/{name}.csv';rs=rows(table);source_tables.append({'dataset':name,'path':str(table.relative_to(ROOT)),'sha256':sha(table),'rows':len(rs),'scope':'github_pr1','role':'native_source_records'})
    for i,r in enumerate(rs,2):
        period=r[date]
        if family=='fx_monthly_proxy':
            raw_path=resolve(r['raw_sha256'])
            payload=json.loads((ROOT/raw_path).read_text()) if raw_path else {}
            timezone=payload.get('chart',{}).get('result',[{}])[0].get('meta',{}).get('exchangeTimezoneName')
            if not timezone:invalid.append({'table':str(table.relative_to(ROOT)),'row':i,'field':series,'value':r[value],'reason':'source_exchange_timezone_unavailable'});continue
            period=datetime.datetime.fromtimestamp(int(r['source_timestamp']),zoneinfo.ZoneInfo(timezone)).strftime('%Y-%m')
            r['definition_note']=r.get('definition_note','')+' Native bar month decoded from original Unix timestamp using source-declared '+timezone+' timezone; original UTC-derived label='+r[date]+'. No mean/close conversion.'
            if period>='2026-11':invalid.append({'table':str(table.relative_to(ROOT)),'row':i,'field':series,'value':r[value],'reason':'incomplete_November_bar_excluded'});continue
        add(table,i,r,family,series,period,r[value],unit,'India',r['frequency'])

mospi_manifest=OUT/'logs/mospi_cpi_acquisition_manifest.json'
if mospi_manifest.exists():
    months={m.lower():i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}
    for receipt in json.loads(mospi_manifest.read_text()):
        if not receipt.get('records'):continue
        table=OUT/receipt['raw_file'];payload=json.loads(table.read_text())
        source_tables.append({'dataset':'MoSPI_CPI_'+receipt['query_year']+'_base_'+receipt['query_base'],'path':str(table.relative_to(ROOT)),'sha256':sha(table),'rows':len(payload['data']),'scope':'new_official_API','role':'native_monthly_latest_vintage'})
        for i,r in enumerate(payload['data']):
            if not (r.get('state')=='All India' and r.get('sector')=='Combined' and r.get('group')=='General' and r.get('subgroup')=='General-Overall'):
                invalid.append({'table':str(table.relative_to(ROOT)),'row':i,'field':'CPI','value':r.get('index'),'reason':'requested_dimensions_not_confirmed'});continue
            month=months.get(str(r.get('month','')).lower())
            if not month:continue
            period=f"{int(r['year']):04d}-{month:02d}"
            if period>='2026-11':continue
            transformed={'source_id':'MoSPI_CPI_'+receipt['query_year']+'_base_'+receipt['query_base'],'period':period,'source_locator':f'JSON data[{i}]','value_type':'official_API_status_'+str(r.get('status','unknown')),'verified_status':'source_API_dimensions_confirmed_historical_vintage_unknown','retrieved_at':receipt['retrieved_at'],'definition_note':'All India Combined General Overall CPI. API-reported base '+str(r['baseyear'])+'. Current API vintage; no historical publication/revision date supplied.'}
            add(table,i+1,transformed,'official_cpi_monthly','MoSPI_CPI_AllIndia_Combined_General_base_'+str(r['baseyear']),period,r['index'],'index_base_'+str(r['baseyear'])+'_100','India','monthly',{'sha256':receipt['raw_sha256'],'url':receipt['url']})
table=PR/'structured/numerical_factors/worldbank_energy_native_monthly.csv';rs=rows(table)
units={r['series']:r['unit'] for r in rows(FRESH/'numerical/structured/energy_benchmarks_monthly.csv')}
source_tables.append({'dataset':'worldbank_energy_native_monthly','path':str(table.relative_to(ROOT)),'sha256':sha(table),'rows':len(rs),'scope':'github_pr1','role':'distinct_source_workbook_vintage'})
for i,r in enumerate(rs,2):
    for series in ['Crude oil, average','Crude oil, Brent','Crude oil, Dubai','Crude oil, WTI','Natural gas, US','Natural gas, Europe','Liquefied natural gas, Japan']:
        add(table,i,r,'energy_benchmarks',series,r['observation_period'].replace('M','-'),r[series],units[series],'International benchmark','monthly')

table=PR/'structured/numerical_factors/gpr_native_monthly.csv';rs=rows(table)
source_tables.append({'dataset':'gpr_native_monthly','path':str(table.relative_to(ROOT)),'sha256':sha(table),'rows':len(rs),'scope':'github_pr1','role':'same_raw_vintage_focus_series_overlap; auxiliary country/codebook columns retained in original raw source'})
gpr_definitions={r['series']:(r['unit'],r['geography']) for r in rows(FRESH/'numerical/structured/geopolitical_risk_monthly.csv')}
for i,r in enumerate(rs,2):
    for series,(unit,geo) in gpr_definitions.items():
        add(table,i,r,'geopolitical_risk',series,r['month'][:7],r.get(series,''),unit,geo,'monthly')

# Keep the unreviewed PPAC transcriptions out of verified numerical observations.
for name in ['ppac_price_transcriptions','ppac_gas_supply_transcriptions']:
    table=PR/f'structured/numerical_factors/{name}.csv';rs=rows(table)
    source_tables.append({'dataset':name,'path':str(table.relative_to(ROOT)),'sha256':sha(table),'rows':len(rs),'scope':'github_pr1','role':'unverified_transcription_candidates'})
    for i,r in enumerate(rs,2):
        if name=='ppac_gas_supply_transcriptions':
            add(table,i,r,'gas_supply_candidate',r['metric'],r['period_raw'],r['value'],r['unit'],r['geographical_grain'],'source_period_label',extra={'verification_status':'candidate_text_regex_requires_semantic_table_review'})
        else:
            for field in ['notified_price_usd_mmbtu','nomination_ceiling_usd_mmbtu']:
                add(table,i,r,'gas_price_candidate','PR1_OCR:'+field,r['period_start'],r[field],r['unit'],r['geographical_grain'],'notified_interval',extra={'verification_status':'candidate_OCR_requires_visual_role_period_review','period_end':r['period_end'],'effective_date':r['period_start'],'effective_end_date':r['period_end']})

# Deduplication is source/version aware. Different values for one key are conflicts,
# and neither side is silently chosen. Multiple extraction origins remain auditable.
bykey=collections.defaultdict(list)
for r in ledger:bykey[r['record_key']].append(r)
canonical=[];conflicts=[];duplicates=[]
for key,rs in bykey.items():
    vals=collections.defaultdict(list)
    # A source claim differing at any reported decimal digit is a conflict.
    # Normalize representation only (e.g. 1.0 == 1), never round to a tolerance.
    for r in rs:vals[Decimal(r['value'])].append(r)
    if len(vals)>1:
        for r in rs:conflicts.append({**r,'conflict_reason':'same_source_version_series_period_unit_different_value'})
        continue
    first=rs[0];origins=[]
    for r in rs:origins.extend(json.loads(r['input_origins']))
    first['input_origins']=json.dumps(origins,sort_keys=True);canonical.append(first)
    for r in rs[1:]:duplicates.append({'canonical_observation_id':first['observation_id'],'record_key':key,'duplicate_input_origins':r['input_origins'],'reason':'same_source_version_and_key_same_numeric_value'})
fields=list(canonical[0])
active=[r for r in canonical if not r['family'].endswith('_candidate')]
candidates=[r for r in canonical if r['family'].endswith('_candidate')]
write('structured/native_numerical_observations.csv',active,fields)
write('structured/unverified_transcription_candidates.csv',candidates,fields)
write('metadata/missing_raw_lineage.csv',missing,['input_table','input_table_sha256','input_row','source_locator','raw_sha256','source_url','series','reason','value'])
write('metadata/excluded_records.csv',invalid,['table','row','field','value','reason'])
write('metadata/duplicate_aliases.csv',duplicates,['canonical_observation_id','record_key','duplicate_input_origins','reason'])
write('metadata/conflicts.csv',conflicts,fields+['conflict_reason'])
write('metadata/source_tables.csv',source_tables)
source_rows={}
for r in canonical:
    key=(r['raw_sha256'],r['source_url'])
    source_rows[key]={'raw_sha256':r['raw_sha256'],'raw_file':r['raw_file'],'source_url':r['source_url'],'source_id':r['source_id'],'bytes':(ROOT/r['raw_file']).stat().st_size,'verification':'local_SHA256_rechecked','historical_release_limitation':'Actual historical availability is not established by retrieval date or current archive vintage.'}
write('metadata/source_registry.csv',list(source_rows.values()))
coverage=[]
for group,rs in __import__('itertools').groupby(sorted(canonical,key=lambda r:(r['family'],r['series'],r['geography'],r['unit'],r['raw_sha256'])),lambda r:(r['family'],r['series'],r['geography'],r['unit'],r['raw_sha256'])):
    rs=list(rs);coverage.append(dict(zip(['family','series','geography','unit','raw_sha256'],group))|{'rows':len(rs),'first_period':min(r['period'] for r in rs),'last_period':max(r['period'] for r in rs),'publication_dates_missing':sum(not r['publication_date'] for r in rs),'scope':'first/last source labels do not establish continuous coverage','candidate_only':group[0].endswith('_candidate')})
write('metadata/coverage.csv',coverage)
definitions={'observation_id':'Source-version-aware identifier including reported value.','record_key':'SHA256 prefix of raw hash, variable, geography, native frequency/period, interval end, unit and effective date.','raw_sha256':'SHA256 of unchanged original source bytes, rechecked locally.','raw_file':'Existing original raw file path relative to ME BTP; no duplicate copies created.','publication_date':'Source-recorded release/date claim only; blanks remain unknown.','input_origins':'JSON list of extracted input table hashes and original CSV row numbers.','value':'Reported numerical value retained without interpolation, fill or frequency conversion.','availability_status':'Records whether a release-date claim exists; not certification of historical point-in-time usability.'}
write('metadata/data_dictionary.csv',[{'field':f,'definition':definitions.get(f,'Explicit source label or extraction metadata; consult original source and input origin.'),'missing_meaning':'unknown/not supplied; never interpreted as zero'} for f in fields])
summary={'built_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'active_native_rows':len(active),'unverified_candidate_rows':len(candidates),'source_hashes_verified':len({r['raw_sha256'] for r in canonical}),'duplicates_suppressed':len(duplicates),'conflicting_rows_excluded':len(conflicts),'missing_raw_rows_excluded':len(missing),'invalid_or_incomplete_rows_excluded':len(invalid),'family_counts':dict(collections.Counter(r['family'] for r in canonical)),'stage3_complete':False,'stage4_started':False,'accepted_data':False,'limitations':['Historical publication/revision vintages remain largely unknown.','IMF/DBnomics CPI is not official MoSPI real-time CPI vintage evidence.','No company procurement-cost or sourcing-share panel, VAHAN observed registrations or verified historical city-CNG consumption acquired.','PPAC OCR/text role transcriptions remain candidates until substantive source review.','Version-specific overlaps are retained deliberately; counts across vintages are not unique economic observations.','No model matrices, monthly joins, lags, statistical EDA or forecasts generated.']}
dump('logs/build_summary.json',summary)
print(json.dumps(summary,indent=2))
