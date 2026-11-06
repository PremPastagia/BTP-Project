"""Bounded recovery of missing official source PDFs from the pinned PR registry."""
from recover import ROOT,HERE,PR,read,write,retrieve,local,sha,now
from pathlib import Path
from collections import Counter
import concurrent.futures,json,urllib.parse

records=read(PR/'metadata/source_registry.csv')
allowed={'ppac.gov.in','mopng.gov.in','www.pngrb.gov.in','pngrb.gov.in','mngl.in','sansad.in'}
sources={}
for r in records:
 h=r['sha256'];host=urllib.parse.urlparse(r['original_url']).netloc
 if h and h not in local and r['raw_path'].endswith('.pdf') and host in allowed:
  sources.setdefault(h,{'source_id':r['source_id'],'company':host,'document_type':'official_report_or_notice','source_url':r['original_url'],'raw_sha256':h,'original_raw_path':r['raw_path']})

if __name__=='__main__':
 print('Missing targeted official PDF hashes:',len(sources),Counter(r['company'] for r in sources.values()),flush=True)
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for future in concurrent.futures.as_completed([pool.submit(retrieve,r) for r in sources.values()]):
   r=future.result();results.append(r);write('metadata/official_recovery_attempts.csv',results)
   print(r['company'],r['status'],r['source_url'],flush=True)
 summary={'generated_at':now(),'targeted_missing_unique_hashes':len(sources),'status_counts':dict(Counter(r['status'] for r in results)),'recovered_exact_distinct_hashes':len({r['actual_sha256'] for r in results if r['status']=='recovered_exact_hash'}),'remaining_expected_unique_hashes':len({r['expected_sha256'] for r in results if r['status']!='recovered_exact_hash'}),'semantic_table_extraction_not_claimed':True,'stage3_complete':False}
 (HERE/'metadata/official_recovery_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2),flush=True)
