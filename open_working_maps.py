#!/usr/bin/env python3
"""
Script to open all working SSM Health facility maps.
"""

import webbrowser
import os
import time

def open_working_maps():
    """Open all working facility maps"""
    
    maps = [
        {
            'name': 'Fixed Facility Map (Recommended)',
            'file': 'ssm_health_fixed_facility_map.html',
            'description': 'Complete interactive map with all facilities, layer controls, and scrollable legend'
        },
        {
            'name': 'Debug Facility Map',
            'file': 'ssm_health_debug_map.html',
            'description': 'Simple map with all facilities visible by default'
        },
        {
            'name': 'MSA Density Heatmap',
            'file': 'ssm_health_msa_density_heatmap.html',
            'description': 'Heatmap showing facility density by MSA'
        },
        {
            'name': 'Strategic Opportunities Map',
            'file': 'ssm_health_strategic_opportunities_map.html',
            'description': 'Map highlighting expansion opportunities and market risks'
        }
    ]
    
    print("🗺️ SSM Health Working Facility Maps")
    print("=" * 50)
    print("Opening all working maps in your default web browser...")
    print()
    
    opened_count = 0
    
    for map_info in maps:
        if os.path.exists(map_info['file']):
            try:
                # Get absolute path
                abs_path = os.path.abspath(map_info['file'])
                file_url = f"file://{abs_path}"
                
                print(f"📊 Opening: {map_info['name']}")
                print(f"   📁 File: {map_info['file']}")
                print(f"   📝 {map_info['description']}")
                
                # Open in browser
                webbrowser.open(file_url)
                opened_count += 1
                
                # Small delay to prevent overwhelming the browser
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error opening {map_info['name']}: {e}")
        else:
            print(f"⚠️  File not found: {map_info['file']}")
    
    print()
    print(f"✅ Successfully opened {opened_count} maps!")
    print()
    print("💡 Tips for using the maps:")
    print("   • The Fixed Facility Map has layer controls in the top right")
    print("   • Click on any marker for detailed facility information")
    print("   • Use the legend to understand facility type colors")
    print("   • The Debug Map shows all facilities without filtering")
    print("   • The Heatmap shows facility density (red = high density)")
    print("   • The Strategic Map highlights expansion opportunities")

if __name__ == "__main__":
    open_working_maps() 