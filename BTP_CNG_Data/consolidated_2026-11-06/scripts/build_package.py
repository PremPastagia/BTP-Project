"""Build a portable Stage 3 review candidate. Never declare researcher acceptance."""
from pathlib import Path
from collections import defaultdict,Counter
import argparse,csv,json,hashlib,shutil,datetime,re,os

a=argparse.ArgumentParser();a.add_argument('--project-root',type=Path,required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
ROOT=args.project_root.resolve();BASE=ROOT/'Stage3_Consolidated_2026-11-06';OUT=args.output.resolve()
for n in ['raw/objects','structured/price_revisions','structured/numerical_factors','structured/news','structured/corporate_disclosures','metadata/reviews','scripts/modules','logs']:(OUT/n).mkdir(parents=True,exist_ok=True)
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
 return h.hexdigest()
def write(p,rows,fields=None):
 fields=fields or (list(rows[0]) if rows else ['status']);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
objects={};aliases=defaultdict(set);urls=defaultdict(set);sourceids=defaultdict(set)
def register(p,h=None,url='',sid=''):
 p=Path(p)
 if not p.is_absolute():p=ROOT/p
 if not p.is_file():raise FileNotFoundError(p)
 h=h or sha(p)
 if h not in objects:
  assert sha(p)==h,('hash mismatch',p)
  objects[h]=p
 aliases[h].add(str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name)
 if url:urls[h].add(url)
 if sid:sourceids[h].add(sid)
 return h

receipts=read(BASE/'evidence/metadata/cumulative_source_registry.csv')
for r in receipts:
 if r['exact_bytes_available']=='True':register(r['canonical_local_path'],r['expected_sha256'],r['source_url'],r['source_id'])
 if r.get('new_capture_path'):register(r['new_capture_path'],r['new_capture_sha256'],r['source_url'],r['source_id']+'__new_capture')
for p in (BASE/'evidence/objects').iterdir():
 if p.is_file():register(p,p.stem)
fresh=ROOT/'BTP/BTP_CNG_Fresh_2026-11-06'
for part in ['prices','numerical','text','supplemental']:
 for r in json.loads((fresh/part/'manifest.json').read_text()):
  if r.get('local_path') and r.get('sha256'):register(fresh/part/r['local_path'],r['sha256'],r.get('url',''),r.get('source_id',''))
for r in read(BASE/'numerical/metadata/source_registry.csv'):register(r['raw_file'],r['raw_sha256'],r['source_url'],r['source_id'])
for r in read(BASE/'text/structured/news_metadata.csv'):register(r['source_path'],r['sha256'],r['source_url'],r['article_id'])
for r in json.loads((BASE/'prices/metadata/corroboration_acquisitions.json').read_text()):
 p=r.get('path') or r.get('local_path');h=r.get('sha256')
 if p and h:
  p=Path(p);p=p if p.is_absolute() else BASE/'prices'/p
  if p.is_file():register(p,h,r.get('url',''),r.get('source_id',''))
asset=[]
for h,p in sorted(objects.items()):
 with p.open('rb') as f:magic=f.read(8)
 ext='.pdf' if magic.startswith(b'%PDF') else p.suffix.lower()
 if ext not in ['.pdf','.html','.htm','.json','.txt','.xlsx','.xls','.csv','.xml']:ext='.bin'
 rel=Path('raw/objects')/(h+ext);dest=OUT/rel
 if not dest.exists():shutil.copyfile(p,dest)
 assert sha(dest)==h
 asset.append(dict(sha256=h,path=rel.as_posix(),bytes=dest.stat().st_size,source_ids=json.dumps(sorted(sourceids[h])),source_urls=json.dumps(sorted(urls[h])),origin_paths=json.dumps(sorted(aliases[h])),role='source_or_preserved_extraction_evidence',license_status='not_established_for_public_redistribution_draft_assets_only'))
byhash={r['sha256']:r for r in asset}
write(OUT/'metadata/raw_objects.csv',asset)

def normalized_csv(src,dest):
 rows=read(src)
 for r in rows:
  h=next((r[c] for c in ['raw_sha256','source_sha256','sha256'] if r.get(c)),None)
  if h:
   assert h in byhash,('missing lineage',src,h)
   r['raw_object_path']=byhash[h]['path']
  for c in ['raw_file','source_path']:
   if c in r and h:r[c]=byhash[h]['path']
 write(dest,rows)
 return rows
datasets=[]
for rel,target in [
 ('prices/structured/source_price_observations.csv','price_revisions/source_price_observations.csv'),
 ('prices/structured/pngrb_price_components.csv','price_revisions/pngrb_price_components.csv'),
 ('numerical/structured/native_numerical_observations.csv','numerical_factors/native_numerical_observations.csv'),
 ('numerical/structured/unverified_transcription_candidates.csv','numerical_factors/unverified_transcription_candidates.csv'),
 ('demand/structured/cng_reported_native.csv','numerical_factors/cng_reported_native.csv'),
 ('text/structured/news_metadata.csv','news/news_metadata.csv')]:
 rows=normalized_csv(BASE/rel,OUT/'structured'/target)
 datasets.append(dict(dataset='structured/'+target,rows=len(rows),columns=list(rows[0]) if rows else [],status='source_evidence_not_model_ready'))

# Document deduplication is by exact raw bytes. Conflicting metadata remains as aliases.
claims=[]
for r in read(BASE/'evidence/metadata/corporate_evidence_reconciled.csv'):
 claims.append(dict(sha256=r['raw_sha256'],company=r['company'],document_type=r['document_type'],source_url=r['source_url'],publication_date=r['publication_release_date'],document_date=r['document_date'],origin='github-pr1',source_id=r['source_id']))
for r in read(fresh/'text/structured/corporate_disclosures_metadata.csv'):
 claims.append(dict(sha256=r['sha256'],company=r['operator'],document_type=r['document_type'],source_url=r['url'],publication_date=r['publication_date'],document_date=r['document_date'],origin='fresh',source_id=r['source_id']))
groups=defaultdict(list)
for r in claims:assert r['sha256'] in byhash;groups[r['sha256']].append(r)
docs=[]
for h,rs in sorted(groups.items()):
 docs.append(dict(document_id=h[:24],raw_sha256=h,raw_object_path=byhash[h]['path'],companies=json.dumps(sorted({r['company'] for r in rs})),document_type_claims=json.dumps(sorted({r['document_type'] for r in rs})),source_urls=json.dumps(sorted({r['source_url'] for r in rs if r['source_url']})),publication_date_claims=json.dumps(sorted({r['publication_date'] for r in rs if r['publication_date']})),publication_status='unverified_no_inferred_release_date',document_date_claims=json.dumps(sorted({r['document_date'] for r in rs if r['document_date']})),metadata_alias_count=len(rs),verification_status='raw_identity_verified_metadata_claims_require_review',synthetic=False))
write(OUT/'structured/corporate_disclosures/corporate_document_metadata.csv',docs)
write(OUT/'metadata/corporate_metadata_aliases.csv',claims)
datasets.append(dict(dataset='structured/corporate_disclosures/corporate_document_metadata.csv',rows=len(docs),columns=list(docs[0]),status='deduplicated_document_metadata_not_text_features'))

# Copy supporting review records, preserve original workspace names, remove host-specific prefixes.
for module in ['prices','numerical','evidence','demand','text','independent_review']:
 source=BASE/module
 for p in source.rglob('*'):
  if not p.is_file() or any(x in p.parts for x in ['objects','raw','__pycache__']):continue
  if p.suffix not in ['.py','.csv','.json','.txt','.log']:continue
  if p.suffix=='.py':dest=OUT/'scripts/modules'/module/p.relative_to(source)
  else:dest=OUT/'metadata/reviews'/module/p.relative_to(source)
  dest.parent.mkdir(parents=True,exist_ok=True)
  if p.suffix=='.py':shutil.copyfile(p,dest)
  else:dest.write_text(p.read_text(errors='replace').replace(str(ROOT),'PROJECT_ROOT'))

source_rows=[]
for r in receipts:
 r=dict(r);h=r['expected_sha256']
 r['canonical_local_path']=byhash[h]['path'] if h in byhash else ''
 r['original_raw_path']=r['original_raw_path'].replace(str(ROOT),'PROJECT_ROOT')
 if r.get('new_capture_sha256') in byhash:r['new_capture_path']=byhash[r['new_capture_sha256']]['path']
 source_rows.append(r)
write(OUT/'metadata/source_receipts.csv',source_rows)
fields=[]
for d in datasets:
 for c in d['columns']:
  fields.append(dict(dataset=d['dataset'],field=c,definition='Source field or explicit provenance; consult module dictionary and source locator',missing_value_meaning='Unknown/unobserved/not supplied; never assumed zero',dataset_status=d['status']))
write(OUT/'metadata/data_dictionary.csv',fields)
(OUT/'metadata/dataset_inventory.json').write_text(json.dumps(datasets,indent=2))

gates=[
 ('G01_original_identity','pass','All available source objects copied once per SHA256 and rehashed.'),
 ('G02_structured_lineage','pass','All exported observation/document source hashes resolve to retained raw objects.'),
 ('G03_independent_engineering_checks','pass','See module checks and independent scientific review receipts.'),
 ('G04_synthetic_exclusion','pass','No fabricated observations, filled missing targets, lags or invented vehicle series imported.'),
 ('G05_verified_price_paths','blocked','All415source-marketcoverageentries remain uncertified complete paths; ambiguous dates and Pune conflict remain.'),
 ('G06_forecast_origin_information','blocked','Historical publication/release vintages remain unknown for many numerical inputs and corporate documents.'),
 ('G07_semantic_extraction','blocked','Recovered document volume does not equal verified factor extraction; OCR and review queue remain.'),
 ('G08_researcher_acceptance','pending','Researcher must review exclusions, bounded market/period scope and accepted snapshot before Stage4.'),
 ('G09_stage4','not_started','No accepted Stage3 snapshot; no preprocessing,EDA,features or models performed.')]
write(OUT/'metadata/acceptance_gates.csv',[dict(gate=k,status=s,evidence=e) for k,s,e in gates])
status=dict(stage=3,stage3_complete=False,researcher_accepted=False,stage4_started=False,raw_objects=len(asset),raw_bytes=sum(r['bytes'] for r in asset),datasets={d['dataset']:d['rows'] for d in datasets},corporate_metadata_claims=len(claims),corporate_unique_documents=len(docs),main_commit='4d4959cc5659c34989a32cc1902622b28a47e429',pr1_commit='5e57b0ed4867bca25461c1e3211f11796a1c76f4',no_synthetic_observations=True)
(OUT/'metadata/candidate_status.json').write_text(json.dumps(status,indent=2))
shutil.copyfile(ROOT/'FINAL_RESEARCH_PROTOCOL_STAGES_4_9.txt',OUT/'RESEARCH_PROTOCOL.txt')
shutil.copyfile(Path(__file__),OUT/'scripts/build_package.py')
checksums=[]
for p in sorted(OUT.rglob('*')):
 if p.is_file() and p.name!='snapshot_checksums.json' and '.git' not in p.parts:
  checksums.append(dict(path=p.relative_to(OUT).as_posix(),sha256=sha(p),bytes=p.stat().st_size))
(OUT/'metadata/snapshot_checksums.json').write_text(json.dumps(checksums,indent=2))
print(json.dumps(status,indent=2))
