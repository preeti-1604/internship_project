#!/usr/bin/env python3
"""
Demo: Using PositionStack API in EV Charging Site Selection Project
"""

import sys
sys.path.insert(0, 'src')

import pandas as pd
from api_integrations import geocode_positionstack, reverse_geocode_positionstack

print("="*70)
print("  POSITIONSTACK API INTEGRATION DEMO")
print("="*70)

# ═══════════════════════════════════════════════════════════════════════════
# USE CASE 1: Geocode User Search Queries
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("USE CASE 1: Geocode User Search Queries")
print("="*70)

user_searches = [
    "Koramangala, Bangalore",
    "MG Road, Bangalore",
]

print("\nUser searches for EV charging stations near their location:")
for search in user_searches:
    location = geocode_positionstack(search)
    if location:
        print(f"\n  User: '{search}'")
        print(f"  → Found: {location['display_name']}")
        print(f"  → Coordinates: {location['lat']:.4f}, {location['lon']:.4f}")
        print(f"  → Can now find nearby EV sites!")

# ═══════════════════════════════════════════════════════════════════════════
# USE CASE 2: Convert Site Coordinates to Readable Addresses
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("USE CASE 2: Convert Site Coordinates to Readable Addresses")
print("="*70)

# Load top ranked sites
try:
    sites = pd.read_csv('outputs/ranked_sites.csv').head(3)
    
    print("\nEnriching top sites with readable addresses:")
    for idx, site in sites.iterrows():
        address = reverse_geocode_positionstack(site['latitude'], site['longitude'])
        if address:
            print(f"\n  Site: {site['site_id']}")
            print(f"  → Coordinates: {site['latitude']:.4f}, {site['longitude']:.4f}")
            print(f"  → Address: {address['display_name']}")
            print(f"  → Locality: {address.get('locality', 'N/A')}")
            print(f"  → Region: {address.get('region', 'N/A')}")
except FileNotFoundError:
    print("\n  ⚠ Run main.py first to generate ranked_sites.csv")

# ═══════════════════════════════════════════════════════════════════════════
# USE CASE 3: Validate and Enrich Location Data
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("USE CASE 3: Validate Location Data")
print("="*70)

test_locations = [
    "Bangalore Airport",
    "Electronic City, Bangalore",
]

print("\nValidating location data for new site proposals:")
for loc in test_locations:
    result = geocode_positionstack(loc)
    if result:
        print(f"\n  ✓ Valid: {loc}")
        print(f"    → {result['display_name']}")
        print(f"    → Region: {result.get('region', 'N/A')}")
        print(f"    → Country: {result.get('country', 'N/A')}")

# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("  INTEGRATION SUMMARY")
print("="*70)
print("""
✅ PositionStack API Successfully Integrated!

Your API provides:
  • Forward Geocoding: Location name → Coordinates
  • Reverse Geocoding: Coordinates → Location name
  • 25,000 requests/month (free tier)

Integration Points in Your Project:
  1. Dashboard Search: Geocode user queries to find nearby sites
  2. Site Details: Convert coordinates to readable addresses
  3. Data Validation: Verify location data quality
  4. Export Reports: Add human-readable addresses to CSV exports

Next Steps:
  1. Update dashboard.py to use geocode_positionstack()
  2. Add address enrichment to ranked_sites.csv
  3. Implement location search in the map interface
  4. Monitor API usage (25,000 req/month limit)

API Documentation:
  https://positionstack.com/documentation
""")
