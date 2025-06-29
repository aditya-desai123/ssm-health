#!/usr/bin/env python3
"""
Merge Minnesota, Wisconsin, and Illinois ZIP code GeoJSONs into a single file.
"""
import json

# Input files
files = [
    'zipcodes_mn.geojson',
    'zipcodes_wi.geojson',
    'zipcodes_il.geojson',
]

all_features = []
for f in files:
    with open(f, 'r') as infile:
        data = json.load(infile)
        all_features.extend(data['features'])

merged = {
    "type": "FeatureCollection",
    "features": all_features
}

with open('zipcodes_mn_wi_il.geojson', 'w') as outfile:
    json.dump(merged, outfile)

print(f"✅ Merged {len(all_features)} ZIP polygons into zipcodes_mn_wi_il.geojson") 