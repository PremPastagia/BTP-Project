"""Rebuild Stage 3 source records; no modeling, imputation, lags or monthly assembly."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, shutil
import pandas as pd
import pdfplumber
B=Path(__file__).resolve().parents[1]; Q=B/'quarantine/original_fd4e65b'
NOW=datetime.now(timezone.utc).isoformat(); ASOF='2026-11-05'; MONTH=ASOF[:7]
def save(df,rel):
 p=B/rel;p.parent.mkdir(parents=True,exist_ok=True);df.to_csv(p,index=False);df.to_parquet(p.with_suffix('.parquet'),index=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def metadata(df,source,raw,kind='observed',geo='global',freq='monthly'):
 df=df.copy();df['source_id']=source;df['source_url']='';df['raw_path']=str(raw.relative_to(B));df['raw_sha256']=sha(raw);df['value_class']=kind;df['geographical_grain']=geo;df['frequency']=freq;df['publication_release_date']=pd.NA;df['publication_status']='unknown';df['extraction_timestamp']=NOW;df['verification_status']='raw_reextracted_not_independently_verified';return df

def run():
 audit=[]
 for p in sorted(Q.rglob('*')):
  if not p.is_file():continue
  row={'path':str(p.relative_to(Q)),'bytes':p.stat().st_size,'sha256':sha(p),'format_status':'binary_preserved'}
  try:
   if p.suffix=='.csv':
    d=pd.read_csv(p);row.update(rows=len(d),columns=json.dumps(list(d.columns)),format_status='parsed')
   elif p.suffix=='.parquet':
    d=pd.read_parquet(p);row.update(rows=len(d),columns=json.dumps(list(d.columns)),format_status='parsed')
   elif p.suffix in ['.xls','.xlsx']:row.update(sheets=json.dumps(pd.ExcelFile(p).sheet_names),format_status='parsed')
   elif p.suffix=='.json':json.loads(p.read_text());row['format_status']='parsed'
   elif p.suffix=='.pdf':
    with pdfplumber.open(p) as pdf: row.update(pages=len(pdf.pages),format_status='parsed')
   else: p.read_text();row['format_status']='text_read'
  except Exception as e:row.update(format_status='parse_failed',error=str(e))
  audit.append(row)
 pd.DataFrame(audit).to_csv(B/'metadata/original_file_audit.csv',index=False)
 # Preserve all rows as observations; a date attached to a sampled point is not a verified effective date.
 raw=Q/'structured/price_revisions/discrete_revisions.csv';obs=pd.read_csv(raw).sort_values(['city','observation_date'],kind='stable')
 obs['source_observation_id']=[f'MPP-{i:05}' for i in range(len(obs))]
 obs['claimed_effective_date']=obs['effective_date'];obs['claimed_publication_date']=obs['publication_release_date']
 obs['effective_date']=pd.NA;obs['publication_release_date']=pd.NA
 obs['publication_status']='unknown';obs['effective_date_status']='unverified_sample_date'
 obs['source']='MyPetrolPrice secondary chart feed';obs['source_id']='MPP_LEGACY'
 obs['source_url']=obs.city.str.lower().map(lambda c:f'raw/cng_prices/{c}_raw_response.html')
 obs['raw_path']=obs['source_url'];ids={'Delhi':2,'Mumbai':3,'Pune':7,'Ahmedabad':10,'Lucknow':25,'Kanpur':292,'Hyderabad':8,'Bengaluru':6,'Noida':38,'Gurgaon':40};obs['source_url']=obs.city.map(lambda c:f'https://www.mypetrolprice.com/FuelHistoryDataServing.aspx?LocationId={ids[c]}&Span=1000&selectedFuels=3H&HikeChartId=FuelHikeChartDetails');obs['raw_sha256']=obs['raw_path'].map(lambda p:sha(B/p))
 obs['value_class']='unverified';obs['verification_status']='requires_primary_crosscheck'
 prev=obs.groupby('city').cng_price.shift();obs['record_type']='repeat_observation'
 obs.loc[prev.isna(),'record_type']='initial_observation'
 obs.loc[prev.notna() & obs.cng_price.ne(prev),'record_type']='candidate_price_change'
 obs['previous_observed_price']=prev
 save(obs,'structured/price_revisions/source_observations.csv')
 changes=obs[obs.record_type.eq('candidate_price_change')].copy()
 save(changes,'structured/price_revisions/discrete_revisions.csv')
 panel=pd.read_csv(Q/'structured/price_revisions/cng_monthly_panel.csv')
 incomplete=panel[panel.year_month.ge(MONTH)].copy();save(incomplete,'quarantine/incomplete_monthly_targets.csv')
 panel=panel[panel.year_month.lt(MONTH)].copy()
 panel['cng_price_monthend']=pd.NA;panel['cng_price_twap']=pd.NA;panel['revisions_in_month']=pd.NA
 for c in ['min_price_month','max_price_month','publication_release_date']:panel[c]=pd.NA
 panel['target_status']='unresolved_effective_price_path';panel['publication_status']='unknown';panel['value_class']='unverified'
 save(panel,'structured/price_revisions/cng_monthly_panel.csv')
 coverage=[]
 for city,g in obs.groupby('city'):
  m=panel[panel.city.eq(city)]; span=pd.period_range(m.year_month.min(),m.year_month.max(),freq='M')
  coverage.append(dict(city=city,state=g.state.iloc[0],cgd_operator=g.cgd_operator.iloc[0],operator_verification='legacy_mapping_needs_dated_GA_check',source_observation_start=g.observation_date.min(),source_observation_end=g.observation_date.max(),source_observations=len(g),repeat_observations=int(g.record_type.eq('repeat_observation').sum()),candidate_changes=int(g.record_type.eq('candidate_price_change').sum()),constructed_complete_month_rows=len(m),constructed_calendar_missing_months=len(set(map(str,span))-set(m.year_month)),verified_monthend_targets=0,verified_twap_targets=0,verified_revision_history='not_established',city_selection='candidate_only'))
 pd.DataFrame(coverage).to_csv(B/'metadata/city_coverage_matrix.csv',index=False)
 # Existing mixed-grain outputs cannot be repaired by shifting or removing a few rows.
 for name in ['demand_factors_monthly','external_shocks_monthly','external_shocks_daily']:
  old=pd.read_csv(Q/f'structured/numerical_factors/{name}.csv')
  # Replace unsafe mixed tables with an explicit quarantine pointer, never model-ready numbers.
  save(pd.DataFrame([{'dataset':name,'status':'quarantined','reason':'synthetic_or_filled_or_mixed_grain_values','preserved_original':f'quarantine/original_fd4e65b/structured/numerical_factors/{name}.csv'}]),f'structured/numerical_factors/{name}.csv')
 # Actual GDP retained at source annual grain, all 66 periods including missing.
 p=B/'raw/macro_weather/gdp_india_wb.json';j=json.loads(p.read_text());d=pd.DataFrame(j[1]);d=d[['date','value','obs_status']].rename(columns={'date':'year','value':'gdp_constant_2015_usd'})
 d=metadata(d,'WB_GDP',p,geo='India',freq='annual');d['source_url']='https://api.worldbank.org/v2/country/IND/indicator/NY.GDP.MKTP.KD?format=json&per_page=1000';d['source_lastupdated']=j[0]['lastupdated'];save(d,'structured/numerical_factors/gdp_annual_source_records.csv')
 # Extract original frequency without extending, filling or constructing publication dates.
 p=B/'raw/macro_weather/cpi_imf_raw.json';j=json.loads(p.read_text())['series']['docs'][0]
 d=pd.DataFrame({'period':j['period'],'cpi_source_value':j['value']});d['source_value_token']=d.cpi_source_value.astype(str);d['cpi_source_value']=pd.to_numeric(d.cpi_source_value,errors='coerce');d=metadata(d,'DBNOMICS_IMF_CPI',p,geo='India');d['source_url']='https://api.db.nomics.world/v22/series/IMF/CPI/M.IN.PCPI_IX?observations=1';save(d,'structured/numerical_factors/cpi_source_records.csv')
 p=B/'raw/macro_weather/usdinr_monthly_raw.json';j=json.loads(p.read_text())['chart']['result'][0]
 d=pd.DataFrame({'source_timestamp':j['timestamp'],'usd_inr_monthly_close':j['indicators']['quote'][0]['close']});d['observation_date']=pd.to_datetime(d.source_timestamp,unit='s',utc=True).dt.strftime('%Y-%m-%d');d=metadata(d,'YAHOO_USDINR',p,kind='proxy',geo='India');d['source_url']='https://query1.finance.yahoo.com/v8/finance/chart/INR=X?range=15y&interval=1mo';d['definition_note']='Monthly bar close, NOT monthly mean; final partial bar remains provisional';save(d,'structured/numerical_factors/usdinr_source_bars.csv')
 # Archive captures are evidence locators, not news publication records.
 d=pd.read_csv(Q/'structured/news/news_archive_metadata.csv');d['publication_release_date']=pd.NA;d['record_type']='website_capture_not_article';d['publication_status']='unknown';d['value_class']='unverified';save(d,'structured/news/news_archive_metadata.csv')
 # Historical policy assertions retained but unverified until source documents are attached.
 d=pd.read_csv(Q/'structured/policy_events/regulatory_timeline.csv');d['claimed_publication_date']=d.publication_release_date;d['publication_release_date']=pd.NA;d['verification_status']='unverified_legacy_assertion';save(d,'structured/policy_events/regulatory_timeline.csv')
 # Repair corporate ingestion from actual PDF; document date is not exchange dissemination timestamp.
 p=B/'documents/annual_reports/IGL_Reduction_Domestic_Gas_Allocation_Nov2024.pdf'
 with pdfplumber.open(p) as pdf:text='\n'.join(pg.extract_text() or '' for pg in pdf.pages)
 out=B/'documents/corporate_disclosures';out.mkdir(exist_ok=True);shutil.copy2(p,out/p.name);(out/p.with_suffix('.txt').name).write_text(text)
 d=pd.DataFrame([dict(disclosure_id='IGL-2024-11-15-ALLOCATION',company='IGL',document_type='exchange_disclosure',document_date='2024-11-15',event_effective_date='2024-11-16',fact='Domestic allocation approx 20% less than previous allocation',allocation_reduction_relative_pct=20,reported_apm_usd_mmbtu=6.5,publication_release_date='',publication_status='document_date_only_exchange_time_unknown',source_id='IGL_LOCAL_DISCLOSURE',source_url='',raw_path=str(p.relative_to(B)),raw_sha256=sha(p),verification_status='text_verified_in_existing_pdf_origin_url_pending',value_class='observed_company_disclosure',geographical_grain='company',extraction_timestamp=NOW)])
 save(d,'structured/corporate_disclosures/corporate_disclosures_metadata.csv')
 # Disable legacy writes; preserved originals remain available for code audit.
 for p in (B/'scripts').glob('0[1-5]_*.py'):
  p.write_text('"""Disabled unsafe legacy pipeline; original retained under quarantine/original_fd4e65b/scripts/."""\nraise SystemExit("Stage 3: use recover_repository.py, retrieve_sources.py, extract_verified_sources.py and validate_stage3.py; legacy writes are disabled.")\n')
 print(json.dumps({'audited_files':len(audit),'observations':len(obs),'repeats':int(obs.record_type.eq('repeat_observation').sum()),'candidate_changes':len(changes),'excluded_incomplete_targets':len(incomplete),'retained_unresolved_months':len(panel)}))
if __name__=='__main__':run()
