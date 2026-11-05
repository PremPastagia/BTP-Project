import requests, ssl, json
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

# 1. Test GDP
url_gdp = 'https://api.mospi.gov.in/api/nas/getNasData?account_code=1&frequency_code=2&indicator_code=5&base_year=2011-12&series=Current&limit=100'
r_gdp = s.get(url_gdp, timeout=20)
gdp_data = r_gdp.json().get('data', [])
print(f"GDP count: {len(gdp_data)}")
if gdp_data:
    print("GDP keys:", gdp_data[0].keys())
    print("First 3 GDP:", [(x.get('year'), x.get('quarter'), x.get('constant_price'), x.get('current_price')) for x in gdp_data[:3]])
    print("Last 3 GDP:", [(x.get('year'), x.get('quarter'), x.get('constant_price'), x.get('current_price')) for x in gdp_data[-3:]])

# 2. Test PFCE
url_pfce = 'https://api.mospi.gov.in/api/nas/getNasData?account_code=1&frequency_code=2&indicator_code=10&base_year=2011-12&series=Current&limit=100'
r_pfce = s.get(url_pfce, timeout=20)
pfce_data = r_pfce.json().get('data', [])
print(f"PFCE count: {len(pfce_data)}")
if pfce_data:
    print("First 3 PFCE:", [(x.get('year'), x.get('quarter'), x.get('constant_price'), x.get('current_price')) for x in pfce_data[:3]])
    print("Last 3 PFCE:", [(x.get('year'), x.get('quarter'), x.get('constant_price'), x.get('current_price')) for x in pfce_data[-3:]])

# 3. Check CPI pagination or range
# Let's see what years are available for CPI Base 2012
url_cpi_meta = 'https://api.mospi.gov.in/api/cpi/getCpiFilterByLevelAndBaseYear?level=Group&base_year=2012'
r_meta = s.get(url_cpi_meta, timeout=20)
print(f"CPI meta status: {r_meta.status_code}")
try:
    meta_json = r_meta.json()
    print("CPI meta keys:", meta_json.keys() if isinstance(meta_json, dict) else len(meta_json))
    if isinstance(meta_json, dict):
        years = [x.get('year') for x in meta_json.get('years', [])]
        print("Available CPI years:", years)
except Exception as e:
    print("Meta parse error:", e)
