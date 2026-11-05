import requests, re, calendar
from datetime import datetime, date, timedelta
import pandas as pd

cities = [
    (2, "Delhi", "IGL"),
    (3, "Mumbai", "MGL"),
    (37, "Noida", "IGL"),
    (39, "Ghaziabad", "IGL"),
    (10, "Ahmedabad", "ATGL/GGL"),
    (7, "Pune", "MNGL"),
]

headers = {"User-Agent": "Mozilla/5.0"}
all_rows = []

for loc_id, city, dist in cities:
    url = f"https://www.mypetrolprice.com/FuelHistoryDataServing.aspx?LocationId={loc_id}&Span=365&selectedFuels=3H&HikeChartId=FuelHikeChartDetails"
    r = requests.get(url, headers=headers, timeout=15)
    pts = re.findall(r"\{x:\s*new Date\('([^']+)'\)\s*,\s*y:\s*([0-9.]+)\s*\}", r.text)
    
    # Parse points
    parsed = []
    for d_str, p_str in pts:
        dt = datetime.strptime(d_str, "%b %d %Y").date()
        p = float(p_str)
        parsed.append((dt, p))
    parsed.sort(key=lambda x: x[0])
    
    # Identify price changes (revisions)
    revisions = []
    last_p = None
    for dt, p in parsed:
        if p != last_p:
            revisions.append((dt, p))
            last_p = p
            
    first_date = revisions[0][0]
    last_date = parsed[-1][0]
    
    # Daily expansion using Zero-Order Hold (step forward fill)
    daily_prices = {}
    rev_dates = set(r[0] for r in revisions)
    
    curr = first_date
    rev_idx = 0
    curr_price = revisions[0][1]
    
    while curr <= last_date:
        # Check if there is a revision on this date
        matching_revs = [r[1] for r in revisions if r[0] == curr]
        if matching_revs:
            curr_price = matching_revs[-1]
        daily_prices[curr] = curr_price
        curr += timedelta(days=1)
        
    # Group by month
    start_year_month = (first_date.year, first_date.month)
    end_year_month = (last_date.year, last_date.month)
    
    y = start_year_month[0]
    m = start_year_month[1]
    
    while (y, m) <= end_year_month:
        _, num_days = calendar.monthrange(y, m)
        month_days = [date(y, m, d) for d in range(1, num_days + 1)]
        valid_days = [d for d in month_days if d in daily_prices]
        
        if valid_days:
            twap = sum(daily_prices[d] for d in valid_days) / len(valid_days)
            rev_count = sum(1 for d in month_days if d in rev_dates)
            month_str = f"{y:04d}-{m:02d}-01"
            all_rows.append({
                "Date": month_str,
                "City": city,
                "Distributor": dist,
                "Price_INR": round(twap, 2),
                "Revision_Count": rev_count
            })
            
        m += 1
        if m > 12:
            m = 1
            y += 1

df = pd.DataFrame(all_rows)
print(f"Total panel rows: {len(df)}")
print("Rows per city:")
print(df.groupby('City')['Date'].agg(['count', 'min', 'max']))
print("\nSample rows:")
print(df.head(10))
print("\nSample revisions > 0:")
print(df[df['Revision_Count'] > 0].head(10))
