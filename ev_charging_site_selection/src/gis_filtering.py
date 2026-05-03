import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import os

CITY_BOUNDS = Polygon([
    (77.45, 12.85), (77.75, 12.85),
    (77.75, 13.15), (77.45, 13.15)
])

ROAD_CORRIDORS = [
    Point(77.50, 12.90), Point(77.55, 12.95),
    Point(77.60, 13.00), Point(77.65, 13.05),
    Point(77.70, 13.10), Point(77.58, 12.92),
    Point(77.62, 13.02),
]

SENSITIVE_ZONES = [
    Point(77.52, 12.88).buffer(0.02),
    Point(77.68, 13.08).buffer(0.015),
]


def load_real_candidate_sites():
    """Load real Bangalore locations from CSV if available, otherwise generate synthetic sites"""
    real_sites_path = "data/raw/real_candidate_sites.csv"
    
    if os.path.exists(real_sites_path):
        print(f"[GIS] Loading real candidate sites from {real_sites_path}")
        df = pd.read_csv(real_sites_path)
        geometries = [Point(lon, lat) for lon, lat in zip(df['longitude'], df['latitude'])]
        
        gdf = gpd.GeoDataFrame({
            "site_id": df['site_name'],
            "site_type": df['site_type'],
            "geometry": geometries,
        }, crs="EPSG:4326")
        
        # Add random attributes for scoring (will be replaced by real data enrichment)
        rng = np.random.default_rng(42)
        n = len(gdf)
        gdf["population_density"] = rng.uniform(1000, 15000, n)
        gdf["land_cost"] = rng.uniform(0.2, 1.0, n)
        gdf["traffic_volume"] = rng.uniform(500, 10000, n)
        gdf["grid_access"] = rng.uniform(0.3, 1.0, n)
        gdf["commercial_proximity"] = rng.uniform(0.1, 1.0, n)
        
        print(f"[GIS] Loaded {len(gdf)} real candidate sites")
        return gdf
    else:
        print(f"[GIS] Real sites file not found, generating synthetic sites")
        return generate_candidate_sites()


def generate_candidate_sites(n=100, seed=42):
    """Generate synthetic candidate sites (fallback method)"""
    rng = np.random.default_rng(seed)
    lons = rng.uniform(77.46, 77.74, n)
    lats = rng.uniform(12.86, 13.14, n)
    geometries = [Point(lon, lat) for lon, lat in zip(lons, lats)]

    gdf = gpd.GeoDataFrame({
        "site_id": [f"S{i:03d}" for i in range(n)],
        "geometry": geometries,
        "population_density": rng.uniform(1000, 15000, n),
        "land_cost":          rng.uniform(0.2, 1.0, n),
        "traffic_volume":     rng.uniform(500, 10000, n),
        "grid_access":        rng.uniform(0.3, 1.0, n),
        "commercial_proximity": rng.uniform(0.1, 1.0, n),
    }, crs="EPSG:4326")
    return gdf


def filter_within_city(gdf):
    return gdf[gdf.geometry.within(CITY_BOUNDS)].copy()


def filter_near_roads(gdf, radius=0.03):
    road_union = gpd.GeoSeries(
        [p.buffer(radius) for p in ROAD_CORRIDORS], crs="EPSG:4326"
    ).union_all()
    return gdf[gdf.geometry.within(road_union)].copy()


def filter_out_sensitive_zones(gdf):
    from shapely.ops import unary_union
    sensitive_union = unary_union(SENSITIVE_ZONES)
    return gdf[~gdf.geometry.within(sensitive_union)].copy()


def run_gis_filtering(n_sites=100):
    gdf = load_real_candidate_sites()  # Try loading real sites first
    gdf = filter_within_city(gdf)
    gdf = filter_near_roads(gdf)
    gdf = filter_out_sensitive_zones(gdf)
    gdf = gdf.reset_index(drop=True)
    print(f"[GIS] {len(gdf)} candidate sites passed spatial filters.")
    return gdf
