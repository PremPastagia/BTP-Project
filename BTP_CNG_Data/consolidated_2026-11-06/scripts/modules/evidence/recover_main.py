"""Recover current main's committed acquisition receipts, including supplemental JSONs."""
from recover import ROOT,HERE,read,write,retrieve,local,now
from recover_other_sources import fetch
from pathlib import Path
from collections import Counter
import concurrent.futures,json

B=ROOT/'Stage3_GitHub_Audit_2026-11-06/snapshots/github-main/BTP_CNG_Data'
rows=read(B/'metadata/acquisition_manifest.csv')
for p in (B/'metadata').glob('*acquisition*.json'):
 d=json.loads(p.read_text());rows.extend(d if isinstance(d,list) else [d])
targets={}
for r in rows:
 if r.get('sha256') and r['sha256'] not in local:targets.setdefault(r['sha256'],r)

def get(r):
 if (r.get('raw_file') or '').endswith('.pdf'):
  return retrieve({'source_id':r['source_id'],'company':r.get('group','official_source'),'document_type':'main_official_source','source_url':r['source_url'],'raw_sha256':r['sha256']})
 return fetch({'source_id':r['source_id'],'original_url':r['source_url'],'raw_path':r.get('raw_file','response.html'),'sha256':r['sha256']})

if __name__=='__main__':
 print('Missing unique main hashes',len(targets),flush=True);results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for f in concurrent.futures.as_completed([pool.submit(get,r) for r in targets.values()]):
   r=f.result();results.append(r);write('metadata/main_recovery_attempts.csv',results);print(r['status'],r['source_url'],flush=True)
 summary={'generated_at':now(),'targeted_unique_hashes':len(targets),'status_counts':dict(Counter(r['status'] for r in results)),'supplemental_receipts_included':True,'claim_limit':'No HTTP/last-modified/document dates were converted into publication dates.'}
 (HERE/'metadata/main_recovery_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2),flush=True)
