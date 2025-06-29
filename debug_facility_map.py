#!/usr/bin/env python3
"""
Debug version of SSM Health Facility Map to ensure markers are visible
"""

import pandas as pd
import folium
from folium import plugins
import random

def create_debug_map():
    """Create a simple debug map to test marker visibility"""
    
    # Load the data
    df = pd.read_csv('ssm_health_locations_with_income_with_age_demographics.csv')
    
    # Clean data
    df = df.dropna(subset=['name', 'city', 'state'])
    df['type'] = df['type'].fillna('Unknown')
    
    # Create facility categories
    def categorize_facility(facility_type):
        if pd.isna(facility_type):
            return 'Unknown'
        facility_type = str(facility_type).lower()
        if any(word in facility_type for word in ['hospital', 'medical center']):
            return 'Hospital'
        elif any(word in facility_type for word in ['urgent', 'express', 'walk']):
            return 'Urgent Care'
        elif any(word in facility_type for word in ['pharmacy', 'prescription']):
            return 'Pharmacy'
        elif any(word in facility_type for word in ['imaging', 'radiology', 'mammography']):
            return 'Imaging'
        elif any(word in facility_type for word in ['laboratory', 'lab']):
            return 'Laboratory'
        elif any(word in facility_type for word in ['therapy', 'rehabilitation']):
            return 'Therapy'
        elif any(word in facility_type for word in ['cancer', 'oncology']):
            return 'Cancer Care'
        elif any(word in facility_type for word in ['eye', 'ophthalmology']):
            return 'Eye Care'
        elif any(word in facility_type for word in ['hospice']):
            return 'Hospice'
        else:
            return 'Primary Care'
    
    df['facility_category'] = df['type'].apply(categorize_facility)
    
    # Predefined coordinates for major cities
    city_coords = {
        'Madison, WI': (43.0731, -89.4012),
        'Milwaukee, WI': (43.0389, -87.9065),
        'Chicago, IL': (41.8781, -87.6298),
        'St. Louis, MO': (38.6270, -90.1994),
        'Oklahoma City, OK': (35.4676, -97.5164),
        'Janesville, WI': (42.6828, -89.0187),
        'Fond du Lac, WI': (43.7730, -88.4470),
        'Rockford, IL': (42.2711, -89.0940),
        'Freeport, IL': (42.2967, -89.6212),
        'Centralia, IL': (38.5250, -89.1334),
        'Mount Vernon, IL': (38.3173, -88.9031),
        'Columbia, IL': (38.4437, -90.2012),
        'Benton, IL': (37.9967, -88.9203),
        'Fenton, MO': (38.5139, -90.4432),
        'Salem, IL': (38.6269, -88.9456),
        'Lena, IL': (42.3794, -89.8223),
        'Durand, IL': (42.4336, -89.3318),
        'Maryville, IL': (38.7231, -89.9559),
        'Wentzville, MO': (38.8114, -90.8529),
        'O\'Fallon, MO': (38.8106, -90.6998),
        'Kirkwood, MO': (38.5834, -90.4068),
        'Chesterfield, MO': (38.6631, -90.5771),
        'Ballwin, MO': (38.5950, -90.5462),
        'Jefferson City, MO': (38.5767, -92.1735),
        'Tipton, MO': (38.6556, -92.7799),
        'Springfield, MO': (37.2090, -93.2923),
        'Shawnee, OK': (35.3273, -96.9253),
        'Edmond, OK': (35.6528, -97.4781),
        'Midwest City, OK': (35.4495, -97.3967),
        'Moore, OK': (35.3395, -97.4867),
        'Mustang, OK': (35.3842, -97.7245),
        'Purcell, OK': (35.0137, -97.3611),
        'El Reno, OK': (35.5323, -97.9550),
        'Blanchard, OK': (35.1378, -97.6589),
        'Pauls Valley, OK': (34.7401, -97.2211),
        'Tecumseh, OK': (35.2578, -96.9361),
        'Choctaw, OK': (35.4795, -97.2706),
        'Okemah, OK': (35.4326, -96.3056),
        'Chandler, OK': (35.7017, -96.8809),
        'Enid, OK': (36.3956, -97.8784),
        'Seminole, OK': (35.2245, -96.6706),
        'McLoud, OK': (35.4362, -97.0914),
        'Harrah, OK': (35.4895, -97.1636),
    }
    
    def get_coordinates(city, state):
        key = f"{city}, {state}"
        coords = city_coords.get(key)
        if coords:
            # Add small random offset to prevent overlapping
            lat_offset = random.uniform(-0.005, 0.005)
            lon_offset = random.uniform(-0.005, 0.005)
            return (coords[0] + lat_offset, coords[1] + lon_offset)
        return None
    
    # Color mapping
    color_map = {
        'Hospital': 'red',
        'Primary Care': 'blue',
        'Urgent Care': 'orange',
        'Pharmacy': 'green',
        'Imaging': 'purple',
        'Laboratory': 'darkred',
        'Therapy': 'darkblue',
        'Cancer Care': 'darkgreen',
        'Eye Care': 'darkpurple',
        'Hospice': 'gray',
        'Unknown': 'lightgray'
    }
    
    # Create the map
    m = folium.Map(
        location=[39.8283, -98.5795],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # Add all facilities directly to the map (no feature groups initially)
    facilities_added = 0
    
    for idx, row in df.iterrows():
        try:
            # Get coordinates
            coords = get_coordinates(row['city'], row['state'])
            
            if coords:
                lat, lon = coords
                
                # Create simple popup
                popup_text = f"""
                <div style="width: 250px;">
                    <h4>{row['name']}</h4>
                    <p><strong>Type:</strong> {row['facility_category']}</p>
                    <p><strong>Address:</strong> {row['street']}, {row['city']}, {row['state']}</p>
                    <p><strong>MSA:</strong> {row['msa_name']}</p>
                    <p><strong>Income:</strong> ${row['msa_median_household_income']:,.0f}</p>
                </div>
                """
                
                # Get color
                color = color_map.get(row['facility_category'], 'lightgray')
                
                # Create marker
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_text, max_width=300),
                    tooltip=f"{row['name']} - {row['facility_category']}",
                    icon=folium.Icon(color=color, icon='info-sign')
                ).add_to(m)
                
                facilities_added += 1
                
                if facilities_added % 100 == 0:
                    print(f"Added {facilities_added} facilities...")
                
        except Exception as e:
            print(f"Error adding facility {row['name']}: {e}")
            continue
    
    # Add a simple legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 300px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px; overflow-y: auto;">
    <h4>Facility Types</h4>
    <p><i class="fa fa-map-marker fa-2x" style="color:red"></i> Hospital</p>
    <p><i class="fa fa-map-marker fa-2x" style="color:blue"></i> Primary Care</p>
    <p><i class="fa fa-map-marker fa-2x" style="color:orange"></i> Urgent Care</p>
    <p><i class="fa fa-map-marker fa-2x" style="color:green"></i> Pharmacy</p>
    <p><i class="fa fa-map-marker fa-2x" style="color:purple"></i> Imaging</p>
    <p><i class="fa fa-map-marker fa-2x" style="color:darkred"></i> Laboratory</p>
    <p><i class="fa fa-map-marker fa-2x" style="color:darkblue"></i> Therapy</p>
    <p><i class="fa fa-map-marker fa-2x" style="color:darkgreen"></i> Cancer Care</p>
    <p><i class="fa fa-map-marker fa-2x" style="color:darkpurple"></i> Eye Care</p>
    <p><i class="fa fa-map-marker fa-2x" style="color:gray"></i> Hospice</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map
    output_file = 'ssm_health_debug_map.html'
    m.save(output_file)
    
    print(f"✅ Debug map created successfully!")
    print(f"📊 Added {facilities_added} facilities to the map")
    print(f"🗺️ Map saved to: {output_file}")
    
    return m

if __name__ == "__main__":
    create_debug_map() 