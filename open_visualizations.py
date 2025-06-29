#!/usr/bin/env python3
"""
Script to open the SSM Health facility analysis visualizations in a web browser.
"""

import webbrowser
import os
import time

def open_visualizations():
    """Open all generated visualizations in the default web browser"""
    
    visualizations = [
        {
            'name': 'Market Analysis Dashboard',
            'file': 'ssm_health_market_analysis.html',
            'description': 'Interactive dashboard showing market coverage analysis, facility density, and market status distribution'
        },
        {
            'name': 'Facility Type Analysis',
            'file': 'ssm_health_facility_types.html',
            'description': 'Analysis of facility types and specialties distribution'
        },
        {
            'name': 'Interactive Facility Map',
            'file': 'ssm_health_facilities_map.html',
            'description': 'Interactive map showing facility locations with color-coded facility types'
        }
    ]
    
    print("Opening SSM Health Facility Analysis Visualizations...")
    print("=" * 60)
    
    for viz in visualizations:
        if os.path.exists(viz['file']):
            print(f"\nOpening: {viz['name']}")
            print(f"Description: {viz['description']}")
            print(f"File: {viz['file']}")
            
            # Open in browser
            webbrowser.open(f'file://{os.path.abspath(viz["file"])}')
            
            # Small delay to prevent overwhelming the browser
            time.sleep(2)
        else:
            print(f"\nWarning: {viz['file']} not found!")
    
    print("\n" + "=" * 60)
    print("All visualizations opened!")
    print("\nAdditional files generated:")
    print("- ssm_health_analysis_report.md (Comprehensive analysis report)")
    print("- facility_analysis_visualization.py (Analysis script)")

if __name__ == "__main__":
    open_visualizations() 