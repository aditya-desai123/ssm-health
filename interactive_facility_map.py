#!/usr/bin/env python3
"""
Interactive SSM Health Facility Map with Demographic Analysis
Shows all facilities with facility type, MSA information, and key demographic attributes
"""

import pandas as pd
import numpy as np
import folium
from folium import plugins
import geopy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import warnings
warnings.filterwarnings('ignore')

class InteractiveFacilityMapper:
    def __init__(self, csv_file):
        """Initialize the mapper with facility data"""
        self.df = pd.read_csv(csv_file)
        self.geolocator = Nominatim(user_agent="ssm_health_mapper")
        self.coordinate_cache = {}
        self.process_data()
        
    def process_data(self):
        """Clean and process the facility data"""
        print("Processing facility data for mapping...")
        
        # Clean data
        self.df = self.df.dropna(subset=['name', 'city', 'state'])
        
        # Fill missing values
        self.df['type'] = self.df['type'].fillna('Unknown')
        self.df['specialty'] = self.df['specialty'].fillna('General')
        
        # Create facility categories for better visualization
        self.df['facility_category'] = self.df['type'].apply(self.categorize_facility)
        
        # Calculate facilities per 100k population
        self.df['facilities_per_100k'] = (1 / self.df['msa_population']) * 100000
        
        # Create market status
        self.df['market_status'] = self.df['facilities_per_100k'].apply(self.categorize_market)
        
        # Create income categories
        self.df['income_category'] = pd.cut(
            self.df['msa_median_household_income'], 
            bins=[0, 50000, 70000, 90000, float('inf')],
            labels=['Low Income', 'Lower Middle', 'Upper Middle', 'High Income']
        )
        
        # Create age mix categories
        self.df['age_mix_category'] = self.df.apply(self.categorize_age_mix, axis=1)
        
        print(f"Processed {len(self.df)} facilities across {self.df['msa_code'].nunique()} MSAs")
    
    def categorize_facility(self, facility_type):
        """Categorize facility types for visualization"""
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
    
    def categorize_market(self, facilities_per_100k):
        """Categorize market status"""
        if pd.isna(facilities_per_100k):
            return 'Unknown'
        elif facilities_per_100k > 50:
            return 'Overserved'
        elif facilities_per_100k < 20:
            return 'Underserved'
        else:
            return 'Adequately Served'
    
    def categorize_age_mix(self, row):
        """Categorize age mix for visualization"""
        if pd.isna(row['pct_65_plus']):
            return 'Unknown'
        elif row['pct_65_plus'] > 20:
            return 'High Senior Population'
        elif row['pct_under_18'] > 25:
            return 'High Youth Population'
        elif row['pct_18_34'] > 25:
            return 'High Young Adult Population'
        elif row['pct_35_54'] > 30:
            return 'High Working Age Population'
        else:
            return 'Balanced Age Mix'
    
    def get_city_coordinates(self, city, state):
        """Get coordinates for a city using predefined lookup"""
        # Predefined coordinates for major cities in SSM Health's footprint
        city_coords = {
            # Wisconsin
            'Madison, WI': (43.0731, -89.4012),
            'Milwaukee, WI': (43.0389, -87.9065),
            'Janesville, WI': (42.6828, -89.0187),
            'Fond du Lac, WI': (43.7730, -88.4470),
            'Beaver Dam, WI': (43.4578, -88.8373),
            'Watertown, WI': (43.1947, -88.7284),
            'Whitewater, WI': (42.8336, -88.7323),
            'Monroe, WI': (42.6011, -89.6385),
            'Stoughton, WI': (42.9169, -89.2179),
            'Campbellsport, WI': (43.5978, -88.2793),
            'Brodhead, WI': (42.6183, -89.3762),
            'Fort Atkinson, WI': (42.9289, -88.8371),
            'Reedsburg, WI': (43.5325, -90.0026),
            'Brownsville, WI': (43.6167, -88.4917),
            
            # Illinois
            'Chicago, IL': (41.8781, -87.6298),
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
            
            # Missouri
            'St. Louis, MO': (38.6270, -90.1994),
            'Wentzville, MO': (38.8114, -90.8529),
            'O\'Fallon, MO': (38.8106, -90.6998),
            'Kirkwood, MO': (38.5834, -90.4068),
            'Chesterfield, MO': (38.6631, -90.5771),
            'Ballwin, MO': (38.5950, -90.5462),
            'Jefferson City, MO': (38.5767, -92.1735),
            'Tipton, MO': (38.6556, -92.7799),
            'Springfield, MO': (37.2090, -93.2923),
            
            # Oklahoma
            'Oklahoma City, OK': (35.4676, -97.5164),
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
        
        key = f"{city}, {state}"
        return city_coords.get(key)
    
    def get_coordinates(self, address, city, state):
        """Get coordinates for an address with fallback to city coordinates"""
        # Try to get from cache first
        if address in self.coordinate_cache:
            return self.coordinate_cache[address]
        
        # Try geocoding the full address
        try:
            location = self.geolocator.geocode(address, timeout=5)
            if location:
                coords = (location.latitude, location.longitude)
                self.coordinate_cache[address] = coords
                return coords
        except:
            pass
        
        # Fallback to city coordinates
        city_coords = self.get_city_coordinates(city, state)
        if city_coords:
            # Add small random offset to prevent overlapping markers
            import random
            lat_offset = random.uniform(-0.01, 0.01)
            lon_offset = random.uniform(-0.01, 0.01)
            coords = (city_coords[0] + lat_offset, city_coords[1] + lon_offset)
            self.coordinate_cache[address] = coords
            return coords
        
        return None, None
    
    def get_facility_color(self, facility_category):
        """Get color for facility category"""
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
        return color_map.get(facility_category, 'lightgray')
    
    def get_market_status_color(self, market_status):
        """Get color for market status"""
        color_map = {
            'Overserved': 'red',
            'Adequately Served': 'yellow',
            'Underserved': 'green',
            'Unknown': 'gray'
        }
        return color_map.get(market_status, 'gray')
    
    def create_facility_popup(self, row):
        """Create detailed popup content for a facility"""
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
                <p style="margin: 2px 0;"><strong>Market Status:</strong> <span style="color: {self.get_market_status_color(row['market_status'])};">{row['market_status']}</span></p>
            </div>
            
            <div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <h4 style="color: #856404; margin: 0 0 5px 0;">💰 Economic Profile</h4>
                <p style="margin: 2px 0;"><strong>Median Income:</strong> ${row['msa_median_household_income']:,.0f}</p>
                <p style="margin: 2px 0;"><strong>Income Category:</strong> {row['income_category']}</p>
                <p style="margin: 2px 0;"><strong>MSA Population:</strong> {row['msa_population']:,.0f}</p>
                <p style="margin: 2px 0;"><strong>Facilities per 100k:</strong> {row['facilities_per_100k']:.1f}</p>
            </div>
            
            <div style="background-color: #d1ecf1; padding: 10px; border-radius: 5px;">
                <h4 style="color: #0c5460; margin: 0 0 5px 0;">👥 Demographics</h4>
                <p style="margin: 2px 0;"><strong>Median Age:</strong> {row['median_age']:.1f} years</p>
                <p style="margin: 2px 0;"><strong>Age Mix:</strong> {row['age_mix_category']}</p>
                <p style="margin: 2px 0;"><strong>Under 18:</strong> {row['pct_under_18']:.1f}%</p>
                <p style="margin: 2px 0;"><strong>18-34:</strong> {row['pct_18_34']:.1f}%</p>
                <p style="margin: 2px 0;"><strong>35-54:</strong> {row['pct_35_54']:.1f}%</p>
                <p style="margin: 2px 0;"><strong>55-64:</strong> {row['pct_55_64']:.1f}%</p>
                <p style="margin: 2px 0;"><strong>65+:</strong> {row['pct_65_plus']:.1f}%</p>
            </div>
        </div>
        """
        return popup_html
    
    def create_interactive_map(self):
        """Create the main interactive facility map"""
        print("Creating interactive facility map...")
        
        # Calculate center point for the map
        center_lat = 39.8283  # Center of US
        center_lon = -98.5795
        
        # Create the base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=5,
            tiles='OpenStreetMap'
        )
        
        # Add tile layers for different map styles
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
        facility_categories = self.df['facility_category'].unique()
        
        for category in facility_categories:
            facility_groups[category] = folium.FeatureGroup(
                name=f"{category} ({len(self.df[self.df['facility_category'] == category])})",
                overlay=True,
                control=True
            )
        
        # Create feature groups for market status
        market_groups = {}
        market_statuses = self.df['market_status'].unique()
        
        for status in market_statuses:
            market_groups[status] = folium.FeatureGroup(
                name=f"{status} Markets ({len(self.df[self.df['market_status'] == status])})",
                overlay=True,
                control=True
            )
        
        # Add facilities to the map
        print("Adding facilities to map...")
        facilities_added = 0
        
        for idx, row in self.df.iterrows():
            try:
                # Create address for geocoding
                address = f"{row['street']}, {row['city']}, {row['state']} {row['zip']}"
                
                # Get coordinates with fallback
                lat, lon = self.get_coordinates(address, row['city'], row['state'])
                
                if lat is not None and lon is not None:
                    # Create popup content
                    popup_html = self.create_facility_popup(row)
                    
                    # Determine marker color based on facility type
                    marker_color = self.get_facility_color(row['facility_category'])
                    
                    # Create marker
                    marker = folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(popup_html, max_width=350),
                        tooltip=f"{row['name']} - {row['facility_category']}",
                        icon=folium.Icon(color=marker_color, icon='info-sign')
                    )
                    
                    # Add to facility type group
                    facility_groups[row['facility_category']].add_child(marker)
                    
                    # Add to market status group
                    market_groups[row['market_status']].add_child(marker)
                    
                    facilities_added += 1
                    
                    # Progress update
                    if facilities_added % 50 == 0:
                        print(f"Added {facilities_added} facilities...")
                
            except Exception as e:
                print(f"Error adding facility {row['name']}: {e}")
                continue
        
        # Add all feature groups to the map
        for group in facility_groups.values():
            m.add_child(group)
        
        for group in market_groups.values():
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
        
        # Add search functionality
        facilities_data = []
        for idx, row in self.df.iterrows():
            facilities_data.append({
                'name': row['name'],
                'city': row['city'],
                'state': row['state'],
                'facility_type': row['facility_category'],
                'msa': row['msa_name']
            })
        
        # Create search plugin
        search = plugins.Search(
            layer=facility_groups['Primary Care'],  # Default layer
            geom_type='Point',
            placeholder='Search facilities...',
            collapsed=False,
            search_label='name'
        )
        m.add_child(search)
        
        # Add scrollable legend with better styling
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 320px; max-height: 500px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; overflow-y: auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h4 style="margin-top: 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">SSM Health Facility Map Legend</h4>
        
        <div style="margin-bottom: 15px;">
            <h5 style="color: #34495e; margin: 5px 0;">🏥 Facility Types:</h5>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <i class="fa fa-map-marker fa-2x" style="color:red; margin-right: 8px;"></i>
                <span>Hospital</span>
            </div>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <i class="fa fa-map-marker fa-2x" style="color:blue; margin-right: 8px;"></i>
                <span>Primary Care</span>
            </div>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <i class="fa fa-map-marker fa-2x" style="color:orange; margin-right: 8px;"></i>
                <span>Urgent Care</span>
            </div>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <i class="fa fa-map-marker fa-2x" style="color:green; margin-right: 8px;"></i>
                <span>Pharmacy</span>
            </div>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <i class="fa fa-map-marker fa-2x" style="color:purple; margin-right: 8px;"></i>
                <span>Imaging</span>
            </div>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <i class="fa fa-map-marker fa-2x" style="color:darkred; margin-right: 8px;"></i>
                <span>Laboratory</span>
            </div>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <i class="fa fa-map-marker fa-2x" style="color:darkblue; margin-right: 8px;"></i>
                <span>Therapy</span>
            </div>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <i class="fa fa-map-marker fa-2x" style="color:darkgreen; margin-right: 8px;"></i>
                <span>Cancer Care</span>
            </div>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <i class="fa fa-map-marker fa-2x" style="color:darkpurple; margin-right: 8px;"></i>
                <span>Eye Care</span>
            </div>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <i class="fa fa-map-marker fa-2x" style="color:gray; margin-right: 8px;"></i>
                <span>Hospice</span>
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <h5 style="color: #34495e; margin: 5px 0;">📊 Market Status:</h5>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <span style="color:red; font-size: 18px; margin-right: 8px;">●</span>
                <span>Overserved</span>
            </div>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <span style="color:yellow; font-size: 18px; margin-right: 8px;">●</span>
                <span>Adequately Served</span>
            </div>
            <div style="display: flex; align-items: center; margin: 3px 0;">
                <span style="color:green; font-size: 18px; margin-right: 8px;">●</span>
                <span>Underserved</span>
            </div>
        </div>
        
        <div style="font-size: 12px; color: #7f8c8d; border-top: 1px solid #ecf0f1; padding-top: 8px;">
            💡 Click markers for detailed facility information
        </div>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Save the map
        output_file = 'ssm_health_interactive_facility_map.html'
        m.save(output_file)
        
        print(f"✅ Interactive map created successfully!")
        print(f"📊 Added {facilities_added} facilities to the map")
        print(f"🗺️ Map saved to: {output_file}")
        
        return m
    
    def create_msa_heatmap(self):
        """Create a heatmap showing facility density by MSA"""
        print("Creating MSA facility density heatmap...")
        
        # Calculate facility density by MSA
        msa_density = self.df.groupby(['msa_name', 'msa_code']).agg({
            'facilities_per_100k': 'first',
            'msa_median_household_income': 'first',
            'median_age': 'first',
            'pct_65_plus': 'first'
        }).reset_index()
        
        # Create a separate map for MSA heatmap
        center_lat = 39.8283
        center_lon = -98.5795
        
        m_heatmap = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=5,
            tiles='CartoDB positron'
        )
        
        # Add facilities as heatmap points
        heatmap_data = []
        
        for idx, row in self.df.iterrows():
            try:
                address = f"{row['street']}, {row['city']}, {row['state']} {row['zip']}"
                lat, lon = self.get_coordinates(address, row['city'], row['state'])
                
                if lat is not None and lon is not None:
                    # Weight by facility density
                    weight = row['facilities_per_100k']
                    heatmap_data.append([lat, lon, weight])
                
            except Exception as e:
                continue
        
        # Add heatmap layer
        plugins.HeatMap(
            heatmap_data,
            radius=25,
            blur=15,
            max_zoom=13,
            gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}
        ).add_to(m_heatmap)
        
        # Add MSA boundaries (simplified representation)
        for idx, msa_row in msa_density.iterrows():
            try:
                # Get a representative location for the MSA
                msa_facilities = self.df[self.df['msa_code'] == msa_row['msa_code']]
                if not msa_facilities.empty:
                    rep_facility = msa_facilities.iloc[0]
                    address = f"{rep_facility['street']}, {rep_facility['city']}, {rep_facility['state']} {rep_facility['zip']}"
                    lat, lon = self.get_coordinates(address, rep_facility['city'], rep_facility['state'])
                    
                    if lat is not None and lon is not None:
                        # Create MSA popup
                        msa_popup_html = f"""
                        <div style="width: 250px;">
                            <h4>{msa_row['msa_name']}</h4>
                            <p><strong>Facilities per 100k:</strong> {msa_row['facilities_per_100k']:.1f}</p>
                            <p><strong>Median Income:</strong> ${msa_row['msa_median_household_income']:,.0f}</p>
                            <p><strong>Median Age:</strong> {msa_row['median_age']:.1f} years</p>
                            <p><strong>Senior Population:</strong> {msa_row['pct_65_plus']:.1f}%</p>
                        </div>
                        """
                        
                        # Color based on facility density
                        if msa_row['facilities_per_100k'] > 50:
                            color = 'red'
                        elif msa_row['facilities_per_100k'] < 20:
                            color = 'green'
                        else:
                            color = 'yellow'
                        
                        folium.CircleMarker(
                            location=[lat, lon],
                            radius=msa_row['facilities_per_100k'] * 0.5,  # Size based on density
                            popup=folium.Popup(msa_popup_html, max_width=300),
                            color=color,
                            fill=True,
                            fillOpacity=0.7
                        ).add_to(m_heatmap)
                
            except Exception as e:
                continue
        
        # Save heatmap
        heatmap_file = 'ssm_health_msa_density_heatmap.html'
        m_heatmap.save(heatmap_file)
        
        print(f"✅ MSA density heatmap created!")
        print(f"🗺️ Heatmap saved to: {heatmap_file}")
        
        return m_heatmap
    
    def create_strategic_insights_map(self):
        """Create a map highlighting strategic insights and opportunities"""
        print("Creating strategic insights map...")
        
        # Analyze strategic opportunities
        msa_analysis = self.df.groupby(['msa_name', 'msa_code']).agg({
            'msa_median_household_income': 'first',
            'median_age': 'first',
            'facilities_per_100k': 'first',
            'pct_65_plus': 'first',
            'pct_under_18': 'first',
            'market_status': 'first'
        }).reset_index()
        
        # Identify opportunities
        high_income_underserved = msa_analysis[
            (msa_analysis['msa_median_household_income'] > 80000) & 
            (msa_analysis['market_status'] == 'Underserved')
        ]
        
        senior_opportunities = msa_analysis[
            (msa_analysis['pct_65_plus'] > 20) & 
            (msa_analysis['facilities_per_100k'] < 30)
        ]
        
        youth_opportunities = msa_analysis[
            (msa_analysis['pct_under_18'] > 25) & 
            (msa_analysis['facilities_per_100k'] < 25)
        ]
        
        overserved_markets = msa_analysis[msa_analysis['market_status'] == 'Overserved']
        
        # Create strategic map
        center_lat = 39.8283
        center_lon = -98.5795
        
        m_strategic = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=5,
            tiles='CartoDB positron'
        )
        
        # Add opportunity markers
        for category, data, color, icon in [
            ('High-Income Underserved', high_income_underserved, 'green', 'star'),
            ('Senior Population Opportunities', senior_opportunities, 'purple', 'heart'),
            ('Youth Population Opportunities', youth_opportunities, 'orange', 'child'),
            ('Overserved Markets (Risk)', overserved_markets, 'red', 'warning')
        ]:
            for idx, row in data.iterrows():
                try:
                    # Get representative facility for MSA
                    msa_facilities = self.df[self.df['msa_code'] == row['msa_code']]
                    if not msa_facilities.empty:
                        rep_facility = msa_facilities.iloc[0]
                        address = f"{rep_facility['street']}, {rep_facility['city']}, {rep_facility['state']} {rep_facility['zip']}"
                        lat, lon = self.get_coordinates(address, rep_facility['city'], rep_facility['state'])
                        
                        if lat is not None and lon is not None:
                            # Create strategic popup
                            if category == 'High-Income Underserved':
                                popup_text = f"<b>{category}</b><br>MSA: {row['msa_name']}<br>Income: ${row['msa_median_household_income']:,.0f}<br>Facilities per 100k: {row['facilities_per_100k']:.1f}"
                            elif category == 'Senior Population Opportunities':
                                popup_text = f"<b>{category}</b><br>MSA: {row['msa_name']}<br>Seniors: {row['pct_65_plus']:.1f}%<br>Facilities per 100k: {row['facilities_per_100k']:.1f}"
                            elif category == 'Youth Population Opportunities':
                                popup_text = f"<b>{category}</b><br>MSA: {row['msa_name']}<br>Youth: {row['pct_under_18']:.1f}%<br>Facilities per 100k: {row['facilities_per_100k']:.1f}"
                            else:
                                popup_text = f"<b>{category}</b><br>MSA: {row['msa_name']}<br>Facilities per 100k: {row['facilities_per_100k']:.1f}"
                            
                            folium.Marker(
                                location=[lat, lon],
                                popup=folium.Popup(popup_text, max_width=300),
                                tooltip=category,
                                icon=folium.Icon(color=color, icon=icon, prefix='fa')
                            ).add_to(m_strategic)
                    
                except Exception as e:
                    continue
        
        # Add legend for strategic map
        strategic_legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 250px; height: 200px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>Strategic Opportunities</h4>
        <p><i class="fa fa-star fa-2x" style="color:green"></i> High-Income Underserved</p>
        <p><i class="fa fa-heart fa-2x" style="color:purple"></i> Senior Opportunities</p>
        <p><i class="fa fa-child fa-2x" style="color:orange"></i> Youth Opportunities</p>
        <p><i class="fa fa-warning fa-2x" style="color:red"></i> Overserved Markets</p>
        </div>
        '''
        m_strategic.get_root().html.add_child(folium.Element(strategic_legend_html))
        
        # Save strategic map
        strategic_file = 'ssm_health_strategic_opportunities_map.html'
        m_strategic.save(strategic_file)
        
        print(f"✅ Strategic opportunities map created!")
        print(f"🗺️ Strategic map saved to: {strategic_file}")
        
        return m_strategic
    
    def run_complete_mapping_analysis(self):
        """Run the complete mapping analysis"""
        print("Starting comprehensive SSM Health facility mapping analysis...")
        print("=" * 70)
        
        # Create all maps
        print("\n1. Creating main interactive facility map...")
        main_map = self.create_interactive_map()
        
        print("\n2. Creating MSA density heatmap...")
        heatmap = self.create_msa_heatmap()
        
        print("\n3. Creating strategic opportunities map...")
        strategic_map = self.create_strategic_insights_map()
        
        # Create summary report
        self.create_mapping_summary()
        
        print("\n✅ Complete mapping analysis finished!")
        print("📊 Generated files:")
        print("  - ssm_health_interactive_facility_map.html (Main facility map)")
        print("  - ssm_health_msa_density_heatmap.html (MSA density heatmap)")
        print("  - ssm_health_strategic_opportunities_map.html (Strategic opportunities)")
        print("  - ssm_health_mapping_summary.md (Analysis summary)")
    
    def create_mapping_summary(self):
        """Create a summary report of the mapping analysis"""
        
        # Calculate key metrics
        total_facilities = len(self.df)
        total_msas = self.df['msa_code'].nunique()
        avg_facilities_per_100k = self.df['facilities_per_100k'].mean()
        avg_income = self.df['msa_median_household_income'].mean()
        avg_age = self.df['median_age'].mean()
        
        # Market status distribution
        market_distribution = self.df['market_status'].value_counts()
        
        # Facility type distribution
        facility_distribution = self.df['facility_category'].value_counts()
        
        # Age mix distribution
        age_mix_distribution = self.df['age_mix_category'].value_counts()
        
        # Income distribution
        income_distribution = self.df['income_category'].value_counts()
        
        summary = f"""
# SSM Health Facility Mapping Analysis Summary

## Overview
This analysis provides comprehensive mapping of SSM Health's facility network with demographic and market insights.

## Key Metrics
- **Total Facilities**: {total_facilities:,}
- **Markets Served (MSAs)**: {total_msas}
- **Average Facilities per 100k**: {avg_facilities_per_100k:.1f}
- **Average Median Income**: ${avg_income:,.0f}
- **Average Median Age**: {avg_age:.1f} years

## Market Status Distribution
{market_distribution.to_string()}

## Facility Type Distribution
{facility_distribution.to_string()}

## Age Mix Distribution
{age_mix_distribution.to_string()}

## Income Distribution
{income_distribution.to_string()}

## Map Features

### 1. Interactive Facility Map
- **File**: ssm_health_interactive_facility_map.html
- **Features**:
  - All facilities with detailed popups
  - Color-coded by facility type
  - Filterable by facility type and market status
  - Search functionality
  - Full demographic and economic data

### 2. MSA Density Heatmap
- **File**: ssm_health_msa_density_heatmap.html
- **Features**:
  - Heatmap showing facility density
  - MSA-level analysis
  - Market saturation visualization

### 3. Strategic Opportunities Map
- **File**: ssm_health_strategic_opportunities_map.html
- **Features**:
  - High-income underserved markets
  - Senior population opportunities
  - Youth population opportunities
  - Overserved market risks

## Strategic Insights

### Expansion Opportunities
- **High-Income Underserved**: {len(self.df[(self.df['msa_median_household_income'] > 80000) & (self.df['market_status'] == 'Underserved')])} markets
- **Senior-Focused**: {len(self.df[(self.df['pct_65_plus'] > 20) & (self.df['facilities_per_100k'] < 30)])} markets
- **Youth-Focused**: {len(self.df[(self.df['pct_under_18'] > 25) & (self.df['facilities_per_100k'] < 25)])} markets

### Risk Areas
- **Overserved Markets**: {len(self.df[self.df['market_status'] == 'Overserved'])} markets

## Usage Instructions

1. **Main Facility Map**: Use to explore individual facilities and their characteristics
2. **Density Heatmap**: Use to identify market saturation and coverage gaps
3. **Strategic Map**: Use to identify expansion opportunities and risks

## Data Quality Notes
- {self.df['age_mix_category'].value_counts().get('Unknown', 0)} locations have incomplete age data
- All facilities include MSA and income information
- Geographic coordinates obtained through geocoding with city-level fallback

---
*Analysis generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Save summary
        with open('ssm_health_mapping_summary.md', 'w') as f:
            f.write(summary)
        
        print("Mapping summary saved to ssm_health_mapping_summary.md")

def main():
    """Main function to run the mapping analysis"""
    print("SSM Health Interactive Facility Mapping Analysis")
    print("=" * 60)
    
    # Use the enriched data file
    input_file = 'ssm_health_locations_with_income_with_age_demographics.csv'
    
    try:
        # Initialize mapper
        mapper = InteractiveFacilityMapper(input_file)
        
        # Run complete mapping analysis
        mapper.run_complete_mapping_analysis()
        
    except Exception as e:
        print(f"❌ Error during mapping analysis: {e}")
        raise

if __name__ == "__main__":
    main() 