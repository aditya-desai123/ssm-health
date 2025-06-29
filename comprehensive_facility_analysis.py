#!/usr/bin/env python3
"""
Comprehensive SSM Health Facility Analysis with Income and Age Demographics
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

class ComprehensiveFacilityAnalyzer:
    def __init__(self, csv_file):
        """Initialize the analyzer with the facility data including income and age demographics"""
        self.df = pd.read_csv(csv_file)
        self.geolocator = Nominatim(user_agent="ssm_health_analyzer")
        self.process_data()
    
    def clean_msa_names(self, df, msa_column='msa_name'):
        """
        Clean MSA names by replacing "Micropolitan Statistical Area" with "Metropolitan Statistical Area"
        
        Args:
            df: pandas DataFrame
            msa_column: name of the column containing MSA names
        
        Returns:
            DataFrame with cleaned MSA names
        """
        if msa_column in df.columns:
            # Replace "Micropolitan Statistical Area" with "Metropolitan Statistical Area"
            df[msa_column] = df[msa_column].str.replace(
                'Micropolitan Statistical Area', 
                'Metropolitan Statistical Area', 
                case=False
            )
            print(f"✅ Cleaned MSA names in column '{msa_column}'")
        else:
            print(f"⚠️ Column '{msa_column}' not found in DataFrame")
        
        return df
    
    def process_data(self):
        """Clean and process the facility data"""
        print("Processing facility data...")
        
        # Clean MSA names first
        self.df = self.clean_msa_names(self.df, 'msa_name')
        
        # Clean data
        self.df = self.df.dropna(subset=['name', 'city', 'state'])
        
        # Fill missing values
        self.df['type'] = self.df['type'].fillna('Unknown')
        self.df['specialty'] = self.df['specialty'].fillna('General')
        
        # Create facility categories
        self.df['facility_category'] = self.df['type'].apply(self.categorize_facility)
        
        # Calculate facilities per 100k population
        self.df['facilities_per_100k'] = (1 / self.df['msa_population']) * 100000
        
        # Create market status based on facilities per 100k
        self.df['market_status'] = self.df['facilities_per_100k'].apply(self.categorize_market)
        
        # Create income categories
        self.df['income_category'] = pd.cut(
            self.df['msa_median_household_income'], 
            bins=[0, 50000, 70000, 90000, float('inf')],
            labels=['Low Income', 'Lower Middle', 'Upper Middle', 'High Income']
        )
        
        # Create age mix categories for analysis
        self.df['senior_population'] = self.df['pct_65_plus'] > 18
        self.df['youth_population'] = self.df['pct_under_18'] > 25
        self.df['young_adult_population'] = self.df['pct_18_34'] > 25
        
        print(f"Processed {len(self.df)} facilities across {self.df['msa_code'].nunique()} MSAs")
    
    def categorize_facility(self, facility_type):
        """Categorize facility types"""
        if pd.isna(facility_type):
            return 'Unknown'
        
        facility_type = str(facility_type).lower()
        
        if any(word in facility_type for word in ['hospital', 'medical center']):
            return 'Hospital'
        elif any(word in facility_type for word in ['urgent', 'express', 'walk']):
            return 'Urgent Care'
        elif any(word in facility_type for word in ['pharmacy', 'prescription']):
            return 'Pharmacy'
        elif any(word in facility_type for word in ['imaging', 'radiology', 'mammography']):
            return 'Imaging'
        elif any(word in facility_type for word in ['laboratory', 'lab']):
            return 'Laboratory'
        elif any(word in facility_type for word in ['therapy', 'rehabilitation']):
            return 'Therapy'
        elif any(word in facility_type for word in ['cancer', 'oncology']):
            return 'Cancer Care'
        elif any(word in facility_type for word in ['eye', 'ophthalmology']):
            return 'Eye Care'
        elif any(word in facility_type for word in ['hospice']):
            return 'Hospice'
        else:
            return 'Primary Care'
    
    def categorize_market(self, facilities_per_100k):
        """Categorize market status based on facility density"""
        if pd.isna(facilities_per_100k):
            return 'Unknown'
        elif facilities_per_100k > 50:
            return 'Overserved'
        elif facilities_per_100k < 20:
            return 'Underserved'
        else:
            return 'Adequately Served'
    
    def create_comprehensive_dashboard(self):
        """Create a comprehensive dashboard with income and age demographics"""
        print("Creating comprehensive dashboard...")
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Facilities per 100k Population by MSA',
                'Market Status Distribution',
                'Income vs Facility Density',
                'Age Demographics by MSA',
                'Facility Distribution by Income Level',
                'Age Mix Categories Distribution'
            ),
            specs=[
                [{"type": "bar"}, {"type": "pie"}],
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "pie"}]
            ]
        )
        
        # Chart 1: Facilities per 100k by MSA
        msa_summary = self.df.groupby(['msa_name', 'msa_code']).agg({
            'facilities_per_100k': 'first',
            'msa_median_household_income': 'first',
            'median_age': 'first'
        }).reset_index()
        
        msa_summary = msa_summary.sort_values('facilities_per_100k', ascending=True).tail(15)
        
        fig.add_trace(
            go.Bar(
                x=msa_summary['facilities_per_100k'],
                y=msa_summary['msa_name'],
                orientation='h',
                name='Facilities per 100k',
                marker_color='lightblue'
            ),
            row=1, col=1
        )
        
        # Chart 2: Market Status Distribution
        market_status_counts = self.df['market_status'].value_counts()
        
        fig.add_trace(
            go.Pie(
                labels=market_status_counts.index,
                values=market_status_counts.values,
                name='Market Status',
                marker_colors=['#ff7f0e', '#2ca02c', '#d62728']
            ),
            row=1, col=2
        )
        
        # Chart 3: Income vs Facility Density
        fig.add_trace(
            go.Scatter(
                x=self.df['msa_median_household_income'],
                y=self.df['facilities_per_100k'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=self.df['median_age'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Median Age")
                ),
                text=self.df['msa_name'],
                name='Income vs Density'
            ),
            row=2, col=1
        )
        
        # Chart 4: Age Demographics by MSA
        age_demo_summary = self.df.groupby('msa_name').agg({
            'pct_under_18': 'first',
            'pct_18_34': 'first',
            'pct_35_54': 'first',
            'pct_55_64': 'first',
            'pct_65_plus': 'first'
        }).reset_index()
        
        age_demo_summary = age_demo_summary.sort_values('pct_65_plus', ascending=False).head(10)
        
        fig.add_trace(
            go.Bar(
                x=age_demo_summary['msa_name'],
                y=age_demo_summary['pct_under_18'],
                name='Under 18',
                marker_color='lightgreen'
            ),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Bar(
                x=age_demo_summary['msa_name'],
                y=age_demo_summary['pct_18_34'],
                name='18-34',
                marker_color='lightblue'
            ),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Bar(
                x=age_demo_summary['msa_name'],
                y=age_demo_summary['pct_35_54'],
                name='35-54',
                marker_color='orange'
            ),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Bar(
                x=age_demo_summary['msa_name'],
                y=age_demo_summary['pct_55_64'],
                name='55-64',
                marker_color='red'
            ),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Bar(
                x=age_demo_summary['msa_name'],
                y=age_demo_summary['pct_65_plus'],
                name='65+',
                marker_color='purple'
            ),
            row=2, col=2
        )
        
        # Chart 5: Facility Distribution by Income Level
        income_facility_counts = self.df.groupby('income_category')['facility_category'].value_counts().unstack(fill_value=0)
        
        for facility_type in income_facility_counts.columns:
            fig.add_trace(
                go.Bar(
                    x=income_facility_counts.index,
                    y=income_facility_counts[facility_type],
                    name=facility_type,
                    showlegend=False
                ),
                row=3, col=1
            )
        
        # Chart 6: Age Mix Categories Distribution
        age_mix_counts = self.df['age_mix_category'].value_counts()
        
        fig.add_trace(
            go.Pie(
                labels=age_mix_counts.index,
                values=age_mix_counts.values,
                name='Age Mix Categories',
                marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'SSM Health Comprehensive Market Analysis Dashboard<br><sub>Income, Age Demographics, and Facility Distribution</sub>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            height=1200,
            showlegend=True,
            template='plotly_white'
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Facilities per 100k Population", row=1, col=1)
        fig.update_xaxes(title_text="Median Household Income ($)", row=2, col=1)
        fig.update_yaxes(title_text="Facilities per 100k Population", row=2, col=1)
        fig.update_xaxes(title_text="MSA", row=2, col=2)
        fig.update_yaxes(title_text="Percentage (%)", row=2, col=2)
        fig.update_xaxes(title_text="Income Category", row=3, col=1)
        fig.update_yaxes(title_text="Number of Facilities", row=3, col=1)
        
        # Save the dashboard
        fig.write_html('ssm_health_comprehensive_dashboard.html')
        print("Comprehensive dashboard saved to ssm_health_comprehensive_dashboard.html")
        
        return fig
    
    def create_income_age_analysis(self):
        """Create detailed income and age analysis"""
        print("Creating income and age analysis...")
        
        # Create subplots for income and age analysis
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Income Distribution by MSA',
                'Age Distribution by MSA',
                'Income vs Age Correlation',
                'Facility Types by Income Level'
            ),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # Chart 1: Income Distribution by MSA
        income_summary = self.df.groupby(['msa_name', 'msa_code'])['msa_median_household_income'].first().sort_values(ascending=False).head(15)
        
        fig.add_trace(
            go.Bar(
                x=income_summary.values,
                y=income_summary.index,
                orientation='h',
                name='Median Income',
                marker_color='green'
            ),
            row=1, col=1
        )
        
        # Chart 2: Age Distribution by MSA
        age_summary = self.df.groupby(['msa_name', 'msa_code'])['median_age'].first().sort_values(ascending=False).head(15)
        
        fig.add_trace(
            go.Bar(
                x=age_summary.values,
                y=age_summary.index,
                orientation='h',
                name='Median Age',
                marker_color='blue'
            ),
            row=1, col=2
        )
        
        # Chart 3: Income vs Age Correlation
        msa_analysis = self.df.groupby(['msa_name', 'msa_code']).agg({
            'msa_median_household_income': 'first',
            'median_age': 'first',
            'facilities_per_100k': 'first'
        }).reset_index()
        
        fig.add_trace(
            go.Scatter(
                x=msa_analysis['msa_median_household_income'],
                y=msa_analysis['median_age'],
                mode='markers',
                marker=dict(
                    size=msa_analysis['facilities_per_100k'] * 2,
                    color=msa_analysis['facilities_per_100k'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Facilities per 100k")
                ),
                text=msa_analysis['msa_name'],
                name='Income vs Age'
            ),
            row=2, col=1
        )
        
        # Chart 4: Facility Types by Income Level
        income_facility_summary = self.df.groupby(['income_category', 'facility_category']).size().unstack(fill_value=0)
        
        for facility_type in income_facility_summary.columns:
            fig.add_trace(
                go.Bar(
                    x=income_facility_summary.index,
                    y=income_facility_summary[facility_type],
                    name=facility_type
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'SSM Health Income and Age Demographics Analysis<br><sub>Market Insights for Strategic Planning</sub>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            height=1000,
            showlegend=True,
            template='plotly_white'
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Median Household Income ($)", row=1, col=1)
        fig.update_xaxes(title_text="Median Age (years)", row=1, col=2)
        fig.update_xaxes(title_text="Median Household Income ($)", row=2, col=1)
        fig.update_yaxes(title_text="Median Age (years)", row=2, col=1)
        fig.update_xaxes(title_text="Income Category", row=2, col=2)
        fig.update_yaxes(title_text="Number of Facilities", row=2, col=2)
        
        # Save the analysis
        fig.write_html('ssm_health_income_age_analysis.html')
        print("Income and age analysis saved to ssm_health_income_age_analysis.html")
        
        return fig
    
    def create_strategic_recommendations(self):
        """Create strategic recommendations based on the analysis"""
        print("Creating strategic recommendations...")
        
        # Analyze market opportunities and risks
        msa_analysis = self.df.groupby(['msa_name', 'msa_code']).agg({
            'msa_median_household_income': 'first',
            'median_age': 'first',
            'facilities_per_100k': 'first',
            'pct_65_plus': 'first',
            'pct_under_18': 'first',
            'pct_18_34': 'first',
            'market_status': 'first'
        }).reset_index()
        
        # Identify opportunities
        high_income_underserved = msa_analysis[
            (msa_analysis['msa_median_household_income'] > 80000) & 
            (msa_analysis['market_status'] == 'Underserved')
        ]
        
        senior_population_opportunities = msa_analysis[
            (msa_analysis['pct_65_plus'] > 20) & 
            (msa_analysis['facilities_per_100k'] < 30)
        ]
        
        young_population_opportunities = msa_analysis[
            (msa_analysis['pct_under_18'] > 25) & 
            (msa_analysis['facilities_per_100k'] < 25)
        ]
        
        # Identify risks (overserved markets)
        overserved_markets = msa_analysis[msa_analysis['market_status'] == 'Overserved']
        
        # Create recommendations visualization
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'High-Income Underserved Markets',
                'Senior Population Opportunities',
                'Young Population Opportunities',
                'Overserved Markets (Risk)'
            ),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Chart 1: High-Income Underserved Markets
        if not high_income_underserved.empty:
            fig.add_trace(
                go.Bar(
                    x=high_income_underserved['msa_name'],
                    y=high_income_underserved['msa_median_household_income'],
                    name='High-Income Underserved',
                    marker_color='green'
                ),
                row=1, col=1
            )
        
        # Chart 2: Senior Population Opportunities
        if not senior_population_opportunities.empty:
            fig.add_trace(
                go.Bar(
                    x=senior_population_opportunities['msa_name'],
                    y=senior_population_opportunities['pct_65_plus'],
                    name='Senior Population %',
                    marker_color='purple'
                ),
                row=1, col=2
            )
        
        # Chart 3: Young Population Opportunities
        if not young_population_opportunities.empty:
            fig.add_trace(
                go.Bar(
                    x=young_population_opportunities['msa_name'],
                    y=young_population_opportunities['pct_under_18'],
                    name='Young Population %',
                    marker_color='orange'
                ),
                row=2, col=1
            )
        
        # Chart 4: Overserved Markets
        if not overserved_markets.empty:
            fig.add_trace(
                go.Bar(
                    x=overserved_markets['msa_name'],
                    y=overserved_markets['facilities_per_100k'],
                    name='Facilities per 100k',
                    marker_color='red'
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'SSM Health Strategic Recommendations<br><sub>Market Opportunities and Risks Analysis</sub>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            height=1000,
            showlegend=True,
            template='plotly_white'
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="MSA", row=1, col=1)
        fig.update_yaxes(title_text="Median Income ($)", row=1, col=1)
        fig.update_xaxes(title_text="MSA", row=1, col=2)
        fig.update_yaxes(title_text="Senior Population %", row=1, col=2)
        fig.update_xaxes(title_text="MSA", row=2, col=1)
        fig.update_yaxes(title_text="Young Population %", row=2, col=1)
        fig.update_xaxes(title_text="MSA", row=2, col=2)
        fig.update_yaxes(title_text="Facilities per 100k", row=2, col=2)
        
        # Save the recommendations
        fig.write_html('ssm_health_strategic_recommendations.html')
        print("Strategic recommendations saved to ssm_health_strategic_recommendations.html")
        
        # Create text recommendations
        self.create_recommendations_report(msa_analysis, high_income_underserved, 
                                         senior_population_opportunities, young_population_opportunities, 
                                         overserved_markets)
        
        return fig
    
    def create_recommendations_report(self, msa_analysis, high_income_underserved, 
                                    senior_population_opportunities, young_population_opportunities, 
                                    overserved_markets):
        """Create a text-based recommendations report"""
        
        report = f"""
# SSM Health Strategic Market Analysis Report

## Executive Summary
This report provides comprehensive analysis of SSM Health's market presence, incorporating income demographics and age distribution data to identify strategic opportunities and risks.

## Key Findings

### Market Coverage
- **Total Facilities**: {len(self.df):,}
- **Markets Served**: {self.df['msa_code'].nunique()}
- **Average Facilities per 100k**: {self.df['facilities_per_100k'].mean():.1f}
- **Average Median Income**: ${self.df['msa_median_household_income'].mean():,.0f}
- **Average Median Age**: {self.df['median_age'].mean():.1f} years

### Market Status Distribution
{self.df['market_status'].value_counts().to_string()}

### Income Distribution
{self.df['income_category'].value_counts().to_string()}

### Age Demographics
- **Average % Under 18**: {self.df['pct_under_18'].mean():.1f}%
- **Average % 18-34**: {self.df['pct_18_34'].mean():.1f}%
- **Average % 35-54**: {self.df['pct_35_54'].mean():.1f}%
- **Average % 55-64**: {self.df['pct_55_64'].mean():.1f}%
- **Average % 65+**: {self.df['pct_65_plus'].mean():.1f}%

## Strategic Opportunities

### 1. High-Income Underserved Markets
{len(high_income_underserved)} markets identified with high income potential but low facility density:

"""
        
        if not high_income_underserved.empty:
            for _, market in high_income_underserved.iterrows():
                report += f"- **{market['msa_name']}**: ${market['msa_median_household_income']:,.0f} median income, {market['facilities_per_100k']:.1f} facilities per 100k\n"
        
        report += f"""
### 2. Senior Population Opportunities
{len(senior_population_opportunities)} markets with high senior population but limited facilities:

"""
        
        if not senior_population_opportunities.empty:
            for _, market in senior_population_opportunities.iterrows():
                report += f"- **{market['msa_name']}**: {market['pct_65_plus']:.1f}% seniors, {market['facilities_per_100k']:.1f} facilities per 100k\n"
        
        report += f"""
### 3. Young Population Opportunities
{len(young_population_opportunities)} markets with high youth population but limited facilities:

"""
        
        if not young_population_opportunities.empty:
            for _, market in young_population_opportunities.iterrows():
                report += f"- **{market['msa_name']}**: {market['pct_under_18']:.1f}% under 18, {market['facilities_per_100k']:.1f} facilities per 100k\n"

        report += f"""
## Strategic Risks

### Overserved Markets
{len(overserved_markets)} markets identified as potentially overserved:

"""
        
        if not overserved_markets.empty:
            for _, market in overserved_markets.iterrows():
                report += f"- **{market['msa_name']}**: {market['facilities_per_100k']:.1f} facilities per 100k (High density)\n"

        report += f"""
## Recommendations

### 1. Expansion Opportunities
- **Priority 1**: Focus on high-income underserved markets for premium service offerings
- **Priority 2**: Target senior-heavy markets for specialized geriatric care
- **Priority 3**: Develop pediatric services in young population markets

### 2. Optimization Strategies
- **Consolidation**: Consider consolidating services in overserved markets
- **Specialization**: Differentiate services based on local demographics
- **Partnerships**: Explore partnerships in underserved areas

### 3. Service Mix Optimization
- **High-Income Markets**: Premium services, concierge care, specialized treatments
- **Senior Markets**: Geriatric care, chronic disease management, home health
- **Young Markets**: Pediatric care, family medicine, urgent care

### 4. Risk Mitigation
- **Market Exit**: Consider reducing presence in overserved markets
- **Service Diversification**: Offer unique services to differentiate from competitors
- **Efficiency Improvements**: Optimize operations in high-density markets

## Data Quality Notes
- {self.df['age_mix_category'].value_counts().get('Unknown', 0)} locations have incomplete age data
- Income data available for {len(self.df) - self.df['msa_median_household_income'].isna().sum()} locations
- Age demographic data available for {len(self.df) - self.df['pct_under_18'].isna().sum()} locations

---
*Report generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Save the report
        with open('ssm_health_comprehensive_analysis_report.md', 'w') as f:
            f.write(report)
        
        print("Comprehensive analysis report saved to ssm_health_comprehensive_analysis_report.md")
    
    def run_comprehensive_analysis(self):
        """Run the complete comprehensive analysis"""
        print("Starting comprehensive SSM Health facility analysis...")
        
        # Create all visualizations
        self.create_comprehensive_dashboard()
        self.create_income_age_analysis()
        self.create_strategic_recommendations()
        
        print("\n✅ Comprehensive analysis completed!")
        print("📊 Generated files:")
        print("  - ssm_health_comprehensive_dashboard.html")
        print("  - ssm_health_income_age_analysis.html")
        print("  - ssm_health_strategic_recommendations.html")
        print("  - ssm_health_comprehensive_analysis_report.md")

def main():
    """Main function to run comprehensive analysis"""
    print("SSM Health Comprehensive Facility Analysis")
    print("=" * 50)
    
    # Use the enriched data file
    input_file = 'ssm_health_locations_with_income_with_age_demographics.csv'
    
    try:
        # Initialize analyzer
        analyzer = ComprehensiveFacilityAnalyzer(input_file)
        
        # Run comprehensive analysis
        analyzer.run_comprehensive_analysis()
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise

if __name__ == "__main__":
    main() 