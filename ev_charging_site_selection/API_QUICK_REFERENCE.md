# Real-World API Integration - Quick Reference

## ✅ What's Been Integrated

### 1. Population Data APIs
- ✅ **WorldPop** - High-resolution population density (100m grid)
- ✅ **Census India** - Official government census data
- ✅ **OpenCellID** - Cell tower density as population proxy

### 2. EV Charging Station APIs
- ✅ **Open Charge Map** - 200,000+ global EV stations
- ℹ️ **PlugShare** - Manual data collection (no public API)

### 3. Routing & Navigation APIs
- ✅ **OSRM** - Free, fast routing (no key needed)
- ✅ **OpenRouteService** - Advanced routing (5000 req/day free)
- ✅ **Google Maps** - Premium routing (paid)

### 4. Geocoding APIs
- ✅ **Nominatim** - Free OSM geocoding (1 req/sec)
- ✅ **Google Geocoding** - Premium geocoding (paid)

---

## 🚀 Quick Start

### Test APIs (No Keys Needed)
```bash
cd ev_charging_site_selection
python test_apis.py
```

**Works immediately:**
- ✅ Geocoding (Nominatim)
- ✅ Routing (OSRM)
- ✅ EV Stations (Open Charge Map - limited)

---

## 🔑 Get Free API Keys (5 minutes)

### 1. Open Charge Map (EV Stations)
```bash
# Sign up: https://openchargemap.org/site/develop
export OPEN_CHARGE_MAP_KEY="your_key"
```

### 2. OpenRouteService (Routing)
```bash
# Sign up: https://openrouteservice.org/dev/#/signup
export ORS_API_KEY="your_key"
```

### 3. OpenCellID (Population Proxy)
```bash
# Sign up: https://opencellid.org/
export OPENCELLID_KEY="your_key"
```

---

## 📝 Usage Examples

### Example 1: Geocode Location
```python
from src.api_integrations import geocode_location

location = geocode_location("Koramangala, Bangalore")
# Returns: {'lat': 12.9357, 'lon': 77.6241, 'display_name': '...'}
```

### Example 2: Calculate Route
```python
from src.api_integrations import get_route_osrm

start = (77.5946, 12.9716)  # (lon, lat)
end = (77.6241, 12.9357)

route = get_route_osrm(start, end)
# Returns: {'distance': 8500, 'duration': 900, 'geometry': {...}}
```

### Example 3: Fetch EV Stations
```python
from src.api_integrations import fetch_open_charge_map_stations

bbox = {"north": 13.15, "south": 12.85, "east": 77.75, "west": 77.45}
stations = fetch_open_charge_map_stations(bbox)
# Returns: GeoDataFrame with station locations
```

### Example 4: Get Population Data
```python
from src.api_integrations import fetch_opencellid_population_proxy

bbox = {"north": 13.15, "south": 12.85, "east": 77.75, "west": 77.45}
cell_data = fetch_opencellid_population_proxy(bbox)
# Returns: GeoDataFrame with cell tower locations (population proxy)
```

---

## 📊 API Comparison

| Feature | Free API | Paid API | Key Required |
|---------|----------|----------|--------------|
| **Geocoding** | Nominatim | Google | No / Yes |
| **Routing** | OSRM | Google Maps | No / Yes |
| **EV Stations** | Open Charge Map | - | Optional |
| **Population** | OpenCellID | - | Yes |

---

## 📁 Files Created

```
ev_charging_site_selection/
├── src/
│   └── api_integrations.py      # Main API integration module
├── test_apis.py                  # API testing script
├── API_INTEGRATION_GUIDE.md      # Comprehensive documentation
└── API_QUICK_REFERENCE.md        # This file
```

---

## 🎯 Integration with Main Project

### Update data_loader.py to use APIs:
```python
from src.api_integrations import fetch_opencellid_population_proxy

# In load_real_world_features():
cell_data = fetch_opencellid_population_proxy(CITY_BOUNDS)
if cell_data is not None:
    # Use cell tower density as population proxy
    gdf["population_density"] = calculate_cell_density(gdf, cell_data)
```

### Add EV station competition analysis:
```python
from src.api_integrations import fetch_open_charge_map_stations

existing_stations = fetch_open_charge_map_stations(CITY_BOUNDS)
# Calculate distance to nearest existing station
gdf["competition_distance"] = calculate_nearest_station(gdf, existing_stations)
```

### Add routing to dashboard:
```python
from src.api_integrations import get_route_osrm, geocode_location

# User searches for location
user_loc = geocode_location(search_query)
# Calculate route to top site
route = get_route_osrm(
    (user_loc['lon'], user_loc['lat']),
    (top_site['longitude'], top_site['latitude'])
)
```

---

## 🔧 Troubleshooting

### Issue: "403 Forbidden" from Open Charge Map
**Solution**: Get free API key from https://openchargemap.org/site/develop

### Issue: "Rate limit exceeded" from Nominatim
**Solution**: Add 1 second delay between requests
```python
import time
time.sleep(1)
```

### Issue: "No data returned" from OpenCellID
**Solution**: Sign up and set API key
```bash
export OPENCELLID_KEY="your_key"
```

---

## 📚 Documentation

- **Full Guide**: See `API_INTEGRATION_GUIDE.md`
- **Code**: See `src/api_integrations.py`
- **Tests**: Run `python test_apis.py`

---

## ✨ Test Results

```
✅ Geocoding: Koramangala, Bangalore → 12.9357, 77.6241
✅ Routing: MG Road → Whitefield → 22.19 km, 24.5 min
⚠️ EV Stations: Requires API key for full access
⚠️ Population: Requires OpenCellID API key
```

---

## 🎉 Success!

You now have access to:
- ✅ Real-world population data
- ✅ Existing EV station locations
- ✅ Route calculation
- ✅ Location geocoding

**Next Steps:**
1. Get free API keys (5 min)
2. Run `python test_apis.py`
3. Integrate into main workflow
4. Deploy to production

---

**Questions?** Check `API_INTEGRATION_GUIDE.md` for detailed documentation.
