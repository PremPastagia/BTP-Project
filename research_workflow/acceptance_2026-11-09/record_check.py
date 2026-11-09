"""Record a real check, preserving the old register and an append-only event log."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse,csv,json,os,shutil,tempfile
from check_acceptance import HERE,sha,resolve,read_register,verify_records

def main():
    policy=json.loads((HERE/'acceptance_policy.json').read_text())
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--requirement-id',required=True)
    ap.add_argument('--verdict',required=True,choices=policy['allowed_verdicts'])
    ap.add_argument('--method',required=True)
    ap.add_argument('--observed',required=True)
    ap.add_argument('--run-id',required=True)
    ap.add_argument('--artifact')
    ap.add_argument('--evidence')
    ap.add_argument('--limitations')
    ap.add_argument('--corrective-action')
    a=ap.parse_args();register=HERE/'acceptance_register.csv';before_hash=sha(register)
    fields,records=read_register(register)
    hits=[r for r in records if r['requirement_id']==a.requirement_id]
    if len(hits)!=1:ap.error('Unknown or duplicate requirement ID')
    r=hits[0];previous=dict(r);stamp=datetime.now(ZoneInfo('Asia/Kolkata'))
    r.update(verdict=a.verdict,check_method=a.method,observed_result=a.observed,run_id=a.run_id,
             executed_at_with_timezone='' if a.verdict=='NOT RUN' else stamp.isoformat())
    if a.artifact:
        p=resolve(a.artifact)
        if not p.is_file():ap.error('Artifact must exist; record missing dependencies as BLOCKED using an actual failure/access receipt')
        r.update(actual_artifact_path=a.artifact,artifact_sha256=sha(p))
    if a.evidence:r['evidence_path']=a.evidence
    if a.limitations is not None:r['limitations']=a.limitations
    if a.corrective_action is not None:r['corrective_action']=a.corrective_action
    errors=verify_records(fields,records,policy)
    if errors:ap.error('; '.join(errors))
    history=HERE/'history';history.mkdir(exist_ok=True)
    tag=stamp.strftime('%Y%m%dT%H%M%S%f%z')
    archived=history/f'register_before_{tag}_{before_hash[:12]}.csv'
    # Concurrency guard prevents overwriting another reviewer's update.
    if sha(register)!=before_hash:raise RuntimeError('Register changed concurrently; reread before recording')
    shutil.copy2(register,archived)
    fd,name=tempfile.mkstemp(prefix='register_',suffix='.tmp',dir=HERE)
    with os.fdopen(fd,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(records)
    if sha(register)!=before_hash:
        Path(name).unlink();raise RuntimeError('Register changed concurrently; update was not applied')
    os.replace(name,register)
    event=dict(timestamp_with_timezone=stamp.isoformat(),requirement_id=a.requirement_id,previous=previous,current=r,
               register_before_sha256=before_hash,register_after_sha256=sha(register),preserved_before=str(archived.relative_to(HERE)),
               evidence_sha256=sha(resolve(r['evidence_path'])) if r['evidence_path'] and resolve(r['evidence_path']).is_file() else None,
               scientific_review_note='The author of this entry is responsible for actual evidence and meaning; this tool does not certify scientific truth.')
    with (HERE/'check_history.jsonl').open('a') as f:f.write(json.dumps(event)+'\n')
    print('Recorded',a.requirement_id,a.verdict,'with preserved previous register')
if __name__=='__main__':main()
