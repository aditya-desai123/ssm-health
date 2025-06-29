#!/usr/bin/env python3
"""
Extract all ZIP codes from zipcodes_mn_wi_il.geojson and save to all_mn_wi_il_zips.csv
"""
import json
import csv

with open('zipcodes_mn_wi_il.geojson', 'r') as f:
    geo = json.load(f)

zip_codes = set()
for feature in geo['features']:
    zip_code = feature['properties'].get('ZCTA5CE10') or feature['properties'].get('ZCTA5CE') or feature['properties'].get('ZIPCODE')
    if zip_code:
        zip_codes.add(str(zip_code).zfill(5))

with open('all_mn_wi_il_zips.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['zip'])
    for z in sorted(zip_codes):
        writer.writerow([z])

print(f"✅ Extracted {len(zip_codes)} ZIP codes to all_mn_wi_il_zips.csv") 