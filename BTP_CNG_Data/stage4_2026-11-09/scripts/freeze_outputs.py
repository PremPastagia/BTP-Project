"""Verify independent receipts and immutable inputs, then checksum this delivery.

No empirical quantities are recomputed or changed here. Audit journals may grow
only by explicitly limited, append-only source-journal links after scientific review.
"""
from pathlib import Path
import csv,datetime,hashlib,json,subprocess
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1];DATA=ROOT/'BTP_CNG_Data'
ACCEPTED=DATA/'accepted_stage3_2026-11-06_restricted_v1'
EXPECTED_ACCEPTED_MANIFEST='968d4ad2b34c444ab6e4c9da33eae5b0c9c14bde7c01d308084136874ce3cea3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def verify_manifest(base,records):
    if isinstance(records,dict):records=[dict(path=k,sha256=v) for k,v in records.items()]
    if not isinstance(records,list) or not records:raise ValueError('Unsupported/empty checksum manifest')
    for r in records:
        p=base/r['path']
        if not p.is_file() or sha(p)!=r['sha256']:raise ValueError('Checksum mismatch: '+str(p))
        if 'bytes' in r and p.stat().st_size!=r['bytes']:raise ValueError('Size mismatch: '+str(p))
    return len(records)
def main():
    checks=[]
    if sha(ACCEPTED/'metadata/snapshot_manifest.json')!=EXPECTED_ACCEPTED_MANIFEST:raise ValueError('Accepted manifest identity changed')
    n=verify_manifest(ACCEPTED,load(ACCEPTED/'metadata/snapshot_manifest.json'))
    checks.append(dict(check='accepted_snapshot_unchanged',files=n,passed=True))
    previous=DATA/'stage4_2026-11-06';n=verify_manifest(previous,load(previous/'metadata/output_manifest.json'))
    changes=subprocess.check_output(['git','-C',str(ROOT),'diff','--name-only','HEAD','--',str(ACCEPTED),str(previous)],text=True)
    if changes.strip():raise ValueError('Original accepted/prior Stage4 tracked files changed: '+changes)
    checks.append(dict(check='previous_stage4_unchanged',files=n,git_diff_empty=True,passed=True))
    # Check raw sources actually supporting accepted prices, without re-downloading archives.
    pricehashes={r['source_sha256'] for r in rows(ACCEPTED/'data/price_intervals.csv')}
    refs={r['sha256']:r for r in rows(ACCEPTED/'metadata/source_object_refs.csv')}
    for h in pricehashes:
        r=refs[h];p=DATA/r['candidate_collection']/r['candidate_object_path']
        if sha(p)!=h:raise ValueError('Price source object changed')
    checks.append(dict(check='accepted_price_raw_source_objects',objects=len(pricehashes),passed=True))
    for relative,manifest in [('project_reconciliation','output_checksums.json'),
                              ('project_reconciliation/independent_eda_audit','output_checksums.json'),
                              ('predictor_reconciliation','output_manifest.json')]:
        base=HERE/relative;n=verify_manifest(base,load(base/manifest));checks.append(dict(check=relative+'_manifest',files=n,passed=True))
    pcheck=load(HERE/'predictor_reconciliation/audit_integrity_checks.json')
    if not pcheck['all_checks_passed'] or any(not r['passed'] for r in pcheck['checks']):raise ValueError('Predictor integrity failed')
    echeck=load(HERE/'project_reconciliation/independent_eda_audit/result.json')
    if echeck['failed'] or echeck['passed']!=echeck['checks']:raise ValueError('Independent EDA failed')
    review=load(HERE/'reconciliation_targets/END_STAGE4_REDO_REVIEW.json')
    if review['critical_failures'] or review['passed']!=review['check_count'] or review['required_report_amendments_remaining']:
        raise ValueError('End-stage independent review failed')
    append_counts={}
    for rel,r in review['input_hashes'].items():
        p=HERE/rel
        if not p.is_file():raise ValueError('Reviewed input missing: '+rel)
        if sha(p)==r['sha256'] and p.stat().st_size==r['bytes']:continue
        # Registry-link metadata is necessarily appended after receipt creation.
        # Verify the audited byte prefix exactly, not merely the old record IDs.
        if rel!='metadata/experiment_registry.jsonl':raise ValueError('Reviewed input changed: '+rel)
        b=p.read_bytes();prefix=b[:r['bytes']]
        if hashlib.sha256(prefix).hexdigest()!=r['sha256']:raise ValueError('Audited registry history changed')
        appended=[json.loads(s) for s in b[r['bytes']:].decode().splitlines() if s.strip()]
        if not appended or any(x.get('status')!='completed_source_journal_link' for x in appended):raise ValueError('Unaudited empirical registry addition')
        append_counts[rel]=len(appended)
    checks.append(dict(check='independent_scientific_review_inputs_unchanged_or_permitted_append_only_links',files=len(review['input_hashes']),appended_metadata_links=append_counts,passed=True))
    registry=[json.loads(s) for s in (HERE/'metadata/experiment_registry.jsonl').read_text().splitlines() if s.strip()]
    if len({r['experiment_id'] for r in registry})!=len(registry):raise ValueError('Duplicate registry IDs')
    for group in load(HERE/'metadata/audit_registry_links.json'):
        verify_manifest(HERE,group['records'])
    checks.append(dict(check='master_journal_unique_ids_and_source_links',records=len(registry),passed=True))
    inputs=rows(HERE/'predictor_reconciliation/ppac_input_hashes.csv')
    for r in inputs:
        if sha(DATA/'consolidated_2026-11-06'/r['path'])!=r['sha256']:raise ValueError('PPAC source changed')
    checks.append(dict(check='PPAC_raw_source_objects_unchanged',objects=len(inputs),passed=True))
    pairs=rows(HERE/'metadata/horizon_coverage.csv')
    calendar_rows=rows(HERE/'analysis/coverage_calendar.csv')
    monthindex=lambda s:int(s[:4])*12+int(s[5:])
    for r in pairs:
        cr={monthindex(x['year_month']):x for x in calendar_rows if x['city']==r['city']}
        h=int(r['horizon_months']);target=r['target']
        supported=[(x,cr[k+h]) for k,x in cr.items() if k+h in cr and x[target] and cr[k+h][target]]
        if len(supported)!=int(r['all_supported_target_pairs']):raise ValueError('Horizon coverage mismatch')
        if sum(x['sample_period']==y['sample_period']=='development' for x,y in supported)!=int(r['development_pairs']):raise ValueError('Development horizon mismatch')
    checks.append(dict(check='horizon_coverage_calendar_alignment',rows=len(pairs),passed=True))
    for p in HERE.rglob('*.py'):
        if '__pycache__' not in p.parts:compile(p.read_text(),str(p),'exec')
    checks.append(dict(check='delivered_python_syntax',passed=True))
    result=dict(verified_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_passed=True,checks=checks,
                independent_gate=review['decision'],forecasting_ready=False,stage5_started=False,
                note='Checksums establish artifact consistency; source/availability/scientific qualifications remain.')
    (HERE/'metadata/final_verification.json').write_text(json.dumps(result,indent=2))
    code={str(p.relative_to(HERE)):sha(p) for p in HERE.rglob('*.py') if '__pycache__' not in p.parts}
    (HERE/'metadata/code_lineage.json').write_text(json.dumps(code,indent=2))
    lines=['STAGE 4 REDO DELIVERY — VERIFIED 9 NOVEMBER 2026','',
           'Qualified analytical checkpoint completed. Researcher acceptance remains pending.',
           f"Independent scientific review: {review['passed']}/{review['check_count']} checks pass; no critical analytical failure.",
           f"Independent EDA: {echeck['passed']}/{echeck['checks']} arithmetic/eligibility checks pass.",
           'Final verification: all package, source-object, journal and immutable-input checks pass.',
           'Accepted Stage3 snapshot unchanged (9 manifest entries + pinned manifest identity).',
           'Previous Stage4 unchanged (91 manifest entries; no tracked modifications).',
           'Registry history remains append-only; later additions are source-journal links only.',
           'All target/availability/EDA inputs match the independently reviewed hashes.',
           'metadata/output_manifest.json binds all delivered files except itself.',
           'Git commit and remote branch supply the external immutable version identity.',
           '', 'Read STAGE4_REDO_CHECKPOINT_REPORT.txt for actual data, assumptions and limitations.',
           'No full ten-city readiness, strict development H1 coverage, H2 effect, untouched final',
           'test, exact intraday TWAP, forecasting result or causal conclusion is established.',
           'Stage5 has not started. Review the Stage4 checkpoint before advancing.']
    (HERE/'DELIVERY_STATUS.txt').write_text('\n'.join(lines)+'\n')
    manifest=[];dest=HERE/'metadata/output_manifest.json'
    for p in sorted(HERE.rglob('*')):
        if not p.is_file() or p==dest or '__pycache__' in p.parts or p.suffix=='.pyc':continue
        manifest.append(dict(path=str(p.relative_to(HERE)),sha256=sha(p),bytes=p.stat().st_size))
    dest.write_text(json.dumps(manifest,indent=2))
    print('Verified and froze',len(manifest),'files. Manifest SHA256:',sha(dest))
if __name__=='__main__':main()
