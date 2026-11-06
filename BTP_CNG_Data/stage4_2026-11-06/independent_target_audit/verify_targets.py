"""Independent monthly target audit using interval overlaps and Decimal arithmetic.

No producer implementation is imported or inspected. Test fixtures are explicitly
synthetic mathematical examples, never research observations.
"""
from pathlib import Path
from datetime import date,timedelta
from decimal import Decimal,localcontext
from collections import defaultdict
import argparse,calendar,csv,json,hashlib

B=Path(__file__).resolve().parent
DATA=B.parents[1]
ACCEPTED=DATA/'accepted_stage3_2026-11-06_restricted_v1'
CUTOFF=date(2026,11,6)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def next_month(d):return date(d.year+1,1,1) if d.month==12 else date(d.year,d.month+1,1)
def value_on(intervals,day):
    hits=[p for start,end,p,_ in intervals if start<=day<end]
    if len(hits)>1:raise ValueError('Overlapping interval coverage')
    return hits[0] if hits else None
def validate(intervals):
    ordered=sorted(intervals)
    for start,end,p,_ in ordered:
        if not start<end or p<=0:raise ValueError('Invalid interval or nonpositive price')
    for a,z in zip(ordered,ordered[1:]):
        if a[1]>z[0]:raise ValueError('Duplicate/overlapping source intervals')
    return ordered

def month_result(intervals,first):
    intervals=validate(intervals);nxt=next_month(first);last=nxt-timedelta(days=1);ndays=(nxt-first).days
    covered=0;price_days=Decimal(0);ids=[]
    # Direct intersections of half-open source intervals with the calendar month.
    for start,end,p,iid in intervals:
        a,z=max(start,first),min(end,nxt)
        if a<z:
            days=(z-a).days;covered+=days;price_days+=Decimal(days)*p;ids.append(iid)
    month_complete=nxt<=CUTOFF.replace(day=1)
    full=covered==ndays and month_complete
    me=value_on(intervals,last) if month_complete else None
    mean=price_days/Decimal(ndays) if full else None
    low,high=price_days,price_days;unknown=[];transitions=[]
    if full:
        # Quote on the day before each possible transition is needed. For a
        # month starting inside an existing interval this is already known.
        if value_on(intervals,first-timedelta(days=1)) is None:
            unknown.append(first.isoformat())
        for start,end,p,iid in intervals:
            if first<=start<nxt:
                prior=value_on(intervals,start-timedelta(days=1))
                if prior is None:unknown.append(start.isoformat());continue
                low+=min(prior,p)-p;high+=max(prior,p)-p
                if prior!=p:transitions.append(start.isoformat())
    bounds_defined=full and not unknown
    return dict(month=first.strftime('%Y-%m'),days_in_month=ndays,days_covered=covered,complete_calendar_month=month_complete,complete_day_end_coverage=full,month_end_quote=str(me) if me is not None else '',calendar_day_end_average=str(mean) if mean is not None else '',continuous_twap_lower=str(low/Decimal(ndays)) if bounds_defined else '',continuous_twap_upper=str(high/Decimal(ndays)) if bounds_defined else '',bounds_status='defined_given_transition_assumptions' if bounds_defined else 'unknown_preceding_day_price' if full else 'incomplete_coverage_or_calendar_month',unknown_prior_days=';'.join(sorted(set(unknown))),transition_days=';'.join(transitions),source_interval_ids=';'.join(sorted(set(ids))))

def fixtures():
    D=Decimal
    xs=[(date(2024,1,31),date(2024,2,15),D('10'),'fixture_a'),(date(2024,2,15),date(2024,3,1),D('20'),'fixture_b')]
    a=month_result(xs,date(2024,2,1))
    assert a['days_in_month']==29 and a['days_covered']==29
    assert Decimal(a['calendar_day_end_average'])==D(440)/D(29)
    assert Decimal(a['month_end_quote'])==20
    assert Decimal(a['continuous_twap_lower'])==D(430)/D(29)
    assert Decimal(a['continuous_twap_upper'])==D(440)/D(29)
    falling=[(date(2024,1,31),date(2024,2,15),D('20'),'fall_a'),(date(2024,2,15),date(2024,3,1),D('10'),'fall_b')]
    a=month_result(falling,date(2024,2,1));assert Decimal(a['continuous_twap_lower'])==D(430)/D(29) and Decimal(a['continuous_twap_upper'])==D(440)/D(29)
    gap=[(date(2024,1,31),date(2024,2,15),D(10),'a'),(date(2024,2,17),date(2024,3,1),D(20),'b')]
    a=month_result(gap,date(2024,2,1));assert a['days_covered']==27 and a['calendar_day_end_average']=='' and a['month_end_quote']=='20'
    a=month_result([(date(2024,2,1),date(2024,3,1),D(20),'first')],date(2024,2,1))
    assert a['calendar_day_end_average']=='20' and a['continuous_twap_lower']=='' and a['bounds_status']=='unknown_preceding_day_price'
    a=month_result([(date(2024,1,31),date(2024,2,20),D(10),'a')],date(2024,2,1));assert a['month_end_quote']=='' and a['calendar_day_end_average']==''
    try:validate(xs+[xs[0]])
    except ValueError:pass
    else:raise AssertionError('Duplicate interval must fail')
    a=month_result([(date(2026,10,31),date(2026,12,1),D(10),'a')],date(2026,11,1));assert not a['complete_calendar_month'] and a['calendar_day_end_average']=='' and a['month_end_quote']==''
    return ['leap_year_29_days','exact_price_day_arithmetic','rising_transition_TWAP_bounds','falling_transition_TWAP_bounds','gap_not_filled','last_day_target_independent_of_month_average','first_day_prior_unknown_bounds_withheld','last_quote_not_extended','duplicate_interval_rejected','incomplete_November_rejected']

def find_input():
    for p in ACCEPTED.rglob('*.csv'):
        with p.open(encoding='utf-8-sig') as f:cols=next(csv.reader(f),[])
        if {'interval_start_date_inclusive','interval_end_date_exclusive','quoted_price_inr_kg','source_market_label'}<=set(cols):return p
    raise FileNotFoundError('Accepted interval CSV has not yet been created')

def run(accepted):
    rs=list(csv.DictReader(accepted.open(encoding='utf-8-sig')));groups=defaultdict(list)
    for r in rs:
        if r.get('known_date_conflict','').lower()=='true':raise ValueError('Disputed interval included in accepted snapshot')
        if r.get('use_class','').startswith('exclude_'):raise ValueError('Excluded interval included in accepted snapshot')
        key=(r['operator'],r['source_market_label'])
        groups[key].append((date.fromisoformat(r['interval_start_date_inclusive']),date.fromisoformat(r['interval_end_date_exclusive']),Decimal(r['quoted_price_inr_kg']),r['interval_id']))
    outputs=[]
    with localcontext() as ctx:
        ctx.prec=45
        fixture_results=fixtures()
        for (operator,market),intervals in sorted(groups.items()):
            intervals=validate(intervals);first=min(x[0] for x in intervals).replace(day=1);end=max(x[1] for x in intervals)
            while first<end:
                rec=month_result(intervals,first);rec.update(operator=operator,market=market,accepted_input_sha256=sha(accepted));outputs.append(rec);first=next_month(first)
    with (B/'independent_monthly_targets.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(outputs[0]));w.writeheader();w.writerows(outputs)
    summary=dict(accepted_input=str(accepted),accepted_sha256=sha(accepted),accepted_interval_rows=len(rs),markets=len(groups),calendar_market_month_rows=len(outputs),complete_day_end_average_rows=sum(r['complete_day_end_coverage'] for r in outputs),month_end_quotes=sum(bool(r['month_end_quote']) for r in outputs),continuous_TWAP_bound_rows=sum(bool(r['continuous_twap_lower']) for r in outputs),fixtures_passed=fixture_results,algorithm='Direct interval/calendar overlaps with45-digit Decimal arithmetic; no producer helpers and no per-day price expansion',stage5_started=False,scientific_limits=['Bounds assume source paths capture all changes and at most one effective new price per boundary day; unlisted intraday round-trips are not identified.','Bounds are sensitivity envelopes, not confidence or prediction intervals.','Date-only source chronology does not establish midnight changes.','Month-end values can be available even when earlier days are missing; monthly averages remain blank.'])
    (B/'independent_computation_receipt.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

def compare(producer):
    independent=list(csv.DictReader((B/'independent_monthly_targets.csv').open()))
    other=list(csv.DictReader(producer.open(encoding='utf-8-sig')))
    ours={(r['market'],r['month']):r for r in independent}
    seen=set();differences=[];numeric_checks=0
    mapping={'month_end_quote':'month_end_price_inr_kg','calendar_day_end_average':'day_weighted_day_end_average_inr_kg','continuous_twap_lower':'continuous_time_twap_lower_bound_inr_kg','continuous_twap_upper':'continuous_time_twap_upper_bound_inr_kg','days_covered':'covered_days','days_in_month':'days_in_month'}
    for row in other:
        key=(row['market'],row['month'])
        if key in seen:differences.append(dict(market=key[0],month=key[1],field='key',independent='unique',producer='duplicate'))
        seen.add(key)
        if key not in ours:differences.append(dict(market=key[0],month=key[1],field='key',independent='absent',producer='present'));continue
        a=ours[key]
        for i,p in mapping.items():
            if p not in row:raise ValueError('Missing producer target field '+p)
            x,y=a[i].strip(),row[p].strip()
            if y.lower() in ['nan','null','none']:y=''
            if bool(x)!=bool(y):differences.append(dict(market=key[0],month=key[1],field=p,independent=x,producer=y));continue
            if x:
                numeric_checks+=1
                if abs(Decimal(x)-Decimal(y))>Decimal('0.00000001'):differences.append(dict(market=key[0],month=key[1],field=p,independent=x,producer=y))
    for key,row in ours.items():
        if key not in seen and any(row[c] for c in ['month_end_quote','calendar_day_end_average']):differences.append(dict(market=key[0],month=key[1],field='key_with_observed_target',independent='present',producer='absent'))
    with (B/'producer_reconciliation_differences.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['market','month','field','independent','producer']);w.writeheader();w.writerows(differences)
    result=dict(producer_file=str(producer),producer_sha256=sha(producer),independent_sha256=sha(B/'independent_monthly_targets.csv'),producer_rows=len(other),independent_rows=len(independent),numeric_cells_compared=numeric_checks,tolerance_inr='0.00000001',differences=len(differences),reconciliation_passed=not differences,scope='Target mathematics/source coverage only; reserved outcomes not used for EDA or model selection',stage5_started=False)
    (B/'producer_reconciliation_receipt.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--accepted',type=Path);ap.add_argument('--producer',type=Path);args=ap.parse_args();B.mkdir(parents=True,exist_ok=True)
    run(args.accepted or find_input())
    if args.producer:compare(args.producer)
