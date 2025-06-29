#!/usr/bin/env python3
"""
Download and prepare Oklahoma and Missouri ZIP code data
This script downloads ZIP code GeoJSON files for OK and MO states
"""

import requests
import json
import os
import zipfile
import io

def download_zip_geojson(state_code, state_name):
    """Download ZIP code GeoJSON for a specific state"""
    print(f"📥 Downloading {state_name} ZIP code data...")
    
    # URL for ZIP code tabulation areas (ZCTA) by state
    # Using Census Bureau's TIGER/Line files
    base_url = "https://www2.census.gov/geo/tiger/TIGER2022/ZCTA5"
    
    try:
        # Download the ZIP file
        url = f"{base_url}/tl_2022_us_zcta520.zip"
        print(f"  Downloading from: {url}")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Extract the ZIP file
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            # Find the GeoJSON file
            geojson_files = [f for f in zip_file.namelist() if f.endswith('.geojson')]
            if not geojson_files:
                print(f"  ❌ No GeoJSON file found in ZIP for {state_name}")
                return None
            
            geojson_file = geojson_files[0]
            print(f"  📄 Found GeoJSON file: {geojson_file}")
            
            # Extract and read the GeoJSON
            with zip_file.open(geojson_file) as f:
                geojson_data = json.load(f)
        
        # Filter for the specific state's ZIP codes
        print(f"  🔍 Filtering {state_name} ZIP codes...")
        
        # Define ZIP code ranges for each state
        zip_ranges = {
            'OK': [('73000', '74999')],  # Oklahoma ZIP codes
            'MO': [('63000', '65999')]   # Missouri ZIP codes
        }
        
        if state_code not in zip_ranges:
            print(f"  ❌ No ZIP range defined for {state_code}")
            return None
        
        # Filter features for the state
        filtered_features = []
        for feature in geojson_data['features']:
            zip_code = feature['properties'].get('ZCTA5CE20', '')
            if zip_code:
                # Check if ZIP code falls within the state's range
                for start_range, end_range in zip_ranges[state_code]:
                    if start_range <= zip_code <= end_range:
                        filtered_features.append(feature)
                        break
        
        # Create filtered GeoJSON
        filtered_geojson = {
            'type': 'FeatureCollection',
            'features': filtered_features
        }
        
        # Save the filtered GeoJSON
        output_file = f"zipcodes_{state_code.lower()}.geojson"
        with open(output_file, 'w') as f:
            json.dump(filtered_geojson, f)
        
        print(f"  ✅ Saved {len(filtered_features)} ZIP codes to {output_file}")
        return output_file
        
    except Exception as e:
        print(f"  ❌ Error downloading {state_name} data: {e}")
        return None

def create_combined_geojson():
    """Create combined GeoJSON for OK and MO"""
    print("🔗 Creating combined OK and MO GeoJSON...")
    
    combined_features = []
    
    # Load OK GeoJSON
    if os.path.exists('zipcodes_ok.geojson'):
        with open('zipcodes_ok.geojson', 'r') as f:
            ok_data = json.load(f)
            combined_features.extend(ok_data['features'])
            print(f"  ✅ Added {len(ok_data['features'])} OK ZIP codes")
    
    # Load MO GeoJSON
    if os.path.exists('zipcodes_mo.geojson'):
        with open('zipcodes_mo.geojson', 'r') as f:
            mo_data = json.load(f)
            combined_features.extend(mo_data['features'])
            print(f"  ✅ Added {len(mo_data['features'])} MO ZIP codes")
    
    # Create combined GeoJSON
    combined_geojson = {
        'type': 'FeatureCollection',
        'features': combined_features
    }
    
    # Save combined file
    with open('zipcodes_ok_mo.geojson', 'w') as f:
        json.dump(combined_geojson, f)
    
    print(f"  ✅ Combined GeoJSON saved with {len(combined_features)} ZIP codes")
    return 'zipcodes_ok_mo.geojson'

def extract_zip_codes_from_geojson(geojson_file):
    """Extract ZIP codes from GeoJSON and save to CSV"""
    print(f"📋 Extracting ZIP codes from {geojson_file}...")
    
    with open(geojson_file, 'r') as f:
        geojson_data = json.load(f)
    
    zip_codes = set()
    for feature in geojson_data['features']:
        zip_code = feature['properties'].get('ZCTA5CE20') or feature['properties'].get('ZCTA5CE10')
        if zip_code:
            zip_codes.add(str(zip_code).zfill(5))
    
    # Save to CSV
    import csv
    output_file = 'all_ok_mo_zips.csv'
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['zip'])
        for zip_code in sorted(zip_codes):
            writer.writerow([zip_code])
    
    print(f"  ✅ Extracted {len(zip_codes)} ZIP codes to {output_file}")
    return output_file

def main():
    """Main function to prepare OK and MO ZIP data"""
    print("🗺️ Oklahoma and Missouri ZIP Code Data Preparation")
    print("=" * 55)
    
    # Download individual state files
    ok_file = download_zip_geojson('OK', 'Oklahoma')
    mo_file = download_zip_geojson('MO', 'Missouri')
    
    if ok_file and mo_file:
        # Create combined GeoJSON
        combined_file = create_combined_geojson()
        
        # Extract ZIP codes to CSV
        zip_csv = extract_zip_codes_from_geojson(combined_file)
        
        print(f"\n🎉 OK and MO ZIP data preparation completed!")
        print(f"📊 Files created:")
        print(f"  • {ok_file} - Oklahoma ZIP codes")
        print(f"  • {mo_file} - Missouri ZIP codes")
        print(f"  • {combined_file} - Combined OK and MO ZIP codes")
        print(f"  • {zip_csv} - ZIP codes list for demographics fetching")
        
        print(f"\n💡 Next steps:")
        print(f"  • Run fetch_all_zip_demographics.py with {zip_csv}")
        print(f"  • Score the demographics with score_all_zip_demographics.py")
        print(f"  • Create the final map with create_final_zip_attractiveness_map.py")
        
    else:
        print("❌ Failed to download required ZIP code data")

if __name__ == "__main__":
    main() 