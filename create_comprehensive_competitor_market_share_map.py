#!/usr/bin/env python3
"""
Create Comprehensive Competitor Market Share Map
Merges all market share data from STL/SoIL, Wisconsin, and Oklahoma into one unified map.
Each ZIP code is colored by the dominant hospital system (2024 data).
Popups show the market share breakdown for all systems in that ZIP.
Includes HHI (Herfindahl-Hirschman Index) scores for market concentration analysis.
"""

import pandas as pd
import folium
import json
from collections import defaultdict

def main():
    # Load all market share data
    print("📊 Loading market share data from all regions...")

    # STL/SoIL data
    stl_soil_df = pd.read_excel('STL_SoIL_2024IP_MktShare.xlsx')
    stl_soil_df['Region'] = 'STL/SoIL'

    # Wisconsin data
    wi_df = pd.read_excel('WI_2024IP_MktShare.xlsx')
    wi_df['Region'] = 'Wisconsin'

    # Oklahoma data
    ok_df = pd.read_excel('OK_2024IP_MktShare.xlsx')
    ok_df['Region'] = 'Oklahoma'

    # Combine all datasets
    all_market_df = pd.concat([stl_soil_df, wi_df, ok_df], ignore_index=True)

    print(f"📈 Total records loaded: {len(all_market_df)}")
    print(f"   - STL/SoIL: {len(stl_soil_df)}")
    print(f"   - Wisconsin: {len(wi_df)}")
    print(f"   - Oklahoma: {len(ok_df)}")

    # Only keep rows with valid ZIP codes and hospital systems
    all_market_df = all_market_df.dropna(subset=['Zip Code', 'Hospital System'])
    all_market_df['Zip Code'] = all_market_df['Zip Code'].astype(float).astype(int).astype(str).str.zfill(5)

    print(f"📊 Valid records after cleaning: {len(all_market_df)}")

    # Aggregate: count interactions per ZIP per system
    zip_sys_counts = all_market_df.groupby(['Zip Code', 'Hospital System']).size().reset_index(name='count')

    # For each ZIP, get total and per-system counts
    zip_totals = zip_sys_counts.groupby('Zip Code')['count'].sum().to_dict()

    # For each ZIP, build a dict of system: market share and calculate HHI
    zip_market_share = defaultdict(dict)
    zip_hhi = {}

    for _, row in zip_sys_counts.iterrows():
        zip_code = row['Zip Code']
        system = row['Hospital System']
        count = row['count']
        total = zip_totals[zip_code]
        share = count / total if total > 0 else 0
        zip_market_share[zip_code][system] = share

    # Calculate HHI for each ZIP (sum of squared market shares)
    for zip_code, systems in zip_market_share.items():
        hhi = sum(share ** 2 for share in systems.values()) * 10000  # Scale to 0-10,000 range
        zip_hhi[zip_code] = hhi

    # For each ZIP, find the dominant system
    zip_dominant = {z: max(systems, key=systems.get) for z, systems in zip_market_share.items()}

    dominant_systems = set(zip_dominant.values())
    print(f"🏥 Dominant systems across all regions: {len(dominant_systems)}")
    print("   Systems:", sorted(dominant_systems))

    # HHI statistics
    hhi_values = list(zip_hhi.values())
    print(f"📊 HHI Statistics:")
    print(f"   - Average HHI: {sum(hhi_values)/len(hhi_values):.0f}")
    print(f"   - Min HHI: {min(hhi_values):.0f}")
    print(f"   - Max HHI: {max(hhi_values):.0f}")

    # Assign a color to each hospital system
    system_list = sorted(dominant_systems)
    colors = [
        '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#a65628', '#f781bf', '#999999', 
        '#dede00', '#00bfff', '#8c564b', '#b15928', '#b2df8a', '#cab2d6', '#6a3d9a', '#ffff99', 
        '#b15928', '#fb8072', '#80b1d3', '#fdb462', '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd',
        '#ccebc5', '#ffed6f', '#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c',
        '#fdbf6f', '#ff7f00', '#cab2d6', '#6a6a6a', '#ffffb3', '#bebada', '#fb8072', '#80b1d3'
    ]

    system_colors = {
        sys: colors[i % len(colors)] for i, sys in enumerate(system_list)
    }

    print(f"🎨 Color scheme assigned to {len(system_colors)} systems")

    # Load ZIP code polygons
    print("🗺️ Loading geographic data...")
    with open('zipcodes_mn_wi_il_scored.geojson', 'r') as f:
        mn_wi_il_geojson = json.load(f)
    with open('zipcodes_mo_ok.geojson', 'r') as f:
        mo_ok_geojson = json.load(f)

    # Combine features
    all_features = mn_wi_il_geojson['features'] + mo_ok_geojson['features']

    # Create base map (centered on the middle of all regions)
    center = [40.0, -90.0]  # Roughly center of all regions
    m = folium.Map(location=center, zoom_start=5, tiles='cartodbpositron')

    # Print sample ZIPs for debugging
    geojson_zips = set()
    for feature in all_features:
        zc = feature['properties'].get('ZCTA5CE10') or feature['properties'].get('ZCTA5CE20')
        if zc:
            geojson_zips.add(zc)

    overlap = set(zip_dominant.keys()) & geojson_zips
    print(f"📍 ZIP codes with market share data: {len(zip_dominant)}")
    print(f"🗺️ ZIP codes in geographic data: {len(geojson_zips)}")
    print(f"✅ Overlapping ZIP codes: {len(overlap)}")

    # Function to get HHI interpretation
    def get_hhi_interpretation(hhi):
        if hhi < 1500:
            return "Unconcentrated (Competitive)"
        elif hhi < 2500:
            return "Moderately Concentrated"
        else:
            return "Highly Concentrated"

    # Add ZIP polygons colored by dominant system
    colored_zips = 0
    for feature in all_features:
        zip_code = feature['properties'].get('ZCTA5CE10') or feature['properties'].get('ZCTA5CE20')
        if not zip_code or zip_code not in zip_dominant:
            continue
        
        dominant_system = zip_dominant[zip_code]
        color = system_colors.get(dominant_system, '#cccccc')
        hhi = zip_hhi[zip_code]
        hhi_interpretation = get_hhi_interpretation(hhi)
        
        # Popup: show all market shares for this ZIP with HHI
        popup_html = f'''
        <b>ZIP: {zip_code}</b><br>
        <b>Dominant System:</b> {dominant_system}<br>
        <b>HHI Score:</b> {hhi:.0f} ({hhi_interpretation})<br>
        <b>Market Share Breakdown:</b><ul>
        '''
        for sys, share in sorted(zip_market_share[zip_code].items(), key=lambda x: -x[1]):
            popup_html += f'<li>{sys}: {share:.1%}</li>'
        popup_html += '</ul>'
        
        def style_fn(f, color=color):
            return {
                'fillColor': color,
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7
            }
        
        folium.GeoJson(
            feature,
            style_function=style_fn,
            highlight_function=lambda f: {'weight': 2, 'color': 'blue'},
            tooltip=f"ZIP: {zip_code} | {dominant_system} | HHI: {hhi:.0f}",
            popup=folium.Popup(popup_html, max_width=400)
        ).add_to(m)
        colored_zips += 1

    print(f"🎨 Colored {colored_zips} ZIP codes on the map")

    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 350px; max-height: 400px; 
                background: white; border:2px solid grey; z-index:9999; font-size:12px; 
                padding: 10px; overflow-y: auto;">
    <b>Hospital System Market Share</b><br>
    <small>Click ZIP codes to see detailed breakdown</small><br>
    <small>HHI: Market concentration index (0-10,000)</small><br>
    '''
    for sys, color in system_colors.items():
        legend_html += f'<div style="display: flex; align-items: center; margin: 2px 0;"><div style="background:{color};width:16px;height:16px;margin-right:8px;border-radius:2px;"></div><span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{sys}</span></div>'
    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add title
    title_html = '''
    <div style="position: fixed; top: 10px; left: 50px; width: 400px; 
                background: white; border:2px solid grey; z-index:9999; font-size:14px; 
                padding: 10px;">
    <b>SSM Health - Comprehensive Competitor Market Share Map</b><br>
    <small>STL/SoIL, Wisconsin, and Oklahoma - 2024 Data</small><br>
    <small>Includes HHI (Herfindahl-Hirschman Index) for market concentration</small>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    # Save map
    output_file = 'ssm_health_comprehensive_competitor_market_share_map.html'
    m.save(output_file)
    print(f"✅ Comprehensive competitor market share map saved to: {output_file}")
    print(f"📊 Map covers {len(zip_dominant)} ZIP codes across all regions")
    print(f"🏥 Shows market share for {len(dominant_systems)} hospital systems")
    print(f"📈 HHI analysis included for market concentration insights")

if __name__ == '__main__':
    main() 