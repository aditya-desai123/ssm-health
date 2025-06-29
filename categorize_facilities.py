#!/usr/bin/env python3
"""
Script to categorize SSM health facilities into specific facility types
based on their names and specialties.
"""

import pandas as pd
import re
from typing import Dict, List

def categorize_facility(name: str, specialty: str) -> str:
    """
    Categorize a facility based on its name and specialty
    
    Args:
        name (str): Facility name
        specialty (str): Facility specialty
        
    Returns:
        str: Categorized facility type
    """
    # Convert to lowercase for easier matching
    name_lower = str(name).lower() if pd.notna(name) else ""
    specialty_lower = str(specialty).lower() if pd.notna(specialty) else ""
    
    # Hospital
    hospital_keywords = [
        'hospital', 'medical center', 'health center', 'medical center'
    ]
    for keyword in hospital_keywords:
        if keyword in name_lower:
            return 'Hospital'
    
    # Emergency Department / Urgent Care
    ed_keywords = [
        'emergency', 'urgent care', 'ed ', 'er ', 'emergency room', 'urgent'
    ]
    for keyword in ed_keywords:
        if keyword in name_lower or keyword in specialty_lower:
            return 'Emergency Department (ED) / Urgent Care'
    
    # Pharmacy
    pharmacy_keywords = [
        'pharmacy', 'drug store', 'medication', 'prescription'
    ]
    for keyword in pharmacy_keywords:
        if keyword in name_lower:
            return 'Pharmacy'
    
    # Surgery Center / ASC
    surgery_keywords = [
        'surgery center', 'ambulatory surgery', 'asc', 'surgical', 'surgery'
    ]
    for keyword in surgery_keywords:
        if keyword in name_lower or keyword in specialty_lower:
            return 'Surgery Center (or Ambulatory Surgery Center – ASC)'
    
    # Imaging Center / Radiology
    imaging_keywords = [
        'imaging', 'radiology', 'x-ray', 'mri', 'ct scan', 'ultrasound', 'mammography',
        'nuclear medicine', 'diagnostic imaging', 'medical imaging'
    ]
    for keyword in imaging_keywords:
        if keyword in name_lower or keyword in specialty_lower:
            return 'Imaging Center / Radiology'
    
    # Laboratory / Lab
    lab_keywords = [
        'laboratory', 'lab ', 'pathology', 'diagnostic lab', 'clinical lab'
    ]
    for keyword in lab_keywords:
        if keyword in name_lower or keyword in specialty_lower:
            return 'Laboratory / Lab'
    
    # Rehabilitation Center / Physical Therapy
    rehab_keywords = [
        'rehabilitation', 'rehab', 'physical therapy', 'pt ', 'occupational therapy',
        'ot ', 'speech therapy', 'cardiac rehab', 'orthopedic rehab', 'therapy services'
    ]
    for keyword in rehab_keywords:
        if keyword in name_lower or keyword in specialty_lower:
            return 'Rehabilitation Center (or Physical Therapy)'
    
    # Clinic / Outpatient Clinic (default for most medical groups)
    clinic_keywords = [
        'clinic', 'medical group', 'outpatient', 'primary care', 'family medicine',
        'internal medicine', 'pediatrics', 'ob/gyn', 'obstetrics', 'gynecology',
        'orthopedics', 'cardiology', 'dermatology', 'neurology', 'psychiatry',
        'psychology', 'behavioral health', 'mental health', 'podiatry', 'chiropractic',
        'audiology', 'ent', 'otolaryngology', 'nephrology', 'gastroenterology',
        'endocrinology', 'rheumatology', 'oncology', 'hematology', 'pulmonology',
        'urology', 'ophthalmology', 'optometry', 'eye care', 'dental', 'orthodontics',
        'hospice', 'palliative care', 'home health', 'at home'
    ]
    for keyword in clinic_keywords:
        if keyword in name_lower or keyword in specialty_lower:
            return 'Clinic (or Outpatient Clinic)'
    
    # Check for specific facility patterns
    if any(pattern in name_lower for pattern in [
        'dean medical group', 'monroe clinic', 'health plaza', 'slucare',
        'physician group', 'medical associates', 'healthcare partners'
    ]):
        return 'Clinic (or Outpatient Clinic)'
    
    # Check for specialty-based categorization
    specialty_clinic_keywords = [
        'orthopedics', 'sports medicine', 'pain management', 'ear nose throat',
        'audiology', 'behavioral health', 'podiatry', 'chiropractic', 'nephrology',
        'academy', 'community'
    ]
    for keyword in specialty_clinic_keywords:
        if keyword in name_lower or keyword in specialty_lower:
            return 'Clinic (or Outpatient Clinic)'
    
    # Default to clinic if it's a medical facility but doesn't match other categories
    if 'ssm health' in name_lower:
        return 'Clinic (or Outpatient Clinic)'
    
    return 'Unknown'

def analyze_facility_types(df: pd.DataFrame) -> None:
    """
    Analyze the distribution of facility types
    
    Args:
        df (pd.DataFrame): DataFrame with facility_type column
    """
    print("\n" + "="*60)
    print("FACILITY TYPE ANALYSIS")
    print("="*60)
    
    # Count facility types
    facility_counts = df['facility_type'].value_counts()
    
    print("Facility Type Distribution:")
    print("-" * 40)
    for facility_type, count in facility_counts.items():
        percentage = (count / len(df)) * 100
        print(f"{facility_type}: {count} locations ({percentage:.1f}%)")
    
    # Show examples of each type
    print("\nExamples of each facility type:")
    print("-" * 40)
    for facility_type in facility_counts.index:
        examples = df[df['facility_type'] == facility_type][['name', 'specialty']].head(3)
        print(f"\n{facility_type}:")
        for _, row in examples.iterrows():
            print(f"  - {row['name']} ({row['specialty']})")

def main():
    """Main function to categorize facilities"""
    print("SSM Health Facility Categorization")
    print("="*50)
    
    # Load the data
    input_file = "ssm_health_locations_with_msa_robust.csv"
    output_file = "ssm_health_locations_categorized.csv"
    
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    print(f"Loaded {len(df)} facility records")
    print(f"Columns: {list(df.columns)}")
    
    # Show sample of original data
    print("\nSample of original data:")
    print(df[['name', 'specialty']].head(10).to_string(index=False))
    
    # Categorize facilities
    print("\nCategorizing facilities...")
    df['facility_type'] = df.apply(
        lambda row: categorize_facility(row['name'], row['specialty']), 
        axis=1
    )
    
    # Analyze results
    analyze_facility_types(df)
    
    # Show sample of categorized data
    print("\nSample of categorized data:")
    sample_cols = ['name', 'specialty', 'facility_type']
    print(df[sample_cols].head(15).to_string(index=False))
    
    # Save the enhanced data
    print(f"\nSaving categorized data to {output_file}...")
    df.to_csv(output_file, index=False)
    print("Categorized data saved successfully!")
    
    # Show summary statistics
    print(f"\nSummary:")
    print(f"- Total facilities: {len(df)}")
    print(f"- Categorized facilities: {len(df[df['facility_type'] != 'Unknown'])}")
    print(f"- Unknown facilities: {len(df[df['facility_type'] == 'Unknown'])}")
    
    # Show unknown facilities for manual review
    unknown_facilities = df[df['facility_type'] == 'Unknown']
    if len(unknown_facilities) > 0:
        print(f"\nFacilities that couldn't be categorized (first 10):")
        for _, row in unknown_facilities.head(10).iterrows():
            print(f"  - {row['name']} (Specialty: {row['specialty']})")

if __name__ == "__main__":
    main() 