#!/usr/bin/env python3
"""
Color-coded SSM Health Facility Map with distinct icons and colors for each facility type
"""

import pandas as pd
import folium
from folium import plugins
import random

def create_color_coded_map():
    """Create a facility map with proper color coding and distinct icons"""
    
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
    
    # Color and icon mapping - using distinct colors and icons
    facility_style = {
        'Hospital': {'color': 'red', 'icon': 'plus'},
        'Primary Care': {'color': 'blue', 'icon': 'user-md'},
        'Urgent Care': {'color': 'orange', 'icon': 'exclamation-triangle'},
        'Pharmacy': {'color': 'green', 'icon': 'pills'},
        'Imaging': {'color': 'purple', 'icon': 'eye'},
        'Laboratory': {'color': 'cadetblue', 'icon': 'flask'},
        'Therapy': {'color': 'darkblue', 'icon': 'heartbeat'},
        'Cancer Care': {'color': 'darkgreen', 'icon': 'shield-alt'},
        'Eye Care': {'color': 'darkpurple', 'icon': 'eye'},
        'Hospice': {'color': 'gray', 'icon': 'home'},
        'Unknown': {'color': 'lightgray', 'icon': 'question'}
    }
    
    # Create the map
    m = folium.Map(
        location=[39.8283, -98.5795],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # Add tile layers
    folium.TileLayer(
        tiles='CartoDB positron',
        name='Light Map',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB dark_matter',
        name='Dark Map',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Create feature groups for different facility types
    facility_groups = {}
    facility_categories = df['facility_category'].unique()
    
    for category in facility_categories:
        count = len(df[df['facility_category'] == category])
        facility_groups[category] = folium.FeatureGroup(
            name=f"{category} ({count})",
            overlay=True,
            control=True
        )
    
    # Add facilities to the map
    facilities_added = 0
    
    for idx, row in df.iterrows():
        try:
            # Get coordinates
            coords = get_coordinates(row['city'], row['state'])
            
            if coords:
                lat, lon = coords
                
                # Create detailed popup
                popup_html = f"""
                <div style="width: 300px; font-family: Arial, sans-serif;">
                    <h3 style="color: #2c3e50; margin-bottom: 10px;">{row['name']}</h3>
                    
                    <div style="background-color: #ecf0f1; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        <h4 style="color: #34495e; margin: 0 0 5px 0;">📍 Location</h4>
                        <p style="margin: 2px 0;"><strong>Address:</strong> {row['street']}, {row['city']}, {row['state']} {row['zip']}</p>
                        <p style="margin: 2px 0;"><strong>MSA:</strong> {row['msa_name']}</p>
                    </div>
                    
                    <div style="background-color: #e8f5e8; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        <h4 style="color: #27ae60; margin: 0 0 5px 0;">🏥 Facility Details</h4>
                        <p style="margin: 2px 0;"><strong>Type:</strong> {row['facility_category']}</p>
                        <p style="margin: 2px 0;"><strong>Specialty:</strong> {row['specialty']}</p>
                    </div>
                    
                    <div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        <h4 style="color: #856404; margin: 0 0 5px 0;">💰 Economic Profile</h4>
                        <p style="margin: 2px 0;"><strong>Median Income:</strong> ${row['msa_median_household_income']:,.0f}</p>
                        <p style="margin: 2px 0;"><strong>MSA Population:</strong> {row['msa_population']:,.0f}</p>
                    </div>
                    
                    <div style="background-color: #d1ecf1; padding: 10px; border-radius: 5px;">
                        <h4 style="color: #0c5460; margin: 0 0 5px 0;">👥 Demographics</h4>
                        <p style="margin: 2px 0;"><strong>Median Age:</strong> {row['median_age']:.1f} years</p>
                        <p style="margin: 2px 0;"><strong>Under 18:</strong> {row['pct_under_18']:.1f}%</p>
                        <p style="margin: 2px 0;"><strong>65+:</strong> {row['pct_65_plus']:.1f}%</p>
                    </div>
                </div>
                """
                
                # Get style for this facility type
                style = facility_style.get(row['facility_category'], {'color': 'lightgray', 'icon': 'question'})
                
                # Create marker with custom icon
                marker = folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=350),
                    tooltip=f"{row['name']} - {row['facility_category']}",
                    icon=folium.Icon(color=style['color'], icon=style['icon'], prefix='fa')
                )
                
                # Add to appropriate feature group
                facility_groups[row['facility_category']].add_child(marker)
                
                facilities_added += 1
                
                if facilities_added % 100 == 0:
                    print(f"Added {facilities_added} facilities...")
                
        except Exception as e:
            print(f"Error adding facility {row['name']}: {e}")
            continue
    
    # Add all feature groups to the map
    for group in facility_groups.values():
        m.add_child(group)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add fullscreen option
    plugins.Fullscreen().add_to(m)
    
    # Add measure tool
    plugins.MeasureControl().add_to(m)
    
    # Add minimap
    minimap = plugins.MiniMap()
    m.add_child(minimap)
    
    # Add scrollable legend with better styling and icons
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 320px; max-height: 500px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px; overflow-y: auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    <h4 style="margin-top: 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">SSM Health Facility Map Legend</h4>
    
    <div style="margin-bottom: 15px;">
        <h5 style="color: #34495e; margin: 5px 0;">🏥 Facility Types:</h5>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-plus fa-2x" style="color:red; margin-right: 8px;"></i>
            <span>Hospital</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-user-md fa-2x" style="color:blue; margin-right: 8px;"></i>
            <span>Primary Care</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-exclamation-triangle fa-2x" style="color:orange; margin-right: 8px;"></i>
            <span>Urgent Care</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-pills fa-2x" style="color:green; margin-right: 8px;"></i>
            <span>Pharmacy</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-eye fa-2x" style="color:purple; margin-right: 8px;"></i>
            <span>Imaging</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-flask fa-2x" style="color:cadetblue; margin-right: 8px;"></i>
            <span>Laboratory</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-heartbeat fa-2x" style="color:darkblue; margin-right: 8px;"></i>
            <span>Therapy</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-shield-alt fa-2x" style="color:darkgreen; margin-right: 8px;"></i>
            <span>Cancer Care</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-eye fa-2x" style="color:darkpurple; margin-right: 8px;"></i>
            <span>Eye Care</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-home fa-2x" style="color:gray; margin-right: 8px;"></i>
            <span>Hospice</span>
        </div>
    </div>
    
    <div style="font-size: 12px; color: #7f8c8d; border-top: 1px solid #ecf0f1; padding-top: 8px;">
        💡 Use the layer control (top right) to filter by facility type
    </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map
    output_file = 'ssm_health_color_coded_map.html'
    m.save(output_file)
    
    print(f"✅ Color-coded facility map created successfully!")
    print(f"📊 Added {facilities_added} facilities to the map")
    print(f"🎨 Each facility type has a distinct color and icon")
    print(f"🗺️ Map saved to: {output_file}")
    print(f"🎛️ Use the layer control in the top right to filter by facility type")
    
    return m

if __name__ == "__main__":
    create_color_coded_map() 