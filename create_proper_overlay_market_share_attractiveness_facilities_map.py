#!/usr/bin/env python3
"""
Create Proper Overlay Market Share + Attractiveness + Facilities Map
Combines market share data (colored ZIPs) with attractiveness scores (opacity) and SSM facilities (icons)
Uses proper data loading and geocoding from the working scripts
"""

import pandas as pd
import folium
import json
from collections import defaultdict
import numpy as np
from folium import plugins
import re

def load_market_share_data():
    """Load and process market share data from all regions"""
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

    # Consolidate SSM systems into a single category
    all_market_df['Hospital System'] = all_market_df['Hospital System'].apply(
        lambda x: 'SSM Health' if 'SSM' in str(x).upper() else x
    )

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

    return zip_dominant, zip_market_share, zip_hhi

def load_attractiveness_data():
    """Load attractiveness scores data"""
    print("📊 Loading attractiveness scores data...")
    
    # Load MN/WI/IL data (excluding MN)
    mn_wi_il_data = pd.read_csv('all_mn_wi_il_zip_demographics_scored.csv')
    if 'state' in mn_wi_il_data.columns:
        mn_wi_il_data = mn_wi_il_data[~(mn_wi_il_data['state'] == 'MN')]
    print(f"  Loaded {len(mn_wi_il_data)} WI/IL ZIP codes")
    
    # Load OK/MO data
    ok_mo_data = pd.read_csv('all_ok_mo_zip_demographics_scored.csv')
    print(f"  Loaded {len(ok_mo_data)} OK/MO ZIP codes")
    
    # Combine the datasets
    combined_data = pd.concat([mn_wi_il_data, ok_mo_data], ignore_index=True)
    print(f"  Combined total: {len(combined_data)} ZIP codes")
    
    # Create lookup dictionary
    zip_attractiveness = {}
    for _, row in combined_data.iterrows():
        zip_code = str(row['zip'])
        zip_attractiveness[zip_code] = {
            'score': row['attractiveness_score'],
            'category': row['attractiveness_category'],
            'population': row['total_population'],
            'income': row['median_household_income'],
            'senior_pct': row['senior_population_pct']
        }
    
    return zip_attractiveness

def load_ssm_facilities():
    """Load SSM Health facility data"""
    print("🏥 Loading SSM Health facilities...")
    
    facility_files = [
        'ssm_health_locations_with_attractiveness_scores_and_coords.csv',
        'ssm_health_locations_with_census_zip_demographics.csv',
        'ssm_health_locations_with_zip_demographics.csv',
        'ssm_health_locations.csv'
    ]
    
    facilities = None
    for file in facility_files:
        try:
            facilities = pd.read_csv(file)
            print(f"  Loaded {len(facilities)} facilities from {file}")
            break
        except FileNotFoundError:
            continue
    
    if facilities is None:
        print("  ⚠️ No facility data found")
        return pd.DataFrame()
    
    # Load hospitals masterlist for classification
    try:
        hospitals_masterlist = pd.read_csv('hospitals_masterlist.csv', skiprows=2)
        hospitals_masterlist = hospitals_masterlist[hospitals_masterlist['name'].notna()]
        hospitals_masterlist = hospitals_masterlist[hospitals_masterlist['name'].str.strip() != '']
        
        hospital_names = set(hospitals_masterlist['name'].str.strip().str.lower())
        print(f"  Loaded {len(hospital_names)} hospital names from masterlist")
        
        def classify_hospitals(row):
            facility_name = str(row.get('name', '')).strip().lower()
            original_type = str(row.get('facility_type', '')).strip()
            
            if facility_name in hospital_names:
                return 'Hospital'
            elif original_type.lower() == 'emergency department (ed) / urgent care':
                if 'urgent care' in facility_name:
                    return 'Urgent Care'
                else:
                    return 'Emergency Department'
            elif original_type.lower() == 'hospital':
                return 'Clinic'
            else:
                return original_type
        
        facilities['facility_type'] = facilities.apply(classify_hospitals, axis=1)
        
        hospital_facilities = facilities[facilities['facility_type'] == 'Hospital']
        print(f"  Hospitals found: {len(hospital_facilities)}")
        
        type_counts = facilities['facility_type'].value_counts()
        print("  Facility classification:")
        for facility_type, count in type_counts.items():
            print(f"    {facility_type}: {count}")
        
        return facilities
        
    except FileNotFoundError:
        print("  ⚠️ hospitals_masterlist.csv not found, using original facility types")
        return facilities

def get_zip_coordinates(zip_code):
    """Get coordinates for a ZIP code from uszips.csv"""
    try:
        if not hasattr(get_zip_coordinates, 'uszips_data'):
            get_zip_coordinates.uszips_data = pd.read_csv('uszips.csv')
        
        zip_row = get_zip_coordinates.uszips_data[
            get_zip_coordinates.uszips_data['zip'] == str(zip_code)
        ]
        
        if not zip_row.empty:
            return zip_row.iloc[0]['lat'], zip_row.iloc[0]['lng']
        return None
    except:
        return None

def create_overlay_map(zip_dominant, zip_market_share, zip_hhi, zip_attractiveness, facilities):
    """Create the overlay map with market share, attractiveness, and facilities"""
    print("🗺️ Creating overlay map...")
    
    # Create base map
    center = [40.0, -90.0]  # Center of all regions
    m = folium.Map(location=center, zoom_start=5, tiles='cartodbpositron')
    
    # Assign colors to hospital systems
    dominant_systems = set(zip_dominant.values())
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
    
    # Load ZIP code polygons
    print("  Loading geographic data...")
    with open('zipcodes_mn_wi_il_scored.geojson', 'r') as f:
        mn_wi_il_geojson = json.load(f)
    with open('zipcodes_mo_ok.geojson', 'r') as f:
        mo_ok_geojson = json.load(f)
    
    # Combine features
    all_features = mn_wi_il_geojson['features'] + mo_ok_geojson['features']
    
    # Function to get HHI interpretation
    def get_hhi_interpretation(hhi):
        if hhi < 1500:
            return "Unconcentrated (Competitive)"
        elif hhi < 2500:
            return "Moderately Concentrated"
        else:
            return "Highly Concentrated"
    
    # Add ZIP polygons with market share colors and attractiveness opacity
    print("  Adding ZIP code polygons...")
    colored_zips = 0
    ssm_dominant_zips = 0
    
    for feature in all_features:
        zip_code = feature['properties'].get('ZCTA5CE10') or feature['properties'].get('ZCTA5CE20')
        if not zip_code or zip_code not in zip_dominant:
            continue
        
        dominant_system = zip_dominant[zip_code]
        color = system_colors.get(dominant_system, '#cccccc')
        hhi = zip_hhi[zip_code]
        hhi_interpretation = get_hhi_interpretation(hhi)
        
        # Get attractiveness data for opacity
        attractiveness_data = zip_attractiveness.get(zip_code, {})
        attractiveness_score = attractiveness_data.get('score', 50)  # Default to 50 if not found
        
        # Calculate opacity based on attractiveness (0.3 to 0.9 range)
        opacity = 0.3 + (attractiveness_score / 100) * 0.6
        
        # Check if SSM is the dominant system
        is_ssm_dominant = 'SSM' in dominant_system.upper()
        if is_ssm_dominant:
            ssm_dominant_zips += 1
        
        # Create popup content
        popup_html = f'''
        <b>ZIP: {zip_code}</b><br>
        <b>Dominant System:</b> {dominant_system}<br>
        <b>HHI Score:</b> {hhi:.0f} ({hhi_interpretation})<br>
        <b>Attractiveness Score:</b> {attractiveness_score:.1f}<br>
        <b>Attractiveness Category:</b> {attractiveness_data.get('category', 'N/A')}<br>
        <b>Population:</b> {attractiveness_data.get('population', 'N/A'):,.0f}<br>
        <b>Median Income:</b> ${attractiveness_data.get('income', 'N/A'):,.0f}<br>
        <b>Senior Population %:</b> {attractiveness_data.get('senior_pct', 'N/A'):.1f}%<br>
        <b>Market Share Breakdown:</b><ul>
        '''
        for sys, share in sorted(zip_market_share[zip_code].items(), key=lambda x: -x[1]):
            popup_html += f'<li>{sys}: {share:.1%}</li>'
        popup_html += '</ul>'
        
        def style_fn(f, color=color, opacity=opacity, is_ssm=is_ssm_dominant):
            style = {
                'fillColor': color,
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': opacity
            }
            # Add special outline for SSM-dominant ZIPs
            if is_ssm:
                style.update({
                    'color': '#FF6B35',  # Orange-red outline
                    'weight': 3,         # Thicker outline
                    'opacity': 1.0       # Full opacity for outline
                })
            return style
        
        folium.GeoJson(
            feature,
            style_function=style_fn,
            highlight_function=lambda f: {'weight': 2, 'color': 'blue'},
            tooltip=f"ZIP: {zip_code} | {dominant_system} | Attractiveness: {attractiveness_score:.1f}",
            popup=folium.Popup(popup_html, max_width=400)
        ).add_to(m)
        colored_zips += 1
    
    print(f"🎨 Colored {colored_zips} ZIP codes on the map")
    print(f"🏥 SSM Health is market leader in {ssm_dominant_zips} ZIP codes")
    
    # Add SSM Health facilities
    if not facilities.empty:
        print("  Adding SSM Health facilities...")
        
        # Create feature groups
        facility_group = folium.FeatureGroup(name="SSM Health Facilities", show=True)
        hospital_group = folium.FeatureGroup(name="🏥 SSM Health Hospitals", show=True)
        
        # Facility type colors and icons
        facility_colors = {
            'Hospital': '#d62728',      # Red
            'Emergency Department': '#ff7f0e', # Orange
            'Emergency Room': '#ff7f0e', # Orange
            'Emergency Department (ED) / Urgent Care': '#ff7f0e', # Orange
            'Urgent Care': '#ff9933',    # Dark Orange
            'Clinic': '#2ca02c',        # Green
            'Clinic (or Outpatient Clinic)': '#2ca02c',        # Green
            'Imaging Center / Radiology': '#1f77b4',        # Blue
            'Rehabilitation Center (or Physical Therapy)': '#9467bd', # Purple
            'Surgery Center (or Ambulatory Surgery Center – ASC)': '#8c564b', # Brown
            'Pharmacy': '#e377c2',      # Pink
            'Laboratory / Lab': '#17becf', # Cyan
            'Other': '#7f7f7f'          # Gray
        }
        
        # Convert hex colors to Folium color names
        def hex_to_folium_color(hex_color):
            color_map = {
                '#d62728': 'red',
                '#ff7f0e': 'orange', 
                '#ff9933': 'orange',
                '#2ca02c': 'green',
                '#1f77b4': 'blue',
                '#9467bd': 'purple',
                '#8c564b': 'darkred',
                '#e377c2': 'pink',
                '#17becf': 'lightblue',
                '#7f7f7f': 'gray'
            }
            return color_map.get(hex_color, 'red')
        
        # Icon mapping
        icon_mapping = {
            'Hospital': 'plus',
            'Emergency Department': 'exclamation-sign',
            'Emergency Room': 'exclamation-sign',
            'Emergency Department (ED) / Urgent Care': 'exclamation-sign',
            'Urgent Care': 'exclamation-sign',
            'Clinic': 'info-sign',
            'Clinic (or Outpatient Clinic)': 'info-sign',
            'Rehabilitation Center': 'heart',
            'Rehabilitation Center (or Physical Therapy)': 'heart',
            'Imaging Center': 'star',
            'Imaging Center / Radiology': 'star',
            'Surgery Center': 'ok-sign',
            'Surgery Center (or Ambulatory Surgery Center – ASC)': 'ok-sign',
            'Pharmacy': 'leaf',
            'Laboratory': 'cloud',
            'Laboratory / Lab': 'cloud',
            'Other': 'home'
        }
        
        for idx, facility in facilities.iterrows():
            try:
                # Get coordinates
                lat = None
                lng = None
                
                if 'lat' in facility.index and pd.notna(facility['lat']):
                    lat = facility['lat']
                elif 'latitude' in facility.index and pd.notna(facility['latitude']):
                    lat = facility['latitude']
                
                if 'lon' in facility.index and pd.notna(facility['lon']):
                    lng = facility['lon']
                elif 'longitude' in facility.index and pd.notna(facility['longitude']):
                    lng = facility['longitude']
                
                # If no coordinates, try ZIP code lookup
                if pd.isna(lat) or pd.isna(lng):
                    zip_code = facility.get('zip')
                    if pd.notna(zip_code):
                        coords = get_zip_coordinates(zip_code)
                        if coords:
                            lat, lng = coords
                
                if pd.notna(lat) and pd.notna(lng):
                    facility_type = facility.get('facility_type', 'Hospital')
                    hex_color = facility_colors.get(facility_type, facility_colors['Hospital'])
                    folium_color = hex_to_folium_color(hex_color)
                    icon_name = icon_mapping.get(facility_type, 'info-sign')
                    
                    # Create popup content
                    popup_content = f"""
                    <b>{facility.get('name', 'Unknown')}</b><br>
                    Type: {facility_type}<br>
                    Address: {facility.get('street', 'N/A')}<br>
                    City: {facility.get('city', 'N/A')}, {facility.get('state', 'N/A')}<br>
                    ZIP: {facility.get('zip', 'N/A')}<br>
                    MSA: {facility.get('msa_name', 'N/A')}
                    """
                    
                    # Add supplemental attributes if available
                    if 'fte_count' in facility.index and pd.notna(facility['fte_count']):
                        popup_content += f"<br>FTE Count: {facility['fte_count']:,.0f}"
                    if 'discharges (inpatient volume, 2023)' in facility.index and pd.notna(facility['discharges (inpatient volume, 2023)']):
                        popup_content += f"<br>Discharges (2023): {facility['discharges (inpatient volume, 2023)']:,.0f}"
                    
                    # Special handling for hospitals
                    if facility_type == 'Hospital':
                        # Create custom HTML marker for hospitals with pulsing effect
                        hospital_icon_html = f'''
                        <div style="
                            background-color: {hex_color};
                            border: 3px solid white;
                            border-radius: 50%;
                            width: 25px;
                            height: 25px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            box-shadow: 0 0 10px rgba(0,0,0,0.5);
                            animation: pulse 2s infinite;
                        ">
                            <i class="fa fa-plus" style="color: white; font-size: 12px;"></i>
                        </div>
                        <style>
                        @keyframes pulse {{
                            0% {{
                                transform: scale(1);
                                box-shadow: 0 0 10px rgba(0,0,0,0.5);
                            }}
                            50% {{
                                transform: scale(1.2);
                                box-shadow: 0 0 20px rgba(214, 39, 40, 0.8);
                            }}
                            100% {{
                                transform: scale(1);
                                box-shadow: 0 0 10px rgba(0,0,0,0.5);
                            }}
                        }}
                        </style>
                        '''
                        
                        marker = folium.Marker(
                            location=[lat, lng],
                            popup=folium.Popup(popup_content, max_width=350),
                            icon=folium.DivIcon(
                                html=hospital_icon_html,
                                icon_size=(25, 25),
                                icon_anchor=(12, 12)
                            ),
                            tooltip=f"🏥 {facility.get('name', 'Unknown')} (Hospital)"
                        )
                        
                        marker.add_to(hospital_group)
                    else:
                        # Regular facility marker
                        marker = folium.Marker(
                            location=[lat, lng],
                            popup=folium.Popup(popup_content, max_width=300),
                            icon=folium.Icon(color=folium_color, icon=icon_name),
                            tooltip=f"{facility.get('name', 'Unknown')} ({facility_type})"
                        )
                        
                        marker.add_to(facility_group)
            except Exception as e:
                print(f"    ⚠️ Error adding facility {facility.get('name', 'Unknown')}: {e}")
                continue
        
        # Add both groups to map
        facility_group.add_to(m)
        hospital_group.add_to(m)
    
    # Add legend
    print("  Adding legend...")
    
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 400px; max-height: 500px; 
                background: white; border:2px solid grey; z-index:9999; font-size:12px; 
                padding: 10px; overflow-y: auto;">
    <b>Market Share + Attractiveness Overlay</b><br>
    <small>ZIP codes colored by dominant hospital system</small><br>
    <small>Opacity indicates attractiveness score (higher = more opaque)</small><br>
    <div style="margin: 8px 0; padding: 5px; background: #fff3cd; border-left: 3px solid #FF6B35;">
        <b>🏥 SSM Health Markets:</b><br>
        <small>Orange-red outlines indicate ZIP codes where SSM Health is the market leader</small>
    </div>
    <hr style="margin: 10px 0;">
    <b>Hospital System Colors:</b><br>
    '''
    for sys, color in system_colors.items():
        legend_html += f'<div style="display: flex; align-items: center; margin: 2px 0;"><div style="background:{color};width:16px;height:16px;margin-right:8px;border-radius:2px;"></div><span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{sys}</span></div>'
    
    legend_html += '''
    <hr style="margin: 10px 0;">
    <b>🏥 SSM Health Hospitals (Highlighted)</b><br>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <div style="
            background-color: #d62728;
            border: 3px solid white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
            margin-right: 10px;
        ">
            <i class="fa fa-plus" style="color: white; font-size: 10px;"></i>
        </div>
        <span><b>Hospital</b> (Pulsing Effect)</span>
    </div>
    <hr style="margin: 10px 0;">
    <b>Other SSM Health Facilities:</b><br>
    <p><i class="glyphicon glyphicon-exclamation-sign" style="color:#ff7f0e"></i> Emergency Department</p>
    <p><i class="glyphicon glyphicon-exclamation-sign" style="color:#ff9933"></i> Urgent Care</p>
    <p><i class="glyphicon glyphicon-info-sign" style="color:#2ca02c"></i> Clinic</p>
    <p><i class="glyphicon glyphicon-star" style="color:#1f77b4"></i> Imaging Center</p>
    <p><i class="glyphicon glyphicon-heart" style="color:#9467bd"></i> Rehabilitation Center</p>
    <p><i class="glyphicon glyphicon-ok-sign" style="color:#8c564b"></i> Surgery Center</p>
    <p><i class="glyphicon glyphicon-leaf" style="color:#e377c2"></i> Pharmacy</p>
    <p><i class="glyphicon glyphicon-cloud" style="color:#17becf"></i> Laboratory</p>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add title
    title_html = '''
    <div style="position: fixed; top: 10px; left: 50px; width: 450px; 
                background: white; border:2px solid grey; z-index:9999; font-size:14px; 
                padding: 10px;">
    <b>SSM Health - Market Share + Attractiveness + Facilities Overlay</b><br>
    <small>STL/SoIL, Wisconsin, and Oklahoma - 2024 Data</small><br>
    <small>ZIP colors: Dominant hospital system | Opacity: Attractiveness score</small><br>
    <small>🏥 Orange-red outlines: SSM Health market-leading ZIP codes</small>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def main():
    """Main function to create the overlay map"""
    print("🏥 SSM Health Market Share + Attractiveness + Facilities Overlay Map")
    print("=" * 70)
    
    # Load all data
    zip_dominant, zip_market_share, zip_hhi = load_market_share_data()
    zip_attractiveness = load_attractiveness_data()
    facilities = load_ssm_facilities()
    
    # Create overlay map
    m = create_overlay_map(zip_dominant, zip_market_share, zip_hhi, zip_attractiveness, facilities)
    
    # Save map
    output_file = 'ssm_health_proper_overlay_market_share_attractiveness_facilities_map.html'
    m.save(output_file)
    
    print(f"\n✅ Proper overlay map saved to: {output_file}")
    print(f"📊 Map includes:")
    print(f"  - Market share data for {len(zip_dominant)} ZIP codes")
    print(f"  - Attractiveness scores for {len(zip_attractiveness)} ZIP codes")
    print(f"  - {len(facilities)} SSM Health facilities")
    print(f"  - Dual-layer visualization with opacity for attractiveness")
    
    print(f"\n🎉 Proper overlay map completed!")

if __name__ == '__main__':
    main() 