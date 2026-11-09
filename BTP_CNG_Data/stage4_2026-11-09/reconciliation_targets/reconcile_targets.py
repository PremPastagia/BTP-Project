"""Independent target reconciliation, with logged runs and preserved audit inputs.

Reserved outcome access is strictly source-quality/mathematical comparison; this
script computes no reserved distributions, forecasting scores, or model selection.
"""
from pathlib import Path
from datetime import datetime,date,timedelta,timezone
from decimal import Decimal,InvalidOperation
from fractions import Fraction
from collections import defaultdict,Counter
import csv,hashlib,io,json,calendar,re,subprocess,traceback,shutil,argparse

OUT=Path(__file__).resolve().parent
REPO=OUT.parents[2]
DATA=REPO/'BTP_CNG_Data'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--desktop-root',type=Path,default=Path('/Users/virajvekariya/Desktop/[ME] BTP'),help='Read-only archived project root containing BTP, fresh and PR1 snapshots; missing archives are reported rather than synthesized')
DESKTOP_ROOT=parser.parse_args().desktop_root
RUN='TARGET-RECON-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
R=OUT/'runs'/RUN
R.mkdir(parents=True,exist_ok=True)
(R/'inputs').mkdir()
shutil.copy2(Path(__file__),R/'reconcile_targets.py')
CITIES=['Delhi','Mumbai','Pune','Ahmedabad','Gurgaon','Noida','Lucknow','Kanpur','Hyderabad','Bengaluru']
FIRST='2011-01';LAST='2026-10';RESERVE='2025-11'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def log(status,**kw):
    record=dict(run_id=RUN,timestamp=datetime.now(timezone.utc).isoformat(),status=status,script_sha256=H(Path(__file__)),**kw)
    with (OUT/'execution_registry.jsonl').open('a') as f:f.write(json.dumps(record,default=str)+'\n')
def write(name,rows,fields=None):
    fields=fields or list(dict.fromkeys(k for r in rows for k in r)) or ['status']
    with (R/name).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def dump(name,obj):(R/name).write_text(json.dumps(obj,indent=2,default=str))
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def git(ref,name):return subprocess.check_output(['git','-C',str(REPO),'show',ref+':BTP_CNG_Data/'+name])
def month_next(m):
    y,n=map(int,m.split('-'));return f'{y+1:04d}-01' if n==12 else f'{y:04d}-{n+1:02d}'
def months(first=FIRST,last=LAST):
    xs=[]
    while first<=last:xs.append(first);first=month_next(first)
    return xs
def city(x):return {'Gurugram':'Gurgaon','Bangalore':'Bengaluru'}.get(x,x)
def num(x):
    try:return Decimal(str(x)) if str(x).strip() not in ['', 'nan','NaN','None'] else None
    except InvalidOperation:return None
def yes(x):return str(x).lower()=='true'
def saved(label,source=None,blob=None):
    p=R/'inputs'/(label+'.csv')
    if blob is None:blob=Path(source).read_bytes()
    p.write_bytes(blob);return p

log('planned_before_data_execution',scope=dict(intended_cities=CITIES,envelope=[FIRST,LAST],auxiliary=['Agra','Unnao']),reserved_outcome_policy='quality_consistency_only_no_EDA_or_selection',planned_methods=['Exact Git-version and source inventory','Independent Fraction prefix-integral approved targets','Legacy baseline/change/hold audit','Raw-feed linkage and forward-hold construction audit','City/month target agreement with reserved values masked in comparison exports','Strict row-specific interval/raw-object lineage audit'])

def run():
    manifest=[];datasets=[]
    def add(label,path,kind='legacy',mean_precision=4):
        if not Path(path).is_file():manifest.append(dict(dataset=label,path=str(path),status='missing'));return
        p=saved(label,path);rows=read(p);manifest.append(dict(dataset=label,path=str(path),audit_copy=str(p),sha256=H(p),rows=len(rows),status='present',kind=kind))
        datasets.append((label,rows,kind,mean_precision))
    ref='6b08b99666ef2b08605c63499418503a4d666c3b'
    refs={}
    for name in ['cng_monthly_panel','cng_monthly_provisional','discrete_observations','discrete_revisions']:
        p=saved('git6b_'+name,blob=git(ref,'structured/price_revisions/'+name+'.csv'));refs[name]=read(p)
        manifest.append(dict(dataset='git6b_'+name,path=f'git:{ref}:BTP_CNG_Data/structured/price_revisions/{name}.csv',audit_copy=str(p),sha256=H(p),rows=len(refs[name]),status='present',kind='frozen_Git_version'))
    datasets.extend([('git6b_complete',refs['cng_monthly_panel'],'legacy_complete_claim',4),('git6b_provisional',refs['cng_monthly_provisional'],'legacy_provisional',4)])
    add('current_root_legacy_panel',DATA/'structured/price_revisions/cng_monthly_panel.csv')
    add('desktop_legacy_complete',DESKTOP_ROOT/'BTP/BTP_CNG_Data/structured/price_revisions/cng_monthly_panel.csv')
    add('desktop_fresh_source_targets',DESKTOP_ROOT/'BTP/BTP_CNG_Fresh_2026-11-06/prices/structured/cng_monthly_targets_source_based.csv','unaccepted_source_candidates',6)
    add('PR1_unresolved_panel',DESKTOP_ROOT/'Stage3_GitHub_Audit_2026-11-06/snapshots/github-pr1/BTP_CNG_Data/structured/price_revisions/cng_monthly_panel.csv','unresolved_blank_target_panel',12)
    add('PR1_monthly_candidates',DESKTOP_ROOT/'Stage3_GitHub_Audit_2026-11-06/snapshots/github-pr1/BTP_CNG_Data/structured/price_revisions/primary_history_monthly_candidates.csv','unaccepted_source_candidates',12)
    add('prior_restricted_Stage4',DATA/'stage4_2026-11-06/targets/monthly_targets.csv','previous_accepted_derivation',12)
    accepted=DATA/'accepted_stage3_2026-11-06_restricted_v1/data/price_intervals.csv';acceptedcopy=saved('accepted_price_intervals',accepted);iv=read(acceptedcopy)
    manifest.append(dict(dataset='accepted_intervals',path=str(accepted),audit_copy=str(acceptedcopy),sha256=H(acceptedcopy),rows=len(iv),status='present',kind='accepted_source_intervals'))
    excludedcopy=saved('explicitly_excluded_intervals',DATA/'accepted_stage3_2026-11-06_restricted_v1/metadata/excluded_price_intervals.csv');excluded=read(excludedcopy);excluded_ids={r['interval_id'] for r in excluded}
    assert len(excluded)==12 and not ({r['interval_id'] for r in iv}&excluded_ids)
    manifest.append(dict(dataset='explicitly_excluded_intervals',path=str(DATA/'accepted_stage3_2026-11-06_restricted_v1/metadata/excluded_price_intervals.csv'),audit_copy=str(excludedcopy),sha256=H(excludedcopy),rows=len(excluded),status='present',kind='exclusion_register'))
    # Fresh independent formulation: rational prefix price-mass and coverage
    # integrals. No root target helper or calendar day expansion is used.
    groups=defaultdict(list);byid={}
    for r in iv:
        assert yes(r['accepted_data']) and not yes(r['known_date_conflict'])
        assert r['use_class']=='researcher_accepted_restricted_source_interval'
        a=date.fromisoformat(r['interval_start_date_inclusive']);z=date.fromisoformat(r['interval_end_date_exclusive']);p=Fraction(r['quoted_price_inr_kg']);assert a<z and p>0
        g=city(r['source_market_label']);groups[g].append((a,z,p,r['interval_id']));byid[r['interval_id']]=r
    for g,rs in groups.items():
        rs.sort();assert all(a[1]<=z[0] for a,z in zip(rs,rs[1:]))
    def prefix(rs,t,price=True):
        return sum((max(0,(min(t,z)-a).days)*(p if price else 1) for a,z,p,_ in rs),Fraction(0))
    def quote(rs,t):
        hits=[(p,i) for a,z,p,i in rs if a<=t<z];assert len(hits)<=1;return hits[0] if hits else (None,None)
    def value(f):return '' if f is None else format(float(f),'.15g')
    # Hand-specified independent boundary checks; these are audit examples,
    # never research observations or source substitutions.
    toy=[(date(2020,2,1),date(2020,2,15),Fraction(10),'first'),(date(2020,2,15),date(2020,3,1),Fraction(20),'second')]
    toy_mass=prefix(toy,date(2020,3,1))-prefix(toy,date(2020,2,1))
    assert toy_mass==14*10+15*20 and toy_mass/29==Fraction(440,29)
    assert quote(toy,date(2020,2,14))==(Fraction(10),'first')
    assert quote(toy,date(2020,2,15))==(Fraction(20),'second')
    assert quote(toy,date(2020,3,1))==(None,None)
    gap=[(date(2021,1,1),date(2021,1,2),Fraction(10),'one'),(date(2021,1,3),date(2021,2,1),Fraction(20),'two')]
    assert prefix(gap,date(2021,2,1),False)-prefix(gap,date(2021,1,1),False)==30
    assert quote(gap,date(2021,1,2))==(None,None)
    boundary_checks=['29-day February exact 14/15-day split','inclusive start and exclusive end','no extension past final endpoint','one-day gap remains uncovered','input interval overlap rejected by explicit assertion','source first-day bounds require known previous day']
    expected=[]
    for g in CITIES+['Agra','Unnao']:
        rs=groups.get(g,[])
        for m in months():
            a=date.fromisoformat(m+'-01');z=date.fromisoformat(month_next(m)+'-01');days=(z-a).days;covered=int(prefix(rs,z,False)-prefix(rs,a,False));mass=prefix(rs,z)-prefix(rs,a);full=covered==days
            eom,_=quote(rs,z-timedelta(days=1));avg=mass/days if full else None;lo=mass;hi=mass;known=True
            used={i for x,y,p,i in rs if max(a,x)<min(z,y)};base_used=set(used)
            if full:
                q,prev_id=quote(rs,a-timedelta(days=1))
                if q is None:known=False
                elif prev_id:used.add(prev_id)
                for x,y,p,i in rs:
                    if a<=x<z:
                        q,prev_id=quote(rs,x-timedelta(days=1))
                        if q is None:known=False
                        else:lo+=min(q,p)-p;hi+=max(q,p)-p
            expected.append(dict(city=g,year_month=m,scope='primary_intended_city' if g in CITIES else 'auxiliary_outside_intended_ten',calendar_days=days,covered_days=covered,monthend=eom,average=avg,lower=lo/days if full and known else None,upper=hi/days if full and known else None,used_ids=used,predecessor_ids=used-base_used,reserved=m>=RESERVE))
    emap={(r['city'],r['year_month']):r for r in expected}
    write('approved_targets_recomputed.csv',[{k:(value(v) if k in ['monthend','average','lower','upper'] else json.dumps(sorted(v)) if k in ['used_ids','predecessor_ids'] else v) for k,v in r.items()} for r in expected])
    comparison=[];target_diffs=[];lineage_diffs=[];version_sourcecounts={}
    for fname in ['coverage_calendar','analysis_targets','development_targets','reserved_targets','auxiliary_coverage_calendar','auxiliary_targets']:
        path=DATA/'stage4_2026-11-09/analysis'/f'{fname}.csv'
        p=saved('new_'+fname,path);rs=read(p);version_sourcecounts[fname]=len(rs);manifest.append(dict(dataset='new_'+fname,path=str(path),audit_copy=str(p),sha256=H(p),rows=len(rs),status='present',kind='current_stage4_producer'))
        assert len({(city(r['city']),r['year_month']) for r in rs})==len(rs)
        for r in rs:
            key=(city(r['city']),r['year_month']);assert key in emap
            e=emap[key];assert r['year_month']>=FIRST and r['year_month']<=LAST
            assert r['sample_period'] in ['provisionally_reserved','development']
            assert (r['sample_period']=='provisionally_reserved')==e['reserved']
            for field,col in [('monthend','cng_price_monthend'),('average','cng_price_twap'),('lower','twap_conditional_lower'),('upper','twap_conditional_upper')]:
                y=num(r[col]);x=e[field]
                bad=(x is None)!=(y is None) or (x is not None and abs(x-Fraction(y))>Fraction(1,10**8))
                if bad:target_diffs.append(dict(dataset=fname,city=key[0],month=key[1],field=col,independent=value(x) if not e['reserved'] else 'MASKED_RESERVED',producer=str(y) if not e['reserved'] else 'MASKED_RESERVED'))
            if int(r['covered_days'])!=e['covered_days'] or int(r['calendar_days'])!=e['calendar_days']:target_diffs.append(dict(dataset=fname,city=key[0],month=key[1],field='coverage_days',independent=e['covered_days'],producer=r['covered_days']))
            assert r['historical_predictor_eligible']=='False' and json.loads(r['source_publication_dates'])==[]
            assert r['research_scope']==e['scope']
            if True: # Check every exported copy, not just its coverage-calendar parent.
                ids=set(json.loads(r['source_interval_ids']));hashes=set(json.loads(r['source_sha256s']));urls=set(json.loads(r['source_urls']));locators=json.loads(r['source_locators'])
                eh={byid[i]['source_sha256'] for i in e['used_ids']};eu={byid[i]['source_url'] for i in e['used_ids']}
                el={(i,byid[i]['start_source_locator'],byid[i]['end_source_locator']) for i in e['used_ids']};al={(x['interval_id'],x['start'],x['end']) for x in locators}
                predecessors=set(json.loads(r['timing_predecessor_interval_ids']))
                assert not(ids&excluded_ids)
                if ids!=e['used_ids'] or hashes!=eh or urls!=eu or al!=el or predecessors!=e['predecessor_ids']:
                    lineage_diffs.append(dict(dataset=fname,city=key[0],year_month=key[1],missing_interval_ids=json.dumps(sorted(e['used_ids']-ids)),extra_interval_ids=json.dumps(sorted(ids-e['used_ids'])),hashes_exact=hashes==eh,urls_exact=urls==eu,locators_exact=al==el,predecessor_ids_exact=predecessors==e['predecessor_ids'],reason='All inputs used for price-day bounds, including preceding-day quote, require row lineage'))
    # Observation claims and baseline/change counts are reconstructed independently.
    obs=refs['discrete_observations'];bycity=defaultdict(list)
    for r in obs:bycity[city(r['city'])].append(r)
    changes=[];construction=[];rawlink=[]
    for g,rs in sorted(bycity.items()):
        rs.sort(key=lambda r:r['observation_date']);assert len({r['observation_date'] for r in rs})==len(rs)
        baseline=1;hikes=cuts=holds=0;prev=None
        for r in rs:
            p=Decimal(r['cng_price']);delta=None if prev is None else p-prev
            if delta is not None:
                if delta>0:hikes+=1
                elif delta<0:cuts+=1
                else:holds+=1
            prev=p
        changes.append(dict(city=g,source_rows=len(rs),initial_baseline_records=baseline,actual_nonzero_sampled_changes=hikes+cuts,hikes=hikes,cuts=cuts,same_price_observation_repeats=holds,earliest_feed_date=rs[0]['observation_date'],latest_feed_date=rs[-1]['observation_date'],quality='Observed aggregator chart points, not independently verified effective revisions; publication dates are proxies'))
        raw=saved('git6b_raw_'+g.lower(),blob=git(ref,'raw/cng_prices/'+g.lower()+'_raw_response.html'));text=raw.read_text(encoding='utf-8-sig')
        pairs=[]
        for dt,p in re.findall(r"new Date\('([^']+)'\)\s*,\s*y:([\d.]+)",text):
            pairs.append((datetime.strptime(dt.strip(),'%b %d %Y').date().isoformat(),Decimal(p)))
        rawpairs=set(pairs);tablepairs={(r['observation_date'],Decimal(r['cng_price'])) for r in rs};rawlink.append(dict(city=g,raw_sha256=H(raw),raw_rows=len(pairs),unique_raw_pairs=len(rawpairs),table_rows=len(rs),table_pairs_missing_in_raw=len(tablepairs-rawpairs),raw_pairs_missing_in_table=len(rawpairs-tablepairs),source='MyPetrolPrice chart payload; source identity does not certify price truth or effective/publication timing'))
        # Reproduce only the documented legacy arithmetic for diagnosis. This is
        # NOT used to declare aggregator holds verified or to extend accepted paths.
        daily={};first=date.fromisoformat(rs[0]['observation_date']);last=date.fromisoformat(rs[-1]['observation_date']);events={date.fromisoformat(r['observation_date']):Decimal(r['cng_price']) for r in rs};p=None;day=first
        while day<=last:
            if day in events:p=events[day]
            daily[day]=p;day+=timedelta(days=1)
        for m in sorted({d.strftime('%Y-%m') for d in daily}):
            ds=sorted(d for d in daily if d.strftime('%Y-%m')==m);nd=calendar.monthrange(ds[0].year,ds[0].month)[1];feed=sum(d in events for d in ds)
            construction.append(dict(city=g,year_month=m,days_in_calendar_month=nd,days_in_feed_derived_sample=len(ds),actual_feed_point_days=feed,forward_held_days=len(ds)-feed,days_before_first_sample=ds[0].day-1,partial_first_historical_month=len(ds)!=nd and m<LAST,incomplete_November=m=='2026-11',backfilled_days_in_examined_builder=0,derived_last_sample_quote=str(daily[ds[-1]]) if m<RESERVE else 'MASKED_RESERVED',derived_sample_average=str(sum(daily[d] for d in ds)/len(ds)) if m<RESERVE else 'MASKED_RESERVED',continuity_status='unsupported_as_verified_effective_path_until_independent_source_validation',historical_availability='unverified_feed_proxy'))
    # Compare all prior target artifacts at their recorded precision; matching a
    # price never upgrades an unsupported source history to accepted evidence.
    for label,rs,kind,prec in datasets:
        counts=Counter();keys=Counter();field_counts={'monthend':Counter(),'average':Counter()}
        for r in rs:
            g=city(r.get('city',r.get('market',r.get('geography_name',''))));m=r.get('year_month',r.get('month',''));keys[(g,m)]+=1
            x=num(r.get('cng_price_monthend',r.get('month_end_price_inr_kg',r.get('month_end_price',''))));y=num(r.get('cng_price_twap',r.get('day_weighted_day_end_average_inr_kg',r.get('time_weighted_average',''))))
            e=emap.get((g,m));scope='primary_intended_city' if g in CITIES else 'auxiliary_or_outside_intended_ten';inside=FIRST<=m<=LAST;reserved=RESERVE<=m<=LAST
            def status(v,field,tolerance):
                if v is None:return 'missing_source_target'
                if not inside:return 'excluded_outside_envelope'
                if e is None or e[field] is None:return 'no_accepted_counterpart'
                delta=abs(Fraction(v)-e[field])
                return 'exact_numeric_match' if delta==0 else 'match_at_export_precision' if delta<=tolerance else 'numeric_conflict'
            sx=status(x,'monthend',Fraction(1,10**8));sy=status(y,'average',Fraction(1,2*10**prec))
            counts[sx]+=1;counts[sy]+=1
            field_counts['monthend'][sx]+=1;field_counts['average'][sy]+=1
            comparison.append(dict(dataset=label,city=g,year_month=m,scope=scope,inside_envelope=inside,reserved_quality_exposure=reserved,source_kind=kind,monthend_status=sx,average_status=sy,legacy_monthend='' if x is None else 'MASKED_RESERVED' if reserved else str(x),accepted_monthend='' if e is None or e['monthend'] is None else 'MASKED_RESERVED' if reserved else value(e['monthend']),legacy_average='' if y is None else 'MASKED_RESERVED' if reserved else str(y),accepted_average='' if e is None or e['average'] is None else 'MASKED_RESERVED' if reserved else value(e['average']),export_precision=prec,source_publication_status=r.get('publication_verification_status',r.get('publication_status',r.get('verification_status','not_recorded'))),eligibility_decision='previous_accepted_derivation_consistency_reference' if kind=='previous_accepted_derivation' else 'not_promoted_from_legacy_or_candidate_by_numeric_agreement'))
        version_sourcecounts[label]=dict(rows=len(rs),duplicate_city_month_rows=sum(n-1 for n in keys.values() if n>1),comparison_status_counts=dict(counts),comparison_status_counts_by_target={k:dict(v) for k,v in field_counts.items()})
    scope=[]
    legacy={(city(r['city']),r['year_month']):r for r in refs['cng_monthly_panel']}
    for g in CITIES:
        es=[r for r in expected if r['city']==g];scope.append(dict(city=g,intended_calendar_months=len(es),legacy_complete_claim_rows=sum((g,m) in legacy for m in months()),accepted_monthend_rows=sum(r['monthend'] is not None for r in es),accepted_day_average_rows=sum(r['average'] is not None for r in es),accepted_development_monthend_rows=sum(r['monthend'] is not None and not r['reserved'] for r in es),accepted_development_average_rows=sum(r['average'] is not None and not r['reserved'] for r in es),disposition='primary_accepted_source_subset' if any(r['monthend'] is not None for r in es) else 'intended_city_missing_accepted_price_path_do_not_fill'))
    write('city_month_reconciliation.csv',comparison);write('coverage_by_intended_city.csv',scope);write('observation_changes_by_city.csv',changes);write('legacy_monthly_construction_audit.csv',construction);write('raw_feed_linkage.csv',rawlink);write('target_math_differences.csv',target_diffs,['dataset','city','month','field','independent','producer']);write('target_lineage_differences.csv',lineage_diffs,['dataset','city','year_month','missing_interval_ids','extra_interval_ids','hashes_exact','urls_exact','locators_exact','predecessor_ids_exact','reason']);write('source_inventory.csv',manifest)
    summary=dict(run_id=RUN,accepted_interval_rows=len(iv),approved_snapshot_sha256=H(acceptedcopy),intended_cities=CITIES,envelope=[FIRST,LAST],intended_grid_rows=190*10,primary_accepted_monthend=sum(r['accepted_monthend_rows'] for r in scope),primary_accepted_average=sum(r['accepted_day_average_rows'] for r in scope),primary_development_monthend=sum(r['accepted_development_monthend_rows'] for r in scope),primary_development_average=sum(r['accepted_development_average_rows'] for r in scope),auxiliary_monthend=sum(r['monthend'] is not None for r in expected if r['city'] not in CITIES),auxiliary_average=sum(r['average'] is not None for r in expected if r['city'] not in CITIES),cities_missing_accepted_paths=[r['city'] for r in scope if not r['accepted_monthend_rows']],legacy_observation_rows=sum(r['source_rows'] for r in changes),legacy_baselines=sum(r['initial_baseline_records'] for r in changes),legacy_actual_nonzero_sampled_changes=sum(r['actual_nonzero_sampled_changes'] for r in changes),legacy_same_price_repeats=sum(r['same_price_observation_repeats'] for r in changes),legacy_provisional_rows=len(refs['cng_monthly_provisional']),legacy_partial_first_months=sum(not r['incomplete_November'] and r['partial_first_historical_month'] for r in construction),legacy_incomplete_November_rows=sum(r['incomplete_November'] for r in construction),raw_table_linkage_failures=sum(r['table_pairs_missing_in_raw'] for r in rawlink),producer_math_discrepancies=len(target_diffs),producer_lineage_discrepancies=len(lineage_diffs),legacy_versions=version_sourcecounts,critical_validity_qualifications=['Commercial chart observations and derived holds are not verified effective-date price paths','No examined CNG builder backward-fills dates before its earliest feed observation; do not equate every forward hold with a fabricated observation','Price equality does not certify publication availability or complete source history','Agra and Unnao retained as auxiliary only under current intended-city brief','Legacy publication proxies remain unverified; synthetic VAHAN not used','All reserved numeric comparison was source-quality audit only; no reserved EDA/model/metric selection'],reserved_outcome_quality_access=True,stage5_started=False)
    summary.update(boundary_checks=boundary_checks,excluded_intervals_checked=len(excluded),excluded_intervals_used=0,all_exports_lineage_rows_checked=sum(version_sourcecounts[f] for f in ['coverage_calendar','analysis_targets','development_targets','reserved_targets','auxiliary_coverage_calendar','auxiliary_targets']),explicit_predecessor_fields_checked=True,prior_stage4_matched_subset_conflicts=version_sourcecounts['prior_restricted_Stage4']['comparison_status_counts'].get('numeric_conflict',0),local_archive_root=str(DESKTOP_ROOT),reproduction_dependencies='Standard-library Python, this repository with Git commit 6b08b99666ef2b08605c63499418503a4d666c3b available, current/accepted/prior targets, and optional Desktop archive supplied by --desktop-root; frozen audit input copies and source inventory are retained')
    dump('reconciliation_summary.json',summary)
    report=['TARGET RECONCILIATION AND INDEPENDENT RECONSTRUCTION — 9 NOVEMBER2026','',json.dumps({k:v for k,v in summary.items() if k!='legacy_versions'},indent=2),'','Read city_month_reconciliation.csv for matches/conflicts/missing counterparts.','Numbers in reserved comparison exports are masked. This pass accessed protected values','only to verify source quality, arithmetic and lineage, never to select a model or sample.','Legacy 275 is265nonzero sampled-price changes plus10baselines. The2,018','same-price repeats are observations, not revisions. Main4d labels2,293points as revisions.','The1,503complete legacy rows are a distinct recovery-branch artifact from main1,521.','Eight initial partial historical months and ten incomplete November rows explain18','provisional rows. Their numeric presence must not make them finalized monthly targets.','The historical source chart plus forward holds can reproduce a number without proving','it is a complete effective-date price path. No automatic promotion to accepted data.','New intended ten-city scope does not add missing prices for seven cities.','Jan2011–Oct2026 is190potential months, not190observed months for every city.','Source versions, failed attempts and raw audit inputs are retained in this run folder.']
    (R/'RECONCILIATION_REPORT.txt').write_text('\n'.join(report)+'\n')
    log('completed',run_directory=str(R),summary_sha256=H(R/'reconciliation_summary.json'),producer_math_discrepancies=len(target_diffs),producer_lineage_discrepancies=len(lineage_diffs),reserved_quality_access=True)
    (OUT/'latest_run.json').write_text(json.dumps(dict(run_id=RUN,run_directory=str(R),summary_path=str(R/'reconciliation_summary.json')),indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k!='legacy_versions'},indent=2))

try:run()
except Exception as e:
    (R/'FAILURE.txt').write_text(traceback.format_exc());log('failed',run_directory=str(R),error=str(e),traceback_path=str(R/'FAILURE.txt'));raise
