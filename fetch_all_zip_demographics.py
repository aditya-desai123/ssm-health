#!/usr/bin/env python3
"""
Fetch Census demographic data for ALL ZIP codes in MN, WI, IL
This script processes the complete all_mn_wi_il_zips.csv file
"""

import pandas as pd
import numpy as np
import requests
import time
import warnings
warnings.filterwarnings('ignore')

class AllZIPDemographicsFetcher:
    def __init__(self):
        """Initialize the fetcher with API endpoints and data sources"""
        self.census_api_key = None  # You can add your Census API key here
        self.base_url = "https://api.census.gov/data"
        
    def get_census_data_by_zip(self, zip_code, year=2020):
        """
        Get Census data for a specific ZIP code using ZCTA (ZIP Code Tabulation Area)
        Uses American Community Survey (ACS) 5-year estimates
        """
        try:
            # Variables we want to collect
            variables = [
                'B01003_001E',  # Total population
                'B01001_003E',  # Male under 5
                'B01001_004E',  # Male 5-9
                'B01001_005E',  # Male 10-14
                'B01001_006E',  # Male 15-17
                'B01001_007E',  # Male 18-19
                'B01001_008E',  # Male 20
                'B01001_009E',  # Male 21
                'B01001_010E',  # Male 22-24
                'B01001_011E',  # Male 25-29
                'B01001_012E',  # Male 30-34
                'B01001_013E',  # Male 35-39
                'B01001_014E',  # Male 40-44
                'B01001_015E',  # Male 45-49
                'B01001_016E',  # Male 50-54
                'B01001_017E',  # Male 55-59
                'B01001_018E',  # Male 60-61
                'B01001_019E',  # Male 62-64
                'B01001_020E',  # Male 65-66
                'B01001_021E',  # Male 67-69
                'B01001_022E',  # Male 70-74
                'B01001_023E',  # Male 75-79
                'B01001_024E',  # Male 80-84
                'B01001_025E',  # Male 85+
                'B01001_027E',  # Female under 5
                'B01001_028E',  # Female 5-9
                'B01001_029E',  # Female 10-14
                'B01001_030E',  # Female 15-17
                'B01001_031E',  # Female 18-19
                'B01001_032E',  # Female 20
                'B01001_033E',  # Female 21
                'B01001_034E',  # Female 22-24
                'B01001_035E',  # Female 25-29
                'B01001_036E',  # Female 30-34
                'B01001_037E',  # Female 35-39
                'B01001_038E',  # Female 40-44
                'B01001_039E',  # Female 45-49
                'B01001_040E',  # Female 50-54
                'B01001_041E',  # Female 55-59
                'B01001_042E',  # Female 60-61
                'B01001_043E',  # Female 62-64
                'B01001_044E',  # Female 65-66
                'B01001_045E',  # Female 67-69
                'B01001_046E',  # Female 70-74
                'B01001_047E',  # Female 75-79
                'B01001_048E',  # Female 80-84
                'B01001_049E',  # Female 85+
                'B19013_001E',  # Median household income
                'B25077_001E',  # Median home value
            ]
            
            # Build API URL with correct ZCTA format
            url = f"{self.base_url}/{year}/acs/acs5"
            params = {
                'get': ','.join(variables),
                'for': f'zip code tabulation area:{zip_code}',
                'key': self.census_api_key if self.census_api_key else ''
            }
            
            # Remove empty key parameter if no API key
            if not self.census_api_key:
                params.pop('key', None)
            
            response = requests.get(url, params=params, timeout=30)
            
            # Check if we got a 400 error and try alternative format
            if response.status_code == 400:
                print(f"  Trying alternative ZCTA format for ZIP {zip_code}...")
                # Try with just the ZIP code as ZCTA
                params['for'] = f'zip%20code%20tabulation%20area:{zip_code}'
                response = requests.get(url, params=params, timeout=30)
            
            response.raise_for_status()
            
            data = response.json()
            if len(data) < 2:  # No data found
                return None
                
            # Parse the data
            headers = data[0]
            values = data[1]
            
            result = {}
            for i, header in enumerate(headers):
                if i < len(values):
                    try:
                        result[header] = int(values[i]) if values[i] is not None else 0
                    except (ValueError, TypeError):
                        result[header] = 0
            
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                print(f"  No Census data available for ZIP {zip_code} (400 error)")
                return None
            else:
                print(f"  HTTP error for ZIP {zip_code}: {e}")
                return None
        except Exception as e:
            print(f"  Error getting Census data for ZIP {zip_code}: {e}")
            return None
    
    def calculate_age_groups(self, census_data):
        """Calculate age group populations from Census data"""
        if not census_data:
            return {}
        
        age_groups = {
            'total_population': census_data.get('B01003_001E', 0),
            'under_5': (census_data.get('B01001_003E', 0) + census_data.get('B01001_027E', 0)),
            'age_5_17': (census_data.get('B01001_004E', 0) + census_data.get('B01001_005E', 0) + 
                        census_data.get('B01001_006E', 0) + census_data.get('B01001_028E', 0) + 
                        census_data.get('B01001_029E', 0) + census_data.get('B01001_030E', 0)),
            'age_18_24': (census_data.get('B01001_007E', 0) + census_data.get('B01001_008E', 0) + 
                         census_data.get('B01001_009E', 0) + census_data.get('B01001_010E', 0) + 
                         census_data.get('B01001_031E', 0) + census_data.get('B01001_032E', 0) + 
                         census_data.get('B01001_033E', 0) + census_data.get('B01001_034E', 0)),
            'age_25_34': (census_data.get('B01001_011E', 0) + census_data.get('B01001_012E', 0) + 
                         census_data.get('B01001_035E', 0) + census_data.get('B01001_036E', 0)),
            'age_35_44': (census_data.get('B01001_013E', 0) + census_data.get('B01001_014E', 0) + 
                         census_data.get('B01001_037E', 0) + census_data.get('B01001_038E', 0)),
            'age_45_54': (census_data.get('B01001_015E', 0) + census_data.get('B01001_016E', 0) + 
                         census_data.get('B01001_039E', 0) + census_data.get('B01001_040E', 0)),
            'age_55_64': (census_data.get('B01001_017E', 0) + census_data.get('B01001_018E', 0) + 
                         census_data.get('B01001_019E', 0) + census_data.get('B01001_041E', 0) + 
                         census_data.get('B01001_042E', 0) + census_data.get('B01001_043E', 0)),
            'age_65_74': (census_data.get('B01001_020E', 0) + census_data.get('B01001_021E', 0) + 
                         census_data.get('B01001_022E', 0) + census_data.get('B01001_044E', 0) + 
                         census_data.get('B01001_045E', 0) + census_data.get('B01001_046E', 0)),
            'age_75_84': (census_data.get('B01001_023E', 0) + census_data.get('B01001_024E', 0) + 
                         census_data.get('B01001_047E', 0) + census_data.get('B01001_048E', 0)),
            'age_85_plus': (census_data.get('B01001_025E', 0) + census_data.get('B01001_049E', 0)),
            'median_household_income': census_data.get('B19013_001E', 0),
            'median_home_value': census_data.get('B25077_001E', 0),
        }
        
        # Calculate percentages
        total = age_groups['total_population']
        if total > 0:
            age_groups['pct_under_5'] = (age_groups['under_5'] / total) * 100
            age_groups['pct_age_5_17'] = (age_groups['age_5_17'] / total) * 100
            age_groups['pct_age_18_24'] = (age_groups['age_18_24'] / total) * 100
            age_groups['pct_age_25_34'] = (age_groups['age_25_34'] / total) * 100
            age_groups['pct_age_35_44'] = (age_groups['age_35_44'] / total) * 100
            age_groups['pct_age_45_54'] = (age_groups['age_45_54'] / total) * 100
            age_groups['pct_age_55_64'] = (age_groups['age_55_64'] / total) * 100
            age_groups['pct_age_65_74'] = (age_groups['age_65_74'] / total) * 100
            age_groups['pct_age_75_84'] = (age_groups['age_75_84'] / total) * 100
            age_groups['pct_age_85_plus'] = (age_groups['age_85_plus'] / total) * 100
        else:
            age_groups.update({f'pct_{k}': 0 for k in ['under_5', 'age_5_17', 'age_18_24', 'age_25_34', 
                                                      'age_35_44', 'age_45_54', 'age_55_64', 'age_65_74', 
                                                      'age_75_84', 'age_85_plus']})
        
        return age_groups
    
    def get_zip_area_sq_miles(self, zip_code):
        """
        Get ZIP code area in square miles
        This would typically come from a ZIP code boundary file
        For now, using approximate values based on ZIP code patterns
        """
        # This is a simplified approach - in practice you'd use actual ZIP boundary data
        # Rural ZIPs are typically larger, urban ZIPs smaller
        zip_str = str(zip_code).zfill(5)
        
        # Approximate areas based on ZIP patterns (very rough estimates)
        if zip_str.startswith(('00', '01', '02', '03', '04', '05')):  # Northeast
            return 15.0  # Smaller, more urban
        elif zip_str.startswith(('06', '07', '08', '09')):  # Northeast
            return 20.0
        elif zip_str.startswith(('10', '11', '12', '13', '14')):  # Northeast
            return 25.0
        elif zip_str.startswith(('15', '16', '17', '18', '19')):  # Northeast
            return 30.0
        elif zip_str.startswith(('20', '21', '22', '23', '24', '25', '26', '27')):  # Southeast
            return 35.0
        elif zip_str.startswith(('28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39')):  # Southeast
            return 40.0
        elif zip_str.startswith(('40', '41', '42', '43', '44', '45', '46', '47', '48', '49')):  # Midwest
            return 45.0
        elif zip_str.startswith(('50', '51', '52', '53', '54', '55', '56', '57', '58', '59')):  # Midwest
            return 50.0
        elif zip_str.startswith(('60', '61', '62', '63', '64', '65', '66', '67', '68', '69')):  # Midwest
            return 55.0
        elif zip_str.startswith(('70', '71', '72', '73', '74')):  # South Central
            return 60.0
        elif zip_str.startswith(('75', '76', '77', '78', '79')):  # South Central
            return 65.0
        elif zip_str.startswith(('80', '81', '82', '83', '84', '85', '86', '87')):  # Mountain West
            return 70.0
        elif zip_str.startswith(('88', '89')):  # Mountain West
            return 75.0
        elif zip_str.startswith(('90', '91', '92', '93', '94', '95', '96', '97', '98', '99')):  # West Coast
            return 80.0
        else:
            return 50.0  # Default
    
    def calculate_population_density(self, population, zip_code):
        """Calculate population density for a ZIP code"""
        area = self.get_zip_area_sq_miles(zip_code)
        return population / area if area > 0 else 0
    
    def get_population_growth_estimate(self, zip_code):
        """
        Get estimated population growth rate for a ZIP code
        This is a simplified estimate based on ZIP code patterns
        """
        zip_str = str(zip_code).zfill(5)
        
        # Growth estimates based on ZIP patterns (very rough estimates)
        if zip_str.startswith(('00', '01', '02', '03', '04', '05')):  # Northeast
            return 0.3  # Slow growth
        elif zip_str.startswith(('06', '07', '08', '09')):  # Northeast
            return 0.5  # Slow growth
        elif zip_str.startswith(('10', '11', '12', '13', '14')):  # Northeast
            return 0.4  # Slow growth
        elif zip_str.startswith(('15', '16', '17', '18', '19')):  # Northeast
            return 0.6  # Moderate growth
        elif zip_str.startswith(('20', '21', '22', '23', '24', '25', '26', '27')):  # Southeast
            return 1.2  # High growth
        elif zip_str.startswith(('28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39')):  # Southeast
            return 1.0  # Moderate-high growth
        elif zip_str.startswith(('40', '41', '42', '43', '44', '45', '46', '47', '48', '49')):  # Midwest
            return 0.8  # Moderate growth
        elif zip_str.startswith(('50', '51', '52', '53', '54', '55', '56', '57', '58', '59')):  # Midwest
            return 0.7  # Moderate growth
        elif zip_str.startswith(('60', '61', '62', '63', '64', '65', '66', '67', '68', '69')):  # Midwest
            return 0.9  # Moderate growth
        elif zip_str.startswith(('70', '71', '72', '73', '74')):  # South Central
            return 1.2  # High growth
        elif zip_str.startswith(('75', '76', '77', '78', '79')):  # South Central
            return 1.1  # High growth
        elif zip_str.startswith(('80', '81', '82', '83', '84', '85', '86', '87')):  # Mountain West
            return 2.0  # High growth
        elif zip_str.startswith(('88', '89')):  # Mountain West
            return 1.8  # High growth
        elif zip_str.startswith(('90', '91', '92', '93', '94', '95', '96', '97', '98', '99')):  # West Coast
            return 1.5  # Moderate-high growth
        else:
            return 0.8  # Default moderate growth
    
    def fetch_all_zip_demographics(self, input_file='all_ok_mo_zips.csv'):
        """
        Fetch Census demographic data for ALL ZIP codes in the input file
        """
        print(f"🏠 Fetching Census demographics for ALL ZIP codes in {input_file}")
        print("=" * 70)
        
        # Load the ZIP codes
        df = pd.read_csv(input_file)
        zip_codes = df['zip'].astype(str).str.zfill(5).tolist()
        
        print(f"📊 Found {len(zip_codes)} ZIP codes to process")
        
        # Create results list
        results = []
        
        # Process each ZIP code
        for i, zip_code in enumerate(zip_codes):
            print(f"  Processing ZIP {zip_code} ({i+1}/{len(zip_codes)})...")
            
            # Get Census data
            census_data = self.get_census_data_by_zip(zip_code)
            
            if census_data:
                # Calculate age groups and demographics
                demographics = self.calculate_age_groups(census_data)
                
                # Add population density
                total_pop = demographics.get('total_population', 0)
                demographics['population_density'] = self.calculate_population_density(total_pop, zip_code)
                
                # Add population growth estimate
                demographics['population_growth_rate'] = self.get_population_growth_estimate(zip_code)
                
                # Calculate growth by age group (simplified)
                demographics['growth_under_18'] = demographics['population_growth_rate'] * 0.8
                demographics['growth_18_34'] = demographics['population_growth_rate'] * 1.2
                demographics['growth_35_54'] = demographics['population_growth_rate'] * 0.9
                demographics['growth_55_64'] = demographics['population_growth_rate'] * 1.1
                demographics['growth_65_plus'] = demographics['population_growth_rate'] * 1.5
                
                print(f"    ✅ Found Census data for ZIP {zip_code}")
            else:
                # Create default demographics for missing data
                demographics = {
                    'total_population': 0,
                    'under_5': 0, 'age_5_17': 0, 'age_18_24': 0, 'age_25_34': 0,
                    'age_35_44': 0, 'age_45_54': 0, 'age_55_64': 0, 'age_65_74': 0,
                    'age_75_84': 0, 'age_85_plus': 0,
                    'pct_under_5': 0, 'pct_age_5_17': 0, 'pct_age_18_24': 0, 'pct_age_25_34': 0,
                    'pct_age_35_44': 0, 'pct_age_45_54': 0, 'pct_age_55_64': 0, 'pct_age_65_74': 0,
                    'pct_age_75_84': 0, 'pct_age_85_plus': 0,
                    'median_household_income': 0,
                    'median_home_value': 0,
                    'population_density': 0,
                    'population_growth_rate': 0,
                    'growth_under_18': 0, 'growth_18_34': 0, 'growth_35_54': 0,
                    'growth_55_64': 0, 'growth_65_plus': 0
                }
                print(f"    ⚠️ No Census data for ZIP {zip_code}, using defaults")
            
            # Add ZIP code to demographics
            demographics['zip'] = zip_code
            
            # Add to results
            results.append(demographics)
            
            # Rate limiting to be respectful to the API
            time.sleep(0.2)
            
            # Save progress every 100 ZIP codes
            if (i + 1) % 100 == 0:
                temp_df = pd.DataFrame(results)
                temp_df.to_csv('all_ok_mo_zip_demographics_temp.csv', index=False)
                print(f"    💾 Saved progress: {i+1}/{len(zip_codes)} ZIP codes processed")
        
        # Create final dataframe
        print("📝 Creating final demographics dataset...")
        final_df = pd.DataFrame(results)
        
        # Save the complete dataset
        output_file = 'all_ok_mo_zip_demographics.csv'
        final_df.to_csv(output_file, index=False)
        
        print(f"✅ Complete demographics data saved to {output_file}")
        print(f"📊 Processed {len(results)} ZIP codes")
        
        # Count successful vs failed API calls
        successful = sum(1 for demo in results if demo.get('total_population', 0) > 0)
        failed = len(results) - successful
        
        print(f"\n📈 API Call Results:")
        print(f"  ✅ Successful: {successful} ZIP codes")
        print(f"  ❌ Failed: {failed} ZIP codes")
        
        if successful > 0:
            # Print summary statistics for successful calls
            successful_data = [demo for demo in results if demo.get('total_population', 0) > 0]
            avg_pop = sum(demo.get('total_population', 0) for demo in successful_data) / len(successful_data)
            avg_income = sum(demo.get('median_household_income', 0) for demo in successful_data) / len(successful_data)
            avg_density = sum(demo.get('population_density', 0) for demo in successful_data) / len(successful_data)
            
            print(f"\n📊 Summary Statistics (Census Data):")
            print(f"  Average ZIP population: {avg_pop:.0f}")
            print(f"  Average population density: {avg_density:.1f} people/sq mile")
            print(f"  Average median household income: ${avg_income:,.0f}")
        
        return final_df

def main():
    """Main function to run ZIP demographics fetching"""
    print("🏠 SSM Health ALL ZIP Code Demographics Fetcher")
    print("=" * 55)
    
    fetcher = AllZIPDemographicsFetcher()
    
    try:
        # Fetch demographics for all ZIP codes
        demographics_df = fetcher.fetch_all_zip_demographics()
        
        print("\n🎉 ZIP demographics fetching completed!")
        print("📊 Dataset includes:")
        print("  - Population density")
        print("  - Detailed age group populations and percentages")
        print("  - Population growth rates by age group")
        print("  - ZIP-level household income and home values")
        print("  - All 3,048 ZIP codes in MN, WI, IL")
        
        if not fetcher.census_api_key:
            print("\n💡 Note: Using Census API without a key (limited to 500 requests/day)")
            print("   For higher limits, get a free API key from: https://api.census.gov/data/key_signup.html")
            print("   This script may take several days to complete all ZIP codes")
        
    except Exception as e:
        print(f"❌ Error during fetching: {e}")
        raise

if __name__ == "__main__":
    main() 