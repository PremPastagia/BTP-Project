"""Stage 3 bounded price-label verification only. These candidates are never final targets."""
import calendar
import pandas as pd
from recover_repository import B,save

def run():
 src=pd.read_csv(B/'structured/price_revisions/primary_price_histories.csv');out=[]
 for city,g in src.groupby('city'):
  g=g.sort_values('effective_date');valid=g[g.cng_price.notna()]
  if valid.empty:continue
  start=pd.Timestamp(valid.effective_date.min());start=start if start.day==1 else start+pd.offsets.MonthBegin(1)
  # Never extend a historical price list beyond its last explicitly dated revision.
  end=pd.Timestamp(g.effective_date.max()).to_period('M')-1
  for month in pd.period_range(start,end.to_timestamp(),freq='M'):
   first=month.start_time.normalize();last=month.end_time.normalize();prices=[];ids=[]
   for day in pd.date_range(first,last):
    known=g[pd.to_datetime(g.effective_date).le(day)]
    if known.empty or pd.isna(known.cng_price.iloc[-1]):break
    prices.append(float(known.cng_price.iloc[-1]));ids.append(known.source_id.iloc[-1])
   if len(prices)!=calendar.monthrange(month.year,month.month)[1]:continue
   out.append(dict(city=city,year_month=str(month),cng_price_monthend=prices[-1],cng_price_twap=sum(prices)/len(prices),days=len(prices),unit='INR/kg',source_ids=';'.join(sorted(set(ids))),raw_sha256=g.raw_sha256.iloc[0],target_status='primary_history_derived_candidate_not_final',value_class='derived',verification_status='independent_conflicts_and_full_history_review_pending',arithmetic_method='Calendar-day weighted carry of explicit primary effective dates, bounded before last revision month',intraday_timing='Day precision only; intraday revision time unknown',publication_release_date='',publication_status='retrospective_history_first_publication_unknown',model_ready=False))
 d=pd.DataFrame(out);save(d,'structured/price_revisions/primary_history_monthly_candidates.csv');print(len(d),'bounded monthly candidates; none finalised')
if __name__=='__main__':run()
