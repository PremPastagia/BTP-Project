"""Restricted Stage 4 EDA. Reserved target values are filtered before numeric use."""
from pathlib import Path
from datetime import date,datetime,timezone
from decimal import Decimal
from collections import Counter,defaultdict
import csv,json,hashlib,math,statistics,sys,platform,itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import ListedColormap,BoundaryNorm
from matplotlib.patches import Patch

B=Path(__file__).resolve().parent
S=B.parent
D=S.parent
TARGET=S/'targets/monthly_targets.csv'
INTERVAL=D/'accepted_stage3_2026-11-06_restricted_v1/data/price_intervals.csv'
RESERVE_START='2025-11';RESERVE_END='2026-10'
MARKETS=['Delhi','Noida','Lucknow','Agra','Unnao']
FIELDS={'month_end_price_inr_kg':'Month-end quote','day_weighted_day_end_average_inr_kg':'Calendar-day average'}
for p in [B/'tables',B/'figures',B/'metadata']:p.mkdir(exist_ok=True)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def write(name,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 if not keys:return
 with (B/name).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)
def yes(s):return str(s).lower()=='true'
def finite(v):return v is not None and math.isfinite(float(v))
def idx(s):return int(s[:4])*12+int(s[5:7])
def month_grid(first,last):
 out=[];year,month=int(first[:4]),int(first[5:7])
 while f'{year:04d}-{month:02d}'<=last:
  out.append(f'{year:04d}-{month:02d}');year,month=(year+1,1) if month==12 else (year,month+1)
 return out
def month_date(s):return date(int(s[:4]),int(s[5:7]),1)
def plain(v):
 if isinstance(v,Decimal):return str(v)
 if isinstance(v,dict):return {k:plain(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [plain(x) for x in v]
 if isinstance(v,(np.integer,)):return int(v)
 if isinstance(v,(np.floating,float)):return float(v) if math.isfinite(v) else None
 return v

raw=read(TARGET);interval_raw=read(INTERVAL)
assert len({(r['market'],r['month']) for r in raw})==len(raw),'Duplicate market/month keys'
assert set(r['market'] for r in raw)==set(MARKETS),'Unexpected market scope'
assert all(not yes(r['exploration_eligible']) for r in raw if RESERVE_START<=r['month']<=RESERVE_END)
# Keep only metadata for global coverage; this frame never receives numeric prices.
coverage_rows=[]
for r in raw:
 coverage_rows.append({'market':r['market'],'operator':r['operator'],'month':r['month'],'full_month_covered':yes(r['full_month_covered']),'eom_available':bool(r['month_end_price_inr_kg']),'average_available':bool(r['day_weighted_day_end_average_inr_kg']),'covered_days':int(r['covered_days']),'missing_days':int(r['missing_days']),'exploration_eligible':yes(r['exploration_eligible']),'reserved':yes(r['provisional_reserved_period'])})
coverage=pd.DataFrame(coverage_rows)
# This is the single entry point for numerical target values. Reserved rows are omitted first.
exploration=[r for r in raw if yes(r['exploration_eligible'])]
assert all(r['month']<RESERVE_START for r in exploration),'Unexpected post-cutoff exploratory data'
df=pd.DataFrame([{k:r[k] for k in ['market','operator','month',*FIELDS]} for r in exploration])
for col in FIELDS:df[col]=pd.to_numeric(df[col],errors='coerce')
if any(((df[c]<=0)&df[c].notna()).any() for c in FIELDS):raise ValueError('Nonpositive accepted target price')
df['ordinal']=df['month'].map(idx)
df=df.sort_values(['market','month'])
operators={m:next(r['operator'] for r in raw if r['market']==m) for m in MARKETS}
assert len(set(operators.values()))==2

coverage_summary=[];gap_rows=[]
for market in MARKETS:
 for period,mask in [('all_target_rows',coverage.market==market),('exploration',(coverage.market==market)&coverage.exploration_eligible),('provisionally_reserved',(coverage.market==market)&coverage.reserved)]:
  g=coverage.loc[mask].sort_values('month')
  coverage_summary.append({'market':market,'operator':operators[market],'period':period,'calendar_rows':len(g),'full_month_rows':int(g.full_month_covered.sum()),'month_end_available_rows':int(g.eom_available.sum()),'average_available_rows':int(g.average_available.sum()),'month_end_only_rows':int((g.eom_available&~g.average_available).sum()),'neither_target_available_rows':int((~g.eom_available&~g.average_available).sum()),'missing_calendar_days':int(g.missing_days.sum()),'first_month':g.month.min() if len(g) else '', 'last_month':g.month.max() if len(g) else ''})
 for metric,col in [('month_end','eom_available'),('calendar_day_average','average_available')]:
  g=coverage.loc[coverage.market==market].sort_values('month');run=[]
  for row in g.to_dict('records')+[None]:
   if row is not None and not row[col] and (not run or idx(row['month'])==idx(run[-1]['month'])+1):run.append(row);continue
   if run:gap_rows.append({'market':market,'target':metric,'first_missing_month':run[0]['month'],'last_missing_month':run[-1]['month'],'months':len(run),'includes_reserved_months':any(r['reserved'] for r in run)});run=[]
   if row is not None and not row[col]:run=[row]
write('tables/coverage_by_market.csv',coverage_summary);write('tables/missing_month_spans.csv',gap_rows)

summaries=[];changes=[];persistence=[];flag_rows=[];calendar_rows=[]
for market in MARKETS:
 g=df.loc[df.market==market].sort_values('month')
 for field,label in FIELDS.items():
  v=g.loc[g[field].notna()];x=v[field]
  summaries.append({'market':market,'operator':operators[market],'target':field,'n':len(v),'first_month':v.month.min() if len(v) else '', 'last_month':v.month.max() if len(v) else '', 'mean':x.mean(),'median':x.median(),'sample_sd':x.std(ddof=1),'minimum':x.min(),'maximum':x.max()})
  pairs=[]
  for a,z in zip(g.to_dict('records'),g.to_dict('records')[1:]):
   if z['ordinal']-a['ordinal']==1 and finite(a[field]) and finite(z[field]):
    pairs.append({'market':market,'operator':operators[market],'target':field,'month':z['month'],'previous_month':a['month'],'change_inr_kg':z[field]-a[field],'flat':z[field]==a[field]})
  changes.extend(pairs);flat=sum(r['flat'] for r in pairs)
  persistence.append({'market':market,'target':field,'valid_adjacent_month_pairs':len(pairs),'flat_pairs':flat,'nonzero_pairs':len(pairs)-flat,'flat_fraction':flat/len(pairs) if pairs else None})
  for mm in range(1,13):
   xs=[r['change_inr_kg'] for r in pairs if int(r['month'][5:])==mm]
   calendar_rows.append({'market':market,'operator':operators[market],'target':field,'calendar_month':mm,'adjacent_pairs':len(xs),'mean_change':statistics.mean(xs) if xs else None,'median_change':statistics.median(xs) if xs else None,'interpretation':'descriptive_only_regime_and_coverage_confounded'})
  nonzero=[r for r in pairs if not r['flat']]
  q1,q3=np.quantile([r['change_inr_kg'] for r in nonzero],[.25,.75]) if len(nonzero)>=8 else (np.nan,np.nan)
  iqr=q3-q1;rule_valid=len(nonzero)>=8 and iqr>0
  for r in nonzero:
   tukey=bool(rule_valid and (r['change_inr_kg']<q1-1.5*iqr or r['change_inr_kg']>q3+1.5*iqr))
   top=r in sorted(nonzero,key=lambda r:abs(r['change_inr_kg']),reverse=True)[:3]
   if tukey or top:flag_rows.append({**r,'tukey_nonzero_change_flag':tukey,'among_three_largest_absolute_changes':top,'rule_applicable':rule_valid,'action':'retained_no_outlier_removal','classification':'exploratory_flag_not_evidence_of_error'})
write('tables/target_descriptives.csv',plain(summaries));write('tables/adjacent_month_changes.csv',plain(changes));write('tables/persistence.csv',plain(persistence));write('tables/calendar_descriptive.csv',plain(calendar_rows));write('tables/flagged_changes.csv',plain(flag_rows))

interval_summary=[]
for market in MARKETS:
 # Do not numerically inspect quotes whose interval starts in the reserved window.
 r=[x for x in interval_raw if x['source_market_label']==market and x['interval_start_date_inclusive']<'2025-11-01'];r.sort(key=lambda x:x['interval_start_date_inclusive']);adj=[]
 for a,z in zip(r,r[1:]):
  if a['interval_end_date_exclusive']==z['interval_start_date_inclusive']:
   delta=Decimal(z['quoted_price_inr_kg'])-Decimal(a['quoted_price_inr_kg']);adj.append(delta)
 interval_summary.append({'market':market,'operator':operators[market],'exploratory_start_intervals':len(r),'contiguous_accepted_boundaries':len(adj),'nonzero_price_changes_at_contiguous_boundaries':sum(x!=0 for x in adj),'same_price_boundaries':sum(x==0 for x in adj),'noncontiguous_boundaries_excluded':max(0,len(r)-1-len(adj)),'interpretation':'source_supported_boundaries_not_exhaustive_revision_history'})
write('tables/interval_boundary_summary.csv',interval_summary)

correlations=[]
for field in FIELDS:
 for kind in ['levels','adjacent_changes']:
  if kind=='levels':wide=df.pivot(index='month',columns='market',values=field)
  else:
   sub=pd.DataFrame([r for r in changes if r['target']==field]);wide=sub.pivot(index='month',columns='market',values='change_inr_kg')
  for a,z in itertools.combinations(MARKETS,2):
   pair=wide[[a,z]].dropna();n=len(pair);coef=pair[a].corr(pair[z]) if n>=3 and pair[a].std()>0 and pair[z].std()>0 else np.nan
   correlations.append({'target':field,'kind':kind,'market_a':a,'market_b':z,'matched_months':n,'pearson':coef,'same_operator':operators[a]==operators[z],'overlap_warning':'fewer_than_12_matched_months' if n<12 else 'serial_dependence_and_common_shocks_reduce_information','interpretation':'descriptive_noncausal_not_predictive_evidence'})
write('tables/descriptive_correlations.csv',plain(correlations))

# Independent headline calculations from source strings: no pandas grouping/stat helper is reused.
checks=[]
def check(name,observed,expected,tol=1e-8):
 ok=observed==expected if isinstance(expected,int) else (observed is not None and abs(float(observed)-float(expected))<=tol)
 checks.append({'check':name,'passed':bool(ok),'observed':plain(observed),'independent_expected':plain(expected)})
for m in MARKETS:
 source=[r for r in raw if r['market']==m];check(m+' total coverage rows',next(r['calendar_rows'] for r in coverage_summary if r['market']==m and r['period']=='all_target_rows'),len(source))
 for field in FIELDS:
  xs=sorted([r for r in exploration if r['market']==m],key=lambda r:r['month']);vals=[Decimal(r[field]) for r in xs if r[field]];s=next(r for r in summaries if r['market']==m and r['target']==field)
  check(m+' '+field+' n',s['n'],len(vals))
  if vals:check(m+' '+field+' mean',s['mean'],sum(vals)/Decimal(len(vals)))
  pairs=[]
  for a,z in zip(xs,xs[1:]):
   ay,am=map(int,a['month'].split('-'));zy,zm=map(int,z['month'].split('-'))
   if (zy-ay)*12+zm-am==1 and a[field] and z[field]:pairs.append((Decimal(a[field]),Decimal(z[field])))
  p=next(r for r in persistence if r['market']==m and r['target']==field);check(m+' '+field+' adjacent pairs',p['valid_adjacent_month_pairs'],len(pairs));check(m+' '+field+' flat pairs',p['flat_pairs'],sum(a==z for a,z in pairs))
def independent_pearson(xs,ys):
 if len(xs)<3:return None
 mx=sum(xs)/len(xs);my=sum(ys)/len(ys);vx=sum((x-mx)**2 for x in xs);vy=sum((y-my)**2 for y in ys)
 return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.sqrt(vx*vy) if vx>0 and vy>0 else None
for c in correlations:
 def series(m):
  rows=sorted([r for r in exploration if r['market']==m],key=lambda r:r['month']);out={}
  if c['kind']=='levels':return {r['month']:float(Decimal(r[c['target']])) for r in rows if r[c['target']]}
  for a,z in zip(rows,rows[1:]):
   ay,am=map(int,a['month'].split('-'));zy,zm=map(int,z['month'].split('-'))
   if (zy-ay)*12+zm-am==1 and a[c['target']] and z[c['target']]:out[z['month']]=float(Decimal(z[c['target']])-Decimal(a[c['target']]))
  return out
 a,z=series(c['market_a']),series(c['market_b']);matched=sorted(set(a)&set(z));v=independent_pearson([a[k] for k in matched],[z[k] for k in matched]);check('correlation matched rows '+str(c),c['matched_months'],len(matched))
 if v is not None:check('Pearson '+c['target']+' '+c['kind']+' '+c['market_a']+'/'+c['market_b'],c['pearson'],v,1e-10)
assert all(r['passed'] for r in checks),'Independent descriptive arithmetic mismatch'
(B/'metadata/independent_summary_check.json').write_text(json.dumps(plain({'checks':checks,'all_passed':True,'implementation':'stdlib CSV/Decimal/direct Pearson arithmetic; no pandas summary helper reused'}),indent=2))

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','figure.facecolor':'white','savefig.facecolor':'white','svg.fonttype':'none'})
def save(fig,name):
 fig.savefig(B/'figures'/(name+'.png'),dpi=200,bbox_inches='tight');fig.savefig(B/'figures'/(name+'.svg'),bbox_inches='tight');plt.close(fig)
blue='#24577F';orange='#C27135';red='#B43B42'
fig,axes=plt.subplots(5,1,figsize=(11.5,10),sharex=True,layout='constrained')
grid=month_grid(df.month.min(),'2025-10');plot_dates=[month_date(s) for s in grid]
for ax,m in zip(axes,MARKETS):
 g=df.loc[df.market==m].set_index('month').reindex(grid)
 ax.plot(plot_dates,g['month_end_price_inr_kg'],color=blue,lw=1.7,label='Month-end quote');ax.plot(plot_dates,g['day_weighted_day_end_average_inr_kg'],color=orange,lw=1.3,ls='--',label='Calendar-day average');ax.set_title(m+' — '+('IGL' if 'Indraprastha' in operators[m] else 'Green Gas'),loc='left',fontsize=11);ax.set_ylabel('₹/kg');ax.grid(alpha=.2)
axes[0].legend(loc='upper left',ncol=2,fontsize=9);axes[-1].xaxis.set_major_locator(mdates.YearLocator(2));axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'));axes[-1].set_xlim(plot_dates[0],date(2025,11,1));fig.suptitle('Exploration-period accepted source-based price targets\nGaps remain unfilled; reserved prices from November 2025 are excluded',fontsize=14);save(fig,'price_timelines')

months=month_grid(coverage.month.min(),coverage.month.max());positions={s:i for i,s in enumerate(months)};matrix=np.full((5,len(months)),np.nan)
for row in coverage_rows:matrix[MARKETS.index(row['market']),positions[row['month']]]=2 if row['average_available'] else 1 if row['eom_available'] else 0
cmap=ListedColormap(['#C85B61','#E7C56B','#3F867C']);cmap.set_bad('#F0F0F0');fig,ax=plt.subplots(figsize=(13,3.5),layout='constrained');ax.imshow(matrix,aspect='auto',interpolation='nearest',cmap=cmap,norm=BoundaryNorm([-.5,.5,1.5,2.5],3));ax.set_yticks(range(5),MARKETS);ticks=[i for i,s in enumerate(months) if s.endswith('-01') and int(s[:4])%2==0];ax.set_xticks(ticks,[months[i][:4] for i in ticks]);boundary=positions.get(RESERVE_START)
if boundary is not None:ax.axvline(boundary-.5,color='#333333',ls='--',lw=1);ax.axvspan(boundary-.5,len(months)-.5,facecolor='none',edgecolor='#333333',hatch='////',lw=0)
ax.set_title('Target availability by calendar month\nHatching marks the provisional reserved window; availability only, no reserved prices',loc='left',fontsize=12);ax.legend(handles=[Patch(color='#3F867C',label='Both targets available'),Patch(color='#E7C56B',label='Month-end only'),Patch(color='#C85B61',label='Neither available'),Patch(color='#F0F0F0',label='Outside market scope')],loc='upper center',bbox_to_anchor=(.5,-.18),ncol=4,fontsize=9);save(fig,'target_coverage')

fig,axes=plt.subplots(5,1,figsize=(11.5,9.5),sharex=True,layout='constrained')
for ax,m in zip(axes,MARKETS):
 rows=[r for r in changes if r['market']==m and r['target']=='month_end_price_inr_kg'];ax.axhline(0,color='#777777',lw=.7);ax.vlines([month_date(r['month']) for r in rows],0,[r['change_inr_kg'] for r in rows],color=blue,lw=1);ax.scatter([month_date(r['month']) for r in rows],[r['change_inr_kg'] for r in rows],color=blue,s=12);ax.set_title(m,loc='left',fontsize=11);ax.set_ylabel('Δ ₹/kg');ax.grid(alpha=.15)
axes[-1].xaxis.set_major_locator(mdates.YearLocator(2));axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'));axes[-1].set_xlim(plot_dates[0],date(2025,11,1));fig.suptitle('Month-end changes on valid adjacent months only\nNo comparisons bridge missing months; reserved prices excluded',fontsize=14);save(fig,'adjacent_month_changes')

fig,axes=plt.subplots(5,1,figsize=(11.5,11),sharex=False,layout='constrained')
for ax,m in zip(axes,MARKETS):
 rows=[r for r in calendar_rows if r['market']==m and r['target']=='month_end_price_inr_kg'];ys=[r['mean_change'] if r['mean_change'] is not None else np.nan for r in rows];ax.bar(range(1,13),ys,color=blue,width=.7);ax.axhline(0,color='#666666',lw=.7);ax.set_title(m,loc='left',fontsize=11);ax.set_ylabel('Mean Δ ₹/kg');ax.grid(axis='y',alpha=.15);ax.set_xticks(range(1,13),[__import__('calendar').month_abbr[r['calendar_month']]+'\nn='+str(r['adjacent_pairs']) for r in rows],fontsize=8);ax.tick_params(labelbottom=True)
fig.suptitle('Descriptive calendar-month changes, exploration period only\nUnequal year/regime coverage; this is not evidence of seasonality',fontsize=14);save(fig,'calendar_month_changes')

fig,axes=plt.subplots(2,2,figsize=(11.5,10),layout='constrained');image=None
for ax,(field,kind) in zip(axes.flat,itertools.product(FIELDS,['levels','adjacent_changes'])):
 mat=np.full((5,5),np.nan);counts=np.zeros((5,5),int)
 for c in correlations:
  if c['target']==field and c['kind']==kind:
   i,j=MARKETS.index(c['market_a']),MARKETS.index(c['market_b']);mat[i,j]=mat[j,i]=c['pearson'];counts[i,j]=counts[j,i]=c['matched_months']
 image=ax.imshow(mat,vmin=-1,vmax=1,cmap='RdBu_r');ax.set_xticks(range(5),MARKETS,rotation=40,ha='right');ax.set_yticks(range(5),MARKETS);ax.set_title(FIELDS[field]+' — '+('levels' if kind=='levels' else 'adjacent changes'),fontsize=11)
 for i,j in itertools.product(range(5),repeat=2):
  if i!=j and finite(mat[i,j]):ax.text(j,i,f'{mat[i,j]:.2f}\nn={counts[i,j]}',ha='center',va='center',fontsize=8,color='white' if abs(mat[i,j])>.65 else '#222222')
fig.colorbar(image,ax=axes.ravel().tolist(),shrink=.75,label='Descriptive Pearson correlation');fig.suptitle('Matched-month co-movement; reserved prices excluded\nTwo operators, common trends and serial dependence: no causal or predictive inference',fontsize=13);save(fig,'matched_month_correlations')

reserved_rows=sum(r['reserved'] for r in coverage_rows);expl_eom=int(df['month_end_price_inr_kg'].notna().sum());expl_avg=int(df['day_weighted_day_end_average_inr_kg'].notna().sum());flags=sum(r['tukey_nonzero_change_flag'] for r in flag_rows if r['target']=='month_end_price_inr_kg')
lines=['STAGE 4 EXPLORATORY DATA REPORT',datetime.now(timezone.utc).isoformat(),'','SCOPE AND RESERVATION','Researcher-accepted restricted source paths: five named markets, two operators.','Only exploration_eligible rows were converted to numerical targets.','Provisional reserved months: November 2025–October 2026. Reserved rows: '+str(reserved_rows)+'.','Reserved values are absent from all price/change/correlation/calendar summaries and figures.','The reservation is provisional; Stage 6 must confirm the final evaluation design.','','ACTUAL COUNTS','All target calendar rows: '+str(len(raw))+'. Exploratory rows: '+str(len(exploration))+'.','Exploratory nonmissing month-end quotes: '+str(expl_eom)+'.','Exploratory nonmissing calendar-day averages: '+str(expl_avg)+'.','Full-coverage/month-end-only/missing counts and exact gap spans are in tables/.','','EXPLORATORY PRICE SUMMARIES']
for m in MARKETS:
 s=next(r for r in summaries if r['market']==m and r['target']=='month_end_price_inr_kg');p=next(r for r in persistence if r['market']==m and r['target']=='month_end_price_inr_kg');lines.append(f"{m}: n={s['n']}; month-end range {s['minimum']:.2f}–{s['maximum']:.2f} INR/kg; mean {s['mean']:.3f}; {p['flat_pairs']}/{p['valid_adjacent_month_pairs']} adjacent valid pairs unchanged ({p['flat_fraction']:.1%}).")
lines += ['','PERSISTENCE AND REVISION INTERPRETATION','Flat fractions use valid consecutive months only. Missing months are never bridged.','Contiguous source-boundary counts distinguish unchanged quotes from nonzero changes.','These are accepted-source observations, not proof that all real-world revisions were captured.','','CORRELATION AND CALENDAR INTERPRETATION','All coefficients use exactly matched exploratory months, with pair counts reported.','Level correlations can reflect common trends. Change correlations can reflect shared','operator tariff decisions and common shocks. Neither establishes a causal relationship','or additional forecasting value. No significance tests were performed.','Calendar displays mix different years/regimes and availability patterns. They do not','establish seasonality or justify a seasonal model. Five markets are not five independent','units: Delhi/Noida share IGL; Lucknow/Agra/Unnao share Green Gas.','','EXPLORATORY FLAGS',str(flags)+' month-end change records satisfy the optional nonzero-change Tukey flag.','Flags and largest changes remain in flagged_changes.csv. No rows were removed,','winsorized, interpolated or treated as errors merely because a change was large.','','ESTIMAND AND VALIDITY LIMITS','Calendar-day averages describe accepted day-end quotes. They are not identified','continuous-time TWAPs. Supplied timing bounds are conditional sensitivity envelopes,','not confidence or prediction intervals. Source chronology completeness and historical','predictor availability remain qualified. No H1/H2 finding, formal power calculation,','stationarity/break test, model fit or forecast was produced.','','INDEPENDENT VERIFICATION',str(len(checks))+' stdlib/Decimal/direct-arithmetic checks passed against pandas summaries.','Input/output checksums and the consequential experiment record are in metadata/.','Separate target reconstruction verification is performed by the independent target auditor.']
lines += ['','COMPARABILITY CAUTION','Market means and ranges cover unequal years and source availability. They cannot','be interpreted as regional price premia. Any comparative price-level statement would','require matched months, compatible geography/definitions and qualified operator scope.','Correlation figure labels are rounded; a displayed 1.00 does not imply identical','series. The CSV retains the computed coefficient and exact matched-month count.']
(B/'EDA_REPORT.txt').write_text('\n'.join(lines)+'\n')
provenance={'generated_at':datetime.now(timezone.utc).isoformat(),'target_path':str(TARGET),'target_sha256':sha(TARGET),'accepted_interval_path':str(INTERVAL),'accepted_interval_sha256':sha(INTERVAL),'specification_sha256':sha(B/'ANALYSIS_SPECIFICATION.txt'),'exploration_filter':'exploration_eligible == True before target numeric conversion','reserved_month_start':RESERVE_START,'reserved_month_end':RESERVE_END,'reserved_rows_coverage_only':reserved_rows,'exploratory_calendar_rows':len(exploration),'exploratory_month_end_values':expl_eom,'exploratory_average_values':expl_avg,'five_markets_two_operators':True,'independent_checks':len(checks),'no_stage5_or_models':True,'environment':{'python':sys.version,'pandas':pd.__version__,'numpy':np.__version__,'matplotlib':matplotlib.__version__,'platform':platform.platform()}}
(B/'metadata/eda_summary.json').write_text(json.dumps(provenance,indent=2))
experiment={'experiment_id':'S4-EDA-001','timestamp':provenance['generated_at'],'question':'Describe verified source-based target coverage, exploratory price properties and qualified co-movement','classification':'exploratory_descriptive','input_hashes':{str(TARGET.relative_to(D)):sha(TARGET),str(INTERVAL.relative_to(D)):sha(INTERVAL)},'models':'none','transformations':['metadata-only coverage state','adjacent-month differences without gap bridging','matched-month Pearson descriptive coefficients','calendar-group descriptive means','optional nonzero-change Tukey flags; no removal'],'training_validation_test_windows':'no model windows; exploration before 2025-11, provisional reservation 2025-11 to 2026-10','hyperparameters':'not_applicable','random_seed':'no_random_process','results':{'calendar_rows':len(raw),'exploration_rows':len(exploration),'month_end_values':expl_eom,'average_values':expl_avg,'independent_checks_passed':len(checks)},'uncertainty':'No inferential intervals or significance claims; dependent/shared-operator data','decision':'descriptive_results_retained_with_limits','deviations':'none','failures':'none','warnings':['source completeness qualified','unknown historical information availability','two shared operators','calendar patterns regime-confounded','reservation provisional until Stage6'],'software':provenance['environment']}
experiment['experiment_id']='S4-EDA-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
experiment['technical_recovery_notes']=['Anaconda pandas nanosecond datetime conversion crashed; all date handling now uses stdlib date without changing target values.','Decimal expected-value serialization repaired.','Independent visual review found shared x-axis calendar counts copied across market panels; market-specific x axes now show each actual sample count.']
experiment['supersedes_experiment_id']='S4-EDA-001'
with (B/'metadata/experiment_registry.jsonl').open('a') as registry:registry.write(json.dumps(experiment)+'\n')
outputs={str(p.relative_to(B)):sha(p) for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ['output_checksums.json','run.log']}
(B/'metadata/output_checksums.json').write_text(json.dumps(outputs,indent=2))
print(json.dumps(provenance,indent=2))
