"""Derive monthly outcomes from accepted bounded intervals, without filling gaps."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal,localcontext
import csv,json,hashlib,datetime,calendar
ROOT=Path(__file__).resolve().parents[3]
A=ROOT/'BTP_CNG_Data/accepted_stage3_2026-11-06_restricted_v1'
B=ROOT/'BTP_CNG_Data/stage4_2026-11-06'
for n in ['targets','metadata','logs']:(B/n).mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,rs,cols=None):
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=cols or list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
def fmt(x):
 if x is None:return ''
 with localcontext() as ctx:
  ctx.prec=40
  return format(x.quantize(Decimal('0.000000000001')),'f')
for rec in json.loads((A/'metadata/snapshot_manifest.json').read_text()):
 if sha(A/rec['path'])!=rec['sha256']:raise ValueError('Accepted input changed: '+rec['path'])
acceptance=json.loads((A/'metadata/acceptance.json').read_text())
if not acceptance['stage4_authorized']:raise ValueError('Stage4 acceptance missing')
with (A/'data/price_intervals.csv').open() as f:intervals=list(csv.DictReader(f))
daily=defaultdict(dict);operators={};boundary=defaultdict(dict);source_ids=defaultdict(set)
for r in intervals:
 market=r['source_market_label'];operators[market]=r['operator'];start=datetime.date.fromisoformat(r['interval_start_date_inclusive']);end=datetime.date.fromisoformat(r['interval_end_date_exclusive']);value=Decimal(r['quoted_price_inr_kg'])
 if not start<end or value<=0:raise ValueError('Invalid accepted interval')
 if r['known_date_conflict']!='False':raise ValueError('Disputed interval entered target construction')
 boundary[market][start]=r['interval_id'];source_ids[market].add(r['source_sha256'])
 day=start
 while day<end:
  if day in daily[market]:raise ValueError('Accepted interval overlap: '+market+' '+str(day))
  daily[market][day]=(value,r['interval_id']);day+=datetime.timedelta(days=1)
cutoff=datetime.date(2026,10,31);holdout_start=datetime.date(2025,11,1)
out=[];excluded=[]
for market,quotes in sorted(daily.items()):
 start=min(quotes).replace(day=1);last=min(max(quotes),cutoff)
 while start<=last:
  count=calendar.monthrange(start.year,start.month)[1];end=start.replace(day=count)
  if end>cutoff:
   excluded.append(dict(market=market,month=start.strftime('%Y-%m'),reason='incomplete_calendar_month'));break
  dates=[start+datetime.timedelta(days=i) for i in range(count)];known=[d for d in dates if d in quotes];full=len(known)==count
  eom=quotes[end][0] if end in quotes else None
  avg=sum((quotes[d][0] for d in dates),Decimal(0))/Decimal(count) if full else None
  low=high=None;unknown_previous=0;changed=0;uncertain=0
  if full:
   lower=upper=Decimal(0)
   for day in dates:
    current=quotes[day][0];previous=quotes.get(day-datetime.timedelta(days=1))
    if previous is None:unknown_previous+=1;continue
    old=previous[0]
    lower+=min(old,current);upper+=max(old,current)
    if current!=old:changed+=1;uncertain+=1
   if not unknown_previous:low=lower/Decimal(count);high=upper/Decimal(count)
  ids=sorted({quotes[d][1] for d in known})
  out.append(dict(snapshot_id=acceptance['snapshot_id'],market=market,operator=operators[market],month=start.strftime('%Y-%m'),month_start=start.isoformat(),month_end=end.isoformat(),days_in_month=count,covered_days=len(known),missing_days=count-len(known),full_month_covered=full,month_end_price_inr_kg=fmt(eom),day_weighted_day_end_average_inr_kg=fmt(avg),continuous_time_twap_lower_bound_inr_kg=fmt(low),continuous_time_twap_upper_bound_inr_kg=fmt(high),bounds_status='bounded_under_documented_path_assumptions' if low is not None else ('withheld_missing_previous_day' if full else 'withheld_incomplete_month_coverage'),unknown_previous_day_count=unknown_previous if full else '',known_price_change_days=changed if full else '',timing_uncertain_day_count=uncertain if full else '',source_interval_ids=json.dumps(ids),source_sha256s=json.dumps(sorted(source_ids[market])),outcome_value_class='derived_from_accepted_source_intervals_not_new_observations',historical_predictor_availability='not_certified',exploration_eligible=end<holdout_start,provisional_reserved_period=end>=holdout_start,coverage_row_type='calendar_coverage_row_not_necessarily_observed_target'))
  start=(end+datetime.timedelta(days=1))
write(B/'targets/monthly_targets.csv',out)
write(B/'metadata/excluded_months.csv',excluded,['market','month','reason'])
dictionary=[]
definitions={
 'month_end_price_inr_kg':'Quoted price at the final calendar day end under the accepted documentary interval path; blank if that day is uncovered.',
 'day_weighted_day_end_average_inr_kg':'Sum of known day-end prices divided by calendar days; only populated if all days have accepted source coverage. This is the approved day-resolution target, not an exact intraday integral.',
 'continuous_time_twap_lower_bound_inr_kg':'Average of each day minimum(previous day-end quote,current day-end quote), under at-most-one listed directional change and no unlisted intraday changes. Withheld if previous day is unknown.',
 'continuous_time_twap_upper_bound_inr_kg':'Average of each day maximum(previous day-end quote,current day-end quote), under the same explicit path assumptions. Not a confidence or prediction interval.',
 'known_price_change_days':'Days with complete-month coverage where consecutive known day-end quotes differ; not the number of source rows or independent price innovations.',
 'exploration_eligible':'True before 2025-11; reserved-period outcome values excluded from descriptive EDA.',
 'coverage_row_type':'Rows enumerate calendar coverage. Missing target rows are not synthetic price observations.',
 'source_interval_ids':'Accepted source interval IDs supporting known days; all lineage retained.',
 'historical_predictor_availability':'Retrospective acceptance does not establish real-time availability for lagged price predictors.'}
for c in out[0]:dictionary.append(dict(dataset='targets/monthly_targets.csv',field=c,definition=definitions.get(c,'Explicit calendar, coverage or accepted-source provenance field; see construction script and transformation log.'),missing_value_meaning='Unknown or not identified under accepted source coverage; never zero-filled'))
write(B/'metadata/target_dictionary.csv',dictionary)
definition=dict(snapshot_id=acceptance['snapshot_id'],source_intervals_sha256=sha(A/'data/price_intervals.csv'),target_file_sha256=sha(B/'targets/monthly_targets.csv'),cutoff_complete_month='2026-10',provisional_reserved_period=['2025-11','2026-10'],reservation_status='operational_protection_Stage6_must_confirm_final_evaluation_design',monthly_average='calendar-day-weighted mean of day-end quotes',continuous_time_bounds='deterministic sensitivity bounds under documented-path assumptions, not measured averages or statistical intervals',rounding='Derived outputs only rounded to12decimal places; raw prices retained unchanged',assumptions=['Official chronology persists until the next listed revision only within accepted bounded intervals','Unknown intraday times stay unknown; day-end resolution is explicitly researcher-approved','No unlisted intraday round-trip changes assumed within each source interval','Unknown gaps are not bridged, final quotes are not extended, no incomplete November target','Retrospective outcome data is not automatically valid as an origin-time predictor'],transformation_steps=['Verify accepted snapshot checksums','Filter only accepted275intervals','Expand intervals internally at day-end calendar resolution with overlap rejection','Require complete calendar-day coverage for monthly mean','Require final calendar day coverage for month-end price','Calculate within-day timing sensitivity bounds only when each previous day quote is known','Preserve missing outcomes and source interval IDs','Flag provisional reserved outcome dates before EDA'])
(B/'metadata/target_definition_and_transformations.json').write_text(json.dumps(definition,indent=2))
summary=dict(snapshot_id=acceptance['snapshot_id'],calendar_coverage_rows=len(out),month_end_targets=sum(bool(r['month_end_price_inr_kg']) for r in out),full_month_average_targets=sum(bool(r['day_weighted_day_end_average_inr_kg']) for r in out),sensitivity_bounds_identified=sum(bool(r['continuous_time_twap_lower_bound_inr_kg']) for r in out),source_intervals=len(intervals),synthetic_observations=0,stage5_started=False)
(B/'logs/target_build_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
