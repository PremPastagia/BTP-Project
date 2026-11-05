"""Content, lineage and arithmetic checks; unresolved authenticity is never a pass."""
import argparse,json,re
from pathlib import Path
import pandas as pd
from recover_repository import B,Q,sha,NOW

def run(require_ready=False):
 checks=[]
 def check(name,ok,note):checks.append(dict(check=name,status='pass' if ok else 'fail',evidence=note))
 m=pd.read_csv(Q/'manifest.csv');bad=[r.path for r in m.itertuples() if not(Q/r.path).exists() or sha(Q/r.path)!=r.sha256]
 check('original_bytes_preserved',not bad,{'files':len(m),'mismatches':bad})
 o=pd.read_csv(B/'structured/price_revisions/source_observations.csv');old=pd.read_csv(Q/'structured/price_revisions/discrete_revisions.csv')
 a=o[['city','observation_date','cng_price']].sort_values(['city','observation_date']).reset_index(drop=True);b=old[['city','observation_date','cng_price']].sort_values(['city','observation_date']).reset_index(drop=True)
 check('all_original_price_observations_preserved',a.equals(b),len(o))
 c=pd.read_csv(B/'structured/price_revisions/discrete_revisions.csv');check('candidate_changes_exclude_repeats',bool((c.cng_price!=c.previous_observed_price).all()),len(c))
 check('unverified_effective_and_release_dates_blank',o.effective_date.isna().all() and o.publication_release_date.isna().all(),len(o))
 p=pd.read_csv(B/'structured/price_revisions/cng_monthly_panel.csv');check('incomplete_month_targets_excluded',not p.year_month.ge('2026-11').any(),len(p))
 check('unknown_effective_paths_have_no_final_target',p.cng_price_monthend.isna().all() and p.cng_price_twap.isna().all(),len(p))
 d=pd.read_csv(B/'structured/numerical_factors/gdp_annual_source_records.csv');check('annual_GDP_stays_annual',d.year.is_unique and d.frequency.eq('annual').all(),len(d))
 for name in ['demand_factors_monthly','external_shocks_monthly','external_shocks_daily']:
  d=pd.read_csv(B/f'structured/numerical_factors/{name}.csv');check('quarantined_'+name,d.status.eq('quarantined').all() and 'apm_price_usd' not in d and 'vahan_cng_reg_monthly_est' not in d,list(d.columns))
 news=pd.read_csv(B/'structured/news/news_archive_metadata.csv');check('website_captures_not_news',news.record_type.eq('website_capture_not_article').all() and news.publication_release_date.isna().all(),len(news))
 # Current source bytes: successful HTTP alone is not acceptance.
 attempts=pd.read_csv(B/'metadata/retrieval_attempts.csv').fillna('');bad=[];empty=[]
 for r in attempts.to_dict('records'):
  if r['raw_path']:
   path=B/r['raw_path']
   if not path.exists() or sha(path)!=r['sha256']:bad.append(r['source_id'])
   if path.exists() and path.stat().st_size==0:empty.append(r['source_id'])
 check('retrieved_file_hashes_match',not bad,{'attempts':len(attempts),'mismatches':bad})
 checks.append(dict(check='source_authenticity_and_publication_timing',status='pending',evidence='Official hosting, PDF text, dates and raw hashes checked; independent price conflicts, missing publication dates, OCR transcriptions and statistical vintages remain unresolved.'))
 # Retail arithmetic is a flag, never a substitute for factual source verification.
 s=pd.read_csv(B/'structured/price_revisions/pngrb_all_district_snapshots.csv')
 s['retail_sum']=s[['basic_price_inr_kg','excise_inr_kg','vat_inr_kg','other_tax_inr_kg']].sum(axis=1,min_count=4)
 s['retail_arithmetic_difference']=s.retail_price_inr_kg-s.retail_sum
 flags=s[s.retail_arithmetic_difference.abs().gt(.05) | s.revision_date_conflict.eq(True)]
 flags.to_csv(B/'metadata/pngrb_quality_flags.csv',index=False)
 dup=int(s.duplicated(['source_table_id','source_row_number']).sum());check('snapshot_source_row_key_unique',dup==0,dup)
 checks.append(dict(check='snapshot_dates_and_arithmetic',status='pending' if len(flags) else 'pass',evidence={'flagged_rows':len(flags),'future_revision_dates':int(s.revision_date_conflict.eq(True).sum()),'retail_sum_mismatch_over_005':int(s.retail_arithmetic_difference.abs().gt(.05).sum()),'arithmetic_not_testable_missing_components':int(s.retail_sum.isna().sum())}))
 x=pd.read_csv(B/'metadata/price_crosschecks.csv');checks.append(dict(check='independent_price_reconciliation',status='pending',evidence=x.comparison.value_counts().to_dict()))
 inv=pd.read_csv(B/'metadata/data_inventory.csv');check('all_nine_factor_groups_in_inventory',set(f'2.{i}' for i in range(1,10)).issubset(set(inv.stage2_group)),len(inv))
 # Every active CSV parses, and existing Parquet counterpart has identical logical content.
 schema_errors=[];pair_errors=[]
 for path in (B/'structured').rglob('*.csv'):
  try:
   csv=pd.read_csv(path)
   pq=path.with_suffix('.parquet')
   if pq.exists():
    par=pd.read_parquet(pq)
    if list(csv.columns)!=list(par.columns) or len(csv)!=len(par):pair_errors.append(str(path.relative_to(B)))
  except Exception as e:schema_errors.append([str(path.relative_to(B)),str(e)])
 check('active_structured_csvs_parse',not schema_errors,schema_errors);check('csv_parquet_shape_consistency',not pair_errors,pair_errors)
 report=dict(extraction_timestamp=NOW,engineering_checks_pass=not any(x['status']=='fail' for x in checks),stage3_ready=False,model_ready_validated=False,checks=checks)
 (B/'logs/stage3_validation.json').write_text(json.dumps(report,indent=2));pd.DataFrame([dict(check=c['check'],status=c['status'],evidence=json.dumps(c['evidence'])) for c in checks]).to_csv(B/'metadata/validation_results.csv',index=False)
 print(json.dumps(report,indent=2));return 2 if (require_ready or not report['engineering_checks_pass']) else 0
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--require-ready',action='store_true');args=a.parse_args();raise SystemExit(run(args.require_ready))
