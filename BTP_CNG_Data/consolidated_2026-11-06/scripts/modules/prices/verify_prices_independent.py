"""Independent source-to-record audit; no import from repair implementation."""
from pathlib import Path
from bs4 import BeautifulSoup
from decimal import Decimal,InvalidOperation
from datetime import date
import csv,json,hashlib,re,calendar
import openpyxl

B=Path(__file__).resolve().parent
def read(n):return list(csv.DictReader((B/n).open(encoding='utf-8-sig')))
manifest=read('metadata/source_manifest.csv');sources={r['source_id']:r for r in manifest}
obs=read('structured/source_price_observations.csv')
repairs=read('metadata/pngrb_schema_repairs.csv')
components=read('structured/pngrb_price_components.csv')
assert len({r['observation_id'] for r in obs})==len(obs)
for r in manifest:assert hashlib.sha256(Path(r['original_path']).read_bytes()).hexdigest()==r['sha256']

soup=BeautifulSoup(Path(sources['pngrb_prices']['original_path']).read_bytes(),'html.parser')
rawrows={}
for t in soup.find_all('table',id=re.compile('^CngPrice')):
    for i,tr in enumerate(t.find_all('tr')[1:],2):
        rawrows[f'{t["id"]}/tr{i}']=[' '.join(td.get_text(' ',strip=True).split()) for td in tr.find_all(['td','th'],recursive=False)]

def expected(c,loc):
    # Separate implementation, explicit documented source-schema variants.
    if loc.split('/')[0] in ['CngPriceJan26','CngPriceDec']:
        assert len(c)==15 and c[-1]==''
        return dict(operator=c[0],geography_name=c[1],district=c[2],state=c[3],price_inr_kg=Decimal(c[5].replace(',','')),ga_id='')
    return dict(ga_id=c[0],operator=c[1],geography_name=c[2],district=c[3],state=c[4],price_inr_kg=Decimal(c[6].replace(',','')))

def agree(rec):
    x=expected(rawrows[rec['source_locator']],rec['source_locator'])
    return all(Decimal(rec[k])==v if k=='price_inr_kg' else rec[k]==v for k,v in x.items())
pn=[r for r in obs if r['source_id']=='pngrb_prices']
assert len(components)==len(pn)
assert {r['observation_id'] for r in components}=={r['observation_id'] for r in pn}
for r in pn:
    assert agree(r),(r['source_locator'],r)
    assert not re.fullmatch(r'\d{1,2}/\d{1,2}/\d{2,4}',r['state'])
    assert r['publication_date']==''
    if r['date_status']=='ambiguous_or_invalid_numeric_date':assert r['effective_date']==''
for r in components:
    e=expected(rawrows[r['source_locator']],r['source_locator'])
    assert Decimal(r['retail_price_inr_kg'])==e['price_inr_kg']
    assert r['state']==e['state'] and r['operator']==e['operator']

sample=next(r for r in pn if r['source_locator']=='CngPriceJan26/tr2')
assert sample['operator']=='GAIL Gas Limited' and sample['state']=='Madhya Pradesh' and Decimal(sample['price_inr_kg'])==96
bad=dict(sample,price_inr_kg='999')
assert not agree(bad),'Independent check must reject deliberately changed value'

wb=openpyxl.load_workbook(sources['igl_chronology']['original_path'],data_only=True,read_only=True)
sheet=wb['CNG Price'];market_names=[sheet.cell(4,c).value for c in range(3,17)]
expected_positive={};numeric_string_locs=[]
for row in sheet.iter_rows(min_row=5,max_row=112,min_col=3,max_col=16):
    for cell in row:
        if cell.value is None:continue
        try:v=Decimal(str(cell.value).replace('\xa0','').strip())
        except InvalidOperation:continue
        if v>0:
            expected_positive['CNG Price!'+cell.coordinate]=v
            if isinstance(cell.value,str):numeric_string_locs.append('CNG Price!'+cell.coordinate)
igl=[r for r in obs if r['source_id']=='igl_chronology']
assert len(igl)==len(expected_positive)==695
for r in igl:assert Decimal(r['price_inr_kg'])==expected_positive[r['source_locator']]
assert len(numeric_string_locs)==5
assert set(numeric_string_locs)<=set(r['source_locator'] for r in igl)
wb.close()

late=[]
for r in pn:
    if r['effective_date'] and r['snapshot_month']:
        y,m=map(int,r['snapshot_month'].split('-'));month_end=date(y,m,calendar.monthrange(y,m)[1]).isoformat()
        if r['effective_date']>month_end:late.append(dict(observation_id=r['observation_id'],source_locator=r['source_locator'],snapshot_month=r['snapshot_month'],effective_date=r['effective_date'],source_date_raw=r['effective_date_raw'],status='unambiguous_source_revision_after_snapshot_month_do_not_silently_fix'))
with (B/'metadata/revision_after_snapshot.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['observation_id','source_locator','snapshot_month','effective_date','source_date_raw','status']);w.writeheader();w.writerows(late)
assert not list((B/'structured').glob('*monthly*')),'Stage 4 target construction prohibited'
receipt=dict(raw_hashes_passed=len(manifest),canonical_rows=len(obs),pngrb_source_rows_independently_reconciled=len(pn),component_rows_independently_reconciled=len(components),corrected_mapping_rows=len(repairs),invalid_date_states_after_repair=0,igl_positive_cells_independently_reconciled=len(igl),new_numeric_string_quotes_retained=numeric_string_locs,deliberately_corrupted_price_rejected=True,source_revision_after_snapshot_count=len(late),structural_and_transcription_checks_passed=True,critical_limitations=['Source-level truth and complete price paths remain uncertified','Publication dates for operator chronologies unknown','Parliamentary geographic extraction retained as provisional prior evidence','MNGL overnight windows and invalid source calendar dates remain unresolved','Snapshot arithmetic conflicts remain source claims, not corrected observations'],stage3_price_path_accepted=False,stage4_started=False)
(B/'logs/independent_validation_receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt,indent=2))
