#!/usr/bin/env python3
"""
Fixed SSM Health Market Analysis - Corrected Facilities per 100k Calculation
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def create_fixed_market_analysis(csv_file):
    """Create market analysis with correct facilities per 100k calculation"""
    
    # Load data
    df = pd.read_csv(csv_file)
    df = df.dropna(subset=['name', 'city', 'state', 'msa_name', 'msa_population'])
    
    # Clean MSA names
    df['msa_name_clean'] = df['msa_name'].apply(clean_msa_name)
    
    print(f"Processing {len(df)} facilities across {df['msa_name_clean'].nunique()} MSAs")
    
    # CORRECT calculation: Count facilities per MSA and divide by population
    msa_facility_counts = df.groupby('msa_name_clean').size().reset_index(name='facility_count')
    msa_populations = df.groupby('msa_name_clean')['msa_population'].first().reset_index()
    
    # Merge facility counts with populations
    msa_analysis = msa_facility_counts.merge(msa_populations, on='msa_name_clean')
    
    # Calculate correct facilities per 100k
    msa_analysis['facilities_per_100k'] = (msa_analysis['facility_count'] / msa_analysis['msa_population']) * 100000
    
    # Add other MSA-level data
    msa_income = df.groupby('msa_name_clean')['msa_median_household_income'].first().reset_index()
    msa_age = df.groupby('msa_name_clean')['median_age'].first().reset_index()
    msa_demographics = df.groupby('msa_name_clean').agg({
        'pct_under_18': 'first',
        'pct_18_34': 'first', 
        'pct_35_54': 'first',
        'pct_55_64': 'first',
        'pct_65_plus': 'first'
    }).reset_index()
    
    # Merge all MSA data
    msa_analysis = msa_analysis.merge(msa_income, on='msa_name_clean')
    msa_analysis = msa_analysis.merge(msa_age, on='msa_name_clean')
    msa_analysis = msa_analysis.merge(msa_demographics, on='msa_name_clean')
    
    # Categorize market status
    def categorize_market(facilities_per_100k):
        if pd.isna(facilities_per_100k):
            return 'Unknown'
        elif facilities_per_100k > 50:
            return 'Overserved'
        elif facilities_per_100k < 20:
            return 'Underserved'
        else:
            return 'Adequately Served'
    
    msa_analysis['market_status'] = msa_analysis['facilities_per_100k'].apply(categorize_market)
    
    # Create income categories
    msa_analysis['income_category'] = pd.cut(
        msa_analysis['msa_median_household_income'],
        bins=[0, 50000, 70000, 90000, float('inf')],
        labels=['Low Income', 'Lower Middle', 'Upper Middle', 'High Income']
    )
    
    print(f"Analysis complete. Top 5 MSAs by facility density:")
    top_msas = msa_analysis.nlargest(5, 'facilities_per_100k')
    for _, row in top_msas.iterrows():
        print(f"  {row['msa_name_clean']}: {row['facilities_per_100k']:.1f} facilities per 100k")
    
    # Create the dashboard
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Facilities per 100k Population by MSA (Fixed)',
            'Market Status Distribution',
            'Income vs Facility Density',
            'Age Demographics by MSA',
            'Facility Distribution by Income Level',
            'Population vs Facility Count'
        ),
        specs=[
            [{"type": "bar"}, {"type": "pie"}],
            [{"type": "scatter"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "scatter"}]
        ]
    )
    
    # Chart 1: Facilities per 100k by MSA (FIXED)
    top_15_msas = msa_analysis.nlargest(15, 'facilities_per_100k')
    
    fig.add_trace(
        go.Bar(
            x=top_15_msas['facilities_per_100k'],
            y=top_15_msas['msa_name_clean'],
            orientation='h',
            name='Facilities per 100k',
            marker_color='lightblue',
            text=[f"{val:.1f}" for val in top_15_msas['facilities_per_100k']],
            textposition='auto'
        ),
        row=1, col=1
    )
    
    # Chart 2: Market Status Distribution
    market_status_counts = msa_analysis['market_status'].value_counts()
    
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
            x=msa_analysis['msa_median_household_income'],
            y=msa_analysis['facilities_per_100k'],
            mode='markers',
            marker=dict(
                size=8,
                color=msa_analysis['median_age'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Median Age")
            ),
            text=msa_analysis['msa_name_clean'],
            name='Income vs Density'
        ),
        row=2, col=1
    )
    
    # Chart 4: Age Demographics by MSA
    top_10_senior = msa_analysis.nlargest(10, 'pct_65_plus')
    
    fig.add_trace(
        go.Bar(
            x=top_10_senior['msa_name_clean'],
            y=top_10_senior['pct_under_18'],
            name='Under 18',
            marker_color='lightgreen'
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=top_10_senior['msa_name_clean'],
            y=top_10_senior['pct_18_34'],
            name='18-34',
            marker_color='lightblue'
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=top_10_senior['msa_name_clean'],
            y=top_10_senior['pct_35_54'],
            name='35-54',
            marker_color='orange'
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=top_10_senior['msa_name_clean'],
            y=top_10_senior['pct_55_64'],
            name='55-64',
            marker_color='red'
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=top_10_senior['msa_name_clean'],
            y=top_10_senior['pct_65_plus'],
            name='65+',
            marker_color='purple'
        ),
        row=2, col=2
    )
    
    # Chart 5: Facility Distribution by Income Level
    income_facility_counts = msa_analysis.groupby('income_category')['facility_count'].sum()
    
    fig.add_trace(
        go.Bar(
            x=income_facility_counts.index,
            y=income_facility_counts.values,
            name='Facilities by Income',
            marker_color='green'
        ),
        row=3, col=1
    )
    
    # Chart 6: Population vs Facility Count
    fig.add_trace(
        go.Scatter(
            x=msa_analysis['msa_population'],
            y=msa_analysis['facility_count'],
            mode='markers',
            marker=dict(
                size=8,
                color=msa_analysis['facilities_per_100k'],
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Facilities per 100k")
            ),
            text=msa_analysis['msa_name_clean'],
            name='Population vs Facilities'
        ),
        row=3, col=2
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'SSM Health Market Analysis Dashboard (Fixed)<br><sub>Corrected Facilities per 100k Calculation</sub>',
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
    fig.update_xaxes(title_text="MSA Population", row=3, col=2)
    fig.update_yaxes(title_text="Number of Facilities", row=3, col=2)
    
    # Save the dashboard
    output_file = 'ssm_health_fixed_market_analysis.html'
    fig.write_html(output_file)
    print(f"Fixed market analysis dashboard saved to: {output_file}")
    
    return fig, msa_analysis

if __name__ == "__main__":
    # Use the file with income and age demographics
    csv_file = "ssm_health_locations_with_income_with_age_demographics.csv"
    fig, analysis = create_fixed_market_analysis(csv_file) 