"""Recover remaining non-PDF PR1 sources at original URLs; preserve version differences."""
from recover import ROOT,HERE,PR,read,write,local,sha,now
import concurrent.futures,json,hashlib,requests,urllib.parse
from collections import Counter
from pathlib import Path

records=read(PR/'metadata/source_registry.csv')
sources={}
for r in records:
 h=r['sha256']
 if h and h not in local and not r['raw_path'].endswith('.pdf'):
  sources.setdefault(h,r)

def fetch(r):
 result={'source_id':r['source_id'],'source_url':r['original_url'],'original_raw_path':r['raw_path'],'expected_sha256':r['sha256'],'retrieved_at':now(),'publication_date':'','publication_status':'unknown'}
 try:
  with requests.get(r['original_url'],headers={'User-Agent':'Mozilla/5.0'},timeout=(10,25),stream=True) as resp:
   result.update(http_status=resp.status_code,final_url=resp.url,content_type=resp.headers.get('Content-Type',''));resp.raise_for_status();data=b''
   for chunk in resp.iter_content(1048576):
    data+=chunk
    if len(data)>100*1024*1024:raise ValueError('Exceeded 100MiB source bound')
  if not data:raise ValueError('Empty response')
  h=hashlib.sha256(data).hexdigest();ext=Path(r['raw_path']).suffix or '.bin';p=HERE/'objects'/(h+ext)
  if not p.exists():p.write_bytes(data)
  result.update(actual_sha256=h,bytes=len(data),local_path=str(p),status='recovered_exact_hash' if h==r['sha256'] else 'retrieved_different_version')
  if ext=='.json':
   try:json.loads(data);result['json_parse_valid']=True
   except Exception:result['json_parse_valid']=False;result['status']='unexpected_non_json_response'
 except Exception as e:result.update(status='failed',error=str(e))
 return result

if __name__=='__main__':
 print('Missing non-PDF hashes',len(sources),flush=True);results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
  for f in concurrent.futures.as_completed([pool.submit(fetch,r) for r in sources.values()]):
   r=f.result();results.append(r);write('metadata/other_recovery_attempts.csv',results);print(r['status'],r['source_url'],flush=True)
 summary={'generated_at':now(),'targeted_unique_hashes':len(sources),'status_counts':dict(Counter(r['status'] for r in results)),'claim_limit':'Different byte versions are not restored historical evidence. HTML access evidence is not a numerical dataset.'}
 (HERE/'metadata/other_recovery_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2),flush=True)
