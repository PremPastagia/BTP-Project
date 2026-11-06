"""Normalize main/PR source receipts and reconcile all retained content by checksum."""
from recover import ROOT,HERE,PR,read,write,now,sha
from pathlib import Path
from collections import Counter,defaultdict
import json,subprocess,concurrent.futures,shutil,re

OLD=ROOT/'Stage3_GitHub_Audit_2026-11-06';MAIN=OLD/'snapshots/github-main/BTP_CNG_Data'
original=json.loads((OLD/'local_inventory.json').read_text());objects={};paths=defaultdict(list)
for r in original:
 p=ROOT/r['path']
 if p.is_file():objects.setdefault(r['sha256'],str(p));paths[r['sha256']].append(str(p))
integrity=[]
for p in (HERE/'objects').glob('*'):
 if not p.is_file():continue
 h=sha(p);integrity.append({'path':str(p),'sha256':h,'filename_hash_matches':h==p.stem,'bytes':p.stat().st_size});objects.setdefault(h,str(p));paths[h].append(str(p))
write('metadata/recovered_object_integrity.csv',integrity)

records=[]
for r in read(PR/'metadata/source_registry.csv'):
 records.append({'collection':'github_pr1','source_id':r['source_id'],'source_url':r['original_url'],'expected_sha256':r['sha256'],'original_raw_path':r['raw_path'],'original_status':r['access_status'],'original_extraction_timestamp':r['extraction_timestamp'],'publication_date':'','publication_status':'unknown','license_status':r['licensing']})
mainrows=read(MAIN/'metadata/acquisition_manifest.csv')
for p in (MAIN/'metadata').glob('*acquisition*.json'):
 d=json.loads(p.read_text());mainrows.extend(d if isinstance(d,list) else [d])
for i,r in enumerate(mainrows):
 records.append({'collection':'github_main','source_id':r['source_id'],'source_url':r['source_url'],'expected_sha256':r.get('sha256',''),'original_raw_path':r.get('raw_file',''),'original_status':r['status'],'original_extraction_timestamp':r.get('extraction_timestamp',''),'publication_date':r.get('publication_timestamp') or '','publication_status':r.get('publication_status','unknown'),'license_status':r.get('license_status','')})
# Duplicate receipts remain in immutable originals; equivalent normalized receipts get one alias list.
unique={}
for r in records:
 key=(r['collection'],r['source_id'],r['expected_sha256'],r['original_raw_path'],r['original_status'])
 if key not in unique:unique[key]=r
records=list(unique.values())
changed_by_url={}
for name in ['recovery_attempts.csv','official_recovery_attempts.csv','other_recovery_attempts.csv','main_recovery_attempts.csv','followup_attempts.csv']:
 p=HERE/'metadata'/name
 if p.is_file():
  for r in read(p):
   if r.get('status')=='retrieved_different_version':changed_by_url[r['source_url']]=r

pdfs={r['expected_sha256']:objects[r['expected_sha256']] for r in records if r['expected_sha256'] in objects and r['original_raw_path'].endswith('.pdf')}
tool=shutil.which('pdfinfo')
def inspect(pair):
 h,p=pair
 try:
  result=subprocess.run([tool,p],capture_output=True,text=True,timeout=25);m=re.search(r'^Pages:\s+(\d+)',result.stdout,re.M)
  return {'sha256':h,'path':p,'file_sha256_verified':sha(p)==h,'pdfinfo_exit':result.returncode,'pages':int(m[1]) if m else '','readable':result.returncode==0 and bool(m),'stderr':result.stderr[-1000:]}
 except Exception as e:return {'sha256':h,'path':p,'readable':False,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:pdfchecks=list(pool.map(inspect,pdfs.items()))
write('metadata/cumulative_pdf_verification.csv',pdfchecks)
badpdf={r['sha256'] for r in pdfchecks if not r['readable']}
parser_disagreements={r['sha256'] for r in read(HERE/'metadata/pdf_parser_disagreements.csv')}

for r in records:
 h=r['expected_sha256'];p=objects.get(h,'');new=changed_by_url.get(r['source_url'],{})
 r.update(canonical_local_path=p,exact_bytes_available=bool(h and p),expected_sha256_verified=bool(h and p and sha(p)==h),new_capture_path=new.get('local_path',''),new_capture_sha256=new.get('actual_sha256',''),pdf_parser_disagreement=h in parser_disagreements,semantic_validation_status='not_certified_by_recovery',recovery_status='exact_source_bytes_available' if p else ('original_version_missing_new_capture_retained' if new else ('original_bytes_unavailable' if h else 'original_attempt_failed_or_unhashed')))
write('metadata/cumulative_source_registry.csv',records)
write('metadata/cumulative_unavailable_sources.csv',[r for r in records if r['expected_sha256'] and not r['exact_bytes_available']])
expected={r['expected_sha256'] for r in records if r['expected_sha256']}
canonical=[{'sha256':h,'canonical_path':objects[h],'bytes':Path(objects[h]).stat().st_size,'path_aliases':json.dumps(paths[h]),'source_urls':json.dumps(sorted({r['source_url'] for r in records if r['expected_sha256']==h}))} for h in sorted(expected & set(objects))]
write('metadata/canonical_source_objects.csv',canonical)
(HERE/'metadata/cumulative_hash_objects.json').write_text(json.dumps({h:objects[h] for h in expected&set(objects)},indent=2))
# Convenience lookup includes exact source objects and separately retained new/derived versions.
lookup={h:objects[h] for h in expected&set(objects)}
for p in (HERE/'objects').glob('*'):
 if p.is_file():lookup.setdefault(p.stem,str(p))
(HERE/'metadata/source_hash_objects.json').write_text(json.dumps(lookup,indent=2))
bundle=read(PR/'metadata/evidence_file_manifest.csv');bundle_hashes={r['sha256'] for r in bundle}
summary={'generated_at':now(),'main_commit':'4d4959cc5659c34989a32cc1902622b28a47e429','pr1_commit':'5e57b0ed4867bca25461c1e3211f11796a1c76f4','normalized_receipts':len(records),'receipt_counts_by_collection':dict(Counter(r['collection'] for r in records)),'distinct_expected_source_hashes':len(expected),'exact_original_source_hashes_available':len(expected&set(objects)),'unrecovered_original_source_hashes':len(expected-set(objects)),'distinct_expected_pdf_hashes':len({r['expected_sha256'] for r in records if r['expected_sha256'] and r['original_raw_path'].endswith('.pdf')}),'exact_pdf_hashes_available':len(pdfs),'poppler_pdf_failures':len(badpdf),'parser_disagreement_hashes':len(parser_disagreements),'new_content_addressed_object_files':len(integrity),'new_object_hash_failures':sum(not r['filename_hash_matches'] for r in integrity),'pr1_bundle_expected_unique_hashes':len(bundle_hashes),'pr1_bundle_hashes_locally_available':len(bundle_hashes&set(objects)),'pr1_bundle_hashes_still_missing':len(bundle_hashes-set(objects)),'publication_dates_inferred':0,'stage3_complete':False,'claim_limit':'This is file recovery and provenance reconciliation, not full semantic data validation. Three malformed-trailer PDFs need Poppler or explicit exclusion; changed HTML does not restore prior versions.'}
(HERE/'metadata/cumulative_recovery_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2),flush=True)

# A category-level review queue is an extraction backlog, not evidence of semantic completion.
import urllib.parse
corporate_hashes={r['raw_sha256'] for r in read(HERE/'metadata/corporate_evidence_reconciled.csv')}
pdf_records={r['expected_sha256']:dict(r) for r in records if r['expected_sha256'] in pdfs and r['original_raw_path'].endswith('.pdf')}
def category(r):
 h=r['expected_sha256'];u=r['source_url'].lower();host=urllib.parse.urlparse(u).netloc
 if h in corporate_hashes:return 'corporate_reports_and_disclosures'
 if 'ppac' in host:return 'PPAC_gas_price_notifications' if any(s in u for s in ('gasprice','gas-price','gas_price')) else 'PPAC_reports_and_ready_reckoners'
 if 'pngrb' in host:return 'PNGRB_MIS_progress_pipeline_and_bulletins'
 if 'mopng' in host:return 'MoPNG_policy_and_guidelines'
 if any(s in host for s in ('mngl','gglonline','iglonline')):return 'operator_price_histories_or_other_documents'
 if 'sansad' in host or 'rajyasabha' in host:return 'parliamentary_evidence'
 return 'other_official_or_operator_reports'
for r in pdf_records.values():r['recovery_document_category']=category(r)
write('metadata/semantic_review_queue.csv',[{k:r.get(k,'') for k in ('expected_sha256','source_id','source_url','canonical_local_path','recovery_document_category','publication_date','publication_status','semantic_validation_status')} for r in pdf_records.values()])
text=read(HERE/'metadata/text_extraction.csv') if (HERE/'metadata/text_extraction.csv').is_file() else []
backlog={'generated_at':now(),'distinct_pdf_count':len(pdfs),'document_category_counts':dict(Counter(category(r) for r in pdf_records.values())),'pdfs_with_native_extraction_record':len(text),'native_text_available':sum(r['status']=='extracted' for r in text),'native_text_empty_requires_OCR':sum(r['status']=='scan_or_no_native_text' for r in text),'pdfs_without_recreated_native_text_record':len(set(pdfs)-{r['raw_sha256'] for r in text}),'semantic_completion_status':'Not certified by recovery; downstream fact extraction/review must report document/page-specific evidence.','publication_timing':'Corporate public release timing remains unknown; no dates inferred.'}
(HERE/'metadata/semantic_extraction_backlog.json').write_text(json.dumps(backlog,indent=2))
