# API Configuration for Real-World Data Integration
# Add your API keys here

# ============================================
# CRITICAL APIs (Must Have for Production)
# ============================================

# Google Maps APIs (Geocoding, Places, Traffic)
GOOGLE_MAPS_API_KEY = ""  # Get from: https://console.cloud.google.com/google/maps-apis
# Cost: $5/1000 geocoding requests, $17/1000 places requests
# Free tier: $200/month credit

# OpenRouteService (Routing, Isochrones, Distance Matrix)
OPENROUTESERVICE_API_KEY = "YOUR_OPENROUTESERVICE_API_KEY"  # Get from: https://openrouteservice.org/dev/#/signup
# Cost: FREE up to 2000 requests/day

# ============================================
# ALREADY CONFIGURED
# ============================================

# PositionStack (Geocoding) - Already working
POSITIONSTACK_API_KEY = "YOUR_POSITIONSTACK_API_KEY"

# Open Charge Map (Existing EV Stations) - Already working
OPEN_CHARGE_MAP_API_KEY = "YOUR_OPEN_CHARGE_MAP_API_KEY"

# ============================================
# IMPORTANT APIs (Highly Recommended)
# ============================================

# TomTom Traffic API (Real-time traffic data)
TOMTOM_API_KEY = "YOUR_TOMTOM_API_KEY"  # Get from: https://developer.tomtom.com/
# Cost: FREE tier available (2500 requests/day)

# OpenWeatherMap (Weather and climate data)
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"  # Get from: https://openweathermap.org/api
# Cost: FREE up to 1000 calls/day

# HERE Maps (Alternative to Google Maps)
HERE_API_KEY = "YOUR_HERE_API_KEY"  # Get from: https://developer.here.com/
# Cost: FREE tier available (250k transactions/month)

# ============================================
# NICE-TO-HAVE APIs (Enhancement)
# ============================================

# Mapbox (Alternative mapping and geocoding)
MAPBOX_API_KEY = ""  # Get from: https://account.mapbox.com/
# Cost: FREE tier available (50k requests/month)

# ============================================
# DATA SOURCES (No API Key Needed)
# ============================================

# Census Data - Download manually from:
# https://data.gov.in/
# Search for: "Census 2011 Ward Data Bangalore"

# Land Cost Data - Scrape from:
# https://kaveri.karnataka.gov.in (Karnataka Land Records)
# https://bbmptax.karnataka.gov.in (BBMP Property Tax - has guidance values)

# Electricity Grid Data - Use OpenStreetMap:
# Already implemented in data_loader.py using OSMnx

# ============================================
# PRIORITY RECOMMENDATION
# ============================================

"""
For a production-ready system, get these 3 APIs first:

1. Google Maps API (Geocoding + Places)
   - Most accurate for India
   - Get real traffic, POI density, business data
   - Cost: ~$200-500/month for moderate usage

2. OpenRouteService API (FREE)
   - Calculate real driving distances
   - Route optimization
   - Accessibility analysis

3. TomTom Traffic API (FREE tier)
   - Real-time traffic patterns
   - Historical traffic data
   - Peak hour analysis

Total cost: ~$200-500/month (Google only, others are FREE)
"""

# ============================================
# USAGE EXAMPLE
# ============================================

"""
# In your code:
from config_apis import GOOGLE_MAPS_API_KEY, OPENROUTESERVICE_API_KEY

# Google Geocoding
import googlemaps
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
result = gmaps.geocode('Koramangala, Bangalore')

# OpenRouteService Distance Matrix
import requests
url = f"https://api.openrouteservice.org/v2/matrix/driving-car"
headers = {'Authorization': OPENROUTESERVICE_API_KEY}
response = requests.post(url, json=payload, headers=headers)
"""
