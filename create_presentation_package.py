#!/usr/bin/env python3
"""
Script to create a presentation package with all visualizations and an index page.
"""

import os
import shutil
from datetime import datetime

def create_presentation_package():
    """Create a presentation package with all files and an index page"""
    
    # Create presentation directory
    presentation_dir = "SSM_Health_Presentation"
    if os.path.exists(presentation_dir):
        shutil.rmtree(presentation_dir)
    os.makedirs(presentation_dir)
    
    # Files to copy
    files_to_copy = [
        'ssm_health_market_analysis.html',
        'ssm_health_facility_types.html', 
        'ssm_health_facilities_map.html',
        'ssm_health_analysis_report.md'
    ]
    
    # Copy files
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, presentation_dir)
            print(f"✓ Copied {file}")
        else:
            print(f"✗ {file} not found")
    
    # Create index page
    index_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSM Health Facility Distribution Analysis</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }}
        .card:hover {{
            transform: translateY(-5px);
        }}
        .card h3 {{
            color: #333;
            margin-top: 0;
        }}
        .card p {{
            color: #666;
            line-height: 1.6;
        }}
        .btn {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
            transition: background 0.2s;
        }}
        .btn:hover {{
            background: #5a6fd8;
        }}
        .summary {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .summary h2 {{
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .key-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .metric {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .metric-number {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 SSM Health Facility Distribution Analysis</h1>
        <p>Strategic Market Analysis for Facility Optimization</p>
        <p><em>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</em></p>
    </div>

    <div class="summary">
        <h2>📊 Executive Summary</h2>
        <p>This analysis examines SSM Health's facility distribution across multiple markets to identify optimization opportunities for consolidation and expansion.</p>
        
        <div class="key-metrics">
            <div class="metric">
                <div class="metric-number">1,412</div>
                <div class="metric-label">Facilities Analyzed</div>
            </div>
            <div class="metric">
                <div class="metric-number">102</div>
                <div class="metric-label">Markets Analyzed</div>
            </div>
            <div class="metric">
                <div class="metric-number">17</div>
                <div class="metric-label">Overserved Markets</div>
            </div>
            <div class="metric">
                <div class="metric-number">30</div>
                <div class="metric-label">Underserved Markets</div>
            </div>
            <div class="metric">
                <div class="metric-number">$116.5M</div>
                <div class="metric-label">Potential Annual Savings</div>
            </div>
            <div class="metric">
                <div class="metric-number">$101.6M</div>
                <div class="metric-label">Revenue Opportunity</div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="card">
            <h3>📈 Market Analysis Dashboard</h3>
            <p>Interactive dashboard showing market coverage analysis, facility density by MSA, market status distribution, and facility count vs population relationships.</p>
            <a href="ssm_health_market_analysis.html" class="btn" target="_blank">Open Dashboard</a>
        </div>

        <div class="card">
            <h3>🏥 Facility Type Analysis</h3>
            <p>Analysis of facility types and specialties distribution, showing the breakdown of different service categories across the health system.</p>
            <a href="ssm_health_facility_types.html" class="btn" target="_blank">View Analysis</a>
        </div>

        <div class="card">
            <h3>🗺️ Interactive Facility Map</h3>
            <p>Geographic visualization of all facilities with color-coded facility types. Click on markers for detailed information about each location.</p>
            <a href="ssm_health_facilities_map.html" class="btn" target="_blank">Open Map</a>
        </div>

        <div class="card">
            <h3>📋 Detailed Analysis Report</h3>
            <p>Comprehensive written report with strategic recommendations, financial impact assessment, and detailed market-by-market analysis.</p>
            <a href="ssm_health_analysis_report.md" class="btn" target="_blank">Read Report</a>
        </div>
    </div>

    <div class="summary">
        <h2>🎯 Key Recommendations</h2>
        <ul>
            <li><strong>Consolidation Opportunities:</strong> Focus on 17 overserved markets with potential for $116.5M annual savings</li>
            <li><strong>Expansion Opportunities:</strong> Target 30 underserved markets representing $101.6M revenue potential</li>
            <li><strong>Priority Markets:</strong> Fond du Lac (WI), Oklahoma City (OK), and St. Louis (MO-IL) areas</li>
            <li><strong>Next Steps:</strong> Conduct detailed facility-level analysis and competitive research</li>
        </ul>
    </div>

    <div style="text-align: center; margin-top: 40px; color: #666;">
        <p><strong>Instructions:</strong> Click any button above to open the interactive visualizations. All files are self-contained and work offline.</p>
        <p><em>For best experience, use Chrome, Firefox, or Edge browser</em></p>
    </div>
</body>
</html>
"""
    
    # Write index file
    with open(os.path.join(presentation_dir, 'index.html'), 'w') as f:
        f.write(index_html)
    
    print(f"\n✓ Created presentation package in '{presentation_dir}' folder")
    print(f"✓ Added index.html with navigation")
    
    # Create README
    readme_content = """# SSM Health Facility Analysis - Presentation Package

## 📁 Contents
- `index.html` - Main navigation page (start here!)
- `ssm_health_market_analysis.html` - Interactive market analysis dashboard
- `ssm_health_facility_types.html` - Facility type and specialty analysis
- `ssm_health_facilities_map.html` - Interactive geographic map
- `ssm_health_analysis_report.md` - Detailed written report

## 🚀 How to Use
1. Double-click `index.html` to open the main page
2. Click any button to open the interactive visualizations
3. All files work offline - no internet connection required
4. Use any modern web browser (Chrome, Firefox, Edge recommended)

## 📊 Key Findings
- 1,412 facilities analyzed across 102 markets
- 17 overserved markets identified for consolidation
- 30 underserved markets identified for expansion
- $116.5M potential annual savings from consolidation
- $101.6M potential revenue from underserved markets

## 🎯 Strategic Recommendations
- Focus consolidation efforts on Fond du Lac, Oklahoma City, and St. Louis areas
- Target expansion in underserved markets with high population density
- Implement pilot programs in selected markets
- Monitor performance metrics post-implementation

For questions or additional analysis, contact the analytics team.
"""
    
    with open(os.path.join(presentation_dir, 'README.txt'), 'w') as f:
        f.write(readme_content)
    
    print(f"✓ Added README.txt with instructions")
    print(f"\n🎉 Presentation package ready!")
    print(f"📂 Copy the '{presentation_dir}' folder to your presentation device")
    print(f"🌐 Open 'index.html' to start the presentation")

if __name__ == "__main__":
    create_presentation_package() 