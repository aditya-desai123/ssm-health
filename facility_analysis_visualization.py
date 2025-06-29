import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from folium import plugins
import geopy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import warnings
warnings.filterwarnings('ignore')

class FacilityAnalyzer:
    def __init__(self, csv_file):
        """Initialize the analyzer with the facility data"""
        self.df = pd.read_csv(csv_file)
        self.geolocator = Nominatim(user_agent="ssm_health_analyzer")
        self.process_data()
    
    def process_data(self):
        """Clean and process the facility data"""
        print("Processing facility data...")
        
        # Clean up the data
        self.df = self.df.dropna(subset=['name', 'city', 'state'])
        
        # Create a unique facility identifier
        self.df['facility_id'] = self.df['name'] + ' - ' + self.df['city'] + ', ' + self.df['state']
        
        # Clean up facility types
        self.df['facility_type'] = self.df['type'].fillna('Unknown')
        
        # Create a simplified facility type category
        def categorize_facility_type(row):
            name = str(row['name']).lower()
            specialty = str(row['specialty']).lower()
            
            if 'hospital' in name:
                return 'Hospital'
            elif 'urgent care' in name or 'urgent care' in specialty:
                return 'Urgent Care'
            elif 'express clinic' in name or 'retail clinic' in specialty:
                return 'Express/Retail Clinic'
            elif 'pharmacy' in name or 'pharmacy' in specialty:
                return 'Pharmacy'
            elif 'imaging' in name or 'mammography' in specialty:
                return 'Imaging Services'
            elif 'laboratory' in name or 'lab' in specialty:
                return 'Laboratory'
            elif 'therapy' in name:
                return 'Therapy Services'
            elif 'cancer' in name or 'oncology' in specialty:
                return 'Cancer Care'
            elif 'cardiology' in name or 'heart' in name:
                return 'Cardiology'
            elif 'orthopedics' in name or 'orthopedics' in specialty:
                return 'Orthopedics'
            elif 'pediatrics' in specialty:
                return 'Pediatrics'
            elif 'obstetrics' in specialty or 'gynecology' in specialty:
                return 'OB/GYN'
            elif 'family medicine' in specialty or 'internal medicine' in specialty:
                return 'Primary Care'
            else:
                return 'Specialty Care'
        
        self.df['facility_category'] = self.df.apply(categorize_facility_type, axis=1)
        
        # Clean up MSA data
        self.df['msa_name_clean'] = self.df['msa_name'].fillna('Unknown MSA')
        self.df['msa_code'] = self.df['msa_code'].fillna(99999)
        
        # Convert MSA population to numeric, handling any non-numeric values
        self.df['msa_population'] = pd.to_numeric(self.df['msa_population'], errors='coerce').fillna(0)
        
        print(f"Processed {len(self.df)} facility records")
        print(f"Unique facilities: {self.df['facility_id'].nunique()}")
        print(f"Unique MSAs: {self.df['msa_name_clean'].nunique()}")
    
    def get_coordinates(self, address, max_retries=3):
        """Get coordinates for an address with retry logic"""
        for attempt in range(max_retries):
            try:
                location = self.geolocator.geocode(address, timeout=10)
                if location:
                    return location.latitude, location.longitude
                time.sleep(1)
            except GeocoderTimedOut:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    return None, None
            except Exception as e:
                print(f"Error geocoding {address}: {e}")
                return None, None
        return None, None
    
    def add_coordinates(self, sample_size=None):
        """Add coordinates to the dataframe"""
        print("Adding coordinates to facilities...")
        
        # If sample_size is provided, use a sample for faster processing
        if sample_size:
            df_sample = self.df.sample(n=min(sample_size, len(self.df)), random_state=42)
        else:
            df_sample = self.df.copy()
        
        coordinates = []
        for idx, row in df_sample.iterrows():
            address = f"{row['street']}, {row['city']}, {row['state']} {row['zip']}"
            lat, lon = self.get_coordinates(address)
            coordinates.append((lat, lon))
            
            # Progress indicator
            if (idx + 1) % 10 == 0:
                print(f"Processed {idx + 1}/{len(df_sample)} facilities")
        
        df_sample['latitude'] = [coord[0] for coord in coordinates]
        df_sample['longitude'] = [coord[1] for coord in coordinates]
        
        # Filter out facilities without coordinates
        df_sample = df_sample.dropna(subset=['latitude', 'longitude'])
        
        return df_sample
    
    def create_interactive_map(self, df_with_coords):
        """Create an interactive map showing facility distribution"""
        print("Creating interactive map...")
        
        # Create a map centered on the middle of the data
        center_lat = df_with_coords['latitude'].mean()
        center_lon = df_with_coords['longitude'].mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=6)
        
        # Color scheme for facility types
        facility_colors = {
            'Hospital': 'red',
            'Urgent Care': 'orange',
            'Express/Retail Clinic': 'yellow',
            'Pharmacy': 'blue',
            'Imaging Services': 'purple',
            'Laboratory': 'green',
            'Therapy Services': 'pink',
            'Cancer Care': 'darkred',
            'Cardiology': 'darkblue',
            'Orthopedics': 'darkgreen',
            'Pediatrics': 'lightblue',
            'OB/GYN': 'lightcoral',
            'Primary Care': 'lightgreen',
            'Specialty Care': 'gray'
        }
        
        # Add markers for each facility
        for idx, row in df_with_coords.iterrows():
            color = facility_colors.get(row['facility_category'], 'gray')
            
            popup_text = f"""
            <b>{row['name']}</b><br>
            <b>Type:</b> {row['facility_category']}<br>
            <b>Specialty:</b> {row['specialty']}<br>
            <b>Address:</b> {row['street']}, {row['city']}, {row['state']}<br>
            <b>MSA:</b> {row['msa_name_clean']}<br>
            <b>MSA Population:</b> {row['msa_population']:,.0f}
            """
            
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=color, icon='info-sign'),
                tooltip=f"{row['name']} - {row['facility_category']}"
            ).add_to(m)
        
        # Add a legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 300px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Facility Types</b></p>
        '''
        
        for facility_type, color in facility_colors.items():
            legend_html += f'<p><i class="fa fa-circle" style="color:{color}"></i> {facility_type}</p>'
        
        legend_html += '</div>'
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Save the map
        map_file = 'ssm_health_facilities_map.html'
        m.save(map_file)
        print(f"Interactive map saved as {map_file}")
        
        return m
    
    def analyze_market_coverage(self):
        """Analyze market coverage to identify overserved and underserved markets"""
        print("Analyzing market coverage...")
        
        # Group by MSA and calculate metrics
        msa_analysis = self.df.groupby(['msa_name_clean', 'msa_code', 'msa_population']).agg({
            'facility_id': 'nunique',
            'facility_category': lambda x: x.value_counts().to_dict(),
            'specialty': lambda x: x.nunique()
        }).reset_index()
        
        msa_analysis.columns = ['msa_name', 'msa_code', 'msa_population', 'facility_count', 'facility_types', 'specialty_count']
        
        # Calculate facilities per capita
        msa_analysis['facilities_per_100k'] = (msa_analysis['facility_count'] / msa_analysis['msa_population']) * 100000
        
        # Calculate percentiles for market classification
        facilities_percentile_75 = msa_analysis['facilities_per_100k'].quantile(0.75)
        facilities_percentile_25 = msa_analysis['facilities_per_100k'].quantile(0.25)
        
        # Classify markets
        def classify_market(row):
            if row['facilities_per_100k'] > facilities_percentile_75:
                return 'Overserved'
            elif row['facilities_per_100k'] < facilities_percentile_25:
                return 'Underserved'
            else:
                return 'Adequately Served'
        
        msa_analysis['market_status'] = msa_analysis.apply(classify_market, axis=1)
        
        # Filter out MSAs with very small populations or missing data
        msa_analysis = msa_analysis[
            (msa_analysis['msa_population'] > 1000) & 
            (msa_analysis['msa_code'] != 99999)
        ]
        
        return msa_analysis
    
    def create_market_analysis_charts(self, msa_analysis):
        """Create charts for market analysis"""
        print("Creating market analysis charts...")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Facilities per 100k Population by MSA',
                'Market Status Distribution',
                'Facility Count vs Population',
                'Top 10 MSAs by Facility Density'
            ),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # Chart 1: Facilities per 100k by MSA
        fig.add_trace(
            go.Bar(
                x=msa_analysis['msa_name'],
                y=msa_analysis['facilities_per_100k'],
                marker_color=msa_analysis['market_status'].map({
                    'Overserved': 'red',
                    'Underserved': 'blue',
                    'Adequately Served': 'green'
                }),
                name='Facilities per 100k'
            ),
            row=1, col=1
        )
        
        # Chart 2: Market status distribution
        status_counts = msa_analysis['market_status'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                name='Market Status'
            ),
            row=1, col=2
        )
        
        # Chart 3: Facility count vs population
        fig.add_trace(
            go.Scatter(
                x=msa_analysis['msa_population'],
                y=msa_analysis['facility_count'],
                mode='markers',
                marker=dict(
                    size=10,
                    color=msa_analysis['market_status'].map({
                        'Overserved': 'red',
                        'Underserved': 'blue',
                        'Adequately Served': 'green'
                    }),
                    opacity=0.7
                ),
                text=msa_analysis['msa_name'],
                name='Facility Count vs Population'
            ),
            row=2, col=1
        )
        
        # Chart 4: Top 10 MSAs by facility density
        top_10_msas = msa_analysis.nlargest(10, 'facilities_per_100k')
        fig.add_trace(
            go.Bar(
                x=top_10_msas['msa_name'],
                y=top_10_msas['facilities_per_100k'],
                marker_color='purple',
                name='Top 10 Facility Density'
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1000,
            title_text="SSM Health Market Analysis Dashboard",
            showlegend=False
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="MSA", row=1, col=1)
        fig.update_yaxes(title_text="Facilities per 100k", row=1, col=1)
        fig.update_xaxes(title_text="Population", row=2, col=1)
        fig.update_yaxes(title_text="Facility Count", row=2, col=1)
        fig.update_xaxes(title_text="MSA", row=2, col=2)
        fig.update_yaxes(title_text="Facilities per 100k", row=2, col=2)
        
        # Save the chart
        chart_file = 'ssm_health_market_analysis.html'
        fig.write_html(chart_file)
        print(f"Market analysis charts saved as {chart_file}")
        
        return fig
    
    def create_facility_type_analysis(self):
        """Create analysis of facility types and specialties"""
        print("Creating facility type analysis...")
        
        # Facility type distribution
        facility_type_counts = self.df['facility_category'].value_counts()
        
        # Specialty distribution
        specialty_counts = self.df['specialty'].value_counts().head(15)
        
        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Facility Type Distribution', 'Top 15 Specialties'),
            specs=[[{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Facility type pie chart
        fig.add_trace(
            go.Pie(
                labels=facility_type_counts.index,
                values=facility_type_counts.values,
                name='Facility Types'
            ),
            row=1, col=1
        )
        
        # Specialty bar chart
        fig.add_trace(
            go.Bar(
                x=specialty_counts.values,
                y=specialty_counts.index,
                orientation='h',
                name='Specialties'
            ),
            row=1, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=600,
            title_text="SSM Health Facility Type and Specialty Analysis",
            showlegend=False
        )
        
        # Save the chart
        chart_file = 'ssm_health_facility_types.html'
        fig.write_html(chart_file)
        print(f"Facility type analysis saved as {chart_file}")
        
        return fig
    
    def generate_recommendations(self, msa_analysis):
        """Generate strategic recommendations based on analysis"""
        print("Generating strategic recommendations...")
        
        # Identify overserved markets
        overserved = msa_analysis[msa_analysis['market_status'] == 'Overserved'].sort_values('facilities_per_100k', ascending=False)
        
        # Identify underserved markets
        underserved = msa_analysis[msa_analysis['market_status'] == 'Underserved'].sort_values('facilities_per_100k')
        
        # Calculate potential savings and opportunities
        recommendations = {
            'overserved_markets': overserved.head(5)[['msa_name', 'facilities_per_100k', 'facility_count', 'msa_population']].to_dict('records'),
            'underserved_markets': underserved.head(5)[['msa_name', 'facilities_per_100k', 'facility_count', 'msa_population']].to_dict('records'),
            'total_overserved_facilities': overserved['facility_count'].sum(),
            'total_underserved_population': underserved['msa_population'].sum(),
            'potential_consolidation_opportunities': len(overserved),
            'potential_expansion_opportunities': len(underserved)
        }
        
        return recommendations
    
    def create_summary_report(self, msa_analysis, recommendations):
        """Create a comprehensive summary report"""
        print("Creating summary report...")
        
        report = f"""
# SSM Health Facility Distribution Analysis Report

## Executive Summary
This analysis examines SSM Health's facility distribution across {len(msa_analysis)} Metropolitan Statistical Areas (MSAs) to identify market optimization opportunities.

## Key Findings

### Market Coverage
- **Total Facilities Analyzed**: {len(self.df)} facility records
- **Unique Facilities**: {self.df['facility_id'].nunique()}
- **Markets Analyzed**: {len(msa_analysis)}
- **Overserved Markets**: {len(msa_analysis[msa_analysis['market_status'] == 'Overserved'])}
- **Underserved Markets**: {len(msa_analysis[msa_analysis['market_status'] == 'Underserved'])}

### Facility Distribution
- **Average Facilities per 100k Population**: {msa_analysis['facilities_per_100k'].mean():.1f}
- **Median Facilities per 100k Population**: {msa_analysis['facilities_per_100k'].median():.1f}
- **Highest Facility Density**: {msa_analysis['facilities_per_100k'].max():.1f} per 100k
- **Lowest Facility Density**: {msa_analysis['facilities_per_100k'].min():.1f} per 100k

## Strategic Recommendations

### Markets for Potential Consolidation (Overserved)
"""
        
        for i, market in enumerate(recommendations['overserved_markets'], 1):
            report += f"""
{i}. **{market['msa_name']}**
   - Facilities per 100k: {market['facilities_per_100k']:.1f}
   - Total Facilities: {market['facility_count']}
   - Population: {market['msa_population']:,.0f}
   - **Recommendation**: Consider consolidating {max(1, market['facility_count'] // 3)} facilities
"""
        
        report += f"""
### Markets for Potential Expansion (Underserved)
"""
        
        for i, market in enumerate(recommendations['underserved_markets'], 1):
            report += f"""
{i}. **{market['msa_name']}**
   - Facilities per 100k: {market['facilities_per_100k']:.1f}
   - Total Facilities: {market['facility_count']}
   - Population: {market['msa_population']:,.0f}
   - **Recommendation**: Consider adding {max(1, int(market['msa_population'] / 50000))} facilities
"""
        
        report += f"""
## Financial Impact Assessment

### Consolidation Opportunities
- **Total Overserved Facilities**: {recommendations['total_overserved_facilities']}
- **Potential Annual Savings**: ${recommendations['total_overserved_facilities'] * 500000:,.0f} (estimated $500k per facility)
- **Markets for Consolidation**: {recommendations['potential_consolidation_opportunities']}

### Expansion Opportunities
- **Underserved Population**: {recommendations['total_underserved_population']:,.0f}
- **Potential Revenue Opportunity**: ${recommendations['total_underserved_population'] * 100:,.0f} (estimated $100 per capita)
- **Markets for Expansion**: {recommendations['potential_expansion_opportunities']}

## Methodology
- Market classification based on facilities per 100k population percentiles
- Overserved: >75th percentile
- Underserved: <25th percentile
- Adequately served: 25th-75th percentile
- Analysis excludes markets with population <1,000 or missing MSA data

## Next Steps
1. Conduct detailed facility-level analysis in overserved markets
2. Perform competitive analysis in underserved markets
3. Develop specific consolidation and expansion plans
4. Implement pilot programs in selected markets
5. Monitor performance metrics post-implementation
"""
        
        # Save the report
        with open('ssm_health_analysis_report.md', 'w') as f:
            f.write(report)
        
        print("Summary report saved as ssm_health_analysis_report.md")
        return report

def main():
    """Main function to run the complete analysis"""
    print("Starting SSM Health Facility Distribution Analysis...")
    
    # Initialize analyzer
    analyzer = FacilityAnalyzer('ssm_health_locations_with_msa_robust.csv')
    
    # Analyze market coverage
    msa_analysis = analyzer.analyze_market_coverage()
    
    # Create visualizations
    analyzer.create_market_analysis_charts(msa_analysis)
    analyzer.create_facility_type_analysis()
    
    # Generate recommendations
    recommendations = analyzer.generate_recommendations(msa_analysis)
    
    # Create summary report
    analyzer.create_summary_report(msa_analysis, recommendations)
    
    # Create interactive map (with sample for faster processing)
    print("\nCreating interactive map (using sample of 100 facilities for faster processing)...")
    df_sample = analyzer.add_coordinates(sample_size=100)
    analyzer.create_interactive_map(df_sample)
    
    print("\nAnalysis complete! Generated files:")
    print("- ssm_health_market_analysis.html (Market analysis dashboard)")
    print("- ssm_health_facility_types.html (Facility type analysis)")
    print("- ssm_health_facilities_map.html (Interactive facility map)")
    print("- ssm_health_analysis_report.md (Comprehensive analysis report)")
    
    # Display key insights
    print(f"\nKey Insights:")
    print(f"- Total facilities analyzed: {len(analyzer.df)}")
    print(f"- Unique markets: {len(msa_analysis)}")
    print(f"- Overserved markets: {len(msa_analysis[msa_analysis['market_status'] == 'Overserved'])}")
    print(f"- Underserved markets: {len(msa_analysis[msa_analysis['market_status'] == 'Underserved'])}")
    print(f"- Potential consolidation opportunities: {recommendations['potential_consolidation_opportunities']}")
    print(f"- Potential expansion opportunities: {recommendations['potential_expansion_opportunities']}")

if __name__ == "__main__":
    main() 