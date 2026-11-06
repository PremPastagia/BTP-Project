"""Re-extract saved PDFs with the pinned repository's documented Poppler recipe."""
from recover import ROOT,HERE,PR,read,write,now,sha
from pathlib import Path
from collections import Counter
import concurrent.futures,json,subprocess,tempfile,hashlib,shutil

objects=json.loads((HERE/'metadata/source_hash_objects.json').read_text())
manifest=read(PR/'metadata/evidence_file_manifest.csv')
textrows=[r for r in manifest if r['path'].endswith('.txt')]
rawhashes=sorted({Path(r['path']).stem for r in textrows})
tool=shutil.which('pdftotext')
version=subprocess.run([tool,'-v'],capture_output=True,text=True).stderr.splitlines()[0]

def extract(h):
 p=objects.get(h);r={'raw_sha256':h,'raw_path':p or '', 'extracted_at':now(),'method':'pdftotext -layout','tool_version':version}
 if not p:return {**r,'status':'raw_unavailable'}
 try:
  with tempfile.TemporaryDirectory(prefix='btp-evidence-text-') as temp:
   output=Path(temp)/'text.txt';subprocess.run([tool,'-layout',p,str(output)],capture_output=True,timeout=90,check=True);data=output.read_bytes()
  actual=hashlib.sha256(data).hexdigest();target=HERE/'objects'/(actual+'.txt')
  if not target.exists():target.write_bytes(data)
  return {**r,'status':'extracted' if data.strip() else 'scan_or_no_native_text','actual_text_sha256':actual,'bytes':len(data),'text_path':str(target),'pages_formfeed':data.count(b'\f')}
 except Exception as e:return {**r,'status':'extraction_failed','error':str(e)}

if __name__=='__main__':
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for f in concurrent.futures.as_completed([pool.submit(extract,h) for h in rawhashes]):
   r=f.result();results.append(r);write('metadata/text_extraction.csv',results)
   if len(results)%50==0:print('Extracted',len(results),'of',len(rawhashes),flush=True)
 byraw={r['raw_sha256']:r for r in results};reconciled=[]
 for expected in textrows:
  r=byraw.get(Path(expected['path']).stem,{})
  reconciled.append({**expected,**r,'original_text_checksum_reproduced':expected['sha256']==r.get('actual_text_sha256'),'original_extraction_kind':'ocr' if 'ocr' in expected['path'].lower() else 'native_layout','claim_limit':'New extraction is derived from exact raw bytes. It replaces no original text unless hashes agree; native extraction is not OCR.'})
 write('metadata/text_bundle_reconciliation.csv',reconciled)
 summary={'generated_at':now(),'raw_pdf_hashes_processed':len(rawhashes),'expected_text_members':len(textrows),'extraction_status_counts':dict(Counter(r['status'] for r in results)),'original_text_member_checksums_reproduced':sum(r['original_text_checksum_reproduced'] for r in reconciled),'original_text_unique_checksums_reproduced':len({r['sha256'] for r in reconciled if r['original_text_checksum_reproduced']}),'derived_text_versions_not_original':sum(bool(r.get('actual_text_sha256')) and not r['original_text_checksum_reproduced'] for r in reconciled),'tool_version':version,'no_semantic_facts_verified':True}
 (HERE/'metadata/text_recovery_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2),flush=True)
