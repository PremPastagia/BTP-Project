"""Bounded official CPI retrieval; legacy TLS compatibility retains certificate checks."""
from pathlib import Path
import urllib.request, ssl, json, hashlib, datetime, concurrent.futures, csv
OUT=Path(__file__).resolve().parents[1]
(OUT/'raw').mkdir(exist_ok=True);(OUT/'logs').mkdir(exist_ok=True)
ctx=ssl.create_default_context();ctx.options |= 0x4
jobs=[(str(y),'2012') for y in range(2011,2027)]+[('2025','2024'),('2026','2024')]
def fetch(job):
    year,base=job
    url=f'https://api.mospi.gov.in/api/cpi/getCpiData?level=Group&base_year={base}&state_code=99&sector_code=3&group_code=0&subgroup_code=0.99&year={year}&limit=100'
    record={'url':url,'query_year':year,'query_base':base,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'TLS_legacy_server_connect_with_certificate_validation'}
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),context=ctx,timeout=30) as response:
            data=response.read();record.update(http_status=response.status,content_type=response.headers.get('Content-Type'))
        h=hashlib.sha256(data).hexdigest();path=OUT/'raw'/('mospi_cpi_'+h+'.response');path.write_bytes(data)
        record.update(raw_sha256=h,raw_file=str(path.relative_to(OUT)),bytes=len(data))
        payload=json.loads(data);records=payload.get('data',[])
        record.update(records=len(records),message=payload.get('msg'),metadata=payload.get('meta_data'))
    except Exception as e:record.update(http_status='failed',error=str(e))
    return record
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:manifest=list(pool.map(fetch,jobs))
(OUT/'logs/mospi_cpi_acquisition_manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'queries':len(manifest),'successful_records':sum(x.get('records',0) for x in manifest),'failed_or_empty':[x for x in manifest if not x.get('records')]},indent=2))
