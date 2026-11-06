"""Record explicit restricted-scope acceptance and freeze the actual input files."""
from pathlib import Path
import csv,json,hashlib,datetime,shutil,subprocess
ROOT=Path(__file__).resolve().parents[3]
C=ROOT/'BTP_CNG_Data/consolidated_2026-11-06'
A=ROOT/'BTP_CNG_Data/accepted_stage3_2026-11-06_restricted_v1'
SID='stage3-restricted-2026-11-06-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def write(p,data,fields):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(data)
if A.exists():raise SystemExit('Accepted snapshot exists; verify it, never overwrite it.')
intervals=rows(C/'metadata/reviews/prices/bounded_path_review_intervals.csv')
kept=[r for r in intervals if r['use_class']=='candidate_source_supported_date_path_not_researcher_accepted' and r['known_date_conflict']=='False']
excluded=[r for r in intervals if r not in kept]
assert len(kept)==275 and len(excluded)==12
assert {r['source_market_label'] for r in kept}=={'Delhi','Noida','Lucknow','Agra','Unnao'}
for r in kept:
 r.update(accepted_data='True',accepted_snapshot_id=SID,acceptance_scope='restricted_documentary_day_resolution_outcomes',use_class='researcher_accepted_restricted_source_interval',historical_predictor_availability='not_certified_by_retrospective_outcome_acceptance')
write(A/'data/price_intervals.csv',kept,list(kept[0]))
write(A/'metadata/excluded_price_intervals.csv',excluded,list(excluded[0]))
inputs=[]
for src,dest,role in [
 ('structured/numerical_factors/native_numerical_observations.csv','native_numerical_observations.csv','native_reference_only_publication_filter_required'),
 ('structured/numerical_factors/cng_reported_native.csv','cng_reported_native.csv','native_reference_only_source_meaning_and_release_checks_required'),
 ('structured/news/news_metadata.csv','news_metadata.csv','selected_article_metadata_only_not_representative_news_volume'),
 ('structured/corporate_disclosures/corporate_document_metadata.csv','corporate_document_metadata.csv','document_metadata_only_undated_historical_predictors_ineligible')]:
 target=A/'reference'/dest;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(C/src,target)
 inputs.append(dict(candidate_path=src,sha256=sha(target),snapshot_path=str(target.relative_to(A)),role=role))
inputsource=C/'metadata/reviews/prices/bounded_path_review_intervals.csv'
inputs.append(dict(candidate_path=str(inputsource.relative_to(C)),sha256=sha(inputsource),snapshot_path='data/price_intervals.csv',role='275_selected_source_intervals_12_excluded'))
hashes={r['source_sha256'] for r in kept}
for p in (A/'reference').glob('*.csv'):
 for r in rows(p):
  for k in ['raw_sha256','source_sha256','sha256']:
   if r.get(k):hashes.add(r[k]);break
objects={r['sha256']:r for r in rows(C/'metadata/raw_objects.csv')}
refs=[]
for h in sorted(hashes):
 obj=objects[h];path=C/obj['path']
 if sha(path)!=h:raise ValueError('Source object changed: '+h)
 refs.append(dict(sha256=h,candidate_object_path=obj['path'],bytes=obj['bytes'],candidate_collection='consolidated_2026-11-06',source_ids=obj['source_ids'],source_urls=obj['source_urls']))
write(A/'metadata/source_object_refs.csv',refs,list(refs[0]))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
acceptance=dict(snapshot_id=SID,accepted_at_utc=now,timezone='Asia/Kolkata',authorization='explicit_researcher_response',question_reference='call_c931f606c9f54678b49a34fbded883bc',researcher_answer='Accept this restricted Stage 3 scope and begin Stage 4',candidate_commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),candidate_manifest_sha256=sha(C/'metadata/snapshot_checksums.json'),restricted_stage3_accepted=True,unrestricted_stage3_complete=False,stage4_authorized=True,scope=dict(markets=sorted({r['source_market_label'] for r in kept}),operators=sorted({r['operator'] for r in kept}),accepted_source_intervals=275,excluded_disputed_intervals=12,target_definition='calendar-day-weighted mean of day-end quotes; month-end price from final calendar day',timing='Preserve date-only precision; quantify continuous-time uncertainty when supported, do not infer midnight changes',predictors='Unknown publication dates excluded from historical forecast inputs; retrospective prices do not certify predictor availability',H2='Text-model feasibility unproven; selected corpus and undated corporate records have explicit limitations'),inputs=inputs)
(A/'metadata/acceptance.json').write_text(json.dumps(acceptance,indent=2))
(A/'README.txt').write_text('RESTRICTED STAGE 3 ACCEPTED SNAPSHOT\n\nResearcher explicitly accepted this scope on 6 November 2026.\n275 documentary price intervals across five markets/two operators are accepted\nfor qualified day-resolution outcome construction. Twelve disputed intervals are\nexcluded. This does not certify unrestricted historical coverage, source truth,\ncontinuous-time TWAP or historical predictor availability.\n\nReference numerical/news/document records preserve native inputs. They are not\nautomatically accepted forecast predictors. Unknown release dates remain ineligible.\nOriginal raw objects remain in the checksum-tracked candidate and draft assets.\n\nDo not modify this snapshot. Reopen Stage3 and create a new version if a material\nsource correction is necessary. See metadata/acceptance.json and snapshot_manifest.json.\n')
manifest=[]
for p in sorted(A.rglob('*')):
 if p.is_file():manifest.append(dict(path=str(p.relative_to(A)),sha256=sha(p),bytes=p.stat().st_size))
(A/'metadata/snapshot_manifest.json').write_text(json.dumps(manifest,indent=2))
for p in A.rglob('*'):
 if p.is_file():p.chmod(0o444)
print(json.dumps(dict(snapshot_id=SID,accepted_intervals=len(kept),excluded_intervals=len(excluded),source_objects=len(refs),snapshot_manifest_sha256=sha(A/'metadata/snapshot_manifest.json')),indent=2))
