"""Source-native CNG-only sales and station indicator extraction. No resampling."""
from pathlib import Path
import csv,json,re,hashlib,datetime,calendar
import pdfplumber
from pypdf import PdfReader

ROOT=Path('/Users/virajvekariya/Desktop/[ME] BTP')
BASE=Path(__file__).parent
FRESH=ROOT/'BTP/BTP_CNG_Fresh_2026-11-06/numerical'
for n in ['metadata','structured','verification']:(BASE/n).mkdir(parents=True,exist_ok=True)
manifest={r['source_id']:r for r in json.loads((FRESH/'manifest.json').read_text())}
registry=list(csv.DictReader((FRESH/'structured/pngrb_document_registry.csv').open(encoding='utf-8-sig')))
observations=[];reviews=[];sources=[]
for receipt in registry:
 if 'bulletin' not in receipt['title'].lower():continue
 sid=receipt['source_id'];raw=FRESH/manifest[sid]['local_path'];h=hashlib.sha256(raw.read_bytes()).hexdigest()
 assert h==manifest[sid]['sha256']
 sources.append(dict(source_id=sid,path=str(raw),sha256=h,url=receipt['url'],publication_date=receipt['publication_date'],publication_date_basis=receipt['publication_date_basis']))
 # Independent text engine is used to corroborate each extracted numeric token.
 native=PdfReader(raw)
 with pdfplumber.open(raw) as document:
  found=False
  for pi,page in enumerate(document.pages):
   text=page.extract_text() or ''
   if 'CNG Stations' not in text:continue
   if 'MMSCM' not in text:continue
   tables=page.extract_tables()
   for ti,table in enumerate(tables):
    header=next((r for r in table if any(c=='High Frequency Indicator' for c in r)),None)
    if not header:continue
    header=[str(c or '').replace('\n',' ').strip() for c in header]
    yi=[(i,c) for i,c in enumerate(header) if re.fullmatch(r'20\d{2}',c)]
    fi=[(i,re.search(r'(20\d{2}[-–]\d{2})$',c).group(1)) for i,c in enumerate(header) if re.search(r'(20\d{2}[-–]\d{2})$',c)]
    if len(yi)!=2 or len(fi)!=2:
     reviews.append(dict(source_id=sid,page=pi+1,reason='unrecognized_year_header',header=header));continue
    labelindex=header.index('High Frequency Indicator');monthindex=header.index('Month');unitindex=header.index('Unit')
    for ri,row in enumerate(table):
     if len(row)!=len(header):continue
     label=str(row[labelindex] or '').strip()
     if label not in ['CNG','CNG Stations']:continue
     token=str(row[monthindex] or '').strip();unit=str(row[unitindex] or '').strip()
     try:month=datetime.datetime.strptime(token,'%b-%y').month
     except ValueError:
      reviews.append(dict(source_id=sid,page=pi+1,reason='unknown_month',token=token));continue
     independent=native.pages[pi].extract_text() or ''
     for ci,year in yi+fi:
      value=str(row[ci] or '').strip()
      if not re.fullmatch(r'[\d,]+(?:\.\d+)?',value):
       reviews.append(dict(source_id=sid,page=pi+1,reason='missing_or_nonnumeric_token',label=label,column=ci,token=value));continue
      if (ci,year) in yi:
       first=f'{year}-{month:02}-01';last=f'{year}-{month:02}-{calendar.monthrange(int(year),month)[1]}';frequency='monthly_source_total'
      else:
       start=int(year[:4]);end=start if month>=4 else start+1
       first=f'{start}-04-01';last=f'{end}-{month:02}-{calendar.monthrange(end,month)[1]}';frequency='financial_year_to_date_source_total'
      corroborated=value in independent or value.replace(',','') in independent.replace(',','')
      assert corroborated,(sid,pi,label,value)
      obs=dict(source_id=sid,source_sha256=h,source_path=str(raw),source_url=receipt['url'],source_page=pi+1,source_table=ti,source_row=ri,source_column=ci,source_label=label,series='cng_sales_volume' if label=='CNG' else 'cng_station_reported_indicator',geography='India',geography_type='national_entity_submissions',period_start=first,period_end=last,frequency=frequency,value=value.replace(',',''),source_value=value,unit=unit,publication_date=receipt['publication_date'],publication_date_basis=receipt['publication_date_basis'],value_class='source_reported_aggregate',definition_status='CNG_only_not_PNG' if label=='CNG' else 'flow_vs_stock_not_explicit_do_not_treat_as_operating_stock',verification_status='table_cells_crosschecked_with_independent_pdf_text_engine',synthetic=False)
      obs['observation_id']=hashlib.sha256(json.dumps(obs,sort_keys=True).encode()).hexdigest()[:24];observations.append(obs);found=True
   if found:break
  if not found:reviews.append(dict(source_id=sid,reason='no_supported_CGD_table_extracted'))
with (BASE/'structured/cng_reported_native.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(observations[0]) if observations else ['observation_id']);w.writeheader();w.writerows(observations)
(BASE/'metadata/source_manifest.json').write_text(json.dumps(sources,indent=2))
(BASE/'metadata/extraction_review_queue.json').write_text(json.dumps(reviews,indent=2))
# Preserve differing reported vintages as conflicts, rather than selecting a favorable value.
groups={}
for r in observations:groups.setdefault((r['series'],r['geography'],r['period_start'],r['period_end'],r['frequency'],r['unit']),[]).append(r)
conflicts=[{'key':k,'values':sorted({r['value'] for r in rs}),'observation_ids':[r['observation_id'] for r in rs]} for k,rs in groups.items() if len({r['value'] for r in rs})>1]
(BASE/'metadata/source_vintage_conflicts.json').write_text(json.dumps(conflicts,indent=2))
# Hand checked against the saved rendered March page, separate from either parser.
manual=[('cng_sales_volume','2026-03-01','2026-03-31','946'),('cng_sales_volume','2025-03-01','2025-03-31','813'),('cng_sales_volume','2025-04-01','2026-03-31','10721'),('cng_station_reported_indicator','2026-03-01','2026-03-31','224')]
for series,start,end,value in manual:
 assert any(r['source_id']=='pngrb_2567b40dcffc' and r['series']==series and r['period_start']==start and r['period_end']==end and r['value']==value for r in observations)
validation=dict(source_files=len(sources),source_observation_rows=len(observations),unique_economic_keys=len(groups),source_vintage_conflict_keys=len(conflicts),review_items=len(reviews),all_values_independently_text_crosschecked=True,visual_spot_check={'image':'verification/bulletin_march2026_page13.png','values':manual},limitations=['National totals do not establish city CNG consumption','Station indicator stock/flow not explicitly defined; excluded from operating-station-stock interpretation','Entity-reported aggregates are source claims, not independent measurements','Financial-year totals and monthly totals remain separate','Reported monthly values rounded by source; not daily measurements'])
(BASE/'metadata/validation.json').write_text(json.dumps(validation,indent=2))
print(json.dumps(validation,indent=2))
