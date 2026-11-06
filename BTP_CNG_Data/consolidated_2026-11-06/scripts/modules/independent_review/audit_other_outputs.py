"""Independent checks of demand, numerical and article products. Producers unchanged."""
from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal
from datetime import datetime
import json,csv,hashlib,re,html
from bs4 import BeautifulSoup
from pypdf import PdfReader

B=Path(__file__).resolve().parent;ROOT=B.parents[1];C=ROOT/'Stage3_Consolidated_2026-11-06'
B.mkdir(exist_ok=True)
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def hashfile(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
    return h.hexdigest()
checks=[];issues=[]
def check(name,ok,evidence):
    checks.append(dict(check=name,passed=bool(ok),evidence=evidence))
    assert ok,(name,evidence)

# Demand: independent visual transcription uses full table cells and periods.
demand=read(C/'demand/structured/cng_reported_native.csv')
manifest=json.loads((C/'demand/metadata/source_manifest.json').read_text())
for r in manifest:check('demand_source_hash',hashfile(Path(r['path']))==r['sha256'],r['source_id'])
march=next(r for r in manifest if r['source_id']=='pngrb_2567b40dcffc')
raw_page=PdfReader(march['path']).pages[12].extract_text()
visual=[('cng_sales_volume','2025-03-01','2025-03-31','monthly_source_total','813'),('cng_sales_volume','2026-03-01','2026-03-31','monthly_source_total','946'),('cng_sales_volume','2024-04-01','2025-03-31','financial_year_to_date_source_total','9189'),('cng_sales_volume','2025-04-01','2026-03-31','financial_year_to_date_source_total','10721'),('cng_station_reported_indicator','2025-03-01','2025-03-31','monthly_source_total','347'),('cng_station_reported_indicator','2026-03-01','2026-03-31','monthly_source_total','224'),('cng_station_reported_indicator','2024-04-01','2025-03-31','financial_year_to_date_source_total','1206'),('cng_station_reported_indicator','2025-04-01','2026-03-31','financial_year_to_date_source_total','849')]
for series,start,end,freq,value in visual:
    hit=[r for r in demand if r['source_id']==march['source_id'] and r['series']==series and r['period_start']==start and r['period_end']==end and r['frequency']==freq]
    check('March2026_visual_value_period_scope',len(hit)==1 and Decimal(hit[0]['value'])==Decimal(value),[series,start,end,freq,value])
check('demand_no_duplicate_source_cells',len({(r['source_sha256'],r['source_page'],r['source_table'],r['source_row'],r['source_column']) for r in demand})==len(demand),len(demand))
check('demand_financial_year_not_monthly',all(r['period_start'][5:]=='04-01' for r in demand if r['frequency'].startswith('financial_year')),len(demand))
check('demand_station_scope_not_operating_stock',all('not_explicit' in r['definition_status'] for r in demand if r['series']=='cng_station_reported_indicator'),len(demand))

# Numerical: source/version uniqueness, independent hashes, no date or source fills.
native=read(C/'numerical/structured/native_numerical_observations.csv')
candidate=read(C/'numerical/structured/unverified_transcription_candidates.csv')
check('numerical_unique_record_keys',len({r['record_key'] for r in native})==len(native),len(native))
check('candidate_families_excluded_from_native',not any(r['family'].endswith('_candidate') for r in native),len(candidate))
hashes={r['raw_sha256']:r['raw_file'] for r in native+candidate}
for h,p in hashes.items():check('numerical_source_hash',hashfile(ROOT/p)==h,p)
check('numerical_all_rows_source_linked',all(r['raw_sha256'] and r['raw_file'] and r['input_origins'] for r in native+candidate),len(native)+len(candidate))
check('numerical_no_monthly_annual_expansion',all(r['frequency']=='annual' for r in native if r['family']=='macro_annual'),sum(r['family']=='macro_annual' for r in native))
check('numerical_unknown_release_flagged',all(r['availability_status']=='historical_release_unknown' for r in native if not r['publication_date']),len(native))
cpi=[r for r in native if r['family']=='official_cpi_monthly']
for r in cpi:
    payload=json.loads((ROOT/r['raw_file']).read_text());idx=int(re.search(r'data\[(\d+)\]',r['source_locator'])[1]);src=payload['data'][idx]
    check('official_CPI_value_raw_dimension_reconciliation',Decimal(r['value'])==Decimal(src['index']) and src['state']=='All India' and src['sector']=='Combined' and src['group']=='General' and src['subgroup']=='General-Overall' and str(src['baseyear']) in r['series'],[r['period'],r['value']])
imf=next(r for r in native if r['family']=='macro_monthly');imfdoc=json.loads((ROOT/imf['raw_file']).read_text())['series']['docs'][0]
check('IMF_CPI2012_reference_metadata', ['REFERENCE_PERIOD','2012A'] in imfdoc['observations_attributes'],imfdoc['observations_attributes'])

# News: check original bytes, parse timestamp claims independently and report
# normalization or multiple-claim ambiguity without fabricating publication times.
news=read(C/'text/structured/news_metadata.csv')
bad_dates=[];date_conflicts=[]
for r in news:
    check('article_source_hash',hashfile(Path(r['source_path']))==r['sha256'],r['article_id'])
    pub=r['publication_date']
    if pub:
        try:datetime.fromisoformat(pub.replace('Z','+00:00'))
        except ValueError:
            decoded=html.unescape(pub)
            try:datetime.fromisoformat(decoded.replace('Z','+00:00'));fix='HTML entity decoding yields ISO timestamp'
            except ValueError:fix='Manual date parsing/review required'
            bad_dates.append(dict(article_id=r['article_id'],source_url=r['source_url'],raw_publication_claim=pub,suggested_decoded_claim=decoded,issue=fix))
    claims=json.loads(r['publication_date_basis'])
    normalized={html.unescape(v).replace('Z','+00:00') for _,v in claims}
    if len(normalized)>1:date_conflicts.append(dict(article_id=r['article_id'],source_url=r['source_url'],claims=claims))
receipts=json.loads((C/'text/metadata/acquisition_receipts.json').read_text());versions=defaultdict(set)
for r in receipts:
    if r.get('status')=='retained_public_html':versions[r['url']].add(r['retrieved_sha256'])
actual_version_loss=[dict(url=u,hashes=sorted(h)) for u,h in versions.items() if len(h)>1]
if bad_dates:issues.append(dict(severity='must_fix_structured_timestamp',finding='Non-ISO publication timestamp claims need normalized fields and explicit precision/status; preserve raw claims.',details=bad_dates))
if date_conflicts:issues.append(dict(severity='review',finding='Multiple publisher date claims differ; do not silently select first as verified timing.',details=date_conflicts))
news_code=(C/'text/collect_news.py').read_text()
resolved=[]
if "key=(canonical(r['url']),r['retrieved_sha256'])" in news_code:
    resolved.append('Producer now keys article versions by canonical URL and content hash; corrected after audit warning. No current same-URL alternate-version loss.')
else:issues.append(dict(severity='latent_design_issue',finding='News canonical URL-only dedup would discard alternate raw versions at one URL.',actual_version_loss=actual_version_loss))
if all('publication_date_raw' in r and 'publication_date_precision' in r for r in news) and not bad_dates:
    resolved.append('Structured publication fields now normalize HTML entities and preserve raw claims/precision; previously escaped AutocarPro timezone offset is valid ISO.')
numerical_code=(C/'numerical/scripts/build_numerical.py').read_text()
if "format(float(r['value']),'.12g')" in numerical_code:
    issues.append(dict(severity='latent_design_issue',finding='Numerical duplicate equivalence uses format(float(value),.12g). Prefer exact Decimal equality or source-defined precision, since blanket12-significant-digit rounding can hide tiny same-key transcription differences. No material current value loss independently demonstrated.'))
input_hashes={str(p.relative_to(C)):hashfile(p) for p in [C/'demand/extract_bulletins.py',C/'demand/structured/cng_reported_native.csv',C/'text/collect_news.py',C/'text/structured/news_metadata.csv',C/'numerical/scripts/build_numerical.py',C/'numerical/structured/native_numerical_observations.csv']}
report=dict(audit_checks=len(checks),all_executed_checks_passed=all(r['passed'] for r in checks),audited_file_hashes=input_hashes,demand_rows=len(demand),demand_source_files=len(manifest),march_visual_independent_cells=len(visual),numerical_native_rows=len(native),numerical_candidate_rows=len(candidate),numerical_raw_hashes_checked=len(hashes),official_CPI_raw_rows_checked=len(cpi),article_rows=len(news),bad_article_date_claims=bad_dates,multiple_article_date_claims=date_conflicts,actual_news_version_loss=actual_version_loss,resolved_findings=resolved,issues=issues,scientific_stage3_acceptance=False,stage4_permission=False,limits=['Numerical source hashes/transcription checks do not verify source economic truth or historical publication vintages.','National CNG sales do not establish company/city-specific demand.','FY-to-date and monthly totals must not be summed together.','Station indicator is not independently established operating stock.','All later research approvals remain with researcher.'])
(B/'independent_audit.json').write_text(json.dumps(report,indent=2))
(B/'independent_check_log.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(report,indent=2))
