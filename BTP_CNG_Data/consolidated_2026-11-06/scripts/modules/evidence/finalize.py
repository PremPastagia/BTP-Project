"""Reconcile recovered source identities and verify PDFs with independent Poppler."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,json,hashlib,subprocess,concurrent.futures,re,datetime,shutil
from recover import ROOT,HERE,PR,read,write,now,sha

original=json.loads((ROOT/'Stage3_GitHub_Audit_2026-11-06/local_inventory.json').read_text())
objects={};aliases=defaultdict(list)
for r in original:
 p=ROOT/r['path']
 if p.is_file():objects.setdefault(r['sha256'],str(p));aliases[r['sha256']].append(str(p))
object_integrity=[]
for p in (HERE/'objects').glob('*'):
 if not p.is_file():continue
 actual=sha(p);good=p.stem==actual
 object_integrity.append({'path':str(p),'bytes':p.stat().st_size,'actual_sha256':actual,'filename_hash_matches':good})
 if good:objects.setdefault(actual,str(p));aliases[actual].append(str(p))
write('metadata/recovered_object_integrity.csv',object_integrity)

source=read(PR/'metadata/source_registry.csv');pdfs={r['sha256']:objects[r['sha256']] for r in source if r['sha256'] in objects and r['raw_path'].endswith('.pdf')}
pdfinfo=shutil.which('pdfinfo')
def inspect(item):
 h,path=item;r={'sha256':h,'path':path,'file_sha256_matches':sha(path)==h,'method':'independent Poppler pdfinfo'}
 try:
  p=subprocess.run([pdfinfo,path],capture_output=True,text=True,timeout=25);m=re.search(r'^Pages:\s+(\d+)',p.stdout,re.M)
  r.update(pdfinfo_exit=p.returncode,pages=int(m[1]) if m else None,pdf_structure_readable=p.returncode==0 and bool(m),diagnostic=p.stderr[-1800:])
 except Exception as e:r.update(pdf_structure_readable=False,diagnostic=str(e))
 return r
checks=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for r in pool.map(inspect,pdfs.items()):checks.append(r)
write('metadata/pdf_independent_verification.csv',checks)
bad={r['sha256'] for r in checks if not r['pdf_structure_readable']}
parser_disagreements=set()
for name in ['official_recovery_attempts.csv','followup_attempts.csv']:
 path=HERE/'metadata'/name
 if path.is_file():
  parser_disagreements.update(r['actual_sha256'] for r in read(path) if r.get('status')=='rejected_unreadable_pdf' and r.get('actual_sha256') in pdfs)
out=[]
for r in source:
 h=r['sha256'];path=objects.get(h,'');available=bool(h and path)
 out.append({**r,'canonical_local_path':path,'expected_bytes_available':available,'expected_hash_reverified':bool(available and sha(path)==h),'pdf_structure_readable':h not in bad if available and r['raw_path'].endswith('.pdf') else '', 'pdf_parser_disagreement':h in parser_disagreements,'collection_use_status':'excluded_invalid_pdf_structure' if h in bad else ('conditional_poppler_only_malformed_trailer' if h in parser_disagreements else ('exact_source_bytes_available_semantics_not_certified' if available else ('original_response_version_not_recovered' if h else 'failed_or_unhashed_original_attempt')))})
write('metadata/source_registry_reconciled.csv',out)
corp=read(PR/'structured/corporate_disclosures/corporate_disclosures_metadata.csv')
corporate=[{**r,'accepted_raw_path':objects.get(r['raw_sha256'],''),'raw_recovery_status':'exact_bytes_available' if r['raw_sha256'] in objects else 'expected_bytes_unavailable','file_sha256_verified':r['raw_sha256'] in objects and sha(objects[r['raw_sha256']])==r['raw_sha256'],'pdf_independent_check_passed':r['raw_sha256'] in pdfs and r['raw_sha256'] not in bad} for r in corp]
write('metadata/corporate_evidence_reconciled.csv',corporate)
expected={r['sha256'] for r in source if r['sha256']};available=expected&set(objects)
expected_pdf={r['sha256'] for r in source if r['sha256'] and r['raw_path'].endswith('.pdf')}
manifest=read(PR/'metadata/evidence_file_manifest.csv');bundle_expected={r['sha256'] for r in manifest}
summary={'generated_at':now(),'pinned_pr1_commit':'5e57b0ed4867bca25461c1e3211f11796a1c76f4','source_registry_rows':len(source),'expected_distinct_source_hashes':len(expected),'exact_source_hashes_available':len(available),'unrecovered_original_source_hashes':len(expected-available),'expected_distinct_pdf_hashes':len(expected_pdf),'exact_pdf_hashes_available':len(expected_pdf&set(objects)),'structurally_unreadable_pdf_hashes':len(bad),'pdf_parser_disagreement_hashes':len(parser_disagreements),'independently_readable_exact_pdf_hashes':len(expected_pdf&set(objects)-bad),'corporate_metadata_rows':len(corporate),'corporate_distinct_hashes':len({r['raw_sha256'] for r in corporate}),'corporate_all_exact_bytes_available':all(r['file_sha256_verified'] for r in corporate),'corporate_all_poppler_checks_passed':all(r['pdf_independent_check_passed'] for r in corporate),'new_content_addressed_objects':len(object_integrity),'object_filename_hash_failures':sum(not r['filename_hash_matches'] for r in object_integrity),'expected_evidence_bundle_unique_hashes':len(bundle_expected),'bundle_member_hashes_available':len(bundle_expected&set(objects)),'bundle_member_hashes_unavailable':len(bundle_expected-set(objects)),'publication_dates_inferred':0,'stage3_complete':False,'claim_limits':['Exact source recovery and file readability do not certify every factual statement.','Three MoPNG originals have malformed startref trailers: Poppler reads them, PyPDF does not. Use only after explicit page review or retain excluded.','Changed HTML versions are retained separately and never replace expected original bytes.','Library bundle extracted-text bytes have not all been restored.','No licensed/private files were published; originals were preserved.']}
(HERE/'metadata/final_recovery_summary.json').write_text(json.dumps(summary,indent=2))
(HERE/'metadata/source_hash_objects.json').write_text(json.dumps({h:objects[h] for h in expected if h in objects},indent=2))
write('metadata/unrecovered_sources.csv',[r for r in out if r['sha256'] and not r['expected_bytes_available']])
write('metadata/excluded_invalid_pdfs.csv',[r for r in out if r['sha256'] in bad])
write('metadata/pdf_parser_disagreements.csv',[r for r in out if r['sha256'] in parser_disagreements])
print(json.dumps(summary,indent=2),flush=True)
