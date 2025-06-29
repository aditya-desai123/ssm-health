#!/usr/bin/env python3
"""
Create Enhanced SSM Health Facility Map with ZIP-Level Attractiveness Scores
Features:
- ZIP code boundaries with color coding based on attractiveness scores
- Enhanced popups with ZIP-level demographics
- MSA overlay bubbles with demographic information
- Facility markers with attractiveness context
"""

import pandas as pd
import folium
from folium import plugins
import json
import requests
from collections import defaultdict
import numpy as np

class EnhancedAttractivenessMap:
    def __init__(self):
        """Initialize the enhanced map creator"""
        self.zip_boundaries = {}
        self.msa_data = {}
        self.facility_data = None
        
    def create_zip_heatmap_layer(self, df, map_obj):
        """Create ZIP heatmap layer with attractiveness color coding"""
        print("🗺️ Creating ZIP attractiveness heatmap layer...")
        
        # Group by ZIP code and calculate average attractiveness
        zip_attractiveness = df.groupby('zip').agg({
            'attractiveness_score': 'mean',
            'attractiveness_category': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Medium',
            'attractiveness_color': lambda x: x.mode()[0] if len(x.mode()) > 0 else '#2ca02c',
            'zip_population_density': 'first',
            'zip_population_growth_rate': 'first',
            'zip_median_household_income': 'first',
            'senior_population_pct': 'first',
            'young_family_pct': 'first',
            'lat': 'mean',
            'lon': 'mean'
        }).reset_index()
        
        # Create ZIP heatmap layer
        zip_layer = folium.FeatureGroup(name="ZIP Code Attractiveness", show=True)
        
        for _, row in zip_attractiveness.iterrows():
            zip_code = row['zip']
            if pd.isna(zip_code) or zip_code == 'N/A' or pd.isna(row['lat']) or pd.isna(row['lon']):
                continue
                
            # Create popup content
            popup_content = f"""
            <div style="width: 300px;">
                <h4>ZIP Code {zip_code}</h4>
                <p><strong>Attractiveness Score:</strong> {row['attractiveness_score']:.1f}/100</p>
                <p><strong>Category:</strong> {row['attractiveness_category']}</p>
                <hr>
                <p><strong>Population Density:</strong> {row['zip_population_density']:,.0f} people/sq mi</p>
                <p><strong>Population Growth:</strong> {row['zip_population_growth_rate']:.1f}%</p>
                <p><strong>Median Income:</strong> ${row['zip_median_household_income']:,.0f}</p>
                <p><strong>Senior Population (65+):</strong> {row['senior_population_pct']:.1f}%</p>
                <p><strong>Young Families (0-17):</strong> {row['young_family_pct']:.1f}%</p>
            </div>
            """
            
            # Add ZIP circle to map
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=15,
                popup=folium.Popup(popup_content, max_width=350),
                color=self.get_attractiveness_color(row['attractiveness_score']),
                fill=True,
                fillColor=self.get_attractiveness_color(row['attractiveness_score']),
                fillOpacity=0.4,
                weight=2,
                tooltip=f"ZIP {zip_code}: {row['attractiveness_score']:.1f}/100"
            ).add_to(zip_layer)
        
        zip_layer.add_to(map_obj)
        return zip_layer
    
    def get_attractiveness_color(self, score):
        """Get color based on attractiveness score"""
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
    
    def create_msa_overlay_layer(self, df, map_obj):
        """Create MSA overlay layer with demographic bubbles"""
        print("🏙️ Creating MSA overlay layer...")
        
        # Group by MSA and calculate demographics
        msa_demographics = df.groupby(['msa_name', 'msa_code']).agg({
            'msa_population': 'first',
            'msa_median_household_income': 'first',
            'pct_under_18': 'first',
            'pct_65_plus': 'first',
            'attractiveness_score': 'mean',
            'lat': 'mean',
            'lon': 'mean'
        }).reset_index()
        
        # Create MSA overlay layer
        msa_layer = folium.FeatureGroup(name="MSA Demographics", show=True)
        
        for _, row in msa_demographics.iterrows():
            if pd.isna(row['lat']) or pd.isna(row['lon']):
                continue
                
            # Calculate bubble size based on population
            population = row['msa_population'] if not pd.isna(row['msa_population']) else 100000
            bubble_size = min(max(population / 10000, 5), 50)  # Scale between 5-50
            
            # Calculate bubble color based on average attractiveness
            bubble_color = self.get_attractiveness_color(row['attractiveness_score'])
            
            # Create popup content
            popup_content = f"""
            <div style="width: 350px;">
                <h4>{row['msa_name']}</h4>
                <p><strong>MSA Code:</strong> {row['msa_code']}</p>
                <p><strong>Population:</strong> {population:,.0f}</p>
                <p><strong>Median Income:</strong> ${row['msa_median_household_income']:,.0f}</p>
                <p><strong>Under 18:</strong> {row['pct_under_18']:.1f}%</p>
                <p><strong>65+:</strong> {row['pct_65_plus']:.1f}%</p>
                <p><strong>Avg Attractiveness:</strong> {row['attractiveness_score']:.1f}/100</p>
            </div>
            """
            
            # Add MSA bubble to map
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=bubble_size,
                popup=folium.Popup(popup_content, max_width=400),
                color=bubble_color,
                fill=True,
                fillColor=bubble_color,
                fillOpacity=0.6,
                weight=2,
                tooltip=f"{row['msa_name']}: {population:,.0f} people"
            ).add_to(msa_layer)
        
        msa_layer.add_to(map_obj)
        return msa_layer
    
    def create_facility_layer(self, df, map_obj):
        """Create facility layer with enhanced popups"""
        print("🏥 Creating facility layer...")
        
        # Define facility type colors and icons (using our refined categorization)
        facility_colors = {
            'Hospital': '#e41a1c',           # Red
            'Emergency Room': '#377eb8',     # Blue
            'Urgent Care': '#4daf4a',        # Green
            'Primary Care': '#984ea3',       # Purple
            'Specialty Care': '#ff7f00',     # Orange
            'Diagnostic': '#a65628',         # Brown
            'Rehabilitation': '#f781bf',     # Pink
            'Pharmacy': '#999999',           # Gray
            'Other': '#999999'               # Gray
        }
        
        facility_icons = {
            'Hospital': 'plus',
            'Emergency Room': 'exclamation-triangle',
            'Urgent Care': 'clock',
            'Primary Care': 'user-md',
            'Specialty Care': 'stethoscope',
            'Diagnostic': 'search',
            'Rehabilitation': 'wheelchair',
            'Pharmacy': 'shopping-cart',
            'Other': 'building'
        }
        
        # Create facility layer
        facility_layer = folium.FeatureGroup(name="SSM Health Facilities", show=True)
        
        for _, row in df.iterrows():
            if pd.isna(row['lat']) or pd.isna(row['lon']):
                continue
                
            # Use the refined facility_type categorization
            facility_type = row['facility_type'] if pd.notna(row['facility_type']) else 'Other'
            
            # Get color and icon for this facility type
            color = facility_colors.get(facility_type, facility_colors['Other'])
            icon_name = facility_icons.get(facility_type, facility_icons['Other'])
            
            # Create enhanced popup content
            popup_content = f"""
            <div style="width: 350px;">
                <h4>{row['name']}</h4>
                <p><strong>Type:</strong> {facility_type}</p>
                <p><strong>Address:</strong> {row['street']}, {row['city']}, {row['state']} {row['zip']}</p>
                <hr>
                <h5>ZIP Code Demographics</h5>
                <p><strong>ZIP:</strong> {row['zip']}</p>
                <p><strong>Attractiveness Score:</strong> {row['attractiveness_score']:.1f}/100</p>
                <p><strong>Population Density:</strong> {row['zip_population_density']:,.0f} people/sq mi</p>
                <p><strong>Population Growth:</strong> {row['zip_population_growth_rate']:.1f}%</p>
                <p><strong>Median Income:</strong> ${row['zip_median_household_income']:,.0f}</p>
                <p><strong>Senior Population (65+):</strong> {row['senior_population_pct']:.1f}%</p>
                <p><strong>Young Families (0-17):</strong> {row['young_family_pct']:.1f}%</p>
                <hr>
                <h5>Component Scores</h5>
                <p><strong>Density:</strong> {row['density_score']:.1f}</p>
                <p><strong>Growth:</strong> {row['growth_score']:.1f}</p>
                <p><strong>Senior:</strong> {row['senior_score']:.1f}</p>
                <p><strong>Income:</strong> {row['income_score']:.1f}</p>
                <p><strong>Young Family:</strong> {row['young_family_score']:.1f}</p>
            </div>
            """
            
            # Add facility marker to map with proper icon color
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(popup_content, max_width=400),
                tooltip=f"{row['name']} - {facility_type}",
                icon=folium.Icon(color='red', icon=icon_name, prefix='fa')
            ).add_to(facility_layer)
        
        facility_layer.add_to(map_obj)
        return facility_layer
    
    def create_legend(self, map_obj):
        """Create legend for attractiveness scores and facility types"""
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 250px; height: 400px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; overflow-y: auto;">
        <h4>Healthcare Attractiveness</h4>
        <p><i class="fa fa-square" style="color:#1f77b4"></i> Very High (80-100)</p>
        <p><i class="fa fa-square" style="color:#ff7f0e"></i> High (60-79)</p>
        <p><i class="fa fa-square" style="color:#2ca02c"></i> Medium (40-59)</p>
        <p><i class="fa fa-square" style="color:#d62728"></i> Low (20-39)</p>
        <p><i class="fa fa-square" style="color:#9467bd"></i> Very Low (0-19)</p>
        <hr>
        <h5>Scoring Factors:</h5>
        <p>• Population Density (25%)</p>
        <p>• Population Growth (20%)</p>
        <p>• Senior Population (25%)</p>
        <p>• Income Level (20%)</p>
        <p>• Young Families (10%)</p>
        <hr>
        <h5>Facility Types:</h5>
        <p><i class="fa fa-plus" style="color:#e41a1c"></i> Hospital</p>
        <p><i class="fa fa-exclamation-triangle" style="color:#377eb8"></i> Emergency Room</p>
        <p><i class="fa fa-clock" style="color:#4daf4a"></i> Urgent Care</p>
        <p><i class="fa fa-user-md" style="color:#984ea3"></i> Primary Care</p>
        <p><i class="fa fa-stethoscope" style="color:#ff7f00"></i> Specialty Care</p>
        <p><i class="fa fa-search" style="color:#a65628"></i> Diagnostic</p>
        <p><i class="fa fa-wheelchair" style="color:#f781bf"></i> Rehabilitation</p>
        <p><i class="fa fa-shopping-cart" style="color:#999999"></i> Pharmacy</p>
        </div>
        '''
        map_obj.get_root().html.add_child(folium.Element(legend_html))
    
    def create_enhanced_map(self, input_file='ssm_health_locations_with_attractiveness_scores_and_coords.csv'):
        """Create the enhanced attractiveness map"""
        print("🗺️ Creating Enhanced SSM Health Attractiveness Map...")
        
        # Load data
        df = pd.read_csv(input_file)
        print(f"📊 Loaded {len(df)} facilities with attractiveness scores")
        
        # Calculate center of the map
        center_lat = df['lat'].mean()
        center_lon = df['lon'].mean()
        
        # Create base map
        map_obj = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles='OpenStreetMap'
        )
        
        # Add tile layers
        folium.TileLayer('cartodbpositron', name='Light Map').add_to(map_obj)
        folium.TileLayer('cartodbdark_matter', name='Dark Map').add_to(map_obj)
        folium.TileLayer('Stamen Terrain', name='Terrain').add_to(map_obj)
        
        # Create layers
        zip_layer = self.create_zip_heatmap_layer(df, map_obj)
        msa_layer = self.create_msa_overlay_layer(df, map_obj)
        facility_layer = self.create_facility_layer(df, map_obj)
        
        # Add layer control
        folium.LayerControl().add_to(map_obj)
        
        # Add legend
        self.create_legend(map_obj)
        
        # Add fullscreen option
        plugins.Fullscreen().add_to(map_obj)
        
        # Add measure tool
        plugins.MeasureControl(position='topleft').add_to(map_obj)
        
        # Save the map
        output_file = 'ssm_health_attractiveness_map.html'
        map_obj.save(output_file)
        
        print(f"✅ Enhanced map saved to {output_file}")
        print("🗺️ Map features:")
        print("  • ZIP code attractiveness heatmap")
        print("  • MSA demographic bubbles")
        print("  • Facility markers with detailed popups")
        print("  • Interactive legend and layer controls")
        print("  • Fullscreen and measurement tools")
        
        return map_obj

def main():
    """Main function to create the enhanced map"""
    print("🏥 Enhanced SSM Health Attractiveness Map Creator")
    print("=" * 60)
    
    mapper = EnhancedAttractivenessMap()
    
    try:
        # Create the enhanced map
        map_obj = mapper.create_enhanced_map()
        
        print("\n🎉 Enhanced map creation completed!")
        print("📊 Map includes:")
        print("  • ZIP-level attractiveness scoring")
        print("  • Demographic overlays")
        print("  • Enhanced facility information")
        print("  • Interactive features")
        
    except Exception as e:
        print(f"❌ Error creating map: {e}")
        raise

if __name__ == "__main__":
    main() 