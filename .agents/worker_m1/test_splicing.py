import test_mospi_details
s = test_mospi_details.s

# Fetch 2011-12 series
r_1112 = s.get('https://api.mospi.gov.in/api/nas/getNasData?account_code=1&frequency_code=2&indicator_code=5&base_year=2011-12&series=Current&limit=100', timeout=20)
d_1112 = {f"{x['year']}_{x['quarter']}": float(x['constant_price']) for x in r_1112.json().get('data', [])}

# Fetch 2022-23 series
r_2223 = s.get('https://api.mospi.gov.in/api/nas/getNasData?account_code=1&frequency_code=2&indicator_code=5&base_year=2022-23&series=Current&limit=100', timeout=20)
d_2223 = {f"{x['year']}_{x['quarter']}": float(x['constant_price']) for x in r_2223.json().get('data', [])}

overlap = sorted(set(d_1112.keys()) & set(d_2223.keys()))
print(f"Overlapping quarters ({len(overlap)}):", overlap)

if overlap:
    sum_1112 = sum(d_1112[k] for k in overlap)
    sum_2223 = sum(d_2223[k] for k in overlap)
    L = sum_1112 / sum_2223
    print(f"Sum 2011-12: {sum_1112}, Sum 2022-23: {sum_2223}")
    print(f"Ratio Linking Factor L (2022-23 -> 2011-12): {L:.6f}")
    
    # Check individual quarterly ratios
    for k in overlap:
        ratio = d_1112[k] / d_2223[k]
        print(f"  {k}: 11-12={d_1112[k]}, 22-23={d_2223[k]}, ratio={ratio:.6f}")
        
    # Check non-overlapping quarters in 2022-23 that can be spliced forward
    only_2223 = sorted(set(d_2223.keys()) - set(d_1112.keys()))
    print("Quarters only in 2022-23 (to be spliced forward):", only_2223)
    for k in only_2223:
        spliced_val = d_2223[k] * L
        print(f"  {k}: 22-23={d_2223[k]} -> spliced (2011-12 equiv) = {spliced_val:.2f}")
