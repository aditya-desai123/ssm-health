#!/usr/bin/env python3
"""
Clean MSA Names - Replace "Micropolitan Statistical Area" with "Metropolitan Statistical Area"
Also fix 99999 MSA codes by looking up correct MSA code and demographics.
"""

import pandas as pd
import os

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

def fix_remaining_99999_msa_codes(main_csv='ssm_health_locations_with_income_with_age_demographics.csv'):
    """
    Manually fix the remaining 99999 MSA codes with the correct data provided by the user
    """
    print(f"\n🔧 Manually fixing remaining 99999 MSA codes in {main_csv}...")
    
    # Manual mappings provided by user
    manual_mappings = {
        ('Okemah', 'OK', '74859'): {
            'msa_code': '36220',
            'msa_name': 'Shawnee, OK Metropolitan Statistical Area',
            'msa_population': 70000  # Approximate population for Shawnee MSA
        },
        ('Pauls Valley', 'OK', '73075'): {
            'msa_code': '29860',
            'msa_name': 'Pauls Valley, OK Metropolitan Statistical Area',
            'msa_population': 12000  # Approximate population for Pauls Valley MSA
        },
        ('Flora', 'IL', '62839'): {
            'msa_code': '21740',
            'msa_name': 'Flora, IL Metropolitan Statistical Area',
            'msa_population': 38000  # Approximate population for Flora MSA
        },
        ('Benton', 'IL', '62812'): {
            'msa_code': '21780',
            'msa_name': 'Franklin County, IL (Benton area) Metropolitan Statistical Area',
            'msa_population': 38000  # Approximate population for Franklin County MSA
        },
        ('Seminole', 'OK', '74868'): {
            'msa_code': '44740',
            'msa_name': 'Seminole, OK Metropolitan Statistical Area',
            'msa_population': 25000  # Approximate population for Seminole MSA
        }
    }
    
    df = pd.read_csv(main_csv)
    fixed = 0
    
    for idx, row in df[df['msa_code'] == 99999].iterrows():
        city = str(row['city']).strip()
        state = str(row['state']).strip()
        zip_code = str(row['zip']).zfill(5) if 'zip' in row and pd.notna(row['zip']) else None
        
        # Check if we have a manual mapping for this city/state/zip
        key = (city, state, zip_code)
        if key in manual_mappings:
            mapping = manual_mappings[key]
            df.at[idx, 'msa_code'] = mapping['msa_code']
            df.at[idx, 'msa_name'] = mapping['msa_name']
            if 'msa_population' in df.columns:
                df.at[idx, 'msa_population'] = mapping['msa_population']
            fixed += 1
            print(f"  ✔️ Fixed {row['name']} ({city}, {state}) -> {mapping['msa_name']} [{mapping['msa_code']}]")
    
    # Save the updated file
    df.to_csv(main_csv, index=False)
    print(f"\n✅ Manually fixed {fixed} rows with 99999 MSA codes and updated {main_csv}")

def fix_99999_msa_codes(main_csv='ssm_health_locations_with_income_with_age_demographics.csv', msa_zip_csv='Geography_MSA_ZIP_2018.csv'):
    """
    For all rows with msa_code == 99999, look up the correct MSA code and demographics using city/state/zip.
    """
    print(f"\n🔍 Fixing 99999 MSA codes in {main_csv} using {msa_zip_csv}...")
    df = pd.read_csv(main_csv)
    msa_zip = pd.read_csv(msa_zip_csv, dtype={'zip': str, 'cbsa10': str})
    
    # Build a lookup by (city, state) and by zip
    msa_zip['zip_name_lower'] = msa_zip['zip_name'].str.lower().str.strip()
    msa_zip['state_abbreviation'] = msa_zip['state_abbreviation'].str.upper()
    msa_zip['cbsa10'] = msa_zip['cbsa10'].astype(str)
    
    # For each row with msa_code == 99999, try to fix
    fixed = 0
    for idx, row in df[df['msa_code'] == 99999].iterrows():
        city = str(row['city']).lower().strip()
        state = str(row['state']).upper().strip()
        zip_code = str(row['zip']).zfill(5) if 'zip' in row and pd.notna(row['zip']) else None
        # Try zip match first
        msa_row = None
        if zip_code:
            msa_row = msa_zip[msa_zip['zip'] == zip_code]
            if not msa_row.empty:
                msa_row = msa_row.iloc[0]
        # If not found, try city/state match
        if msa_row is None or msa_row is pd.Series() or msa_row.empty:
            msa_row = msa_zip[(msa_zip['zip_name_lower'] == city) & (msa_zip['state_abbreviation'] == state)]
            if not msa_row.empty:
                msa_row = msa_row.iloc[0]
        # If found, update
        if msa_row is not None and not isinstance(msa_row, pd.Series) and not msa_row.empty:
            msa_row = msa_row.iloc[0]
        if msa_row is not None and isinstance(msa_row, pd.Series) and not msa_row.empty:
            msa_row = msa_row.iloc[0]
        if msa_row is not None and isinstance(msa_row, pd.Series) and not msa_row.empty:
            df.at[idx, 'msa_code'] = msa_row['cbsa10']
            df.at[idx, 'msa_name'] = msa_row['cbsa_name']
            # Optionally update population if column exists
            if 'msa_population' in df.columns and 'population_2016' in msa_row:
                df.at[idx, 'msa_population'] = msa_row['population_2016']
            fixed += 1
            print(f"  ✔️ Fixed {row['name']} ({row['city']}, {row['state']}) -> {msa_row['cbsa_name']} [{msa_row['cbsa10']}]")
        else:
            print(f"  ❌ Could not fix {row['name']} ({row['city']}, {row['state']})")
    # Save
    df.to_csv(main_csv, index=False)
    print(f"\n✅ Fixed {fixed} rows with 99999 MSA codes and updated {main_csv}")

def clean_all_data_files():
    """Clean MSA names in all relevant data files"""
    
    # List of files to clean
    files_to_clean = [
        'ssm_health_locations_with_income_with_age_demographics.csv',
        'hospitals_masterlist.csv',
        'ssm_health_locations_categorized.csv',
        'ssm_health_hospitals_deduplicated.csv',
        'ssm_health_locations_hospitals.csv',
        'ssm_health_income_analysis.csv'
    ]
    
    for filename in files_to_clean:
        if os.path.exists(filename):
            try:
                print(f"\n🔄 Processing {filename}...")
                df = pd.read_csv(filename)
                
                # Clean MSA names in various possible column names
                msa_columns = ['msa_name', 'msa', 'MSA', 'msa_name_clean']
                for col in msa_columns:
                    if col in df.columns:
                        df = clean_msa_names(df, col)
                
                # Save the cleaned data back to the file
                df.to_csv(filename, index=False)
                print(f"✅ Saved cleaned data to {filename}")
                
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")
        else:
            print(f"⚠️ File {filename} not found, skipping...")

def main():
    """Main function to clean MSA names"""
    print("🧹 Starting MSA name cleaning process...")
    print("📝 Replacing 'Micropolitan Statistical Area' with 'Metropolitan Statistical Area'")
    
    clean_all_data_files()
    fix_99999_msa_codes()
    fix_remaining_99999_msa_codes()
    
    print("\n🎉 MSA name cleaning and 99999 code fixing completed!")
    print("📊 All data files have been updated with corrected MSA names and MSA codes")

if __name__ == "__main__":
    main() 