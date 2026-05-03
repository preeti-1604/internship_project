"""
Real-world data loader for EV Charging Site Selection.

Data sources used:
  - OpenStreetMap (via OSMnx)  : roads, power lines, substations, commercial POIs
  - WorldPop / Census CSV      : population density  (place data/raw/population.csv)
  - Manual / data.gov.in CSV   : land cost by zone   (place data/raw/land_cost.csv)

CSV formats expected
--------------------
data/raw/population.csv
    columns: latitude, longitude, population_density
    one row per census ward / grid cell

data/raw/land_cost.csv
    columns: latitude, longitude, land_cost_normalized   (0.0 – 1.0)
    one row per zone / locality centroid

If these files are absent the loader falls back to OSM-derived proxies.
"""

import os
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import unary_union

warnings.filterwarnings("ignore")

# ── City configuration ────────────────────────────────────────────────────────
CITY_NAME   = "Bengaluru, Karnataka, India"
CITY_BOUNDS = {
    "north": 13.15, "south": 12.85,
    "east":  77.75, "west":  77.45,
}

POPULATION_CSV = "data/raw/population.csv"
LAND_COST_CSV  = "data/raw/land_cost.csv"


# ── OSM fetchers ──────────────────────────────────────────────────────────────

def _bbox_tuple(bbox):
    """OSMnx v2 expects (left, bottom, right, top) = (west, south, east, north)."""
    return (bbox["west"], bbox["south"], bbox["east"], bbox["north"])


def _fetch_roads(bbox):
    """Return a GeoDataFrame of major road geometries."""
    try:
        import osmnx as ox
        print("[Data] Fetching road network from OSM …")
        G = ox.graph_from_bbox(_bbox_tuple(bbox), network_type="drive")
        edges = ox.graph_to_gdfs(G, nodes=False)
        return edges.to_crs("EPSG:4326")
    except Exception as e:
        print(f"[Data] Road fetch failed ({e}), using corridor fallback.")
        return None


def _fetch_power(bbox):
    """Return a GeoDataFrame of power lines and substations from OSM."""
    try:
        import osmnx as ox
        print("[Data] Fetching power infrastructure from OSM …")
        gdf = ox.features_from_bbox(_bbox_tuple(bbox), tags={"power": ["line", "substation", "tower"]})
        return gdf[gdf.geometry.notnull()].to_crs("EPSG:4326")
    except Exception as e:
        print(f"[Data] Power fetch failed ({e}), skipping.")
        return None


def _fetch_commercial(bbox):
    """Return a GeoDataFrame of commercial POIs (shops, malls, offices)."""
    try:
        import osmnx as ox
        print("[Data] Fetching commercial POIs from OSM …")
        gdf = ox.features_from_bbox(_bbox_tuple(bbox), tags={"landuse": "commercial", "shop": True})
        return gdf[gdf.geometry.notnull()].to_crs("EPSG:4326")
    except Exception as e:
        print(f"[Data] Commercial POI fetch failed ({e}), skipping.")
        return None


# ── Feature computers ─────────────────────────────────────────────────────────

def _min_distance_to_layer(points_gdf, layer_gdf):
    """
    For each point in points_gdf compute the minimum distance (degrees)
    to any geometry in layer_gdf.  Returns a numpy array.
    """
    if layer_gdf is None or len(layer_gdf) == 0:
        return None
    union = unary_union(layer_gdf.geometry.values)
    return np.array([geom.distance(union) for geom in points_gdf.geometry])


def _normalize(arr, invert=False):
    mn, mx = arr.min(), arr.max()
    if mx == mn:
        return np.ones_like(arr) * (0.0 if not invert else 1.0)
    n = (arr - mn) / (mx - mn)
    return 1 - n if invert else n


def _load_csv_feature(csv_path, sites_gdf, value_col):
    """
    Spatial nearest-neighbour join: for each candidate site find the
    closest row in the CSV and return its value_col.
    """
    if not os.path.exists(csv_path):
        return None
    df = pd.read_csv(csv_path)
    required = {"latitude", "longitude", value_col}
    if not required.issubset(df.columns):
        print(f"[Data] {csv_path} missing columns {required - set(df.columns)}, skipping.")
        return None

    ref_gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["longitude"], df["latitude"]), crs="EPSG:4326"
    )
    joined = gpd.sjoin_nearest(sites_gdf[["geometry"]], ref_gdf[[value_col, "geometry"]], how="left")
    return joined[value_col].values


# ── Main entry point ──────────────────────────────────────────────────────────

def load_real_world_features(sites_gdf):
    """
    Enrich sites_gdf with real-world feature columns.
    Any feature that cannot be fetched falls back to the synthetic value
    already present in sites_gdf (from gis_filtering.py).

    Returns an enriched copy of sites_gdf.
    """
    gdf = sites_gdf.copy()

    roads      = _fetch_roads(CITY_BOUNDS)
    power      = _fetch_power(CITY_BOUNDS)
    commercial = _fetch_commercial(CITY_BOUNDS)

    # ── proximity_to_roads ────────────────────────────────────────────────────
    road_dist = _min_distance_to_layer(gdf, roads)
    if road_dist is not None:
        gdf["proximity_to_roads"] = _normalize(road_dist, invert=True)
        print("[Data] ✓ proximity_to_roads  ← OSM road network")
    else:
        # proxy: normalise existing traffic_volume
        gdf["proximity_to_roads"] = _normalize(gdf["traffic_volume"].values)
        print("[Data] ~ proximity_to_roads  ← traffic_volume proxy")

    # ── grid_access ───────────────────────────────────────────────────────────
    power_dist = _min_distance_to_layer(gdf, power)
    if power_dist is not None:
        gdf["grid_access"] = _normalize(power_dist, invert=True)
        print("[Data] ✓ grid_access         ← OSM power infrastructure")
    else:
        print("[Data] ~ grid_access         ← synthetic (kept as-is)")

    # ── proximity_to_commercial_areas ─────────────────────────────────────────
    comm_dist = _min_distance_to_layer(gdf, commercial)
    if comm_dist is not None:
        gdf["commercial_proximity"] = _normalize(comm_dist, invert=True)
        print("[Data] ✓ commercial_proximity← OSM commercial POIs")
    else:
        print("[Data] ~ commercial_proximity← synthetic (kept as-is)")

    # ── population_density ────────────────────────────────────────────────────
    pop = _load_csv_feature(POPULATION_CSV, gdf, "population_density")
    if pop is not None:
        gdf["population_density"] = pop
        print("[Data] ✓ population_density  ← population.csv")
    else:
        print("[Data] ~ population_density  ← synthetic (kept as-is)")
        print(f"         → To use real data: place a CSV at {POPULATION_CSV}")
        print(f"           with columns: latitude, longitude, population_density")

    # ── land_cost ─────────────────────────────────────────────────────────────
    lc = _load_csv_feature(LAND_COST_CSV, gdf, "land_cost_normalized")
    if lc is not None:
        gdf["land_cost"] = lc
        print("[Data] ✓ land_cost           ← land_cost.csv")
    else:
        print("[Data] ~ land_cost           ← synthetic (kept as-is)")
        print(f"         → To use real data: place a CSV at {LAND_COST_CSV}")
        print(f"           with columns: latitude, longitude, land_cost_normalized")

    # ── traffic_volume ────────────────────────────────────────────────────────
    # OSM road network edge speeds / lane counts are the best free proxy.
    if roads is not None and "lanes" in roads.columns:
        road_dist2 = _min_distance_to_layer(gdf, roads)
        gdf["traffic_volume"] = _normalize(road_dist2, invert=True) * 10000
        print("[Data] ✓ traffic_volume      ← OSM road lane density")
    else:
        print("[Data] ~ traffic_volume      ← synthetic (kept as-is)")

    # ── environmental_sensitivity ─────────────────────────────────────────────
    # Derived: areas far from roads + power = likely greener / more sensitive
    if road_dist is not None and power_dist is not None:
        gdf["environmental_sensitivity"] = (
            _normalize(road_dist) * 0.5 + _normalize(power_dist) * 0.5
        )
        print("[Data] ✓ environmental_sensitivity ← road+power distance proxy")
    else:
        gdf["environmental_sensitivity"] = 1 - gdf["grid_access"]
        print("[Data] ~ environmental_sensitivity ← 1 - grid_access proxy")

    print(f"\n[Data] Feature enrichment complete. {len(gdf)} sites ready.")
    return gdf


def print_data_guide():
    """Print a guide on where to get real data for each feature."""
    guide = """
╔══════════════════════════════════════════════════════════════════════════╗
║           REAL-WORLD DATA SOURCES GUIDE                                 ║
╠══════════════════════════════════════════════════════════════════════════╣
║ FEATURE               SOURCE                  URL / HOW TO GET          ║
╠══════════════════════════════════════════════════════════════════════════╣
║ proximity_to_roads    OpenStreetMap (auto)     fetched via OSMnx         ║
║ grid_access           OpenStreetMap (auto)     fetched via OSMnx         ║
║ commercial_proximity  OpenStreetMap (auto)     fetched via OSMnx         ║
║ traffic_volume        OSM road lanes (auto)    fetched via OSMnx         ║
║ environmental_sens.   Derived from above       computed automatically    ║
╠══════════════════════════════════════════════════════════════════════════╣
║ population_density    WorldPop (manual CSV)                              ║
║   → https://hub.worldpop.org/geodata/listing?id=29                      ║
║   → Download: IND population 100m raster → convert to CSV               ║
║   → Or: Census of India ward data → data.gov.in                         ║
║   → Save as: data/raw/population.csv                                    ║
║   → Columns: latitude, longitude, population_density                    ║
╠══════════════════════════════════════════════════════════════════════════╣
║ land_cost             BBMP / BDA guidance value (manual CSV)             ║
║   → https://bbmptax.karnataka.gov.in  (guidance value tables)           ║
║   → Or: https://kaveri.karnataka.gov.in (stamp duty guidance values)    ║
║   → Save as: data/raw/land_cost.csv                                     ║
║   → Columns: latitude, longitude, land_cost_normalized  (0.0–1.0)       ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
    print(guide)
