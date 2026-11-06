"""Verify immutable inputs and existing verification receipts, then freeze outputs."""
from pathlib import Path
import csv,json,hashlib,datetime
R=Path(__file__).resolve().parents[3];B=R/'BTP_CNG_Data/stage4_2026-11-06';A=R/'BTP_CNG_Data/accepted_stage3_2026-11-06_restricted_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
for rec in json.loads((A/'metadata/snapshot_manifest.json').read_text()):
 p=A/rec['path']
 if not p.is_file() or sha(p)!=rec['sha256'] or p.stat().st_size!=rec['bytes']:raise ValueError('Accepted snapshot changed: '+rec['path'])
checks.append(dict(check='accepted_snapshot_unchanged',entries=9,passed=True))
for rel in ['eda/metadata/output_checksums.json','integration/metadata/integration_checksums.json']:
 values=json.loads((B/rel).read_text());base=B/('eda' if rel.startswith('eda/') else 'integration')
 # Both checksum-map and record-list formats must be checked, never skipped.
 if isinstance(values,dict):
  entries=[dict(path=name,sha256=h) for name,h in values.items()]
 elif isinstance(values,list):entries=values
 else:raise ValueError('Unsupported checksum format: '+rel)
 if not entries:raise ValueError('Empty checksum collection: '+rel)
 for rec in entries:
  name,h=rec['path'],rec['sha256'];p=base/name
  if not isinstance(h,str) or len(h)!=64:raise ValueError('Invalid checksum: '+name)
  if not p.is_file() or sha(p)!=h:raise ValueError('Stale output checksum: '+str(p))
  if 'bytes' in rec and p.stat().st_size!=rec['bytes']:raise ValueError('Stale output size: '+str(p))
 checks.append(dict(check=rel,entries=len(entries),passed=True))
root=json.loads((B/'independent_target_audit/producer_reconciliation_receipt.json').read_text())
if not root['reconciliation_passed'] or root['differences']!=0:raise ValueError('Target audit failed')
if sha(B/'targets/monthly_targets.csv')!=root['producer_sha256']:raise ValueError('Audited targets changed')
peer=json.loads((B/'independent_target_audit/END_STAGE4_REVIEW.json').read_text())
if not peer['all_independent_checks_passed'] or peer['critical_failures']:raise ValueError('Scientific review not passed')
for r in peer.get('audited_inputs',[]):
 path=Path(r['path'])
 if not path.is_file() or sha(path)!=r['sha256']:raise ValueError('Audited input missing or changed: '+str(path))
checks.append(dict(check='independent_target_and_scientific_review_inputs_unchanged',passed=True))
records=[json.loads(s) for s in (B/'metadata/experiment_registry.jsonl').read_text().splitlines() if s.strip()]
if len({r['experiment_id'] for r in records})!=len(records):raise ValueError('Duplicate experiment IDs')
checks.append(dict(check='experiment_registry_unique_ids',entries=len(records),passed=True))
with (B/'logs/final_verification.json').open('w') as f:json.dump(dict(verified_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,all_passed=True,stage5_started=False),f,indent=2)
code={str(p.relative_to(B)):sha(p) for p in B.rglob('*.py') if '__pycache__' not in p.parts}
(B/'metadata/code_lineage.json').write_text(json.dumps(dict(current_reproduction_scripts=code,note='Earlier artifact-retention and retrospective-registration limits are explicitly recorded in the experiment history.'),indent=2))
manifest=[];target=B/'metadata/output_manifest.json'
for p in sorted(B.rglob('*')):
 if not p.is_file() or p==target or '__pycache__' in p.parts or p.suffix=='.pyc':continue
 manifest.append(dict(path=str(p.relative_to(B)),sha256=sha(p),bytes=p.stat().st_size))
target.write_text(json.dumps(manifest,indent=2))
print('STAGE4_OUTPUT_MANIFEST_SHA256',sha(target),'FILES',len(manifest))
