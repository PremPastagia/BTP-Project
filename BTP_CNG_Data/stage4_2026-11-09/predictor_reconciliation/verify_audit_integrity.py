"""Recompute audit provenance and separation checks; no outcome calculations."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import csv,json,hashlib,subprocess,argparse,calendar

def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(a):
    out=a.output;checks=[]
    def check(name,condition,detail):checks.append({'check':name,'passed':bool(condition),'detail':detail})
    audit=json.loads((out/'audit_results.json').read_text());prereg=json.loads((out/'registry/S4-PRED-RECON-20261109-001.json').read_text())
    check('preregistration_precedes_audit',prereg['registered_at_utc']<audit['executed_at_utc'],prereg['registered_at_utc'])
    bad=[];rs=read(out/'input_hashes.csv')
    for r in rs:
        if r['locator'].startswith('git:'):
            _,ref,path=r['locator'].split(':',2);data=subprocess.check_output(['git','-C',str(a.repo),'show',ref+':'+path]);h=hashlib.sha256(data).hexdigest()
        else:h=sha(Path(r['locator']))
        if h!=r['sha256']:bad.append(r['locator'])
    check('all_audited_input_hashes_rechecked',not bad,{'inputs':len(rs),'mismatches':bad})
    ppac=read(out/'ppac_native_release_claims.csv');ppinputs=read(out/'ppac_input_hashes.csv');candidate=a.repo/'BTP_CNG_Data/consolidated_2026-11-06'
    check('PPAC_original_input_hashes',all(sha(candidate/r['path'])==r['sha256'] for r in ppinputs),len(ppinputs))
    check('PPAC_tier_never_strict',all(r['strict_historical_eligible']=='False' for r in ppac),len(ppac))
    for r in ppac:
        if r['sensitivity_eligible']=='True':
            assert all(r[c]=='True' for c in ['native_PDF_role_value_verified','native_PDF_GCV_basis_verified','archive_title_interval_verified','PDF_month_year_words_verified']) and not r['PDF_decode_warning']
    check('qualified_PPAC_records_have_all_claim_checks',True,sum(r['sensitivity_eligible']=='True' for r in ppac))
    core=read(out/'core_origin_availability.csv');strict=read(out/'strict_core_asof_ledger.csv');proxy=read(out/'qualified_PPAC_core_reference.csv');keys={(r['city'],r['year_month']) for r in core}
    check('core_calendar_unique_and_strict_subset',len(keys)==len(core) and all((r['market'],r['month']) in keys for r in strict),len(core))
    check('strict_ledger_retains_all_time_and_vintage_qualifications',all(datetime.fromisoformat(r['publication_timestamp_bound'])<=datetime.fromisoformat(r['forecast_origin']) and r['historical_vintage_status'] and r['lagged_price_predictor_availability']=='not_certified_by_retrospective_outcome_acceptance' for r in strict),len(strict))
    for r in proxy:
        y,m=map(int,r['year_month'].split('-'));last=f'{y:04d}-{m:02d}-{calendar.monthrange(y,m)[1]:02d}'
        assert r['effective_start']<=last<=r['effective_end'] and r['official_archive_date_claim']<=last and r['strict_historical_eligible']=='False'
    check('qualified_PPAC_mapping_no_future_or_expired_holds',True,len(proxy))
    news=read(out/'news_reconciliation.csv');check('manual_news_seed_provenance_explicit',len(news)==10 and all(r['timestamp_is_code_literal']=='True' and r['hash_is_authored_headline_excerpt']=='True' and r['strict_H2_eligible']=='False' for r in news),len(news))
    var=read(out/'variable_eligibility_dictionary.csv');forbidden={'cng_price_monthend','cng_price_twap','min_price_month','max_price_month'}
    check('no_outcome_columns_in_predictor_comparison',not any(r['variable'] in forbidden for r in var) and not any(r['legacy_variable'] in forbidden for r in read(out/'legacy_native_value_matches.csv')),len(var))
    widths=[]
    for p in out.glob('*.csv'):
        with p.open(newline='',encoding='utf-8-sig') as f:
            rd=csv.reader(f);header=next(rd,[])
            if any(len(row)!=len(header) for row in rd):widths.append(p.name)
    check('all_output_CSV_widths_valid',not widths,widths)
    result={'verified_at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'all_checks_passed':all(r['passed'] for r in checks),'qualification':'Source/transcription/provenance checks are not proof of independent real-time historical vintages. No model or inferential test executed.'}
    (out/'audit_integrity_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));raise SystemExit(0 if result['all_checks_passed'] else 1)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--output',type=Path,required=True);run(p.parse_args())
