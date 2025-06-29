import pandas as pd
import json

# Load the scored CSV
csv_file = 'all_mn_wi_il_zip_demographics_scored.csv'
df = pd.read_csv(csv_file)

# Load the GeoJSON
geojson_file = 'zipcodes_mn_wi_il_scored.geojson'
with open(geojson_file, 'r') as f:
    geojson = json.load(f)

# Create a lookup dict from ZIP to row
csv_lookup = df.set_index('zip').to_dict(orient='index')

# Add scoring fields to each feature
for feature in geojson['features']:
    zip_code = feature['properties'].get('ZCTA5CE10')
    if zip_code in csv_lookup:
        for key, value in csv_lookup[zip_code].items():
            feature['properties'][key] = value

# Save the enriched GeoJSON
output_file = 'zipcodes_mn_wi_il_scored_enriched.geojson'
with open(output_file, 'w') as f:
    json.dump(geojson, f)

print(f"✅ Enriched GeoJSON saved to {output_file}") 