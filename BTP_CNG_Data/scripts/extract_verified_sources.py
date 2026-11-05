"""Extract source-native records and document text. No predictors, EDA or training."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import csv,hashlib,html,json,re,subprocess
import pandas as pd
from bs4 import BeautifulSoup
from recover_repository import B,save,sha,metadata,NOW

def catalog():
 rows=[]
 for p in sorted((B/'logs').glob('retrieval_*.json')):rows.extend(json.loads(p.read_text()))
 # Keep every attempted response; select latest successful per source for parsing.
 pd.DataFrame(rows).to_csv(B/'metadata/retrieval_attempts.csv',index=False)
 return rows,{r['source_id']:r for r in rows if r.get('raw_path')}

def pdf_text(row):
 p=B/row['raw_path'];out=B/'documents/extracted'/row['source_id']/(p.stem+'.txt');out.parent.mkdir(parents=True,exist_ok=True)
 status='extracted';err=''
 if not out.exists():
  try:subprocess.run(['pdftotext','-layout',str(p),str(out)],check=True,capture_output=True,timeout=90)
  except Exception as e:status='text_extraction_failed';err=str(e)
 text=out.read_text(errors='replace') if out.exists() else ''
 return dict(source_id=row['source_id'],source_url=row['url'],raw_path=row['raw_path'],raw_sha256=row['sha256'],text_path=str(out.relative_to(B)),text_sha256=sha(out) if out.exists() else '',pages=text.count('\f'),text_characters=len(text),text_extraction_status=status if text.strip() else 'scan_or_no_text',error=err,publication_release_date='',publication_status='unknown',extraction_timestamp=NOW)

def common(row):return dict(source_id=row['source_id'],source_url=row['url'],raw_path=row['raw_path'],raw_sha256=row['sha256'],extraction_timestamp=row['extraction_timestamp'],publication_release_date='',publication_status='unknown')
def clean(s):return ' '.join(html.unescape(re.sub('<[^>]+>',' ',s)).split())

def pngrb(row):
 text=(B/row['raw_path']).read_text();rows=[];reject=[]
 fields=['ga_id','cgd_operator','ga_name','district','state','last_revision_date_raw','retail_price_inr_kg','gas_cost_inr_kg','supply_distribution_cost_inr_kg','margin_inr_kg','transmission_tariff_inr_kg','basic_price_inr_kg','excise_inr_kg','vat_inr_kg','other_tax_inr_kg']
 for table in re.findall(r'<table\b[^>]*>.*?</table>',text,re.S|re.I):
  tid=re.search(r'id="([^"]+)"',table);tid=tid.group(1) if tid else ''
  if not tid.lower().startswith('cng'):continue
  tag=re.search(r'data-csv-name="([^"]+)"',table);period=tag.group(1) if tag else tid
  # Heading before this exact table supplies period for older tables lacking data-csv-name.
  before=text[max(0,text.find(table)-15000):text.find(table)]
  heads=re.findall(r'(?:PNG\s*(?:&amp;|&)\s*CNG\s*Prices|CNG\s*(?:&amp;|&)\s*PNG\s*Prices)\s*\(([^)]+)\)',before,re.I)
  if not tag and heads:period=heads[-1]
  for n,tr in enumerate(re.findall(r'<tr\b[^>]*>.*?</tr>',table,re.S|re.I)):
   cells=[clean(c) for c in re.findall(r'<td\b[^>]*>(.*?)</td>',tr,re.S|re.I)]
   if not cells:continue
   if len(cells)!=15:reject.append(dict(table_id=tid,row_number=n,cells=json.dumps(cells),reason='unexpected_cell_count'));continue
   rec=dict(zip(fields,cells));rec.update(common(row),source_table_id=tid,source_period_label=period,source_row_number=n,value_class='observed_entity_submission',verification_status='regulator_hosted_entity_report_not_independently_verified',geographical_grain='district_GA',unit='INR/kg')
   rec['last_revision_date']=pd.to_datetime(rec['last_revision_date_raw'],dayfirst=True,errors='coerce').strftime('%Y-%m-%d') if pd.notna(pd.to_datetime(rec['last_revision_date_raw'],dayfirst=True,errors='coerce')) else ''
   for f in fields[6:]:rec[f+'_raw']=rec[f];rec[f]=pd.to_numeric(rec[f].replace(',',''),errors='coerce')
   m=re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)[_ ,\-]*(20\d{2})',period,re.I)
   rec['observation_period']=pd.to_datetime(m.group(1)+' '+m.group(2)).strftime('%Y-%m') if m else ''
   rec['revision_date_conflict']=bool(rec['observation_period'] and rec['last_revision_date'] and rec['last_revision_date'][:7]>rec['observation_period'])
   rows.append(rec)
 save(pd.DataFrame(rows),'structured/price_revisions/pngrb_all_district_snapshots.csv')
 pd.DataFrame(reject,columns=['table_id','row_number','cells','reason']).to_csv(B/'metadata/pngrb_parse_rejections.csv',index=False)
 return rows

def native_numeric(src):
 for sid,r in src.items():
  if sid not in ['WB','GPR']:continue
  p=B/r['raw_path']
  if sid=='WB':
   d=pd.read_excel(p,sheet_name='Monthly Prices',skiprows=4);d=d[d.iloc[:,0].astype(str).str.fullmatch(r'\d{4}M\d{2}')]
   columns=['Crude oil, average','Crude oil, Brent','Crude oil, Dubai','Crude oil, WTI','Natural gas, US','Natural gas, Europe','Liquefied natural gas, Japan']
   d=d[[d.columns[0]]+[c for c in columns if c in d]].rename(columns={d.columns[0]:'observation_period'})
   # Keep source labels; Europe is not a homogeneous TTF series over the full history.
   for c in d.columns[1:]:d[c]=pd.to_numeric(d[c],errors='coerce')
   d=metadata(d,'WB',p,kind='proxy');d['source_url']=r['url'];d['extraction_timestamp']=r['extraction_timestamp'];d['definition_note']='Benchmarks; source descriptions retained in workbook. Not operator procurement costs.'
   save(d,'structured/numerical_factors/worldbank_energy_native_monthly.csv')
  else:
   d=pd.read_excel(p);d=metadata(d,'GPR',p,kind='proxy');d['source_url']=r['url'];d['extraction_timestamp']=r['extraction_timestamp'];save(d,'structured/numerical_factors/gpr_native_monthly.csv')

def price_histories(src,docs):
 rows=[]
 for sid,city,operator in [('DELHI_PARLIAMENT','Delhi','IGL'),('GGL_HISTORY','Lucknow','Green Gas Limited')]:
  if sid not in docs:continue
  text=(B/docs[sid]['text_path']).read_text();r=src[sid]
  if sid=='DELHI_PARLIAMENT':text=text.split('ANNEXURE-I')[-1]
  for line in text.splitlines():
   m=re.match(r'^\s*(\d{2}\.\d{2}\.\d{4})\s+(\d+\.\d{2})\b',line)
   if not m:continue
   date=pd.to_datetime(m[1],dayfirst=True).strftime('%Y-%m-%d')
   rows.append(dict(common(r),city=city,cgd_operator=operator,effective_date=date,cng_price=float(m[2]),unit='INR/kg',value_class='observed_primary_record',effective_date_status='explicit_in_primary_document',verification_status='primary_source_not_independent_final_validation',document_date='2024-12-16' if sid=='DELHI_PARLIAMENT' else '',source_line=line.strip(),geographical_grain='city_GA'))
   # Retain all GGL GAs; no transfer from Lucknow to neighbouring cities.
   if sid=='GGL_HISTORY':
    values=re.split(r'\s{2,}',line.strip())
    for idx,ga in [(2,'Agra'),(3,'Ayodhya & Sultanpur'),(4,'Unnao')]:
     if len(values)>idx:
      v=pd.to_numeric(values[idx],errors='coerce');rows.append(dict(common(r),city=ga,cgd_operator=operator,effective_date=date,cng_price=v,unit='INR/kg',value_class='observed_primary_record',effective_date_status='explicit_in_primary_document',verification_status='primary_source_not_independent_final_validation',document_date='',source_line=line.strip(),geographical_grain='GA',source_status_token=values[idx]))
 d=pd.DataFrame(rows)
 if len(d):
  d=d.sort_values(['city','effective_date']);prev=d.groupby('city').cng_price.shift();d['record_type']='reported_unchanged';d.loc[prev.isna(),'record_type']='initial_or_missing_prior';d.loc[prev.notna() & d.cng_price.ne(prev),'record_type']='reported_price_change';save(d,'structured/price_revisions/primary_price_histories.csv')
  sec=pd.read_csv(B/'structured/price_revisions/source_observations.csv');checks=[]
  for _,x in d.iterrows():
   g=sec[(sec.city.eq(x.city)) & (sec.observation_date.eq(x.effective_date))]
   checks.append(dict(city=x.city,effective_date=x.effective_date,primary_price=x.cng_price,source_id=x.source_id,secondary_exact_date_rows=len(g),secondary_price=g.cng_price.iloc[0] if len(g) else '',comparison='no_exact_secondary_date' if not len(g) else 'agree' if abs(g.cng_price.iloc[0]-x.cng_price)<.005 else 'CONFLICT'))
  pd.DataFrame(checks).to_csv(B/'metadata/price_crosschecks.csv',index=False)
 # MNGL preserves subcity and ambiguous midnight/starting-month labels as printed, no invented day.
 out=[]
 for sid,doc in docs.items():
  if not sid.startswith('MNGL_HISTORY_DOC_'):continue
  text=(B/doc['text_path']).read_text()
  for n,line in enumerate(text.splitlines(),1):
   if not re.search(r'\d+\.\d+\s*/-',line):continue
   cols=re.split(r'\s{2,}',line.strip())
   out.append(dict(common(src[sid]),source_line_number=n,source_line=line,source_cells=json.dumps(cols),value_class='observed_document_row',verification_status='date_and_subcity_review_required',geographical_grain='GA_or_subcity',unit='source_mixed_CNG_INRkg_and_PNG_INRscm'))
 save(pd.DataFrame(out),'structured/price_revisions/mngl_historical_source_rows.csv')

def ppac_notifications(src,docs):
 rows=[]
 for sid,doc in docs.items():
  if not sid.startswith('PPAC_NOTE_'):continue
  text=(B/doc['text_path']).read_text()
  # Only take explicitly readable currency matches; scanned OCR that fails is a documented gap.
  matches=re.findall(r'(?:US\s*\$|USD|US§)\s*([\d]+(?:\.\d+)?)\s*/?\s*M?M[Bb][Tt][Uu]',text)
  dated=re.search(r'[Dd]ated\s*[:.]*\s*(\d{1,2}[./-]\d{1,2}[./-]\d{4})',text)
  date=pd.to_datetime(dated[1],dayfirst=True,errors='coerce') if dated else pd.NaT
  rows.append(dict(common(src[sid]),document_date=date.strftime('%Y-%m-%d') if pd.notna(date) else '',document_date_status='parsed_document_date_not_verified_publication' if pd.notna(date) else 'unresolved',currency_values_in_source_order=json.dumps(matches),text_path=doc['text_path'],record_type='notification_document',verification_status='manual_field_assignment_and_OCR_review_required',value_class='observed_document',definition_note='Calculated gas price; nomination-block ceiling; difficult-field ceiling and PAF must remain distinct. Never assign a ceiling to every month automatically.'))
 save(pd.DataFrame(rows),'structured/numerical_factors/ppac_notification_records.csv')

def news(src):
 rows=[]
 for sid,r in src.items():
  if not sid.startswith('NEWS_'):continue
  s=BeautifulSoup((B/r['raw_path']).read_bytes(),'html.parser');ld=[]
  for t in s.select('script[type="application/ld+json"]'):
   try:ld.append(json.loads(t.string or t.text))
   except Exception:pass
  def walk(v):
   if isinstance(v,dict):
    yield v
    for x in v.values():yield from walk(x)
   elif isinstance(v,list):
    for x in v:yield from walk(x)
  arts=[v for v in walk(ld) if any(k in str(v.get('@type','')).lower() for k in ['newsarticle','reportagenewsarticle','article']) and v.get('headline')]
  a=arts[0] if arts else {};published=a.get('datePublished','');modified=a.get('dateModified','')
  h=s.find('h1');title=a.get('headline') or (h.get_text(' ',strip=True) if h else '')
  rows.append(dict(common(r),article_id=sid,title=title,publication_release_date=published,modified_timestamp=modified,publication_status='publisher_structured_metadata' if published else 'unknown',source_type='independent_news',article_body_available=bool(a.get('articleBody')),article_body_characters=len(a.get('articleBody','')),verification_status='article_metadata_extracted' if arts else 'article_parse_requires_review',value_class='observed_publisher_record',copyright_note='Full article raw retained privately; do not redistribute full text without permission.',duplicate_cluster='unreviewed',company_city_relevance='CNG India; manual entity review pending',text_features_status='not_computed_stage3'))
 save(pd.DataFrame(rows),'structured/news/actual_article_metadata.csv')

def run():
 attempts,src=catalog();pr=pngrb(src['PNGRB_PRICES']) if 'PNGRB_PRICES' in src else []
 native_numeric(src)
 pdfs=[r for r in src.values() if r['raw_path'].endswith('.pdf')]
 docs=list(ThreadPoolExecutor(max_workers=4).map(pdf_text,pdfs));dd={r['source_id']:r for r in docs}
 pd.DataFrame(docs).to_csv(B/'metadata/document_extraction_manifest.csv',index=False)
 price_histories(src,dd);ppac_notifications(src,dd);news(src)
 corp=pd.read_csv(B/'structured/corporate_disclosures/corporate_disclosures_metadata.csv');corp=corp[corp['disclosure_id'].eq('IGL-2024-11-15-ALLOCATION')]
 extra=[]
 for sid,doc in dd.items():
  if sid.startswith(('MNGL_REPORTS_DOC_','ATGL_REPORTS_PDF_','GGL_REPORTS_PDF_','GGL_OLD_REPORTS_PDF_')) or sid in ['ATGL_FY24','GGL_NSE_FY25']:
   company='MNGL' if sid.startswith('MNGL') else 'ATGL' if sid.startswith('ATGL') else 'Gujarat Gas';url=src[sid]['url'].lower();kind='annual_report' if 'annual' in url or sid.startswith('MNGL_REPORTS') or sid in ['ATGL_FY24','GGL_NSE_FY25'] else 'investor_document_unclassified'
   extra.append(dict(doc,company=company,document_type=kind,geographical_grain='company',value_class='observed_company_document',verification_status='document_downloaded_text_extracted_publication_unresolved',reporting_period_status='refer_to_original_document_not_download_name'))
 if extra:save(pd.concat([corp,pd.DataFrame(extra)],ignore_index=True),'structured/corporate_disclosures/corporate_disclosures_metadata.csv')
 print(json.dumps(dict(attempts=len(attempts),retrieved_sources=len(src),pngrb_snapshots=len(pr),pdf_documents=len(docs),corporate_reports=len(extra))))
if __name__=='__main__':run()
