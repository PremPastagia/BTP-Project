"""Check register integrity and gating, not the scientific truth of its verdicts."""
from pathlib import Path
from datetime import datetime
import argparse,csv,hashlib,json,sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def resolve(s):
    p=Path(s);return p if p.is_absolute() else ROOT/p
def read_register(p):
    with p.open(newline='',encoding='utf-8-sig') as f:
        r=csv.DictReader(f);return r.fieldnames,list(r)
def verify_records(fields,records,policy):
    errors=[]
    if fields!=policy['schema_fields']:errors.append('Register schema differs from required fields/order')
    ids=[r.get('requirement_id','') for r in records]
    if len(ids)!=len(set(ids)):errors.append('Duplicate requirement IDs')
    if set(ids)!=set(policy['requirement_ids']):errors.append('Missing/unrecognized requirement IDs; record any design amendment explicitly')
    for r in records:
        rid=r.get('requirement_id','?');v=r.get('verdict','')
        if v not in policy['allowed_verdicts']:errors.append(rid+': invalid verdict')
        if not r.get('expected_result','').strip():errors.append(rid+': expected result absent')
        artifact=r.get('actual_artifact_path','');h=r.get('artifact_sha256','')
        if h:
            p=resolve(artifact)
            if not p.is_file() or sha(p)!=h:errors.append(rid+': indexed artifact missing/changed')
        if v in ['PASS','FAIL','N/A WITH REASON']:
            try:
                t=datetime.fromisoformat(r.get('executed_at_with_timezone',''))
                if t.utcoffset() is None:raise ValueError('timezone required')
            except ValueError:errors.append(rid+': executed timestamp must include timezone')
            if not r.get('run_id','').strip():errors.append(rid+': run ID required')
            if not r.get('observed_result','').strip():errors.append(rid+': actual observed result required')
            method=r.get('check_method','').lower()
            if not method.startswith(('automated:','manual:','mixed:')):errors.append(rid+': distinguish automated/manual/mixed method')
            evidence=r.get('evidence_path','')
            if not evidence or not resolve(evidence).is_file():errors.append(rid+': actual evidence file required')
        if v=='PASS':
            if not artifact or not h or not resolve(artifact).is_file() or resolve(artifact).stat().st_size==0:
                errors.append(rid+': PASS needs a nonempty identifiable actual artifact')
        if v=='N/A WITH REASON':
            if not r.get('limitations','').strip() or not r.get('corrective_action','').strip():
                errors.append(rid+': N/A needs explicit rationale, impact and scope/action in limitations/corrective_action')
    return errors
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--original-stage',type=int,choices=range(4,10))
    ap.add_argument('--gate',action='store_true',help='Return exit2 if selected requirements are pending/failed/blocked')
    ap.add_argument('--output',type=Path,help='Write a new receipt; existing receipt cannot be overwritten')
    a=ap.parse_args();policy=json.loads((HERE/'acceptance_policy.json').read_text())
    fields,records=read_register(HERE/'acceptance_register.csv');errors=verify_records(fields,records,policy)
    checklist=resolve(policy['checklist_path'])
    if not checklist.is_file() or sha(checklist)!=policy['checklist_sha256']:errors.append('Original imported checklist changed')
    mapping=list(csv.DictReader((HERE/'requirement_stage_mapping.csv').open()))
    if {r['requirement_id'] for r in mapping}!={r['requirement_id'] for r in records}:errors.append('Requirement-stage mapping incomplete')
    original={r['requirement_id']:{int(s) for s in r['governing_original_stages'].split(';')} for r in mapping}
    selected=[r for r in records if a.original_stage is None or a.original_stage in original.get(r['requirement_id'],set())]
    unmet=[dict(requirement_id=r['requirement_id'],verdict=r['verdict']) for r in selected if r['verdict'] not in ['PASS','N/A WITH REASON']]
    result=dict(checked_at_with_timezone=datetime.now().astimezone().isoformat(),register_sha256=sha(HERE/'acceptance_register.csv'),
                register_structure_valid=not errors,errors=errors,requirements_total=len(records),selected_original_stage=a.original_stage,
                selected_requirements=len(selected),verdict_counts={v:sum(r['verdict']==v for r in records) for v in policy['allowed_verdicts']},
                unmet=unmet,stage_gate_passed=not errors and bool(selected) and not unmet,
                scientific_acceptance='NOT ESTABLISHED by this structural validator. Inspect/recompute evidence and independent review; file/hash/schema success is insufficient.',
                researcher_approval_granted=False)
    if a.output:
        if a.output.exists():raise FileExistsError('Preserve earlier acceptance receipts')
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='unmet'},indent=2))
    if errors:return 1
    return 2 if a.gate and unmet else 0
if __name__=='__main__':sys.exit(main())
