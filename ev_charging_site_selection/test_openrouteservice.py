#!/usr/bin/env python3
"""
Test OpenRouteService (HeiGIT) API Integration
"""

import sys
sys.path.append('src')

from api_integrations import get_route_openrouteservice, API_CONFIG

print("="*70)
print("  Testing OpenRouteService (HeiGIT) API")
print("="*70)

# Check API key
api_key = API_CONFIG["openrouteservice"]["api_key"]
print(f"\n✓ API Key configured: {api_key[:20]}...")

# Test 1: Route from MG Road to Koramangala
print("\n" + "-"*70)
print("Test 1: Route Calculation")
print("-"*70)

start = (77.6069, 12.9756)  # MG Road, Bangalore (lon, lat)
end = (77.6193, 12.9352)    # Koramangala, Bangalore (lon, lat)

print(f"Start: MG Road ({start[1]}, {start[0]})")
print(f"End: Koramangala ({end[1]}, {end[0]})")

route = get_route_openrouteservice(start, end)

if route:
    print(f"\n✓ SUCCESS!")
    print(f"  Distance: {route['distance']/1000:.2f} km")
    print(f"  Duration: {route['duration']/60:.1f} minutes")
    if isinstance(route['geometry'], dict):
        print(f"  Geometry points: {len(route['geometry'].get('coordinates', []))}")
else:
    print("\n✗ FAILED - Route calculation failed")

# Test 2: Multiple routes
print("\n" + "-"*70)
print("Test 2: Multiple Routes")
print("-"*70)

locations = [
    ("MG Road", (77.6069, 12.9756)),
    ("Whitefield", (77.7461, 12.9899)),
    ("Electronic City", (77.6603, 12.8458)),
]

for name, coords in locations:
    route = get_route_openrouteservice(start, coords)
    if route:
        print(f"✓ {name:20s}: {route['distance']/1000:6.2f} km, {route['duration']/60:5.1f} min")
    else:
        print(f"✗ {name:20s}: Failed")

print("\n" + "="*70)
print("  OpenRouteService API Test Complete")
print("="*70)
