#!/usr/bin/env python3
"""
Add OK/MO ZIP codes to the existing final map
"""

import pandas as pd
import folium
import json
import numpy as np

def load_ok_mo_data():
    """Load OK/MO ZIP demographics with scores"""
    print("📊 Loading OK/MO ZIP demographics data...")
    
    ok_mo_data = pd.read_csv('all_ok_mo_zip_demographics_scored.csv')
    print(f"  Loaded {len(ok_mo_data)} OK/MO ZIP codes")
    
    return ok_mo_data

def load_ssm_facilities():
    """Load SSM Health facility data"""
    print("🏥 Loading SSM Health facilities...")
    
    try:
        facilities = pd.read_csv('ssm_health_locations_with_census_zip_demographics.csv')
        print(f"  Loaded {len(facilities)} facilities")
        return facilities
    except FileNotFoundError:
        print("  ⚠️ No facility data found")
        return pd.DataFrame()

def add_ok_mo_to_existing_map():
    """Add OK/MO data to the existing final map"""
    print("🗺️ Adding OK/MO data to existing final map...")
    
    # Load the existing map
    try:
        with open('ssm_health_final_zip_attractiveness_map.html', 'r') as f:
            existing_map_html = f.read()
        
        # Create a new map with the same center and zoom
        center_lat = 39.0
        center_lng = -93.0
        
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=6,
            tiles='cartodbpositron'
        )
        
        # Load existing GeoJSON for MN/WI/IL
        with open('zipcodes_mn_wi_il_scored.geojson', 'r') as f:
            mn_wi_il_geojson = json.load(f)
        
        # Add MN/WI/IL ZIP polygons
        folium.GeoJson(
            mn_wi_il_geojson,
            name='MN/WI/IL ZIP Codes',
            style_function=lambda feature: {
                'fillColor': feature['properties'].get('attractiveness_color', '#gray'),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['ZCTA5CE10', 'attractiveness_score'],
                aliases=['ZIP Code', 'Attractiveness Score'],
                localize=True,
                sticky=False,
                labels=True,
                style="""
                    background-color: #YELLOW;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """
            )
        ).add_to(m)
        print("    Added MN/WI/IL ZIP polygons")
        
        # Load and add OK/MO data
        ok_mo_data = load_ok_mo_data()
        
        # Color mapping for attractiveness scores
        def get_color(score):
            if score >= 80:
                return '#1f77b4'  # Dark blue - Very High
            elif score >= 60:
                return '#ff7f0e'  # Orange - High
            elif score >= 40:
                return '#2ca02c'  # Green - Medium
            elif score >= 20:
                return '#d62728'  # Red - Low
            else:
                return '#9467bd'  # Purple - Very Low
        
        # Add OK/MO ZIP codes as markers
        print("  Adding OK/MO ZIP code markers...")
        
        # Load uszips.csv for coordinates
        uszips_data = pd.read_csv('uszips.csv', low_memory=False)
        
        # Sample some OK/MO ZIP codes to avoid overcrowding
        ok_mo_sample = ok_mo_data.sample(min(300, len(ok_mo_data)))
        
        for _, row in ok_mo_sample.iterrows():
            try:
                # Get coordinates from uszips.csv
                zip_row = uszips_data[uszips_data['zip'] == str(row['zip'])]
                
                if not zip_row.empty:
                    lat = zip_row.iloc[0]['lat']
                    lng = zip_row.iloc[0]['lng']
                    
                    # Create marker
                    folium.CircleMarker(
                        location=[lat, lng],
                        radius=4,
                        color=get_color(row['attractiveness_score']),
                        fill=True,
                        fillColor=get_color(row['attractiveness_score']),
                        fillOpacity=0.8,
                        popup=folium.Popup(
                            f"""
                            <b>ZIP Code: {row['zip']}</b><br>
                            Attractiveness Score: {row['attractiveness_score']:.1f}<br>
                            Category: {row['attractiveness_category']}<br>
                            Population: {row['total_population']:,}<br>
                            Median Income: ${row['median_household_income']:,}<br>
                            Senior Population: {row['senior_population_pct']:.1f}%
                            """,
                            max_width=300
                        )
                    ).add_to(m)
            except Exception as e:
                continue
        
        # Add SSM Health facilities
        facilities = load_ssm_facilities()
        if not facilities.empty:
            print("  Adding SSM Health facilities...")
            
            for _, facility in facilities.iterrows():
                try:
                    # Get coordinates
                    lat = facility.get('latitude', facility.get('lat'))
                    lng = facility.get('longitude', facility.get('lng'))
                    
                    if pd.notna(lat) and pd.notna(lng):
                        facility_type = facility.get('type', 'Other')
                        
                        # Create facility marker
                        folium.Marker(
                            location=[lat, lng],
                            popup=folium.Popup(
                                f"""
                                <b>{facility.get('name', 'Unknown')}</b><br>
                                Type: {facility_type}<br>
                                Address: {facility.get('address', 'N/A')}<br>
                                Phone: {facility.get('phone', 'N/A')}<br>
                                MSA: {facility.get('msa', 'N/A')}
                                """,
                                max_width=300
                            ),
                            icon=folium.Icon(color='red', icon='plus')
                        ).add_to(m)
                except:
                    continue
        
        # Add legend
        print("  Adding legend...")
        
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 300px; height: 220px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Healthcare Attractiveness Score</b></p>
        <p><i class="fa fa-circle" style="color:#1f77b4"></i> Very High (80-100)</p>
        <p><i class="fa fa-circle" style="color:#ff7f0e"></i> High (60-79)</p>
        <p><i class="fa fa-circle" style="color:#2ca02c"></i> Medium (40-59)</p>
        <p><i class="fa fa-circle" style="color:#d62728"></i> Low (20-39)</p>
        <p><i class="fa fa-circle" style="color:#9467bd"></i> Very Low (0-19)</p>
        <p><b>SSM Facilities</b></p>
        <p><i class="fa fa-plus" style="color:red"></i> SSM Health Facility</p>
        <p><b>Coverage</b></p>
        <p>• MN/WI/IL: ZIP polygons</p>
        <p>• OK/MO: ZIP markers</p>
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m
        
    except FileNotFoundError:
        print("  ⚠️ Existing final map not found")
        return None

def main():
    """Main function to add OK/MO to final map"""
    print("🏥 Adding OK/MO to SSM Health Final Map")
    print("=" * 50)
    
    # Create map with OK/MO data added
    m = add_ok_mo_to_existing_map()
    
    if m:
        # Save the comprehensive map
        output_file = 'ssm_health_comprehensive_final_map.html'
        m.save(output_file)
        
        print(f"\n✅ Comprehensive map saved to: {output_file}")
        print(f"📊 Map includes:")
        print(f"  - MN/WI/IL ZIP polygons with attractiveness scores")
        print(f"  - OK/MO ZIP markers with attractiveness scores")
        print(f"  - All SSM Health facilities")
        print(f"  - All 5 states: MN, WI, IL, OK, MO")
        
        print(f"\n🎉 Comprehensive final map completed!")
    else:
        print("❌ Failed to create comprehensive map")

if __name__ == "__main__":
    main() 