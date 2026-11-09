"""Descriptive Stage 4 profile. No holdout value is parsed for EDA.

Standard-library arithmetic and matplotlib for static scientific figures.
No learned transformation, inferential test, feature selection or forecasting.
"""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import argparse, calendar, csv, datetime as dt, hashlib, json, math, platform, statistics, sys

HERE=Path(__file__).resolve().parents[1]
TARGETS=['cng_price_monthend','cng_price_twap']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def write(p,rs,cols):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');w.writeheader();w.writerows(rs)
def index(month):
    y,m=map(int,month.split('-'));return y*12+m
def adjacent(rs,target):
    by={index(r['year_month']):r for r in rs if r[target]}
    return [(by[k-1],by[k],Decimal(by[k][target])-Decimal(by[k-1][target])) for k in sorted(by) if k-1 in by]
def pearson(x,y):
    if len(x)<3:return None
    mx=statistics.mean(x);my=statistics.mean(y)
    a=sum((v-mx)*(w-my) for v,w in zip(x,y));b=sum((v-mx)**2 for v in x)*sum((w-my)**2 for w in y)
    return a/b.sqrt() if b>0 else None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=HERE);ap.add_argument('--output',type=Path,default=HERE)
    args=ap.parse_args();src=args.input;out=args.output
    if (out/'eda/descriptive_summary.csv').exists():raise FileExistsError('Use a fresh --output directory; do not overwrite completed EDA.')
    for sub in ['eda','figures','metadata','logs']:(out/sub).mkdir(parents=True,exist_ok=True)
    spec=json.loads((HERE/'metadata/analysis_specification.json').read_text())
    stamp=dt.datetime.now(dt.timezone.utc).isoformat();rid='S4R-EDA-'+stamp
    def reg(x):
        with (out/'metadata/experiment_registry.jsonl').open('a') as f:f.write(json.dumps(x)+'\n')
    reg(dict(experiment_id=rid,timestamp_utc=stamp,status='started_before_numeric_eda',question='Coverage, persistence and descriptive differences across supported core cities',
             input_sha256=sha(src/'analysis/coverage_calendar.csv'),script_sha256=sha(Path(__file__)),spec_sha256=sha(HERE/'metadata/analysis_specification.json'),
             method='development-only descriptive arithmetic, adjacent-only changes, matched-month correlations',
             training_validation_test='no model training; Nov2025-Oct2026 provisionally reserved',hyperparameters='Tukey1.5IQR only when n>=8 nonzero changes and IQR>0; flag only',seed=None,comparison_type='exploratory'))
    # The filter is applied to string rows before parsing any target value.
    allrows=read(src/'analysis/coverage_calendar.csv')
    if len({(r['city'],r['year_month']) for r in allrows})!=len(allrows):raise ValueError('Duplicate city-month key')
    dev=[r for r in allrows if r['sample_period']=='development']
    if any(r['year_month']>=spec['reserved_start'] for r in dev):raise ValueError('Reserved outcome entered EDA')
    groups={c:[r for r in dev if r['city']==c] for c in spec['primary_cities']}
    coverage=[];spans=[]
    for city in spec['primary_cities']:
        for period in ['all','development','provisionally_reserved']:
            rs=[r for r in allrows if r['city']==city and (period=='all' or r['sample_period']==period)]
            coverage.append(dict(city=city,period=period,calendar_months=len(rs),monthend_available=sum(bool(r[TARGETS[0]]) for r in rs),
                                 twap_available=sum(bool(r[TARGETS[1]]) for r in rs),missing_days=sum(int(r['missing_days']) for r in rs),
                                 accepted_path_months=sum(int(r['covered_days'])>0 for r in rs)))
        for target in TARGETS:
            missing=[r for r in allrows if r['city']==city and not r[target]]
            run=[]
            for r in missing+[None]:
                if run and (r is None or index(r['year_month'])!=index(run[-1]['year_month'])+1):
                    spans.append(dict(city=city,target=target,missing_start=run[0]['year_month'],missing_end=run[-1]['year_month'],months=len(run),reason='no accepted target under required calendar coverage'));run=[]
                if r:run.append(r)
    summary=[];persist=[];changes=[];yearly=[];flags=[];series={}
    for city,rs in groups.items():
        for target in TARGETS:
            vals=[Decimal(r[target]) for r in rs if r[target]]
            if not vals:continue
            obs=[r for r in rs if r[target]];pairs=adjacent(rs,target)
            summary.append(dict(city=city,target=target,n=len(vals),first_month=obs[0]['year_month'],last_month=obs[-1]['year_month'],
                                mean=str(statistics.mean(vals)),sample_sd=str(statistics.stdev(vals)) if len(vals)>1 else '',minimum=str(min(vals)),median=str(statistics.median(vals)),maximum=str(max(vals))))
            nz=[x for _,_,x in pairs if x!=0];flat=sum(x==0 for _,_,x in pairs)
            persist.append(dict(city=city,target=target,adjacent_pairs=len(pairs),flat_pairs=flat,nonzero_pairs=len(nz),
                                flat_fraction=flat/len(pairs) if pairs else '',hikes=sum(x>0 for x in nz),cuts=sum(x<0 for x in nz),
                                max_abs_change=str(max(abs(x) for x in nz)) if nz else '0'))
            series[(city,target,'level')]={r['year_month']:Decimal(r[target]) for r in rs if r[target]}
            series[(city,target,'change')]={b['year_month']:x for a,b,x in pairs}
            quartiles=statistics.quantiles(nz,n=4,method='inclusive') if len(nz)>=8 else None
            lo=hi=None
            if quartiles and quartiles[2]>quartiles[0]:
                iqr=quartiles[2]-quartiles[0];lo=quartiles[0]-Decimal('1.5')*iqr;hi=quartiles[2]+Decimal('1.5')*iqr
            for a,b,x in pairs:
                row=dict(city=city,target=target,previous_month=a['year_month'],year_month=b['year_month'],change_inr_kg=str(x),
                         flagged_tukey=bool(x!=0 and lo is not None and (x<lo or x>hi)),action='retain',source_interval_ids=b['source_interval_ids'])
                changes.append(row)
                if row['flagged_tukey']:flags.append(row)
            for year in sorted({b['year_month'][:4] for a,b,x in pairs}):
                ys=[x for a,b,x in pairs if b['year_month'].startswith(year)]
                yearly.append(dict(city=city,target=target,year=year,adjacent_pairs=len(ys),nonzero_pairs=sum(x!=0 for x in ys),
                                   sum_abs_change_inr_kg=str(sum(map(abs,ys))),sample_sd_change=str(statistics.stdev(ys)) if len(ys)>1 else '',
                                   interpretation='descriptive partial-year/regime mixture; not a structural-break test'))
    corr=[];active=[c for c in spec['primary_cities'] if any(r[TARGETS[0]] or r[TARGETS[1]] for r in groups[c])]
    for target in TARGETS:
        for kind in ['level','change']:
            for i,a in enumerate(active):
                for b in active[i+1:]:
                    x=series.get((a,target,kind),{});y=series.get((b,target,kind),{});dates=sorted(set(x)&set(y))
                    rho=pearson([x[d] for d in dates],[y[d] for d in dates])
                    corr.append(dict(city_a=a,city_b=b,target=target,quantity=kind,matched_months=len(dates),pearson=str(rho) if rho is not None else '',
                                     first_month=dates[0] if dates else '',last_month=dates[-1] if dates else '',interpretation='descriptive; common trends/operators; not predictive or causal evidence'))
    for name,rs,cols in [('coverage_by_city',coverage,list(coverage[0])),('missing_spans',spans,list(spans[0])),
                         ('descriptive_summary',summary,list(summary[0])),('persistence',persist,list(persist[0])),
                         ('adjacent_changes',changes,list(changes[0])),('yearly_change_profile',yearly,list(yearly[0])),
                         ('flagged_changes',flags,list(changes[0])),('matched_correlations',corr,list(corr[0]))]:write(out/f'eda/{name}.csv',rs,cols)
    # Rendering uses the existing scientific Python because bundled runtime has no matplotlib.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np
    from matplotlib.colors import ListedColormap, BoundaryNorm
    from matplotlib.patches import Patch
    calendar_months=[r['year_month'] for r in allrows if r['city']==spec['primary_cities'][0]]
    matrix=[]
    for city in spec['primary_cities']:
        rs=[r for r in allrows if r['city']==city]
        matrix.append([2 if r[TARGETS[1]] else 1 if r[TARGETS[0]] else 0 for r in rs])
    fig,ax=plt.subplots(figsize=(13,5.7));ax.imshow(matrix,aspect='auto',interpolation='nearest',cmap=ListedColormap(['#ededed','#e0a457','#285f85']),norm=BoundaryNorm([-.5,.5,1.5,2.5],3))
    ax.set_yticks(range(10),spec['primary_cities']);ticks=[i for i,m in enumerate(calendar_months) if m.endswith('-01')]
    ax.set_xticks(ticks,[m[:4] for m in calendar_months if m.endswith('-01')]);cut=calendar_months.index(spec['reserved_start'])
    ax.axvline(cut-.5,color='black',ls='--',lw=1);ax.set_title('Accepted target coverage in the intended ten cities, Jan 2011–Oct 2026\nCoverage only; missing cells contain no invented prices')
    ax.legend(handles=[Patch(color=c,label=l) for c,l in [('#ededed','No accepted target'),('#e0a457','Month-end only'),('#285f85','Both targets')]],loc='upper center',bbox_to_anchor=(.5,-.12),ncol=3,frameon=False)
    ax.set_xlabel('Calendar year; dashed line marks provisional reservation');fig.tight_layout()
    for ext in ['png','svg']:fig.savefig(out/f'figures/target_coverage.{ext}',dpi=170,bbox_inches='tight')
    plt.close(fig)
    fig,axes=plt.subplots(len(active),1,figsize=(12,3*len(active)),sharex=True,squeeze=False)
    for ax,city in zip(axes[:,0],active):
        rs=groups[city];xs=[dt.date.fromisoformat(r['year_month']+'-01') for r in rs]
        for target,label,color in [(TARGETS[0],'Month-end','#285f85'),(TARGETS[1],'Day-end monthly mean','#b16c28')]:
            ax.plot(xs,[float(r[target]) if r[target] else math.nan for r in rs],label=label,color=color,lw=1.4)
        ax.axvspan(dt.date(2025,11,1),dt.date(2026,11,1),color='#eeeeee');ax.set_ylabel('INR/kg');ax.set_title(city,loc='left');ax.grid(alpha=.15)
        ax.set_xlim(dt.date(2011,1,1),dt.date(2026,11,1))
    axes[0,0].legend(frameon=False,ncol=2);axes[-1,0].xaxis.set_major_locator(mdates.YearLocator(2));axes[-1,0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    fig.suptitle('Development-period accepted price paths\nGaps break lines; shaded reservation has no plotted prices',fontsize=14);fig.tight_layout(rect=(0,0,1,.94))
    for ext in ['png','svg']:fig.savefig(out/f'figures/development_prices.{ext}',dpi=170,bbox_inches='tight')
    plt.close(fig)
    fig,axes=plt.subplots(len(active),2,figsize=(12,2.8*len(active)),squeeze=False)
    for i,city in enumerate(active):
        for j,target in enumerate(TARGETS):
            ax=axes[i,j];rs=[r for r in changes if r['city']==city and r['target']==target];xs=[dt.date.fromisoformat(r['year_month']+'-01') for r in rs]
            ax.vlines(xs,0,[float(r['change_inr_kg']) for r in rs],color='#285f85');ax.axhline(0,color='gray',lw=.7);ax.set_title(city+(' — Month-end' if j==0 else ' — Day-end mean'),loc='left');ax.set_ylabel('Change INR/kg');ax.grid(alpha=.15)
            ax.xaxis.set_major_locator(mdates.YearLocator(4));ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    fig.suptitle('Adjacent-month development changes\nMissing months are never bridged; flagged extremes remain retained',fontsize=14);fig.tight_layout(rect=(0,0,1,.93))
    for ext in ['png','svg']:fig.savefig(out/f'figures/development_changes.{ext}',dpi=170,bbox_inches='tight')
    plt.close(fig)
    meta=dict(development_calendar_rows=len(dev),reserved_calendar_rows=len(allrows)-len(dev),development_monthend=sum(bool(r[TARGETS[0]]) for r in dev),development_twap=sum(bool(r[TARGETS[1]]) for r in dev),
              supported_primary_cities=active,missing_primary_cities=[c for c in spec['primary_cities'] if c not in active],
              summary_rows=len(summary),correlation_rows=len(corr),change_rows=len(changes),flagged_rows=len(flags),
              no_reserved_target_numeric_conversion_for_eda=True,no_models_or_formal_tests=True,
              environment=dict(python=sys.version,platform=platform.platform(),matplotlib=matplotlib.__version__,numpy=np.__version__),
              plotting_runtime_note='Bundled Python lacks matplotlib; existing /opt/anaconda3/bin/python3 used, with package versions recorded.')
    (out/'metadata/eda_summary.json').write_text(json.dumps(meta,indent=2))
    reg(dict(experiment_id=rid+'-RESULT',timestamp_utc=dt.datetime.now(dt.timezone.utc).isoformat(),parent=rid,status='completed',decision='descriptive_only',results=meta))
    print(json.dumps(meta,indent=2))

if __name__=='__main__':main()
