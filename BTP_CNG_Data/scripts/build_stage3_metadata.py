"""Inventory every agreed candidate and report evidence separately from verified values."""
from pathlib import Path
import csv,json,re,hashlib
import pandas as pd
from recover_repository import B,NOW,sha
from extract_verified_sources import catalog
GROUPS={
'2.1':['retail_prices','effective_revisions','procurement_cost','distribution_cost','compression_cost','transmission_cost','margins','tax_components'],
'2.2':['apm_prices','non_apm_domestic_prices','lng_imports','lng_prices','sourcing_mix','allocation_shares','blended_procurement_cost','domestic_production','domestic_supply_disruptions'],
'2.3':['cng_vehicle_registrations','cng_vehicle_stock','cng_consumption','station_counts','petrol_prices','diesel_prices','seasonal_transport_demand'],
'2.4':['apm_policy','allocation_policy','state_vat','central_duties','pipeline_tariffs','cgd_licensing','environmental_transport_regulations'],
'2.5':['operator_identity','geographical_areas','regional_sourcing','regional_taxes','pipeline_connectivity','distribution_infrastructure','local_demand'],
'2.6':['lng_benchmarks','crude_benchmarks','usd_inr','geopolitical_events','global_gas_demand','international_supply_interruptions','extreme_weather'],
'2.7':['news_sentiment','news_events','news_uncertainty','news_volume','pos_validated_collocations','news_forward_statements','source_credibility'],
'2.8':['corporate_procurement','corporate_financials','corporate_operations','management_tone','corporate_guidance','corporate_risks','report_novelty'],
'2.9':['management_bias','media_bias','duplicate_reporting','source_overlap','publication_timing','sentiment_errors','source_disagreements'],
'macro':['gdp','pfce','cpi']}
KEYS={'procurement':'procure','distribution':'distribution','compression':'compress','transmission':'transmission','margin':'margin','apm':'APM','non_apm':'non-APM','lng':'LNG','sourcing':'sourc','allocation':'allocat','production':'production','disruptions':'disrupt','vehicle':'vehicle','consumption':'consumption','station':'station','petrol':'petrol','diesel':'diesel','seasonal':'season','policy':'policy','vat':'VAT','duties':'excise','tariff':'tariff','licensing':'authoriz','environmental':'environment','operator':'entity','geographical':'geographical','pipeline':'pipeline','infrastructure':'infrastructure','demand':'demand','geopolitical':'geopolit','weather':'weather','risks':'risk','guidance':'outlook','financials':'financial','operations':'operation','procurement':'procure'}
DIRECT={
 'transmission_cost':('structured/price_revisions/pngrb_all_district_snapshots.csv','transmission_tariff_inr_kg','district_GA','observation_period'),
 'tax_components':('structured/price_revisions/pngrb_all_district_snapshots.csv','vat_inr_kg','district_GA_amount_not_rate','observation_period'),
'retail_prices':('structured/price_revisions/pngrb_all_district_snapshots.csv','retail_price_inr_kg','district_GA','observation_period'),
'effective_revisions':('structured/price_revisions/primary_price_histories.csv','cng_price','city_GA','effective_date'),
'distribution_cost':('structured/price_revisions/pngrb_all_district_snapshots.csv','supply_distribution_cost_inr_kg','district_GA','observation_period'),
'procurement_cost':('structured/price_revisions/pngrb_all_district_snapshots.csv','gas_cost_inr_kg','district_GA_reported_component','observation_period'),
'margins':('structured/price_revisions/pngrb_all_district_snapshots.csv','margin_inr_kg','district_GA','observation_period'),
'blended_procurement_cost':('structured/price_revisions/pngrb_all_district_snapshots.csv','gas_cost_inr_kg','district_GA_reported_component_not_contract_mix','observation_period'),
'apm_prices':('structured/numerical_factors/ppac_price_transcriptions.csv','notified_price_usd_mmbtu','India_regime','period_start'),
'lng_imports':('structured/numerical_factors/ppac_gas_supply_transcriptions.csv','value','India','period_raw'),
 'domestic_production':('structured/numerical_factors/ppac_gas_supply_transcriptions.csv','value','India','period_raw'),
 'lng_prices':('structured/numerical_factors/worldbank_energy_native_monthly.csv','Liquefied natural gas, Japan','global_proxy','observation_period'),
'lng_benchmarks':('structured/numerical_factors/worldbank_energy_native_monthly.csv','Liquefied natural gas, Japan','global_proxy','observation_period'),
'crude_benchmarks':('structured/numerical_factors/worldbank_energy_native_monthly.csv','Crude oil, Brent','global','observation_period'),
'usd_inr':('structured/numerical_factors/usdinr_source_bars.csv','usd_inr_monthly_close','India_proxy_not_RBI','observation_date'),
'gdp':('structured/numerical_factors/gdp_annual_source_records.csv','gdp_constant_2015_usd','India_annual','year'),
'cpi':('structured/numerical_factors/cpi_source_records.csv','cpi_source_value','India','period')}

def run():
 attempts,src=catalog();reg=[]
 for sid,r in src.items():
  p=B/r['raw_path']; status='downloaded_unparsed';note='Access success does not establish data completeness.'
  if p.stat().st_size==0:status='invalid_empty_response'
  elif p.suffix=='.html':
   t=p.read_text(errors='replace')
   if len(t)<5000 and any(x in t.lower() for x in ['javascript','enable','app-root','react']):status='javascript_shell_no_dataset'
  else:status='raw_file_downloaded'
  reg.append(dict(source_id=sid,original_url=r['url'],resolved_url=r.get('final_url',''),http_status=r.get('http_status',''),access_status=status,raw_path=r['raw_path'],sha256=r['sha256'],bytes=r['bytes'],extraction_timestamp=r['extraction_timestamp'],source_title=r.get('title',''),portal_listed_date=r.get('listed_upload_date',''),listed_publication_context=r.get('listed_publication_context',''),frequency='source_native_varies',coverage='see data_inventory and document/source records',licensing='not_verified_public_access_does_not_imply_open_licence',reliability=('primary_regulator_entity_submissions' if 'pngrb.gov.in' in r['url'] else 'primary_government' if any(x in r['url'] for x in ['ppac.gov.in','mopng.gov.in','pib.gov.in','sansad.in','imd.gov.in','rbi.org.in','mospi.gov.in']) else 'benchmark_provider_proxy' if 'worldbank.org' in r['url'] else 'academic_index_proxy' if 'iacoviello.com' in r['url'] else 'secondary_independent_publisher' if sid.startswith('NEWS_') else 'company_or_exchange_disclosure' if any(x in sid for x in ['ATGL','MNGL','GGL','IGL','MGL']) else 'access_catalogue_or_unclassified_requires_review'),verification_status='raw_retrieval_only',notes=note))
 for r in attempts:
  if not r.get('raw_path'):reg.append(dict(source_id=r['source_id'],original_url=r['url'],access_status='retrieval_failed',verification_status='unavailable_this_attempt',notes=r.get('error')))
 
 for sid,path,url in [('MPP_LEGACY','raw/cng_prices/delhi_raw_response.html','https://www.mypetrolprice.com/'),('WB_GDP','raw/macro_weather/gdp_india_wb.json','https://api.worldbank.org/v2/country/IND/indicator/NY.GDP.MKTP.KD'),('DBNOMICS_IMF_CPI','raw/macro_weather/cpi_imf_raw.json','https://api.db.nomics.world/v22/series/IMF/CPI/M.IN.PCPI_IX?observations=1'),('YAHOO_USDINR','raw/macro_weather/usdinr_monthly_raw.json','https://query1.finance.yahoo.com/v8/finance/chart/INR=X?range=15y&interval=1mo'),('IGL_LOCAL_DISCLOSURE','documents/annual_reports/IGL_Reduction_Domestic_Gas_Allocation_Nov2024.pdf','')]:
  reg.append(dict(source_id=sid,original_url=url,access_status='preserved_legacy_raw_not_refetched',raw_path=path,sha256=sha(B/path),bytes=(B/path).stat().st_size,licensing='unverified',verification_status='legacy_origin_and_publication_unresolved',notes='For MPP use row-specific raw files/hashes; registry example path does not represent all cities.'))
 pd.DataFrame(reg).to_csv(B/'metadata/source_registry.csv',index=False)
 # Search every downloaded text for potential evidence; keywords do not count as collected variables.
 docs=[]
 for p in (B/'documents/extracted').glob('*/*.txt'):
  docs.append((p.parent.name,p.read_text(errors='replace').lower()))
 news_path='structured/news/actual_article_metadata.csv';corp_path='structured/corporate_disclosures/corporate_disclosures_metadata.csv'
 inventory=[];evidence=[]
 for group,factors in GROUPS.items():
  for factor in factors:
   fid=group+'.'+factor;kw=next((v for k,v in KEYS.items() if k in factor),factor.replace('_',' '));matches=[sid for sid,t in docs if kw.lower() in t]
   for sid in matches:evidence.append(dict(factor_id=fid,source_id=sid,evidence_type='keyword_in_document_requires_semantic_verification',keyword=kw))
   path='';n=0;lo='';hi='';grain='unestablished';missing='No structured observations verified; historical coverage unknown.';status='not_collected';action='Retrieve source-native records; resolve period, unit and release date.'
   if factor in DIRECT:
    path,field,grain,date=DIRECT[factor];p=B/path
    if p.exists():
     d=pd.read_csv(p)
     if factor=='apm_prices':d=d[d.notification_type.eq('domestic_gas')]
     if factor in ['lng_imports','domestic_production']:d=d[d.metric.eq('lng_import_volume' if factor=='lng_imports' else 'domestic_gas_gross_production')]
     n=int(d[field].notna().sum()) if field in d else 0
     if date in d:
      v=d[date].dropna().astype(str);lo=v.min() if len(v) else '';hi=v.max() if len(v) else ''
     status='partially_collected_source_records';missing='Not a completeness claim; raw missing tokens, period gaps, publication dates and vintage coverage require review.'
   elif group in ['2.7','2.9']:
    path=news_path;n=len(pd.read_csv(B/path));grain='article';status='partial_input_corpus_no_text_indicators';action='Expand independent historical article coverage and verify publication, entities and syndicated duplicates. No sentiment or collocation features computed in Stage 3.'
   elif group=='2.8':
    path=corp_path;n=len(pd.read_csv(B/path));grain='company_document';status='partial_input_documents_no_text_indicators';action='Add remaining companies, quarterlies, calls and factual fields with exact exchange dissemination dates; no tone/bias features computed.'
   elif matches:status='candidate_document_evidence_not_variable_extracted'
   inventory.append(dict(factor_id=fid,stage2_group=group,factor=factor,status=status,structured_path=path,nonmissing_source_records=n,source_period_start=lo,source_period_end=hi,geographical_grain=grain,candidate_evidence_documents=len(matches),source_ids=';'.join(matches),missing_periods_and_limitations=missing,verification_status='NOT_STAGE3_COMPLETE',next_retrieval_action=action))
 
 for row in inventory:
  group=row['stage2_group'];provider={'2.1':'PNGRB price breakdowns; CGD historical notices; company reports','2.2':'PPAC gas monthly reports/notifications; MoPNG policy; CGD disclosures','2.3':'VAHAN fuel/state/RTO; PNGRB CGD MIS; PPAC fuel reports','2.4':'MoPNG policy/gazettes; PNGRB tariffs/authorisations; state tax gazettes','2.5':'PNGRB CGD progress/network/MIS; dated CGD disclosures','2.6':'World Bank energy descriptions; IEA gas statistics; RBI DBIE; GPR; IMD','2.7':'Independent publisher archives; GDELT authorised history','2.8':'Company IR; NSE/BSE dissemination records; annual/quarterly reports','2.9':'Matched independent articles, corporate filings and official event sources','macro':'MoSPI native CPI/NAS/PFCE releases; RBI; World Bank'}.get(group,'official source')
  row['candidate_sources']=provider;row['search_terms']=row['factor'].replace('_',' ')+' India CNG historical source release date';row['next_retrieval_action']+=' Search '+provider+' for '+row['factor']+'; consult manual_collection_queue.csv where access is restricted.'
 inv=pd.DataFrame(inventory);inv.to_csv(B/'metadata/data_inventory.csv',index=False);pd.DataFrame(evidence).to_csv(B/'metadata/factor_document_evidence.csv',index=False)
 # Interval coverage for every factor x candidate city, with honest geography and no artificial monthly expansion.
 cities=pd.read_csv(B/'metadata/city_coverage_matrix.csv');primary=pd.read_csv(B/'structured/price_revisions/primary_price_histories.csv');candidates=pd.read_csv(B/'structured/price_revisions/primary_history_monthly_candidates.csv');
 for idx,cityrow in cities.iterrows():
  g=primary[primary.city.eq(cityrow.city)];h=candidates[candidates.city.eq(cityrow.city)];cities.loc[idx,'primary_source_records']=len(g);cities.loc[idx,'primary_effective_start']=g.effective_date.min() if len(g) else '';cities.loc[idx,'primary_effective_end']=g.effective_date.max() if len(g) else '';cities.loc[idx,'primary_derived_candidate_months']=len(h)
 cities.to_csv(B/'metadata/city_coverage_matrix.csv',index=False);matrix=[]
 for r in inventory:
  for c in cities.to_dict('records'):
   matrix.append(dict(factor_id=r['factor_id'],city=c['city'],city_candidate_start=c['source_observation_start'],city_candidate_end=c['source_observation_end'],source_geographical_grain=r['geographical_grain'],source_period_start=r['source_period_start'],source_period_end=r['source_period_end'],source_record_count=r['nonmissing_source_records'],availability_status=r['status'],city_attribution='not_assigned_global_company_GA_grains_preserved',verified_city_month_coverage='not_established',missing_periods=r['missing_periods_and_limitations'],structured_path=r['structured_path']))
 pd.DataFrame(matrix).to_csv(B/'metadata/factor_city_period_coverage.csv',index=False)
 # Dictionary includes every current structured field; source-native units are never invented.
 dictionary=[]
 for p in sorted((B/'structured').rglob('*.csv')):
  try:d=pd.read_csv(p)
  except Exception:continue
  for col in d:
   units='INR/kg' if col.endswith('inr_kg') or col=='cng_price' else 'USD/MMBtu GCV; verify component role' if 'usd_mmbtu' in col else 'see source header and source-native definition'
   dictionary.append(dict(dataset_path=str(p.relative_to(B)),field=col,dtype=str(d[col].dtype),unit=units,definition={'publication_release_date':'Actual publication if established; blank means unknown, never observation date by default.','value_class':'Observed, derived, proxy, estimated or unverified as explicitly labelled.','effective_date':'Date price/event is stated to take effect; not publication date.','source_id':'Join to source_registry; legacy IDs may reference original inputs.'}.get(col,'Source field or collection metadata; retain exact original label and consult raw document.'),transformation='Source transcription/type parsing only; legacy constructed outputs quarantined.',provenance='Source ID, raw path, checksum, source row/page where present; no model-ready guarantee'))
 pd.DataFrame(dictionary).to_csv(B/'metadata/data_dictionary.csv',index=False)
 print(len(inv),'factors;',len(matrix),'factor-city coverage intervals;',len(reg),'source registry rows')
if __name__=='__main__':run()
