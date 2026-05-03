# Real-World API Integration Guide

## Overview
This document provides comprehensive information about integrating real-world APIs for:
1. **Population Data** - WorldPop, Census India, OpenCellID
2. **EV Charging Stations** - Open Charge Map, PlugShare
3. **Location & Routing** - OSRM, OpenRouteService, Google Maps
4. **Geocoding** - Nominatim, Google Geocoding

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install requests geopandas pandas shapely
```

### 2. Set Up API Keys (Optional but Recommended)
```bash
# Free APIs
export OPEN_CHARGE_MAP_KEY="your_key_here"
export ORS_API_KEY="your_key_here"
export OPENCELLID_KEY="your_key_here"
export DATA_GOV_IN_KEY="your_key_here"

# Paid APIs
export GOOGLE_MAPS_KEY="your_key_here"
```

### 3. Test APIs
```bash
cd ev_charging_site_selection
python test_apis.py
```

---

## 📊 1. Population Data APIs

### A. WorldPop API
**Purpose**: High-resolution population density data  
**Cost**: FREE  
**Coverage**: Global (100m resolution for India)  
**Signup**: https://www.worldpop.org/

**Data Format**:
- Raster GeoTIFF files
- 100m x 100m grid cells
- Population count per cell

**How to Use**:
```python
from src.api_integrations import fetch_worldpop_data

bbox = {"north": 13.15, "south": 12.85, "east": 77.75, "west": 77.45}
pop_data = fetch_worldpop_data(bbox, year=2020)
```

**Manual Download**:
1. Visit: https://hub.worldpop.org/geodata/listing?id=29
2. Select: India → Year → Download GeoTIFF
3. Convert to CSV using QGIS or Python rasterio
4. Save as: `data/raw/population.csv`

**CSV Format**:
```csv
latitude,longitude,population_density
12.9716,77.5946,18500
12.9352,77.6245,22000
```

---

### B. Census India API
**Purpose**: Official government census data  
**Cost**: FREE  
**Coverage**: India (ward/district level)  
**Website**: https://censusindia.gov.in/

**Data Sources**:
1. **Census India Portal**: https://censusindia.gov.in/
2. **Data.gov.in**: https://data.gov.in/catalog/population-india
3. **NADA Catalog**: https://censusindia.gov.in/nada/

**How to Use**:
```python
from src.api_integrations import fetch_census_india_population

pop_data = fetch_census_india_population(
    state="Karnataka",
    district="Bangalore"
)
```

**Manual Download**:
1. Visit: https://data.gov.in/
2. Search: "Bangalore population"
3. Download CSV
4. Save as: `data/raw/population_census.csv`

---

### C. OpenCellID API (Population Proxy)
**Purpose**: Cell tower locations as population density proxy  
**Cost**: FREE (with registration)  
**Coverage**: Global  
**Signup**: https://opencellid.org/

**Why Cell Towers?**
- High correlation with population density
- Real-time data
- Good proxy for urban areas

**How to Use**:
```python
from src.api_integrations import fetch_opencellid_population_proxy

bbox = {"north": 13.15, "south": 12.85, "east": 77.75, "west": 77.45}
cell_data = fetch_opencellid_population_proxy(bbox)
```

**API Key Setup**:
```bash
# 1. Sign up at https://opencellid.org/
# 2. Get API key from dashboard
# 3. Set environment variable
export OPENCELLID_KEY="your_api_key"
```

---

## 🔌 2. EV Charging Station APIs

### A. Open Charge Map API
**Purpose**: Global EV charging station database  
**Cost**: FREE  
**Coverage**: 200,000+ stations worldwide  
**Signup**: https://openchargemap.org/site/develop

**Features**:
- Station locations
- Number of charging points
- Connector types
- Availability status
- User ratings

**How to Use**:
```python
from src.api_integrations import fetch_open_charge_map_stations

bbox = {"north": 13.15, "south": 12.85, "east": 77.75, "west": 77.45}
stations = fetch_open_charge_map_stations(bbox, max_results=500)

# Save to CSV
stations.to_csv('data/raw/ev_stations.csv', index=False)
```

**API Response Fields**:
```python
{
    "station_id": 12345,
    "name": "Charging Station Name",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "address": "123 Main Street",
    "town": "Bangalore",
    "num_points": 4,
    "usage_type": "Public",
    "status": "Operational"
}
```

**API Key Setup** (Optional):
```bash
# Increases rate limits
export OPEN_CHARGE_MAP_KEY="your_api_key"
```

---

### B. PlugShare (Manual Data)
**Purpose**: Community-driven EV charging map  
**Cost**: FREE (no public API)  
**Website**: https://www.plugshare.com/

**How to Get Data**:
1. Visit: https://www.plugshare.com/
2. Search: "Bangalore, India"
3. Manually collect station data
4. Or use Open Charge Map API instead

---

## 🗺️ 3. Location & Routing APIs

### A. OSRM (Open Source Routing Machine)
**Purpose**: Fast routing engine  
**Cost**: FREE (no API key needed)  
**Coverage**: Global  
**Website**: http://project-osrm.org/

**Features**:
- Distance calculation
- Duration estimation
- Route geometry
- No rate limits on public server

**How to Use**:
```python
from src.api_integrations import get_route_osrm

start = (77.5946, 12.9716)  # (lon, lat) - MG Road
end = (77.6241, 12.9357)    # (lon, lat) - Koramangala

route = get_route_osrm(start, end)
print(f"Distance: {route['distance']/1000:.2f} km")
print(f"Duration: {route['duration']/60:.1f} minutes")
```

**Response**:
```python
{
    "distance": 8500,  # meters
    "duration": 900,   # seconds
    "geometry": {...}  # GeoJSON LineString
}
```

---

### B. OpenRouteService API
**Purpose**: Advanced routing with multiple profiles  
**Cost**: FREE (5000 requests/day)  
**Coverage**: Global  
**Signup**: https://openrouteservice.org/dev/#/signup

**Features**:
- Multiple routing profiles (car, bike, walk)
- Isochrone analysis
- Matrix calculations
- Elevation data

**How to Use**:
```python
from src.api_integrations import get_route_openrouteservice

start = (77.5946, 12.9716)
end = (77.6241, 12.9357)

route = get_route_openrouteservice(start, end)
```

**API Key Setup**:
```bash
# 1. Sign up at https://openrouteservice.org/dev/#/signup
# 2. Get API key from dashboard
# 3. Set environment variable
export ORS_API_KEY="your_api_key"
```

---

### C. Google Maps Directions API
**Purpose**: Premium routing with traffic data  
**Cost**: PAID ($5 per 1000 requests)  
**Coverage**: Global  
**Signup**: https://console.cloud.google.com/

**Features**:
- Real-time traffic
- Alternative routes
- Waypoint optimization
- Transit directions

**How to Use**:
```python
from src.api_integrations import get_route_google_maps

start = (77.5946, 12.9716)
end = (77.6241, 12.9357)

route = get_route_google_maps(start, end)
```

**API Key Setup**:
```bash
# 1. Create project in Google Cloud Console
# 2. Enable Directions API
# 3. Create API key
# 4. Set environment variable
export GOOGLE_MAPS_KEY="your_api_key"
```

---

## 📍 4. Geocoding APIs

### A. Nominatim (OpenStreetMap)
**Purpose**: Free geocoding service  
**Cost**: FREE  
**Coverage**: Global  
**Rate Limit**: 1 request/second  
**Website**: https://nominatim.openstreetmap.org/

**How to Use**:
```python
from src.api_integrations import geocode_location

location = geocode_location("Koramangala, Bangalore")
print(f"Lat: {location['lat']}, Lon: {location['lon']}")
print(f"Full address: {location['display_name']}")
```

**Response**:
```python
{
    "lat": 12.9357,
    "lon": 77.6241,
    "display_name": "Koramangala, Bengaluru, Karnataka, India"
}
```

**Usage Policy**:
- Max 1 request per second
- Include User-Agent header
- Cache results
- Don't use for heavy batch processing

---

### B. Google Geocoding API
**Purpose**: Premium geocoding with high accuracy  
**Cost**: PAID ($5 per 1000 requests)  
**Coverage**: Global  
**Signup**: https://console.cloud.google.com/

---

## 🔧 Integration Examples

### Example 1: Fetch Population Data for Sites
```python
import pandas as pd
from src.api_integrations import fetch_opencellid_population_proxy

# Load candidate sites
sites = pd.read_csv('outputs/ranked_sites.csv')

# Get cell tower data as population proxy
bbox = {
    "north": sites['latitude'].max() + 0.1,
    "south": sites['latitude'].min() - 0.1,
    "east": sites['longitude'].max() + 0.1,
    "west": sites['longitude'].min() - 0.1,
}

cell_data = fetch_opencellid_population_proxy(bbox)

# Calculate cell tower density around each site (population proxy)
from scipy.spatial import cKDTree

tree = cKDTree(cell_data[['latitude', 'longitude']].values)
for idx, site in sites.iterrows():
    # Count towers within 1km
    nearby = tree.query_ball_point([site['latitude'], site['longitude']], r=0.01)
    sites.loc[idx, 'cell_tower_density'] = len(nearby)

sites.to_csv('outputs/sites_with_population.csv', index=False)
```

---

### Example 2: Find Existing EV Stations Near Sites
```python
from src.api_integrations import fetch_open_charge_map_stations
import geopandas as gpd

# Fetch existing EV stations
bbox = {"north": 13.15, "south": 12.85, "east": 77.75, "west": 77.45}
stations = fetch_open_charge_map_stations(bbox)

# Load candidate sites
sites = gpd.read_file('outputs/ranked_sites.csv')
sites = gpd.GeoDataFrame(
    sites,
    geometry=gpd.points_from_xy(sites['longitude'], sites['latitude']),
    crs='EPSG:4326'
)

# Find nearest existing station for each candidate site
from shapely.ops import nearest_points

for idx, site in sites.iterrows():
    distances = stations.geometry.distance(site.geometry)
    nearest_idx = distances.idxmin()
    nearest_station = stations.loc[nearest_idx]
    
    sites.loc[idx, 'nearest_station_name'] = nearest_station['name']
    sites.loc[idx, 'nearest_station_distance_km'] = distances[nearest_idx] * 111  # deg to km

sites.to_csv('outputs/sites_with_competition.csv', index=False)
```

---

### Example 3: Calculate Routes to Top Sites
```python
from src.api_integrations import geocode_location, get_route_osrm
import pandas as pd

# Load top sites
sites = pd.read_csv('outputs/ranked_sites.csv').head(10)

# User's current location
user_location = geocode_location("MG Road, Bangalore")
start = (user_location['lon'], user_location['lat'])

# Calculate routes to all top sites
routes = []
for idx, site in sites.iterrows():
    end = (site['longitude'], site['latitude'])
    route = get_route_osrm(start, end)
    
    if route:
        routes.append({
            'site_id': site['site_id'],
            'distance_km': route['distance'] / 1000,
            'duration_min': route['duration'] / 60,
        })

routes_df = pd.DataFrame(routes)
routes_df.to_csv('outputs/routes_to_top_sites.csv', index=False)
print(routes_df)
```

---

## 📦 Complete Integration Workflow

```python
from src.api_integrations import (
    fetch_all_real_world_data,
    fetch_open_charge_map_stations,
    geocode_location,
    get_route_osrm,
)

# 1. Define area of interest
bbox = {
    "north": 13.15,
    "south": 12.85,
    "east": 77.75,
    "west": 77.45,
}

# 2. Fetch all available data
data = fetch_all_real_world_data(bbox)

# 3. Get existing EV stations
ev_stations = fetch_open_charge_map_stations(bbox)
print(f"Found {len(ev_stations)} existing EV stations")

# 4. Geocode user location
location = geocode_location("Koramangala, Bangalore")

# 5. Calculate route to nearest station
if ev_stations is not None and len(ev_stations) > 0:
    nearest = ev_stations.iloc[0]
    route = get_route_osrm(
        (location['lon'], location['lat']),
        (nearest['longitude'], nearest['latitude'])
    )
    print(f"Route to nearest station: {route['distance']/1000:.2f} km")
```

---

## 🔑 API Key Management

### Environment Variables (Recommended)
```bash
# Add to ~/.bashrc or ~/.zshrc
export OPEN_CHARGE_MAP_KEY="your_key"
export ORS_API_KEY="your_key"
export OPENCELLID_KEY="your_key"
export DATA_GOV_IN_KEY="your_key"
export GOOGLE_MAPS_KEY="your_key"
```

### .env File (Alternative)
```bash
# Create .env file in project root
OPEN_CHARGE_MAP_KEY=your_key
ORS_API_KEY=your_key
OPENCELLID_KEY=your_key
DATA_GOV_IN_KEY=your_key
GOOGLE_MAPS_KEY=your_key
```

```python
# Load in Python
from dotenv import load_dotenv
load_dotenv()
```

---

## 📊 API Comparison Table

| API | Cost | Rate Limit | Coverage | Key Required | Best For |
|-----|------|------------|----------|--------------|----------|
| **Population** |
| WorldPop | Free | None | Global | No | High-res population |
| Census India | Free | None | India | No | Official census |
| OpenCellID | Free | 1000/day | Global | Yes | Real-time proxy |
| **EV Stations** |
| Open Charge Map | Free | 1000/day | Global | Optional | Station database |
| PlugShare | Free | No API | Global | N/A | Manual collection |
| **Routing** |
| OSRM | Free | None | Global | No | Fast routing |
| OpenRouteService | Free | 5000/day | Global | Yes | Advanced features |
| Google Maps | Paid | 40000/day | Global | Yes | Premium quality |
| **Geocoding** |
| Nominatim | Free | 1/sec | Global | No | Basic geocoding |
| Google Geocoding | Paid | 40000/day | Global | Yes | High accuracy |

---

## 🚨 Best Practices

1. **Cache API Responses**
   - Save fetched data to CSV
   - Avoid repeated API calls
   - Respect rate limits

2. **Error Handling**
   - Always check for None returns
   - Implement retry logic
   - Log API failures

3. **Rate Limiting**
   - Add delays between requests
   - Use batch endpoints when available
   - Monitor usage quotas

4. **Data Quality**
   - Validate coordinates
   - Check for missing values
   - Cross-reference multiple sources

5. **Cost Management**
   - Use free APIs first
   - Cache expensive API calls
   - Monitor billing alerts

---

## 📞 Support & Resources

- **Open Charge Map**: https://openchargemap.org/site/develop
- **OpenRouteService**: https://openrouteservice.org/dev/#/api-docs
- **OSRM**: http://project-osrm.org/docs/v5.24.0/api/
- **Nominatim**: https://nominatim.org/release-docs/latest/api/Overview/
- **WorldPop**: https://www.worldpop.org/methods/
- **Census India**: https://censusindia.gov.in/

---

## 🎯 Next Steps

1. Sign up for free API keys
2. Run `python test_apis.py` to verify setup
3. Integrate APIs into main workflow
4. Cache results for production use
5. Monitor API usage and costs

---

**Last Updated**: 2024
**Version**: 1.0
