#!/usr/bin/env python3
"""
Enhanced SSM Health Facility Analysis with Income Data
"""

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

class EnhancedFacilityAnalyzer:
    def __init__(self, csv_file):
        """Initialize the analyzer with the facility data including income"""
        self.df = pd.read_csv(csv_file)
        self.geolocator = Nominatim(user_agent="ssm_health_analyzer")
        self.process_data()
    
    def process_data(self):
        """Clean and process the facility data with income information"""
        print("Processing facility data with income information...")
        
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
        
        # Process income data
        self.df['msa_median_household_income'] = pd.to_numeric(self.df['msa_median_household_income'], errors='coerce').fillna(67000)
        
        # Create income categories
        self.df['income_category'] = pd.cut(
            self.df['msa_median_household_income'],
            bins=[0, 55000, 65000, 75000, 85000, float('inf')],
            labels=['<$55k', '$55k-65k', '$65k-75k', '$75k-85k', '$85k+']
        )
        
        print(f"Processed {len(self.df)} facility records")
        print(f"Unique facilities: {self.df['facility_id'].nunique()}")
        print(f"Unique MSAs: {self.df['msa_name_clean'].nunique()}")
        print(f"Average median household income: ${self.df['msa_median_household_income'].mean():,.0f}")
    
    def analyze_market_coverage_with_income(self):
        """Analyze market coverage including income factors"""
        print("Analyzing market coverage with income data...")
        
        # Group by MSA and calculate metrics
        msa_analysis = self.df.groupby(['msa_name_clean', 'msa_code', 'msa_population', 'msa_median_household_income']).agg({
            'facility_id': 'nunique',
            'facility_category': lambda x: x.value_counts().to_dict(),
            'specialty': lambda x: x.nunique(),
            'income_category': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Unknown'
        }).reset_index()
        
        msa_analysis.columns = ['msa_name', 'msa_code', 'msa_population', 'msa_median_household_income', 'facility_count', 'facility_types', 'specialty_count', 'income_category']
        
        # Calculate facilities per capita
        msa_analysis['facilities_per_100k'] = (msa_analysis['facility_count'] / msa_analysis['msa_population']) * 100000
        
        # Calculate income-adjusted facility density (facilities per 100k per $10k income)
        msa_analysis['income_adjusted_density'] = (msa_analysis['facilities_per_100k'] / (msa_analysis['msa_median_household_income'] / 10000))
        
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
    
    def create_enhanced_market_analysis_charts(self, msa_analysis):
        """Create enhanced charts including income data"""
        print("Creating enhanced market analysis charts...")
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Facilities per 100k Population by MSA',
                'Market Status Distribution',
                'Facility Count vs Population',
                'Income vs Facility Density',
                'Income Distribution by Market Status',
                'Top 10 MSAs by Income-Adjusted Density'
            ),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "box"}, {"type": "bar"}]]
        )
        
        # Chart 1: Facilities per 100k by MSA (color by income)
        fig.add_trace(
            go.Bar(
                x=msa_analysis['msa_name'],
                y=msa_analysis['facilities_per_100k'],
                marker_color=msa_analysis['msa_median_household_income'],
                marker_colorscale='Viridis',
                colorbar=dict(title="Median Income ($)"),
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
        
        # Chart 3: Facility count vs population (color by income)
        fig.add_trace(
            go.Scatter(
                x=msa_analysis['msa_population'],
                y=msa_analysis['facility_count'],
                mode='markers',
                marker=dict(
                    size=10,
                    color=msa_analysis['msa_median_household_income'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Median Income ($)")
                ),
                text=msa_analysis['msa_name'],
                name='Facility Count vs Population'
            ),
            row=2, col=1
        )
        
        # Chart 4: Income vs facility density
        fig.add_trace(
            go.Scatter(
                x=msa_analysis['msa_median_household_income'],
                y=msa_analysis['facilities_per_100k'],
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
                name='Income vs Facility Density'
            ),
            row=2, col=2
        )
        
        # Chart 5: Income distribution by market status
        for status in ['Overserved', 'Underserved', 'Adequately Served']:
            status_data = msa_analysis[msa_analysis['market_status'] == status]['msa_median_household_income']
            if len(status_data) > 0:
                fig.add_trace(
                    go.Box(
                        y=status_data,
                        name=status,
                        boxpoints='outliers'
                    ),
                    row=3, col=1
                )
        
        # Chart 6: Top 10 MSAs by income-adjusted density
        top_10_income_adjusted = msa_analysis.nlargest(10, 'income_adjusted_density')
        fig.add_trace(
            go.Bar(
                x=top_10_income_adjusted['msa_name'],
                y=top_10_income_adjusted['income_adjusted_density'],
                marker_color='purple',
                name='Income-Adjusted Density'
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text="SSM Health Enhanced Market Analysis Dashboard (with Income Data)",
            showlegend=False
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="MSA", row=1, col=1)
        fig.update_yaxes(title_text="Facilities per 100k", row=1, col=1)
        fig.update_xaxes(title_text="Population", row=2, col=1)
        fig.update_yaxes(title_text="Facility Count", row=2, col=1)
        fig.update_xaxes(title_text="Median Household Income ($)", row=2, col=2)
        fig.update_yaxes(title_text="Facilities per 100k", row=2, col=2)
        fig.update_xaxes(title_text="Market Status", row=3, col=1)
        fig.update_yaxes(title_text="Median Household Income ($)", row=3, col=1)
        fig.update_xaxes(title_text="MSA", row=3, col=2)
        fig.update_yaxes(title_text="Income-Adjusted Density", row=3, col=2)
        
        # Save the chart
        chart_file = 'ssm_health_enhanced_market_analysis.html'
        fig.write_html(chart_file)
        print(f"Enhanced market analysis charts saved as {chart_file}")
        
        return fig
    
    def create_income_analysis_charts(self):
        """Create charts specifically for income analysis"""
        print("Creating income analysis charts...")
        
        # Income distribution
        income_dist = self.df['msa_median_household_income'].value_counts(bins=10).sort_index()
        
        # Facility distribution by income category
        facility_by_income = self.df.groupby('income_category').size().reset_index(name='facility_count')
        
        # Facility type distribution by income
        facility_type_by_income = self.df.groupby(['income_category', 'facility_category']).size().reset_index(name='count')
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Income Distribution',
                'Facilities by Income Category',
                'Facility Types by Income Category',
                'Income vs Facility Type Heatmap'
            ),
            specs=[[{"type": "histogram"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "heatmap"}]]
        )
        
        # Chart 1: Income distribution histogram
        fig.add_trace(
            go.Histogram(
                x=self.df['msa_median_household_income'],
                nbinsx=20,
                name='Income Distribution'
            ),
            row=1, col=1
        )
        
        # Chart 2: Facilities by income category
        fig.add_trace(
            go.Bar(
                x=facility_by_income['income_category'],
                y=facility_by_income['facility_count'],
                name='Facilities by Income'
            ),
            row=1, col=2
        )
        
        # Chart 3: Facility types by income category
        for facility_type in self.df['facility_category'].unique():
            type_data = facility_type_by_income[facility_type_by_income['facility_category'] == facility_type]
            if len(type_data) > 0:
                fig.add_trace(
                    go.Bar(
                        x=type_data['income_category'],
                        y=type_data['count'],
                        name=facility_type
                    ),
                    row=2, col=1
                )
        
        # Chart 4: Income vs Facility Type Heatmap
        pivot_data = facility_type_by_income.pivot(index='facility_category', columns='income_category', values='count').fillna(0)
        
        fig.add_trace(
            go.Heatmap(
                z=pivot_data.values,
                x=pivot_data.columns,
                y=pivot_data.index,
                colorscale='Viridis',
                name='Income vs Facility Type'
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text="SSM Health Income Analysis Dashboard",
            showlegend=True
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Median Household Income ($)", row=1, col=1)
        fig.update_yaxes(title_text="Number of Facilities", row=1, col=1)
        fig.update_xaxes(title_text="Income Category", row=1, col=2)
        fig.update_yaxes(title_text="Number of Facilities", row=1, col=2)
        fig.update_xaxes(title_text="Income Category", row=2, col=1)
        fig.update_yaxes(title_text="Number of Facilities", row=2, col=1)
        
        # Save the chart
        chart_file = 'ssm_health_income_analysis_dashboard.html'
        fig.write_html(chart_file)
        print(f"Income analysis dashboard saved as {chart_file}")
        
        return fig
    
    def generate_enhanced_recommendations(self, msa_analysis):
        """Generate strategic recommendations including income factors"""
        print("Generating enhanced strategic recommendations...")
        
        # Identify overserved markets
        overserved = msa_analysis[msa_analysis['market_status'] == 'Overserved'].sort_values('facilities_per_100k', ascending=False)
        
        # Identify underserved markets
        underserved = msa_analysis[msa_analysis['market_status'] == 'Underserved'].sort_values('facilities_per_100k')
        
        # High-income overserved markets (potential for premium services)
        high_income_overserved = overserved[overserved['msa_median_household_income'] > 70000]
        
        # Low-income underserved markets (potential for community health focus)
        low_income_underserved = underserved[underserved['msa_median_household_income'] < 60000]
        
        # Calculate potential savings and opportunities
        recommendations = {
            'overserved_markets': overserved.head(5)[['msa_name', 'facilities_per_100k', 'facility_count', 'msa_population', 'msa_median_household_income']].to_dict('records'),
            'underserved_markets': underserved.head(5)[['msa_name', 'facilities_per_100k', 'facility_count', 'msa_population', 'msa_median_household_income']].to_dict('records'),
            'high_income_overserved': high_income_overserved.head(3)[['msa_name', 'facilities_per_100k', 'facility_count', 'msa_population', 'msa_median_household_income']].to_dict('records'),
            'low_income_underserved': low_income_underserved.head(3)[['msa_name', 'facilities_per_100k', 'facility_count', 'msa_population', 'msa_median_household_income']].to_dict('records'),
            'total_overserved_facilities': overserved['facility_count'].sum(),
            'total_underserved_population': underserved['msa_population'].sum(),
            'potential_consolidation_opportunities': len(overserved),
            'potential_expansion_opportunities': len(underserved),
            'avg_income_overserved': overserved['msa_median_household_income'].mean(),
            'avg_income_underserved': underserved['msa_median_household_income'].mean()
        }
        
        return recommendations
    
    def create_enhanced_summary_report(self, msa_analysis, recommendations):
        """Create a comprehensive summary report including income analysis"""
        print("Creating enhanced summary report...")
        
        report = f"""
# SSM Health Enhanced Facility Distribution Analysis Report (with Income Data)

## Executive Summary
This enhanced analysis examines SSM Health's facility distribution across {len(msa_analysis)} Metropolitan Statistical Areas (MSAs), incorporating median household income data to provide deeper insights into market optimization opportunities.

## Key Findings

### Market Coverage
- **Total Facilities Analyzed**: {len(self.df)} facility records
- **Unique Facilities**: {self.df['facility_id'].nunique()}
- **Markets Analyzed**: {len(msa_analysis)}
- **Overserved Markets**: {len(msa_analysis[msa_analysis['market_status'] == 'Overserved'])}
- **Underserved Markets**: {len(msa_analysis[msa_analysis['market_status'] == 'Underserved'])}

### Income Analysis
- **Average Median Household Income**: ${self.df['msa_median_household_income'].mean():,.0f}
- **Income Range**: ${self.df['msa_median_household_income'].min():,.0f} - ${self.df['msa_median_household_income'].max():,.0f}
- **Average Income in Overserved Markets**: ${recommendations['avg_income_overserved']:,.0f}
- **Average Income in Underserved Markets**: ${recommendations['avg_income_underserved']:,.0f}

### Facility Distribution
- **Average Facilities per 100k Population**: {msa_analysis['facilities_per_100k'].mean():.1f}
- **Median Facilities per 100k Population**: {msa_analysis['facilities_per_100k'].median():.1f}
- **Highest Facility Density**: {msa_analysis['facilities_per_100k'].max():.1f} per 100k
- **Lowest Facility Density**: {msa_analysis['facilities_per_100k'].min():.1f} per 100k

## Enhanced Strategic Recommendations

### High-Income Overserved Markets (Premium Service Opportunities)
"""
        
        for i, market in enumerate(recommendations['high_income_overserved'], 1):
            report += f"""
{i}. **{market['msa_name']}**
   - Facilities per 100k: {market['facilities_per_100k']:.1f}
   - Total Facilities: {market['facility_count']}
   - Population: {market['msa_population']:,.0f}
   - Median Income: ${market['msa_median_household_income']:,.0f}
   - **Recommendation**: Consider consolidating facilities but adding premium services (concierge medicine, specialized care)
"""
        
        report += f"""
### Low-Income Underserved Markets (Community Health Focus)
"""
        
        for i, market in enumerate(recommendations['low_income_underserved'], 1):
            report += f"""
{i}. **{market['msa_name']}**
   - Facilities per 100k: {market['facilities_per_100k']:.1f}
   - Total Facilities: {market['facility_count']}
   - Population: {market['msa_population']:,.0f}
   - Median Income: ${market['msa_median_household_income']:,.0f}
   - **Recommendation**: Add community health centers with sliding scale pricing and preventive care focus
"""
        
        report += f"""
### General Markets for Potential Consolidation (Overserved)
"""
        
        for i, market in enumerate(recommendations['overserved_markets'], 1):
            report += f"""
{i}. **{market['msa_name']}**
   - Facilities per 100k: {market['facilities_per_100k']:.1f}
   - Total Facilities: {market['facility_count']}
   - Population: {market['msa_population']:,.0f}
   - Median Income: ${market['msa_median_household_income']:,.0f}
   - **Recommendation**: Consider consolidating {max(1, market['facility_count'] // 3)} facilities
"""
        
        report += f"""
### General Markets for Potential Expansion (Underserved)
"""
        
        for i, market in enumerate(recommendations['underserved_markets'], 1):
            report += f"""
{i}. **{market['msa_name']}**
   - Facilities per 100k: {market['facilities_per_100k']:.1f}
   - Total Facilities: {market['facility_count']}
   - Population: {market['msa_population']:,.0f}
   - Median Income: ${market['msa_median_household_income']:,.0f}
   - **Recommendation**: Consider adding {max(1, int(market['msa_population'] / 50000))} facilities
"""
        
        report += f"""
## Enhanced Financial Impact Assessment

### Consolidation Opportunities
- **Total Overserved Facilities**: {recommendations['total_overserved_facilities']}
- **Potential Annual Savings**: ${recommendations['total_overserved_facilities'] * 500000:,.0f} (estimated $500k per facility)
- **Markets for Consolidation**: {recommendations['potential_consolidation_opportunities']}
- **Average Income in Consolidation Markets**: ${recommendations['avg_income_overserved']:,.0f}

### Expansion Opportunities
- **Underserved Population**: {recommendations['total_underserved_population']:,.0f}
- **Potential Revenue Opportunity**: ${recommendations['total_underserved_population'] * 100:,.0f} (estimated $100 per capita)
- **Markets for Expansion**: {recommendations['potential_expansion_opportunities']}
- **Average Income in Expansion Markets**: ${recommendations['avg_income_underserved']:,.0f}

## Income-Based Strategic Insights

### High-Income Market Strategy
- Focus on premium services and specialized care in high-income overserved markets
- Consider concierge medicine models and advanced diagnostic services
- Target markets with median income >$70,000 for premium service expansion

### Low-Income Market Strategy
- Prioritize community health centers and preventive care in low-income underserved markets
- Implement sliding scale pricing and financial assistance programs
- Focus on primary care and essential services in markets with median income <$60,000

## Methodology
- Market classification based on facilities per 100k population percentiles
- Income data from Census Bureau ACS 5-year estimates
- Overserved: >75th percentile facility density
- Underserved: <25th percentile facility density
- Adequately served: 25th-75th percentile facility density
- Analysis excludes markets with population <1,000 or missing MSA data

## Next Steps
1. Conduct detailed facility-level analysis in overserved markets
2. Perform competitive analysis in underserved markets
3. Develop income-based service tier strategies
4. Implement pilot programs in selected markets
5. Monitor performance metrics post-implementation
6. Consider income-based pricing strategies
"""
        
        # Save the report
        with open('ssm_health_enhanced_analysis_report.md', 'w') as f:
            f.write(report)
        
        print("Enhanced summary report saved as ssm_health_enhanced_analysis_report.md")
        return report

def main():
    """Main function to run the enhanced analysis"""
    print("Starting SSM Health Enhanced Facility Distribution Analysis (with Income Data)...")
    
    # Initialize analyzer with income data
    analyzer = EnhancedFacilityAnalyzer('ssm_health_locations_with_income.csv')
    
    # Analyze market coverage with income
    msa_analysis = analyzer.analyze_market_coverage_with_income()
    
    # Create enhanced visualizations
    analyzer.create_enhanced_market_analysis_charts(msa_analysis)
    analyzer.create_income_analysis_charts()
    
    # Generate enhanced recommendations
    recommendations = analyzer.generate_enhanced_recommendations(msa_analysis)
    
    # Create enhanced summary report
    analyzer.create_enhanced_summary_report(msa_analysis, recommendations)
    
    print("\nEnhanced analysis complete! Generated files:")
    print("- ssm_health_enhanced_market_analysis.html (Enhanced market analysis dashboard)")
    print("- ssm_health_income_analysis_dashboard.html (Income analysis dashboard)")
    print("- ssm_health_enhanced_analysis_report.md (Enhanced analysis report)")
    
    # Display key insights
    print(f"\nKey Enhanced Insights:")
    print(f"- Total facilities analyzed: {len(analyzer.df)}")
    print(f"- Unique markets: {len(msa_analysis)}")
    print(f"- Average median household income: ${analyzer.df['msa_median_household_income'].mean():,.0f}")
    print(f"- Overserved markets: {len(msa_analysis[msa_analysis['market_status'] == 'Overserved'])}")
    print(f"- Underserved markets: {len(msa_analysis[msa_analysis['market_status'] == 'Underserved'])}")
    print(f"- High-income overserved markets: {len(recommendations['high_income_overserved'])}")
    print(f"- Low-income underserved markets: {len(recommendations['low_income_underserved'])}")

if __name__ == "__main__":
    main() 