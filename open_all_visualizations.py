#!/usr/bin/env python3
"""
Script to open all SSM Health visualizations in the default web browser.
"""

import webbrowser
import os
import time

def open_visualizations():
    """Open all generated visualizations in the default web browser"""
    
    visualizations = [
        {
            'name': 'Interactive Facility Map',
            'file': 'ssm_health_interactive_facility_map.html',
            'description': 'Main interactive map showing all facilities with detailed popups, facility types, and demographic data'
        },
        {
            'name': 'MSA Density Heatmap',
            'file': 'ssm_health_msa_density_heatmap.html',
            'description': 'Heatmap showing facility density by MSA with market saturation analysis'
        },
        {
            'name': 'Strategic Opportunities Map',
            'file': 'ssm_health_strategic_opportunities_map.html',
            'description': 'Map highlighting expansion opportunities and market risks'
        },
        {
            'name': 'Market Analysis Dashboard',
            'file': 'ssm_health_market_analysis.html',
            'description': 'Comprehensive dashboard with market coverage analysis and facility distribution'
        },
        {
            'name': 'Facility Type Analysis',
            'file': 'ssm_health_facility_types.html',
            'description': 'Analysis of facility types and specialties distribution'
        },
        {
            'name': 'Comprehensive Dashboard',
            'file': 'ssm_health_comprehensive_dashboard.html',
            'description': 'Enhanced dashboard with income and age demographic data'
        },
        {
            'name': 'Income & Age Analysis',
            'file': 'ssm_health_income_age_analysis.html',
            'description': 'Detailed analysis of income and age demographics by market'
        },
        {
            'name': 'Strategic Recommendations',
            'file': 'ssm_health_strategic_recommendations.html',
            'description': 'Strategic recommendations based on market analysis'
        }
    ]
    
    print("🗺️ SSM Health Facility Visualization Suite")
    print("=" * 50)
    print("Opening all visualizations in your default web browser...")
    print()
    
    opened_count = 0
    
    for viz in visualizations:
        if os.path.exists(viz['file']):
            try:
                # Get absolute path
                abs_path = os.path.abspath(viz['file'])
                file_url = f"file://{abs_path}"
                
                print(f"📊 Opening: {viz['name']}")
                print(f"   📁 File: {viz['file']}")
                print(f"   📝 {viz['description']}")
                
                # Open in browser
                webbrowser.open(file_url)
                opened_count += 1
                
                # Small delay to prevent overwhelming the browser
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error opening {viz['name']}: {e}")
        else:
            print(f"⚠️  File not found: {viz['file']}")
    
    print()
    print(f"✅ Successfully opened {opened_count} visualizations!")
    print()
    print("📋 Available Analysis Files:")
    print("   📄 ssm_health_mapping_summary.md - Mapping analysis summary")
    print("   📄 ssm_health_comprehensive_analysis_report.md - Comprehensive analysis report")
    print("   📄 ssm_health_analysis_report.md - Original analysis report")
    print()
    print("💡 Tips:")
    print("   • Use the layer controls in the maps to filter by facility type or market status")
    print("   • Click on facility markers for detailed information")
    print("   • Use the search functionality to find specific facilities")
    print("   • The heatmap shows facility density - red areas are overserved, green are underserved")
    print("   • Strategic maps highlight expansion opportunities and risks")

if __name__ == "__main__":
    open_visualizations() 