# Open Charge Map API - Setup Guide

## ✅ You've Signed Up! Now Let's Integrate

### Step 1: Get Your API Key

1. Go to https://openchargemap.org/
2. Log in to your account
3. Go to your profile/dashboard
4. Find your API key (looks like: `abc123def456...`)
5. Copy it

### Step 2: Test Your API Key

**Option A: Quick Test (Recommended)**

1. Open `test_open_charge_map.py`
2. Replace line 10:
   ```python
   OPEN_CHARGE_MAP_KEY = "YOUR_API_KEY"  # Replace with your actual key
   ```
   With:
   ```python
   OPEN_CHARGE_MAP_KEY = "your_actual_key_here"
   ```
3. Run:
   ```bash
   python test_open_charge_map.py
   ```

**Option B: Set Environment Variable**

```bash
# Set your API key
export OPEN_CHARGE_MAP_KEY="your_actual_key_here"

# Test it
python test_apis.py
```

### Step 3: Integrate into Main Project

Once your API key works, add it to your project:

**Method 1: Environment Variable (Recommended)**

```bash
# Add to ~/.bashrc or ~/.zshrc
export OPEN_CHARGE_MAP_KEY="your_actual_key_here"

# Reload
source ~/.bashrc  # or source ~/.zshrc
```

**Method 2: Direct in Code**

Edit `src/api_integrations.py` line 23:
```python
"api_key": os.getenv("OPEN_CHARGE_MAP_KEY", "your_actual_key_here"),
```

### Step 4: Run Your Project

```bash
python main.py
```

---

## 🎯 What You'll Get

### Real EV Station Data

The API will fetch existing EV charging stations in Bangalore:

```python
from src.api_integrations import fetch_open_charge_map_stations

bbox = {"north": 13.15, "south": 12.85, "east": 77.75, "west": 77.45}
stations = fetch_open_charge_map_stations(bbox)

# Returns:
# - Station name
# - Location (lat/lon)
# - Address
# - Number of charging points
# - Status (operational/planned)
# - Usage type (public/private)
```

### Competition Analysis

Use this data to:
- Avoid placing new sites too close to competitors
- Identify underserved areas
- Calculate market saturation

---

## 📊 Example Output

```
✅ Found 45 EV charging stations in Bangalore

Top Stations:
1. Tata Power Charging Station
   📍 Koramangala, Bangalore
   🔌 4 charging points
   📊 Operational
   
2. Ather Grid
   📍 Indiranagar, Bangalore
   🔌 2 charging points
   📊 Operational
```

---

## 🔧 Add Competition Analysis

Create `src/competition_analysis.py`:

```python
from api_integrations import fetch_open_charge_map_stations

def analyze_competition(candidate_sites, bbox):
    """Analyze competition from existing EV stations"""
    
    # Fetch existing stations
    existing = fetch_open_charge_map_stations(bbox)
    
    if existing is None or len(existing) == 0:
        print("[Competition] No existing stations found")
        candidate_sites['competition_score'] = 1.0
        return candidate_sites
    
    print(f"[Competition] Found {len(existing)} existing stations")
    
    # Calculate distance to nearest competitor
    for idx, site in candidate_sites.iterrows():
        distances = existing.geometry.distance(site.geometry)
        min_distance = distances.min() * 111  # degrees to km
        
        # Score: 0 km = 0.0, 5+ km = 1.0
        competition_score = min(min_distance / 5.0, 1.0)
        candidate_sites.loc[idx, 'competition_score'] = competition_score
        candidate_sites.loc[idx, 'nearest_competitor_km'] = min_distance
    
    return candidate_sites
```

Add to `main.py`:

```python
from src.competition_analysis import analyze_competition

# After Step 1b (load_real_world_features)
CITY_BOUNDS = {"north": 13.15, "south": 12.85, "east": 77.75, "west": 77.45}
gdf = analyze_competition(gdf, CITY_BOUNDS)

# Update final score
gdf["final_score"] = (
    0.5 * gdf["ahp_score"] + 
    0.3 * gdf["predicted_demand"] +
    0.2 * gdf["competition_score"]
)
```

---

## 🚀 Quick Start Checklist

- [ ] Get API key from https://openchargemap.org/
- [ ] Edit `test_open_charge_map.py` with your key
- [ ] Run `python test_open_charge_map.py`
- [ ] Verify it finds EV stations
- [ ] Set environment variable: `export OPEN_CHARGE_MAP_KEY="your_key"`
- [ ] Run `python main.py`
- [ ] Add competition analysis (optional)

---

## 📞 Support

- **API Docs:** https://openchargemap.org/site/develop/api
- **Dashboard:** https://openchargemap.org/
- **Support:** https://openchargemap.org/site/develop/contact

---

## ✅ Summary

Your Open Charge Map API will provide:
- ✅ Real EV station locations in Bangalore
- ✅ Station details (charging points, status)
- ✅ Competition analysis data
- ✅ Market saturation insights

**Cost:** FREE (unlimited with API key)  
**Setup Time:** 5 minutes  
**Value:** Avoid competition, find underserved areas
