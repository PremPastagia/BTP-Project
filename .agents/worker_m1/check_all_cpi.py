import requests, ssl
from requests.adapters import HTTPAdapter
from urllib3.util import create_urllib3_context

class LegacySSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.options |= 0x4
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

s = requests.Session()
s.mount('https://', LegacySSLAdapter())
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

results = {}
for y in range(2011, 2027):
    url = f'https://api.mospi.gov.in/api/cpi/getCpiData?level=Group&base_year=2012&state_code=99&sector_code=3&group_code=0&subgroup_code=0.99&year={y}&limit=100'
    try:
        r = s.get(url, timeout=15)
        d = r.json().get('data', [])
        results[y] = [(x.get('month'), x.get('index')) for x in d]
        print(f"Year {y}: {len(d)} records. Earliest/latest: {d[-1]['month']} ({d[-1]['index']}) to {d[0]['month']} ({d[0]['index']}) if d else 'Empty'")
    except Exception as e:
        print(f"Year {y} error: {e}")

total_records = sum(len(v) for v in results.values())
print(f"Total CPI records found: {total_records}")
