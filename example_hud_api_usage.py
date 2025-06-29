#!/usr/bin/env python3
"""
Example script showing how to use the HUD USPS ZIP Code Crosswalk API
for MSA lookup in the SSM Health scraper.

This script demonstrates:
1. How to get an API key from HUD
2. How to use the API to get MSA data from ZIP codes
3. How to integrate it with the scraper
"""

from hud_msa_lookup import HUDMSALookup

def main():
    print("HUD USPS ZIP Code Crosswalk API Example")
    print("=" * 50)
    
    # Show instructions for getting API key
    msa_lookup = HUDMSALookup()
    print(msa_lookup.get_api_key_instructions())
    
    print("\nExample Usage:")
    print("-" * 30)
    
    # Example 1: Using with API key (when you have one)
    print("1. With API Key:")
    print("   msa_lookup = HUDMSALookup(api_key='your_api_key_here')")
    print("   msa_data = msa_lookup.get_msa_from_zip_api('60622')")
    print("   print(msa_data)")
    print()
    
    # Example 2: Using fallback mapping (current setup)
    print("2. With Fallback Mapping (current setup):")
    msa_lookup = HUDMSALookup()  # No API key
    msa_data = msa_lookup.get_msa_from_zip_api('60622')
    print(f"   ZIP: 60622 -> MSA: {msa_data['msa_name']}")
    print(f"   Source: {msa_data['source']}")
    print()
    
    # Example 3: Using address parsing
    print("3. Using Address Parsing:")
    address = "2233 W Division St, Chicago, IL 60622"
    msa_data = msa_lookup.get_msa_from_address(address)
    print(f"   Address: {address}")
    print(f"   MSA: {msa_data['msa_name']}")
    print(f"   Source: {msa_data['source']}")
    print()
    
    # Example 4: Using city/state
    print("4. Using City/State:")
    msa_data = msa_lookup.get_msa('Chicago', 'IL')
    print(f"   City: Chicago, IL -> MSA: {msa_data['msa_name']}")
    print(f"   Source: {msa_data['source']}")
    print()
    
    print("Integration with Scraper:")
    print("-" * 30)
    print("The scraper will automatically:")
    print("1. Extract ZIP codes from addresses")
    print("2. Use ZIP codes for MSA lookup when available")
    print("3. Fall back to city/state mapping if ZIP not found")
    print("4. Include MSA name, code, and source in output")
    print()
    
    print("Expected Output Columns:")
    print("-" * 30)
    print("• msa: MSA name (e.g., 'Chicago-Naperville-Elgin, IL-IN-WI')")
    print("• msa_code: CBSA code (e.g., '16980' for Chicago)")
    print("• msa_source: Data source ('HUD API' or 'Fallback Mapping')")
    print("• zip_code: Extracted ZIP code from address")

if __name__ == "__main__":
    main() 