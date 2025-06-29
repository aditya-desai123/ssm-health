#!/usr/bin/env python3
"""
Simple Color-coded SSM Health Facility Map - All markers visible by default
"""

import pandas as pd
import folium
from folium import plugins
import random

def clean_msa_names(df, msa_column='msa_name'):
    """
    Clean MSA names by replacing "Micropolitan Statistical Area" with "Metropolitan Statistical Area"
    
    Args:
        df: pandas DataFrame
        msa_column: name of the column containing MSA names
    
    Returns:
        DataFrame with cleaned MSA names
    """
    if msa_column in df.columns:
        # Replace "Micropolitan Statistical Area" with "Metropolitan Statistical Area"
        df[msa_column] = df[msa_column].str.replace(
            'Micropolitan Statistical Area', 
            'Metropolitan Statistical Area', 
            case=False
        )
        print(f"✅ Cleaned MSA names in column '{msa_column}'")
    else:
        print(f"⚠️ Column '{msa_column}' not found in DataFrame")
    
    return df

def create_simple_color_coded_map():
    """Create a simple facility map with all markers visible"""
    
    # Load the data
    df = pd.read_csv('ssm_health_locations_with_income_with_age_demographics.csv')
    
    # Load the hospital masterlist
    hospitals_df = pd.read_csv('hospitals_masterlist.csv', skiprows=2)
    
    # Clean MSA names in both dataframes
    df = clean_msa_names(df, 'msa_name')
    hospitals_df = clean_msa_names(hospitals_df, 'msa_name')
    
    # Clean data
    df = df.dropna(subset=['name', 'city', 'state'])
    df['facility_type'] = df['facility_type'].fillna('Unknown')
    
    # Create improved facility categorization
    def categorize_facility(row):
        name = str(row['name']).lower()
        current_type = str(row['facility_type']).lower()
        
        # Emergency Department (ED/ER) - if "Emergency Room" in name
        if 'emergency room' in name:
            return 'Emergency Department (ED/ER)'
        # Urgent Care - if "Urgent Care" in name (and not Emergency Room)
        if 'urgent care' in name:
            return 'Urgent Care'
        # Emergency Department (ED/ER) - if previous type is ED/Urgent Care
        if current_type == 'emergency department (ed) / urgent care':
            return 'Emergency Department (ED/ER)'
        # Keep existing categorization for other types
        return row['facility_type']
    
    # Apply the new categorization
    df['facility_type'] = df.apply(categorize_facility, axis=1)
    
    # Print facility type distribution
    print("Facility type distribution:")
    print(df['facility_type'].value_counts())
    
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
        'St. Charles, MO': (38.7881, -90.4974),
        'Fond Du Lac, WI': (43.7730, -88.4470),
        'Waupun, WI': (43.6333, -88.7295),
        'Baraboo, WI': (43.4711, -89.7443),
        'Ripon, WI': (43.8422, -88.8359),
        'Bridgeton, MO': (38.7506, -90.4115),
        'Monroe, WI': (42.6011, -89.6385),
        'Lake St. Louis, MO': (38.7976, -90.7857),
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
    
    # Color and icon mapping - using only Folium-supported colors
    facility_style = {
        'Hospital': {'color': 'red', 'icon': 'plus'},
        'Emergency Department (ED/ER)': {'color': 'darkred', 'icon': 'exclamation-triangle'},
        'Urgent Care': {'color': 'orange', 'icon': 'clock'},
        'Clinic (or Outpatient Clinic)': {'color': 'blue', 'icon': 'user-md'},
        'Pharmacy': {'color': 'green', 'icon': 'pills'},
        'Imaging Center / Radiology': {'color': 'purple', 'icon': 'eye'},
        'Laboratory / Lab': {'color': 'red', 'icon': 'flask'},
        'Rehabilitation Center (or Physical Therapy)': {'color': 'blue', 'icon': 'heartbeat'},
        'Surgery Center (or Ambulatory Surgery Center – ASC)': {'color': 'green', 'icon': 'shield-alt'},
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
    
    facilities_added = 0
    facility_counts = {}
    all_states = set()
    
    # --- Add hospitals from masterlist ---
    for idx, row in hospitals_df.iterrows():
        try:
            coords = get_coordinates(row['city'], row['state'])
            if coords:
                lat, lon = coords
                all_states.add(row['state'])
                
                popup_html = f"""
                <div style='width: 320px; font-family: Arial, sans-serif;'>
                    <h3 style='color: #b71c1c; margin-bottom: 10px;'>{row['name']}</h3>
                    <div style='background-color: #ecf0f1; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                        <h4 style='color: #34495e; margin: 0 0 5px 0;'>📍 Location</h4>
                        <p style='margin: 2px 0;'><strong>Address:</strong> {row['street']}, {row['city']}, {row['state']} {row['zip']}</p>
                        <p style='margin: 2px 0;'><strong>MSA:</strong> {row['msa_name']}</p>
                        <p style='margin: 2px 0;'><a href='{row['link']}' target='_blank'>Facility Website</a></p>
                    </div>
                    <div style='background-color: #e8f5e8; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                        <h4 style='color: #27ae60; margin: 0 0 5px 0;'>🏥 Hospital Details</h4>
                        <p style='margin: 2px 0;'><strong>FTE Count:</strong> {row.get('fte_count', 'N/A')}</p>
                        <p style='margin: 2px 0;'><strong>Discharges (2023):</strong> {row.get('discharges (inpatient volume, 2023)', 'N/A')}</p>
                        <p style='margin: 2px 0;'><strong>Patient Days (2023):</strong> {row.get('patient_days (2023)', 'N/A')}</p>
                        <p style='margin: 2px 0;'><strong>CMI (12/2023):</strong> {row.get('cmi (12/2023)', 'N/A')}</p>
                    </div>
                </div>
                """
                style = facility_style['Hospital']
                facility_counts['Hospital'] = facility_counts.get('Hospital', 0) + 1
                marker = folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=350),
                    tooltip=f"{row['name']} | {row['state']} | Hospital",
                    icon=folium.Icon(color=style['color'], icon=style['icon'], prefix='fa')
                )
                marker.add_to(m)
                facilities_added += 1
        except Exception as e:
            print(f"Error adding hospital {row.get('name', 'N/A')}: {e}")
            continue
    
    # --- Add all other facilities (non-hospitals) ---
    for idx, row in df.iterrows():
        if str(row['facility_type']).strip().lower() == 'hospital':
            continue  # skip, already added from masterlist
        try:
            coords = get_coordinates(row['city'], row['state'])
            if coords:
                lat, lon = coords
                all_states.add(row['state'])
                
                popup_html = f"""
                <div style='width: 300px; font-family: Arial, sans-serif;'>
                    <h3 style='color: #2c3e50; margin-bottom: 10px;'>{row['name']}</h3>
                    <div style='background-color: #ecf0f1; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                        <h4 style='color: #34495e; margin: 0 0 5px 0;'>📍 Location</h4>
                        <p style='margin: 2px 0;'><strong>Address:</strong> {row['street']}, {row['city']}, {row['state']} {row['zip']}</p>
                        <p style='margin: 2px 0;'><strong>MSA:</strong> {row['msa_name']}</p>
                    </div>
                    <div style='background-color: #e8f5e8; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                        <h4 style='color: #27ae60; margin: 0 0 5px 0;'>🏥 Facility Details</h4>
                        <p style='margin: 2px 0;'><strong>Type:</strong> {row['facility_type']}</p>
                        <p style='margin: 2px 0;'><strong>Specialty:</strong> {row['specialty']}</p>
                    </div>
                    <div style='background-color: #fff3cd; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                        <h4 style='color: #856404; margin: 0 0 5px 0;'>💰 Economic Profile</h4>
                        <p style='margin: 2px 0;'><strong>Median Income:</strong> ${row['msa_median_household_income']:,.0f}</p>
                        <p style='margin: 2px 0;'><strong>MSA Population:</strong> {row['msa_population']:,.0f}</p>
                    </div>
                    <div style='background-color: #d1ecf1; padding: 10px; border-radius: 5px;'>
                        <h4 style='color: #0c5460; margin: 0 0 5px 0;'>👥 Demographics</h4>
                        <p style='margin: 2px 0;'><strong>Median Age:</strong> {row['median_age']:.1f} years</p>
                        <p style='margin: 2px 0;'><strong>Under 18:</strong> {row['pct_under_18']:.1f}%</p>
                        <p style='margin: 2px 0;'><strong>65+:</strong> {row['pct_65_plus']:.1f}%</p>
                    </div>
                </div>
                """
                style = facility_style.get(row['facility_type'], {'color': 'lightgray', 'icon': 'question'})
                facility_counts[row['facility_type']] = facility_counts.get(row['facility_type'], 0) + 1
                marker = folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=350),
                    tooltip=f"{row['name']} | {row['state']} | {row['facility_type']}",
                    icon=folium.Icon(color=style['color'], icon=style['icon'], prefix='fa')
                )
                marker.add_to(m)
                facilities_added += 1
        except Exception as e:
            print(f"Error adding facility {row['name']}: {e}")
            continue
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add fullscreen option
    plugins.Fullscreen().add_to(m)
    
    # Add measure tool
    plugins.MeasureControl().add_to(m)
    
    # Add minimap
    minimap = plugins.MiniMap()
    m.add_child(minimap)
    
    # Add scrollable legend with facility counts
    legend_html = f'''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 320px; max-height: 500px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px; overflow-y: auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    <h4 style="margin-top: 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">SSM Health Facility Map Legend</h4>
    
    <div style="margin-bottom: 15px;">
        <h5 style="color: #34495e; margin: 5px 0;">🏥 Facility Types ({facilities_added} total):</h5>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-plus fa-2x" style="color:red; margin-right: 8px;"></i>
            <span>Hospital ({facility_counts.get('Hospital', 0)})</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-exclamation-triangle fa-2x" style="color:darkred; margin-right: 8px;"></i>
            <span>Emergency Department (ED/ER) ({facility_counts.get('Emergency Department (ED/ER)', 0)})</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-clock fa-2x" style="color:orange; margin-right: 8px;"></i>
            <span>Urgent Care ({facility_counts.get('Urgent Care', 0)})</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-user-md fa-2x" style="color:blue; margin-right: 8px;"></i>
            <span>Clinic (or Outpatient Clinic) ({facility_counts.get('Clinic (or Outpatient Clinic)', 0)})</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-pills fa-2x" style="color:green; margin-right: 8px;"></i>
            <span>Pharmacy ({facility_counts.get('Pharmacy', 0)})</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-eye fa-2x" style="color:purple; margin-right: 8px;"></i>
            <span>Imaging Center / Radiology ({facility_counts.get('Imaging Center / Radiology', 0)})</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-flask fa-2x" style="color:red; margin-right: 8px;"></i>
            <span>Laboratory / Lab ({facility_counts.get('Laboratory / Lab', 0)})</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-heartbeat fa-2x" style="color:blue; margin-right: 8px;"></i>
            <span>Rehabilitation Center (or Physical Therapy) ({facility_counts.get('Rehabilitation Center (or Physical Therapy)', 0)})</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-shield-alt fa-2x" style="color:green; margin-right: 8px;"></i>
            <span>Surgery Center (or Ambulatory Surgery Center – ASC) ({facility_counts.get('Surgery Center (or Ambulatory Surgery Center – ASC)', 0)})</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <i class="fa fa-question fa-2x" style="color:lightgray; margin-right: 8px;"></i>
            <span>Unknown ({facility_counts.get('Unknown', 0)})</span>
        </div>
    </div>
    
    <div style="font-size: 12px; color: #7f8c8d; border-top: 1px solid #ecf0f1; padding-top: 8px;">
        💡 All facility types are visible by default
    </div>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map
    output_file = 'ssm_health_simple_color_coded_map.html'
    m.save(output_file)
    
    print(f"✅ Simple color-coded facility map created successfully!")
    print(f"📊 Added {facilities_added} facilities to the map")
    print(f"🎨 Facility type distribution:")
    for facility_type, count in facility_counts.items():
        print(f"   - {facility_type}: {count}")
    print(f"🗺️ Map saved to: {output_file}")
    
    return m

if __name__ == "__main__":
    create_simple_color_coded_map() 