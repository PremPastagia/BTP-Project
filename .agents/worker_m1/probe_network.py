import requests, re, ssl
from requests.adapters import HTTPAdapter
from urllib3.util import create_urllib3_context

# 1. Test CNG endpoint
headers = {'User-Agent': 'Mozilla/5.0'}
url = 'https://www.mypetrolprice.com/FuelHistoryDataServing.aspx?LocationId=2&Span=365&selectedFuels=3H&HikeChartId=FuelHikeChartDetails'
try:
    r_cng = requests.get(url, headers=headers, timeout=15)
    pts = re.findall(r"\{x:new Date\('([^']+)'\)\s*,\s*y:([0-9.]+)\}", r_cng.text)
    print(f"CNG Delhi: status={r_cng.status_code}, points={len(pts)}, first={pts[0] if pts else None}, last={pts[-1] if pts else None}")
except Exception as e:
    print('CNG Error:', e)

# 2. Test MoSPI endpoint
class LegacySSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.options |= 0x4
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

s = requests.Session()
s.mount('https://', LegacySSLAdapter())
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

try:
    r_gdp = s.get('https://api.mospi.gov.in/api/nas/getNasData?account_code=1&frequency_code=2&indicator_code=5&base_year=2011-12&series=Current&limit=100', timeout=20)
    data_gdp = r_gdp.json().get('data', [])
    print(f"MoSPI GDP: status={r_gdp.status_code}, count={len(data_gdp)}")
    if data_gdp:
        print("GDP sample:", data_gdp[0])
except Exception as e:
    print('MoSPI GDP Error:', e)

try:
    r_cpi = s.get('https://api.mospi.gov.in/api/cpi/getCpiData?level=Group&base_year=2012&state_code=99&sector_code=3&group_code=0&subgroup_code=0.99&year=2023&month_code=6', timeout=20)
    data_cpi = r_cpi.json().get('data', [])
    print(f"MoSPI CPI: status={r_cpi.status_code}, data={data_cpi}")
except Exception as e:
    print('MoSPI CPI Error:', e)
