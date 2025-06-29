#!/usr/bin/env python3
"""
Robust script to add MSA and population data to existing SSM health locations
using the Geography_MSA_ZIP_2018.csv file.

This script handles CSV formatting issues and focuses on the essential columns.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional

def load_geography_data(csv_path: str) -> pd.DataFrame:
    """Load the Geography_MSA_ZIP_2018.csv file"""
    print(f"Loading geography data from {csv_path}...")
    
    geo_df = pd.read_csv(csv_path)
    print(f"Loaded {len(geo_df)} ZIP code records")
    
    return geo_df

def load_ssm_data_robust(csv_path: str) -> pd.DataFrame:
    """Load SSM data with error handling for CSV formatting issues"""
    print(f"Loading SSM health locations from {csv_path}...")
    
    try:
        # Try to read with error handling (newer pandas syntax)
        ssm_df = pd.read_csv(csv_path, on_bad_lines='skip')
        print(f"Loaded {len(ssm_df)} SSM location records")
        return ssm_df
    except Exception as e:
        print(f"Error with standard CSV reading: {e}")
        
        # Try alternative approach - read with different parameters
        try:
            ssm_df = pd.read_csv(csv_path, engine='python', on_bad_lines='skip')
            print(f"Loaded {len(ssm_df)} SSM location records (with python engine)")
            return ssm_df
        except Exception as e2:
            print(f"Error with python engine: {e2}")
            
            # Last resort - read line by line
            print("Attempting to read CSV line by line...")
            lines = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i == 0:  # Header
                        lines.append(line.strip())
                    elif i < 1000:  # Limit to first 1000 lines to avoid issues
                        lines.append(line.strip())
            
            # Create DataFrame from lines
            from io import StringIO
            csv_content = '\n'.join(lines)
            ssm_df = pd.read_csv(StringIO(csv_content), on_bad_lines='skip')
            print(f"Loaded {len(ssm_df)} SSM location records (line by line)")
            return ssm_df

def clean_zip_codes(df: pd.DataFrame, zip_column: str = 'zip') -> pd.DataFrame:
    """Clean ZIP codes in the dataframe"""
    df_clean = df.copy()
    
    # Check if zip column exists
    if zip_column not in df_clean.columns:
        print(f"Warning: '{zip_column}' column not found. Available columns: {list(df_clean.columns)}")
        return df_clean
    
    # Convert ZIP codes to string and clean them
    df_clean[zip_column] = df_clean[zip_column].astype(str)
    df_clean[zip_column] = df_clean[zip_column].str.replace(r'[^\d]', '', regex=True)
    
    # Keep only 5-digit ZIP codes
    df_clean = df_clean[df_clean[zip_column].str.len() == 5]
    
    print(f"Cleaned ZIP codes: {len(df_clean)} records with valid 5-digit ZIP codes")
    return df_clean

def create_zip_msa_mapping(geo_df: pd.DataFrame) -> Dict[str, Dict]:
    """Create a ZIP code to MSA mapping dictionary"""
    print("Creating ZIP to MSA mapping...")
    
    zip_msa_mapping = {}
    
    for _, row in geo_df.iterrows():
        zip_code = str(row['zip']).zfill(5)  # Ensure 5 digits
        cbsa_code = str(row['cbsa10'])
        cbsa_name = row['cbsa_name']
        population = row['population_2016']
        
        zip_msa_mapping[zip_code] = {
            'cbsa_code': cbsa_code,
            'cbsa_name': cbsa_name,
            'population_2016': population
        }
    
    print(f"Created mapping for {len(zip_msa_mapping)} unique ZIP codes")
    return zip_msa_mapping

def add_msa_data_to_ssm(ssm_df: pd.DataFrame, zip_msa_mapping: Dict[str, Dict]) -> pd.DataFrame:
    """Add MSA and population data to SSM locations dataframe"""
    print("Adding MSA and population data to SSM locations...")
    
    enhanced_df = ssm_df.copy()
    
    # Initialize new columns
    enhanced_df['msa_name'] = 'Unknown'
    enhanced_df['msa_code'] = '00000'
    enhanced_df['population_2016'] = np.nan
    enhanced_df['msa_source'] = 'Not Found'
    
    matched_count = 0
    total_count = len(enhanced_df)
    
    # Process each row
    for idx, row in enhanced_df.iterrows():
        zip_code = str(row['zip']).zfill(5) if pd.notna(row['zip']) else None
        
        if zip_code and zip_code in zip_msa_mapping:
            mapping = zip_msa_mapping[zip_code]
            enhanced_df.at[idx, 'msa_name'] = mapping['cbsa_name']
            enhanced_df.at[idx, 'msa_code'] = mapping['cbsa_code']
            enhanced_df.at[idx, 'population_2016'] = mapping['population_2016']
            enhanced_df.at[idx, 'msa_source'] = 'Geography_MSA_ZIP_2018.csv'
            matched_count += 1
    
    print(f"MSA data added: {matched_count}/{total_count} locations matched ({matched_count/total_count*100:.1f}%)")
    return enhanced_df

def analyze_results(df: pd.DataFrame) -> None:
    """Analyze the results of the MSA mapping"""
    print("\n" + "="*50)
    print("ANALYSIS RESULTS")
    print("="*50)
    
    total_locations = len(df)
    matched_locations = len(df[df['msa_source'] == 'Geography_MSA_ZIP_2018.csv'])
    unmatched_locations = total_locations - matched_locations
    
    print(f"Total locations: {total_locations}")
    print(f"Locations with MSA data: {matched_locations} ({matched_locations/total_locations*100:.1f}%)")
    print(f"Locations without MSA data: {unmatched_locations} ({unmatched_locations/total_locations*100:.1f}%)")
    
    # Top MSAs
    print("\nTop 10 MSAs by number of locations:")
    msa_counts = df[df['msa_source'] == 'Geography_MSA_ZIP_2018.csv']['msa_name'].value_counts().head(10)
    for msa, count in msa_counts.items():
        print(f"  {msa}: {count} locations")
    
    # Population statistics
    print("\nPopulation statistics (2016):")
    population_data = df[df['population_2016'].notna()]['population_2016']
    if len(population_data) > 0:
        print(f"  Total population covered: {population_data.sum():,.0f}")
        print(f"  Average population per location: {population_data.mean():,.0f}")
        print(f"  Median population per location: {population_data.median():,.0f}")
        print(f"  Min population: {population_data.min():,.0f}")
        print(f"  Max population: {population_data.max():,.0f}")

def main():
    """Main function to process the data"""
    print("Robust SSM Health Locations MSA Enhancement")
    print("="*50)
    
    # File paths
    geography_csv = "Geography_MSA_ZIP_2018.csv"
    ssm_csv = "ssm_health_locations.csv"
    output_csv = "ssm_health_locations_with_msa_robust.csv"
    
    try:
        # Load data
        geo_df = load_geography_data(geography_csv)
        ssm_df = load_ssm_data_robust(ssm_csv)
        
        # Show what columns we have
        print(f"\nAvailable columns in SSM data: {list(ssm_df.columns)}")
        print(f"Sample data:")
        print(ssm_df.head(3))
        
        # Clean ZIP codes
        ssm_df_clean = clean_zip_codes(ssm_df)
        
        # Create ZIP to MSA mapping
        zip_msa_mapping = create_zip_msa_mapping(geo_df)
        
        # Add MSA data to SSM locations
        enhanced_df = add_msa_data_to_ssm(ssm_df_clean, zip_msa_mapping)
        
        # Analyze results
        analyze_results(enhanced_df)
        
        # Save enhanced data
        print(f"\nSaving enhanced data to {output_csv}...")
        enhanced_df.to_csv(output_csv, index=False)
        print(f"Enhanced data saved successfully!")
        
        # Show sample of enhanced data
        print("\nSample of enhanced data:")
        sample_cols = ['name', 'zip', 'msa_name', 'msa_code', 'population_2016', 'msa_source']
        available_cols = [col for col in sample_cols if col in enhanced_df.columns]
        print(enhanced_df[available_cols].head(10).to_string(index=False))
        
    except Exception as e:
        print(f"Error processing data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 