"""Selected independent native-source check using pypdf, not producer Poppler.

The manually specified examples check monetary roles, not historical web vintages.
"""
from pathlib import Path
from decimal import Decimal
import csv,datetime,hashlib,json,re,argparse
from pypdf import PdfReader

HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1]
EXAMPLES=[('notified_calculated_domestic_formula_price','2023-05','8.27','30.04.2023'),
          ('notified_calculated_domestic_formula_price','2025-01','7.30','31.12.2024'),
          ('nomination_field_explicit_ceiling','2024-04','6.50','31.03.2024')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=HERE/'metadata/selected_ppac_check.json');a=ap.parse_args()
    if a.output.exists():raise FileExistsError('Preserve previous verification receipt')
    rows=list(csv.DictReader((HERE/'predictor_reconciliation/ppac_native_release_claims.csv').open()))
    objects=list(csv.DictReader((HERE/'predictor_reconciliation/ppac_input_hashes.csv').open()))
    out=[]
    for role,month,expected,signed_date in EXAMPLES:
        r=next(r for r in rows if r['variable']==role and r['effective_start'].startswith(month) and r['claim_checks_passed']=='True')
        p=ROOT/'BTP_CNG_Data/consolidated_2026-11-06'/next(x['path'] for x in objects if x['sha256']==r['notification_sha256'])
        if sha(p)!=r['notification_sha256']:raise ValueError('Source hash changed')
        text=' '.join(' '.join(page.extract_text() or '' for page in PdfReader(p).pages).split())
        phrase='notified as' if role.startswith('notified_') else 'ceiling of'
        clause=text.lower().split(phrase,1)[1].split('mmbtu',1)[0]
        amounts=re.findall(r'\d+(?:\.\d+)?',clause)
        if len(amounts)!=1 or Decimal(amounts[0])!=Decimal(expected) or Decimal(r['value'])!=Decimal(expected):raise ValueError('Value/role mismatch')
        if signed_date not in text or 'Gross Calorific Value' not in text:raise ValueError('Date/unit basis mismatch')
        out.append(dict(candidate_id=r['candidate_observation_id'],notification_sha256=sha(p),role=role,value=expected,
                        unit='USD/MMBTU_GCV',effective_start=r['effective_start'],signed_document_date=signed_date,
                        archive_publication_day_claim=r['official_archive_date_claim'],arithmetic_and_role_check_passed=True,
                        availability_conclusion='Retrospective archive date claim only; signed date does not establish historical public availability'))
    receipt=dict(timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),implementation='pypdf independent decode and manually specified role/value/date examples; no producer helper',
                 source_examples=out,all_passed=True,scope='3 selected examples, not a verification of every PPAC candidate or vintage',
                 important_boundary='January2025 PDF signed31Dec2024 has archive-listed date1Jan2025. Do not assign31Dec public availability from signature.',strict_historical_admissions=0)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(receipt,indent=2));print('3 selected PPAC native monetary-role/date checks passed; historical vintage not established')
if __name__=='__main__':main()
