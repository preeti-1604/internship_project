"""
Real-world API integrations for EV Charging Site Selection System

APIs integrated:
1. Population Data - WorldPop, Census India, OpenCellID
2. EV Stations - Open Charge Map, PlugShare
3. Location & Routing - OpenRouteService, OSRM, Google Maps
4. Geocoding - Nominatim, Google Geocoding
"""

import os
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import time
import json

# API Configuration
API_CONFIG = {
    "open_charge_map": {
        "base_url": "https://api.openchargemap.io/v3/poi/",
        "api_key": os.getenv("OPEN_CHARGE_MAP_KEY", "YOUR_OPEN_CHARGE_MAP_KEY"),
    },
    "openrouteservice": {
        "base_url": "https://api.openrouteservice.org",
        "api_key": os.getenv("ORS_API_KEY", "YOUR_ORS_API_KEY"),
    },
    "osrm": {
        "base_url": "http://router.project-osrm.org",  # Free, no key needed
    },
    "nominatim": {
        "base_url": "https://nominatim.openstreetmap.org",  # Free, no key needed
    },
    "census_india": {
        "base_url": "https://www.censusindia.gov.in/pca/cdb_pca_census/",  # Public data
    },
    "google_maps": {
        "base_url": "https://maps.googleapis.com/maps/api",
        "api_key": os.getenv("GOOGLE_MAPS_KEY", ""),  # Paid, get from Google Cloud Console
    },
    "mapbox": {
        "base_url": "https://api.mapbox.com",
        "api_key": os.getenv("MAPBOX_API_KEY", "YOUR_MAPBOX_API_KEY"),
    },
    "opencage": {
        "base_url": "https://api.opencagedata.com/geocode/v1",
        "api_key": os.getenv("OPENCAGE_API_KEY", "YOUR_OPENCAGE_API_KEY"),
    },
    "here_maps": {
        "base_url": "https://geocode.search.hereapi.com/v1",
        "api_key": os.getenv("HERE_API_KEY", "YOUR_HERE_API_KEY"),
    },
    "positionstack": {
        "base_url": "http://api.positionstack.com/v1",
        "api_key": os.getenv("POSITIONSTACK_API_KEY", "YOUR_POSITIONSTACK_API_KEY"),
    }
}


# ═══════════════════════════════════════════════════════════════════════════
# 1. POPULATION DATA APIs
# ═══════════════════════════════════════════════════════════════════════════

def fetch_worldpop_data(bbox, year=2020):
    """
    Fetch population data from WorldPop API
    
    Args:
        bbox: dict with keys 'north', 'south', 'east', 'west'
        year: Population data year
    
    Returns:
        GeoDataFrame with population density
    
    API: https://www.worldpop.org/rest/data
    Free: Yes
    """
    print("[API] Fetching WorldPop population data...")
    
    # WorldPop REST API endpoint
    url = "https://www.worldpop.org/rest/data/pop/wpgp"
    
    params = {
        "iso3": "IND",  # India
        "year": year,
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        # Note: WorldPop returns raster data, you'll need to process it
        # For production, download the GeoTIFF and extract values
        print("[API] ✓ WorldPop data available. Download GeoTIFF from:")
        print(f"      https://hub.worldpop.org/geodata/listing?id=29")
        
        return None  # Placeholder - implement raster processing
        
    except Exception as e:
        print(f"[API] ✗ WorldPop fetch failed: {e}")
        return None


def fetch_census_india_population(state="Karnataka", district="Bangalore"):
    """
    Fetch population data from Census India
    
    Args:
        state: State name
        district: District name
    
    Returns:
        DataFrame with ward-level population
    
    API: Census India Open Data
    Free: Yes
    """
    print("[API] Fetching Census India population data...")
    
    # Census India data portal
    url = "https://censusindia.gov.in/nada/index.php/api/catalog"
    
    try:
        # Note: Census India doesn't have a direct REST API
        # Use their data portal or download CSV files
        print("[API] ℹ Census India data available at:")
        print("      https://censusindia.gov.in/")
        print("      https://data.gov.in/catalog/population-india")
        
        # Alternative: Use data.gov.in API
        datagov_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        api_key = os.getenv("DATA_GOV_IN_KEY", "")
        
        if api_key:
            params = {
                "api-key": api_key,
                "format": "json",
                "filters[state]": state,
                "filters[district]": district,
            }
            response = requests.get(datagov_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return pd.DataFrame(data.get("records", []))
        
        return None
        
    except Exception as e:
        print(f"[API] ✗ Census India fetch failed: {e}")
        return None


def fetch_opencellid_population_proxy(bbox):
    """
    Use OpenCellID cell tower density as population proxy
    
    Args:
        bbox: dict with keys 'north', 'south', 'east', 'west'
    
    Returns:
        GeoDataFrame with cell tower locations (population proxy)
    
    API: https://opencellid.org/
    Free: Yes (with registration)
    """
    print("[API] Fetching OpenCellID data (population proxy)...")
    
    api_key = os.getenv("OPENCELLID_KEY", "")
    if not api_key:
        print("[API] ℹ Get free API key from: https://opencellid.org/")
        return None
    
    url = "https://opencellid.org/cell/getInArea"
    
    params = {
        "key": api_key,
        "BBOX": f"{bbox['west']},{bbox['south']},{bbox['east']},{bbox['north']}",
        "format": "json",
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "cells" in data:
            df = pd.DataFrame(data["cells"])
            gdf = gpd.GeoDataFrame(
                df,
                geometry=gpd.points_from_xy(df["lon"], df["lat"]),
                crs="EPSG:4326"
            )
            print(f"[API] ✓ OpenCellID: {len(gdf)} cell towers fetched")
            return gdf
        
        return None
        
    except Exception as e:
        print(f"[API] ✗ OpenCellID fetch failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# 2. EV CHARGING STATIONS APIs
# ═══════════════════════════════════════════════════════════════════════════

def _parse_ocm_response(data):
    """Parse raw Open Charge Map API response into a list of station dicts."""
    stations = []
    for station in data:
        addr = station.get("AddressInfo", {})
        lat = addr.get("Latitude")
        lon = addr.get("Longitude")
        if lat is None or lon is None:
            continue
        stations.append({
            "station_id": station.get("ID"),
            "name": addr.get("Title", "Unknown"),
            "latitude": lat,
            "longitude": lon,
            "address": addr.get("AddressLine1", ""),
            "town": addr.get("Town", ""),
            "postcode": addr.get("Postcode", ""),
            "num_points": station.get("NumberOfPoints", 0) or 0,
            "usage_type": (station.get("UsageType") or {}).get("Title", "Unknown"),
            "status": (station.get("StatusType") or {}).get("Title", "Unknown"),
        })
    return stations


def fetch_open_charge_map_stations(bbox, max_results=500):
    """
    Fetch ALL existing EV charging stations from Open Charge Map using a
    grid-tile pagination strategy (API hard-caps each request at 500).

    The Bangalore bounding box is split into a 4x4 grid of 16 tiles.
    Each tile is fetched independently, results are deduplicated by station_id.

    Args:
        bbox: dict with keys 'north', 'south', 'east', 'west'
        max_results: per-tile limit (max 500 per OCM API rules)

    Returns:
        GeoDataFrame with all EV charging stations found
    """
    print("[API] Fetching Open Charge Map EV stations (full grid scan)...")

    api_key = API_CONFIG["open_charge_map"]["api_key"]
    url = API_CONFIG["open_charge_map"]["base_url"]
    headers = {"Accept": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key

    # Split bbox into grid tiles to overcome the 500-result cap
    grid_rows, grid_cols = 4, 4
    lat_step = (bbox["north"] - bbox["south"]) / grid_rows
    lon_step = (bbox["east"]  - bbox["west"])  / grid_cols

    all_stations = {}
    tile_count = 0

    for row in range(grid_rows):
        for col in range(grid_cols):
            tile_south = bbox["south"] + row * lat_step
            tile_north = tile_south + lat_step
            tile_west  = bbox["west"]  + col * lon_step
            tile_east  = tile_west  + lon_step

            center_lat = (tile_south + tile_north) / 2
            center_lon = (tile_west  + tile_east)  / 2
            # radius that covers the tile diagonal (approx)
            radius_km  = max(lat_step, lon_step) * 111 * 0.9

            params = {
                "output":      "json",
                "countrycode": "IN",
                "latitude":    center_lat,
                "longitude":   center_lon,
                "distance":    radius_km,
                "maxresults":  500,
                "compact":     "true",
                "verbose":     "false",
            }

            try:
                resp = requests.get(url, params=params, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                parsed = _parse_ocm_response(data)
                for s in parsed:
                    all_stations[s["station_id"]] = s  # deduplicate by ID
                tile_count += 1
                time.sleep(0.3)  # respect rate limit
            except Exception as e:
                print(f"[API] ⚠ Tile ({row},{col}) failed: {e}")

    if not all_stations:
        print("[API] ✗ Open Charge Map: no stations found")
        return None

    df = pd.DataFrame(list(all_stations.values()))
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326"
    )
    print(f"[API] ✓ Open Charge Map: {len(gdf)} unique EV stations fetched across {tile_count} tiles")
    print(f"[API]   Total charging points: {int(df['num_points'].sum())}")
    return gdf


def fetch_plugshare_stations(bbox):
    """
    Fetch EV stations from PlugShare (requires scraping or unofficial API)
    
    Args:
        bbox: dict with keys 'north', 'south', 'east', 'west'
    
    Returns:
        GeoDataFrame with EV charging stations
    
    Note: PlugShare doesn't have official public API
    Alternative: Use Open Charge Map or manual data collection
    """
    print("[API] ℹ PlugShare doesn't have public API")
    print("      Use Open Charge Map or https://www.plugshare.com/ for manual data")
    return None


# ═══════════════════════════════════════════════════════════════════════════
# 3. LOCATION & ROUTING APIs
# ═══════════════════════════════════════════════════════════════════════════

def geocode_location(location_name):
    """
    Geocode location name to coordinates using Nominatim
    
    Args:
        location_name: Location name (e.g., "Koramangala, Bangalore")
    
    Returns:
        dict with 'lat', 'lon', 'display_name'
    
    API: https://nominatim.openstreetmap.org/
    Free: Yes (rate limited to 1 req/sec)
    """
    print(f"[API] Geocoding: {location_name}")
    
    url = f"{API_CONFIG['nominatim']['base_url']}/search"
    
    params = {
        "q": location_name,
        "format": "json",
        "limit": 1,
    }
    
    headers = {
        "User-Agent": "EV-Charging-Site-Selection/1.0"
    }
    
    try:
        time.sleep(1)  # Rate limiting
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data:
            result = data[0]
            print(f"[API] ✓ Geocoded: {result['display_name']}")
            return {
                "lat": float(result["lat"]),
                "lon": float(result["lon"]),
                "display_name": result["display_name"],
            }
        
        return None
        
    except Exception as e:
        print(f"[API] ✗ Geocoding failed: {e}")
        return None


def get_route_osrm(start_coords, end_coords):
    """
    Get route between two points using OSRM
    
    Args:
        start_coords: tuple (lon, lat)
        end_coords: tuple (lon, lat)
    
    Returns:
        dict with 'distance' (meters), 'duration' (seconds), 'geometry'
    
    API: http://project-osrm.org/
    Free: Yes
    """
    print("[API] Calculating route with OSRM...")
    
    url = f"{API_CONFIG['osrm']['base_url']}/route/v1/driving/{start_coords[0]},{start_coords[1]};{end_coords[0]},{end_coords[1]}"
    
    params = {
        "overview": "full",
        "geometries": "geojson",
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == "Ok" and data.get("routes"):
            route = data["routes"][0]
            print(f"[API] ✓ Route: {route['distance']/1000:.2f} km, {route['duration']/60:.1f} min")
            return {
                "distance": route["distance"],  # meters
                "duration": route["duration"],  # seconds
                "geometry": route["geometry"],
            }
        
        return None
        
    except Exception as e:
        print(f"[API] ✗ OSRM routing failed: {e}")
        return None


def get_route_openrouteservice(start_coords, end_coords):
    """
    Get route between two points using OpenRouteService
    
    Args:
        start_coords: tuple (lon, lat)
        end_coords: tuple (lon, lat)
    
    Returns:
        dict with 'distance' (meters), 'duration' (seconds), 'geometry'
    
    API: https://openrouteservice.org/
    Free: Yes (5000 requests/day)
    """
    api_key = API_CONFIG["openrouteservice"]["api_key"]
    if not api_key:
        print("[API] ℹ Get free API key from: https://openrouteservice.org/dev/#/signup")
        return None
    
    print("[API] Calculating route with OpenRouteService...")
    
    url = f"{API_CONFIG['openrouteservice']['base_url']}/v2/directions/driving-car"
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }
    
    body = {
        "coordinates": [list(start_coords), list(end_coords)],
    }
    
    try:
        response = requests.post(url, json=body, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("routes"):
            route = data["routes"][0]
            summary = route["summary"]
            print(f"[API] ✓ Route: {summary['distance']/1000:.2f} km, {summary['duration']/60:.1f} min")
            return {
                "distance": summary["distance"],  # meters
                "duration": summary["duration"],  # seconds
                "geometry": route["geometry"],
            }
        
        return None
        
    except Exception as e:
        print(f"[API] ✗ OpenRouteService routing failed: {e}")
        return None


def get_route_google_maps(start_coords, end_coords):
    """
    Get route using Google Maps Directions API
    
    Args:
        start_coords: tuple (lon, lat)
        end_coords: tuple (lon, lat)
    
    Returns:
        dict with 'distance' (meters), 'duration' (seconds), 'polyline'
    
    API: https://developers.google.com/maps/documentation/directions
    Free: No (requires billing, $5/1000 requests)
    """
    api_key = API_CONFIG["google_maps"]["api_key"]
    if not api_key:
        print("[API] ℹ Google Maps API requires billing setup")
        return None
    
    print("[API] Calculating route with Google Maps...")
    
    url = f"{API_CONFIG['google_maps']['base_url']}/directions/json"
    
    params = {
        "origin": f"{start_coords[1]},{start_coords[0]}",
        "destination": f"{end_coords[1]},{end_coords[0]}",
        "key": api_key,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "OK" and data.get("routes"):
            route = data["routes"][0]
            leg = route["legs"][0]
            print(f"[API] ✓ Route: {leg['distance']['text']}, {leg['duration']['text']}")
            return {
                "distance": leg["distance"]["value"],  # meters
                "duration": leg["duration"]["value"],  # seconds
                "polyline": route["overview_polyline"]["points"],
            }
        
        return None
        
    except Exception as e:
        print(f"[API] ✗ Google Maps routing failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# NEW: MAPBOX API INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════

def geocode_mapbox(location_name):
    """
    Geocode location using Mapbox Geocoding API
    
    Args:
        location_name: Location name (e.g., "Koramangala, Bangalore")
    
    Returns:
        dict with 'lat', 'lon', 'display_name'
    
    API: https://docs.mapbox.com/api/search/geocoding/
    Free: Yes (100,000 requests/month)
    """
    api_key = API_CONFIG["mapbox"]["api_key"]
    if not api_key:
        print("[API] ℹ Mapbox API key not set")
        return None
    
    print(f"[API] Geocoding with Mapbox: {location_name}")
    
    url = f"{API_CONFIG['mapbox']['base_url']}/geocoding/v5/mapbox.places/{location_name}.json"
    
    params = {
        "access_token": api_key,
        "limit": 1,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("features"):
            feature = data["features"][0]
            coords = feature["geometry"]["coordinates"]
            print(f"[API] ✓ Mapbox Geocoded: {feature['place_name']}")
            return {
                "lat": coords[1],
                "lon": coords[0],
                "display_name": feature["place_name"],
            }
        
        return None
        
    except Exception as e:
        print(f"[API] ✗ Mapbox geocoding failed: {e}")
        return None


def get_route_mapbox(start_coords, end_coords, profile="driving"):
    """
    Get route using Mapbox Directions API
    
    Args:
        start_coords: tuple (lon, lat)
        end_coords: tuple (lon, lat)
        profile: 'driving', 'walking', 'cycling', 'driving-traffic'
    
    Returns:
        dict with 'distance' (meters), 'duration' (seconds), 'geometry'
    
    API: https://docs.mapbox.com/api/navigation/directions/
    Free: Yes (100,000 requests/month)
    """
    api_key = API_CONFIG["mapbox"]["api_key"]
    if not api_key:
        print("[API] ℹ Mapbox API key not set")
        return None
    
    print(f"[API] Calculating route with Mapbox ({profile})...")
    
    url = f"{API_CONFIG['mapbox']['base_url']}/directions/v5/mapbox/{profile}/{start_coords[0]},{start_coords[1]};{end_coords[0]},{end_coords[1]}"
    
    params = {
        "access_token": api_key,
        "geometries": "geojson",
        "overview": "full",
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("routes"):
            route = data["routes"][0]
            print(f"[API] ✓ Mapbox Route: {route['distance']/1000:.2f} km, {route['duration']/60:.1f} min")
            return {
                "distance": route["distance"],  # meters
                "duration": route["duration"],  # seconds
                "geometry": route["geometry"],
            }
        
        return None
        
    except Exception as e:
        print(f"[API] ✗ Mapbox routing failed: {e}")
        return None


def geocode_opencage(location_name):
    """
    Geocode location using OpenCage Geocoding API
    
    Args:
        location_name: Location name (e.g., "Koramangala, Bangalore")
    
    Returns:
        dict with 'lat', 'lon', 'display_name'
    
    API: https://opencagedata.com/api
    Free: Yes (2,500 requests/day)
    """
    api_key = API_CONFIG["opencage"]["api_key"]
    if not api_key:
        print("[API] ℹ OpenCage API key not set")
        return None
    
    print(f"[API] Geocoding with OpenCage: {location_name}")
    
    url = f"{API_CONFIG['opencage']['base_url']}/json"
    
    params = {
        "q": location_name,
        "key": api_key,
        "limit": 1,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("results"):
            result = data["results"][0]
            coords = result["geometry"]
            print(f"[API] ✓ OpenCage Geocoded: {result['formatted']}")
            return {
                "lat": coords["lat"],
                "lon": coords["lng"],
                "display_name": result["formatted"],
            }
        
        return None
        
    except Exception as e:
        print(f"[API] ✗ OpenCage geocoding failed: {e}")
        return None


def geocode_here(location_name):
    """
    Geocode location using HERE Geocoding API
    
    Args:
        location_name: Location name (e.g., "Koramangala, Bangalore")
    
    Returns:
        dict with 'lat', 'lon', 'display_name'
    
    API: https://developer.here.com/documentation/geocoding-search-api
    Free: Yes (250,000 requests/month)
    """
    api_key = API_CONFIG["here_maps"]["api_key"]
    if not api_key:
        print("[API] ℹ HERE Maps API key not set")
        return None
    
    print(f"[API] Geocoding with HERE Maps: {location_name}")
    
    url = f"{API_CONFIG['here_maps']['base_url']}/geocode"
    
    params = {
        "q": location_name,
        "apiKey": api_key,
        "limit": 1,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("items"):
            item = data["items"][0]
            coords = item["position"]
            print(f"[API] ✓ HERE Geocoded: {item['title']}")
            return {
                "lat": coords["lat"],
                "lon": coords["lng"],
                "display_name": item["title"],
            }
        
        return None
        
    except Exception as e:
        print(f"[API] ✗ HERE geocoding failed: {e}")
        return None


def geocode_positionstack(location_name):
    """
    Geocode location using PositionStack API
    
    Args:
        location_name: Location name (e.g., "Koramangala, Bangalore")
    
    Returns:
        dict with 'lat', 'lon', 'display_name'
    
    API: https://positionstack.com/documentation
    Free: Yes (25,000 requests/month)
    """
    api_key = API_CONFIG["positionstack"]["api_key"]
    if not api_key:
        print("[API] ℹ PositionStack API key not set")
        return None
    
    print(f"[API] Geocoding with PositionStack: {location_name}")
    
    url = f"{API_CONFIG['positionstack']['base_url']}/forward"
    
    params = {
        "access_key": api_key,
        "query": location_name,
        "limit": 1,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("data"):
            result = data["data"][0]
            print(f"[API] ✓ PositionStack Geocoded: {result['label']}")
            return {
                "lat": result["latitude"],
                "lon": result["longitude"],
                "display_name": result["label"],
                "country": result.get("country", ""),
                "region": result.get("region", ""),
                "locality": result.get("locality", ""),
            }
        
        return None
        
    except Exception as e:
        print(f"[API] ✗ PositionStack geocoding failed: {e}")
        return None


def reverse_geocode_positionstack(lat, lon):
    """
    Reverse geocode coordinates to location name using PositionStack
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        dict with location details
    
    API: https://positionstack.com/documentation
    Free: Yes (25,000 requests/month)
    """
    api_key = API_CONFIG["positionstack"]["api_key"]
    if not api_key:
        print("[API] ℹ PositionStack API key not set")
        return None
    
    print(f"[API] Reverse geocoding with PositionStack: {lat}, {lon}")
    
    url = f"{API_CONFIG['positionstack']['base_url']}/reverse"
    
    params = {
        "access_key": api_key,
        "query": f"{lat},{lon}",
        "limit": 1,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("data"):
            result = data["data"][0]
            print(f"[API] ✓ PositionStack Reverse Geocoded: {result['label']}")
            return {
                "display_name": result["label"],
                "country": result.get("country", ""),
                "region": result.get("region", ""),
                "locality": result.get("locality", ""),
                "street": result.get("street", ""),
                "postal_code": result.get("postal_code", ""),
            }
        
        return None
        
    except Exception as e:
        print(f"[API] ✗ PositionStack reverse geocoding failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# 4. UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def save_api_data_to_csv(data, filename, output_dir="data/raw"):
    """Save API data to CSV for caching"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    if isinstance(data, gpd.GeoDataFrame):
        # Save with lat/lon columns
        df = data.copy()
        df["latitude"] = df.geometry.y
        df["longitude"] = df.geometry.x
        df.drop(columns=["geometry"]).to_csv(filepath, index=False)
    else:
        data.to_csv(filepath, index=False)
    
    print(f"[API] ✓ Saved to {filepath}")


def print_api_setup_guide():
    """Print guide for setting up API keys"""
    guide = """
╔══════════════════════════════════════════════════════════════════════════╗
║                     API SETUP GUIDE                                      ║
╠══════════════════════════════════════════════════════════════════════════╣
║ API                    FREE?   SIGNUP URL                                ║
╠══════════════════════════════════════════════════════════════════════════╣
║ Open Charge Map        ✓ Yes  https://openchargemap.org/site/develop    ║
║ OpenRouteService       ✓ Yes  https://openrouteservice.org/dev/#/signup ║
║ OSRM                   ✓ Yes  No key needed                              ║
║ Nominatim (OSM)        ✓ Yes  No key needed                              ║
║ OpenCellID             ✓ Yes  https://opencellid.org/                    ║
║ Data.gov.in            ✓ Yes  https://data.gov.in/                       ║
║ Google Maps            ✗ Paid https://console.cloud.google.com/          ║
╠══════════════════════════════════════════════════════════════════════════╣
║ SET ENVIRONMENT VARIABLES:                                               ║
║   export OPEN_CHARGE_MAP_KEY="your_key"                                 ║
║   export ORS_API_KEY="your_key"                                          ║
║   export OPENCELLID_KEY="your_key"                                       ║
║   export DATA_GOV_IN_KEY="your_key"                                      ║
║   export GOOGLE_MAPS_KEY="your_key"                                      ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
    print(guide)


# ═══════════════════════════════════════════════════════════════════════════
# 5. MAIN INTEGRATION FUNCTION
# ═══════════════════════════════════════════════════════════════════════════

def fetch_all_real_world_data(bbox):
    """
    Fetch all available real-world data from APIs
    
    Args:
        bbox: dict with keys 'north', 'south', 'east', 'west'
    
    Returns:
        dict with all fetched data
    """
    print("\n" + "="*70)
    print("  FETCHING REAL-WORLD DATA FROM APIs")
    print("="*70 + "\n")
    
    results = {}
    
    # Population data
    results["population_worldpop"] = fetch_worldpop_data(bbox)
    results["population_census"] = fetch_census_india_population()
    results["population_cellid"] = fetch_opencellid_population_proxy(bbox)
    
    # EV stations
    results["ev_stations"] = fetch_open_charge_map_stations(bbox)
    
    # Save fetched data
    if results["ev_stations"] is not None:
        save_api_data_to_csv(results["ev_stations"], "ev_stations_real.csv")
    
    if results["population_cellid"] is not None:
        save_api_data_to_csv(results["population_cellid"], "population_cellid.csv")
    
    print("\n" + "="*70)
    print("  API DATA FETCH COMPLETE")
    print("="*70 + "\n")
    
    return results


if __name__ == "__main__":
    print_api_setup_guide()
    
    # Example usage
    bbox = {
        "north": 13.15,
        "south": 12.85,
        "east": 77.75,
        "west": 77.45,
    }
    
    # Test geocoding
    location = geocode_location("Koramangala, Bangalore")
    if location:
        print(f"\nLocation: {location['display_name']}")
        print(f"Coordinates: {location['lat']}, {location['lon']}")
    
    # Test routing
    if location:
        start = (77.5946, 12.9716)  # MG Road
        end = (location['lon'], location['lat'])
        route = get_route_osrm(start, end)
        if route:
            print(f"\nRoute distance: {route['distance']/1000:.2f} km")
            print(f"Route duration: {route['duration']/60:.1f} minutes")
    
    # Fetch all data
    # data = fetch_all_real_world_data(bbox)
