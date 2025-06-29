#!/usr/bin/env python3
"""
Corrected SSM Health Comprehensive Facility Analysis - Clean MSA Names
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

def clean_msa_name(msa_name):
    """Clean MSA names by removing statistical area suffixes"""
    if pd.isna(msa_name):
        return msa_name
    
    # Remove common suffixes
    suffixes_to_remove = [
        ' Metropolitan Statistical Area',
        ' Micropolitan Statistical Area',
        ' MSA',
        ' MicroSA'
    ]
    
    cleaned_name = msa_name
    for suffix in suffixes_to_remove:
        if cleaned_name.endswith(suffix):
            cleaned_name = cleaned_name.replace(suffix, '')
            break
    
    return cleaned_name

class CorrectedComprehensiveFacilityAnalyzer:
    def __init__(self, csv_file):
        """Initialize the analyzer with the facility data including income and age demographics"""
        self.df = pd.read_csv(csv_file)
        self.geolocator = Nominatim(user_agent="ssm_health_analyzer")
        self.process_data()
    
    def process_data(self):
        """Clean and process the facility data"""
        print("Processing facility data...")
        
        # Clean data
        self.df = self.df.dropna(subset=['name', 'city', 'state'])
        
        # Remove 99999 MSA entries
        self.df = self.df[self.df['msa_code'] != '99999']
        
        # Fill missing values
        self.df['type'] = self.df['type'].fillna('Unknown')
        self.df['specialty'] = self.df['specialty'].fillna('General')
        
        # Clean MSA names
        self.df['msa_name_clean'] = self.df['msa_name'].apply(clean_msa_name)
        
        # Create facility categories
        self.df['facility_category'] = self.df['type'].apply(self.categorize_facility)
        
        # Calculate facilities per 100k population (original method)
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
        
        # Create age mix category
        def create_age_mix_category(row):
            if row['pct_65_plus'] > 20:
                return 'Senior-Heavy'
            elif row['pct_under_18'] > 25:
                return 'Youth-Heavy'
            elif row['pct_18_34'] > 25:
                return 'Young Adult-Heavy'
            else:
                return 'Balanced'
        
        self.df['age_mix_category'] = self.df.apply(create_age_mix_category, axis=1)
        
        print(f"Processed {len(self.df)} facilities across {self.df['msa_name_clean'].nunique()} MSAs")
    
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
        print("Creating polished comprehensive dashboard...")
        
        # Create subplots - 2x2 layout
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Facilities per 100k Population by MSA',
                'Market Status Distribution',
                'Income vs Facility Density',
                'Age Mix Categories Distribution'
            ),
            specs=[
                [{"type": "bar"}, {"type": "pie"}],
                [{"type": "scatter"}, {"type": "pie"}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.08
        )
        
        # Chart 1: Facilities per 100k by MSA
        msa_summary = self.df.groupby(['msa_name_clean', 'msa_code']).agg({
            'facilities_per_100k': 'first',
            'msa_median_household_income': 'first',
            'median_age': 'first'
        }).reset_index()
        
        msa_summary = msa_summary.sort_values('facilities_per_100k', ascending=True).tail(15)
        
        fig.add_trace(
            go.Bar(
                x=msa_summary['facilities_per_100k'],
                y=msa_summary['msa_name_clean'],
                orientation='h',
                name='Facilities per 100k',
                marker_color='#1f77b4',
                hovertemplate='<b>%{y}</b><br>Facilities per 100k: %{x:.2f}<extra></extra>'
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
                marker_colors=['#ff7f0e', '#2ca02c', '#d62728'],
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent:.1%}<extra></extra>'
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
                    size=10,
                    color=self.df['median_age'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Median Age", x=0.45)
                ),
                text=self.df['msa_name_clean'],
                hovertemplate='<b>%{text}</b><br>Income: $%{x:,.0f}<br>Facilities per 100k: %{y:.2f}<br>Median Age: %{marker.color:.0f}<extra></extra>',
                name='Income vs Density'
            ),
            row=2, col=1
        )
        
        # Chart 4: Age Mix Categories Distribution
        age_mix_counts = self.df['age_mix_category'].value_counts()
        
        fig.add_trace(
            go.Pie(
                labels=age_mix_counts.index,
                values=age_mix_counts.values,
                name='Age Mix Categories',
                marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent:.1%}<extra></extra>'
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'SSM Health Market Analysis Dashboard<br><sub>Facility Distribution, Market Status, and Demographic Insights</sub>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': '#2c3e50'}
            },
            height=900,
            showlegend=True,
            template='plotly_white',
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(t=100, b=50, l=50, r=50)
        )
        
        # Update axes labels and formatting
        fig.update_xaxes(
            title_text="Facilities per 100k Population", 
            row=1, col=1,
            showgrid=True,
            gridcolor='#f0f0f0',
            gridwidth=1
        )
        
        fig.update_xaxes(
            title_text="Median Household Income ($)", 
            row=2, col=1,
            showgrid=True,
            gridcolor='#f0f0f0',
            gridwidth=1,
            tickformat=','
        )
        
        fig.update_yaxes(
            title_text="Facilities per 100k Population", 
            row=2, col=1,
            showgrid=True,
            gridcolor='#f0f0f0',
            gridwidth=1
        )
        
        # Improve formatting for facilities per 100k chart
        fig.update_xaxes(
            row=1, col=1,
            showgrid=True,
            gridcolor='#f0f0f0',
            gridwidth=1
        )
        
        fig.update_yaxes(
            row=1, col=1,
            showgrid=False
        )
        
        # Save the dashboard
        fig.write_html('ssm_health_market_analysis_polished.html')
        print("Polished comprehensive dashboard saved to ssm_health_market_analysis_polished.html")
        
        return fig

def main():
    """Main function to run the corrected comprehensive analysis"""
    csv_file = "ssm_health_locations_with_income_with_age_demographics.csv"
    
    analyzer = CorrectedComprehensiveFacilityAnalyzer(csv_file)
    fig = analyzer.create_comprehensive_dashboard()
    
    print("✅ Corrected comprehensive analysis complete!")
    print("📊 Dashboard saved with clean MSA names")

if __name__ == "__main__":
    main() 