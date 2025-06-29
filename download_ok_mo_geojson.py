import requests
import zipfile
import os
import json
import pandas as pd

def download_and_extract_zip_geojson():
    """Download and extract ZIP code GeoJSON for MO and OK using real ZIP codes"""
    print("Downloading ZIP code GeoJSON for MO and OK...")
    
    # Create directories if they don't exist
    os.makedirs('geojson', exist_ok=True)
    
    # Download URL for ZIP code tabulation areas
    url = f"https://www2.census.gov/geo/tiger/TIGER2022/ZCTA520/tl_2022_us_zcta520.zip"
    
    zip_filename = f"geojson/us_zcta5.zip"
    geojson_filename = f"geojson/us_zcta5.geojson"
    
    try:
        # Download the file
        print(f"Downloading from {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(zip_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded to {zip_filename}")
        
        # Extract the ZIP file
        print("Extracting ZIP file...")
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall('geojson')
        
        # Find the extracted .shp file and convert to GeoJSON
        shp_files = [f for f in os.listdir('geojson') if f.endswith('.shp')]
        if shp_files:
            shp_file = shp_files[0]
            print(f"Found shapefile: {shp_file}")
            
            # Use ogr2ogr to convert to GeoJSON (if available)
            import subprocess
            try:
                cmd = f"ogr2ogr -f GeoJSON {geojson_filename} geojson/{shp_file}"
                subprocess.run(cmd, shell=True, check=True)
                print(f"Converted to GeoJSON: {geojson_filename}")
                
                # Filter to only include ZIP codes for MO and OK
                filter_zip_codes_for_mo_ok(geojson_filename)
                
            except subprocess.CalledProcessError:
                print("ogr2ogr not available, trying alternative method...")
                # Alternative: use geopandas if available
                try:
                    import geopandas as gpd
                    gdf = gpd.read_file(f"geojson/{shp_file}")
                    gdf.to_file(geojson_filename, driver='GeoJSON')
                    print(f"Converted to GeoJSON using geopandas: {geojson_filename}")
                    filter_zip_codes_for_mo_ok(geojson_filename)
                except ImportError:
                    print("geopandas not available. Please install it or use ogr2ogr.")
                    return None
        else:
            print("No shapefile found in extracted ZIP")
            return None
            
    except Exception as e:
        print(f"Error downloading/extracting: {e}")
        return None
    
    return geojson_filename

def filter_zip_codes_for_mo_ok(geojson_file):
    """Filter ZIP codes to only include those in MO and OK from all_ok_mo_zips.csv"""
    print("Filtering ZIP codes for MO and OK using real ZIP list...")
    
    # Load the real MO/OK ZIP codes
    try:
        mo_ok_zips = pd.read_csv('all_ok_mo_zips.csv')
        real_zip_set = set(str(zip_code).zfill(5) for zip_code in mo_ok_zips['zip'])
        print(f"Loaded {len(real_zip_set)} real MO/OK ZIP codes")
    except FileNotFoundError:
        print("all_ok_mo_zips.csv not found, using ZIP code ranges as fallback")
        # Fallback to ZIP code ranges
        real_zip_set = set()
        # Missouri ZIP codes: 63000-65899
        for zip_code in range(63000, 65900):
            real_zip_set.add(str(zip_code))
        # Oklahoma ZIP codes: 73000-74999
        for zip_code in range(73000, 75000):
            real_zip_set.add(str(zip_code))
        print(f"Using fallback: {len(real_zip_set)} ZIP codes from ranges")
    
    # Load the GeoJSON file
    with open(geojson_file, 'r') as f:
        data = json.load(f)
    
    # Filter features to only include ZIP codes in our real ZIP set
    filtered_features = []
    for feature in data['features']:
        zip_code = feature['properties'].get('ZCTA5CE20', '')
        if zip_code in real_zip_set:
            filtered_features.append(feature)
    
    # Create filtered GeoJSON
    filtered_data = {
        'type': 'FeatureCollection',
        'features': filtered_features
    }
    
    # Save filtered GeoJSON
    filtered_filename = f"zipcodes_mo_ok.geojson"
    with open(filtered_filename, 'w') as f:
        json.dump(filtered_data, f)
    
    print(f"Filtered to {len(filtered_features)} ZIP codes for MO and OK")
    print(f"Saved to: {filtered_filename}")
    
    # Extract ZIP codes to CSV for verification
    zip_codes = [feature['properties']['ZCTA5CE20'] for feature in filtered_features]
    zip_df = pd.DataFrame({'zip': zip_codes})
    csv_filename = f"mo_ok_extracted_zips.csv"
    zip_df.to_csv(csv_filename, index=False)
    print(f"Saved {len(zip_codes)} ZIP codes to: {csv_filename}")

def main():
    """Download ZIP code GeoJSON for Oklahoma and Missouri"""
    print(f"\n{'='*50}")
    print("Processing MO and OK ZIP polygons")
    print(f"{'='*50}")
    
    result = download_and_extract_zip_geojson()
    if result:
        print(f"Successfully created MO/OK ZIP polygons")
    else:
        print(f"Failed to create MO/OK ZIP polygons")

if __name__ == "__main__":
    main() 