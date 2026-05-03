#!/usr/bin/env python3
"""
Test script for PositionStack API: 25568ac20b49c89857f39f3505b6f7f5
PositionStack is a geocoding service (forward & reverse geocoding)
"""

import sys
sys.path.insert(0, 'src')

from api_integrations import geocode_positionstack, reverse_geocode_positionstack

print("="*70)
print("  TESTING POSITIONSTACK API")
print("  API Key: 25568ac20b49c89857f39f3505b6f7f5")
print("  Free Tier: 25,000 requests/month")
print("="*70)

# Test locations
test_locations = [
    "Koramangala, Bangalore",
    "Whitefield, Bangalore",
    "Indiranagar, Bangalore",
    "MG Road, Bangalore",
]

print("\n" + "="*70)
print("TEST 1: FORWARD GEOCODING (Location → Coordinates)")
print("="*70)

results = []
for location in test_locations:
    result = geocode_positionstack(location)
    if result:
        results.append(result)
        print(f"\n✅ {location}")
        print(f"   Coordinates: {result['lat']:.4f}, {result['lon']:.4f}")
        print(f"   Full Address: {result['display_name']}")
        print(f"   Region: {result.get('region', 'N/A')}")
        print(f"   Country: {result.get('country', 'N/A')}")
    else:
        print(f"\n❌ Failed: {location}")

if results:
    print("\n" + "="*70)
    print("TEST 2: REVERSE GEOCODING (Coordinates → Location)")
    print("="*70)
    
    # Test reverse geocoding with first result
    first = results[0]
    reverse = reverse_geocode_positionstack(first['lat'], first['lon'])
    
    if reverse:
        print(f"\n✅ Reverse Geocoding Successful")
        print(f"   Input: {first['lat']:.4f}, {first['lon']:.4f}")
        print(f"   Address: {reverse['display_name']}")
        print(f"   Street: {reverse.get('street', 'N/A')}")
        print(f"   Locality: {reverse.get('locality', 'N/A')}")
        print(f"   Postal Code: {reverse.get('postal_code', 'N/A')}")
    else:
        print("\n❌ Reverse geocoding failed")

print("\n" + "="*70)
print("  TEST COMPLETE")
print("="*70)

if results:
    print(f"""
✅ SUCCESS! PositionStack API is working!

Your API provides:
  ✓ Forward Geocoding (location name → coordinates)
  ✓ Reverse Geocoding (coordinates → location name)
  ✓ 25,000 requests/month (free tier)

Usage in your code:
  from src.api_integrations import geocode_positionstack, reverse_geocode_positionstack
  
  # Forward geocoding
  location = geocode_positionstack("Koramangala, Bangalore")
  print(f"Lat: {{location['lat']}}, Lon: {{location['lon']}}")
  
  # Reverse geocoding
  address = reverse_geocode_positionstack(12.9357, 77.6241)
  print(f"Address: {{address['display_name']}}")

Integration with your project:
  - Use for geocoding user search queries
  - Convert site coordinates to readable addresses
  - Validate location data
  - Enrich site information with locality details
""")
else:
    print("""
❌ API test failed. Please check:
  1. API key is correct: 25568ac20b49c89857f39f3505b6f7f5
  2. You haven't exceeded the free tier limit (25,000 req/month)
  3. Your account is active at https://positionstack.com/
""")
