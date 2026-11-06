"""Independent source decoding checks; does not import the ledger builder."""
from pathlib import Path
import csv,json,hashlib,collections,math,datetime,zoneinfo,re,os
import openpyxl
OUT=Path(__file__).resolve().parents[1]
ROOT=Path(os.environ.get('BTP_PROJECT_ROOT',str(OUT.parents[1]))).resolve()
def read(p):
    with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
observations=read(OUT/'structured/native_numerical_observations.csv')
candidates=read(OUT/'structured/unverified_transcription_candidates.csv')
registry=read(OUT/'metadata/source_registry.csv')
checks=[];failures=[]
def check(name,passed,detail):
    checks.append({'check':name,'passed':bool(passed),'detail':detail})
    if not passed:failures.append(name)
hashes={}
for r in registry:
    p=ROOT/r['raw_file'];got=hashlib.sha256(p.read_bytes()).hexdigest();hashes[r['raw_sha256']]=p
    if got!=r['raw_sha256']:failures.append('source_hash:'+r['raw_sha256'])
check('all_raw_source_hashes',not failures,len(hashes))
check('observation_identifiers_unique',len({r['observation_id'] for r in observations})==len(observations),len(observations))
check('source_version_keys_unique',len({r['record_key'] for r in observations})==len(observations),len(observations))
check('finite_reported_values',all(math.isfinite(float(r['value'])) for r in observations),len(observations))
check('no_transcription_candidate_in_native_ledger',all(not r['family'].endswith('_candidate') for r in observations),len(candidates))
check('native_frequency_retained',all(r['frequency'] not in ['monthly_interpolated','monthly_filled'] for r in observations),'No numerical annual/quarterly series expanded into months')

imf=[r for r in observations if r['series']=='IMF_CPI_PCPI_IX'];raw=json.loads(hashes[imf[0]['raw_sha256']].read_text())['series']['docs'][0]
expected={p:float(v) for p,v in zip(raw['period'],raw['value']) if v not in ['NA','',None]}
check('IMF_CPI_independent_JSON_decode',len(imf)==len(expected) and all(float(r['value'])==expected[r['period']] for r in imf),{'rows':len(imf),'source_reference_period':raw.get('observations_attributes')})
gdp=[r for r in observations if r['series']=='WorldBank_GDP_constant_2015_USD'];raw=json.loads(hashes[gdp[0]['raw_sha256']].read_text());expected={str(r['date']):float(r['value']) for r in raw[1] if r['value'] is not None}
check('constant_GDP_independent_JSON_decode',len(gdp)==len(expected) and all(float(r['value'])==expected[r['period']] for r in gdp),len(gdp))

official=[r for r in observations if r['family']=='official_cpi_monthly'];allclaims=collections.defaultdict(list)
monthnames=['january','february','march','april','may','june','july','august','september','october','november','december']
for receipt in json.loads((OUT/'logs/mospi_cpi_acquisition_manifest.json').read_text()):
    if not receipt.get('records'):continue
    payload=json.loads((OUT/receipt['raw_file']).read_text())
    for r in payload['data']:
        if (r['state'],r['sector'],r['group'],r['subgroup'])!=('All India','Combined','General','General-Overall'):continue
        period=str(r['year'])+'-'+str(monthnames.index(r['month'].lower())+1).zfill(2)
        allclaims[(receipt['raw_sha256'],period,r['baseyear'])].append(float(r['index']))
unambiguous={k:v[0] for k,v in allclaims.items() if len(set(v))==1}
bad=[]
for r in official:
    k=(r['raw_sha256'],r['period'],r['series'].rsplit('_',1)[-1])
    if k not in unambiguous or float(r['value'])!=unambiguous[k]:bad.append(r['observation_id'])
check('MoSPI_dimensions_values_and_conflicts_independent',not bad and len(official)==len(unambiguous),{'retained':len(official),'ambiguous_periods':[k[1] for k,v in allclaims.items() if len(set(v))>1]})

energy=[r for r in observations if r['family']=='energy_benchmarks' and r['source_locator'].startswith('Monthly Prices!')]
workbooks={};mismatches=[]
for r in energy:
    h=r['raw_sha256']
    if h not in workbooks:workbooks[h]=openpyxl.load_workbook(hashes[h],read_only=False,data_only=True)
    m=re.fullmatch(r'Monthly Prices!R(\d+)C(\d+)',r['source_locator'])
    val=workbooks[h]['Monthly Prices'].cell(int(m[1]),int(m[2])).value
    if not math.isclose(float(val),float(r['value']),rel_tol=1e-10,abs_tol=1e-10):mismatches.append(r['observation_id'])
check('fresh_energy_every_original_Excel_cell',not mismatches,{'checked':len(energy),'mismatches':len(mismatches)})

fx=[r for r in observations if r['family']=='fx_monthly_proxy'];raw=json.loads(hashes[fx[0]['raw_sha256']].read_text())['chart']['result'][0]
tz=zoneinfo.ZoneInfo(raw['meta']['exchangeTimezoneName']);native={}
for t,v in zip(raw['timestamp'],raw['indicators']['quote'][0]['close']):
    period=datetime.datetime.fromtimestamp(t,tz).strftime('%Y-%m')
    if v is not None and period<'2026-11':native[period]=float(v)
check('Yahoo_month_native_exchange_timezone',len(fx)==len(native) and all(float(r['value'])==native[r['period']] for r in fx),{'rows':len(fx),'exchange_timezone':str(tz),'excluded_incomplete_November':True})

conflicts=read(OUT/'metadata/conflicts.csv')
check('conflicting_source_keys_excluded',not ({r['record_key'] for r in conflicts}&{r['record_key'] for r in observations}),{'excluded_rows':len(conflicts),'families':dict(collections.Counter(r['family'] for r in conflicts))})
check('unknown_publication_dates_not_backfilled',all(not r['publication_date'] for r in imf+gdp+fx+official),'These inputs do not carry independently verified historical publication dates')
result={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'all_checks_passed':not failures,'failures':failures,'stage3_complete':False,'stage4_started':False,'historical_point_in_time_validity_certified':False,'limitation':'Independent raw decoding verifies specified extraction calculations, not every source claim or full research readiness.'}
(OUT/'logs/independent_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
raise SystemExit(0 if not failures else 1)
