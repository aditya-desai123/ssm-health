#!/usr/bin/env python3
"""
Create a full ZIP-level attractiveness map for MN, WI, IL:
- Fill each ZIP polygon by attractiveness score (red/green scale)
- Overlay SSM facilities with correct icons/colors
- Show a combined legend
"""
import folium
import pandas as pd
import json
from folium.plugins import MarkerCluster

# Load scored ZIP polygons
with open('zipcodes_mn_wi_il_scored.geojson', 'r') as f:
    zip_geo = json.load(f)

# Load SSM facility data (with lat/lon and facility_type)
facilities = pd.read_csv('ssm_health_locations_with_attractiveness_scores_and_coords.csv')

# Color scale for ZIP polygons (red = low, green = high)
def zip_color(score):
    if score is None or pd.isna(score):
        return '#cccccc'  # Gray for missing
    if score >= 80:
        return '#006837'  # Dark green
    elif score >= 60:
        return '#31a354'  # Green
    elif score >= 40:
        return '#fed976'  # Yellow
    elif score >= 20:
        return '#fd8d3c'  # Orange
    else:
        return '#e31a1c'  # Red

# Create base map
center = [45.0, -92.5]
map_obj = folium.Map(location=center, zoom_start=6, tiles='cartodbpositron')

# Add ZIP polygons
folium.GeoJson(
    zip_geo,
    name='ZIP Attractiveness',
    style_function=lambda feature: {
        'fillColor': zip_color(feature['properties'].get('attractiveness_score')),
        'color': 'black',
        'weight': 0.5,
        'fillOpacity': 0.6
    },
    highlight_function=lambda x: {'weight': 2, 'color': 'blue'},
    tooltip=folium.GeoJsonTooltip(
        fields=['ZCTA5CE10', 'attractiveness_score'],
        aliases=['ZIP', 'Attractiveness Score'],
        localize=True
    ),
    popup=folium.GeoJsonPopup(
        fields=['ZCTA5CE10', 'attractiveness_score'],
        aliases=['ZIP', 'Attractiveness Score'],
        localize=True
    )
).add_to(map_obj)

# Facility icon/colors
facility_icons = {
    'Hospital': ('plus', 'red'),
    'Emergency Room': ('exclamation-triangle', 'blue'),
    'Urgent Care': ('clock', 'green'),
    'Primary Care': ('user-md', 'purple'),
    'Specialty Care': ('stethoscope', 'orange'),
    'Diagnostic': ('search', 'brown'),
    'Rehabilitation': ('wheelchair', 'pink'),
    'Pharmacy': ('shopping-cart', 'gray'),
    'Other': ('building', 'gray')
}

# Add facility markers (clustered)
marker_cluster = MarkerCluster(name='SSM Facilities').add_to(map_obj)
for _, row in facilities.iterrows():
    if pd.isna(row['lat']) or pd.isna(row['lon']):
        continue
    facility_type = row['facility_type'] if pd.notna(row['facility_type']) else 'Other'
    icon, color = facility_icons.get(facility_type, ('building', 'gray'))
    popup = folium.Popup(f"""
        <b>{row['name']}</b><br>
        <b>Type:</b> {facility_type}<br>
        <b>Address:</b> {row['street']}, {row['city']}, {row['state']} {row['zip']}<br>
        <b>Attractiveness Score:</b> {row.get('attractiveness_score', 'N/A'):.1f}<br>
    """, max_width=300)
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=popup,
        tooltip=f"{row['name']} - {facility_type}",
        icon=folium.Icon(color=color, icon=icon, prefix='fa')
    ).add_to(marker_cluster)

# Add legend
legend_html = '''
 <div style="position: fixed; bottom: 50px; left: 50px; width: 260px; height: 350px; 
      background-color: white; border:2px solid grey; z-index:9999; font-size:14px; padding: 10px; overflow-y: auto;">
 <h4>ZIP Attractiveness Score</h4>
 <p><span style="background:#006837;color:white;padding:2px 8px;">80-100</span> Very High</p>
 <p><span style="background:#31a354;color:white;padding:2px 8px;">60-79</span> High</p>
 <p><span style="background:#fed976;color:black;padding:2px 8px;">40-59</span> Medium</p>
 <p><span style="background:#fd8d3c;color:white;padding:2px 8px;">20-39</span> Low</p>
 <p><span style="background:#e31a1c;color:white;padding:2px 8px;">0-19</span> Very Low</p>
 <hr>
 <h5>Facility Types</h5>
 <p><i class="fa fa-plus" style="color:red"></i> Hospital</p>
 <p><i class="fa fa-exclamation-triangle" style="color:blue"></i> Emergency Room</p>
 <p><i class="fa fa-clock" style="color:green"></i> Urgent Care</p>
 <p><i class="fa fa-user-md" style="color:purple"></i> Primary Care</p>
 <p><i class="fa fa-stethoscope" style="color:orange"></i> Specialty Care</p>
 <p><i class="fa fa-search" style="color:brown"></i> Diagnostic</p>
 <p><i class="fa fa-wheelchair" style="color:pink"></i> Rehabilitation</p>
 <p><i class="fa fa-shopping-cart" style="color:gray"></i> Pharmacy</p>
 <p><i class="fa fa-building" style="color:gray"></i> Other</p>
 </div>
 '''
map_obj.get_root().html.add_child(folium.Element(legend_html))

folium.LayerControl().add_to(map_obj)

map_obj.save('ssm_health_full_zip_attractiveness_map.html')
print('✅ Full ZIP-level attractiveness map saved to ssm_health_full_zip_attractiveness_map.html') 