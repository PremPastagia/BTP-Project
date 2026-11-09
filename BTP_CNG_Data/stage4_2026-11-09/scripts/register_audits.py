"""Append references to independent/failure journals without rewriting history."""
from pathlib import Path
import datetime,hashlib,json
HERE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
GROUPS={
 'PROJECT-RECONCILIATION':['project_reconciliation/pre_execution_log.jsonl','project_reconciliation/reconciliation_provenance.json','project_reconciliation/evaluation_exposure.json'],
 'TARGET-RECONCILIATION':['reconciliation_targets/execution_registry.jsonl','reconciliation_targets/FINAL_RECONCILIATION_REVIEW.json'],
 'PREDICTOR-RECONCILIATION':['predictor_reconciliation/registry/S4-PRED-RECON-20261109-001.json','predictor_reconciliation/registry/AMENDMENT_001_CORE_ORIGINS.json','predictor_reconciliation/audit_results.json','predictor_reconciliation/ppac_audit_results.json','predictor_reconciliation/core_availability_summary.json'],
 'INDEPENDENT-EDA':['project_reconciliation/independent_eda_audit/pre_execution.json','project_reconciliation/independent_eda_audit/result.json'],
 'SELECTED-PPAC-CHECK':['metadata/selected_ppac_check.json'],
 'END-STAGE-REVIEW':['reconciliation_targets/END_STAGE4_REDO_REVIEW.json']}
def main():
    registry=HERE/'metadata/experiment_registry.jsonl'
    existing=[json.loads(x) for x in registry.read_text().splitlines() if x.strip()]
    ids={x['experiment_id'] for x in existing};links=[]
    for group,files in GROUPS.items():
        records=[dict(path=rel,sha256=sha(HERE/rel),bytes=(HERE/rel).stat().st_size) for rel in files]
        fingerprint=hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest()
        rid='S4R-LINK-'+group+'-'+fingerprint[:16]
        links.append(dict(group=group,experiment_id=rid,records=records))
        if rid in ids:continue
        rec=dict(experiment_id=rid,timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='completed_source_journal_link',
                 comparison_type='exploratory source/calculation verification; no forecasting experiment',source_journals=records,
                 registration_timing='This master link is retrospective; actual execution/planning times and failed runs remain in the linked source journals. Selected PPAC examples were specified after source inspection and are not preregistered confirmatory evidence.',
                 method='Independent implementations/source inspection as specified in linked receipts',training_validation_test='No model estimation or final-test scoring',seed=None,hyperparameters=None,
                 decision='qualified_audit_complete; no H1/H2 performance claim',limitations='All scientific availability, source-path and previous-exposure limitations remain.')
        with registry.open('a') as f:f.write(json.dumps(rec)+'\n')
    (HERE/'metadata/audit_registry_links.json').write_text(json.dumps(links,indent=2))
    print('Linked',len(links),'independent/source audit journal groups')
if __name__=='__main__':main()
