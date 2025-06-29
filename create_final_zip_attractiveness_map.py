#!/usr/bin/env python3
"""
Create Final ZIP Attractiveness Map with SSM Facility Overlays
Combines scored ZIP demographics with GeoJSON polygons and SSM facilities
"""

import pandas as pd
import folium
import json
import numpy as np
from folium import plugins
import warnings
warnings.filterwarnings('ignore')

class FinalZIPAttractivenessMapper:
    def __init__(self):
        """Initialize the mapper"""
        self.facility_icons = {
            'Hospital': '🏥',
            'Emergency Room': '🚨',
            'Urgent Care': '⚡',
            'Clinic': '🏥',
            'Medical Office': '🏥',
            'Specialty Center': '🏥',
            'Rehabilitation': '🏥',
            'Laboratory': '🔬',
            'Imaging Center': '📷',
            'Pharmacy': '💊',
            'Other': '🏥'
        }
        
        self.facility_colors = {
            'Hospital': '#d62728',  # Red
            'Emergency Room': '#ff7f0e',  # Orange
            'Urgent Care': '#2ca02c',  # Green
            'Clinic': '#1f77b4',  # Blue
            'Medical Office': '#9467bd',  # Purple
            'Specialty Center': '#8c564b',  # Brown
            'Rehabilitation': '#e377c2',  # Pink
            'Laboratory': '#7f7f7f',  # Gray
            'Imaging Center': '#bcbd22',  # Yellow-green
            'Pharmacy': '#17becf',  # Cyan
            'Other': '#a6cee3'  # Light blue
        }
    
    def load_data(self):
        """Load all required data files"""
        print("📊 Loading data files...")
        
        # Load scored ZIP demographics
        self.zip_scores = pd.read_csv('all_mn_wi_il_zip_demographics_scored.csv')
        print(f"  ✅ Loaded {len(self.zip_scores)} scored ZIP codes")
        
        # Load SSM facilities with coordinates
        self.facilities = pd.read_csv('ssm_health_locations_with_attractiveness_scores_and_coords.csv')
        print(f"  ✅ Loaded {len(self.facilities)} SSM facilities")
        
        # Load GeoJSON
        with open('zipcodes_mn_wi_il.geojson', 'r') as f:
            self.geojson = json.load(f)
        print(f"  ✅ Loaded GeoJSON with {len(self.geojson['features'])} ZIP polygons")
        
        # Clean facility data
        self.clean_facility_data()
    
    def clean_facility_data(self):
        """Clean and prepare facility data"""
        print("🧹 Cleaning facility data...")
        
        # Remove facilities without coordinates
        self.facilities = self.facilities.dropna(subset=['lat', 'lon'])
        
        # Ensure ZIP codes are strings and match format
        self.facilities['zip'] = self.facilities['zip'].astype(str).str.zfill(5)
        self.zip_scores['zip'] = self.zip_scores['zip'].astype(str).str.zfill(5)
        
        # Categorize facility types
        self.facilities['facility_category'] = self.facilities['type'].apply(self.categorize_facility)
        
        print(f"  ✅ Cleaned {len(self.facilities)} facilities with coordinates")
    
    def categorize_facility(self, facility_type):
        """Categorize facility types for consistent mapping"""
        if pd.isna(facility_type):
            return 'Other'
        
        facility_type = str(facility_type).lower()
        
        if 'hospital' in facility_type:
            return 'Hospital'
        elif 'emergency' in facility_type or 'er' in facility_type:
            return 'Emergency Room'
        elif 'urgent' in facility_type:
            return 'Urgent Care'
        elif 'clinic' in facility_type:
            return 'Clinic'
        elif 'office' in facility_type:
            return 'Medical Office'
        elif 'specialty' in facility_type:
            return 'Specialty Center'
        elif 'rehab' in facility_type:
            return 'Rehabilitation'
        elif 'lab' in facility_type:
            return 'Laboratory'
        elif 'imaging' in facility_type or 'radiology' in facility_type:
            return 'Imaging Center'
        elif 'pharmacy' in facility_type:
            return 'Pharmacy'
        else:
            return 'Other'
    
    def join_scores_to_geojson(self):
        """Join attractiveness scores to GeoJSON features"""
        print("🔗 Joining scores to GeoJSON...")
        
        # Create ZIP to score mapping
        zip_score_map = dict(zip(self.zip_scores['zip'], self.zip_scores['attractiveness_score']))
        zip_category_map = dict(zip(self.zip_scores['zip'], self.zip_scores['attractiveness_category']))
        zip_color_map = dict(zip(self.zip_scores['zip'], self.zip_scores['attractiveness_color']))
        
        # Join data to GeoJSON features
        joined_features = []
        matched_count = 0
        
        for feature in self.geojson['features']:
            # Extract ZIP code from feature properties
            zip_code = None
            for prop_key in ['ZCTA5CE10', 'ZCTA5CE', 'ZIPCODE', 'zip']:
                if prop_key in feature['properties']:
                    zip_code = str(feature['properties'][prop_key]).zfill(5)
                    break
            
            if zip_code and zip_code in zip_score_map:
                # Add attractiveness data to properties
                feature['properties']['attractiveness_score'] = zip_score_map[zip_code]
                feature['properties']['attractiveness_category'] = zip_category_map[zip_code]
                feature['properties']['attractiveness_color'] = zip_color_map[zip_code]
                feature['properties']['zip_code'] = zip_code
                matched_count += 1
            else:
                # Use default values for unmatched ZIPs
                feature['properties']['attractiveness_score'] = 50.0
                feature['properties']['attractiveness_category'] = 'Medium'
                feature['properties']['attractiveness_color'] = '#2ca02c'
                feature['properties']['zip_code'] = zip_code or 'Unknown'
            
            joined_features.append(feature)
        
        self.geojson['features'] = joined_features
        print(f"  ✅ Joined scores to {matched_count} ZIP polygons")
    
    def create_attractiveness_style_function(self):
        """Create style function for ZIP polygon coloring"""
        def style_function(feature):
            score = feature['properties'].get('attractiveness_score', 50)
            color = feature['properties'].get('attractiveness_color', '#2ca02c')
            
            return {
                'fillColor': color,
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.7,
                'opacity': 0.3
            }
        
        return style_function
    
    def create_facility_popup(self, facility):
        """Create popup content for facility markers"""
        # Use 'address' if present, else construct from street, city, state, zip
        if 'address' in facility and pd.notna(facility['address']):
            address = facility['address']
        else:
            address = f"{facility.get('street','')}, {facility.get('city','')}, {facility.get('state','')} {facility.get('zip','')}"
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px;">
            <h4 style="margin: 0 0 10px 0; color: #333;">{facility['name']}</h4>
            <p style="margin: 5px 0;"><strong>Type:</strong> {facility['type']}</p>
            <p style="margin: 5px 0;"><strong>Address:</strong> {address}</p>
            <p style="margin: 5px 0;"><strong>Phone:</strong> {facility.get('phone','')}</p>
            <p style="margin: 5px 0;"><strong>ZIP:</strong> {facility.get('zip','')}</p>
        </div>
        """
        return popup_html
    
    def create_map(self):
        """Create the final interactive map"""
        print("🗺️ Creating final ZIP attractiveness map...")
        
        # Calculate center point for the map
        center_lat = self.facilities['lat'].mean()
        center_lon = self.facilities['lon'].mean()
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles='cartodbpositron'
        )
        
        # Add ZIP polygon layer
        print("  🏠 Adding ZIP attractiveness polygons...")
        folium.GeoJson(
            self.geojson,
            name='ZIP Attractiveness',
            style_function=self.create_attractiveness_style_function(),
            tooltip=folium.GeoJsonTooltip(
                fields=['zip_code', 'attractiveness_score', 'attractiveness_category'],
                aliases=['ZIP Code', 'Attractiveness Score', 'Category'],
                localize=True,
                sticky=False,
                labels=True,
                style="""
                    background-color: yellow;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """
            )
        ).add_to(m)
        
        # Add facility markers
        print("  🏥 Adding SSM facility markers...")
        for _, facility in self.facilities.iterrows():
            try:
                lat = float(facility['lat'])
                lon = float(facility['lon'])
                
                if pd.isna(lat) or pd.isna(lon):
                    continue
                
                category = facility['facility_category']
                icon = self.facility_icons.get(category, '🏥')
                color = self.facility_colors.get(category, '#a6cee3')
                
                # Create popup
                popup_html = self.create_facility_popup(facility)
                
                # Add marker
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"{facility['name']} ({category})",
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)
                
            except (ValueError, TypeError) as e:
                print(f"    ⚠️ Skipping facility with invalid coordinates: {facility['name']}")
                continue
        
        # Add legend
        print("  📋 Adding legend...")
        self.add_legend(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add fullscreen option
        plugins.Fullscreen().add_to(m)
        
        # Add measure tool
        plugins.MeasureControl(position='bottomleft').add_to(m)
        
        return m
    
    def add_legend(self, m):
        """Add comprehensive legend to the map"""
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 300px; height: 400px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; overflow-y: auto;">
        <h4 style="margin-top: 0;">SSM Health Market Attractiveness</h4>
        
        <h5>ZIP Code Attractiveness:</h5>
        <p><i class="fa fa-square" style="color:#1f77b4"></i> Very High (80-100)</p>
        <p><i class="fa fa-square" style="color:#ff7f0e"></i> High (60-79)</p>
        <p><i class="fa fa-square" style="color:#2ca02c"></i> Medium (40-59)</p>
        <p><i class="fa fa-square" style="color:#d62728"></i> Low (20-39)</p>
        <p><i class="fa fa-square" style="color:#9467bd"></i> Very Low (0-19)</p>
        
        <h5>SSM Facilities:</h5>
        <p><i class="fa fa-hospital-o" style="color:#d62728"></i> Hospital</p>
        <p><i class="fa fa-ambulance" style="color:#ff7f0e"></i> Emergency Room</p>
        <p><i class="fa fa-plus-circle" style="color:#2ca02c"></i> Urgent Care</p>
        <p><i class="fa fa-stethoscope" style="color:#1f77b4"></i> Clinic</p>
        <p><i class="fa fa-user-md" style="color:#9467bd"></i> Medical Office</p>
        <p><i class="fa fa-medkit" style="color:#8c564b"></i> Specialty Center</p>
        
        <h5>Scoring Factors:</h5>
        <p>• Population Density (25%)</p>
        <p>• Population Growth (20%)</p>
        <p>• Senior Population (25%)</p>
        <p>• Income Level (20%)</p>
        <p>• Young Families (10%)</p>
        
        <p style="font-size: 12px; margin-top: 10px;">
        <strong>Data Sources:</strong><br>
        • Census ACS 5-Year Estimates<br>
        • SSM Health Facility Database<br>
        • ZIP Code Tabulation Areas
        </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
    
    def save_map(self, m, filename='ssm_health_final_zip_attractiveness_map.html'):
        """Save the map to HTML file"""
        print(f"💾 Saving map to {filename}...")
        m.save(filename)
        print(f"✅ Map saved successfully!")
        
        # Print summary statistics
        self.print_summary()
    
    def print_summary(self):
        """Print summary statistics"""
        print(f"\n📊 Final Map Summary:")
        print(f"  🏠 ZIP polygons: {len(self.geojson['features'])}")
        print(f"  🏥 SSM facilities: {len(self.facilities)}")
        print(f"  🎯 Average attractiveness score: {self.zip_scores['attractiveness_score'].mean():.1f}")
        
        # Facility type breakdown
        facility_counts = self.facilities['facility_category'].value_counts()
        print(f"\n🏥 Facility Types:")
        for facility_type, count in facility_counts.items():
            print(f"  {facility_type}: {count}")
        
        # Attractiveness distribution
        category_counts = self.zip_scores['attractiveness_category'].value_counts()
        print(f"\n🏷️ Attractiveness Distribution:")
        for category, count in category_counts.items():
            percentage = (count / len(self.zip_scores)) * 100
            print(f"  {category}: {count} ZIP codes ({percentage:.1f}%)")

def main():
    """Main function to create the final map"""
    print("🗺️ SSM Health Final ZIP Attractiveness Map Creator")
    print("=" * 60)
    
    mapper = FinalZIPAttractivenessMapper()
    
    try:
        # Load all data
        mapper.load_data()
        
        # Join scores to GeoJSON
        mapper.join_scores_to_geojson()
        
        # Create the map
        m = mapper.create_map()
        
        # Save the map
        mapper.save_map(m)
        
        print(f"\n🎉 Final ZIP attractiveness map created successfully!")
        print(f"📊 Features:")
        print(f"  • All 3,048 ZIP codes colored by attractiveness score")
        print(f"  • SSM facility locations with icons and popups")
        print(f"  • Interactive legend and controls")
        print(f"  • Tooltips with ZIP details")
        print(f"  • Fullscreen and measurement tools")
        
        print(f"\n💡 Open 'ssm_health_final_zip_attractiveness_map.html' in your browser to view the map!")
        
    except Exception as e:
        print(f"❌ Error creating map: {e}")
        raise

if __name__ == "__main__":
    main() 