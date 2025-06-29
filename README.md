# SSM Health Facility Analysis & Visualization Suite

## 🏥 Project Overview

This comprehensive analysis suite provides strategic insights into SSM Health's facility network, helping identify overserved and underserved markets for strategic decision-making. The project includes interactive maps, demographic analysis, and market intelligence tools.

## 📊 Key Features

### 🗺️ Interactive Visualizations
- **Interactive Facility Map**: All 1,412 facilities with detailed popups showing facility type, MSA information, and demographic data
- **MSA Density Heatmap**: Market saturation analysis with facility density visualization
- **Strategic Opportunities Map**: Highlights expansion opportunities and market risks
- **Comprehensive Dashboards**: Multi-dimensional analysis with income and age demographics

### 📈 Market Intelligence
- **Market Status Analysis**: Identifies overserved (79), adequately served (88), and underserved (1,245) markets
- **Demographic Profiling**: Income levels, age distribution, and population characteristics by MSA
- **Strategic Recommendations**: Data-driven insights for expansion and optimization

### 🔍 Data Enrichment
- **Income Data**: Median household income for all MSAs
- **Age Demographics**: Population age distribution and median age
- **MSA Mapping**: Metropolitan Statistical Area classification for all facilities

## 📁 Generated Files

### 🗺️ Interactive Maps
- `ssm_health_interactive_facility_map.html` (1.4MB) - Main facility map with all features
- `ssm_health_msa_density_heatmap.html` - Market density visualization
- `ssm_health_strategic_opportunities_map.html` - Strategic insights map

### 📊 Analysis Dashboards
- `ssm_health_market_analysis.html` (4.5MB) - Market coverage analysis
- `ssm_health_facility_types.html` (4.4MB) - Facility type distribution
- `ssm_health_comprehensive_dashboard.html` - Enhanced dashboard with demographics
- `ssm_health_income_age_analysis.html` - Income and age analysis
- `ssm_health_strategic_recommendations.html` - Strategic recommendations

### 📄 Reports & Data
- `ssm_health_mapping_summary.md` - Mapping analysis summary
- `ssm_health_comprehensive_analysis_report.md` - Detailed strategic report
- `ssm_health_locations_with_income_with_age_demographics.csv` - Enriched data file

## 🚀 Quick Start

### 1. Open All Visualizations
```bash
python3 open_all_visualizations.py
```
This will open all interactive maps and dashboards in your default web browser.

### 2. Run Complete Analysis
```bash
python3 interactive_facility_map.py
```
This creates the comprehensive interactive mapping suite.

### 3. View Specific Analysis
```bash
python3 comprehensive_facility_analysis.py
```
This generates enhanced dashboards with income and age demographics.

## 📋 Key Findings

### Market Coverage
- **Total Facilities**: 1,412 across 20 MSAs
- **Average Facilities per 100k**: 283.1
- **Average Median Income**: $75,837
- **Average Median Age**: 39.1 years

### Market Status Distribution
- **Underserved Markets**: 1,245 facilities (opportunity areas)
- **Adequately Served**: 88 facilities
- **Overserved Markets**: 79 facilities (consolidation candidates)

### Strategic Opportunities
- **High-Income Underserved**: 245 markets identified
- **Expansion Candidates**: Markets with high income potential but low facility density
- **Risk Areas**: 79 overserved markets requiring optimization

## 🛠️ Technical Architecture

### Data Pipeline
1. **Data Collection**: Web scraping of SSM Health facility locations
2. **MSA Mapping**: Geographic classification using ZIP codes and MSA lookup
3. **Income Enrichment**: Census Bureau API integration for household income data
4. **Age Demographics**: Population age distribution analysis
5. **Market Analysis**: Facility density and market status calculation

### Visualization Stack
- **Interactive Maps**: Folium with OpenStreetMap tiles
- **Dashboards**: Plotly with interactive charts and filters
- **Geocoding**: Nominatim for address-to-coordinate conversion
- **Data Processing**: Pandas for data manipulation and analysis

### Key Scripts
- `main.py` - Original web scraper for SSM Health locations
- `interactive_facility_map.py` - Comprehensive mapping analysis
- `add_income_data.py` - Income data enrichment
- `add_age_demographics.py` - Age demographic enrichment
- `comprehensive_facility_analysis.py` - Enhanced analysis with demographics

## 📊 Usage Instructions

### Interactive Facility Map
1. **Layer Controls**: Use the layer panel to filter by facility type or market status
2. **Facility Details**: Click any marker for comprehensive facility information
3. **Search**: Use the search bar to find specific facilities
4. **Map Styles**: Switch between light and dark map themes

### Strategic Analysis
1. **Market Status**: Red = Overserved, Yellow = Adequately Served, Green = Underserved
2. **Income Analysis**: Color-coded by income levels for strategic targeting
3. **Age Demographics**: Population age distribution for service planning
4. **Opportunity Identification**: Star markers indicate high-potential markets

### Dashboard Features
1. **Facility Distribution**: Charts showing facility types and specialties
2. **Market Coverage**: Facilities per 100k population analysis
3. **Demographic Insights**: Income and age distribution by market
4. **Strategic Recommendations**: Data-driven expansion and optimization guidance

## 📈 Strategic Applications

### For Healthcare Executives
- **Market Expansion**: Identify underserved high-income markets
- **Service Optimization**: Consolidate overserved areas
- **Demographic Targeting**: Align services with local population needs
- **Competitive Analysis**: Understand market saturation and opportunities

### For Strategic Planning
- **Resource Allocation**: Data-driven facility planning
- **Service Mix Optimization**: Match services to demographic profiles
- **Risk Assessment**: Identify markets requiring attention
- **Growth Strategy**: Prioritize expansion opportunities

## 🔧 Installation & Setup

### Prerequisites
```bash
pip install -r requirements.txt
```

### Required Packages
- pandas >= 1.5.0
- numpy >= 1.21.0
- plotly >= 5.0.0
- folium >= 0.14.0
- geopy >= 2.3.0
- selenium (for web scraping)

### Data Sources
- **SSM Health Website**: Primary facility data source
- **Census Bureau API**: Income and demographic data
- **MSA Lookup Tables**: Geographic classification data
- **OpenStreetMap**: Geocoding and mapping services

## 📝 Data Quality Notes

- **Geocoding**: Some facilities may have incomplete coordinates due to geocoding limitations
- **Income Data**: Based on MSA-level Census Bureau estimates
- **Age Demographics**: Derived from American Community Survey data
- **Market Status**: Calculated using facility density thresholds

## 🤝 Contributing

This analysis suite is designed for strategic healthcare planning. For enhancements or modifications:

1. Review the data pipeline in the main scripts
2. Test with sample data before running full analysis
3. Update documentation for any new features
4. Ensure data quality and accuracy standards

## 📞 Support

For questions about the analysis or technical issues:
- Review the generated reports for detailed insights
- Check the mapping summary for key findings
- Use the interactive visualizations for exploration
- Refer to the comprehensive analysis report for strategic guidance

---

**Last Updated**: June 2025  
**Data Source**: SSM Health Facility Network  
**Analysis Scope**: 1,412 facilities across 20 MSAs 