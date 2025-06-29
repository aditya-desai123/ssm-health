import requests
import pandas as pd
import time
from typing import Dict, Optional
import json

class HUDMSALookup:
    def __init__(self, api_key=None):
        """Initialize the MSA lookup system with HUD API"""
        self.msa_cache = {}
        self.api_key = api_key
        self.base_url = "https://www.huduser.gov/portal/dataset/uspszip-api.html"
        
        # Fallback mapping for when API is not available
        self.fallback_mapping = {
            # Illinois MSAs - basic fallback
            ('Chicago', 'IL'): 'Chicago-Naperville-Elgin, IL-IN-WI',
            ('Naperville', 'IL'): 'Chicago-Naperville-Elgin, IL-IN-WI',
            ('Elgin', 'IL'): 'Chicago-Naperville-Elgin, IL-IN-WI',
            ('Aurora', 'IL'): 'Chicago-Naperville-Elgin, IL-IN-WI',
            ('Rockford', 'IL'): 'Rockford, IL',
            ('Peoria', 'IL'): 'Peoria, IL',
            ('Springfield', 'IL'): 'Springfield, IL',
            ('Champaign', 'IL'): 'Champaign-Urbana, IL',
            ('Urbana', 'IL'): 'Champaign-Urbana, IL',
            ('Bloomington', 'IL'): 'Bloomington, IL',
            ('Normal', 'IL'): 'Bloomington, IL',
            ('Decatur', 'IL'): 'Decatur, IL',
            ('Carbondale', 'IL'): 'Carbondale-Marion, IL',
            ('Marion', 'IL'): 'Carbondale-Marion, IL',
            ('Quincy', 'IL'): 'Quincy, IL-MO',
            ('Danville', 'IL'): 'Danville, IL',
            ('Kankakee', 'IL'): 'Kankakee, IL',
            ('Ottawa', 'IL'): 'Ottawa-Peru, IL',
            ('Peru', 'IL'): 'Ottawa-Peru, IL',
            ('Dixon', 'IL'): 'Dixon, IL',
            ('Sterling', 'IL'): 'Sterling, IL',
            ('Rock Island', 'IL'): 'Davenport-Moline-Rock Island, IA-IL',
            ('Moline', 'IL'): 'Davenport-Moline-Rock Island, IA-IL',
            ('East Moline', 'IL'): 'Davenport-Moline-Rock Island, IA-IL',
            ('Galesburg', 'IL'): 'Galesburg, IL',
            ('Macomb', 'IL'): 'Macomb, IL',
            ('Freeport', 'IL'): 'Freeport, IL',
        }
    
    def get_zip_from_address(self, address: str) -> Optional[str]:
        """
        Extract ZIP code from address string
        
        Args:
            address (str): Full address string
            
        Returns:
            str: ZIP code or None if not found
        """
        if not address or address == 'N/A':
            return None
        
        # Try to extract ZIP from address
        # Common format: "Street, City, State ZIP"
        parts = address.split(',')
        if len(parts) >= 3:
            state_zip = parts[2].strip()
            # Extract ZIP (last 5 digits)
            words = state_zip.split()
            for word in words:
                if len(word) == 5 and word.isdigit():
                    return word
        
        return None
    
    def get_msa_from_zip_api(self, zip_code: str) -> Dict:
        """
        Get MSA data from HUD API using ZIP code
        
        Args:
            zip_code (str): 5-digit ZIP code
            
        Returns:
            Dict: MSA data from API
        """
        if not self.api_key:
            return self._get_fallback_msa_data()
        
        try:
            # HUD API endpoint for ZIP to CBSA (MSA) lookup
            url = f"https://www.huduser.gov/portal/dataset/uspszip-api.html"
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'zip': zip_code,
                'year': '2023',  # Use most recent year
                'quarter': '4'   # Use most recent quarter
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract CBSA (MSA) information
                if data and 'cbsa' in data:
                    cbsa_code = data['cbsa']
                    cbsa_name = self._get_cbsa_name(cbsa_code)
                    
                    return {
                        'msa_name': cbsa_name,
                        'msa_code': cbsa_code,
                        'zip_code': zip_code,
                        'source': 'HUD API'
                    }
            
            return self._get_fallback_msa_data()
            
        except Exception as e:
            print(f"Error calling HUD API: {e}")
            return self._get_fallback_msa_data()
    
    def _get_cbsa_name(self, cbsa_code: str) -> str:
        """
        Convert CBSA code to MSA name
        
        Args:
            cbsa_code (str): CBSA code
            
        Returns:
            str: MSA name
        """
        # CBSA code to name mapping for Illinois
        cbsa_mapping = {
            '16980': 'Chicago-Naperville-Elgin, IL-IN-WI',
            '40340': 'Rockford, IL',
            '37900': 'Peoria, IL',
            '44100': 'Springfield, IL',
            '16580': 'Champaign-Urbana, IL',
            '14060': 'Bloomington, IL',
            '19500': 'Decatur, IL',
            '16060': 'Carbondale-Marion, IL',
            '39500': 'Quincy, IL-MO',
            '19180': 'Danville, IL',
            '28100': 'Kankakee, IL',
            '36837': 'Ottawa-Peru, IL',
            '20994': 'Dixon, IL',
            '44540': 'Sterling, IL',
            '19340': 'Davenport-Moline-Rock Island, IA-IL',
            '30660': 'Galesburg, IL',
            '31300': 'Macomb, IL',
            '27060': 'Freeport, IL',
        }
        
        return cbsa_mapping.get(cbsa_code, f'Unknown MSA ({cbsa_code})')
    
    def _get_fallback_msa_data(self) -> Dict:
        """
        Get fallback MSA data when API is not available
        
        Returns:
            Dict: Fallback MSA data
        """
        return {
            'msa_name': 'Unknown',
            'msa_code': '00000',
            'zip_code': None,
            'source': 'Fallback'
        }
    
    def get_msa(self, city: str, state: str, zip_code: str = None) -> Dict:
        """
        Get MSA data for a given city, state, and optionally ZIP code
        
        Args:
            city (str): City name
            state (str): State abbreviation
            zip_code (str): ZIP code (optional)
            
        Returns:
            Dict: MSA data
        """
        # Normalize the input
        city = city.strip().title()
        state = state.strip().upper()
        
        # Check cache first
        cache_key = f"{city}, {state}, {zip_code}"
        if cache_key in self.msa_cache:
            return self.msa_cache[cache_key]
        
        # If we have a ZIP code, try the API first
        if zip_code:
            msa_data = self.get_msa_from_zip_api(zip_code)
            if msa_data['msa_name'] != 'Unknown':
                self.msa_cache[cache_key] = msa_data
                return msa_data
        
        # Fallback to city/state mapping
        msa_name = self.fallback_mapping.get((city, state), 'Unknown')
        msa_data = {
            'msa_name': msa_name,
            'msa_code': '00000',
            'zip_code': zip_code,
            'source': 'Fallback Mapping'
        }
        
        self.msa_cache[cache_key] = msa_data
        return msa_data
    
    def get_msa_from_address(self, address: str) -> Dict:
        """
        Extract ZIP code from address and get MSA data
        
        Args:
            address (str): Full address string
            
        Returns:
            Dict: MSA data
        """
        if not address or address == 'N/A':
            return self._get_fallback_msa_data()
        
        # Extract ZIP code from address
        zip_code = self.get_zip_from_address(address)
        
        if zip_code:
            return self.get_msa_from_zip_api(zip_code)
        
        # Try to extract city and state as fallback
        parts = address.split(',')
        if len(parts) >= 3:
            city = parts[1].strip()
            state_zip = parts[2].strip()
            state = state_zip[:2].strip()
            return self.get_msa(city, state)
        
        return self._get_fallback_msa_data()
    
    def add_msa_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add MSA columns to a pandas DataFrame
        
        Args:
            df (pd.DataFrame): DataFrame with address or city/state/zip columns
            
        Returns:
            pd.DataFrame: DataFrame with added MSA columns
        """
        # Try to extract ZIP codes from addresses if zip column doesn't exist
        if 'zip' not in df.columns and 'address' in df.columns:
            df['zip'] = df['address'].apply(self.get_zip_from_address)
        
        if 'city' in df.columns and 'state' in df.columns:
            # Get MSA data for each row
            msa_data_list = df.apply(
                lambda row: self.get_msa(
                    row['city'], 
                    row['state'], 
                    row.get('zip', None)
                ), 
                axis=1
            )
        elif 'address' in df.columns:
            # Get MSA data for each row using address
            msa_data_list = df['address'].apply(self.get_msa_from_address)
        else:
            # Set default values
            msa_data_list = [self._get_fallback_msa_data()] * len(df)
        
        # Extract individual fields
        df['msa'] = msa_data_list.apply(lambda x: x['msa_name'])
        df['msa_code'] = msa_data_list.apply(lambda x: x['msa_code'])
        df['msa_source'] = msa_data_list.apply(lambda x: x['source'])
        
        return df
    
    def get_api_key_instructions(self) -> str:
        """
        Get instructions for obtaining HUD API key
        
        Returns:
            str: Instructions for API key
        """
        return """
To use the HUD USPS ZIP Code Crosswalk API:

1. Visit: https://www.huduser.gov/portal/dataset/uspszip-api.html
2. Create an account and get an access token
3. Set the API key when initializing HUDMSALookup:
   msa_lookup = HUDMSALookup(api_key='your_api_key_here')

The API provides:
- ZIP code to CBSA (MSA) mapping
- Quarterly updates
- More accurate geographic data than hardcoded mappings

Without an API key, the system will use fallback mappings.
""" 