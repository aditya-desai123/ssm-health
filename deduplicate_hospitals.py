#!/usr/bin/env python3
"""
Deduplicate hospital entries in the dataset
Keep only the main hospital entries, remove duplicate service/clinic entries
"""

import pandas as pd
import re

def deduplicate_hospitals():
    """Deduplicate hospital entries in the dataset"""
    print("🏥 Deduplicating hospital entries...")
    
    # Load the dataset
    df = pd.read_csv('ssm_health_locations_with_attractiveness_scores_and_coords.csv')
    print(f"  Original dataset: {len(df)} facilities")
    
    # Get hospital entries
    hospitals = df[df['facility_type'] == 'Hospital'].copy()
    print(f"  Original hospitals: {len(hospitals)}")
    
    # Load masterlist to get the exact hospital names we want to keep
    masterlist = pd.read_csv('hospitals_masterlist.csv', skiprows=2)
    masterlist = masterlist[masterlist['name'].notna()]
    masterlist = masterlist[masterlist['name'].str.strip() != '']
    
    masterlist_hospital_names = set(masterlist['name'].str.strip().str.lower())
    print(f"  Masterlist hospitals: {len(masterlist_hospital_names)}")
    
    # Function to check if a hospital name is a main hospital (exact match with masterlist)
    def is_main_hospital(name):
        name_lower = name.lower().strip()
        
        # Check if it's an exact match with masterlist
        if name_lower in masterlist_hospital_names:
            return True
        
        return False
    
    # Identify main hospitals vs service/clinic entries
    hospitals['is_main_hospital'] = hospitals['name'].apply(is_main_hospital)
    
    main_hospitals = hospitals[hospitals['is_main_hospital'] == True]
    service_entries = hospitals[hospitals['is_main_hospital'] == False]
    
    print(f"  Main hospitals (exact matches): {len(main_hospitals)}")
    print(f"  Service/clinic entries: {len(service_entries)}")
    
    # Show the main hospitals we're keeping
    print(f"\n  Main hospitals to keep:")
    for _, hospital in main_hospitals.iterrows():
        print(f"    - {hospital['name']}")
    
    # Show some examples of service entries we're removing
    print(f"\n  Examples of service entries being removed:")
    for _, hospital in service_entries.head(10).iterrows():
        print(f"    - {hospital['name']}")
    
    # Create new dataset: keep all non-hospital entries + only main hospitals
    non_hospitals = df[df['facility_type'] != 'Hospital']
    deduplicated_df = pd.concat([non_hospitals, main_hospitals.drop('is_main_hospital', axis=1)], ignore_index=True)
    
    print(f"\n  Final dataset: {len(deduplicated_df)} facilities")
    print(f"  Final hospitals: {len(deduplicated_df[deduplicated_df['facility_type'] == 'Hospital'])}")
    
    # Save deduplicated dataset
    output_file = 'ssm_health_locations_with_attractiveness_scores_and_coords_deduplicated.csv'
    deduplicated_df.to_csv(output_file, index=False)
    
    print(f"✅ Deduplicated dataset saved to: {output_file}")
    
    # Replace original file
    import shutil
    shutil.copy(output_file, 'ssm_health_locations_with_attractiveness_scores_and_coords.csv')
    print(f"✅ Replaced original dataset with deduplicated version")
    
    return output_file

if __name__ == "__main__":
    deduplicate_hospitals() 