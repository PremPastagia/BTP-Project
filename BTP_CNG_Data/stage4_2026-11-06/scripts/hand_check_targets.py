"""Hand-specified real-source examples; no producer aggregation helpers imported."""
from pathlib import Path
from decimal import Decimal
import csv,json,hashlib,datetime,openpyxl
R=Path(__file__).resolve().parents[3];B=R/'BTP_CNG_Data/stage4_2026-11-06';C=R/'BTP_CNG_Data/consolidated_2026-11-06'
source_hash='6518c228703442e3c206e5445d181add0906ec11373ecf625361d6b537bd3067'
objects=list(csv.DictReader((C/'metadata/raw_objects.csv').open()));record=next(r for r in objects if r['sha256']==source_hash);raw=C/record['path']
if hashlib.sha256(raw.read_bytes()).hexdigest()!=source_hash:raise ValueError('Source identity mismatch')
s=openpyxl.load_workbook(raw,data_only=True)['CNG Price']
for cell,value in [('C5','27.5'),('C8','29.3'),('C9','29.8'),('C12','33.75')]:
 if Decimal(str(s[cell].value))!=Decimal(value):raise ValueError('Source cell differs: '+cell)
for cell,value in [('B5','17.06.10'),('B8','02.04.11'),('B9','06.06.11'),('B12','01.01.12')]:
 if str(s[cell].value)!=value:raise ValueError('Source date differs: '+cell)
data={(r['market'],r['month']):r for r in csv.DictReader((B/'targets/monthly_targets.csv').open())}
checks=[]
cases=[('Delhi','2011-06','month_end_price_inr_kg',Decimal('29.8'),'CellC9 persists through month end'),('Delhi','2011-06','day_weighted_day_end_average_inr_kg',(Decimal(5)*Decimal('29.3')+Decimal(25)*Decimal('29.8'))/30,'Five days at29.3 plus25days at29.8; no intraday time invented'),('Delhi','2011-06','continuous_time_twap_lower_bound_inr_kg',(Decimal(6)*Decimal('29.3')+Decimal(24)*Decimal('29.8'))/30,'June6 change can occur within day; lower area uses old quote for change day'),('Delhi','2011-06','continuous_time_twap_upper_bound_inr_kg',(Decimal(5)*Decimal('29.3')+Decimal(25)*Decimal('29.8'))/30,'Upper area uses new quote for change day'),('Delhi','2012-02','days_in_month',Decimal(29),'Leap year:29calendar days'),('Delhi','2012-02','day_weighted_day_end_average_inr_kg',Decimal('33.75'),'29days unchanged source quoteC12'),('Delhi','2010-06','covered_days',Decimal(14),'June17throughJune30only'),('Delhi','2010-06','missing_days',Decimal(16),'June1throughJune16unobserved'),('Delhi','2010-06','month_end_price_inr_kg',Decimal('27.5'),'Month-end quote known although full average is not')]
for market,month,col,expected,reason in cases:
 actual=Decimal(data[(market,month)][col]);passed=abs(actual-expected)<=Decimal('0.00000000001')
 checks.append(dict(market=market,month=month,field=col,expected=str(expected),actual=str(actual),reason=reason,passed=passed))
 if not passed:raise ValueError(checks[-1])
if data[('Delhi','2010-06')]['day_weighted_day_end_average_inr_kg']!='':raise ValueError('Incomplete month received invented average')
checks.append(dict(market='Delhi',month='2010-06',field='day_weighted_day_end_average_inr_kg',expected='',reason='Incomplete coverage stays missing',passed=True))
out=dict(source_sha256=source_hash,source_cells_checked=['B5','C5','B8','C8','B9','C9','B12','C12'],implementation='hand-specified source examples separate from both aggregation algorithms',checks=checks,all_passed=all(r['passed'] for r in checks),reserved_outcomes_used=False)
(B/'logs/hand_checked_real_examples.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
