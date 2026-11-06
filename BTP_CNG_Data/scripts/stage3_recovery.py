#!/usr/bin/env python3
"""Non-destructive, restartable Stage 3 recovery. No preprocessing or modeling.

Commands: audit, collect, extract, catalogue, verify, all.
Original inputs are frozen from BASE; downloaded bytes are content-addressed;
each completed attempt is journaled before the next result is handled.
"""
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse, unquote
from functools import lru_cache
import argparse, hashlib, io, json, os, re, shutil, subprocess, tempfile, zipfile
import pandas as pd
import requests
from bs4 import BeautifulSoup

B=Path(__file__).resolve().parents[1]
BASE='fd4e65ba762cb0acdc273ac9ad9e9f809e52e5b4'
Q=B/'quarantine/legacy_main'
J=B/'logs/acquisition_journal.jsonl'
TODAY=datetime.now(timezone.utc).date().isoformat()
MONTH=TODAY[:7]
GROUPS={
'2.1':('retail CNG price;effective price revisions;gas procurement cost;distribution cost;compression cost;transmission tariff;operator margins;CNG taxes','PNGRB;operator dated notices','GA/district/operator'),
'2.2':('APM notified domestic gas price;other domestic non-APM prices;LNG imports volume;LNG import prices;domestic allocation shares;sourcing mix shares;blended procurement costs;domestic gas production;supply disruptions','PPAC;MoPNG;operator reports','national/company'),
'2.3':('CNG vehicle registrations;active CNG vehicle stock;CNG consumption and sales;CNG station counts;petrol retail prices;diesel retail prices;seasonal transport demand','VAHAN;PNGRB CGD MIS;PPAC;operators','RTO/state/GA/company'),
'2.4':('APM pricing rules;gas allocation policy;state VAT;central duties;pipeline tariff policy;CGD regulation and licensing;environmental regulations;transport regulations','MoPNG;PIB;PNGRB;gazettes;CAQM','national/state/GA'),
'2.5':('CGD operator identity;city and state taxes;regional sourcing mix;pipeline connectivity;station and distribution infrastructure;regional distribution costs;regional demand','PNGRB;operators;gazettes','GA/district/operator'),
'2.6':('international LNG benchmarks;global crude prices;Indian crude basket;USD INR exchange rate;geopolitical events;geopolitical risk index;global gas demand;international supply interruptions;extreme weather;CPI;GDP;PFCE;state economic data','World Bank;PPAC;RBI;GPR authors;IEA;IMD;MoSPI','global/national/state/station'),
'2.7':('news sentiment source text;news event categories;news uncertainty source text;article volume metadata;POS collocation source text;forward-looking news statements;news source credibility','independent publishers;GDELT','article/event/company/city relevance'),
'2.8':('corporate procurement disclosures;corporate financial metrics;corporate operating metrics;management tone source text;management guidance;corporate risk disclosures;report novelty source documents','operator reports;NSE/BSE;presentations;transcripts','company/report'),
'2.9':('management bias source evidence;editorial bias source evidence;duplicates;news report information overlap;publication timing;sentiment error annotation evidence;cross-source disagreements','matched independent/corporate/official documents','document/event/source')}

def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic_csv(df,p):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+'.tmp');df.to_csv(tmp,index=False);os.replace(tmp,p)
def save(df,relative):
    p=B/relative;p.parent.mkdir(parents=True,exist_ok=True)
    atomic_csv(df,p.with_suffix('.csv'))
    tmp=p.with_suffix('.parquet.tmp');df.to_parquet(tmp,index=False);os.replace(tmp,p.with_suffix('.parquet'))
def read(relative):
    try:return pd.read_csv(B/relative)
    except (FileNotFoundError,pd.errors.EmptyDataError):return pd.DataFrame()
def journal():
    if not J.exists():return []
    rows=[]
    for line in J.read_text().splitlines():
        try:rows.append(json.loads(line))
        except json.JSONDecodeError:pass
    return rows

def audit():
    Q.mkdir(parents=True,exist_ok=True);manifest=[];profiles=[]
    files=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=B.parent,text=True).splitlines()
    for f in files:
        if not f.startswith('BTP_CNG_Data/'):continue
        rel=Path(f).relative_to('BTP_CNG_Data');p=Q/rel
        if not p.exists():
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(subprocess.check_output(['git','show',BASE+':'+f],cwd=B.parent))
        manifest.append(dict(path=str(rel),preserved_path=str(p.relative_to(B)),bytes=p.stat().st_size,sha256=sha(p),base_commit=BASE))
        if p.suffix in ['.csv','.parquet']:
            try:
                d=pd.read_csv(p) if p.suffix=='.csv' else pd.read_parquet(p)
                profiles.append(dict(path=str(rel),rows=len(d),columns=len(d.columns),schema=json.dumps({c:str(t) for c,t in d.dtypes.items()}),nulls=json.dumps(d.isna().sum().to_dict()),duplicate_rows=int(d.duplicated().sum()),status='parsed'))
            except Exception as e:profiles.append(dict(path=str(rel),status='parse_failure',error=str(e)))
    atomic_csv(pd.DataFrame(manifest),B/'metadata/legacy_file_manifest.csv')
    atomic_csv(pd.DataFrame(profiles),B/'metadata/legacy_table_audit.csv')
    d=pd.read_csv(Q/'structured/price_revisions/discrete_revisions.csv').sort_values(['city','observation_date']).reset_index(drop=True)
    d['legacy_effective_date_claim']=d.pop('effective_date');d['legacy_publication_date_claim']=d.pop('publication_release_date')
    d['effective_date']=None;d['publication_timestamp']=None;d['publication_status']='unknown';d['value_class']='unverified';d['verification_status']='secondary_observation_not_primary_verified'
    prev=d.groupby('city').cng_price.shift();d['previous_observed_price']=prev;d['observation_type']='same_price_observation';d.loc[d.cng_price.ne(prev),'observation_type']='candidate_price_change';d.loc[prev.isna(),'observation_type']='initial_observation'
    ids={'Delhi':2,'Mumbai':3,'Pune':7,'Ahmedabad':10,'Lucknow':25,'Kanpur':292,'Hyderabad':8,'Bengaluru':6,'Noida':38,'Gurgaon':40}
    d['source_id']='LEGACY-MPP';d['source_url']=d.city.map(lambda c:f'https://www.mypetrolprice.com/FuelHistoryDataServing.aspx?LocationId={ids[c]}&Span=1000&selectedFuels=3H&HikeChartId=FuelHikeChartDetails')
    d['raw_file']=d.city.str.lower().map(lambda c:f'raw/cng_prices/{c}_raw_response.html');d['raw_sha256']=d.raw_file.map(lambda p:sha(B/p));d['observation_id']=['MPP-'+str(i+1).zfill(6) for i in range(len(d))]
    save(d,'structured/price_revisions/source_observations');save(d[d.observation_type.eq('candidate_price_change')],'structured/price_revisions/discrete_revisions')
    m=pd.read_csv(Q/'structured/price_revisions/cng_monthly_panel.csv');m['verification_status']='unknown_effective_price_path'
    save(m[m.year_month<MONTH],'quarantine/constructed_monthly_targets');save(m[m.year_month>=MONTH],'quarantine/incomplete_monthly_targets')
    save(pd.DataFrame(columns=['city','year_month','cng_price_monthend','cng_price_twap','verified_days','path_status','source_ids']),'structured/price_revisions/cng_monthly_panel')
    dem=pd.read_csv(Q/'structured/numerical_factors/demand_factors_monthly.csv');safe=dem[['city','year_month']].copy()
    for c in ['vahan_cng_registrations','apm_notified_price','state_vat_pct','petrol_price','diesel_price']:safe[c]=None
    safe['status']='missing_pending_observed_source';safe['publication_timestamp']=None;save(safe,'structured/numerical_factors/demand_factors_monthly')
    save(pd.DataFrame(columns=['date','variable','value','source_id','publication_timestamp']),'structured/numerical_factors/external_shocks_daily')
    save(pd.DataFrame([dict(status='quarantined_legacy_vintage_unsafe_join',legacy_path='quarantine/legacy_main/structured/numerical_factors/external_shocks_monthly.csv')]),'structured/numerical_factors/external_shocks_monthly')
    n=pd.read_csv(Q/'structured/news/news_archive_metadata.csv');n['legacy_publication_date_claim']=n.pop('publication_release_date');n['publication_timestamp']=None;n['record_type']='archive_locator_not_article';save(n,'structured/news/archive_locators')
    if not (B/'structured/news/real_article_metadata.csv').exists():save(pd.DataFrame(columns=['article_id','source_url','publisher','title','publication_timestamp','publication_status']),'structured/news/real_article_metadata')
    save(pd.DataFrame(columns=['article_id','source_url','publication_timestamp','publication_status']),'structured/news/news_archive_metadata')
    reg=pd.read_csv(Q/'structured/policy_events/regulatory_timeline.csv');reg['legacy_publication_date_claim']=reg.pop('publication_release_date');reg['publication_timestamp']=None;reg['verification_status']='hardcoded_event_requires_primary_record';save(reg,'structured/policy_events/regulatory_timeline')
    cov=[]
    for city,g in d.groupby('city'):
        cov.append(dict(city=city,state=g.state.iloc[0],operator_candidate=g.cgd_operator.iloc[0],operator_mapping_status='GA_boundaries_unverified',first_secondary_observation=g.observation_date.min(),last_secondary_observation=g.observation_date.max(),source_observations=len(g),same_price_observations=int(g.observation_type.eq('same_price_observation').sum()),candidate_changes=int(g.observation_type.eq('candidate_price_change').sum()),constructed_months=int(m.city.eq(city).sum()),verified_continuous_months=0,missing_periods='all effective-price intervals pending primary verification',selection='candidate_only'))
    atomic_csv(pd.DataFrame(cov),B/'metadata/city_coverage_matrix.csv')
    qr=[]
    for c in dem.columns:
        if c in ['city','year_month','state','cgd_operator']:continue
        qr.append(dict(variable=c,nonnull_records=int(dem[c].notna().sum()),status='quarantined',reason='synthetic_exponential' if c.startswith('vahan') else 'hardcoded_without_notification' if c.startswith('apm') or c=='state_vat_pct' else 'unverified_path_backward_fill_or_assumed_timing'))
    atomic_csv(pd.DataFrame(qr),B/'metadata/quarantine_register.csv')
    for p in (B/'scripts').glob('0[1-4]_*.py'):
        original=(Q/'scripts'/p.name).read_text();p.write_text(original.replace('if __name__ == "__main__":\n    main()','if __name__ == "__main__":\n    raise SystemExit("Quarantined legacy pipeline. Use scripts/stage3_recovery.py; original preserved in quarantine/legacy_main/scripts/.")'))
    (B/'scripts/05_validate_integrity.py').write_text('from stage3_recovery import verify\nif __name__ == "__main__": verify()\n')
    result=dict(as_of_date=TODAY,base_commit=BASE,preserved_files=len(manifest),source_observations=len(d),observation_types=d.observation_type.value_counts().to_dict(),incomplete_target_rows=int((m.year_month>=MONTH).sum()),finalized_targets=0,stage3_complete=False)
    (B/'logs/stage3_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

def fetch(job):
    u,group,context=job;sid='SRC-'+hashlib.sha256(u.encode()).hexdigest()[:16]
    out=dict(source_id=sid,source_url=u,group=group,context=context,extraction_timestamp=now(),publication_timestamp=None,publication_status='unknown',license_status='public_access_reuse_terms_unverified')
    try:
        r=requests.get(u,timeout=(10,35),headers={'User-Agent':'BTP-Stage3-Academic-Collection/1.0'})
        out.update(http_status=r.status_code,final_url=r.url,content_type=r.headers.get('Content-Type'),http_last_modified=r.headers.get('Last-Modified'))
        if r.status_code!=200:raise ValueError('HTTP '+str(r.status_code))
        data=r.content;kind='html';ext='.html'
        if data.startswith(b'%PDF'):kind='pdf';ext='.pdf'
        elif data.startswith(b'PK\x03\x04'):
            names=zipfile.ZipFile(io.BytesIO(data)).namelist();kind,ext=('presentation','.pptx') if any(x.startswith('ppt/') for x in names) else ('spreadsheet','.xlsx')
        elif data.startswith(bytes.fromhex('D0CF11E0')):kind='spreadsheet';ext='.xls'
        elif 'json' in r.headers.get('Content-Type',''):kind='json';ext='.json'
        digest=hashlib.sha256(data).hexdigest();p=B/'raw'/group/(sid+'_'+digest[:12]+ext);p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():
            temp=p.with_name(p.name+'.part');temp.write_bytes(data);os.replace(temp,p)
        out.update(raw_file=str(p.relative_to(B)),sha256=digest,bytes=len(data),kind=kind,status='downloaded')
        if re.search(r'\.pdf(?:$|[?&])',u,re.I) and kind!='pdf':out.update(status='unexpected_content',error='Expected PDF; received '+kind)
        if kind=='pdf':
            t=B/'documents/source_text'/(sid+'.txt');t.parent.mkdir(parents=True,exist_ok=True)
            try:
                subprocess.run(['pdftotext','-layout','-enc','UTF-8',str(p),str(t)],check=True,timeout=60,capture_output=True)
                text=t.read_text();out.update(text_file=str(t.relative_to(B)),text_chars=len(text.strip()),pages=max(1,text.count('\f')),parse_status='text_extracted' if text.strip() else 'OCR_required')
            except Exception as e:out.update(parse_status='failed',parse_error=str(e))
    except Exception as e:out.update(status='failed',error=str(e))
    return out

def batch(jobs,retry=False,workers=8):
    old=journal();seen={r['source_url'] for r in old if not retry or r['status']=='downloaded'}
    todo=list({j[0]:j for j in jobs if j[0] not in seen}.values())
    J.parent.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for future in as_completed([pool.submit(fetch,j) for j in todo]):
            r=future.result()
            with J.open('a') as f:f.write(json.dumps(r)+'\n');f.flush();os.fsync(f.fileno())
            print(r['status'],r['source_url'],flush=True)
    return journal()

ROOTS=[
('https://pngrb.gov.in/eng-web/png-cng-prices.html','cng_prices','all embedded monthly price tables'),
('https://pngrb.gov.in/eng-web/data-bank.html','demand','all historical CGD and gas-pipeline documents'),
('https://ppac.gov.in/natural-gas/gas-price','gas_supply','notified price archive and pagination'),
('https://ppac.gov.in/archives/reports','gas_supply','historical Natural Gas Reports and Ready Reckoners'),
('https://ppac.gov.in/archives/circular-notice','regulations','historical notices'),
('https://ppac.gov.in/archives/impnews','regulations','historical official news'),
('https://www.iglonline.net/annual-reports','corporate_disclosures','annual report archive'),
('https://www.iglonline.net/financial','corporate_disclosures','financial statement archive'),
('https://www.iglonline.net/latest-presentation','corporate_disclosures','presentations'),
('https://mngl.in/investors/annual-reports','corporate_disclosures','MNGL annual archive'),
('https://www.adanigas.com/investors','corporate_disclosures','ATGL reports and presentations'),
('https://www.gujaratgas.com/investors/annual-reports/','corporate_disclosures','verify redirect and entity changes'),
('https://www.bglgas.com/price-tag/','cng_prices','dated operator price table'),
('https://www.cugl.co.in/','cng_prices','operator price page discovery'),
('https://www.iglonline.net/cng-png-prices','cng_prices','operator prices'),
('https://gglonline.net/storage/pdf-uploads/06052026.pdf','cng_prices','GGL component document'),
('https://www.mahanagargas.com/cng/customer-zone/cng-rate-card','cng_prices','MGL rate card access test'),
('https://www.adanigas.com/cng','cng_prices','ATGL retail price page'),
('https://library.iitkgp.ac.in/pages/eSearch3.0/index.html','discovery','institutional listings do not establish entitlement'),
('https://www.onos.gov.in/publishers','discovery','publisher availability not dataset licensing'),
('https://analytics.parivahan.gov.in/analytics/publicdashboard/vahan?lang=en','demand','new VAHAN dashboard'),
('https://data.rbi.org.in/DBIE/','macro_weather','official exchange-rate export access'),
('https://esankhyiki.mospi.gov.in/','macro_weather','native CPI GDP PFCE data and releases'),
('https://mausam.imd.gov.in/responsive/climate_services.php','macro_weather','weather archive access'),
('https://gdeltproject.org/data.html','news','historical article metadata access'),
('https://www.iea.org/reports/gas-market-report-q3-2026','energy_markets','global gas demand and supply'),
('https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls','macro_weather','full native GPR history'),
('https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Monthly.xlsx','energy_markets','full historical monthly commodity workbook'),
('https://www.pib.gov.in/PressReleasePage.aspx?PRID=1914450','regulations','posted gas reform announcement'),
('https://pngrb.gov.in/pdf/orders/20260213_TariffOrder_UFT.pdf','regulations','unified gas transmission tariff order'),
('https://www.bseindia.com/xml-data/corpfiling/AttachHis/9b343ed5-c3c1-45f0-bb06-9e5eee964d64.pdf','corporate_disclosures','IGL allocation disclosure'),
('https://www.adanigas.com/-/media/Project/AdaniGas/Investors/Financials/Annual-Report/ATGL-IR-2025_For-Website.pdf','corporate_disclosures','ATGL FY25'),
('https://www.adanigas.com/-/media/Project/AdaniGas/Investors/Financials/Annual-Report/FY26.pdf','corporate_disclosures','ATGL FY26'),
('https://mngl.in/storage/109733/MNGL_AR2025_12.09.2025.pdf','corporate_disclosures','MNGL FY25'),
('https://mngl.in/storage/191333/MNGL-AR-2025-26_upload-file_2.pdf','corporate_disclosures','MNGL FY26')]

def collect(retry=False):
    batch(ROOTS,retry)
    # Follow all public gas-price pages discovered in navigation.
    pages=set()
    for r in journal():
        if r['status']!='downloaded' or r.get('kind')!='html':continue
        if 'ppac.gov.in/natural-gas/gas-price' in r['source_url']:
            html=(B/r['raw_file']).read_text(errors='replace')
            nums=[int(n) for n in re.findall(r'gas-price\?page=(\d+)',html)]
            if nums:pages.update('https://ppac.gov.in/natural-gas/gas-price?page='+str(i) for i in range(1,max(nums)+1))
    batch([(u,'gas_supply','official price listing page') for u in sorted(pages)],retry)
    links={};navigation=[]
    for r in journal():
        if r['status']!='downloaded' or r.get('kind')!='html':continue
        u=r['source_url'];soup=BeautifulSoup((B/r['raw_file']).read_bytes(),'lxml')
        if not any(h in u for h in ['ppac.gov.in','pngrb.gov.in','iglonline.net','mngl.in','adanigas.com','cugl.co.in']):continue
        for a in soup.find_all(['a','iframe','embed'],href=True)+soup.find_all(['iframe','embed'],src=True):
            link=urljoin(u,a.get('href') or a.get('src'));title=a.get_text(' ',strip=True)
            isfile=bool(re.search(r'\.(pdf|xlsx?|pptx)(?:$|[?&])',link,re.I))
            keep=(isfile and ('pngrb.gov.in/data-bank/' in link and re.search(r'CGD|NGPL|CNG|NG.Sales|\.xlsx?$',link,re.I) or
                  'ppac.gov.in/download.php?file=' in link and re.search(r'gasprice/|natural.gas|Monthly.Gas|Ready.Reckoner|Snapshot|crude|allocation|gas.price',link+' '+title,re.I) or
                  any(h in link for h in ['iglonline.net','mngl.in','adanigas.com']) and re.search(r'annual|report|presentation|financial|quarter|transcript|earnings',link+' '+title,re.I)))
            if keep:
                parent=a
                for _ in range(3):
                    if parent.parent:parent=parent.parent
                context=parent.get_text(' ',strip=True)[:3000]
                group='gas_supply' if 'ppac.gov.in' in link else 'demand' if 'pngrb.gov.in' in link else 'corporate_disclosures'
                links[link]=dict(source_url=link,listing_url=u,listing_raw_file=r['raw_file'],title=title,listing_context=context,publication_timestamp=None,publication_status='requires_listing_date_review',group=group)
            if 'cugl.co.in' in u and re.search(r'CNG.*price',title,re.I):navigation.append((link,'cng_prices','CUGL price navigation'))
    # Preserve unmatched links even if they have not been downloaded.
    atomic_csv(pd.DataFrame(list(links.values())),B/'metadata/discovered_document_links.csv')
    jobs=[(u,x['group'],x['title']) for u,x in links.items()]
    jobs.sort(key=lambda j:(0 if 'gasprice/' in j[0] else 1 if 'CGD' in j[0] else 2 if re.search(r'gas|reckoner',j[0],re.I) else 3,j[0]))
    batch(navigation+jobs,retry)
    materialize_manifest()

def materialize_manifest():
    rows=journal();df=pd.DataFrame(rows)
    if len(df):atomic_csv(df,B/'metadata/acquisition_manifest.csv')
    return df

def extract():
    m=materialize_manifest();records=[];tables=[]
    source=m[m.source_url.eq(ROOTS[0][0]) & m.status.eq('downloaded')]
    if len(source):
        r=source.iloc[-1];s=BeautifulSoup((B/r.raw_file).read_bytes(),'lxml')
        for table in s.find_all('table'):
            ident=table.get('id','');label=table.get('data-csv-name','')
            if not ident.lower().startswith('cngprice'):continue
            match=re.search(r'([A-Za-z]+)_(\d{4})$',label);period=pd.to_datetime(match.group(1)+' '+match.group(2),format='%B %Y').strftime('%Y-%m') if match else None
            trs=table.find_all('tr');heads=[re.sub(r'\s+',' ',c.get_text(' ',strip=True)).strip() for c in trs[0].find_all(['td','th'])];count=0
            for ri,tr in enumerate(trs[1:],1):
                vals=[re.sub(r'\s+',' ',c.get_text(' ',strip=True)).strip() for c in tr.find_all(['td','th'])]
                if len(vals)!=len(heads):continue
                d=dict(zip(heads,vals));d.update(record_id=f'PNGRB-{ident}-{ri}',report_period=period,source_table=ident,raw_file=r.raw_file,raw_sha256=r.sha256,source_id=r.source_id,source_url=r.source_url,frequency='monthly_snapshot',geographical_grain='GA_district_operator',unit='INR/kg',value_class='observed',verification_status='official_entity_submission_not_independently_verified',publication_timestamp=None,publication_status='unknown',extraction_timestamp=r.extraction_timestamp);records.append(d);count+=1
            tables.append(dict(table=ident,report_period=period,records=count))
    prices=pd.DataFrame(records)
    mapping={'Retail Selling Price (Rs./KG)':'retail_price','Cost of Natural Gas to CGD Entity':'gas_cost','Supply & Distribution Cost of CGD Entity':'supply_distribution_cost',"Entity's Margin":'margin','Transmission Tariff':'transmission_tariff','Basic Selling Price':'basic_price','Excise Duty':'excise_duty','Value Added Tax (If applicable)':'vat_amount','Any Other Tax':'other_tax'}
    if len(prices):
        for orig,new in mapping.items():
            prices[new]=float('nan')
            for c in [c for c in prices.columns if c.lower()==orig.lower()]:prices[new]=prices[new].combine_first(pd.to_numeric(prices[c].str.replace(',','',regex=False),errors='coerce'))
        dates=[c for c in prices if 'last price revision' in c.lower()];prices['effective_date_claim']=pd.to_datetime(prices[dates[0]],dayfirst=True,errors='coerce').dt.strftime('%Y-%m-%d') if dates else None
        prices['rsp_arithmetic_residual']=prices.retail_price-prices[['basic_price','excise_duty','vat_amount','other_tax']].sum(axis=1,min_count=4)
        prices['basic_arithmetic_residual']=prices.basic_price-prices[['gas_cost','supply_distribution_cost','margin','transmission_tariff']].sum(axis=1,min_count=4)
        prices['arithmetic_status']='pass_tolerance_0.05';prices.loc[(prices.rsp_arithmetic_residual.abs()>.05)|(prices.basic_arithmetic_residual.abs()>.05),'arithmetic_status']='conflict';prices.loc[prices.rsp_arithmetic_residual.isna()|prices.basic_arithmetic_residual.isna(),'arithmetic_status']='missing_components'
        save(prices,'structured/price_revisions/pngrb_cng_components_native');atomic_csv(pd.DataFrame(tables),B/'metadata/pngrb_price_table_coverage.csv');atomic_csv(prices[prices.arithmetic_status.ne('pass_tolerance_0.05')],B/'metadata/pngrb_component_conflicts.csv')
    native=[]
    def add(variable,period,value,frequency,unit,raw,sid,geo='India',kind='observed'):
        if pd.notna(value):native.append(dict(variable=variable,period=str(period),value=value,frequency=frequency,unit=unit,geography=geo,source_id=sid,raw_file=raw,value_class=kind,publication_timestamp=None,publication_status='unknown_release_and_vintage',extraction_timestamp=now()))
    graw='raw/macro_weather/gdp_india_wb.json';gdp=json.loads((B/graw).read_text())
    for x in gdp[1]:
        if x['value'] is not None:add('GDP_'+x['indicator']['id'],x['date'],x['value'],'annual','constant_2015_USD',graw,'LEGACY-WB-GDP')
    craw='raw/macro_weather/cpi_imf_raw.json';cpi=json.loads((B/craw).read_text())['series']['docs'][0]
    for period,value in zip(cpi['period'],cpi['value']):add('IMF_CPI_all_items_base_unconfirmed',period,pd.to_numeric(value,errors='coerce'),'monthly','index_base_requires_source_metadata',craw,'LEGACY-IMF-DBNOMICS')
    fxraw='raw/macro_weather/usdinr_monthly_raw.json';fx=json.loads((B/fxraw).read_text())['chart']['result'][0]
    for ts,value in zip(fx['timestamp'],fx['indicators']['quote'][0]['close']):
        if value is not None:add('USDINR_Yahoo_bar_close',datetime.fromtimestamp(ts,timezone.utc).isoformat(),value,'monthly_bar','INR/USD',fxraw,'LEGACY-YAHOO-FX',kind='proxy')
    for name,default in [('data_gpr_export.xls','raw/macro_weather/data_gpr_export.xls'),('CMO-Historical-Data-Monthly.xlsx','raw/energy_markets/CMO-Historical-Data-Monthly.xlsx')]:
        found=m[m.source_url.str.contains(name,regex=False) & m.status.eq('downloaded')];raw=found.iloc[-1].raw_file if len(found) else default;sid=found.iloc[-1].source_id if len(found) else 'LEGACY-SPREADSHEET'
        if name.endswith('.xls'):
            df=pd.read_excel(B/raw)
            for _,row in df.iterrows():
                period=pd.to_datetime(row.get('month'),errors='coerce')
                if pd.isna(period):continue
                for c in ['GPR','GPRT','GPRA']:
                    if c in row:add(c,period.strftime('%Y-%m'),row[c],'monthly','index',raw,sid,'global')
        else:
            df=pd.read_excel(B/raw,sheet_name='Monthly Prices',header=None);headers=df.iloc[4];units=df.iloc[5]
            for _,row in df.iloc[6:].iterrows():
                if not re.fullmatch(r'\d{4}M\d{2}',str(row.iloc[0])):continue
                for i in range(1,11):add(str(headers.iloc[i]),str(row.iloc[0]).replace('M','-'),pd.to_numeric(row.iloc[i],errors='coerce'),'monthly',str(units.iloc[i]),raw,sid,'global_benchmark')
    save(pd.DataFrame(native),'structured/numerical_factors/native_observations')
    save(pd.DataFrame([r for r in native if r['frequency']=='annual']),'structured/numerical_factors/gdp_annual_native')
    docs=[];lines=[];cells=[]
    if len(m):
        for _,r in m[m.status.eq('downloaded')].drop_duplicates(['source_id','sha256'],keep='last').iterrows():
            if r.kind=='pdf':
                text=(B/r.text_file).read_text() if isinstance(r.get('text_file'),str) and (B/r.text_file).exists() else ''
                docs.append(dict(document_id=r.source_id,source_url=r.source_url,raw_file=r.raw_file,sha256=r.sha256,text_file=r.get('text_file'),group=r.group,context=r.context,pages=r.get('pages'),text_chars=len(text.strip()),publication_timestamp=None,publication_status='unknown_report_year_is_not_release_time',verification_status='primary_host_document_content_review_pending',extraction_timestamp=r.extraction_timestamp))
                for no,line in enumerate(text.splitlines(),1):
                    if re.search(r'CNG|procurement|allocation|MMBTU|MMSCM|station|LNG|production|consumption|import',line,re.I):lines.append(dict(source_id=r.source_id,raw_file=r.raw_file,text_file=r.get('text_file'),line_number=no,source_excerpt=line,record_type='evidence_line_requires_original_table_context'))
            if r.kind=='spreadsheet':
                try:
                    xl=pd.ExcelFile(B/r.raw_file)
                    for sheet in xl.sheet_names:
                        df=pd.read_excel(xl,sheet_name=sheet,header=None)
                        for ri,row in df.iterrows():
                            for ci,value in row.items():
                                if pd.notna(value):cells.append(dict(source_id=r.source_id,raw_file=r.raw_file,sheet=sheet,row_number=ri+1,column_number=ci+1,value=str(value),value_class='observed',publication_timestamp=None))
                except Exception as e:print('spreadsheet_parse_failed',r.raw_file,str(e),flush=True)
    save(pd.DataFrame(docs,columns=['document_id','source_url','raw_file','sha256','text_file','group','context','pages','text_chars','publication_timestamp','publication_status','verification_status','extraction_timestamp']),'structured/documents/source_document_index')
    save(pd.DataFrame(lines),'structured/documents/source_evidence_lines');save(pd.DataFrame(cells),'structured/documents/native_spreadsheet_cells')
    save(pd.DataFrame([r for r in docs if r['group']=='corporate_disclosures'],columns=['document_id','source_url','raw_file','sha256','text_file','group','context','pages','text_chars','publication_timestamp','publication_status','verification_status','extraction_timestamp']),'structured/corporate_disclosures/corporate_disclosures_metadata')
    print(json.dumps(dict(price_snapshots=len(prices),native_records=len(native),documents=len(docs),source_cells=len(cells),stage3_complete=False)),flush=True)

def catalogue():
    m=materialize_manifest();prices=read('structured/price_revisions/pngrb_cng_components_native.csv');native=read('structured/numerical_factors/native_observations.csv');docs=read('structured/documents/source_document_index.csv');corp=read('structured/corporate_disclosures/corporate_disclosures_metadata.csv');inv=[]
    for group,(factors,sources,grain) in GROUPS.items():
        for i,factor in enumerate(factors.split(';'),1):
            n=0;first=None;last=None;status='source_discovery_partial';evidence='metadata/acquisition_manifest.csv';action='Retrieve historical records and review definitions, units and release evidence.'
            if factor in ['retail CNG price','gas procurement cost','distribution cost','transmission tariff','operator margins','CNG taxes','CGD operator identity','city and state taxes','regional distribution costs'] and len(prices):
                n=len(prices);first=prices.report_period.min();last=prices.report_period.max();status='official_entity_submitted_snapshots_collected_requires_crosscheck';evidence='structured/price_revisions/pngrb_cng_components_native.csv';action='Resolve arithmetic conflicts and missing components; retrieve dated operator notices and publication evidence.'
            elif factor=='effective price revisions':status='secondary_candidates_only';evidence='structured/price_revisions/source_observations.csv';action='Verify each candidate date and price against original dated notices. Do not infer interval continuity.'
            elif factor in ['global crude prices','international LNG benchmarks','geopolitical risk index','USD INR exchange rate','CPI','GDP'] and len(native):
                pat={'global crude prices':'Crude oil','international LNG benchmarks':'Liquefied natural gas','geopolitical risk index':'^GPR','USD INR exchange rate':'USDINR','CPI':'CPI','GDP':'^GDP'}[factor];d=native[native.variable.str.contains(pat,case=False,regex=True)];n=len(d);first=d.period.min() if n else None;last=d.period.max() if n else None;status='native_records_release_vintage_unverified';evidence='structured/numerical_factors/native_observations.csv';action='Recover actual release vintages and official alternatives; preserve GDP annually, Japan LNG as its own benchmark and FX bar close as proxy.'
            elif factor in ['CNG vehicle registrations','active CNG vehicle stock']:status='observed_records_missing_manual_export_required';action='Export CNG ONLY and PETROL/CNG separately from new Parivahan portal by RTO/state/month. Registrations do not establish active fleet.'
            elif group=='2.8':status='corporate_documents_collected_extraction_partial' if len(corp) else 'corporate_collection_pending';evidence='structured/corporate_disclosures/corporate_disclosures_metadata.csv';action='Review financial/operational source tables and obtain original exchange release timestamps. No tone or novelty features in Stage 3.'
            elif group in ['2.7','2.9']:status='historical_H2_corpus_incomplete';evidence='structured/news/real_article_metadata.csv';action='Collect legally accessible historical article metadata/text and matched events. Sentiment, POS and bias computation remain deferred.'
            else:status='source_documents_partial_reviewed_table_extraction_pending' if len(docs) else 'source_discovery_partial';evidence='structured/documents/source_document_index.csv';action='Extract original tables/events at native frequency and geography, reviewing issue, effective and public release dates separately.'
            inv.append(dict(factor_id=f'{group}-{i:02}',stage2_group=group,factor=factor,hypothesis='H2' if group in ['2.7','2.8','2.9'] else 'H1',source_candidates=sources,native_geographical_grain=grain,collected_records=n,collected_documents=len(corp) if group=='2.8' else len(docs) if 'documents_partial' in status else 0,earliest_record_period=first,latest_record_period=last,status=status,evidence_paths=evidence,missing_periods='all periods outside explicit retained evidence; initial historical bound unknown; no continuity inferred',next_retrieval_action=action))
    atomic_csv(pd.DataFrame(inv),B/'metadata/data_inventory.csv');cities=read('metadata/city_coverage_matrix.csv');matrix=[]
    for city in cities.city:
        for r in inv:matrix.append(dict(city_candidate=city,**r,city_mapping_status='unverified_no_city_observations_created',verified_continuous_target_months=0))
    atomic_csv(pd.DataFrame(matrix),B/'metadata/factor_city_period_coverage.csv')
    if len(prices):prices.groupby(['GA ID','Name of CGD Entity','GA Name','District'],dropna=False).agg(first_period=('report_period','min'),last_period=('report_period','max'),snapshot_records=('record_id','size'),observed_periods=('report_period','nunique')).reset_index().to_csv(B/'metadata/alternative_ga_coverage.csv',index=False)
    if len(m):
        registry=m.copy();registry['access_status']=registry.status;registry['reliability']='primary_host_candidate_content_and_timing_review_required';registry['frequency']='item_specific_native_frequency';registry['coverage']='retained_content_only_no_continuity_claim';registry['licensing']='public_access_does_not_establish_redistribution_rights';atomic_csv(registry,B/'metadata/source_registry.csv')
    dictionary=[]
    definitions={'publication_timestamp':'Actual public release time only when explicit evidence supports it; otherwise null.','effective_date_claim':'Source-reported revision date; independent verification pending.','gas_cost':'Entity-submitted natural-gas cost in INR/kg, distinct from market benchmarks.','report_period':'Original table monthly label, not a publication time.','value_class':'Observed, derived, estimated, proxy or unverified; observed is not independently validated.','rsp_arithmetic_residual':'Reported RSP less basic price, excise, VAT and other tax. Missing terms remain missing.','basic_arithmetic_residual':'Reported basic price less gas, supply/distribution, margin and transmission components.'}
    for p in sorted((B/'structured').rglob('*.csv')):
        try:d=pd.read_csv(p,nrows=3)
        except pd.errors.EmptyDataError:continue
        for c in d.columns:dictionary.append(dict(dataset=str(p.relative_to(B)),field=c,data_type=str(d[c].dtype),definition=definitions.get(c,'Native source field or explicit extraction metadata. Consult retained source and extraction code; no new definition inferred.'),units='see_native_unit_field_or_source',transformation='source extraction or named arithmetic/provenance operation; no imputation',provenance='source_id/raw_file -> acquisition manifest; legacy records -> legacy_file_manifest.csv',missing_value_meaning='unknown/unavailable/not applicable; never zero by default'))
    atomic_csv(pd.DataFrame(dictionary),B/'metadata/data_dictionary.csv')
    print('catalogued',len(inv),'factors',len(matrix),'factor-city rows',flush=True)

def verify(strict=False):
    checks=[]
    def ck(name,ok,detail,block=False):checks.append(dict(check=name,status='pass' if ok else 'blocked' if block else 'fail',detail=detail))
    original=read('metadata/legacy_file_manifest.csv');bad=[r.path for _,r in original.iterrows() if not (B/r.preserved_path).exists() or sha(B/r.preserved_path)!=r.sha256];ck('original_bytes_preserved',len(original)>0 and not bad,dict(files=len(original),mismatches=bad))
    obs=read('structured/price_revisions/source_observations.csv');bad=[]
    for city,g in obs.groupby('city'):
        pairs=re.findall(r"new Date\('([^']+)'\)\s*,\s*y:([\d.]+)",(B/g.raw_file.iloc[0]).read_text());source={(pd.to_datetime(d).strftime('%Y-%m-%d'),float(v)) for d,v in pairs}
        if source!=set(zip(g.observation_date,g.cng_price.astype(float))):bad.append(city)
    ck('observations_match_raw_source_pairs',not bad,bad);ck('unverified_dates_not_claimed_verified',obs.effective_date.isna().all() and obs.publication_timestamp.isna().all(),dict(records=len(obs)))
    targets=read('structured/price_revisions/cng_monthly_panel.csv');ck('incomplete_month_excluded',not len(targets) or targets.year_month.lt(MONTH).all(),dict(target_rows=len(targets)));ck('continuous_primary_target_paths_verified',False,'Primary effective-date histories remain incomplete.',True)
    demand=read('structured/numerical_factors/demand_factors_monthly.csv');ck('synthetic_vehicle_values_removed',demand.vahan_cng_registrations.isna().all(),dict(missing_observed_records=len(demand)))
    m=materialize_manifest();bad=[]
    if len(m):
        for _,r in m[m.status.eq('downloaded')].iterrows():
            if not (B/r.raw_file).exists() or sha(B/r.raw_file)!=r.sha256:bad.append(r.source_url)
    ck('acquired_file_checksums',not bad,dict(acquisitions=len(m),mismatches=bad));ck('source_access_and_content',len(m)>0 and m.status.eq('downloaded').all(),dict(failures=int(m.status.ne('downloaded').sum()) if len(m) else 0),True)
    prices=read('structured/price_revisions/pngrb_cng_components_native.csv');ck('PNGRB_component_arithmetic',len(prices)>0 and prices.arithmetic_status.eq('pass_tolerance_0.05').all(),prices.arithmetic_status.value_counts().to_dict() if len(prices) else {},True);ck('historical_public_release_timing_verified',False,'Monthly reporting periods, issue dates and revision dates are not public release timestamps.',True)
    gdp=read('structured/numerical_factors/gdp_annual_native.csv');ck('GDP_kept_annual',len(gdp)>0 and gdp.frequency.eq('annual').all(),dict(records=len(gdp)))
    inv=read('metadata/data_inventory.csv');cov=read('metadata/factor_city_period_coverage.csv');cities=read('metadata/city_coverage_matrix.csv');ck('all_groups_and_candidate_cities_catalogued',set(inv.stage2_group.astype(str))=={f'2.{i}' for i in range(1,10)} and len(cov)==len(inv)*len(cities),dict(factors=len(inv),factor_city_rows=len(cov)))
    corp=read('structured/corporate_disclosures/corporate_disclosures_metadata.csv');ck('corporate_documents_collected',len(corp)>0,dict(records=len(corp)),True);ck('all_factor_collection_complete',False,'Manual exports, reviewed numeric tables, historical city price paths and H2 corpus remain incomplete.',True)
    parity=[]
    for p in (B/'structured').rglob('*.csv'):
        q=p.with_suffix('.parquet')
        if not q.exists():continue
        try:a=pd.read_csv(p);b=pd.read_parquet(q)
        except pd.errors.EmptyDataError:continue
        if a.shape!=b.shape or list(a.columns)!=list(b.columns):parity.append(str(p.relative_to(B)))
    ck('CSV_Parquet_schema_row_parity',not parity,parity)
    result=dict(run_timestamp=now(),stage=3,stage3_complete=False,stage4_authorized=False,model_ready_validated=False,checks=checks,check_status_counts=pd.Series([x['status'] for x in checks]).value_counts().to_dict());(B/'logs/stage3_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['check_status_counts']),flush=True)
    if any(x['status']=='fail' for x in checks):raise SystemExit(1)
    if strict and any(x['status']=='blocked' for x in checks):raise SystemExit(2)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['audit','collect','extract','catalogue','verify','all']);p.add_argument('--retry-failed',action='store_true');p.add_argument('--strict',action='store_true');a=p.parse_args()
    (B/'metadata').mkdir(exist_ok=True);(B/'logs').mkdir(exist_ok=True)
    if a.command in ['audit','all']:audit()
    if a.command in ['collect','all']:collect(a.retry_failed)
    if a.command in ['extract','all']:extract()
    if a.command in ['catalogue','all']:catalogue()
    if a.command in ['verify','all']:verify(a.strict)
