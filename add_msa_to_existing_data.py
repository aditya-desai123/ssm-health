#!/usr/bin/env python3
"""
Script to add MSA and population data to existing SSM health locations
using the Geography_MSA_ZIP_2018.csv file.

This script will:
1. Load the existing SSM health locations CSV
2. Load the Geography_MSA_ZIP_2018.csv mapping file
3. Match ZIP codes to get MSA and population data
4. Add new columns to the existing data
5. Save the enhanced dataset
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional

def load_geography_data(csv_path: str) -> pd.DataFrame:
    """
    Load the Geography_MSA_ZIP_2018.csv file
    
    Args:
        csv_path (str): Path to the geography CSV file
        
    Returns:
        pd.DataFrame: Geography data with ZIP to MSA mapping
    """
    print(f"Loading geography data from {csv_path}...")
    
    # Load the geography CSV
    geo_df = pd.read_csv(csv_path)
    
    print(f"Loaded {len(geo_df)} ZIP code records")
    print(f"Columns: {list(geo_df.columns)}")
    
    # Show sample data
    print("\nSample geography data:")
    print(geo_df.head())
    
    return geo_df

def load_ssm_data(csv_path: str) -> pd.DataFrame:
    """
    Load the existing SSM health locations CSV
    
    Args:
        csv_path (str): Path to the SSM locations CSV file
        
    Returns:
        pd.DataFrame: SSM locations data
    """
    print(f"Loading SSM health locations from {csv_path}...")
    
    # Load the SSM locations CSV
    ssm_df = pd.read_csv(csv_path)
    
    print(f"Loaded {len(ssm_df)} SSM location records")
    print(f"Columns: {list(ssm_df.columns)}")
    
    # Show sample data
    print("\nSample SSM data:")
    print(ssm_df.head())
    
    return ssm_df

def clean_zip_codes(df: pd.DataFrame, zip_column: str = 'zip') -> pd.DataFrame:
    """
    Clean ZIP codes in the dataframe
    
    Args:
        df (pd.DataFrame): DataFrame with ZIP codes
        zip_column (str): Name of the ZIP code column
        
    Returns:
        pd.DataFrame: DataFrame with cleaned ZIP codes
    """
    # Create a copy to avoid modifying original
    df_clean = df.copy()
    
    # Convert ZIP codes to string and clean them
    df_clean[zip_column] = df_clean[zip_column].astype(str)
    
    # Remove any non-numeric characters and ensure 5 digits
    df_clean[zip_column] = df_clean[zip_column].str.replace(r'[^\d]', '', regex=True)
    
    # Keep only 5-digit ZIP codes
    df_clean = df_clean[df_clean[zip_column].str.len() == 5]
    
    print(f"Cleaned ZIP codes: {len(df_clean)} records with valid 5-digit ZIP codes")
    
    return df_clean

def create_zip_msa_mapping(geo_df: pd.DataFrame) -> Dict[str, Dict]:
    """
    Create a ZIP code to MSA mapping dictionary
    
    Args:
        geo_df (pd.DataFrame): Geography dataframe
        
    Returns:
        Dict: ZIP code to MSA mapping
    """
    print("Creating ZIP to MSA mapping...")
    
    # Create mapping dictionary
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
    
    # Show some sample mappings
    sample_zips = list(zip_msa_mapping.keys())[:5]
    print("\nSample ZIP to MSA mappings:")
    for zip_code in sample_zips:
        mapping = zip_msa_mapping[zip_code]
        print(f"  {zip_code}: {mapping['cbsa_name']} (CBSA: {mapping['cbsa_code']}, Pop: {mapping['population_2016']:,.0f})")
    
    return zip_msa_mapping

def add_msa_data_to_ssm(ssm_df: pd.DataFrame, zip_msa_mapping: Dict[str, Dict]) -> pd.DataFrame:
    """
    Add MSA and population data to SSM locations dataframe
    
    Args:
        ssm_df (pd.DataFrame): SSM locations dataframe
        zip_msa_mapping (Dict): ZIP to MSA mapping
        
    Returns:
        pd.DataFrame: Enhanced SSM locations dataframe
    """
    print("Adding MSA and population data to SSM locations...")
    
    # Create a copy to avoid modifying original
    enhanced_df = ssm_df.copy()
    
    # Initialize new columns
    enhanced_df['msa_name'] = 'Unknown'
    enhanced_df['msa_code'] = '00000'
    enhanced_df['population_2016'] = np.nan
    enhanced_df['msa_source'] = 'Not Found'
    
    # Track statistics
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
    """
    Analyze the results of the MSA mapping
    
    Args:
        df (pd.DataFrame): Enhanced dataframe with MSA data
    """
    print("\n" + "="*50)
    print("ANALYSIS RESULTS")
    print("="*50)
    
    # Overall statistics
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
    
    # Sample of unmatched locations
    unmatched = df[df['msa_source'] == 'Not Found']
    if len(unmatched) > 0:
        print(f"\nSample of unmatched locations (first 5):")
        for idx, row in unmatched.head().iterrows():
            print(f"  {row['name']} - {row['address']} (ZIP: {row['zip']})")

def main():
    """Main function to process the data"""
    print("SSM Health Locations MSA Enhancement")
    print("="*50)
    
    # File paths
    geography_csv = "Geography_MSA_ZIP_2018.csv"
    ssm_csv = "ssm_health_locations.csv"
    output_csv = "ssm_health_locations_with_msa.csv"
    
    try:
        # Load data
        geo_df = load_geography_data(geography_csv)
        ssm_df = load_ssm_data(ssm_csv)
        
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
        sample_cols = ['name', 'address', 'zip', 'msa_name', 'msa_code', 'population_2016', 'msa_source']
        print(enhanced_df[sample_cols].head(10).to_string(index=False))
        
    except Exception as e:
        print(f"Error processing data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 