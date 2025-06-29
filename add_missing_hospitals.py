#!/usr/bin/env python3
"""
Add missing hospitals from masterlist to the main dataset
"""

import pandas as pd
import requests
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

def get_coordinates_for_address(address, city, state, zip_code):
    """Get coordinates for an address using geocoding"""
    geolocator = Nominatim(user_agent="SSMHealthMapper/1.0")
    
    try:
        # Try full address first
        full_address = f"{address}, {city}, {state} {zip_code}"
        location = geolocator.geocode(full_address, timeout=10)
        
        if location:
            return location.latitude, location.longitude
        
        # Fallback to city, state, zip
        location = geolocator.geocode(f"{city}, {state} {zip_code}", timeout=10)
        if location:
            return location.latitude, location.longitude
            
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"Geocoding error for {city}, {state} {zip_code}: {e}")
    except Exception as e:
        print(f"Unexpected error for {city}, {state} {zip_code}: {e}")
    
    return None, None

def add_missing_hospitals():
    """Add hospitals from masterlist that are missing from main dataset"""
    print("🏥 Adding missing hospitals from masterlist...")
    
    # Load the masterlist
    masterlist = pd.read_csv('hospitals_masterlist.csv', skiprows=2)
    masterlist = masterlist[masterlist['name'].notna()]
    masterlist = masterlist[masterlist['name'].str.strip() != '']
    
    # Load the main dataset
    main_data = pd.read_csv('ssm_health_locations_with_attractiveness_scores_and_coords.csv')
    
    print(f"  Masterlist has {len(masterlist)} hospitals")
    print(f"  Main dataset has {len(main_data)} facilities")
    
    # Get hospital names from both datasets
    masterlist_hospitals = set(masterlist['name'].str.strip().str.lower())
    main_hospitals = set(main_data[main_data['facility_type'] == 'Hospital']['name'].str.strip().str.lower())
    
    # Find missing hospitals
    missing_hospitals = masterlist_hospitals - main_hospitals
    print(f"  Found {len(missing_hospitals)} missing hospitals")
    
    if not missing_hospitals:
        print("  ✅ All hospitals from masterlist are already in the main dataset!")
        return
    
    # Get the missing hospital records from masterlist
    missing_records = masterlist[masterlist['name'].str.strip().str.lower().isin(missing_hospitals)]
    
    print(f"\n  Missing hospitals:")
    for _, hospital in missing_records.iterrows():
        print(f"    - {hospital['name']}")
    
    # Create new records for missing hospitals
    new_records = []
    
    for _, hospital in missing_records.iterrows():
        print(f"\n  Processing: {hospital['name']}")
        
        # Get coordinates
        lat, lon = get_coordinates_for_address(
            hospital['street'], 
            hospital['city'], 
            hospital['state'], 
            hospital['zip']
        )
        
        if lat and lon:
            print(f"    ✅ Found coordinates: {lat}, {lon}")
        else:
            print(f"    ⚠️ Could not get coordinates")
            # Use default coordinates for the state center as fallback
            state_coords = {
                'WI': (44.5, -89.5),
                'IL': (40.0, -89.0),
                'MO': (38.5, -92.5),
                'OK': (35.5, -97.5)
            }
            lat, lon = state_coords.get(hospital['state'], (39.0, -93.0))
            print(f"    Using fallback coordinates: {lat}, {lon}")
        
        # Create new record with same structure as main dataset
        new_record = {
            'name': hospital['name'],
            'street': hospital['street'],
            'city': hospital['city'],
            'state': hospital['state'],
            'zip': hospital['zip'],
            'type': '',
            'facility_type': 'Hospital',
            'specialty': hospital.get('specialty', ''),
            'link': hospital.get('link', ''),
            'msa_name': hospital.get('msa_name', ''),
            'msa_code': hospital.get('msa_code', ''),
            'msa_population': hospital.get('msa_population', ''),
            'msa_median_household_income': hospital.get('msa_median_household_income', ''),
            'pct_under_18': '',
            'pct_18_34': '',
            'pct_35_54': '',
            'pct_55_64': '',
            'pct_65_plus': '',
            'median_age': '',
            'msa_total_population': '',
            'age_mix_summary': '',
            'age_mix_category': '',
            'zip_total_population': '',
            'zip_population_density': '',
            'zip_median_household_income': '',
            'zip_median_home_value': '',
            'zip_population_growth_rate': '',
            'zip_under_5': '',
            'zip_age_5_17': '',
            'zip_age_18_24': '',
            'zip_age_25_34': '',
            'zip_age_35_44': '',
            'zip_age_45_54': '',
            'zip_age_55_64': '',
            'zip_age_65_74': '',
            'zip_age_75_84': '',
            'zip_age_85_plus': '',
            'zip_pct_under_5': '',
            'zip_pct_age_5_17': '',
            'zip_pct_age_18_24': '',
            'zip_pct_age_25_34': '',
            'zip_pct_age_35_44': '',
            'zip_pct_age_45_54': '',
            'zip_pct_age_55_64': '',
            'zip_pct_age_65_74': '',
            'zip_pct_age_75_84': '',
            'zip_pct_age_85_plus': '',
            'zip_growth_under_18': '',
            'zip_growth_18_34': '',
            'zip_growth_35_54': '',
            'zip_growth_55_64': '',
            'zip_growth_65_plus': '',
            'attractiveness_score': '',
            'attractiveness_category': '',
            'attractiveness_color': '',
            'density_score': '',
            'growth_score': '',
            'senior_score': '',
            'income_score': '',
            'young_family_score': '',
            'senior_population_pct': '',
            'young_family_pct': '',
            'lat': lat,
            'lon': lon
        }
        
        # Add supplemental attributes if available
        if 'fte_count' in hospital.index and pd.notna(hospital['fte_count']):
            new_record['fte_count'] = hospital['fte_count']
        if 'discharges (inpatient volume, 2023)' in hospital.index and pd.notna(hospital['discharges (inpatient volume, 2023)']):
            new_record['discharges (inpatient volume, 2023)'] = hospital['discharges (inpatient volume, 2023)']
        if 'patient_days (2023)' in hospital.index and pd.notna(hospital['patient_days (2023)']):
            new_record['patient_days (2023)'] = hospital['patient_days (2023)']
        if 'cmi (12/2023)' in hospital.index and pd.notna(hospital['cmi (12/2023)']):
            new_record['cmi (12/2023)'] = hospital['cmi (12/2023)']
        
        new_records.append(new_record)
        
        # Rate limiting
        time.sleep(1)
    
    # Add new records to main dataset
    if new_records:
        new_df = pd.DataFrame(new_records)
        updated_data = pd.concat([main_data, new_df], ignore_index=True)
        
        # Save updated dataset
        output_file = 'ssm_health_locations_with_attractiveness_scores_and_coords_updated.csv'
        updated_data.to_csv(output_file, index=False)
        
        print(f"\n✅ Added {len(new_records)} missing hospitals")
        print(f"✅ Updated dataset saved to: {output_file}")
        print(f"📊 Total facilities: {len(updated_data)}")
        
        # Show hospital count
        hospital_count = len(updated_data[updated_data['facility_type'] == 'Hospital'])
        print(f"🏥 Total hospitals: {hospital_count}")
        
        return output_file
    else:
        print("❌ No new records to add")
        return None

if __name__ == "__main__":
    add_missing_hospitals() 