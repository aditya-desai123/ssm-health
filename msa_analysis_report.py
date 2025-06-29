#!/usr/bin/env python3
"""
Generate a detailed analysis report of the MSA data added to SSM health locations.
"""

import pandas as pd
import numpy as np

def generate_msa_report(csv_path: str):
    """
    Generate a comprehensive MSA analysis report
    
    Args:
        csv_path (str): Path to the enhanced SSM locations CSV
    """
    print("SSM Health Locations MSA Analysis Report")
    print("="*60)
    
    # Load the enhanced data
    df = pd.read_csv(csv_path)
    
    print(f"Total SSM Health Locations: {len(df):,}")
    print(f"Locations with MSA data: {len(df[df['msa_source'] == 'Geography_MSA_ZIP_2018.csv']):,}")
    print(f"Match rate: {len(df[df['msa_source'] == 'Geography_MSA_ZIP_2018.csv'])/len(df)*100:.1f}%")
    
    # Filter to only locations with valid MSA data
    valid_msa_df = df[df['msa_source'] == 'Geography_MSA_ZIP_2018.csv'].copy()
    
    print(f"\n{'='*60}")
    print("TOP 15 METROPOLITAN STATISTICAL AREAS")
    print("="*60)
    
    # Top MSAs by number of locations
    top_msas = valid_msa_df['msa_name'].value_counts().head(15)
    
    print(f"{'Rank':<4} {'MSA Name':<50} {'Locations':<12} {'Total Pop (2016)':<15} {'Avg Pop/Location':<15}")
    print("-" * 100)
    
    for rank, (msa_name, location_count) in enumerate(top_msas.items(), 1):
        msa_data = valid_msa_df[valid_msa_df['msa_name'] == msa_name]
        total_pop = msa_data['population_2016'].sum()
        avg_pop = msa_data['population_2016'].mean()
        
        print(f"{rank:<4} {msa_name:<50} {location_count:<12} {total_pop:>12,.0f} {avg_pop:>14,.0f}")
    
    print(f"\n{'='*60}")
    print("POPULATION ANALYSIS")
    print("="*60)
    
    # Population statistics
    pop_stats = valid_msa_df['population_2016'].describe()
    
    print(f"Total population covered: {valid_msa_df['population_2016'].sum():,.0f}")
    print(f"Average population per location: {pop_stats['mean']:,.0f}")
    print(f"Median population per location: {pop_stats['50%']:,.0f}")
    print(f"Standard deviation: {pop_stats['std']:,.0f}")
    print(f"Minimum population: {pop_stats['min']:,.0f}")
    print(f"Maximum population: {pop_stats['max']:,.0f}")
    
    # Population distribution
    print(f"\nPopulation Distribution:")
    print(f"  < 10,000: {len(valid_msa_df[valid_msa_df['population_2016'] < 10000]):,} locations")
    print(f"  10,000 - 25,000: {len(valid_msa_df[(valid_msa_df['population_2016'] >= 10000) & (valid_msa_df['population_2016'] < 25000)]):,} locations")
    print(f"  25,000 - 50,000: {len(valid_msa_df[(valid_msa_df['population_2016'] >= 25000) & (valid_msa_df['population_2016'] < 50000)]):,} locations")
    print(f"  50,000 - 100,000: {len(valid_msa_df[(valid_msa_df['population_2016'] >= 50000) & (valid_msa_df['population_2016'] < 100000)]):,} locations")
    print(f"  > 100,000: {len(valid_msa_df[valid_msa_df['population_2016'] >= 100000]):,} locations")
    
    print(f"\n{'='*60}")
    print("GEOGRAPHIC DISTRIBUTION BY STATE")
    print("="*60)
    
    # Extract state from address for geographic analysis
    def extract_state(address):
        if pd.isna(address):
            return 'Unknown'
        parts = address.split(',')
        if len(parts) >= 3:
            state_zip = parts[2].strip()
            state = state_zip[:2].strip()
            return state
        return 'Unknown'
    
    valid_msa_df['state_extracted'] = valid_msa_df['address'].apply(extract_state)
    state_counts = valid_msa_df['state_extracted'].value_counts()
    
    print(f"{'State':<6} {'Locations':<12} {'Total Pop (2016)':<15} {'Avg Pop/Location':<15}")
    print("-" * 60)
    
    for state, count in state_counts.head(10).items():
        state_data = valid_msa_df[valid_msa_df['state_extracted'] == state]
        total_pop = state_data['population_2016'].sum()
        avg_pop = state_data['population_2016'].mean()
        
        print(f"{state:<6} {count:<12} {total_pop:>12,.0f} {avg_pop:>14,.0f}")
    
    print(f"\n{'='*60}")
    print("FACILITY TYPE ANALYSIS")
    print("="*60)
    
    # Analyze by facility type
    type_counts = valid_msa_df['type'].value_counts()
    
    print(f"{'Facility Type':<30} {'Count':<8} {'Avg Pop/Location':<15}")
    print("-" * 55)
    
    for facility_type, count in type_counts.head(10).items():
        type_data = valid_msa_df[valid_msa_df['type'] == facility_type]
        avg_pop = type_data['population_2016'].mean()
        
        print(f"{facility_type:<30} {count:<8} {avg_pop:>14,.0f}")
    
    print(f"\n{'='*60}")
    print("KEY INSIGHTS")
    print("="*60)
    
    # Key insights
    print("1. Geographic Concentration:")
    top_msa = valid_msa_df['msa_name'].value_counts().index[0]
    top_msa_count = valid_msa_df['msa_name'].value_counts().iloc[0]
    print(f"   - {top_msa} has the most SSM locations ({top_msa_count})")
    
    print("\n2. Population Coverage:")
    total_pop_covered = valid_msa_df['population_2016'].sum()
    print(f"   - SSM locations serve a total population of {total_pop_covered:,.0f} (2016)")
    
    print("\n3. Market Penetration:")
    avg_pop_per_location = valid_msa_df['population_2016'].mean()
    print(f"   - Average population per location: {avg_pop_per_location:,.0f}")
    
    print("\n4. Geographic Diversity:")
    unique_msas = valid_msa_df['msa_name'].nunique()
    print(f"   - SSM operates in {unique_msas} different Metropolitan Statistical Areas")
    
    print("\n5. Facility Distribution:")
    most_common_type = valid_msa_df['type'].value_counts().index[0]
    most_common_count = valid_msa_df['type'].value_counts().iloc[0]
    print(f"   - Most common facility type: {most_common_type} ({most_common_count} locations)")
    
    # Save detailed report to file
    report_file = "msa_analysis_report.txt"
    with open(report_file, 'w') as f:
        f.write("SSM Health Locations MSA Analysis Report\n")
        f.write("="*60 + "\n\n")
        f.write(f"Generated on: {pd.Timestamp.now()}\n\n")
        f.write(f"Total SSM Health Locations: {len(df):,}\n")
        f.write(f"Locations with MSA data: {len(valid_msa_df):,}\n")
        f.write(f"Match rate: {len(valid_msa_df)/len(df)*100:.1f}%\n\n")
        
        f.write("TOP 15 METROPOLITAN STATISTICAL AREAS\n")
        f.write("-" * 50 + "\n")
        for rank, (msa_name, location_count) in enumerate(top_msas.items(), 1):
            msa_data = valid_msa_df[valid_msa_df['msa_name'] == msa_name]
            total_pop = msa_data['population_2016'].sum()
            avg_pop = msa_data['population_2016'].mean()
            f.write(f"{rank}. {msa_name}: {location_count} locations, {total_pop:,.0f} total pop, {avg_pop:,.0f} avg pop/location\n")
    
    print(f"\nDetailed report saved to: {report_file}")

if __name__ == "__main__":
    generate_msa_report("ssm_health_locations_with_msa.csv") 