# 🌍 Complete Real-World API Integration Guide

## ✅ What's Already Integrated

### 1. PositionStack API (YOUR API) ✅
- **Status:** INTEGRATED & WORKING
- **Location:** Map search in `main.py`
- **Usage:** Geocoding user searches
- **Free Tier:** 25,000 requests/month

---

## 🎯 Essential APIs You Need (Priority Order)

### Priority 1: MUST HAVE (Free & Easy)

#### 1. Open Charge Map API (EV Stations) 🔌
**Why:** Get existing EV charging stations to avoid competition

**Sign up:** https://openchargemap.org/site/develop  
**Cost:** FREE (unlimited with key)  
**Time:** 2 minutes

**How to get:**
1. Go to https://openchargemap.org/site/develop
2. Click "Register for API Key"
3. Fill form → Get API key instantly
4. Copy your API key

**How to use:**
```bash
# Set your API key
export OPEN_CHARGE_MAP_KEY="your_key_here"

# Run project
python main.py
```

**What it provides:**
- Existing EV station locations
- Number of charging points
- Station status (operational/planned)
- Usage type (public/private)

---

#### 2. OpenRouteService API (Routing) 🗺️
**Why:** Calculate routes and distances between locations

**Sign up:** https://openrouteservice.org/dev/#/signup  
**Cost:** FREE (5,000 requests/day)  
**Time:** 2 minutes

**How to get:**
1. Go to https://openrouteservice.org/dev/#/signup
2. Sign up with email
3. Verify email
4. Get API key from dashboard

**How to use:**
```bash
export ORS_API_KEY="your_key_here"
```

**What it provides:**
- Route calculation
- Distance matrix
- Isochrone analysis (reachability)
- Travel time estimation

---

### Priority 2: HIGHLY RECOMMENDED (Free)

#### 3. OpenCellID API (Population Proxy) 📱
**Why:** Cell tower density = population density

**Sign up:** https://opencellid.org/  
**Cost:** FREE (1,000 requests/day)  
**Time:** 3 minutes

**How to get:**
1. Go to https://opencellid.org/
2. Create account
3. Get API token from dashboard

**How to use:**
```bash
export OPENCELLID_KEY="your_key_here"
```

**What it provides:**
- Cell tower locations
- Population density proxy
- Real-time urban data

---

#### 4. Data.gov.in API (Census Data) 📊
**Why:** Official Indian government population data

**Sign up:** https://data.gov.in/  
**Cost:** FREE  
**Time:** 5 minutes

**How to get:**
1. Go to https://data.gov.in/
2. Register account
3. Request API key
4. Wait for approval (1-2 days)

**How to use:**
```bash
export DATA_GOV_IN_KEY="your_key_here"
```

**What it provides:**
- Census population data
- Ward-level demographics
- Official government statistics

---

### Priority 3: OPTIONAL (For Production)

#### 5. Google Maps API (Premium Features) 💰
**Why:** Best accuracy, real-time traffic

**Sign up:** https://console.cloud.google.com/  
**Cost:** PAID ($5 per 1,000 requests)  
**Time:** 10 minutes

**What it provides:**
- High-accuracy geocoding
- Real-time traffic data
- Street view integration
- Premium routing

---

## 📋 Quick Setup Checklist

### Step 1: Get Free API Keys (15 minutes total)

```bash
# 1. Open Charge Map (2 min)
✓ Sign up: https://openchargemap.org/site/develop
✓ Get API key
✓ export OPEN_CHARGE_MAP_KEY="your_key"

# 2. OpenRouteService (2 min)
✓ Sign up: https://openrouteservice.org/dev/#/signup
✓ Verify email
✓ export ORS_API_KEY="your_key"

# 3. OpenCellID (3 min)
✓ Sign up: https://opencellid.org/
✓ Get token
✓ export OPENCELLID_KEY="your_key"

# 4. Data.gov.in (5 min + wait)
✓ Sign up: https://data.gov.in/
✓ Request API key
✓ Wait for approval
✓ export DATA_GOV_IN_KEY="your_key"
```

### Step 2: Test APIs

```bash
cd ev_charging_site_selection
python test_apis.py
```

### Step 3: Run Project

```bash
python main.py
```

---

## 🔧 Where APIs Are Used in Your Project

### 1. PositionStack (Already Integrated) ✅
**File:** `main.py` (line ~200)
**Usage:** Map search functionality
```javascript
// User searches "Koramangala" → PositionStack geocodes it
const psUrl = `http://api.positionstack.com/v1/forward?access_key=25568ac20b49c89857f39f3505b6f7f5...`;
```

### 2. Open Charge Map (To Add)
**File:** `src/data_loader.py`
**Usage:** Fetch existing EV stations
```python
from api_integrations import fetch_open_charge_map_stations

# Get existing stations
bbox = {"north": 13.15, "south": 12.85, "east": 77.75, "west": 77.45}
existing_stations = fetch_open_charge_map_stations(bbox)

# Calculate competition score
for site in candidate_sites:
    nearest_station = find_nearest(site, existing_stations)
    site['competition_distance'] = calculate_distance(site, nearest_station)
```

### 3. OpenRouteService (To Add)
**File:** `src/dashboard.py`
**Usage:** Calculate routes to top sites
```python
from api_integrations import get_route_openrouteservice

# User clicks "Get Directions"
route = get_route_openrouteservice(
    (user_lon, user_lat),
    (site_lon, site_lat)
)
print(f"Distance: {route['distance']/1000:.2f} km")
print(f"Duration: {route['duration']/60:.1f} minutes")
```

### 4. OpenCellID (To Add)
**File:** `src/data_loader.py`
**Usage:** Population density proxy
```python
from api_integrations import fetch_opencellid_population_proxy

# Get cell tower data
cell_data = fetch_opencellid_population_proxy(bbox)

# Calculate population density
for site in sites:
    nearby_towers = count_towers_within_radius(site, cell_data, radius=1km)
    site['population_density'] = nearby_towers * 100  # proxy
```

---

## 💡 Integration Examples

### Example 1: Add Competition Analysis

Create `src/competition_analysis.py`:

```python
from api_integrations import fetch_open_charge_map_stations
import numpy as np

def analyze_competition(sites_gdf, bbox):
    """Analyze competition from existing EV stations"""
    
    # Fetch existing stations
    existing = fetch_open_charge_map_stations(bbox)
    
    if existing is None or len(existing) == 0:
        print("[Competition] No existing stations found")
        sites_gdf['competition_score'] = 1.0
        return sites_gdf
    
    print(f"[Competition] Found {len(existing)} existing stations")
    
    # Calculate distance to nearest competitor
    for idx, site in sites_gdf.iterrows():
        distances = existing.geometry.distance(site.geometry)
        min_distance = distances.min() * 111  # degrees to km
        
        # Score: higher distance = better (less competition)
        # 0 km = 0.0, 5+ km = 1.0
        competition_score = min(min_distance / 5.0, 1.0)
        sites_gdf.loc[idx, 'competition_score'] = competition_score
        sites_gdf.loc[idx, 'nearest_competitor_km'] = min_distance
    
    return sites_gdf
```

Add to `main.py`:
```python
from src.competition_analysis import analyze_competition

# After Step 1b (load_real_world_features)
gdf = analyze_competition(gdf, CITY_BOUNDS)

# Update final score to include competition
gdf["final_score"] = (
    0.5 * gdf["ahp_score"] + 
    0.3 * gdf["predicted_demand"] +
    0.2 * gdf["competition_score"]
)
```

---

### Example 2: Add Route Calculation

Create `src/route_calculator.py`:

```python
from api_integrations import get_route_openrouteservice, geocode_positionstack

def calculate_route_to_site(user_location, site_coords):
    """Calculate route from user to site"""
    
    # Geocode user location
    location = geocode_positionstack(user_location)
    if not location:
        return None
    
    # Calculate route
    route = get_route_openrouteservice(
        (location['lon'], location['lat']),
        (site_coords[0], site_coords[1])
    )
    
    if route:
        return {
            'distance_km': route['distance'] / 1000,
            'duration_min': route['duration'] / 60,
            'geometry': route['geometry']
        }
    
    return None

# Usage
route = calculate_route_to_site("MG Road, Bangalore", (77.6241, 12.9357))
print(f"Route: {route['distance_km']:.2f} km, {route['duration_min']:.1f} min")
```

---

### Example 3: Add Population Data

Update `src/data_loader.py`:

```python
from api_integrations import fetch_opencellid_population_proxy

def enrich_with_population(sites_gdf, bbox):
    """Enrich sites with real population data"""
    
    # Get cell tower data
    cell_data = fetch_opencellid_population_proxy(bbox)
    
    if cell_data is None:
        print("[Population] Using synthetic data")
        return sites_gdf
    
    print(f"[Population] Using {len(cell_data)} cell towers as proxy")
    
    # Count towers within 1km of each site
    for idx, site in sites_gdf.iterrows():
        distances = cell_data.geometry.distance(site.geometry) * 111  # to km
        nearby_count = (distances < 1.0).sum()
        
        # Normalize: 0-50 towers → 0.0-1.0
        sites_gdf.loc[idx, 'population_density'] = min(nearby_count / 50.0, 1.0)
    
    return sites_gdf
```

---

## 📊 API Usage Summary

| API | Status | Priority | Cost | Requests/Month | Integration Time |
|-----|--------|----------|------|----------------|------------------|
| PositionStack | ✅ Done | High | Free | 25,000 | Done |
| Open Charge Map | ⏳ Pending | High | Free | Unlimited | 5 min |
| OpenRouteService | ⏳ Pending | High | Free | 150,000 | 5 min |
| OpenCellID | ⏳ Pending | Medium | Free | 30,000 | 5 min |
| Data.gov.in | ⏳ Pending | Medium | Free | Varies | 1-2 days |
| Google Maps | ⏳ Optional | Low | Paid | Pay-per-use | 10 min |

---

## 🚀 Next Steps (Action Plan)

### Today (30 minutes):
1. ✅ Sign up for Open Charge Map
2. ✅ Sign up for OpenRouteService
3. ✅ Sign up for OpenCellID
4. ✅ Set environment variables
5. ✅ Run `python test_apis.py`

### Tomorrow:
1. ✅ Sign up for Data.gov.in (wait for approval)
2. ✅ Add competition analysis
3. ✅ Add route calculation
4. ✅ Test with real data

### This Week:
1. ✅ Integrate all APIs into main workflow
2. ✅ Add API usage monitoring
3. ✅ Implement caching
4. ✅ Deploy to production

---

## 📞 Support & Resources

- **PositionStack:** https://positionstack.com/documentation
- **Open Charge Map:** https://openchargemap.org/site/develop/api
- **OpenRouteService:** https://openrouteservice.org/dev/#/api-docs
- **OpenCellID:** https://opencellid.org/
- **Data.gov.in:** https://data.gov.in/

---

## ✅ Summary

**Already Integrated:**
- ✅ PositionStack API (geocoding in map search)

**Need to Add (15 min setup):**
- ⏳ Open Charge Map (EV stations)
- ⏳ OpenRouteService (routing)
- ⏳ OpenCellID (population)

**Total Cost:** $0/month (all free tiers)

**Your project will have:**
- Real geocoding ✅
- Real EV station data ⏳
- Real routing ⏳
- Real population data ⏳
- Competition analysis ⏳
- Route calculation ⏳

All APIs are FREE and take 15 minutes to set up!
