"""Independent NumPy/Pandas audit; no producer helper imports; fresh output required."""
from pathlib import Path
import argparse,csv,datetime as dt,hashlib,json,sys,platform
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--stage',type=Path,default=P.parent);ap.add_argument('--output',type=Path,default=P/'independent_eda_audit');args=ap.parse_args();S=args.stage;O=args.output
if O.exists():raise FileExistsError('Fresh audit output required')
O.mkdir();stamp=dt.datetime.now(dt.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
inputs=[S/'analysis/coverage_calendar.csv',S/'metadata/analysis_specification.json',S/'scripts/profile_analysis.py']+sorted((S/'eda').glob('*.csv'))
(O/'pre_execution.json').write_text(json.dumps(dict(timestamp_utc=stamp,question='Independent descriptive EDA arithmetic and scope verification',method='NumPy/Pandas versus producer Decimal/statistics; numeric parsing only after development filter',inputs={str(p.relative_to(S)):sha(p) for p in inputs},script_sha256=sha(Path(__file__))),indent=2))
checks=[]
def check(name,ok,detail=''):
 checks.append(dict(check=name,passed=bool(ok),detail=str(detail)))
def close(name,a,b):check(name,np.isclose(float(a),float(b),rtol=1e-10,atol=1e-9),f'independent={a};producer={b}')
spec=json.loads((S/'metadata/analysis_specification.json').read_text());allrows=rows(S/'analysis/coverage_calendar.csv');keys={(r['city'],r['year_month']) for r in allrows}
check('1900_unique_core_calendar_rows',len(allrows)==1900 and len(keys)==1900,len(allrows))
check('ten_intended_core_cities',set(r['city'] for r in allrows)==set(spec['primary_cities']) and len(spec['primary_cities'])==10)
check('calendar_envelope',min(r['year_month'] for r in allrows)=='2011-01' and max(r['year_month'] for r in allrows)=='2026-10')
# Keep all reserved values as opaque strings. Filter first, then create numeric frame.
dev=[r for r in allrows if r['sample_period']=='development'];check('filter_excludes_reserved_dates',all(r['year_month']<spec['reserved_start'] for r in dev))
check('development_calendar_rows',len(dev)==1780,len(dev));check('reserved_calendar_rows',len(allrows)-len(dev)==120)
targets=['cng_price_monthend','cng_price_twap'];active=sorted({r['city'] for r in dev if any(r[t] for t in targets)});absent=sorted(set(spec['primary_cities'])-set(active))
check('three_supported_core_cities',active==['Delhi','Lucknow','Noida'],active)
check('seven_absent_cities_no_invented_price',len(absent)==7 and all(not r[t] for r in allrows if r['city'] in absent for t in targets),absent)
check('auxiliary_markets_separate',not ({'Agra','Unnao'} & {r['city'] for r in allrows}))
f=pd.DataFrame(dev);f['ordinal']=f['year_month'].map(lambda s:int(s[:4])*12+int(s[5:]));f=f.set_index(['city','ordinal'])
for t in targets:f[t]=pd.to_numeric(f[t],errors='coerce')
summaries=rows(S/'eda/descriptive_summary.csv');persistence=rows(S/'eda/persistence.csv');producer_changes=rows(S/'eda/adjacent_changes.csv');corrs=rows(S/'eda/matched_correlations.csv');flags=rows(S/'eda/flagged_changes.csv');series={};independent_changes={};flagkeys=set()
for r in summaries:
 city,t=r['city'],r['target'];g=f.xs(city).sort_index();v=g[t].dropna();months=g.loc[v.index,'year_month']
 check('summary_n_'+city+t,len(v)==int(r['n']));check('summary_dates_'+city+t,months.iloc[0]==r['first_month'] and months.iloc[-1]==r['last_month'])
 for k,value in dict(mean=v.mean(),sample_sd=v.std(ddof=1),minimum=v.min(),median=v.median(),maximum=v.max()).items():close('summary_'+city+t+k,value,r[k])
 # Full calendar reindex ensures diff never bridges missing or uncovered months.
 grid=g[t].reindex(range(g.index.min(),g.index.max()+1));delta=grid.diff().dropna();values=delta.to_numpy();nz=values[np.abs(values)>1e-10];flat=int(np.sum(np.abs(values)<=1e-10))
 pr=next(x for x in persistence if x['city']==city and x['target']==t)
 for k,value in dict(adjacent_pairs=len(delta),flat_pairs=flat,nonzero_pairs=len(nz),hikes=int(np.sum(nz>0)),cuts=int(np.sum(nz<0))).items():check('persistence_'+city+t+k,value==int(pr[k]))
 close('persistence_'+city+t+'flat_fraction',flat/len(delta),pr['flat_fraction']);close('persistence_'+city+t+'max_abs_change',np.max(np.abs(nz)) if len(nz) else 0,pr['max_abs_change'])
 bounds=None
 if len(nz)>=8:
  q1,q3=np.quantile(nz,[.25,.75],method='linear')
  if q3>q1:bounds=(q1-1.5*(q3-q1),q3+1.5*(q3-q1))
 series[(city,t,'level')]=pd.Series(v.to_numpy(),index=months.to_numpy())
 months_delta=[g.loc[k,'year_month'] for k in delta.index];series[(city,t,'change')]=pd.Series(values,index=months_delta)
 for k,x in delta.items():
  mo=g.loc[k,'year_month'];prev=g.loc[k-1,'year_month'];key=(city,t,mo);independent_changes[key]=(prev,x,g.loc[k,'source_interval_ids'])
  if abs(x)>1e-10 and bounds and (x<bounds[0]-1e-10 or x>bounds[1]+1e-10):flagkeys.add(key)
check('six_summaries_and_persistence',len(summaries)==6 and len(persistence)==6)
ckeys={(r['city'],r['target'],r['year_month']) for r in producer_changes};check('759_change_keys_exact',len(producer_changes)==759 and len(ckeys)==759 and ckeys==set(independent_changes))
for r in producer_changes:
 key=(r['city'],r['target'],r['year_month']);prev,x,source=independent_changes[key]
 check('change_metadata_'+'|'.join(key),prev==r['previous_month'] and source==r['source_interval_ids'] and r['action']=='retain')
 close('change_value_'+'|'.join(key),x,r['change_inr_kg'])
 check('change_flag_'+'|'.join(key),(r['flagged_tukey']=='True')==(key in flagkeys))
check('54_flags_exact_and_retained',len(flags)==54 and len(flagkeys)==54 and {(r['city'],r['target'],r['year_month']) for r in flags}==flagkeys and all(r['action']=='retain' for r in flags))
check('12_correlations',len(corrs)==12)
for r in corrs:
 a=series[(r['city_a'],r['target'],r['quantity'])];b=series[(r['city_b'],r['target'],r['quantity'])];both=pd.concat([a,b],axis=1,join='inner').dropna().sort_index();label='|'.join(r[k] for k in ['city_a','city_b','target','quantity'])
 check('correlation_n_'+label,len(both)==int(r['matched_months']));check('correlation_dates_'+label,both.index[0]==r['first_month'] and both.index[-1]==r['last_month']);close('correlation_'+label,both.iloc[:,0].corr(both.iloc[:,1]),r['pearson'])
producer=(S/'scripts/profile_analysis.py').read_text();check('producer_filter_before_decimal_target_parsing',producer.index("dev=[r for r in allrows")<producer.index("vals=[Decimal(r[target])"))
check('producer_plot_uses_filtered_groups','rs=groups[city]' in producer and "float(r[target]) if r[target] else math.nan for r in rs" in producer)
with (O/'checks.csv').open('w',newline='') as h:w=csv.DictWriter(h,fieldnames=['check','passed','detail']);w.writeheader();w.writerows(checks)
result=dict(timestamp_utc=dt.datetime.now(dt.timezone.utc).isoformat(),checks=len(checks),passed=sum(r['passed'] for r in checks),failed=[r for r in checks if not r['passed']],summary_rows=len(summaries),persistence_rows=len(persistence),adjacent_changes=len(independent_changes),tukey_flags=len(flagkeys),correlations=len(corrs),active_core_cities=active,absent_core_cities=absent,reserved_numeric_values_inspected=False,producer_helpers_imported=False,environment=dict(python=sys.version,numpy=np.__version__,pandas=pd.__version__),limitations=['Numerical reconciliation does not certify source truth or historical predictor publication availability.','Only three of ten intended cities have accepted targets. Agra/Unnao are auxiliary and not silently counted as completing ten cities.','Cities share two operators; common shocks and matched trends preclude independent-city or causal interpretations.','Different target coverage creates unequal period means; unmatched ranges are not regional price premia.','Tukey thresholds are descriptive flags, not rejection or significance tests.','Reservation is provisional with documented prior-study exposure, not a pristine final test.'])
(O/'result.json').write_text(json.dumps(result,indent=2))
(O/'INDEPENDENT_EDA_AUDIT.txt').write_text('INDEPENDENT STAGE 4 EDA AUDIT\n\n'+f"{result['passed']}/{result['checks']} checks passed. Recomputed 6 summaries, 6 persistence records, all 759 adjacent-month changes, 54 retained Tukey flags and 12 matched-month correlations with NumPy/Pandas, independently of producer Decimal/statistics helpers.\n\n"+'The 1,900-row calendar covers ten intended cities Jan2011–Oct2026. The development filter is applied to string rows before numeric conversion; 1,780 development calendar rows and 120 provisional-reservation rows. Seven unsupported cities contain no invented prices. Three supported core cities are Delhi, Noida and Lucknow; Agra and Unnao remain separate auxiliaries. Missing months break changes and plotted lines.\n\n'+'\n'.join(result['limitations'])+'\n\nNo model fit, stationarity/break test, holdout performance, or causal claim was produced by this audit. Scope is Stage4; original nine-stage protocol remains governing.\n')
(O/'output_checksums.json').write_text(json.dumps({p.name:sha(p) for p in sorted(O.iterdir()) if p.is_file()},indent=2))
print(json.dumps({k:result[k] for k in ['checks','passed','failed','adjacent_changes','tukey_flags','correlations']},indent=2))
if result['failed']:raise SystemExit(1)
