import requests, re
from datetime import datetime

cities = [
    (2, "Delhi", "IGL"),
    (3, "Mumbai", "MGL"),
    (37, "Noida", "IGL"),
    (39, "Ghaziabad", "IGL"),
    (10, "Ahmedabad", "ATGL/GGL"),
    (7, "Pune", "MNGL"),
]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

for loc_id, city, dist in cities:
    url = f"https://www.mypetrolprice.com/FuelHistoryDataServing.aspx?LocationId={loc_id}&Span=365&selectedFuels=3H&HikeChartId=FuelHikeChartDetails"
    r = requests.get(url, headers=headers, timeout=15)
    # Match patterns like { x: new Date('Oct 01 2011'), y: 32.00 } or {x:new Date('...'),y:...}
    pts = re.findall(r"\{x:\s*new Date\('([^']+)'\)\s*,\s*y:\s*([0-9.]+)\s*\}", r.text)
    if not pts:
        # Try alternate spacing
        pts = re.findall(r"new Date\('([^']+)'\)[^0-9]+([0-9.]+)", r.text)
    print(f"{city} ({loc_id}): {len(pts)} points. First: {pts[0] if pts else 'None'}, Last: {pts[-1] if pts else 'None'}")
