"""Recover exact missing source bytes without changing the original collection."""
from pathlib import Path
import csv,json,hashlib,datetime,concurrent.futures,threading,io,time
import requests
from pypdf import PdfReader

ROOT=Path('/Users/virajvekariya/Desktop/[ME] BTP')
HERE=Path(__file__).parent
OLD=ROOT/'Stage3_GitHub_Audit_2026-11-06'
PR=OLD/'snapshots/github-pr1/BTP_CNG_Data'
for p in [HERE/'objects',HERE/'logs',HERE/'metadata']:p.mkdir(parents=True,exist_ok=True)

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for c in iter(lambda:f.read(1048576),b''):h.update(c)
 return h.hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def write(name,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with (HERE/name).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)

inventory=json.loads((OLD/'local_inventory.json').read_text())
local={}
for r in inventory:
 p=ROOT/r['path']
 if p.is_file():local.setdefault(r['sha256'],str(p))
for p in (HERE/'objects').glob('*'):
 if p.is_file():local.setdefault(p.stem,str(p))
corporate=read(PR/'structured/corporate_disclosures/corporate_disclosures_metadata.csv')
missing={}
for r in corporate:
 if r['raw_sha256'] not in local:missing.setdefault(r['raw_sha256'],r)

lock=threading.Lock()
logfile=HERE/'logs/attempts.jsonl'
def log(r):
 with lock:
  with logfile.open('a',encoding='utf-8') as f:f.write(json.dumps(r,ensure_ascii=False)+'\n')

def retrieve(r):
 expected=r['raw_sha256'];u=r['source_url']
 result={'source_id':r['source_id'],'company':r['company'],'document_type':r['document_type'],'source_url':u,'expected_sha256':expected,'retrieved_at':now(),'publication_date':'','publication_status':'unknown_not_inferred_from_document_or_http_dates'}
 if expected in local and Path(local[expected]).is_file():
  result.update(status='existing_exact_hash',actual_sha256=expected,local_path=local[expected]);return result
 for attempt in range(2):
  try:
   headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36','Accept':'application/pdf,*/*;q=0.8'}
   with requests.get(u,headers=headers,timeout=(12,35),stream=True) as resp:
    result.update(http_status=resp.status_code,final_url=resp.url,content_type=resp.headers.get('Content-Type',''),http_last_modified=resp.headers.get('Last-Modified',''))
    resp.raise_for_status();buf=io.BytesIO()
    for chunk in resp.iter_content(1048576):
     buf.write(chunk)
     if buf.tell()>180*1024*1024:raise ValueError('File exceeds bounded 180MiB request limit')
    data=buf.getvalue()
   actual=hashlib.sha256(data).hexdigest();is_pdf=data.lstrip()[:5]==b'%PDF-'
   result.update(actual_sha256=actual,bytes=len(data),pdf_signature=is_pdf)
   if not is_pdf:
    result.update(status='rejected_not_pdf',error='Successful HTTP response was not a PDF');log(result);return result
   p=HERE/'objects'/(actual+'.pdf')
   if actual in local:p=Path(local[actual])
   elif not p.exists():p.write_bytes(data)
   result['local_path']=str(p)
   try:
    reader=PdfReader(io.BytesIO(data),strict=False);pages=len(reader.pages)
    result['pdf_pages']=pages
    if pages<1:raise ValueError('No readable PDF pages')
   except Exception as e:
    result.update(status='rejected_unreadable_pdf',error=str(e));log(result);return result
   result.update(local_path=str(p),status='recovered_exact_hash' if actual==expected else 'retrieved_different_version')
   log(result)
   return result
  except Exception as e:
   result.update(status='failed',error=str(e),attempt=attempt+1);log(result)
   if attempt==0 and not isinstance(e,requests.HTTPError):continue
   break
 return result

if __name__=='__main__':
 print('Missing unique corporate hashes:',len(missing),flush=True)
 results=[]
 # Every rerun reuses the receipts of successfully recovered bytes.
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
  tasks={pool.submit(retrieve,r):h for h,r in missing.items()}
  for task in concurrent.futures.as_completed(tasks):
   r=task.result();results.append(r)
   write('metadata/recovery_attempts.csv',results)
   print(r['company'],r['status'],r['source_url'],flush=True)
 # Reconcile every corporate row with its actual original or recovered source.
 available=dict(local)
 for r in results:
  if r['status']=='recovered_exact_hash':available[r['expected_sha256']]=r['local_path']
 rows=[]
 for r in corporate:
  h=r['raw_sha256'];p=available.get(h,'')
  rows.append({**r,'accepted_raw_path':p,'raw_recovery_status':'exact_bytes_available' if p else 'expected_bytes_unavailable','file_sha256_verified':bool(p and sha(p)==h)})
 write('metadata/corporate_evidence_reconciled.csv',rows)
 remaining=[r for r in rows if not r['accepted_raw_path']]
 write('metadata/unrecovered_corporate.csv',remaining)
 summary={'generated_at':now(),'metadata_rows':len(rows),'expected_distinct_hashes':len({r['raw_sha256'] for r in rows}),'initial_missing_distinct_hashes':len(missing),'attempt_status_counts':dict(__import__('collections').Counter(r['status'] for r in results)),'exact_bytes_available_rows':sum(bool(r['accepted_raw_path']) for r in rows),'exact_bytes_available_unique_hashes':len({r['raw_sha256'] for r in rows if r['accepted_raw_path']}),'remaining_unique_hashes':len({r['raw_sha256'] for r in remaining}),'originals_preserved':True,'all_publication_dates_remain_unknown':True,'stage3_complete':False}
 (HERE/'metadata/recovery_summary.json').write_text(json.dumps(summary,indent=2))
 print(json.dumps(summary,indent=2),flush=True)
