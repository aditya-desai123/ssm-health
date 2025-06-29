#!/usr/bin/env python3
"""
Simple summary of MSA data added to SSM health locations.
"""

import pandas as pd

def simple_summary():
    """Generate a simple summary of the MSA data"""
    
    # Load the enhanced data
    df = pd.read_csv("ssm_health_locations_with_msa.csv")
    
    print("SSM Health Locations MSA Summary")
    print("="*50)
    print(f"Total locations: {len(df):,}")
    print(f"Locations with MSA data: {len(df[df['msa_source'] == 'Geography_MSA_ZIP_2018.csv']):,}")
    print(f"Match rate: {len(df[df['msa_source'] == 'Geography_MSA_ZIP_2018.csv'])/len(df)*100:.1f}%")
    
    # Filter to valid MSA data
    valid_df = df[df['msa_source'] == 'Geography_MSA_ZIP_2018.csv'].copy()
    
    print(f"\nTop 10 MSAs by number of locations:")
    print("-" * 50)
    
    msa_counts = valid_df['msa_name'].value_counts().head(10)
    for i, (msa_name, count) in enumerate(msa_counts.items(), 1):
        msa_data = valid_df[valid_df['msa_name'] == msa_name]
        total_pop = msa_data['population_2016'].sum()
        avg_pop = msa_data['population_2016'].mean()
        
        print(f"{i:2d}. {msa_name}")
        print(f"    Locations: {count}, Total Pop: {total_pop:,.0f}, Avg Pop/Location: {avg_pop:,.0f}")
        print()
    
    print(f"Population Statistics:")
    print("-" * 50)
    print(f"Total population covered: {valid_df['population_2016'].sum():,.0f}")
    print(f"Average population per location: {valid_df['population_2016'].mean():,.0f}")
    print(f"Median population per location: {valid_df['population_2016'].median():,.0f}")
    print(f"Min population: {valid_df['population_2016'].min():,.0f}")
    print(f"Max population: {valid_df['population_2016'].max():,.0f}")
    
    print(f"\nUnique MSAs: {valid_df['msa_name'].nunique()}")
    
    # Show sample of enhanced data
    print(f"\nSample of enhanced data:")
    print("-" * 50)
    sample_cols = ['name', 'zip', 'msa_name', 'msa_code', 'population_2016']
    print(valid_df[sample_cols].head(10).to_string(index=False))

if __name__ == "__main__":
    simple_summary() 