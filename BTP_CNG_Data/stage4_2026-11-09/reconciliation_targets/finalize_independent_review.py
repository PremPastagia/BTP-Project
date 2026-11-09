"""Independent legacy flag/arithmetic and lineage-repair preservation receipt.
Uses frozen audit inputs; reserved values are compared only for quality checking.
"""
from pathlib import Path
from datetime import datetime,date,timedelta,timezone
from fractions import Fraction
from decimal import Decimal
from collections import Counter,defaultdict
import csv,json,hashlib,shutil,traceback
OUT=Path(__file__).resolve().parent
REPO=OUT.parents[2]
RUN='TARGET-FINAL-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
R=OUT/'runs'/RUN;R.mkdir(parents=True)
shutil.copy2(__file__,R/'finalize_independent_review.py')
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def log(status,**kw):
 with (OUT/'execution_registry.jsonl').open('a') as f:f.write(json.dumps(dict(run_id=RUN,timestamp=datetime.now(timezone.utc).isoformat(),status=status,script_sha256=H(Path(__file__)),**kw))+'\n')
def read(p):return list(csv.DictReader(p.open()))
log('planned_before_data_execution',purpose='Independently check legacy arithmetic, baseline/change flags, and preserved lineage-repair invariance',reserved_policy='quality comparisons only; no model or outcome EDA')
try:
 latest=json.loads((OUT/'latest_run.json').read_text());A=Path(latest['run_directory']);s=json.loads(Path(latest['summary_path']).read_text());inputs=A/'inputs'
 observations=read(inputs/'git6b_discrete_observations.csv');rev=read(inputs/'git6b_discrete_revisions.csv');panels=read(inputs/'git6b_cng_monthly_panel.csv')+read(inputs/'git6b_cng_monthly_provisional.csv')
 groups=defaultdict(list)
 for r in observations:groups[r['city']].append(r)
 expected_rev=set();flag_errors=[];monthly={};statements=[]
 for city,rs in groups.items():
  rs.sort(key=lambda r:r['observation_date']);previous=None;month_revision_count=Counter()
  for n,r in enumerate(rs):
   p=Fraction(r['cng_price']);change=None if previous is None else p-previous;expected=(n==0 or change!=0)
   if (r['is_price_revision']=='True')!=expected:flag_errors.append([city,r['observation_date'],'revision_flag'])
   expected_type='initial_baseline' if n==0 else 'price_hike' if change>0 else 'price_cut' if change<0 else 'observation_hold'
   if r['revision_type']!=expected_type:flag_errors.append([city,r['observation_date'],'revision_type',r['revision_type'],expected_type])
   if expected:expected_rev.add((city,r['observation_date']));month_revision_count[r['observation_date'][:7]]+=1
   previous=p
  events={date.fromisoformat(r['observation_date']):Fraction(r['cng_price']) for r in rs};day=min(events);end=max(events);price=None;daily=defaultdict(list)
  while day<=end:
   if day in events:price=events[day]
   daily[day.strftime('%Y-%m')].append(price);day+=timedelta(days=1)
  for m,ps in daily.items():monthly[(city,m)]=(ps[-1],sum(ps)/len(ps),len(ps),month_revision_count[m])
  statements.append(dict(city=city,rows=len(rs),distinct_publication_verification_status=sorted({r['publication_verification_status'] for r in rs}),feed_dates_copied_to_publication_dates=all(r['publication_release_date']==r['observation_date'] for r in rs),source_ids=sorted({r['source_id'] for r in rs}),source_names=sorted({r['source_name'] for r in rs})))
 selected_rev={(r['city'],r['observation_date']) for r in rev};revision_set_errors=len(expected_rev^selected_rev)
 arithmetic_errors=[]
 for r in panels:
  key=(r['city'],r['year_month']);eom,avg,days,revision_count=monthly[key]
  for field,x,tol in [('cng_price_monthend',eom,Fraction(1,100000000)),('cng_price_twap',avg,Fraction(1,20000))]:
   if abs(Fraction(r[field])-x)>tol:arithmetic_errors.append([*key,field])
  if int(r['days_observed'])!=days:arithmetic_errors.append([*key,'days_observed'])
  if int(r['revisions_in_month'])!=revision_count:arithmetic_errors.append([*key,'revisions_in_month_including_baseline'])
 # Parent retained the faulty lineage predecessor. Verify no numeric result changed
 # while lineage changed, using row keys rather than relying on CSV order.
 numeric_fields=['cng_price_monthend','cng_price_twap','twap_conditional_lower','twap_conditional_upper','covered_days','calendar_days']
 retained=REPO/'BTP_CNG_Data/stage4_2026-11-09/logs/versions/predecessor_lineage_v1/analysis';current=REPO/'BTP_CNG_Data/stage4_2026-11-09/analysis'
 file_stats=[];repair_errors=[];object_manifest=[]
 for file in ['coverage_calendar','analysis_targets','development_targets','reserved_targets','auxiliary_coverage_calendar','auxiliary_targets']:
  oldpath=retained/(file+'.csv');newpath=current/(file+'.csv');old=read(oldpath);new=read(newpath)
  # Preserve exact old/current files in this receipt as independent frozen evidence.
  for label,p in [('pre_fix',oldpath),('corrected',newpath)]:
   q=R/(label+'_'+file+'.csv');shutil.copy2(p,q);object_manifest.append(dict(role=label,source_path=str(p),audit_path=str(q),sha256=H(q)))
  od={(r['city'],r['year_month']):r for r in old};nd={(r['city'],r['year_month']):r for r in new}
  if od.keys()!=nd.keys():repair_errors.append([file,'row_keys'])
  changed=0
  for k in od.keys()&nd.keys():
   if any(od[k][f]!=nd[k][f] for f in numeric_fields):repair_errors.append([file,k,'quantities_changed'])
   if od[k]['source_interval_ids']!=nd[k]['source_interval_ids']:changed+=1
  file_stats.append(dict(dataset=file,rows=len(new),lineage_changed_rows=changed,numeric_fields_tested=numeric_fields))
 receipt=dict(run_id=RUN,main_successful_audit=latest,main_summary_sha256=H(Path(latest['summary_path'])),independent_method='Exact rational interval-prefix reconstruction, separately coded calendar-day legacy replication, raw-feed pair matching and source-object lineage verification; no producer helper imported',legacy_flag_errors=flag_errors,legacy_revision_set_errors=revision_set_errors,legacy_panel_arithmetic_errors=arithmetic_errors,legacy_panel_rows_recomputed=len(panels),legacy_revision_type_counts=dict(Counter(r['revision_type'] for r in observations)),legacy_revision_list_rows=len(rev),legacy_baseline_caution='is_price_revision=True includes initial_baseline; 275 selected rows are 265 nonzero sampled changes plus 10 baselines',legacy_source_timing=statements,lineage_repair_preserved_versions=file_stats,lineage_repair_numeric_errors=repair_errors,main_independent_summary=s,gate_decision='PASS restricted target transformation and source reconciliation checks, conditional on documented source-path/day-end/timing assumptions; no full-ten-city completion or Stage5 approval',limitations=['Seven intended markets lack accepted paths; auxiliary Agra/Unnao do not fill those cities','Source-supported intervals remain qualified retrospective paths; unknown original publication dates prohibit historical forecasting predictor use','cng_price_twap is the approved calendar-day-weighted mean of day-end quotes, not identified continuous-time TWAP','Reported lower/upper bounds are conditional on source completeness and within-day boundary uncertainty assumptions, not empirical prediction intervals','Reserved outcomes accessed only for source/mathematical audit; prior study exposure prevents claims of pristine untouched research history','Legacy matching or mathematical reproducibility does not validate authenticity or publication timing','No analysis here establishes forecasting improvement, stationarity, power, causal effect, H1, H2 or GAM superiority'],original_audit_failure='An initial reviewer run failed on an incorrect expected sample_period enum (reserved instead of provisionally_reserved). A separate first final-review pass used abbreviated expected revision labels (hike/cut/no_change), generating 2283 string-label differences despite zero arithmetic or flag differences. Both earlier artifacts and sources are retained; corrected fresh passes use the recorded schema labels. These were reviewer implementation errors, not source-data repairs.',preserved_inputs=object_manifest,stage5_started=False)
 (R/'FINAL_RECONCILIATION_REVIEW.json').write_text(json.dumps(receipt,indent=2))
 errors=len(flag_errors)+revision_set_errors+len(arithmetic_errors)+len(repair_errors)+s['producer_math_discrepancies']+s['producer_lineage_discrepancies']
 report=f'''INDEPENDENT TARGET RECONCILIATION — 9 NOVEMBER 2026

Decision: {'PASS' if errors==0 else 'REVISE'} for restricted Stage 4 target transformations and reconciliation only.
No Stage 5 work or researcher stage approval is claimed.

Independent reconstruction
Accepted input: 275 source intervals; all 12 explicitly excluded intervals stayed excluded.
Exact rational prefix integrals independently reconstructed monthly price mass and covered days.
Start dates are inclusive, end dates exclusive; no gaps were filled and no final quote extended.
Hand checks include leap February, changing-price day boundaries and a one-day gap.
All 3,256 exported rows were checked for arithmetic, scope, reservation status and exact
row-specific interval/hash/URL/locator lineage, including explicit predecessor interval IDs.
Current producer arithmetic discrepancies: {s['producer_math_discrepancies']}.
Current producer lineage discrepancies: {s['producer_lineage_discrepancies']}.
The preserved lineage-repair versions have {sum(x['lineage_changed_rows'] for x in file_stats)} changed lineage rows and
{len(repair_errors)} quantity/key discrepancies. No price or bound changed in the repair.

Accepted scope inside January 2011 through October 2026
The ten-city calendar has 1,900 potential rows, not 1,900 observed targets.
Primary: 424 month-end quotes and 416 full-month day-end averages, in Delhi, Noida and Lucknow.
Development portion: 394 month-end quotes and 386 averages.
Agra and Unnao remain auxiliary: 128 month-end quotes and 125 averages.
Missing accepted paths: Mumbai, Pune, Ahmedabad, Gurgaon, Kanpur, Hyderabad and Bengaluru.
An auxiliary city cannot silently replace an intended city.
Prior accepted Stage 4: all 552 available month-end and 541 average values inside the new
envelope agree at their recorded precision; no matched-subset numerical conflicts.
The previous version also included 14 month-end and 12 average values outside this envelope.

Legacy evidence reconciliation
Recovery Git 6b08b996 contains 1,503 complete-labelled rows plus 18 provisional rows.
The 18 are eight partial historical first months and ten incomplete November 2026 rows.
Main/current legacy 1,521 and recovery 1,503 are different artifacts, not a row-loss error.
The 2,293 raw chart observations decompose into 10 initial baselines, 265 actual nonzero
sampled changes and 2,018 same-price observations. The 275-row revision subset includes
the 10 baselines. All raw chart pairs linked back to the saved raw HTML payloads.
Independent replication checked all {len(panels)} legacy complete/provisional rows: {len(arithmetic_errors)}
arithmetic/count differences; {len(flag_errors)} observation-flag differences and {revision_set_errors} revision-set differences.
Legacy flags can be reproduced without authenticating effective dates. Publication dates
were copied from feed dates and remain unverified. Forward holds begin at the first feed
observation; no examined builder backward-fills before that first observation.

Against the accepted price paths, the 1,503 complete-labelled legacy rows contain
216 month-end numerical conflicts and 250 average conflicts where counterparts exist.
There are 187 exact month-end matches; 145 averages match exactly or at export precision.
1,100 month-end and 1,108 average rows have no accepted counterpart.
Matching does not promote a legacy observation to accepted evidence. Conflicts are retained,
not averaged together. The PR1 1,511-row panel has missing target values throughout;
its 350-row candidate file is a separate artifact with four target-cell conflicts.
See the per-city/month CSV for every disposition and masked protected comparisons.

Scientific limits and protection
cng_price_twap names the approved calendar-day-weighted day-end average. True continuous
time TWAP is unidentified from date-only changes; bounds are conditional source-path bounds.
The bounds are not forecast uncertainty intervals. Unknown source publication times remain
unknown; retrospective chronology values are not certified origin-time predictor features.
Reserved November 2025–October 2026 values were accessed only to audit consistency,
arithmetic and lineage, never for descriptive outcome exploration or model selection.
This audit does not establish predictive performance, statistical power, H1, H2 or causality.
The parent preserved the initial lineage-omission outputs before repair. An earlier reviewer
run also failed on an incorrect enum expectation. A first final-review pass used shortened
revision label names and generated string-label mismatches; both attempts remain preserved.

Reproduction and evidence
Main successful run: {latest['run_id']}
Main run directory: {A}
Main source and input snapshots are retained there with hashes and a source inventory.
This final receipt also freezes pre-repair/current target exports and records their hashes.
The standard-library script accepts --desktop-root for the separate archived project files;
local Git object 6b08b996 and repository accepted/current/prior inputs are required.
This final review has {errors} discrepancies requiring correction.
'''
 (R/'FINAL_RECONCILIATION_REVIEW.txt').write_text(report)
 for name in ['FINAL_RECONCILIATION_REVIEW.json','FINAL_RECONCILIATION_REVIEW.txt']:shutil.copy2(R/name,OUT/name)
 (OUT/'latest_final_review.json').write_text(json.dumps(dict(run_id=RUN,run_directory=str(R),report_path=str(R/'FINAL_RECONCILIATION_REVIEW.txt'),report_sha256=H(R/'FINAL_RECONCILIATION_REVIEW.txt'),main_run=latest['run_id']),indent=2))
 log('completed',run_directory=str(R),errors=errors,report_sha256=H(R/'FINAL_RECONCILIATION_REVIEW.txt'))
 print(json.dumps(dict(run_id=RUN,errors=errors,flag_error_examples=flag_errors[:5],arithmetic_error_examples=arithmetic_errors[:5],repair_lineage_changed_rows=sum(x['lineage_changed_rows'] for x in file_stats)),indent=2))
except Exception as e:
 (R/'FAILURE.txt').write_text(traceback.format_exc());log('failed',run_directory=str(R),error=str(e));raise
