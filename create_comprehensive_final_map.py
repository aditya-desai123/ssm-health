#!/usr/bin/env python3
"""
Create Comprehensive Final Map with ALL States
Combines MN/WI/IL and OK/MO ZIP codes with attractiveness scores
"""

import pandas as pd
import folium
import json
import numpy as np
from folium import plugins
from folium.plugins import Geocoder

def load_and_merge_zip_data():
    """Load and merge all ZIP demographics data, excluding MN"""
    print("📊 Loading ZIP demographics data...")
    
    # Load MN/WI/IL data
    mn_wi_il_data = pd.read_csv('all_mn_wi_il_zip_demographics_scored.csv')
    print(f"  Loaded {len(mn_wi_il_data)} MN/WI/IL ZIP codes (before filtering)")
    
    # Remove MN ZIPs (state == 'MN')
    if 'state' in mn_wi_il_data.columns:
        mn_wi_il_data = mn_wi_il_data[~(mn_wi_il_data['state'] == 'MN')]
    else:
        print("  ⚠️ 'state' column not found in MN/WI/IL data. No MN filtering applied.")
    print(f"  After removing MN: {len(mn_wi_il_data)} WI/IL ZIP codes")
    
    # Load OK/MO data
    ok_mo_data = pd.read_csv('all_ok_mo_zip_demographics_scored.csv')
    print(f"  Loaded {len(ok_mo_data)} OK/MO ZIP codes")
    
    # Combine the datasets
    combined_data = pd.concat([mn_wi_il_data, ok_mo_data], ignore_index=True)
    print(f"  Combined total: {len(combined_data)} ZIP codes (WI, IL, MO, OK)")
    
    return combined_data

def load_ssm_facilities():
    """Load SSM Health facility data and classify hospitals based on masterlist"""
    print("🏥 Loading SSM Health facilities...")
    
    # Load the full facility dataset (now includes the 5 manually added hospitals)
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
    
    # Load the hospitals masterlist to identify which facilities are hospitals
    try:
        hospitals_masterlist = pd.read_csv('hospitals_masterlist.csv', skiprows=2)
        hospitals_masterlist = hospitals_masterlist[hospitals_masterlist['name'].notna()]
        hospitals_masterlist = hospitals_masterlist[hospitals_masterlist['name'].str.strip() != '']
        
        # Create a set of hospital names from masterlist for quick lookup
        hospital_names = set(hospitals_masterlist['name'].str.strip().str.lower())
        print(f"  Loaded {len(hospital_names)} hospital names from masterlist")
        
        # Only change facility type to "Hospital" if name matches masterlist
        def classify_hospitals(row):
            facility_name = str(row.get('name', '')).strip().lower()
            original_type = str(row.get('facility_type', '')).strip()
            
            # Check if this facility name exactly matches a hospital name from masterlist
            if facility_name in hospital_names:
                return 'Hospital'
            # Handle Emergency Department vs Urgent Care classification
            elif original_type.lower() == 'emergency department (ed) / urgent care':
                if 'urgent care' in facility_name:
                    return 'Urgent Care'
                else:
                    return 'Emergency Department'
            # If it was originally "Hospital" but not on masterlist, fallback to Clinic
            elif original_type.lower() == 'hospital':
                return 'Clinic'
            else:
                # Keep the original facility type for everything else
                return original_type
        
        # Apply classification
        facilities['facility_type'] = facilities.apply(classify_hospitals, axis=1)
        
        # Check how many hospitals we found
        hospital_facilities = facilities[facilities['facility_type'] == 'Hospital']
        print(f"  Hospitals found: {len(hospital_facilities)}")
        
        # Debug: Print which facilities are classified as hospitals
        print(f"  Hospitals found ({len(hospital_facilities)}):")
        for _, facility in hospital_facilities.iterrows():
            print(f"    - {facility['name']}")
        
        # Count by type
        type_counts = facilities['facility_type'].value_counts()
        print("  Facility classification:")
        for facility_type, count in type_counts.items():
            print(f"    {facility_type}: {count}")
        
        return facilities
        
    except FileNotFoundError:
        print("  ⚠️ hospitals_masterlist.csv not found, using original facility types")
        return facilities

def create_comprehensive_map(zip_data, facilities):
    """Create comprehensive map with all ZIP codes and facilities"""
    print("🗺️ Creating comprehensive map...")
    
    # Calculate center point for the map (middle of all states)
    center_lat = 39.0  # Rough center of the 5 states
    center_lng = -93.0
    
    # Create base map
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=6,
        tiles='cartodbpositron'
    )
    
    # Add ZIP code polygons with attractiveness scores
    print("  Adding ZIP code polygons...")
    
    # Color mapping for attractiveness scores
    def get_color(score):
        if score >= 80:
            return '#00e600'  # Bright Green - Very Attractive
        elif score >= 60:
            return '#99ff99'  # Light Green - High
        elif score >= 40:
            return '#ffff66'  # Yellow - Medium
        elif score >= 20:
            return '#ff9933'  # Orange - Low
        else:
            return '#ff3333'  # Bright Red - Very Unattractive
    
    # Create a lookup dictionary for ZIP codes to their attractiveness scores
    zip_score_lookup = {}
    for _, row in zip_data.iterrows():
        zip_code = str(row['zip'])
        zip_score_lookup[zip_code] = {
            'score': row['attractiveness_score'],
            'category': row['attractiveness_category'],
            'population': row['total_population'],
            'income': row['median_household_income'],
            'senior_pct': row['senior_population_pct']
        }
    
    # Load existing GeoJSON for WI/IL only (filter out MN polygons)
    try:
        with open('zipcodes_mn_wi_il_scored.geojson', 'r') as f:
            mn_wi_il_geojson = json.load(f)
        # Filter features to only WI and IL
        wi_il_features = []
        for feature in mn_wi_il_geojson['features']:
            statefp = feature['properties'].get('STATEFP10')
            # WI: 55, IL: 17 (FIPS codes)
            if statefp in ('55', '17'):
                wi_il_features.append(feature)
        mn_wi_il_geojson['features'] = wi_il_features
        # Add extra popup fields to WI/IL features
        for feature in mn_wi_il_geojson['features']:
            zip_code = feature['properties'].get('ZCTA5CE10', '')
            data = zip_score_lookup.get(zip_code, {})
            feature['properties']['attractiveness_score'] = data.get('score', 'N/A')
            feature['properties']['attractiveness_category'] = data.get('category', 'N/A')
            feature['properties']['total_population'] = data.get('population', 'N/A')
            feature['properties']['median_household_income'] = data.get('income', 'N/A')
            feature['properties']['senior_population_pct'] = data.get('senior_pct', 'N/A')

        folium.GeoJson(
            mn_wi_il_geojson,
            name='WI/IL ZIP Codes',
            style_function=lambda feature: {
                'fillColor': get_color_from_csv(feature['properties'].get('ZCTA5CE10'), zip_score_lookup),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['ZCTA5CE10'],
                aliases=['ZIP Code'],
                localize=True,
                sticky=False,
                labels=True,
                style="""
                    background-color: #YELLOW;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """
            ),
            popup=folium.GeoJsonPopup(
                fields=['ZCTA5CE10', 'attractiveness_score', 'attractiveness_category', 'total_population', 'median_household_income', 'senior_population_pct'],
                aliases=['ZIP Code', 'Attractiveness Score', 'Category', 'Population', 'Median Income', 'Senior Population %'],
                localize=True,
                labels=True,
                style="background-color: white; border-radius: 5px; padding: 10px;"
            )
        ).add_to(m)
        print("    Added WI/IL ZIP polygons")
    except FileNotFoundError:
        print("    ⚠️ WI/IL GeoJSON not found")
    
    # Add OK/MO ZIP polygons from new GeoJSON
    try:
        with open('zipcodes_mo_ok.geojson', 'r') as f:
            mo_ok_geojson = json.load(f)
        # Add MO/OK ZIP polygons with colors from CSV data and popups
        # Add extra popup fields to MO/OK features
        for feature in mo_ok_geojson['features']:
            zip_code = feature['properties'].get('ZCTA5CE20', '')
            data = zip_score_lookup.get(zip_code, {})
            feature['properties']['attractiveness_score'] = data.get('score', 'N/A')
            feature['properties']['attractiveness_category'] = data.get('category', 'N/A')
            feature['properties']['total_population'] = data.get('population', 'N/A')
            feature['properties']['median_household_income'] = data.get('income', 'N/A')
            feature['properties']['senior_population_pct'] = data.get('senior_pct', 'N/A')

        folium.GeoJson(
            mo_ok_geojson,
            name='MO/OK ZIP Codes',
            style_function=lambda feature: {
                'fillColor': get_color_from_csv(feature['properties'].get('ZCTA5CE20'), zip_score_lookup),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['ZCTA5CE20'],
                aliases=['ZIP Code'],
                localize=True,
                sticky=False,
                labels=True,
                style="""
                    background-color: #YELLOW;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """
            ),
            popup=folium.GeoJsonPopup(
                fields=['ZCTA5CE20', 'attractiveness_score', 'attractiveness_category', 'total_population', 'median_household_income', 'senior_population_pct'],
                aliases=['ZIP Code', 'Attractiveness Score', 'Category', 'Population', 'Median Income', 'Senior Population %'],
                localize=True,
                labels=True,
                style="background-color: white; border-radius: 5px; padding: 10px;"
            )
        ).add_to(m)
        print("    Added MO/OK ZIP polygons")
    except FileNotFoundError:
        print("    ⚠️ MO/OK GeoJSON not found")
    
    # Add SSM Health facilities
    if not facilities.empty:
        print("  Adding SSM Health facilities...")
        
        # Create a feature group for facilities
        facility_group = folium.FeatureGroup(name="SSM Health Facilities", show=True)
        
        # Facility type colors
        facility_colors = {
            'Hospital': '#d62728',      # Red
            'Emergency Department': '#ff7f0e', # Orange
            'Emergency Room': '#ff7f0e', # Orange
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
                '#ff9933': 'orange',    # Dark Orange -> Orange
                '#2ca02c': 'green',
                '#1f77b4': 'blue',
                '#9467bd': 'purple',
                '#8c564b': 'darkred',   # Brown -> Dark Red (valid Folium color)
                '#e377c2': 'pink',
                '#17becf': 'lightblue',
                '#7f7f7f': 'gray'
            }
            mapped_color = color_map.get(hex_color, 'red')
            return mapped_color
        
        for idx, facility in facilities.iterrows():
            try:
                # Get coordinates - try multiple column name variations
                lat = None
                lng = None
                
                # Try different possible column names
                if 'lat' in facility.index and pd.notna(facility['lat']):
                    lat = facility['lat']
                elif 'latitude' in facility.index and pd.notna(facility['latitude']):
                    lat = facility['latitude']
                
                if 'lon' in facility.index and pd.notna(facility['lon']):
                    lng = facility['lon']
                elif 'longitude' in facility.index and pd.notna(facility['longitude']):
                    lng = facility['longitude']
                
                # If no coordinates in the data, try to get them from uszips.csv using ZIP code
                if pd.isna(lat) or pd.isna(lng):
                    zip_code = facility.get('zip')
                    if pd.notna(zip_code):
                        coords = get_zip_coordinates(zip_code)
                        if coords:
                            lat, lng = coords
                
                if pd.notna(lat) and pd.notna(lng):
                    facility_type = facility.get('facility_type', facility.get('type', 'Hospital'))
                    hex_color = facility_colors.get(facility_type, facility_colors['Hospital'])
                    folium_color = hex_to_folium_color(hex_color)
                    
                    # Map facility types to supported Folium icons
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
                    # Get icon based on facility type
                    icon_name = icon_mapping.get(facility_type, 'info-sign')
                    
                    # Create popup content with supplemental attributes
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
                    if 'patient_days (2023)' in facility.index and pd.notna(facility['patient_days (2023)']):
                        popup_content += f"<br>Patient Days (2023): {facility['patient_days (2023)']:,.0f}"
                    if 'cmi (12/2023)' in facility.index and pd.notna(facility['cmi (12/2023)']):
                        popup_content += f"<br>CMI (12/2023): {facility['cmi (12/2023)']:.2f}"
                    
                    # Create facility marker
                    marker = folium.Marker(
                        location=[lat, lng],
                        popup=folium.Popup(popup_content, max_width=300),
                        icon=folium.Icon(color=folium_color, icon=icon_name),
                        tooltip=f"{facility.get('name', 'Unknown')} ({facility_type})"
                    )
                    
                    # Add marker to facility group
                    marker.add_to(facility_group)
            except Exception as e:
                print(f"    ⚠️ Error adding facility {facility.get('name', 'Unknown')}: {e}")
                continue
        
        # Add facility group to map
        facility_group.add_to(m)
    
    # Add custom search functionality for markers
    print("  Adding search functionality...")
    
    # Create a list of all facility data for search
    facility_search_data = []
    for _, facility in facilities.iterrows():
        try:
            lat = None
            lng = None
            
            # Get coordinates
            if 'lat' in facility.index and pd.notna(facility['lat']):
                lat = facility['lat']
            elif 'latitude' in facility.index and pd.notna(facility['latitude']):
                lat = facility['latitude']
            
            if 'lon' in facility.index and pd.notna(facility['lon']):
                lng = facility['lon']
            elif 'longitude' in facility.index and pd.notna(facility['longitude']):
                lng = facility['longitude']
            
            if pd.isna(lat) or pd.isna(lng):
                zip_code = facility.get('zip')
                if pd.notna(zip_code):
                    coords = get_zip_coordinates(zip_code)
                    if coords:
                        lat, lng = coords
            
            if pd.notna(lat) and pd.notna(lng):
                facility_search_data.append({
                    'name': str(facility.get('name', 'Unknown')),
                    'type': str(facility.get('facility_type', 'Unknown')),
                    'zip': str(facility.get('zip', 'N/A')),
                    'city': str(facility.get('city', 'N/A')),
                    'state': str(facility.get('state', 'N/A')),
                    'lat': lat,
                    'lng': lng
                })
        except:
            continue
    
    # Add custom search box that works with the original markers
    search_html = f'''
    <div style="position: fixed; top: 10px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
        <input id="facilitySearch" type="text" placeholder="Search facilities by name, type, or ZIP..." style="width: 300px; padding: 8px; border: 1px solid #ccc; border-radius: 3px;">
        <button onclick="clearSearch()" style="margin-left: 5px; padding: 8px; background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 3px; cursor: pointer;">Clear</button>
        <div id="searchResults" style="max-height: 200px; overflow-y: auto; margin-top: 5px; border: 1px solid #ddd; border-radius: 3px; background-color: white;"></div>
    </div>
    
    <script>
    var facilitySearchIndex = {facility_search_data};
    var currentSearchResults = [];
    var mapInstance = null;
    
    // Function to find the map instance
    function findMapInstance() {{
        if (mapInstance) return mapInstance;
        
        // Look for the map in various ways
        for (let key in window) {{
            if (window[key] && typeof window[key].setView === 'function') {{
                mapInstance = window[key];
                console.log('Found map instance:', key);
                return mapInstance;
            }}
        }}
        
        // Try to find by leaflet ID
        const mapElements = document.querySelectorAll('[id*="map"]');
        for (let element of mapElements) {{
            if (element._leaflet_id) {{
                mapInstance = element;
                console.log('Found map element by ID');
                return mapInstance;
            }}
        }}
        
        console.log('No map instance found');
        return null;
    }}
    
    function searchFacilities() {{
        const searchTerm = document.getElementById('facilitySearch').value.toLowerCase();
        const resultsDiv = document.getElementById('searchResults');
        
        if (searchTerm.length < 2) {{
            resultsDiv.innerHTML = '';
            return;
        }}
        
        const results = facilitySearchIndex.filter(facility => 
            facility.name.toLowerCase().includes(searchTerm) ||
            facility.type.toLowerCase().includes(searchTerm) ||
            facility.zip.toLowerCase().includes(searchTerm) ||
            facility.city.toLowerCase().includes(searchTerm)
        ).slice(0, 10);
        
        currentSearchResults = results;
        
        if (results.length > 0) {{
            resultsDiv.innerHTML = '<div style="padding: 5px; background-color: #f8f9fa; border-bottom: 1px solid #ddd; font-weight: bold;">Search Results:</div>';
            results.forEach((facility, index) => {{
                resultsDiv.innerHTML += `<div style="cursor: pointer; padding: 8px; border-bottom: 1px solid #eee; hover:background-color: #f5f5f5;" onmouseover="this.style.backgroundColor='#f5f5f5'" onmouseout="this.style.backgroundColor='white'" onclick="selectFacility(${{index}})"><strong>${{facility.name}}</strong><br><small>${{facility.type}} • ${{facility.city}}, ${{facility.state}} • ZIP: ${{facility.zip}}</small></div>`;
            }});
        }} else {{
            resultsDiv.innerHTML = '<div style="padding: 10px; color: #666; font-style: italic;">No facilities found</div>';
        }}
    }}
    
    function selectFacility(index) {{
        const facility = currentSearchResults[index];
        const map = findMapInstance();
        
        if (facility && map) {{
            console.log('Selecting facility:', facility.name);
            console.log('Setting view to:', [facility.lat, facility.lng]);
            
            // Fly to the facility location
            map.setView([facility.lat, facility.lng], 15);
            
            // Clear search
            document.getElementById('facilitySearch').value = '';
            document.getElementById('searchResults').innerHTML = '';
        }} else {{
            console.log('Failed to select facility. Facility:', facility, 'Map:', map);
        }}
    }}
    
    function clearSearch() {{
        document.getElementById('facilitySearch').value = '';
        document.getElementById('searchResults').innerHTML = '';
    }}
    
    // Initialize search when page loads
    document.addEventListener('DOMContentLoaded', function() {{
        const searchInput = document.getElementById('facilitySearch');
        if (searchInput) {{
            searchInput.addEventListener('input', searchFacilities);
            console.log('Search input initialized');
        }}
        
        // Try to find map instance after a short delay
        setTimeout(findMapInstance, 1000);
    }});
    </script>
    '''
    
    m.get_root().html.add_child(folium.Element(search_html))
    
    # Add legend
    print("  Adding legend...")
    
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 350px; height: 400px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px; overflow-y: auto;">
    <p><b>Healthcare Attractiveness Score</b></p>
    <p><i class="fa fa-square" style="color:#00e600"></i> Very Attractive (80-100)</p>
    <p><i class="fa fa-square" style="color:#99ff99"></i> High (60-79)</p>
    <p><i class="fa fa-square" style="color:#ffff66"></i> Medium (40-59)</p>
    <p><i class="fa fa-square" style="color:#ff9933"></i> Low (20-39)</p>
    <p><i class="fa fa-square" style="color:#ff3333"></i> Very Unattractive (0-19)</p>
    <p><b>SSM Health Facilities</b></p>
    <p><i class="glyphicon glyphicon-plus" style="color:#d62728"></i> Hospital</p>
    <p><i class="glyphicon glyphicon-exclamation-sign" style="color:#ff7f0e"></i> Emergency Department</p>
    <p><i class="glyphicon glyphicon-exclamation-sign" style="color:#ff9933"></i> Urgent Care</p>
    <p><i class="glyphicon glyphicon-info-sign" style="color:#2ca02c"></i> Clinic</p>
    <p><i class="glyphicon glyphicon-star" style="color:#1f77b4"></i> Imaging Center / Radiology</p>
    <p><i class="glyphicon glyphicon-heart" style="color:#9467bd"></i> Rehabilitation Center</p>
    <p><i class="glyphicon glyphicon-ok-sign" style="color:#8c564b"></i> Surgery Center</p>
    <p><i class="glyphicon glyphicon-leaf" style="color:#e377c2"></i> Pharmacy</p>
    <p><i class="glyphicon glyphicon-cloud" style="color:#17becf"></i> Laboratory / Lab</p>
    <p><i class="glyphicon glyphicon-home" style="color:#7f7f7f"></i> Other</p>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def get_color_from_csv(zip_code, zip_score_lookup):
    """Get color for ZIP code based on CSV data"""
    if zip_code in zip_score_lookup:
        score = zip_score_lookup[zip_code]['score']
        if score >= 80:
            return '#00e600'  # Bright Green - Very Attractive
        elif score >= 60:
            return '#99ff99'  # Light Green - High
        elif score >= 40:
            return '#ffff66'  # Yellow - Medium
        elif score >= 20:
            return '#ff9933'  # Orange - Low
        else:
            return '#ff3333'  # Bright Red - Very Unattractive
    else:
        return '#gray'  # Gray for ZIP codes not in CSV

def get_zip_coordinates(zip_code):
    """Get coordinates for a ZIP code from uszips.csv"""
    try:
        # Load uszips.csv if not already loaded
        if not hasattr(get_zip_coordinates, 'uszips_data'):
            get_zip_coordinates.uszips_data = pd.read_csv('uszips.csv')
        
        # Find the ZIP code
        zip_row = get_zip_coordinates.uszips_data[
            get_zip_coordinates.uszips_data['zip'] == str(zip_code)
        ]
        
        if not zip_row.empty:
            return zip_row.iloc[0]['lat'], zip_row.iloc[0]['lng']
        return None
    except:
        return None

def main():
    """Main function to create comprehensive map"""
    print("🏥 SSM Health Comprehensive Final Map")
    print("=" * 50)
    
    # Load data
    zip_data = load_and_merge_zip_data()
    facilities = load_ssm_facilities()
    
    # Create map
    m = create_comprehensive_map(zip_data, facilities)
    
    # Save map
    output_file = 'ssm_health_comprehensive_final_map.html'
    m.save(output_file)
    
    print(f"\n✅ Comprehensive map saved to: {output_file}")
    print(f"📊 Map includes:")
    print(f"  - {len(zip_data)} ZIP codes with attractiveness scores")
    print(f"  - {len(facilities)} SSM Health facilities")
    print(f"  - All 5 states: MN, WI, IL, OK, MO")
    
    print(f"\n🎉 Comprehensive final map completed!")

if __name__ == "__main__":
    main() 