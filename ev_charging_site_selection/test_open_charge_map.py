#!/usr/bin/env python3
"""
Test Open Charge Map API
Replace 'YOUR_API_KEY' with your actual API key
"""

import sys
sys.path.insert(0, 'src')

# PASTE YOUR API KEY HERE
OPEN_CHARGE_MAP_KEY = "a334ea36-bf1e-4f05-b1e0-8000e73c4c11"  # Your actual key

import os
os.environ['OPEN_CHARGE_MAP_KEY'] = OPEN_CHARGE_MAP_KEY

from api_integrations import fetch_open_charge_map_stations

print("="*70)
print("  TESTING OPEN CHARGE MAP API")
print("="*70)

# Bangalore bounding box
bbox = {
    "north": 13.15,
    "south": 12.85,
    "east": 77.75,
    "west": 77.45,
}

print(f"\nAPI Key: {OPEN_CHARGE_MAP_KEY[:10]}...")
print(f"Searching for EV stations in Bangalore...")
print(f"Bounding box: {bbox}")

# Fetch stations
stations = fetch_open_charge_map_stations(bbox, max_results=50)

if stations is not None and len(stations) > 0:
    print(f"\n✅ SUCCESS! Found {len(stations)} EV charging stations")
    
    print("\n" + "="*70)
    print("TOP 10 EV CHARGING STATIONS IN BANGALORE")
    print("="*70)
    
    for idx, row in stations.head(10).iterrows():
        print(f"\n{idx+1}. {row['name']}")
        print(f"   📍 Location: {row['town']}, {row['address']}")
        print(f"   🔌 Charging Points: {row['num_points']}")
        print(f"   📊 Status: {row['status']}")
        print(f"   🏢 Usage: {row['usage_type']}")
        print(f"   🗺️  Coordinates: {row['latitude']:.4f}, {row['longitude']:.4f}")
    
    # Save to CSV
    stations_df = stations.copy()
    stations_df['latitude'] = stations_df.geometry.y
    stations_df['longitude'] = stations_df.geometry.x
    stations_df.drop(columns=['geometry']).to_csv('outputs/ev_stations_bangalore.csv', index=False)
    
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    print(f"""
✅ API is working!
✅ Found {len(stations)} EV charging stations in Bangalore
✅ Data saved to: outputs/ev_stations_bangalore.csv

Station Statistics:
  - Total Stations: {len(stations)}
  - Total Charging Points: {stations['num_points'].sum()}
  - Average Points per Station: {stations['num_points'].mean():.1f}
  
Status Breakdown:
{stations['status'].value_counts().to_string()}

Usage Type Breakdown:
{stations['usage_type'].value_counts().to_string()}

Next Steps:
  1. Use this data to analyze competition
  2. Avoid placing new sites too close to existing stations
  3. Identify underserved areas
""")
    
else:
    print("\n❌ No stations found or API error")
    print("\nTroubleshooting:")
    print("  1. Check your API key is correct")
    print("  2. Make sure you replaced 'YOUR_API_KEY' with actual key")
    print("  3. Verify your account is active at https://openchargemap.org/")
    print("  4. Check internet connection")

print("\n" + "="*70)
print("  TEST COMPLETE")
print("="*70)
