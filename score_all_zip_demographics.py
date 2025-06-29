#!/usr/bin/env python3
"""
Score ALL ZIP Code Demographics with Healthcare Attractiveness Algorithm
Applies the same scoring method to the complete ZIP demographics dataset
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class AllZIPAttractivenessScorer:
    def __init__(self):
        """Initialize the attractiveness scorer"""
        self.weights = {
            'population_density': 0.25,      # 25% weight
            'population_growth': 0.20,       # 20% weight
            'senior_population': 0.25,       # 25% weight (65+)
            'income_level': 0.20,            # 20% weight
            'young_family': 0.10             # 10% weight (0-17)
        }
    
    def normalize_score(self, values, method='percentile'):
        """
        Normalize values to 0-100 scale
        method: 'percentile' or 'minmax'
        """
        if method == 'percentile':
            # Use percentile ranking (0-100)
            return values.rank(pct=True) * 100
        elif method == 'minmax':
            # Use min-max normalization
            min_val = values.min()
            max_val = values.max()
            if max_val == min_val:
                return pd.Series([50] * len(values), index=values.index)
            return ((values - min_val) / (max_val - min_val)) * 100
    
    def calculate_population_density_score(self, df):
        """Calculate attractiveness score based on population density"""
        # Higher density = higher score
        density_scores = self.normalize_score(df['population_density'])
        
        # Bonus for very high density areas (urban centers)
        density_scores = np.where(
            df['population_density'] > 1000,  # Very dense urban
            density_scores * 1.2,  # 20% bonus
            density_scores
        )
        
        return density_scores
    
    def calculate_growth_score(self, df):
        """Calculate attractiveness score based on population growth"""
        # Higher growth = higher score
        growth_scores = self.normalize_score(df['population_growth_rate'])
        
        # Bonus for very high growth areas
        growth_scores = np.where(
            df['population_growth_rate'] > 2.0,  # High growth
            growth_scores * 1.3,  # 30% bonus
            growth_scores
        )
        
        return growth_scores
    
    def calculate_senior_population_score(self, df):
        """Calculate attractiveness score based on senior population (65+)"""
        # Higher senior population = higher score (more healthcare needs)
        senior_pct = df['pct_age_65_74'] + df['pct_age_75_84'] + df['pct_age_85_plus']
        senior_scores = self.normalize_score(senior_pct)
        
        # Bonus for very high senior populations
        senior_scores = np.where(
            senior_pct > 20,  # High senior population
            senior_scores * 1.4,  # 40% bonus
            senior_scores
        )
        
        return senior_scores
    
    def calculate_income_score(self, df):
        """Calculate attractiveness score based on income levels"""
        # Moderate to high income = higher score (better payer mix)
        income_scores = self.normalize_score(df['median_household_income'])
        
        # Bonus for high-income areas (better commercial insurance)
        income_scores = np.where(
            df['median_household_income'] > 75000,  # High income
            income_scores * 1.2,  # 20% bonus
            income_scores
        )
        
        # Small bonus for moderate income (stable payer mix)
        income_scores = np.where(
            (df['median_household_income'] >= 50000) & 
            (df['median_household_income'] <= 75000),
            income_scores * 1.1,  # 10% bonus
            income_scores
        )
        
        return income_scores
    
    def calculate_young_family_score(self, df):
        """Calculate attractiveness score based on young family population (0-17)"""
        # Moderate young family population = higher score (pediatrics, OB-GYN)
        young_pct = df['pct_under_5'] + df['pct_age_5_17']
        young_scores = self.normalize_score(young_pct)
        
        # Bonus for moderate young family populations (not too high, not too low)
        young_scores = np.where(
            (young_pct >= 15) & (young_pct <= 25),  # Moderate young families
            young_scores * 1.3,  # 30% bonus
            young_scores
        )
        
        return young_scores
    
    def calculate_composite_score(self, df):
        """Calculate overall healthcare attractiveness score"""
        print("🏥 Calculating healthcare attractiveness scores for all ZIP codes...")
        
        # Calculate individual component scores
        density_score = self.calculate_population_density_score(df)
        growth_score = self.calculate_growth_score(df)
        senior_score = self.calculate_senior_population_score(df)
        income_score = self.calculate_income_score(df)
        young_family_score = self.calculate_young_family_score(df)
        
        # Calculate weighted composite score
        composite_score = (
            density_score * self.weights['population_density'] +
            growth_score * self.weights['population_growth'] +
            senior_score * self.weights['senior_population'] +
            income_score * self.weights['income_level'] +
            young_family_score * self.weights['young_family']
        )
        
        # Ensure scores are between 0-100
        composite_score = np.clip(composite_score, 0, 100)
        
        return composite_score
    
    def categorize_attractiveness(self, scores):
        """Categorize attractiveness scores into levels"""
        categories = []
        colors = []
        
        for score in scores:
            if score >= 80:
                categories.append('Very High')
                colors.append('#1f77b4')  # Dark blue
            elif score >= 60:
                categories.append('High')
                colors.append('#ff7f0e')  # Orange
            elif score >= 40:
                categories.append('Medium')
                colors.append('#2ca02c')  # Green
            elif score >= 20:
                categories.append('Low')
                colors.append('#d62728')  # Red
            else:
                categories.append('Very Low')
                colors.append('#9467bd')  # Purple
        
        return categories, colors
    
    def score_all_zip_demographics(self, input_file='all_ok_mo_zip_demographics.csv'):
        """Score all ZIP code demographics with attractiveness algorithm"""
        print("📊 Loading complete ZIP demographics data...")
        df = pd.read_csv(input_file)
        
        print(f"🏠 Processing {len(df)} ZIP codes...")
        
        # Calculate attractiveness scores
        df['attractiveness_score'] = self.calculate_composite_score(df)
        
        # Categorize scores
        categories, colors = self.categorize_attractiveness(df['attractiveness_score'])
        df['attractiveness_category'] = categories
        df['attractiveness_color'] = colors
        
        # Add component scores for transparency
        df['density_score'] = self.calculate_population_density_score(df)
        df['growth_score'] = self.calculate_growth_score(df)
        df['senior_score'] = self.calculate_senior_population_score(df)
        df['income_score'] = self.calculate_income_score(df)
        df['young_family_score'] = self.calculate_young_family_score(df)
        
        # Calculate senior population percentage
        df['senior_population_pct'] = (df['pct_age_65_74'] + 
                                     df['pct_age_75_84'] + 
                                     df['pct_age_85_plus'])
        
        # Calculate young family percentage
        df['young_family_pct'] = df['pct_under_5'] + df['pct_age_5_17']
        
        # Save the scored data
        output_file = 'all_ok_mo_zip_demographics_scored.csv'
        df.to_csv(output_file, index=False)
        
        print(f"✅ Scored data saved to {output_file}")
        
        # Print summary statistics
        print(f"\n📊 Scoring Summary:")
        print(f"  Total ZIP codes processed: {len(df)}")
        print(f"  Average attractiveness score: {df['attractiveness_score'].mean():.1f}")
        print(f"  Score range: {df['attractiveness_score'].min():.1f} - {df['attractiveness_score'].max():.1f}")
        
        # Category breakdown
        category_counts = df['attractiveness_category'].value_counts()
        print(f"\n🏷️ Attractiveness Categories:")
        for category, count in category_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  {category}: {count} ZIP codes ({percentage:.1f}%)")
        
        # Top 10 highest scoring ZIP codes
        top_zip_codes = df.nlargest(10, 'attractiveness_score')[['zip', 'attractiveness_score', 'attractiveness_category']]
        print(f"\n🏆 Top 10 Highest Scoring ZIP Codes:")
        for _, row in top_zip_codes.iterrows():
            print(f"  {row['zip']}: {row['attractiveness_score']:.1f} ({row['attractiveness_category']})")
        
        # Component score averages
        print(f"\n📈 Component Score Averages:")
        print(f"  Population Density: {df['density_score'].mean():.1f}")
        print(f"  Population Growth: {df['growth_score'].mean():.1f}")
        print(f"  Senior Population: {df['senior_score'].mean():.1f}")
        print(f"  Income Level: {df['income_score'].mean():.1f}")
        print(f"  Young Family: {df['young_family_score'].mean():.1f}")
        
        return df

def main():
    """Main function to score all ZIP demographics"""
    print("🏥 SSM Health ALL ZIP Code Attractiveness Scoring")
    print("=" * 55)
    
    scorer = AllZIPAttractivenessScorer()
    
    try:
        # Score all ZIP demographics
        scored_df = scorer.score_all_zip_demographics()
        
        print("\n🎉 ZIP attractiveness scoring completed!")
        print("📊 Output includes:")
        print("  - Overall attractiveness scores (0-100)")
        print("  - Attractiveness categories (Very Low to Very High)")
        print("  - Component scores for each factor")
        print("  - Color coding for mapping")
        print("  - All 3,048 ZIP codes in MN, WI, IL")
        
        print(f"\n💡 Next steps:")
        print(f"  - Use 'all_mn_wi_il_zip_demographics_scored.csv' for mapping")
        print(f"  - Join with GeoJSON for ZIP polygon visualization")
        print(f"  - Overlay SSM facility locations")
        
    except Exception as e:
        print(f"❌ Error during scoring: {e}")
        raise

if __name__ == "__main__":
    main() 