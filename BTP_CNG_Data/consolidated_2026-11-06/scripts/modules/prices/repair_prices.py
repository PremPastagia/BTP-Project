"""Stage 3 source-level price repair. No filling, monthly targets, or modeling.

Original sources are referenced by absolute path and hash, never overwritten.
"""
from pathlib import Path
from datetime import datetime, date, timezone
from collections import Counter, defaultdict
import calendar,csv,hashlib,json,re
from lxml import html
import openpyxl,pdfplumber
from pypdf import PdfReader
from dateutil import parser as dp

B=Path(__file__).resolve().parent
ROOT=B.parents[1]
OLD=ROOT/'BTP/BTP_CNG_Fresh_2026-11-06/prices'
for p in ['structured','metadata','scripts','logs']: (B/p).mkdir(exist_ok=True)
MAN=json.loads((OLD/'manifest.json').read_text())
SOURCES={r['source_id']:dict(r,original_path=str(OLD/r['local_path'])) for r in MAN}
OBS=[];CELLS=[];EX=[];REP=[];SCHEMA=[]
FIELDS=['observation_id','source_id','source_sha256','source_url','source_locator','geography_name','geography_type','operator','ga_id','district','state','price_inr_kg','effective_date','effective_month','effective_window_start','effective_window_end','effective_date_raw','date_status','snapshot_month','publication_date','retrieved_at','observation_type','extraction_status','raw_cells_json','notes']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,rows,fields=None):
    fields=fields or list(rows[0]) if rows else fields or ['status']
    with (B/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def number(v):
    if v is None:return None
    s=str(v).replace('\xa0',' ').strip().replace(',','')
    if not re.fullmatch(r'-?\d+(?:\.\d+)?',s):return None
    return float(s)
def exact(v):
    if isinstance(v,datetime):return v.date().isoformat()
    for fmt in ['%d.%m.%Y','%d.%m.%y','%d-%b-%y','%d-%B-%y']:
        try:return datetime.strptime(str(v).strip(),fmt).date().isoformat()
        except ValueError:pass
    return ''
def dates(raw,slashes=False):
    raw=str(raw).strip();r=dict(effective_date='',effective_month='',effective_window_start='',effective_window_end='',effective_date_raw=raw,date_status='unparsed_source_date')
    d=exact(raw)
    if d:r.update(effective_date=d,date_status='exact_source_date');return r
    if slashes:
        m=re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{2,4})',raw)
        if m:
            a,b,y=map(int,m.groups()); y+=2000 if y<100 else 0; candidates=[]
            for month,day in [(a,b),(b,a)]:
                try:candidates.append(date(y,month,day).isoformat())
                except ValueError:pass
            candidates=sorted(set(candidates))
            if len(candidates)==1:r.update(effective_date=candidates[0],date_status='unambiguous_numeric_source_date')
            else:r['date_status']='ambiguous_or_invalid_numeric_date'
        return r
    clean=re.sub(r'(\d+)(st|nd|rd|th)',r'\1',raw,flags=re.I).replace('\ufffd',' ').replace('’',' ').replace("'",' ').replace('Starting price -','').replace('Midnight','').strip()
    clean=re.sub(r'\bSept\b','Sep',clean)
    try:
        if re.fullmatch(r'[A-Za-z]+\.?[- ]\d{2,4}',clean):
            token,year=re.split('[- ]',clean);y=int(year);y+=2000 if y<100 else 0
            r.update(effective_month=f'{y:04d}-{dp.parse(token+" 1 2000").month:02d}',date_status='source_month_only');return r
        if '/' in clean:
            a,b=clean.split('/',1);end=dp.parse(b,default=datetime(2000,1,1),dayfirst=True).date()
            start=date(end.year,end.month,int(a.strip())) if not re.search('[A-Za-z]',a) else dp.parse(a,default=datetime(end.year,end.month,1),dayfirst=True).date()
            r.update(effective_window_start=start.isoformat(),effective_window_end=end.isoformat(),date_status='overnight_window_not_exact_day');return r
        d=dp.parse(clean,default=datetime(2000,1,1),dayfirst=True).date()
        r.update(effective_date=d.isoformat(),date_status='midnight_day_unspecified' if 'Midnight' in raw else 'exact_source_date')
    except Exception:pass
    return r
def add(sid,loc,geo,value,**kw):
    r={k:'' for k in FIELDS};s=SOURCES[sid]
    r.update(source_id=sid,source_sha256=s['sha256'],source_url=s['url'],source_locator=loc,geography_name=geo,price_inr_kg=value,retrieved_at=s['retrieved_at'],observation_type='price_source_claim',extraction_status='source_transcription_not_independent_truth_verification')
    r.update(kw);r['observation_id']=hashlib.sha256(json.dumps([r[k] for k in FIELDS if k!='observation_id'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:24]
    OBS.append(r);return r

tree=html.fromstring(Path(SOURCES['pngrb_prices']['original_path']).read_bytes())
tables=tree.xpath('//table[starts-with(@id,"CngPrice")]')
MONTHS=['2026-08','2026-07','2026-06','2026-05','2026-04','2026-03','2026-02','2026-01','2025-12','2025-11','2025-10','2025-09','2025-08','2025-07','2025-06','2025-05','2025-04','2025-03']
assert len(tables)==len(MONTHS)
EXPECTED=['ga_id','operator','geography_name','district','state','effective_date_raw','price_inr_kg','gas_cost','supply_distribution_cost','entity_margin','transmission_tariff','basic_selling_price','excise_duty','value_added_tax','other_tax']
def header_key(s):
    s=re.sub('[^a-z0-9]','',s.lower())
    for pat,k in [('gaid','ga_id'),('nameofcgdentity','operator'),('ganame','geography_name'),('district','district'),('state','state'),('lastpricerevisiondate','effective_date_raw'),('retailsellingprice','price_inr_kg'),('costofnaturalgas','gas_cost'),('supplydistributioncost','supply_distribution_cost'),('entitysmargin','entity_margin'),('transmissiontariff','transmission_tariff'),('basicsellingprice','basic_selling_price'),('exciseduty','excise_duty'),('valueaddedtax','value_added_tax'),('anyothertax','other_tax')]:
        if s.startswith(pat):return k
    raise ValueError('Unexpected header '+s)

for table,month in zip(tables,MONTHS):
    tid=table.get('id');trs=table.xpath('.//tr')
    title=' '.join(' '.join(table.xpath('preceding::h2[1]//text()')).split())
    title_month=re.search(r'\(([A-Za-z]+)\s+(\d{4})\)',title)
    assert title_month,(tid,title)
    observed_month=dp.parse('1 '+title_month[1]+' '+title_month[2]).strftime('%Y-%m')
    assert observed_month==month,(tid,title,month)
    headers=[' '.join(' '.join(x.itertext()).split()) for x in trs[0].xpath('./td|./th')]
    keys=list(map(header_key,headers));assert keys==EXPECTED,(tid,keys)
    SCHEMA.append(dict(table_id=tid,source_heading=title,snapshot_month=month,header_json=json.dumps(headers),body_schema='omitted_GA_ID_trailing_blank' if tid in ['CngPriceJan26','CngPriceDec'] else 'header_aligned',source_sha256=SOURCES['pngrb_prices']['sha256']))
    for ix,tr in enumerate(trs[1:],2):
        raw=[' '.join(' '.join(x.itertext()).split()) for x in tr.xpath('./td|./th')];c=list(raw);loc=f'{tid}/tr{ix}'
        if len(c)!=len(keys):EX.append(dict(source_id='pngrb_prices',source_locator=loc,reason='unexpected_column_count',raw_json=json.dumps(raw)));continue
        mapping='direct_source_headers'
        # Explicit source HTML defect: missing GA ID, body shifted, blank final td.
        # Never borrow GA IDs from another month to disguise missing source fields.
        if tid in ['CngPriceJan26','CngPriceDec'] and not re.fullmatch(r'\d+(?:\.\d+)?',c[0]) and not c[-1]:
            c=['']+c[:-1];mapping='missing_GA_ID_body_cell_restored_as_blank'
            REP.append(dict(source_id='pngrb_prices',source_locator=loc,snapshot_month=month,repair=mapping,old_ga_id=raw[0],old_state=raw[4],old_price=raw[6],new_ga_id='',new_operator=c[1],new_state=c[4],new_price=c[6],evidence='Original source has 15 headers but omitted GA-ID body cell in Jan26 and Dec tables; final cell blank; date (or missing-date cell) located in body column 5.'))
        d=dict(zip(keys,c));v=number(d['price_inr_kg'])
        if v is None or v<=0:
            EX.append(dict(source_id='pngrb_prices',source_locator=loc,reason='missing_non_numeric_or_nonpositive_retail_price',raw_json=json.dumps(raw)));continue
        rec=add('pngrb_prices',loc,d['geography_name'],v,operator=d['operator'],ga_id=d['ga_id'],district=d['district'],state=d['state'],geography_type='source_GA_and_district_snapshot',snapshot_month=month,raw_cells_json=json.dumps(raw,ensure_ascii=False),notes=mapping+'; Snapshot is not a month-end target. Source-reported entity components; publication unknown.',**dates(d['effective_date_raw'],True))
        co={k:rec[k] for k in ['observation_id','source_id','source_sha256','source_locator','snapshot_month','geography_name','operator','ga_id','district','state']}
        co.update(retail_price_inr_kg=v,mapping_status=mapping,raw_cells_json=json.dumps(raw,ensure_ascii=False))
        for k in keys[7:]:co[k+'_raw']=d[k];co[k]=number(d[k])
        terms=['basic_selling_price','excise_duty','value_added_tax','other_tax']
        co['retail_tax_identity_residual']=round(v-sum(co[k] for k in terms),6) if all(co[k] is not None for k in terms) else None
        co['component_status']='incomplete' if co['retail_tax_identity_residual'] is None else 'conflict' if abs(co['retail_tax_identity_residual'])>.05 else 'within_0.05'
        CELLS.append(co)

# Read all current-workbook CNG market cells. Textual numeric prices are values,
# while zero, dash, missing and formula-only cells never establish retail levels.
w=openpyxl.load_workbook(Path(SOURCES['igl_chronology']['original_path']),data_only=False,read_only=True)
s=w['CNG Price'];data=list(s.iter_rows(values_only=True));markets=data[3]
cell_audit=[]
for rn,row in enumerate(data[4:],5):
    day=exact(row[1])
    for ci in range(2,16):
        raw=row[ci];v=number(raw);loc=f'CNG Price!{openpyxl.utils.get_column_letter(ci+1)}{rn}'
        status='positive_numeric_string' if isinstance(raw,str) and v is not None and v>0 else 'positive_numeric' if v is not None and v>0 else 'missing' if raw is None else 'nonpositive_or_unknown_token'
        cell_audit.append(dict(source_id='igl_chronology',source_locator=loc,geography_name=str(markets[ci]),raw_value=raw,source_date_raw=row[1],effective_date=day,value_class=status))
        if v is not None and v>0 and day:
            add('igl_chronology',loc,str(markets[ci]),v,operator='Indraprastha Gas Limited',geography_type='operator_named_price_market',effective_date=day,effective_date_raw=str(row[1]),date_status='exact_source_date',raw_cells_json=json.dumps([row[1],raw],default=str),notes='Retrospective official workbook quote. No missing cell filling or proof of price continuity. Workbook publication date unknown.')
        elif raw is not None:EX.append(dict(source_id='igl_chronology',source_locator=loc,reason=status,raw_json=json.dumps([row[1],raw],default=str)))
w.close()

# GGL four GA columns, retaining source noncommencement markers as exclusions.
reader=PdfReader(SOURCES['ggl_chronology']['original_path']);text='\n'.join(p.extract_text() or '' for p in reader.pages)
for ln,line in enumerate(text.splitlines(),1):
    m=re.match(r'^(\d{2}\.\d{2}\.\d{4})\s+(.*)$',line.strip())
    if not m:continue
    tokens=re.findall(r'\d+\.\d+\*?|Sale not commenced',m[2])
    if len(tokens)!=4:EX.append(dict(source_id='ggl_chronology',source_locator=f'line{ln}',reason='unexpected_price_columns',raw_json=json.dumps(line)));continue
    for geo,token in zip(['Lucknow','Agra','Ayodhya & Sultanpur','Unnao'],tokens):
        if token=='Sale not commenced':EX.append(dict(source_id='ggl_chronology',source_locator=f'line{ln}:{geo}',reason='sales_not_commenced',raw_json=token));continue
        d=dates(m[1]);note='Official chronology source claim; public release date unknown.'
        if '*' in token and geo=='Lucknow':
            assert '24.07.2026' in text
            d['effective_date']='2026-07-24';d['date_status']='explicit_source_footnote_overrides_row';note+=' Source footnote overrides 18.07.2026 row for Lucknow only.'
        add('ggl_chronology',f'line{ln}:{geo}',geo,float(token.replace('*','')),operator='Green Gas Limited',geography_type='operator_named_GA',raw_cells_json=json.dumps([m[1],token]),notes=note,**d)

geos={0:'Nanded GA',1:'Nashik-Dhule District',2:'Nizamabad GA',3:'Pune Municipal Corporation',4:'Ramanagara GA',5:'Sindhudurg GA',6:'Valsad (Kaprada Tehsil)'}
for i,geo in geos.items():
    sid=f'mngl_history_{i}'
    with pdfplumber.open(SOURCES[sid]['original_path']) as pdf:
        for pn,page in enumerate(pdf.pages,1):
            for tn,table in enumerate(page.extract_tables(),1):
                for rn,c in enumerate(table,1):
                    if not c or not c[0] or not re.search(r'\d',c[0]):continue
                    raw=' '.join(c[0].split())
                    for ci,name in [(1,geo)]+([(2,'Pimpri-Chinchwad Municipal Corporation')] if i==3 else []):
                        if len(c)<=ci or not c[ci]:continue
                        m=re.fullmatch(r'\s*(\d+(?:\.\d+)?)\s*(?:/-)?\s*',c[ci])
                        if not m:continue
                        add(sid,f'page{pn}:table{tn}:row{rn}:col{ci+1}',name,float(m[1]),operator='Maharashtra Natural Gas Limited',geography_type='operator_named_GA',raw_cells_json=json.dumps(c,ensure_ascii=False),notes='CNG columns selected by table geometry. No filling merged PCMC cells; overnight or month-only dates remain imprecise.',**dates(raw))

# Retain parliamentary interval extraction as explicit prior extraction evidence.
# Check each token against the original page rather than blindly promoting it.
parliament_checks=[]
oldrows=list(csv.DictReader((OLD/'structured/parliamentary_price_intervals.csv').open(encoding='utf-8-sig')))
pdfs={sid:PdfReader(SOURCES[sid]['original_path']) for sid in ['parliament_2010_floor','parliament_2012_floor']}
for r in oldrows:
    sid=r['source_id'];pno=int(re.search(r'pdf_page(\d+)',r['source_locator'])[1]);tx=pdfs[sid].pages[pno-1].extract_text() or ''
    token_present=r['effective_date_raw'] in tx and re.search(r'(?<!\d)'+re.escape(r['price'])+r'(?:0)?(?!\d)',tx) is not None
    parliament_checks.append(dict(source_id=sid,source_locator=r['source_locator'],original_date_token=r['effective_date_raw'],price=r['price'],date_and_price_tokens_on_source_page=bool(token_present),verification_limit='Page-token reconciliation does not independently validate prior geographic association or source date consistency.'))
    add(sid,r['source_locator'],r['geography_name'],float(r['price']),operator=r['operator'],geography_type='parliamentary_price_market',publication_date=r['publication_date'],observation_type='parliamentary_interval_claim_requires_geography_review',extraction_status='prior_extraction_page_tokens_checked' if token_present else 'prior_extraction_requires_review',notes=r['notes']+' Geographic association not independently revalidated; exclude from accepted target path pending manual review.',**{k:r[k] for k in ['effective_date','effective_month','effective_window_start','effective_window_end','effective_date_raw','date_status']})

# Semantic duplicate key includes original source content and all price/geography/date
# fields. Merge exact repeated source claims; preserve locator aliases for lineage.
canonical={};duplicates=[]
KEY=['source_sha256','geography_name','operator','ga_id','district','state','price_inr_kg','effective_date','effective_month','effective_window_start','effective_window_end','effective_date_raw','snapshot_month','observation_type','raw_cells_json']
for r in OBS:
    k=tuple(str(r[x]) for x in KEY)
    if k in canonical:
        duplicates.append(dict(duplicate_observation_id=r['observation_id'],canonical_observation_id=canonical[k]['observation_id'],source_id=r['source_id'],duplicate_locator=r['source_locator'],canonical_locator=canonical[k]['source_locator'],reason='same_source_hash_geography_date_price_claim'))
    else:canonical[k]=r
dedup=list(canonical.values())
# Components use the same canonical observation identity. Duplicate raw-row
# locations remain in the alias register rather than becoming orphan records.
duplicate_ids={r['duplicate_observation_id'] for r in duplicates}
CELLS=[r for r in CELLS if r['observation_id'] not in duplicate_ids]
coverage=[]
for k in sorted({(r['source_id'],r['operator'],r['geography_name']) for r in dedup}):
    rs=[r for r in dedup if (r['source_id'],r['operator'],r['geography_name'])==k];ds=sorted(r['effective_date'] for r in rs if r['effective_date']);ms=sorted(r['snapshot_month'] for r in rs if r['snapshot_month'])
    coverage.append(dict(source_id=k[0],operator=k[1],geography_name=k[2],observations=len(rs),earliest_exact_effective_date=ds[0] if ds else '',latest_exact_effective_date=ds[-1] if ds else '',first_snapshot_month=ms[0] if ms else '',last_snapshot_month=ms[-1] if ms else '',complete_price_path_verified=False,publication_dates_known=sum(bool(r['publication_date']) for r in rs),limitation='Counts and endpoints do not establish continuity or independent truth.'))

for sid,s in SOURCES.items():assert sha(Path(s['original_path']))==s['sha256'],sid
write('structured/source_price_observations.csv',dedup,FIELDS)
write('structured/pngrb_price_components.csv',CELLS)
write('metadata/source_manifest.csv',list(SOURCES.values()))
write('metadata/source_cell_exclusions.csv',EX,['source_id','source_locator','reason','raw_json'])
write('metadata/pngrb_schema_repairs.csv',REP)
write('metadata/pngrb_table_schema.csv',SCHEMA)
write('metadata/igl_source_cell_audit.csv',cell_audit)
write('metadata/source_claim_duplicates.csv',duplicates,['duplicate_observation_id','canonical_observation_id','source_id','duplicate_locator','canonical_locator','reason'])
write('metadata/source_market_coverage.csv',coverage)
write('metadata/parliament_page_token_checks.csv',parliament_checks)
summary=dict(source_observations_before_dedup=len(OBS),canonical_source_observations=len(dedup),exact_source_claim_duplicates=len(duplicates),source_counts=Counter(r['source_id'] for r in OBS),pngrb_schema_repairs=len(REP),pngrb_component_status=Counter(r['component_status'] for r in CELLS),igl_cell_status=Counter(r['value_class'] for r in cell_audit),date_status=Counter(r['date_status'] for r in dedup),sources_verified_by_hash=len(SOURCES),stage3_price_path_accepted=False,stage4_started=False)
(B/'metadata/repair_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps(summary,indent=2,ensure_ascii=False))
