#!/usr/bin/env python3
"""
Example script showing how to use the Public ZIP-to-MSA API
for MSA lookup in the SSM Health scraper.

This script demonstrates:
1. How to use the public API (no API key required)
2. How to get MSA data from ZIP codes
3. How to integrate it with the scraper
4. Additional population data available
"""

from zip_msa_lookup import ZipMSALookup

def main():
    print("Public ZIP-to-MSA API Example")
    print("=" * 50)
    
    # Initialize the lookup
    msa_lookup = ZipMSALookup()
    
    # Show API information
    print(msa_lookup.get_api_info())
    
    # Test API connection
    print("Testing API connection...")
    if msa_lookup.test_api_connection():
        print("✅ API is accessible!")
    else:
        print("❌ API is not accessible, will use fallback mapping")
    
    print("\nExample Usage:")
    print("-" * 30)
    
    # Example 1: Using ZIP code directly
    print("1. Using ZIP Code Directly:")
    test_zips = ["60622", "60601", "60605", "60610", "60611"]
    
    for zip_code in test_zips:
        msa_data = msa_lookup.get_msa_from_zip_api(zip_code)
        print(f"   ZIP: {zip_code}")
        print(f"   MSA: {msa_data['msa_name']}")
        print(f"   CBSA Code: {msa_data['msa_code']}")
        print(f"   Population 2014: {msa_data['population_2014']}")
        print(f"   Population 2015: {msa_data['population_2015']}")
        print(f"   Source: {msa_data['source']}")
        print()
    
    # Example 2: Using address parsing
    print("2. Using Address Parsing:")
    test_addresses = [
        "2233 W Division St, Chicago, IL 60622",
        "1 N Franklin St, Chicago, IL 60606",
        "1500 S Lake Shore Dr, Chicago, IL 60605"
    ]
    
    for address in test_addresses:
        msa_data = msa_lookup.get_msa_from_address(address)
        print(f"   Address: {address}")
        print(f"   Extracted ZIP: {msa_data['zip_code']}")
        print(f"   MSA: {msa_data['msa_name']}")
        print(f"   Source: {msa_data['source']}")
        print()
    
    # Example 3: Using city/state (fallback)
    print("3. Using City/State (Fallback):")
    msa_data = msa_lookup.get_msa('Chicago', 'IL')
    print(f"   City: Chicago, IL")
    print(f"   MSA: {msa_data['msa_name']}")
    print(f"   Source: {msa_data['source']}")
    print()
    
    # Example 4: Test with different Illinois cities
    print("4. Testing Different Illinois Cities:")
    test_cities = [
        ('Naperville', 'IL'),
        ('Rockford', 'IL'),
        ('Peoria', 'IL'),
        ('Springfield', 'IL')
    ]
    
    for city, state in test_cities:
        msa_data = msa_lookup.get_msa(city, state)
        print(f"   {city}, {state} -> MSA: {msa_data['msa_name']}")
    
    print("\nIntegration with Scraper:")
    print("-" * 30)
    print("The scraper will automatically:")
    print("1. Extract ZIP codes from addresses")
    print("2. Use ZIP codes for MSA lookup via the public API")
    print("3. Fall back to city/state mapping if ZIP not found")
    print("4. Include MSA name, code, source, and population data in output")
    print()
    
    print("Expected Output Columns:")
    print("-" * 30)
    print("• msa: MSA name (e.g., 'Chicago-Naperville-Elgin, IL-IN-WI')")
    print("• msa_code: CBSA code (e.g., '16980' for Chicago)")
    print("• msa_source: Data source ('Public ZIP-to-MSA API' or 'Fallback Mapping')")
    print("• zip_code: Extracted ZIP code from address")
    print("• population_2014: Population in 2014")
    print("• population_2015: Population in 2015")
    
    print("\nBenefits of this API:")
    print("-" * 30)
    print("✅ No API key required")
    print("✅ Public and free to use")
    print("✅ Includes population data")
    print("✅ More accurate than city/state mapping")
    print("✅ Simple integration")
    print("✅ Automatic fallback to hardcoded mapping")

if __name__ == "__main__":
    main() 