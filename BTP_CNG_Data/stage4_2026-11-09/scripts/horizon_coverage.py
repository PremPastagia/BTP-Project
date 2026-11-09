"""Count calendar-aligned target pairs; this does not certify forecast availability."""
from pathlib import Path
import csv,json,datetime,hashlib,argparse

HERE=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=HERE);ap.add_argument('--output',type=Path,default=HERE)
    a=ap.parse_args();src=a.input/'analysis/coverage_calendar.csv';dest=a.output/'metadata/horizon_coverage.csv'
    if dest.exists():raise FileExistsError('Use a fresh output directory')
    dest.parent.mkdir(parents=True,exist_ok=True)
    rs=list(csv.DictReader(src.open()));cities=list(dict.fromkeys(r['city'] for r in rs))
    idx=lambda s:int(s[:4])*12+int(s[5:])
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();rid='S4R-HORIZON-COVERAGE-'+stamp
    registry=a.output/'metadata/experiment_registry.jsonl'
    with registry.open('a') as f:f.write(json.dumps(dict(experiment_id=rid,timestamp_utc=stamp,status='started',input_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),method='calendar-origin/target eligibility counts only',comparison_type='descriptive feasibility',training_validation_test='no evaluation',seed=None,hyperparameters=None))+'\n')
    out=[]
    for c in cities:
        cr=[r for r in rs if r['city']==c];by={idx(r['year_month']):r for r in cr}
        for target in ['cng_price_monthend','cng_price_twap']:
            for h in [1,3,6]:
                pairs=[(r,by[k+h]) for k,r in by.items() if k+h in by and r[target] and by[k+h][target]]
                out.append(dict(city=c,target=target,horizon_months=h,all_supported_target_pairs=len(pairs),development_pairs=sum(x['sample_period']==y['sample_period']=='development' for x,y in pairs),
                                target_in_reserved_period=sum(y['sample_period']=='provisionally_reserved' for x,y in pairs),
                                strict_real_time_origin_count='not_certified',interpretation='Outcome coverage only; counts are dependent/overlapping and do not certify contemporaneous prices, labels or covariates.'))
    with dest.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]),lineterminator='\n');w.writeheader();w.writerows(out)
    with registry.open('a') as f:f.write(json.dumps(dict(experiment_id=rid+'-RESULT',timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent=rid,status='completed',output_rows=len(out),output_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),decision='coverage_only_no_forecast_design'))+'\n')
    print('Wrote',len(out),'city-target-horizon coverage records')
if __name__=='__main__':main()
