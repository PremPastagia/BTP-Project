"""Preserve source cells and extract narrowly defined factual values, with review flags."""
import json,re
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
from recover_repository import B,save,NOW
from extract_verified_sources import catalog,common

def run():
 attempts,src=catalog();manifest=pd.read_csv(B/'metadata/document_extraction_manifest.csv').fillna('');tables=[];pages=[];gas=[];prices=[];titles={}
 for p in (B/'raw/recovery').glob('PPAC_GAS*/*.html'):
  s=BeautifulSoup(p.read_bytes(),'html.parser')
  for a in s.select('a[href]'):
   if 'file=gasprice/' in a['href']:
    h=a.find_previous('h3');titles[a['href']]=h.get_text(' ',strip=True) if h else ''
 for doc in manifest.to_dict('records'):
  sid=doc['source_id'];r=src[sid];p=B/doc['text_path']
  if not p.exists():continue
  text=p.read_text(errors='replace')
  for page,txt in enumerate(text.split('\f'),1):
   if not txt.strip():continue
   pages.append(dict(source_id=sid,page=page,text_path=doc['text_path'],text_characters=len(txt),raw_path=doc['raw_path'],raw_sha256=doc['raw_sha256'],verification_status='source_text_not_semantically_validated'))
   # Raw source table rows remain at original document grain and retain page/line.
   if sid.startswith(('PNGRB','PPAC','MNGL','ATGL','GGL')):
    for line_no,line in enumerate(txt.splitlines(),1):
     cells=re.split(r'\s{2,}',line.strip())
     if len(cells)>=3 and sum(bool(re.search(r'\d',c)) for c in cells)>=2:
      tables.append(dict(source_id=sid,page=page,line=line_no,source_cells=json.dumps(cells,ensure_ascii=False),raw_source_line=line,raw_path=doc['raw_path'],raw_sha256=doc['raw_sha256'],geographical_grain='refer_to_page_header',units='refer_to_page_header',value_class='unverified_source_table_transcription',verification_status='header_period_column_alignment_requires_review'))
  if sid.startswith('PPAC') and ('gross production of natural gas for the month' in text.lower() or 'total import of lng' in text.lower()):
   for metric,pat in [('domestic_gas_gross_production',r'Gross\s+Production\s+of\s+natural\s+gas\s+for\s+the\s+month\s+of\s+(.{1,70}?)\s+was\s+([\d,]+)\s+MMSCM'),('lng_import_volume',r'Total\s+Import\s+of\s+LNG\s*\(Provisional\)\s+during\s+the\s+month\s+of\s+(.{1,70}?)\s+was\s+([\d,]+)\s+MMSCM')]:
    for m in re.finditer(pat,text,re.I|re.S):
     gas.append(dict(common(r),metric=metric,period_raw=' '.join(m[1].split()),value=float(m[2].replace(',','')),unit='MMSCM',geographical_grain='India',value_class='observed_provisional',verification_status='text_regex_transcription_requires_table_crosscheck',evidence_quote=' '.join(m[0].split())))
  if sid.startswith('PPAC_NOTE_'):
   ocr=B/'documents/ocr'/sid/(p.stem+'.txt');used='native_text'
   if len(text.strip())<150 and ocr.exists():text=ocr.read_text();used='OCR_unverified'
   title=titles.get(r['url'],'');flat=' '.join(text.split());currency=list(re.finditer(r'(?:US\s*[$§S]|USD)\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*M?M[Bb][Tt][Uu]',flat))
   typ='domestic_gas' if 'domestic' in title.lower() else 'difficult_field_ceiling' if 'ceiling' in title.lower() else 'other_notification'
   if not currency:
    prices.append(dict(common(r),notification_title=title,notification_type=typ,parse_status='no_readable_currency_value',text_method=used,notified_price_usd_mmbtu=None,nomination_ceiling_usd_mmbtu=None,period_start='',period_end='',value_class='unverified',verification_status='manual_transcription_required'));continue
   vals=[float(m[1]) for m in currency];ceiling=[float(m[1]) for m in currency if 'ceiling' in flat[max(0,m.start()-45):m.start()].lower()]
   # Range comes from website title, never the URL epoch or an assumed first-of-month release.
   dates=re.findall(r'(\d{1,2})(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})',title,re.I)
   ds=[pd.to_datetime(' '.join(v),dayfirst=True).strftime('%Y-%m-%d') for v in dates]
   dated=re.search(r'Dated\s*[:.]*\s*(\d{1,2}[./-]\d{1,2}[./-]\d{4})',text,re.I)
   dd=pd.to_datetime(dated[1],dayfirst=True,errors='coerce') if dated else pd.NaT
   prices.append(dict(common(r),notification_title=title,notification_type=typ,parse_status='transcribed_requires_review',text_method=used,notified_price_usd_mmbtu=vals[0],nomination_ceiling_usd_mmbtu=ceiling[0] if ceiling else None,all_currency_values=json.dumps(vals),period_start=ds[0] if ds else '',period_end=ds[-1] if len(ds)>1 else '',document_date=dd.strftime('%Y-%m-%d') if pd.notna(dd) else '',document_date_status='document_date_not_publication',unit='USD/MMBtu GCV',geographical_grain='India_pricing_regime',value_class='unverified_source_transcription',verification_status='manual_OCR_role_and_period_check_required',definition_note='Notified calculated domestic price and nomination-block ceiling retained separately; no constant ceiling used as observed procurement price.'))
 save(pd.DataFrame(tables),'structured/source_native/document_table_rows.csv');pd.DataFrame(tables).to_parquet(B/'structured/source_native/document_table_rows.parquet',compression='zstd',compression_level=10,index=False);save(pd.DataFrame(pages),'structured/source_native/document_pages.csv')
 save(pd.DataFrame(gas),'structured/numerical_factors/ppac_gas_supply_transcriptions.csv');save(pd.DataFrame(prices),'structured/numerical_factors/ppac_price_transcriptions.csv')
 print(len(tables),'source table rows;',len(pages),'pages;',len(gas),'gas supply facts;',len(prices),'price notifications')
if __name__=='__main__':run()
