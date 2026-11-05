import test_mospi_details
s = test_mospi_details.s

for by in ['2004-05', '2011-12', '2022-23']:
    url = f'https://api.mospi.gov.in/api/nas/getNasData?account_code=1&frequency_code=2&indicator_code=5&base_year={by}&series=Current&limit=10'
    r = s.get(url, timeout=15)
    d = r.json().get('data', [])
    print(f"GDP base_year={by}: status={r.status_code}, count={len(d)}")

for by in ['2010', '2012', '2024']:
    url = f'https://api.mospi.gov.in/api/cpi/getCpiData?level=Group&base_year={by}&state_code=99&sector_code=3&group_code=0&subgroup_code=0.99&year=2012&limit=5'
    r = s.get(url, timeout=15)
    d = r.json().get('data', [])
    print(f"CPI base_year={by}: status={r.status_code}, count={len(d)}")
