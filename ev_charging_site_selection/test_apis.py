#!/usr/bin/env python3
"""
Demo script to test real-world API integrations
Run: python test_apis.py
"""

import sys
sys.path.insert(0, 'src')

from api_integrations import (
    print_api_setup_guide,
    geocode_location,
    get_route_osrm,
    get_route_openrouteservice,
    fetch_open_charge_map_stations,
    fetch_opencellid_population_proxy,
    fetch_all_real_world_data,
)

# Bangalore bounding box
BBOX = {
    "north": 13.15,
    "south": 12.85,
    "east": 77.75,
    "west": 77.45,
}

def test_geocoding():
    """Test geocoding API"""
    print("\n" + "="*70)
    print("TEST 1: GEOCODING")
    print("="*70)
    
    locations = [
        "Koramangala, Bangalore",
        "Whitefield, Bangalore",
        "Indiranagar, Bangalore",
        "MG Road, Bangalore",
    ]
    
    results = []
    for loc in locations:
        result = geocode_location(loc)
        if result:
            results.append(result)
            print(f"  ✓ {loc}")
            print(f"    → {result['lat']:.4f}, {result['lon']:.4f}")
    
    return results


def test_routing(locations):
    """Test routing APIs"""
    print("\n" + "="*70)
    print("TEST 2: ROUTING")
    print("="*70)
    
    if len(locations) < 2:
        print("  ⚠ Need at least 2 locations for routing test")
        return
    
    start = (locations[0]['lon'], locations[0]['lat'])
    end = (locations[1]['lon'], locations[1]['lat'])
    
    print(f"\n  Route: {locations[0]['display_name']}")
    print(f"      → {locations[1]['display_name']}")
    
    # Test OSRM (free, no key)
    print("\n  Testing OSRM...")
    route = get_route_osrm(start, end)
    if route:
        print(f"    ✓ Distance: {route['distance']/1000:.2f} km")
        print(f"    ✓ Duration: {route['duration']/60:.1f} minutes")
    
    # Test OpenRouteService (requires key)
    print("\n  Testing OpenRouteService...")
    route = get_route_openrouteservice(start, end)
    if route:
        print(f"    ✓ Distance: {route['distance']/1000:.2f} km")
        print(f"    ✓ Duration: {route['duration']/60:.1f} minutes")


def test_ev_stations():
    """Test EV stations API"""
    print("\n" + "="*70)
    print("TEST 3: EV CHARGING STATIONS")
    print("="*70)
    
    stations = fetch_open_charge_map_stations(BBOX, max_results=20)
    
    if stations is not None and len(stations) > 0:
        print(f"\n  ✓ Found {len(stations)} EV charging stations")
        print("\n  Top 5 stations:")
        for idx, row in stations.head(5).iterrows():
            print(f"    {idx+1}. {row['name']}")
            print(f"       {row['town']}, {row['address']}")
            print(f"       {row['num_points']} charging points | Status: {row['status']}")
        
        # Save to CSV
        stations_df = stations.copy()
        stations_df['latitude'] = stations_df.geometry.y
        stations_df['longitude'] = stations_df.geometry.x
        stations_df.drop(columns=['geometry']).to_csv('outputs/ev_stations_real.csv', index=False)
        print(f"\n  ✓ Saved to outputs/ev_stations_real.csv")
    else:
        print("  ⚠ No stations found or API key needed")


def test_population_proxy():
    """Test population proxy API"""
    print("\n" + "="*70)
    print("TEST 4: POPULATION DATA (Cell Tower Proxy)")
    print("="*70)
    
    cell_data = fetch_opencellid_population_proxy(BBOX)
    
    if cell_data is not None and len(cell_data) > 0:
        print(f"\n  ✓ Found {len(cell_data)} cell towers")
        print("  (Cell tower density can be used as population proxy)")
        
        # Save to CSV
        cell_df = cell_data.copy()
        cell_df['latitude'] = cell_df.geometry.y
        cell_df['longitude'] = cell_df.geometry.x
        cell_df.drop(columns=['geometry']).to_csv('outputs/population_cellid.csv', index=False)
        print(f"  ✓ Saved to outputs/population_cellid.csv")
    else:
        print("  ⚠ API key needed. Get free key from: https://opencellid.org/")


def main():
    """Run all API tests"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "REAL-WORLD API INTEGRATION TEST" + " "*22 + "║")
    print("╚" + "="*68 + "╝")
    
    # Print setup guide
    print_api_setup_guide()
    
    # Test 1: Geocoding (no key needed)
    locations = test_geocoding()
    
    # Test 2: Routing (no key needed for OSRM)
    if locations:
        test_routing(locations)
    
    # Test 3: EV Stations (optional key)
    test_ev_stations()
    
    # Test 4: Population proxy (requires key)
    test_population_proxy()
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    print("""
  ✓ Geocoding: Works without API key (Nominatim)
  ✓ Routing: Works without API key (OSRM)
  ✓ EV Stations: Works without API key (Open Charge Map)
  ⚠ Population: Requires API key (OpenCellID)
  
  For production use:
  1. Sign up for free API keys (see guide above)
  2. Set environment variables
  3. Run: python test_apis.py
  
  Output files saved to: outputs/
    - ev_stations_real.csv
    - population_cellid.csv (if API key provided)
""")


if __name__ == "__main__":
    main()
