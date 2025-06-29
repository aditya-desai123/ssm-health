# HUD USPS ZIP Code Crosswalk API Integration

This document explains how to use the [HUD USPS ZIP Code Crosswalk API](https://www.huduser.gov/portal/datasets/usps_crosswalk.html) to get accurate MSA (Metropolitan Statistical Area) data for the SSM Health scraper.

## What the HUD API Provides

The HUD USPS ZIP Code Crosswalk API provides:
- **ZIP code to CBSA (MSA) mapping** - More accurate than city/state mapping
- **Quarterly updates** - Reflects current ZIP code configurations
- **Address-based allocation** - Uses residential address distribution
- **Official government data** - From the U.S. Department of Housing and Urban Development

## Getting an API Key

1. Visit: https://www.huduser.gov/portal/dataset/uspszip-api.html
2. Create an account and get an access token
3. The API is free for government and research use

## How to Use with the Scraper

### Option 1: With API Key (Recommended)

```python
from hud_msa_lookup import HUDMSALookup

# Initialize with your API key
msa_lookup = HUDMSALookup(api_key='your_api_key_here')

# The scraper will automatically use the API
scraper = SSMHealthLocationsScraper()
scraper.msa_lookup = msa_lookup
```

### Option 2: Without API Key (Current Setup)

```python
from hud_msa_lookup import HUDMSALookup

# Initialize without API key - uses fallback mapping
msa_lookup = HUDMSALookup()
```

## What You'll Get

The scraper will now output these additional columns:

| Column | Description | Example |
|--------|-------------|---------|
| `msa` | MSA name | "Chicago-Naperville-Elgin, IL-IN-WI" |
| `msa_code` | CBSA code | "16980" |
| `msa_source` | Data source | "HUD API" or "Fallback Mapping" |
| `zip_code` | Extracted ZIP | "60622" |

## Example Output

```
1. SSM Health St. Mary's Hospital
   Address: 2233 W Division St, Chicago, IL 60622
   ZIP Code: 60622
   Phone: (773) 278-2000
   Type: Hospital
   Specialty: General Hospital
   Hours: 24/7
   Distance: 2.3 miles
   MSA: Chicago-Naperville-Elgin, IL-IN-WI
   MSA Code: 16980
   MSA Source: HUD API
   Link: https://www.ssmhealth.com/locations/st-marys-hospital
   Location ID: 12345
```

## Benefits of Using the HUD API

1. **Accuracy**: ZIP code-based mapping is more precise than city/state mapping
2. **Timeliness**: Quarterly updates reflect current geographic boundaries
3. **Completeness**: Covers all ZIP codes, including those that cross city/county boundaries
4. **Official Data**: Government-sourced data for research and analysis

## Fallback Behavior

If the API is unavailable or you don't have an API key:
- The system uses a comprehensive fallback mapping for Illinois cities
- Still provides MSA information, just less precise
- Source will show "Fallback Mapping" instead of "HUD API"

## For Demographic Analysis

With accurate MSA data, you can now:
- **Aggregate by MSA** for market analysis
- **Calculate MSA-level statistics** (average distance, facility count, etc.)
- **Cross-reference with Census data** using MSA codes
- **Analyze payer mix** by metropolitan area
- **Study healthcare access** patterns across different MSAs

## Running the Example

```bash
python example_hud_api_usage.py
```

This will show you how the API works and what data you can expect.

## Next Steps for Demographics

Once you have MSA data, you can enhance it with:
- **Census Bureau API** for population demographics
- **American Community Survey** for income and insurance data
- **CMS data** for Medicare/Medicaid statistics
- **Commercial databases** for payer mix information

The MSA codes provide the geographic foundation for all these demographic analyses. 