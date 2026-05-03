"""
Competition Analysis Module
Analyzes competition from existing EV charging stations
"""

import numpy as np
import pandas as pd
from src.api_integrations import fetch_open_charge_map_stations


def analyze_competition(sites_gdf, bbox, existing_stations=None):
    """
    Analyze competition from existing EV charging stations
    
    Args:
        sites_gdf: GeoDataFrame of candidate sites
        bbox: Bounding box dict with 'north', 'south', 'east', 'west'
        existing_stations: Pre-fetched GeoDataFrame of stations (avoids double API call)
    
    Returns:
        GeoDataFrame with competition scores added
    """
    print("\n[Competition] Analyzing existing EV stations...")
    
    # Use pre-fetched stations or fetch now
    if existing_stations is not None:
        existing = existing_stations
    else:
        existing = fetch_open_charge_map_stations(bbox)
    
    if existing is None or len(existing) == 0:
        print("[Competition] ⚠ No existing stations found, using default scores")
        sites_gdf['competition_score'] = 1.0
        sites_gdf['nearest_competitor_km'] = 999.0
        sites_gdf['competitor_name'] = 'None'
        return sites_gdf
    
    print(f"[Competition] ✓ Found {len(existing)} existing EV stations")
    print(f"[Competition]   Total charging points: {existing['num_points'].sum()}")
    
    # Calculate competition metrics for each candidate site
    competition_scores = []
    nearest_distances = []
    competitor_names = []
    
    for idx, site in sites_gdf.iterrows():
        # Calculate distances to all existing stations
        distances = existing.geometry.distance(site.geometry) * 111  # degrees to km
        
        # Find nearest competitor
        min_idx = distances.idxmin()
        min_distance = distances.min()
        nearest_name = existing.loc[min_idx, 'name']
        
        # Competition score calculation:
        # - 0 km = 0.0 (very high competition)
        # - 2 km = 0.4 (high competition)
        # - 5 km = 1.0 (low competition)
        # - 10+ km = 1.0 (no competition)
        
        if min_distance < 0.5:
            score = 0.0  # Too close, very high competition
        elif min_distance < 2.0:
            score = min_distance / 5.0  # Linear scaling
        elif min_distance < 5.0:
            score = 0.4 + (min_distance - 2.0) / 5.0  # Gradual improvement
        else:
            score = 1.0  # Good distance, low competition
        
        competition_scores.append(score)
        nearest_distances.append(min_distance)
        competitor_names.append(nearest_name)
    
    # Add to GeoDataFrame
    sites_gdf['competition_score'] = competition_scores
    sites_gdf['nearest_competitor_km'] = nearest_distances
    sites_gdf['competitor_name'] = competitor_names
    
    # Print statistics
    avg_distance = np.mean(nearest_distances)
    avg_score = np.mean(competition_scores)
    
    print(f"[Competition] ✓ Analysis complete")
    print(f"[Competition]   Average distance to competitor: {avg_distance:.2f} km")
    print(f"[Competition]   Average competition score: {avg_score:.3f}")
    print(f"[Competition]   Sites with low competition (>5km): {sum(d > 5 for d in nearest_distances)}")
    print(f"[Competition]   Sites with high competition (<2km): {sum(d < 2 for d in nearest_distances)}")
    
    return sites_gdf


def get_underserved_areas(sites_gdf, threshold_km=5.0):
    """
    Identify underserved areas (far from existing stations)
    
    Args:
        sites_gdf: GeoDataFrame with competition analysis
        threshold_km: Distance threshold for underserved areas
    
    Returns:
        GeoDataFrame of underserved sites
    """
    underserved = sites_gdf[sites_gdf['nearest_competitor_km'] > threshold_km].copy()
    
    print(f"\n[Underserved] Found {len(underserved)} sites in underserved areas (>{threshold_km}km from competitors)")
    
    if len(underserved) > 0:
        print(f"[Underserved] Top 5 most underserved sites:")
        top_underserved = underserved.nlargest(5, 'nearest_competitor_km')
        for idx, site in top_underserved.iterrows():
            print(f"  • {site['site_id']}: {site['nearest_competitor_km']:.2f} km from nearest competitor")
    
    return underserved


def save_competition_report(sites_gdf, output_path="outputs/competition_report.csv"):
    """
    Save detailed competition analysis report
    
    Args:
        sites_gdf: GeoDataFrame with competition analysis
        output_path: Output CSV path
    """
    report_cols = [
        'site_id', 
        'competition_score', 
        'nearest_competitor_km', 
        'competitor_name',
        'ahp_score',
        'predicted_demand',
        'final_score',
        'final_rank'
    ]
    
    # Check which columns exist
    available_cols = [col for col in report_cols if col in sites_gdf.columns]
    
    report = sites_gdf[available_cols].copy()
    report = report.sort_values('competition_score', ascending=False)
    
    report.to_csv(output_path, index=False)
    print(f"\n[Competition] ✓ Report saved to {output_path}")
    
    return report


if __name__ == "__main__":
    # Test the module
    import geopandas as gpd
    from shapely.geometry import Point
    
    # Create sample sites
    np.random.seed(42)
    n_sites = 10
    
    lats = np.random.uniform(12.85, 13.15, n_sites)
    lons = np.random.uniform(77.45, 77.75, n_sites)
    
    sites = gpd.GeoDataFrame({
        'site_id': [f'S{i:03d}' for i in range(1, n_sites+1)],
        'geometry': [Point(lon, lat) for lon, lat in zip(lons, lats)]
    }, crs='EPSG:4326')
    
    bbox = {
        "north": 13.15,
        "south": 12.85,
        "east": 77.75,
        "west": 77.45,
    }
    
    # Run analysis
    sites = analyze_competition(sites, bbox)
    underserved = get_underserved_areas(sites)
    
    print("\n" + "="*70)
    print("Competition Analysis Results:")
    print("="*70)
    print(sites[['site_id', 'competition_score', 'nearest_competitor_km', 'competitor_name']].to_string(index=False))
