"""Independently decode official listing/native PDF claims; sensitivity tier only."""
from pathlib import Path
from decimal import Decimal
from datetime import datetime,date,timezone
from collections import defaultdict,Counter
import csv,json,re,hashlib,subprocess,argparse,urllib.parse
from bs4 import BeautifulSoup

def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,rs,fields):
    with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs)
def normurl(u):
    q=urllib.parse.urlsplit(u);return urllib.parse.urlunsplit((q.scheme,q.netloc.removeprefix('www.'),q.path,q.query,''))

def run(a):
    out=a.output;assert (out/'registry/S4-PRED-RECON-20261109-001.json').is_file()
    objects=read(a.candidate/'metadata/raw_objects.csv');source_inputs=[];listings=defaultdict(list)
    for r in objects:
        if not any(s.startswith('ppac_gas_price_page_') for s in json.loads(r['source_ids'])):continue
        p=a.candidate/r['path'];assert sha(p)==r['sha256'];source_inputs.append({'path':r['path'],'sha256':r['sha256'],'role':'official_listing_capture','source_urls':r['source_urls']})
        soup=BeautifulSoup(p.read_bytes(),'html.parser')
        for link in soup.find_all('a',href=True):
            if 'download.php?file=gasprice/' not in link['href']:continue
            parent=link.find_parent('div',class_='right-info-col')
            if parent is None:continue
            text=parent.get_text(' ',strip=True);m=re.match(r'(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})\s+(.+?)\s+Size:',text)
            if not m:continue
            try:d=datetime.strptime(m[1],'%d %b %Y').date().isoformat()
            except ValueError:continue
            listings[normurl(link['href'])].append({'date':d,'title':m[2],'archive_sha256':r['sha256'],'archive_path':r['path'],'card_text':text})
    candidates=[r for r in read(a.candidate/'structured/numerical_factors/unverified_transcription_candidates.csv') if r['series'].startswith('fresh_monthly:')]
    outputs=[];gaps=[];cache={};warnings={};months='January February March April May June July August September October November December'.split();monthpattern='|'.join(months)
    for r in candidates:
        found=listings.get(normurl(r['source_url']),[]);dates={x['date'] for x in found}
        p=a.candidate/r['raw_object_path'];assert sha(p)==r['raw_sha256']
        if r['raw_sha256'] not in cache:
            extraction=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,text=True)
            cache[r['raw_sha256']]=extraction.stdout;warnings[r['raw_sha256']]=extraction.stderr.strip()
            if extraction.returncode:warnings[r['raw_sha256']]='nonzero_exit='+str(extraction.returncode)+'; '+warnings[r['raw_sha256']]
            source_inputs.append({'path':r['raw_object_path'],'sha256':r['raw_sha256'],'role':'official_original_notification','source_urls':json.dumps([r['source_url']])})
        text=' '.join(cache[r['raw_sha256']].split())
        role='notified_calculated_domestic_formula_price' if r['series'].endswith('notified_domestic_formula_price') else 'nomination_field_explicit_ceiling'
        pat=r'notified\s+as\s+US\s*\$\s*(\d+(?:\.\d+)?)' if role.startswith('notified') else r'ceiling\s+of\s+US\s*\$\s*(\d+(?:\.\d+)?)'
        vals=[Decimal(x) for x in re.findall(pat,text,re.I)]
        role_match=bool(vals) and set(vals)=={Decimal(r['value'])}
        basis_match=bool(re.search(r'Gross\s+Calorific\s+Value|\bGCV\b',text,re.I))
        date_matches=[]
        for x in found:
            ds=re.findall(r'(\d{1,2})\s*(?:st|nd|rd|th|\'st|\'th)?\s*('+monthpattern+r')\s*(\d{4})',x['title'],re.I)
            if len(ds)==2:
                try:
                    decoded=[datetime.strptime(' '.join(d),'%d %B %Y').date().isoformat() for d in ds]
                    if decoded==[r['effective_date'],r['effective_end_date']]:date_matches.append(x)
                except ValueError:pass
        native_period_words=all(re.search(datetime.fromisoformat(r[k]).strftime('%B')+r'\s*'+r[k][:4],text,re.I) for k in ['effective_date','effective_end_date'])
        passed=role_match and basis_match and bool(date_matches) and len(dates)==1 and native_period_words and not warnings[r['raw_sha256']]
        rec={'candidate_observation_id':r['observation_id'],'source_id':r['source_id'],'variable':role,'geography':'India_regulatory_nomination_or_domestic_formula_scope','native_frequency':'notified_monthly_interval','effective_start':r['effective_date'],'effective_end':r['effective_end_date'],'value':r['value'],'unit':'USD_per_MMBTU_GCV','legacy_publication_claim':r['publication_date'],'official_archive_date_claim':next(iter(dates)) if len(dates)==1 else '', 'source_url':r['source_url'],'notification_sha256':r['raw_sha256'],'notification_object_path':r['raw_object_path'],'archive_capture_hashes':json.dumps(sorted({x['archive_sha256'] for x in found})),'archive_object_paths':json.dumps(sorted({x['archive_path'] for x in found})),'native_PDF_role_value_verified':role_match,'native_PDF_GCV_basis_verified':basis_match,'archive_title_interval_verified':bool(date_matches),'PDF_month_year_words_verified':native_period_words,'PDF_decode_warning':warnings[r['raw_sha256']],'claim_checks_passed':passed,'strict_historical_eligible':False,'sensitivity_eligible':passed,'availability_tier':'qualified_official_listing_date_proxy_sensitivity_only' if passed else 'requires_manual_source_review','availability_rule':'If explicitly approved later, use end of official archive listed day in Asia/Kolkata, never before that day; do not substitute an assumed fixed lag.','historical_vintage_limitation':'Archive HTML captured in Nov2026 is a retrospective source date claim, not independently archived proof of historical bytes/public availability.','cost_definition_limit':'Formula price or nomination-block cap is not actual blended CGD procurement cost.'}
        outputs.append(rec)
        if not passed:gaps.append({'candidate_observation_id':r['observation_id'],'source_id':r['source_id'],'role_match':role_match,'basis_match':basis_match,'archive_dates':json.dumps(sorted(dates)),'title_interval_match':bool(date_matches),'native_period_words':native_period_words,'PDF_decode_warning':warnings[r['raw_sha256']],'decision':'not_admitted_even_to_qualified_sensitivity_ledger'})
    write(out/'ppac_native_release_claims.csv',outputs,list(outputs[0]));write(out/'ppac_source_gaps.csv',gaps,['candidate_observation_id','source_id','role_match','basis_match','archive_dates','title_interval_match','native_period_words','PDF_decode_warning','decision']);write(out/'ppac_input_hashes.csv',source_inputs,['path','sha256','role','source_urls'])
    qualified=[r for r in outputs if r['sensitivity_eligible']]
    summary={'executed_at_utc':datetime.now(timezone.utc).isoformat(),'fresh_monthly_candidates_audited':len(outputs),'native_PDFs_checked':len(cache),'official_listing_captures_checked':sum(r['role']=='official_listing_capture' for r in source_inputs),'passed_native_role_value_and_listing_interval_checks':len(qualified),'strict_historical_admissions':0,'qualified_exploration_release_claims':sum(r['official_archive_date_claim']<'2025-11-01' for r in qualified),'qualified_variables':dict(Counter(r['variable'] for r in qualified)),'first_qualified_effective_start':min((r['effective_start'] for r in qualified),default=''),'last_qualified_effective_end':max((r['effective_end'] for r in qualified),default=''),'no_fixed_lag_or_filling':True,'no_models_or_statistical_tests':True,'original_stage3_and_prior_stage4_unchanged':True,'interpretation':'Potential exploratory H1 source material recovered at a qualified sensitivity tier only. No strict real-time archival-vintage proof or company-cost equivalence is claimed.'}
    (out/'ppac_audit_results.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);run(p.parse_args())
