#!/usr/bin/env python3
"""
Create ZIP code lists for Oklahoma and Missouri
Generate comprehensive ZIP code lists based on state ZIP code ranges
"""

import csv

def generate_zip_codes_for_state(state_code, zip_ranges):
    """Generate all ZIP codes for a state based on ranges"""
    zip_codes = set()
    
    for start_range, end_range in zip_ranges:
        start = int(start_range)
        end = int(end_range)
        
        for zip_code in range(start, end + 1):
            zip_codes.add(str(zip_code).zfill(5))
    
    return sorted(list(zip_codes))

def save_zip_codes_to_csv(zip_codes, filename):
    """Save ZIP codes to CSV file"""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['zip'])
        for zip_code in zip_codes:
            writer.writerow([zip_code])
    
    print(f"  ✅ Saved {len(zip_codes)} ZIP codes to {filename}")

def main():
    """Main function to create OK and MO ZIP lists"""
    print("🗺️ Creating Oklahoma and Missouri ZIP Code Lists")
    print("=" * 55)
    
    # Define ZIP code ranges for each state
    state_zip_ranges = {
        'OK': [
            ('73000', '74999'),  # Oklahoma
        ],
        'MO': [
            ('63000', '65999'),  # Missouri
        ]
    }
    
    all_ok_mo_zips = set()
    
    # Generate ZIP codes for each state
    for state_code, ranges in state_zip_ranges.items():
        print(f"📋 Generating {state_code} ZIP codes...")
        
        zip_codes = generate_zip_codes_for_state(state_code, ranges)
        print(f"  📊 Generated {len(zip_codes)} ZIP codes for {state_code}")
        
        # Save individual state file
        state_filename = f"all_{state_code.lower()}_zips.csv"
        save_zip_codes_to_csv(zip_codes, state_filename)
        
        # Add to combined set
        all_ok_mo_zips.update(zip_codes)
    
    # Save combined file
    print(f"📋 Creating combined OK and MO ZIP list...")
    combined_filename = "all_ok_mo_zips.csv"
    save_zip_codes_to_csv(sorted(all_ok_mo_zips), combined_filename)
    
    print(f"\n🎉 ZIP code lists created successfully!")
    print(f"📊 Summary:")
    print(f"  • Oklahoma: {len([z for z in all_ok_mo_zips if z.startswith(('730', '731', '732', '733', '734', '735', '736', '737', '738', '739', '740', '741', '742', '743', '744', '745', '746', '747', '748', '749'))])} ZIP codes")
    print(f"  • Missouri: {len([z for z in all_ok_mo_zips if z.startswith(('630', '631', '632', '633', '634', '635', '636', '637', '638', '639', '640', '641', '642', '643', '644', '645', '646', '647', '648', '649', '650', '651', '652', '653', '654', '655', '656', '657', '658', '659'))])} ZIP codes")
    print(f"  • Total: {len(all_ok_mo_zips)} ZIP codes")
    
    print(f"\n💡 Next steps:")
    print(f"  • Run: python3 fetch_all_zip_demographics.py all_ok_mo_zips.csv")
    print(f"  • Run: python3 score_all_zip_demographics.py")
    print(f"  • Create map with the scored data")

if __name__ == "__main__":
    main() 