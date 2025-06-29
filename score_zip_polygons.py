#!/usr/bin/env python3
"""
Join demographics and score all ZIP polygons in MN, WI, IL using existing weights.
"""
import pandas as pd
import json
import numpy as np

# Load demographic data
zip_demo = pd.read_csv('ssm_health_locations_with_zip_demographics.csv', dtype={'zip': str})

# Deduplicate ZIPs by taking the mean for each ZIP
zip_demo = zip_demo.groupby('zip').mean(numeric_only=True).reset_index()

# Calculate scores using the same logic as in create_attractiveness_scores.py
# (Copying the scoring logic for consistency)
def normalize_score(values, method='percentile'):
    if method == 'percentile':
        return values.rank(pct=True) * 100
    elif method == 'minmax':
        min_val = values.min()
        max_val = values.max()
        if max_val == min_val:
            return pd.Series([50] * len(values), index=values.index)
        return ((values - min_val) / (max_val - min_val)) * 100

def calculate_scores(df):
    weights = {
        'population_density': 0.25,
        'population_growth': 0.20,
        'senior_population': 0.25,
        'income_level': 0.20,
        'young_family': 0.10
    }
    # Component scores
    density_score = normalize_score(df['zip_population_density'])
    growth_score = normalize_score(df['zip_population_growth_rate'])
    senior_pct = df['zip_pct_age_65_74'] + df['zip_pct_age_75_84'] + df['zip_pct_age_85_plus']
    senior_score = normalize_score(senior_pct)
    income_score = normalize_score(df['zip_median_household_income'])
    young_pct = df['zip_pct_under_5'] + df['zip_pct_age_5_17']
    young_score = normalize_score(young_pct)
    # Composite
    composite = (
        density_score * weights['population_density'] +
        growth_score * weights['population_growth'] +
        senior_score * weights['senior_population'] +
        income_score * weights['income_level'] +
        young_score * weights['young_family']
    )
    composite = np.clip(composite, 0, 100)
    df['attractiveness_score'] = composite
    return df

zip_demo = calculate_scores(zip_demo)

# Load merged ZIP polygons
with open('zipcodes_mn_wi_il.geojson', 'r') as f:
    geo = json.load(f)

# Attach demographic and score data to each polygon
zip_demo_dict = zip_demo.set_index('zip').to_dict(orient='index')

for feature in geo['features']:
    zip_code = feature['properties'].get('ZCTA5CE10') or feature['properties'].get('ZCTA5CE') or feature['properties'].get('ZIPCODE') or feature['properties'].get('zip')
    if not zip_code:
        continue
    zip_code = str(zip_code).zfill(5)
    if zip_code in zip_demo_dict:
        for k, v in zip_demo_dict[zip_code].items():
            feature['properties'][k] = v
    else:
        feature['properties']['attractiveness_score'] = None

with open('zipcodes_mn_wi_il_scored.geojson', 'w') as f:
    json.dump(geo, f)

print('✅ Scored ZIP polygons saved to zipcodes_mn_wi_il_scored.geojson') 