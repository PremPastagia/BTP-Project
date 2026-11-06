"""Append consequential Stage 4 experiment records without erasing earlier entries."""
from pathlib import Path
import json,hashlib,datetime,sys,importlib.metadata,argparse
parser=argparse.ArgumentParser();parser.add_argument('--reason',default='');args=parser.parse_args()
R=Path(__file__).resolve().parents[3];B=R/'BTP_CNG_Data/stage4_2026-11-06';A=R/'BTP_CNG_Data/accepted_stage3_2026-11-06_restricted_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(path):return json.loads((B/path).read_text())
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
software={'python':sys.version}
for x in ['numpy','pandas','openpyxl','matplotlib','requests','pypdf','pdfplumber']:
 try:software[x]=importlib.metadata.version(x)
 except importlib.metadata.PackageNotFoundError:pass
common=dict(recorded_at_utc=now,data_snapshot='stage3-restricted-2026-11-06-v1',snapshot_manifest_sha256=sha(A/'metadata/snapshot_manifest.json'),training_window=None,validation_window=None,test_window='provisional reservation 2025-11 to2026-10; Stage6 must freeze final design',models_fitted=[],hyperparameters=None,random_seed='not_applicable_deterministic',software=software,confirmatory_or_exploratory='exploratory_or_engineering_verification_no_confirmatory_hypothesis_test',uncertainty='Conditional timing sensitivity envelopes only; no confidence/prediction intervals or significance tests',decision='verified_outputs_retained_for_researcher_stage_review',warnings=['Five markets share two operators; rows are dependent','Retrospective outcome acceptance does not certify price-predictor availability','Unknown predictor release dates excluded','H1/H2 forecasting performance not evaluated'],plan_deviations=['Root transformation records entered after first execution; accepted target specification and reservation preceded results. No prospective preregistration is claimed.'],failures=[])
records=[]
def record(eid,question,method,outputs,result,extra=None):
 d=dict(common);d.update(experiment_id=eid,research_question=question,predeclared_hypothesis='Not an inferential experiment; follow accepted data definitions or verify a deterministic property',method=method,variables_and_transformations=method,input_hashes={'accepted_snapshot_manifest':sha(A/'metadata/snapshot_manifest.json')},output_hashes={p:sha(B/p) for p in outputs},results=result,metrics_type='data_counts_and_verification_not_forecast_accuracy')
 if extra:d.update(extra)
 records.append(d)
record('S4-TARGETS-001','Construct both monthly outcomes without inventing missing prices','Accepted interval expansion internally at calendar-day resolution; month-end support; complete-day monthly mean; conditional timing bounds; reserved flag',['targets/monthly_targets.csv','metadata/target_definition_and_transformations.json'],load('logs/target_build_summary.json'))
record('S4-TARGET-AUDIT-001','Do independently specified target calculations reconcile?','Separate Decimal direct interval-overlap algorithm; no producer helper or daily expansion',['independent_target_audit/producer_reconciliation_receipt.json','independent_target_audit/independent_computation_receipt.json'],load('independent_target_audit/producer_reconciliation_receipt.json'))
record('S4-SOURCE-HANDCHECK-001','Do real raw-source examples match calendar arithmetic?','Independent source workbook cells and hand-specified June2011/February2012/partialJune2010 calculations',['logs/hand_checked_real_examples.json'],load('logs/hand_checked_real_examples.json'))
record('S4-HORIZON-COVERAGE-001','Which retrospective outcome pairs exist at1/3/6calendar-month horizons?','Calendar-month addition, no positional shifts across gaps; counts only, no forecasts',['metadata/horizon_coverage.csv','metadata/horizon_coverage_definition.json'],{'rows':30,'interpretation':'coverage only, not independent sample size or forecast feasibility'})
record('S4-ASOF-001','Which retained native records could be known at each observed month-end origin?','Exclude unknown release dates/ambiguous meanings; select released native reference periods/vintages, retaining age/scope; no frequency disaggregation',['integration/metadata/integration_summary.json','integration/metadata/independent_integration_validation.json','integration/asof_numerical_ledger.csv'],load('integration/metadata/integration_summary.json'))
eda=[json.loads(s) for s in (B/'eda/metadata/experiment_registry.jsonl').read_text().splitlines() if s.strip()]
for d in eda:
 d.update(recorded_in_master_registry_at_utc=now,data_snapshot=common['data_snapshot'],snapshot_manifest_sha256=common['snapshot_manifest_sha256'],source_registry_path='eda/metadata/experiment_registry.jsonl',source_registry_sha256=sha(B/'eda/metadata/experiment_registry.jsonl'))
 records.append(d)
path=B/'metadata/experiment_registry.jsonl';existing=[]
if path.exists():existing=[json.loads(s) for s in path.read_text().splitlines() if s.strip()]
seen={r['experiment_id']:r for r in existing}
added=0
with path.open('a') as f:
 for d in records:
  if d['experiment_id'] in seen:
   prior=seen[d['experiment_id']]
   if prior.get('output_hashes')==d.get('output_hashes') and prior.get('input_hashes')==d.get('input_hashes') and prior.get('source_registry_sha256')==d.get('source_registry_sha256'):continue
   if not args.reason:raise ValueError('Changed prior experiment needs an explicit --reason; history will not be overwritten.')
   d['parent_experiment_id']=d['experiment_id'];d['experiment_id']+='-update-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');d['subsequent_modification_reason']=args.reason
  f.write(json.dumps(d,ensure_ascii=False)+'\n')
  added+=1
print('MASTER_EXPERIMENT_RECORDS',len(existing)+added)
