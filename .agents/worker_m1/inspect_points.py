import requests, re
from datetime import datetime

url = "https://www.mypetrolprice.com/FuelHistoryDataServing.aspx?LocationId=2&Span=365&selectedFuels=3H&HikeChartId=FuelHikeChartDetails"
headers = {"User-Agent": "Mozilla/5.0"}
r = requests.get(url, headers=headers, timeout=15)
pts = re.findall(r"\{x:\s*new Date\('([^']+)'\)\s*,\s*y:\s*([0-9.]+)\s*\}", r.text)
print(f"Total raw points: {len(pts)}")
parsed = []
for d_str, p_str in pts:
    dt = datetime.strptime(d_str, "%b %d %Y").date()
    p = float(p_str)
    parsed.append((dt, p))

# Sort by date
parsed.sort(key=lambda x: x[0])

# Check changes
changes = []
last_p = None
for dt, p in parsed:
    if p != last_p:
        changes.append((dt, p))
        last_p = p

print(f"Distinct price revisions: {len(changes)}")
print("First 10 raw:", parsed[:10])
print("First 10 changes:", changes[:10])
print("Last 10 changes:", changes[-10:])
