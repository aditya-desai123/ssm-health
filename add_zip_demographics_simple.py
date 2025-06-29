#!/usr/bin/env python3
"""
Add ZIP Code Level Demographics to SSM Health Facility Data (Simple Version)
Generates realistic ZIP-level demographics based on existing MSA data
"""

import pandas as pd
import numpy as np
import random
import warnings
warnings.filterwarnings('ignore')

class SimpleZIPDemographicsEnricher:
    def __init__(self):
        """Initialize the enricher"""
        self.random_seed = 42  # For reproducible results
        np.random.seed(self.random_seed)
        random.seed(self.random_seed)
    
    def get_zip_area_sq_miles(self, zip_code):
        """Get approximate ZIP code area in square miles based on ZIP patterns"""
        zip_str = str(zip_code).zfill(5)
        
        # Approximate areas based on ZIP patterns (rural vs urban)
        if zip_str.startswith(('10', '11', '12', '13', '14')):  # NYC area
            return 8.0  # Very dense urban
        elif zip_str.startswith(('60', '61', '62', '63', '64', '65', '66')):  # Illinois
            return 25.0  # Mixed urban/suburban
        elif zip_str.startswith(('73', '74')):  # Oklahoma
            return 45.0  # More rural
        elif zip_str.startswith(('53', '54', '55', '56', '57')):  # Wisconsin
            return 35.0  # Mixed rural/urban
        elif zip_str.startswith(('80', '81', '82', '83', '84', '85', '86', '87')):  # Mountain West
            return 60.0  # Rural
        elif zip_str.startswith(('90', '91', '92', '93', '94', '95', '96', '97', '98', '99')):  # West Coast
            return 20.0  # Urban/suburban
        else:
            return 30.0  # Default
    
    def generate_zip_demographics_from_msa(self, msa_population, msa_median_income, zip_code, city, state):
        """
        Generate realistic ZIP-level demographics based on MSA data
        """
        zip_str = str(zip_code).zfill(5)
        
        # Calculate ZIP area
        area_sq_miles = self.get_zip_area_sq_miles(zip_code)
        
        # Estimate ZIP population as a fraction of MSA population
        # Urban ZIPs have higher population density
        if zip_str.startswith(('10', '11', '12', '13', '14')):  # NYC area
            population_factor = 0.15  # Higher density
        elif zip_str.startswith(('60', '61', '62', '63', '64', '65', '66')):  # Illinois
            population_factor = 0.08  # Medium density
        elif zip_str.startswith(('73', '74')):  # Oklahoma
            population_factor = 0.05  # Lower density
        elif zip_str.startswith(('53', '54', '55', '56', '57')):  # Wisconsin
            population_factor = 0.06  # Medium-low density
        else:
            population_factor = 0.07  # Default
        
        # Add some randomness to make it realistic
        population_factor *= random.uniform(0.7, 1.3)
        
        total_population = int(msa_population * population_factor)
        
        # Generate age distribution based on typical patterns
        age_distribution = {
            'under_5': 0.06,      # 6% under 5
            'age_5_17': 0.16,     # 16% 5-17
            'age_18_24': 0.09,    # 9% 18-24
            'age_25_34': 0.13,    # 13% 25-34
            'age_35_44': 0.12,    # 12% 35-44
            'age_45_54': 0.13,    # 13% 45-54
            'age_55_64': 0.12,    # 12% 55-64
            'age_65_74': 0.09,    # 9% 65-74
            'age_75_84': 0.06,    # 6% 75-84
            'age_85_plus': 0.04   # 4% 85+
        }
        
        # Adjust for rural vs urban areas
        if area_sq_miles > 40:  # Rural areas tend to have older populations
            age_distribution['under_5'] *= 0.8
            age_distribution['age_5_17'] *= 0.9
            age_distribution['age_18_24'] *= 0.7
            age_distribution['age_65_74'] *= 1.2
            age_distribution['age_75_84'] *= 1.3
            age_distribution['age_85_plus'] *= 1.4
        
        # Calculate age group populations
        age_groups = {}
        for age_group, percentage in age_distribution.items():
            age_groups[age_group] = int(total_population * percentage)
        
        # Calculate percentages
        age_percentages = {}
        for age_group, population in age_groups.items():
            age_percentages[f'pct_{age_group}'] = (population / total_population * 100) if total_population > 0 else 0
        
        # Estimate household income (ZIP level can vary from MSA level)
        income_variation = random.uniform(0.8, 1.2)
        median_household_income = int(msa_median_income * income_variation)
        
        # Estimate home values (typically 3-5x annual income)
        home_value_multiplier = random.uniform(3.5, 4.5)
        median_home_value = int(median_household_income * home_value_multiplier)
        
        # Calculate population density
        population_density = total_population / area_sq_miles if area_sq_miles > 0 else 0
        
        # Estimate population growth rates
        base_growth_rate = 0.8  # Base 0.8% annual growth
        
        # Adjust based on region
        if zip_str.startswith(('60', '61', '62', '63', '64', '65', '66')):  # Illinois
            base_growth_rate = 0.2  # Slow growth
        elif zip_str.startswith(('73', '74')):  # Oklahoma
            base_growth_rate = 1.2  # Moderate growth
        elif zip_str.startswith(('53', '54', '55', '56', '57')):  # Wisconsin
            base_growth_rate = 0.5  # Slow growth
        elif zip_str.startswith(('80', '81', '82', '83', '84', '85', '86', '87')):  # Mountain West
            base_growth_rate = 2.0  # High growth
        
        # Add some randomness
        population_growth_rate = base_growth_rate * random.uniform(0.8, 1.2)
        
        # Growth rates by age group (seniors grow faster, young adults vary)
        growth_rates = {
            'growth_under_18': population_growth_rate * 0.8,
            'growth_18_34': population_growth_rate * 1.2,
            'growth_35_54': population_growth_rate * 0.9,
            'growth_55_64': population_growth_rate * 1.1,
            'growth_65_plus': population_growth_rate * 1.5
        }
        
        return {
            'total_population': total_population,
            'population_density': population_density,
            'median_household_income': median_household_income,
            'median_home_value': median_home_value,
            'population_growth_rate': population_growth_rate,
            **age_groups,
            **age_percentages,
            **growth_rates
        }
    
    def enrich_facility_data(self, input_file='ssm_health_locations_with_income_with_age_demographics.csv'):
        """
        Enrich facility data with ZIP code level demographics
        """
        print(f"🔍 Enriching facility data with ZIP code demographics...")
        
        # Load the data
        df = pd.read_csv(input_file)
        
        # Get unique ZIP codes
        unique_zips = df['zip'].dropna().unique()
        print(f"📊 Found {len(unique_zips)} unique ZIP codes to process")
        
        # Create a cache for ZIP code data
        zip_demographics = {}
        
        # Process each unique ZIP code
        for i, zip_code in enumerate(unique_zips):
            if pd.isna(zip_code) or zip_code == '':
                continue
                
            print(f"  Processing ZIP {zip_code} ({i+1}/{len(unique_zips)})...")
            
            # Find the MSA data for this ZIP code
            zip_data = df[df['zip'] == zip_code].iloc[0]
            
            # Get MSA population and income
            msa_population = zip_data.get('msa_population', 50000)  # Default if missing
            msa_median_income = zip_data.get('msa_median_income', 60000)  # Default if missing
            
            # Generate ZIP-level demographics
            demographics = self.generate_zip_demographics_from_msa(
                msa_population, msa_median_income, zip_code, 
                zip_data.get('city', ''), zip_data.get('state', '')
            )
            
            zip_demographics[zip_code] = demographics
        
        # Add the demographic columns to the dataframe
        print("📝 Adding demographic columns to facility data...")
        
        # Create new columns
        demographic_columns = [
            'zip_total_population', 'zip_population_density', 'zip_median_household_income',
            'zip_median_home_value', 'zip_population_growth_rate',
            'zip_under_5', 'zip_age_5_17', 'zip_age_18_24', 'zip_age_25_34',
            'zip_age_35_44', 'zip_age_45_54', 'zip_age_55_64', 'zip_age_65_74',
            'zip_age_75_84', 'zip_age_85_plus',
            'zip_pct_under_5', 'zip_pct_age_5_17', 'zip_pct_age_18_24', 'zip_pct_age_25_34',
            'zip_pct_age_35_44', 'zip_pct_age_45_54', 'zip_pct_age_55_64', 'zip_pct_age_65_74',
            'zip_pct_age_75_84', 'zip_pct_age_85_plus',
            'zip_growth_under_18', 'zip_growth_18_34', 'zip_growth_35_54',
            'zip_growth_55_64', 'zip_growth_65_plus'
        ]
        
        for col in demographic_columns:
            df[col] = 0
        
        # Fill in the data
        for idx, row in df.iterrows():
            zip_code = row['zip']
            if pd.notna(zip_code) and zip_code in zip_demographics:
                demo = zip_demographics[zip_code]
                
                df.at[idx, 'zip_total_population'] = demo.get('total_population', 0)
                df.at[idx, 'zip_population_density'] = demo.get('population_density', 0)
                df.at[idx, 'zip_median_household_income'] = demo.get('median_household_income', 0)
                df.at[idx, 'zip_median_home_value'] = demo.get('median_home_value', 0)
                df.at[idx, 'zip_population_growth_rate'] = demo.get('population_growth_rate', 0)
                
                # Age groups
                df.at[idx, 'zip_under_5'] = demo.get('under_5', 0)
                df.at[idx, 'zip_age_5_17'] = demo.get('age_5_17', 0)
                df.at[idx, 'zip_age_18_24'] = demo.get('age_18_24', 0)
                df.at[idx, 'zip_age_25_34'] = demo.get('age_25_34', 0)
                df.at[idx, 'zip_age_35_44'] = demo.get('age_35_44', 0)
                df.at[idx, 'zip_age_45_54'] = demo.get('age_45_54', 0)
                df.at[idx, 'zip_age_55_64'] = demo.get('age_55_64', 0)
                df.at[idx, 'zip_age_65_74'] = demo.get('age_65_74', 0)
                df.at[idx, 'zip_age_75_84'] = demo.get('age_75_84', 0)
                df.at[idx, 'zip_age_85_plus'] = demo.get('age_85_plus', 0)
                
                # Percentages
                df.at[idx, 'zip_pct_under_5'] = demo.get('pct_under_5', 0)
                df.at[idx, 'zip_pct_age_5_17'] = demo.get('pct_age_5_17', 0)
                df.at[idx, 'zip_pct_age_18_24'] = demo.get('pct_age_18_24', 0)
                df.at[idx, 'zip_pct_age_25_34'] = demo.get('pct_age_25_34', 0)
                df.at[idx, 'zip_pct_age_35_44'] = demo.get('pct_age_35_44', 0)
                df.at[idx, 'zip_pct_age_45_54'] = demo.get('pct_age_45_54', 0)
                df.at[idx, 'zip_pct_age_55_64'] = demo.get('pct_age_55_64', 0)
                df.at[idx, 'zip_pct_age_65_74'] = demo.get('pct_age_65_74', 0)
                df.at[idx, 'zip_pct_age_75_84'] = demo.get('pct_age_75_84', 0)
                df.at[idx, 'zip_pct_age_85_plus'] = demo.get('pct_age_85_plus', 0)
                
                # Growth rates
                df.at[idx, 'zip_growth_under_18'] = demo.get('growth_under_18', 0)
                df.at[idx, 'zip_growth_18_34'] = demo.get('growth_18_34', 0)
                df.at[idx, 'zip_growth_35_54'] = demo.get('growth_35_54', 0)
                df.at[idx, 'zip_growth_55_64'] = demo.get('growth_55_64', 0)
                df.at[idx, 'zip_growth_65_plus'] = demo.get('growth_65_plus', 0)
        
        # Save the enriched data
        output_file = 'ssm_health_locations_with_zip_demographics.csv'
        df.to_csv(output_file, index=False)
        
        print(f"✅ Enriched data saved to {output_file}")
        print(f"📊 Added {len(demographic_columns)} new demographic columns")
        print(f"🏠 Processed {len(zip_demographics)} ZIP codes")
        
        # Print summary statistics
        print("\n📈 Summary Statistics:")
        print(f"  Average ZIP population: {df['zip_total_population'].mean():.0f}")
        print(f"  Average population density: {df['zip_population_density'].mean():.1f} people/sq mile")
        print(f"  Average median household income: ${df['zip_median_household_income'].mean():,.0f}")
        print(f"  Average population growth rate: {df['zip_population_growth_rate'].mean():.1f}%")
        
        # Show sample of new columns
        print("\n📋 Sample of new ZIP-level columns:")
        sample_cols = ['zip_total_population', 'zip_population_density', 'zip_median_household_income', 
                      'zip_pct_age_65_74', 'zip_growth_65_plus']
        for col in sample_cols:
            if col in df.columns:
                print(f"  {col}: {df[col].mean():.1f}")
        
        return df

def main():
    """Main function to run ZIP demographics enrichment"""
    print("🏠 SSM Health ZIP Code Demographics Enrichment (Simple Version)")
    print("=" * 60)
    
    enricher = SimpleZIPDemographicsEnricher()
    
    try:
        # Enrich the facility data
        enriched_df = enricher.enrich_facility_data()
        
        print("\n🎉 ZIP demographics enrichment completed!")
        print("📊 New columns added:")
        print("  - Population density (people per square mile)")
        print("  - Detailed age group populations and percentages")
        print("  - Population growth rates by age group")
        print("  - ZIP-level household income and home values")
        print("\n💡 This data is generated based on MSA-level data and realistic patterns.")
        print("   For more accurate data, consider using the Census API with a key.")
        
    except Exception as e:
        print(f"❌ Error during enrichment: {e}")
        raise

if __name__ == "__main__":
    main() 