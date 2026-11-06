"""Independent native PDF cell/date verification before historical as-of use."""
from pathlib import Path
from decimal import Decimal
import argparse, csv, json, re, hashlib, subprocess, datetime

def verify(table,pdf):
    source_hash=hashlib.sha256(pdf.read_bytes()).hexdigest()
    records=list(csv.DictReader(table.open(encoding='utf-8-sig')))
    relevant=[r for r in records if r['family']=='national_accounts_quarterly']
    assert relevant and {r['raw_sha256'] for r in relevant}=={source_hash}
    cells={};checks=[]
    for page,basis in [(15,'constant_2022_23'),(17,'current')]:
        text=subprocess.check_output(['pdftotext','-f',str(page),'-l',str(page),'-layout',str(pdf),'-'],text=True)
        assert re.search(r'4:00 PM of 5th June, 2026',text),'Explicit release embargo not verified'
        assert all(x in text for x in ['2022-23','2023-24','2024-25','2025-26'])
        assert re.search(r'Values are.*Crore',text),'Source units not confirmed'
        if basis=='current':assert 'Current Prices' in text
        else:assert 'Constant Prices' in text
        gdp_lines=[line for line in text.splitlines() if re.match(r'^\s*GDP\s+\d',line)]
        pfce_lines=[line for line in text.splitlines() if 'Private Final Consumption Expenditure (PFCE)' in line]
        assert gdp_lines and len(pfce_lines)==1
        def values(line):
            tokens=re.findall(r'\b\d[\d,]*\b',line)
            assert len(tokens)>=16
            return [Decimal(t.replace(',','')) for t in tokens[-16:]]
        gdp=values(gdp_lines[0]);pfce=values(pfce_lines[0])
        assert all(values(line)==gdp for line in gdp_lines),'Repeated GDP lines disagree'
        for idx in range(16):
            fy=2022+idx//4;q=idx%4
            year=fy if q<3 else fy+1;month=[4,7,10,1][q]
            period=f'{year:04d}-{month:02d}-01'
            for var,vs in [('gdp',gdp),('pfce',pfce)]:cells[(var+':'+basis,period)]=vs[idx]
    for r in relevant:
        expected=cells[(r['series'],r['period'])]
        assert Decimal(r['value'])==expected,(r['series'],r['period'],r['value'],str(expected))
        assert r['publication_date']=='2026-06-05'
        checks.append({'observation_id':r['observation_id'],'series':r['series'],'period':r['period'],'value':r['value'],'source_page':r['source_locator'],'source_sha256':source_hash,'exact_cell_match':True})
    assert len(checks)==len(cells)==64
    return {'source_sha256':source_hash,'source_pdf':str(pdf),'native_table_sha256':hashlib.sha256(table.read_bytes()).hexdigest(),'release_timestamp':'2026-06-05T16:00:00+05:30','release_basis':'Explicit source PDF embargo: publication/telecast/internet circulation barred until 4:00 PM of 5th June 2026. This validates this release vintage, not earlier vintages.','value_checks':checks,'all_checks_passed':True,'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--native-table',type=Path,required=True);p.add_argument('--source-pdf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=verify(a.native_table,a.source_pdf);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2));print(json.dumps({'checked_cells':len(result['value_checks']),'release':result['release_timestamp'],'passed':True}))
