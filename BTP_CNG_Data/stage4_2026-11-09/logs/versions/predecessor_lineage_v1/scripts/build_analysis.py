"""Versioned Stage 4 redo: derive qualified outcomes without fabricating prices.

Uses only stdlib; accepts an output root for a fresh reproduction directory.
The daily expansion is an internal tariff-path calculation, not new observations.
"""
from pathlib import Path
from decimal import Decimal, localcontext
from collections import defaultdict, Counter
import argparse, calendar, csv, datetime as dt, hashlib, json, platform, sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, rows, columns):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
        w.writeheader(); w.writerows(rows)

def fmt(x):
    if x is None:
        return ''
    with localcontext() as c:
        c.prec = 45
        return format(x.quantize(Decimal('0.000000000001')), 'f')

def months(first, last):
    p = dt.date.fromisoformat(first + '-01')
    while p.strftime('%Y-%m') <= last:
        yield p
        p = (p.replace(day=28) + dt.timedelta(days=4)).replace(day=1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, default=HERE)
    args = ap.parse_args(); out = args.output.resolve()
    spec = json.loads((HERE/'metadata/analysis_specification.json').read_text())
    accepted = ROOT/spec['accepted_snapshot']
    if (out/'analysis/analysis_targets.csv').exists():
        raise FileExistsError('Preserve existing outputs; use --output with a fresh directory.')
    for sub in ['analysis','metadata','logs']:
        (out/sub).mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    inputs = [accepted/'metadata/snapshot_manifest.json', accepted/'data/price_intervals.csv',
              HERE/'metadata/analysis_specification.json', Path(__file__).resolve()]
    planned = dict(experiment_id='S4R-TARGETS-'+started, timestamp_utc=started,
                   status='started_before_calculation', question='Rebuild qualified monthly outcomes and coverage in requested geography/envelope',
                   inputs={str(p):sha(p) for p in inputs}, method='calendar-day expansion of accepted half-open intervals',
                   seed=None, hyperparameters=None, comparison_type='exploratory transformation audit',
                   training_validation_test='none; reservation retained from earlier checkpoint',
                   failure_policy='leave failed run intact; reproduce into fresh output directory')
    registry=out/'metadata/experiment_registry.jsonl'
    with registry.open('a') as f:f.write(json.dumps(planned)+'\n')
    for rec in json.loads((accepted/'metadata/snapshot_manifest.json').read_text()):
        p=accepted/rec['path']
        if not p.is_file() or sha(p)!=rec['sha256'] or p.stat().st_size!=rec['bytes']:
            raise ValueError('Accepted snapshot checksum/size mismatch: '+str(p))
    intervals=list(csv.DictReader((accepted/'data/price_intervals.csv').open()))
    days=defaultdict(dict); operators={}; by_id={}
    for r in intervals:
        city=r['source_market_label']; operators[city]=r['operator']; by_id[r['interval_id']]=r
        if r['known_date_conflict']!='False' or r['accepted_data']!='True':
            raise ValueError('Unaccepted/disputed input')
        start=dt.date.fromisoformat(r['interval_start_date_inclusive'])
        end=dt.date.fromisoformat(r['interval_end_date_exclusive'])
        price=Decimal(r['quoted_price_inr_kg'])
        if not start<end or not price.is_finite() or price<=0:raise ValueError('Invalid interval')
        while start<end:
            if start in days[city]:raise ValueError('Overlapping accepted intervals')
            days[city][start]=(price,r['interval_id']); start+=dt.timedelta(days=1)
    columns=['snapshot_id','city','operator','year_month','research_scope','calendar_days','covered_days','missing_days',
             'cng_price_monthend','cng_price_twap','twap_conditional_lower','twap_conditional_upper',
             'monthend_status','twap_status','timing_bounds_status','known_price_change_days',
             'publication_verification_status','source_publication_dates','historical_predictor_eligible',
             'extraction_timestamp','source_interval_ids','source_sha256s','source_urls','source_locators',
             'quality_class','sample_period','forecasting_readiness']
    allrows=[]; auxrows=[]
    for city in spec['primary_cities']+spec['auxiliary_markets']:
        for first in months(spec['envelope_start'], spec['envelope_end']):
            n=calendar.monthrange(first.year,first.month)[1]; last=first.replace(day=n)
            dates=[first+dt.timedelta(days=i) for i in range(n)]
            known=[d for d in dates if d in days[city]]
            full=len(known)==n; eom=days[city].get(last, (None,None))[0]
            mean=low=high=None; changes=None
            if full:
                with localcontext() as c:
                    c.prec=45
                    mean=sum((days[city][d][0] for d in dates),Decimal(0))/n
                    previous=[days[city].get(d-dt.timedelta(days=1)) for d in dates]
                    if all(p is not None for p in previous):
                        low=sum((min(p[0],days[city][d][0]) for d,p in zip(dates,previous)),Decimal(0))/n
                        high=sum((max(p[0],days[city][d][0]) for d,p in zip(dates,previous)),Decimal(0))/n
                    changes=sum(days[city][d][0]!=p[0] for d,p in zip(dates,previous) if p is not None)
            ids=sorted({days[city][d][1] for d in known}); refs=[by_id[i] for i in ids]
            publications=sorted({r['source_publication_date'] for r in refs if r['source_publication_date']})
            row=dict(snapshot_id='stage3-restricted-2026-11-06-v1',city=city,operator=operators.get(city,''),year_month=first.strftime('%Y-%m'),
                     research_scope='primary_intended_city' if city in spec['primary_cities'] else 'auxiliary_outside_intended_ten',
                     calendar_days=n,covered_days=len(known),missing_days=n-len(known),
                     cng_price_monthend=fmt(eom),cng_price_twap=fmt(mean),twap_conditional_lower=fmt(low),twap_conditional_upper=fmt(high),
                     monthend_status='derived_qualified_day_end_path' if eom is not None else 'missing_no_accepted_final_day',
                     twap_status='derived_qualified_day_end_mean' if full else 'missing_incomplete_accepted_days',
                     timing_bounds_status='conditional_path_bounds' if low is not None else 'unidentified_missing_previous_day' if full else 'unidentified_incomplete_month',
                     known_price_change_days=changes if changes is not None else '',
                     publication_verification_status='unknown_retrospective_source' if refs else 'no_accepted_path',
                     source_publication_dates=json.dumps(publications),historical_predictor_eligible=False,extraction_timestamp='',
                     source_interval_ids=json.dumps(ids),source_sha256s=json.dumps(sorted({r['source_sha256'] for r in refs})),
                     source_urls=json.dumps(sorted({r['source_url'] for r in refs})),
                     source_locators=json.dumps([dict(interval_id=r['interval_id'],start=r['start_source_locator'],end=r['end_source_locator']) for r in refs]),
                     quality_class='researcher_accepted_documentary_path_conditional_hold' if refs else 'unavailable_not_imputed',
                     sample_period='development' if first.strftime('%Y-%m')<spec['reserved_start'] else 'provisionally_reserved',
                     forecasting_readiness='outcome_only_origin_time_price_availability_uncertified')
            (allrows if city in spec['primary_cities'] else auxrows).append(row)
    observed=lambda rs:[r for r in rs if r['cng_price_monthend'] or r['cng_price_twap']]
    analysis=observed(allrows); aux=observed(auxrows)
    write(out/'analysis/coverage_calendar.csv',allrows,columns)
    write(out/'analysis/analysis_targets.csv',analysis,columns)
    write(out/'analysis/development_targets.csv',[r for r in analysis if r['sample_period']=='development'],columns)
    write(out/'analysis/reserved_targets.csv',[r for r in analysis if r['sample_period']=='provisionally_reserved'],columns)
    write(out/'analysis/auxiliary_targets.csv',aux,columns)
    write(out/'analysis/auxiliary_coverage_calendar.csv',auxrows,columns)
    # Every retained target column has a concrete meaning and missing-value rule.
    meaning={
      'snapshot_id':('Accepted restricted input version identifier','identifier','snapshot manifest'),
      'city':('Exact accepted market label; no district/GA-to-city allocation','identifier','source market'),
      'operator':('Operator stated in accepted intervals; blank for city without accepted path','identifier','accepted source'),
      'year_month':('Calendar month in India; Jan2011-Oct2026 inclusive','YYYY-MM','calendar'),
      'research_scope':('Primary intended ten cities versus auxiliary Agra/Unnao','category','user brief'),
      'calendar_days':('Actual days in calendar month including leap days','days','calendar'),
      'covered_days':('Days supported by accepted bounded intervals; internal persistence is conditional','days','interval expansion'),
      'missing_days':('Calendar days minus covered days; not zero prices','days','calendar minus coverage'),
      'cng_price_monthend':('Quote at last calendar day end, conditional on accepted path','INR/kg','accepted intervals'),
      'cng_price_twap':('Calendar-day-weighted mean of day-end quotes only with all days covered; exact intraday TWAP unidentified','INR/kg','accepted intervals'),
      'twap_conditional_lower':('Average daily min(previous/current quote), assuming documented path with no unlisted intraday round trips','INR/kg','accepted intervals'),
      'twap_conditional_upper':('Average daily max(previous/current quote), same assumptions; not a confidence interval','INR/kg','accepted intervals'),
      'monthend_status':('Qualified observed path outcome versus final-day missing','category','coverage rule'),
      'twap_status':('Qualified day-end average versus incomplete-day missing','category','coverage rule'),
      'timing_bounds_status':('Bounds identified conditionally, or reason withheld','category','previous-day coverage rule'),
      'known_price_change_days':('Nonzero consecutive known day-end transitions in a full month; missing predecessor transitions not counted','count','accepted path'),
      'publication_verification_status':('Retrospective chronology does not certify contemporaneous release','category','accepted availability limitation'),
      'source_publication_dates':('Documented source publication dates if any; [] means unknown, never effective-date substitution','JSON ISO dates','accepted sources'),
      'historical_predictor_eligible':('False until origin-time public availability independently established; not an outcome rejection','boolean','availability gate'),
      'extraction_timestamp':('Unknown per-target original extraction timestamp; accepted snapshot creation is not original extraction','ISO timestamp','not asserted'),
      'source_interval_ids':('Only intervals covering known days in this row','JSON identifiers','accepted lineage'),
      'source_sha256s':('Only raw object SHA256 hashes actually supporting this row, not all market sources','JSON SHA256','accepted lineage'),
      'source_urls':('URLs for supporting accepted objects; current contents may differ from hashed object','JSON URLs','accepted lineage'),
      'source_locators':('Source cell/row locators of interval endpoints','JSON objects','accepted lineage'),
      'quality_class':('Accepted conditional documentary holds, or unavailable; no unsupported legacy fills included','category','eligibility specification'),
      'sample_period':('Development before Nov2025; provisional reservation Nov2025-Oct2026, with prior exposure caveat','category','retained reservation'),
      'forecasting_readiness':('Outcome construction only; not certified real-time predictor/label availability','category','scientific gate')}
    dictionary=[dict(field=c,definition=meaning[c][0],unit_or_type=meaning[c][1],source=meaning[c][2],
                     availability_rule='Retrospective outcome/coverage audit only; do not use as a forecast input without origin-time evidence',
                     missing_rule='Blank numeric/timestamp means unknown or ineligible, not zero; JSON [] means no supporting item') for c in columns]
    write(out/'metadata/target_dictionary.csv',dictionary,list(dictionary[0]))
    provenance=[dict(path=str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),sha256=sha(p),bytes=p.stat().st_size) for p in inputs]
    (out/'metadata/target_input_provenance.json').write_text(json.dumps(provenance,indent=2))
    def count(rs):return dict(calendar_rows=len(rs),monthend=sum(bool(r['cng_price_monthend']) for r in rs),twap=sum(bool(r['cng_price_twap']) for r in rs),conditional_bounds=sum(bool(r['twap_conditional_lower']) for r in rs))
    summary=dict(version=spec['version'],primary=count(allrows),auxiliary=count(auxrows),
                 primary_analysis_rows=len(analysis),auxiliary_analysis_rows=len(aux),
                 development=count([r for r in allrows if r['sample_period']=='development']),
                 reserved_coverage_only=count([r for r in allrows if r['sample_period']=='provisionally_reserved']),
                 per_city={c:count([r for r in allrows+auxrows if r['city']==c]) for c in spec['primary_cities']+spec['auxiliary_markets']},
                 distinct_primary_operators=len({r['operator'] for r in analysis}),synthetic_observations=0,
                 no_imputation_scaling_or_outlier_deletion=True,stage5_started=False,
                 environment=dict(python=sys.version,platform=platform.platform()),
                 inherited_qualifications=['Day-end mean is qualified rather than an exact intraday integral',
                 'Reservation was chosen in earlier Stage4 and previous exposure has not been ruled out',
                 'No official interval path for seven intended cities; exclude their prices rather than fill',
                 'Original extraction/publication times stay unknown; snapshot hashing does not establish authenticity'])
    (out/'metadata/target_build_summary.json').write_text(json.dumps(summary,indent=2))
    with registry.open('a') as f:f.write(json.dumps(dict(experiment_id=planned['experiment_id']+'-RESULT',timestamp_utc=dt.datetime.now(dt.timezone.utc).isoformat(),status='completed',parent=planned['experiment_id'],results=summary,decision='qualified_outcomes_only',output_sha256=sha(out/'analysis/analysis_targets.csv')))+'\n')
    print(json.dumps(dict(primary=summary['primary'],development=summary['development'],auxiliary=summary['auxiliary']),indent=2))

if __name__=='__main__':main()
