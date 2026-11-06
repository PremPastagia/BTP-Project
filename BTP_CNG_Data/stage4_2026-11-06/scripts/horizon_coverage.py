"""Count calendar-aligned outcome pairs; not training samples or forecast results."""
from pathlib import Path
import csv,collections,json,hashlib
R=Path(__file__).resolve().parents[3];B=R/'BTP_CNG_Data/stage4_2026-11-06'
p=B/'targets/monthly_targets.csv';rows=list(csv.DictReader(p.open()));lookup={(r['market'],r['month']):r for r in rows}
def future(month,h):
 y,m=map(int,month.split('-'));y,m=divmod(y*12+m-1+h,12);return f'{y:04}-{m+1:02}'
results=[]
for market in sorted({r['market'] for r in rows}):
 for h in [1,3,6]:
  for target,col in [('month_end','month_end_price_inr_kg'),('day_weighted_average','day_weighted_day_end_average_inr_kg')]:
   matches=[(r,lookup[(market,future(r['month'],h))]) for r in rows if r['market']==market and r['month_end_price_inr_kg'] and (market,future(r['month'],h)) in lookup and lookup[(market,future(r['month'],h))][col]]
   results.append(dict(market=market,target=target,horizon_months=h,retrospective_outcome_pairs=len(matches),pairs_with_exploration_target=sum(t['exploration_eligible']=='True' for _,t in matches),pairs_with_reserved_target=sum(t['provisional_reserved_period']=='True' for _,t in matches),price_predictor_availability='not_certified',interpretation='coverage_only_not_independent_forecast_samples_or_power'))
with (B/'metadata/horizon_coverage.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]),lineterminator='\n');w.writeheader();w.writerows(results)
(B/'metadata/horizon_coverage_definition.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),alignment='calendar_month_plus_horizon_not_row_shift',origin='month_end_outcome_exists',targets=['month_end','day_weighted_average'],horizons=[1,3,6],reservation_partition='by_target_month',limitations='Does not certify origin-time price availability, effective independent sample size, model feasibility or statistical power.'),indent=2))
print('HORIZON_COVERAGE_ROWS',len(results))
