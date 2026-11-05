import test_mospi_details

gdp = test_mospi_details.gdp_data
pfce = test_mospi_details.pfce_data

print(f"Total GDP records: {len(gdp)}")
print(f"Total PFCE records: {len(pfce)}")

# Inspect sort order and quarters
quarters = [(x['year'], x['quarter'], float(x['constant_price']), float(x['current_price'])) for x in gdp]
print("All GDP quarters in order returned by API:")
for q in quarters:
    print(q)
