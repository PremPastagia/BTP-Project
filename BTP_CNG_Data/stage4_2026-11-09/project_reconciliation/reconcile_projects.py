"""Read-only bounded project identity, artifact and workflow reconciliation."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,json,hashlib,datetime,subprocess,re

REPO=Path('/Users/virajvekariya/.codex/worktrees/stage3-consolidation/BTP')
DESK=Path('/Users/virajvekariya/Desktop/[ME] BTP')
OUT=Path(__file__).parent
ATTACH=Path('/Users/virajvekariya/.codex/attachments/dc952c79-5fe5-402c-b96d-71d93e2081f7/Pasted text.txt')
CURRENT=REPO/'BTP_CNG_Data'
roots={
 'current_cng_workspace':CURRENT,
 'desktop_legacy_ten_city':DESK/'BTP/BTP_CNG_Data',
 'desktop_initial_source_batch':DESK/'BTP_CNG_Data',
 'desktop_fresh_collection':DESK/'BTP/BTP_CNG_Fresh_2026-11-06',
 'desktop_recovery_work':DESK/'Stage3_Consolidated_2026-11-06',
 'desktop_research_workflow':DESK/'BTP/research_workflow',
 'desktop_original_model_code':DESK/'BTP/BackUp/src',
}
extensions={'.csv','.parquet','.json','.jsonl','.txt','.md','.py','.bib','.tex','.xlsx','.xls','.html'}
skip_parts={'__pycache__','.git','.venv','node_modules','archive_assets','objects','figures'}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(name,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 if not keys:return
 with (OUT/name).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)
def role(label,relative):
 if 'quarantine/' in relative:return 'preserved_excluded_legacy'
 if relative.startswith('accepted_stage3_2026-11-06_restricted_v1/data/'):return 'accepted_restricted_source_intervals'
 if relative.startswith('accepted_stage3_2026-11-06_restricted_v1/reference/'):return 'accepted_snapshot_reference_only_availability_checks_required'
 if relative.startswith('stage4_2026-11-06/'):return 'executed_previous_stage4_artifact_not_new_independent_data'
 if relative.startswith('consolidated_2026-11-06/'):return 'preserved_stage3_review_candidate'
 if label=='desktop_legacy_ten_city':return 'legacy_reported_collection_not_accepted_forecast_data'
 if label=='desktop_initial_source_batch':return 'partial_initial_batch_not_complete_price_paths'
 if label=='desktop_research_workflow':return 'research_protocol_or_template_not_execution_proof'
 if 'raw/' in relative:return 'source_bytes_provenance_not_authenticity_certification'
 if 'structured/' in relative:return 'structured_claims_require_dataset_specific_eligibility'
 return 'documentation_code_or_metadata'

inventory=[];tables=[];unique_paths={};excluded=Counter()
for label,base in roots.items():
 if not base.exists():continue
 for p in sorted(base.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(base)
  if OUT in p.parents or any(x in skip_parts for x in rel.parts) or rel.parts[0]=='stage4_2026-11-09':excluded[label]+=1;continue
  if p.suffix.lower() not in extensions:continue
  h=sha(p);r={'collection':label,'collection_root':str(base),'relative_path':str(rel),'absolute_path':str(p),'bytes':p.stat().st_size,'sha256':h,'hash_basis':'recomputed_from_actual_bytes','role':role(label,str(rel))}
  inventory.append(r);unique_paths[str(p)]=r
  if p.suffix=='.csv':
   try:
    with p.open(encoding='utf-8-sig',newline='') as f:
     reader=csv.reader(f);header=next(reader,[]);n=0;bad=0;blank=0
     for cells in reader:
      if not cells or all(not cell.strip() for cell in cells):blank+=1;continue
      n+=1;bad+=len(cells)!=len(header)
    tables.append({**r,'rows':n,'fully_blank_rows_excluded':blank,'columns':len(header),'column_names':json.dumps(header),'csv_row_width_errors':bad,'header_unique':len(set(header))==len(header),'schema_valid':bad==0 and len(set(header))==len(header)})
   except Exception as e:tables.append({**r,'parse_error':str(e)})
  elif p.suffix=='.parquet':
   try:
    import pyarrow.parquet as pq
    f=pq.ParquetFile(p);tables.append({**r,'rows':f.metadata.num_rows,'columns':f.metadata.num_columns,'column_names':json.dumps(f.schema.names),'schema_valid':True})
   except Exception as e:tables.append({**r,'parse_error':str(e)})

# Explicit top-level scientific documents; no Unity/flight-project recursion.
extra=[DESK/'FINAL_RESEARCH_PROTOCOL_STAGES_4_9.txt',DESK/'BTP_Master_Checkpoint_2026-11-05 (1).md',DESK/'Stage4_Report_2026-11-06.txt',DESK/'BTP/BackUp/output/model_results.json',Path('/Users/virajvekariya/Desktop/BTP Project/DOCUMENTATION.md'),ATTACH]
for p in extra:
 if p.is_file():
  r={'collection':'explicit_context_documents','collection_root':str(p.parent),'relative_path':p.name,'absolute_path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'hash_basis':'recomputed_from_actual_bytes','role':'excluded_unrelated_flight_project_identity_evidence' if 'BTP Project' in p.parts else 'context_or_prior_results_not_accepted_new_empirical_result'};inventory.append(r);unique_paths[str(p)]=r
write('file_inventory.csv',inventory);write('table_inventory.csv',tables)
by_hash=defaultdict(list)
for r in inventory:by_hash[r['sha256']].append(r)
copies=[]
for h,rs in by_hash.items():
 if len(rs)>1:
  copies.append({'sha256':h,'copies':len(rs),'collections':json.dumps(sorted({r['collection'] for r in rs})),'paths':json.dumps([r['absolute_path'] for r in rs]),'decision':'same_bytes_multiple_references_not_independent_observations'})
write('exact_copy_groups.csv',copies)

# Compare legacy and initial files with the current preserved root tables, by relative path.
lookup={(r['collection'],r['relative_path']):r for r in inventory};reconciled=[]
for label in ['desktop_legacy_ten_city','desktop_initial_source_batch']:
 for (collection,rel),r in lookup.items():
  if collection!=label:continue
  other=lookup.get(('current_cng_workspace',rel))
  reconciled.append({'source_collection':label,'source_path':r['absolute_path'],'comparison_path':str(CURRENT/rel),'relative_path':rel,'source_sha256':r['sha256'],'comparison_sha256':other['sha256'] if other else '', 'status':'exact_copy' if other and other['sha256']==r['sha256'] else 'different_version_at_same_relative_path' if other else 'absent_at_comparison_path','decision':'retain_original; compare_semantics_and_roles_before_any_merge'})
write('directory_reconciliation.csv',reconciled)

identities=[
 {'identity':'BTP 2','provider':'Codex list_projects','project_id':'0bcf0e15-a3cc-4738-9ffe-f2f408add148','kind':'local','path':str(DESK),'conclusion':'App project container for CNG research and multiple collection generations; not itself a Git root'},
 {'identity':'BTP','provider':'Codex list_projects','project_id':'7217503d-7001-4068-b22d-8dd1139a5efa','kind':'local','path':'/Users/virajvekariya/Desktop/BTP Project','conclusion':'Unrelated Cessna FlightAssessmentSim project; excluded after top-level documentation inspection'},
 {'identity':'BTP','provider':'Codex list_projects','project_id':'g-p-ef17710206c08191816531d505e17f92','kind':'chatgpt','path':'','conclusion':'Project identity retrievable; ChatGPT history query returned no accessible threads, so project conversation contents were not inspected'},
 {'identity':'current CNG worktree','provider':'current filesystem and read-only Git metadata','project_id':'','kind':'git_worktree','path':str(REPO),'conclusion':'BTP repository worktree within BTP 2 research context; name alone does not prove a separate BTP2 collection'},
 {'identity':'legacy ten-city CNG collection','provider':'actual filesystem tables matching attachment counts','project_id':'','kind':'scientific_artifact_collection','path':str(roots['desktop_legacy_ten_city']),'conclusion':'Accessible scientific counterpart of the 1503/2293/799 BTP handoff; status claims remain claims, not authenticity proof'},
]
write('project_identities.csv',identities)

def table(label,rel):return next((r for r in tables if r['collection']==label and r['relative_path']==rel),None)
legacy=roots['desktop_legacy_ten_city'];claims=[]
for topic,rel,count in [
 ('finalized city-month rows','structured/price_revisions/cng_monthly_panel.csv',1503),
 ('discrete price observation records','structured/price_revisions/discrete_observations.csv',2293),
 ('revision table records including initial baselines','structured/price_revisions/discrete_revisions.csv',275),
 ('external factor month rows','structured/numerical_factors/external_shocks_monthly.csv',190),
 ('corporate disclosure metadata rows','structured/corporate_disclosures/corporate_disclosures_metadata.csv',799),
 ('news/policy records','structured/news/news_archive_metadata.csv',10),
 ('regulatory events','structured/policy_events/regulatory_timeline.csv',8)]:
 t=table('desktop_legacy_ten_city',rel);actual=t.get('rows') if t else None
 claims.append({'topic':topic,'reported_count':count,'actual_count':actual,'count_match':actual==count,'evidence_path':str(legacy/rel),'evidence_sha256':t['sha256'] if t else '', 'scientific_status':'count_verified_only; authenticity_availability_and_target_validity_not_certified_by_count'})
def dictrows(path):return list(csv.DictReader(path.open(encoding='utf-8-sig')))
pr= dictrows(legacy/'structured/price_revisions/cng_monthly_panel.csv')
pub=Counter(r.get('publication_verification_status','') for r in pr)
revs=dictrows(legacy/'structured/price_revisions/discrete_revisions.csv');revision_types=Counter(r.get('revision_type','') for r in revs)
corp=dictrows(legacy/'structured/corporate_disclosures/corporate_disclosures_metadata.csv');download_flags=Counter(r.get('is_downloaded_local','') for r in corp)
demand=dictrows(legacy/'structured/numerical_factors/demand_factors_monthly.csv');vahan_nonmissing=sum(bool(r.get('vahan_cng_reg_monthly_observed','').strip()) for r in demand)
claims += [
 {'topic':'legacy price public availability','reported_count':'report says verified/frozen','actual_count':json.dumps(pub),'count_match':False,'evidence_path':str(legacy/'structured/price_revisions/cng_monthly_panel.csv'),'scientific_status':'unverified_feed_proxy does not establish forecast-origin availability'},
 {'topic':'legacy corporate full downloads','reported_count':'799 filings metadata; not 799 downloaded PDFs','actual_count':json.dumps(download_flags),'count_match':'not_applicable','evidence_path':str(legacy/'structured/corporate_disclosures/corporate_disclosures_metadata.csv'),'scientific_status':'metadata counts are not full-document corpus counts'},
 {'topic':'monthly observed VAHAN registration values','reported_count':'unobserved','actual_count':vahan_nonmissing,'count_match':vahan_nonmissing==0,'evidence_path':str(legacy/'structured/numerical_factors/demand_factors_monthly.csv'),'scientific_status':'active monthly series missing; quarantined generated values must stay excluded'},
 {'topic':'revision types rather than record count','reported_count':'275 table records','actual_count':json.dumps(revision_types),'count_match':'not_applicable','evidence_path':str(legacy/'structured/price_revisions/discrete_revisions.csv'),'scientific_status':'baseline rows must not be counted as nonzero price changes'},
]
write('claim_vs_evidence.csv',claims)

accepted=CURRENT/'accepted_stage3_2026-11-06_restricted_v1';accept=json.loads((accepted/'metadata/acceptance.json').read_text());snapshot=json.loads((accepted/'metadata/snapshot_manifest.json').read_text());checks=[]
for r in snapshot:
 p=accepted/r['path'];checks.append({'path':str(p),'expected_sha256':r['sha256'],'actual_sha256':sha(p) if p.exists() else '', 'matches':p.exists() and sha(p)==r['sha256']})
write('accepted_snapshot_checksum_check.csv',checks)
status=json.loads((CURRENT/'RESEARCH_STATUS.json').read_text());gate=json.loads((CURRENT/'stage4_2026-11-06/metadata/stage_gate_status.json').read_text())
claims.append({'topic':'275 legacy revision records versus 275 accepted source intervals','reported_count':'same numeral, different scientific entities','actual_count':'legacy:10baselines+265changes; accepted:275date-resolution intervals after12disputed exclusions','count_match':'not_comparable','evidence_path':str(legacy/'structured/price_revisions/discrete_revisions.csv')+';'+str(accepted/'data/price_intervals.csv'),'scientific_status':'Do not merge or equate records on the shared count275'})
write('claim_vs_evidence.csv',claims)

mapping=[
 (1,'Define the research problem','Research context / inherited design','Preserve finalized target/horizon and qualified geography; do not silently reinstate uncertified ten-city target histories'),
 (2,'Understand the commodity market','Research context / H1 and H2','Preserve nine factor groups as candidate questions, not guaranteed predictors'),
 (3,'Collect and systematically store data','Reported Stage3 and qualifications','Reconcile actual inputs; keep restricted acceptance separate from unrestricted completion claims'),
 (4,'Preprocessing, Integration and EDA','Attachment Stage4','Direct match: inventory, provenance, eligibility, target calculations, missingness, integration and descriptive exploration'),
 (5,'Stationarity, Structural Breaks and Statistical Properties','Attachment Stage4 diagnostic items; retained original diagnostic stage','Retain original Stage5 name and diagnostic/power gate. The attachment Stage5 design/features title does not rename this stage'),
 (6,'Model Identification and Experimental Design','Attachment Stage5 and baseline-design parts of Stage6','Freeze origins, labels, splits, candidate models, feature/availability rules, tuning, primary comparisons and multiplicity here; no final-test inspection'),
 (7,'Model Estimation and Diagnostics','Attachment Stage6 baseline execution and Stage7 model development','Fit fold-specific transformations/features and models; preserve baseline and advanced-model runs/diagnostics with matched comparisons'),
 (8,'Forecasting and Hypothesis Testing','Attachment Stage8 and baseline/result evaluation requirements','Frozen final evaluation, dependence-aware uncertainty, matched H1/H2 comparisons and robustness'),
 (9,'Interpretation, Scenarios and Research Paper','Attachment Stage9','Thesis/reproducibility package; scenario claims conditional and only when justified'),
]
workflow=[{'original_stage':n,'retrieved_original_stage_name':name,'attachment_mapping':new,'execution_requirement':req,'retrieved_agreement':True,'source':str(DESK/'FINAL_RESEARCH_PROTOCOL_STAGES_4_9.txt') if n>=4 else str(DESK/'BTP_Master_Checkpoint_2026-11-05 (1).md')} for n,name,new,req in mapping]
write('workflow_mapping.csv',workflow)

gitmeta=[]
for label,path in [('current_worktree',REPO),('desktop_nested_repository',DESK/'BTP')]:
 for args in [['rev-parse','HEAD'],['branch','--show-current'],['status','--short']]:
  p=subprocess.run(['git','--no-optional-locks','-C',str(path),*args],capture_output=True,text=True);gitmeta.append({'collection':label,'command':'git '+' '.join(args),'exit_code':p.returncode,'output':p.stdout.strip(),'error':p.stderr.strip()})
(OUT/'read_only_git_metadata.json').write_text(json.dumps(gitmeta,indent=2))

summary={'generated_at_utc':now(),'attachment_path':str(ATTACH),'attachment_sha256':sha(ATTACH),'bounded_discovery':'Desktop directory names to depth4; explicit scientific roots only; unrelated Unity project excluded after top-level read','app_project_records':identities[:3],'chatgpt_history_access':'list_threads history sourcechatgpt returned no accessible threads','inventory_files':len(inventory),'table_files':len(tables),'exact_copy_groups':len(copies),'current_vs_legacy_comparison_statuses':dict(Counter(r['status'] for r in reconciled if r['source_collection']=='desktop_legacy_ten_city')),'excluded_bulk_or_self_paths':dict(excluded),'legacy_publication_flags':dict(pub),'legacy_revision_types':dict(revision_types),'legacy_corporate_download_flags':dict(download_flags),'legacy_nonmissing_observed_monthly_vahan':vahan_nonmissing,'accepted_restricted_snapshot':accept,'accepted_manifest_all_checks_passed':all(r['matches'] for r in checks),'prior_stage4_recorded_status':status,'prior_stage4_gate_status':gate,'scientific_boundary':'No raw archive redownload, Git mutation, model execution, final-test metric, or reserved-value descriptive inspection','completion_scope':'Project/file/workflow reconciliation executed; not a new unrestricted data-authenticity certificate'}
(OUT/'reconciliation_provenance.json').write_text(json.dumps(summary,indent=2))
lines=['PROJECT IDENTITY AND SCIENTIFIC EVIDENCE RECONCILIATION',summary['generated_at_utc'],'','IDENTITY','App BTP 2 is the Desktop/[ME] BTP container. The current directory is a Git worktree of its CNG BTP repository, not evidence of a separately named filesystem BTP2 repository.','App-local BTP at Desktop/BTP Project is an unrelated Cessna flight simulator. It was excluded after a top-level documentation read; no Unity recursion was performed.','ChatGPT BTP project identity exists, but its chat artifacts were not accessible through the history query. The CNG handoff counts can nevertheless be checked against the actual local legacy dataset.','','ACTUALLY ACCESSIBLE CNG GENERATIONS','1. Initial top-level BTP_CNG_Data: partial 118 PNGRB source snapshots; not complete target histories.','2. Nested BTP/BTP_CNG_Data: legacy ten-city collection matching the attachment counts.','3. Nested fresh collection and Desktop recovered evidence: expanded source versions, not interchangeable independent observations.','4. Current consolidated review candidate: corrected/reconciled source records and preserved scientific limits.','5. Restricted accepted snapshot: 275 source intervals for Agra, Delhi, Lucknow, Noida, Unnao, two operators; unrestricted Stage 3 remains incomplete.','6. Prior Stage 4: executed target/availability/EDA outputs and independent audit receipts; researcher acceptance of Stage 4 is recorded false, and Stage 5 has not started.','','MEASURED LEGACY EVIDENCE']
for r in claims[:7]:lines.append(str(r['topic'])+': reported '+str(r['reported_count'])+', actual '+str(r['actual_count'])+', count match='+str(r['count_match']))
lines += ['Legacy publication flags: '+json.dumps(dict(pub)),'Legacy revision types: '+json.dumps(dict(revision_types)),'Legacy corporate download flags: '+json.dumps(dict(download_flags)),'Nonmissing observed monthly VAHAN values: '+str(vahan_nonmissing),'These counts verify file contents, not report assertions of authenticity or historical availability.','','COPY AND VERSION RECONCILIATION','Files hashed: '+str(len(inventory))+'; table files inspected: '+str(len(tables))+'; exact-byte copy groups: '+str(len(copies))+'.','Legacy/current same-relative-path statuses: '+json.dumps(summary['current_vs_legacy_comparison_statuses']),'See directory_reconciliation.csv for exact copies, differing versions and missing paths. Identical bytes do not represent independent evidence; differing versions must not be merged by filename alone.','Raw object directories and already-local archives were not re-downloaded or redundantly rehashed by this inventory; their manifest/audit artifacts are inventoried.','','ACCEPTANCE AND PRIOR EXECUTION','The actual accepted snapshot contains an explicit researcher answer accepting the restricted Stage3 scope and beginning Stage4. Its manifest hashes were independently checked: '+str(summary['accepted_manifest_all_checks_passed'])+'.','Reference numerical/text corpora in that snapshot are not blanket-approved historically available predictors. Unknown release dates remain ineligible without evidence or declared assumptions.','The prior Stage4 completion state is supported by saved tables/scripts/checks, but those artifacts need reconciliation against this new brief rather than automatic acceptance. No Stage5 model or final-test result is demonstrated by the inspected status.','','WORKFLOW RECONCILIATION','A saved finalized nine-stage protocol was retrieved. Its names are preserved in workflow_mapping.csv.','The attachment Stage5 design/features tasks map mainly to original Stage6; original Stage5 stationarity/structural-break/statistical-properties work is retained.','Attachment baseline execution maps across original Stage6 design, Stage7 estimation and Stage8 evaluation. No workflow renaming or invented prior agreement is required.','','DEPENDENCIES AND LIMITS','No separate independent filesystem BTP2 corpus was found beyond the app container and its multiple CNG generations.','ChatGPT BTP conversation contents are inaccessible via the queried history endpoint; no claim of reading them is made.','An unrestricted ten-city empirical sample remains a scientific decision requiring defensible price paths; matching old row counts is insufficient.','Corporate publication times, representative text coverage and actual monthly VAHAN observations remain distinct unresolved dependencies.','Reserved final-test outcomes were not inspected for price statistics or model selection.','All original files were preserved. No Git writes, collection replay or raw-archive download was performed.']
(OUT/'PROJECT_RECONCILIATION_REPORT.txt').write_text('\n'.join(lines)+'\n')
(OUT/'output_checksums.json').write_text(json.dumps({str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name not in ['output_checksums.json','execution.log'] and '__pycache__' not in p.parts and 'independent_eda_audit' not in p.parts},indent=2))
print(json.dumps({'files':len(inventory),'tables':len(tables),'exact_copy_groups':len(copies),'legacy_counts':[{'topic':r['topic'],'actual':r['actual_count']} for r in claims[:7]],'accepted_snapshot_hashes_passed':summary['accepted_manifest_all_checks_passed'],'legacy_pubflags':dict(pub),'legacy_downloadflags':dict(download_flags),'revision_types':dict(revision_types)},indent=2))
