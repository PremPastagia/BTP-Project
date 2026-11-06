"""Independently check retained file identity, keys and lineage; never approve science."""
from pathlib import Path
import csv,json,hashlib,sys
BASE=Path(__file__).resolve().parents[1]
def rows(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def hashfile(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1048576),b''):h.update(c)
 return h.hexdigest()
checks=[]
assets=rows(BASE/'metadata/raw_objects.csv');hashes=set();missing=[]
for r in assets:
 p=BASE/r['path']
 if not p.is_file():missing.append(r['path']);continue
 assert hashfile(p)==r['sha256'],r['path']
 assert r['sha256'] not in hashes,'duplicate raw objects'
 hashes.add(r['sha256'])
assert not missing,('Raw evidence missing: restore draft assets first',missing[:5])
checks.append(dict(check='one_raw_object_per_verified_hash',count=len(hashes)))
prices=None;components=None;table_counts={}
for d in json.loads((BASE/'metadata/dataset_inventory.json').read_text()):
 data=rows(BASE/d['dataset']);assert len(data)==d['rows'];table_counts[d['dataset']]=len(data)
 for key in ['observation_id','article_id','document_id']:
  if data and key in data[0]:assert len({r[key] for r in data})==len(data),(d['dataset'],key)
 for r in data:
  h=next((r[c] for c in ['raw_sha256','source_sha256','sha256'] if r.get(c)),None)
  if h:assert h in hashes,(d['dataset'],h)
  if 'synthetic' in r:assert r['synthetic'].lower()=='false'
  if 'state' in r:assert not __import__('re').fullmatch(r'\d{1,2}/\d{1,2}/\d{2,4}',r['state'])
 if d['dataset'].endswith('/source_price_observations.csv'):prices={r['observation_id'] for r in data}
 if d['dataset'].endswith('/pngrb_price_components.csv'):components={r['observation_id'] for r in data}
checks.append(dict(check='table_keys_counts_and_raw_lineage',tables=table_counts))
assert components<=prices;checks.append(dict(check='component_foreign_keys',count=len(components)))
status=json.loads((BASE/'metadata/candidate_status.json').read_text())
assert status['stage3_complete'] is False and status['researcher_accepted'] is False and status['stage4_started'] is False
checks.append(dict(check='no_false_stage_acceptance',passed=True))
receipt=dict(engineering_checks_passed=True,checks=checks,stage3_complete=False,researcher_accepted=False,stage4_started=False,scientific_gate='blocked_pending_validity_resolution_and_researcher_review')
(BASE/'logs/package_validation.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt,indent=2))
if '--require-accepted' in sys.argv:sys.exit(2)
