#!/usr/bin/env python3
"""
Add coordinates to attractiveness data using geocoding
"""

import pandas as pd
import requests
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

class CoordinateAdder:
    def __init__(self):
        """Initialize the coordinate adder"""
        self.geolocator = Nominatim(user_agent="SSMHealthMapper/1.0")
        self.coordinate_cache = {}
        
    def get_coordinates(self, address, city, state, zip_code):
        """Get coordinates for an address"""
        # Create cache key
        cache_key = f"{city}, {state} {zip_code}"
        
        # Check cache first
        if cache_key in self.coordinate_cache:
            return self.coordinate_cache[cache_key]
        
        try:
            # Try full address first
            full_address = f"{address}, {city}, {state} {zip_code}"
            location = self.geolocator.geocode(full_address, timeout=10)
            
            if location:
                coords = (location.latitude, location.longitude)
                self.coordinate_cache[cache_key] = coords
                return coords
            
            # Fallback to city, state, zip
            location = self.geolocator.geocode(cache_key, timeout=10)
            if location:
                coords = (location.latitude, location.longitude)
                self.coordinate_cache[cache_key] = coords
                return coords
                
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Geocoding error for {cache_key}: {e}")
        except Exception as e:
            print(f"Unexpected error for {cache_key}: {e}")
        
        return None, None
    
    def add_coordinates(self, input_file='ssm_health_locations_with_attractiveness_scores.csv'):
        """Add coordinates to the attractiveness data"""
        print("🗺️ Adding coordinates to attractiveness data...")
        
        # Load data
        df = pd.read_csv(input_file)
        print(f"📊 Loaded {len(df)} facilities")
        
        # Add coordinate columns
        df['lat'] = None
        df['lon'] = None
        
        # Process each facility
        for idx, row in df.iterrows():
            if idx % 50 == 0:
                print(f"Processing facility {idx+1}/{len(df)}...")
            
            # Get coordinates
            lat, lon = self.get_coordinates(
                row['street'], 
                row['city'], 
                row['state'], 
                row['zip']
            )
            
            df.at[idx, 'lat'] = lat
            df.at[idx, 'lon'] = lon
            
            # Rate limiting
            time.sleep(1)
        
        # Save enhanced data
        output_file = 'ssm_health_locations_with_attractiveness_scores_and_coords.csv'
        df.to_csv(output_file, index=False)
        
        # Print summary
        valid_coords = df[df['lat'].notna() & df['lon'].notna()]
        print(f"✅ Enhanced data saved to {output_file}")
        print(f"📊 Coordinates added: {len(valid_coords)}/{len(df)} facilities ({len(valid_coords)/len(df)*100:.1f}%)")
        
        return df

def main():
    """Main function to add coordinates"""
    print("🗺️ Coordinate Adder for Attractiveness Data")
    print("=" * 50)
    
    adder = CoordinateAdder()
    
    try:
        # Add coordinates
        enhanced_df = adder.add_coordinates()
        
        print("\n🎉 Coordinate addition completed!")
        print("📊 New columns added:")
        print("  - lat (latitude)")
        print("  - lon (longitude)")
        
    except Exception as e:
        print(f"❌ Error adding coordinates: {e}")
        raise

if __name__ == "__main__":
    main() 