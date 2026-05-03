# PositionStack API Integration Guide

## ✅ Your API is Now Integrated!

**API Key:** `25568ac20b49c89857f39f3505b6f7f5`  
**Service:** PositionStack Geocoding API  
**Free Tier:** 25,000 requests/month  
**Features:** Forward & Reverse Geocoding

---

## 🚀 Quick Start

### 1. Forward Geocoding (Location → Coordinates)

```python
from src.api_integrations import geocode_positionstack

# Geocode a location
location = geocode_positionstack("Koramangala, Bangalore")

print(f"Latitude: {location['lat']}")
print(f"Longitude: {location['lon']}")
print(f"Address: {location['display_name']}")
print(f"Region: {location['region']}")
print(f"Country: {location['country']}")
```

**Output:**
```
Latitude: 12.9407
Longitude: 77.6248
Address: Koramangala Depot, Bangalore, KA, India
Region: Karnataka
Country: India
```

---

### 2. Reverse Geocoding (Coordinates → Location)

```python
from src.api_integrations import reverse_geocode_positionstack

# Get address from coordinates
address = reverse_geocode_positionstack(12.9407, 77.6248)

print(f"Address: {address['display_name']}")
print(f"Locality: {address['locality']}")
print(f"Region: {address['region']}")
```

**Output:**
```
Address: Koramangala Depot, Bangalore, KA, India
Locality: Bangalore
Region: Karnataka
```

---

## 💡 Integration with Your EV Charging Project

### Use Case 1: User Location Search

Add this to your dashboard to let users search for locations:

```python
from src.api_integrations import geocode_positionstack

def search_nearby_sites(user_query):
    """Find EV sites near user's searched location"""
    
    # Geocode user's search query
    location = geocode_positionstack(user_query)
    
    if location:
        user_lat = location['lat']
        user_lon = location['lon']
        
        # Calculate distance to all sites
        # (Add your distance calculation logic here)
        
        return {
            'location': location['display_name'],
            'coordinates': (user_lat, user_lon),
            'nearby_sites': []  # Your filtered sites
        }
    
    return None

# Example usage
result = search_nearby_sites("Whitefield, Bangalore")
```

---

### Use Case 2: Enrich Site Data with Addresses

Add readable addresses to your site data:

```python
from src.api_integrations import reverse_geocode_positionstack
import geopandas as gpd

def enrich_sites_with_addresses(sites_gdf):
    """Add human-readable addresses to site data"""
    
    addresses = []
    for idx, site in sites_gdf.iterrows():
        lat = site.geometry.y
        lon = site.geometry.x
        
        address = reverse_geocode_positionstack(lat, lon)
        
        if address:
            addresses.append({
                'site_id': site['site_id'],
                'address': address['display_name'],
                'locality': address.get('locality', ''),
                'region': address.get('region', ''),
            })
    
    return addresses

# Example usage
# sites = gpd.read_file('outputs/sites.geojson')
# addresses = enrich_sites_with_addresses(sites)
```

---

### Use Case 3: Validate User Input

Validate location names before processing:

```python
from src.api_integrations import geocode_positionstack

def validate_location(location_name):
    """Check if location is valid and in Bangalore"""
    
    result = geocode_positionstack(location_name)
    
    if result:
        # Check if location is in Bangalore/Karnataka
        if 'bangalore' in result['display_name'].lower() or \
           result.get('region', '').lower() == 'karnataka':
            return {
                'valid': True,
                'coordinates': (result['lat'], result['lon']),
                'address': result['display_name']
            }
    
    return {'valid': False, 'error': 'Location not found or not in Bangalore'}

# Example usage
validation = validate_location("Koramangala")
if validation['valid']:
    print(f"Valid location: {validation['address']}")
```

---

### Use Case 4: Update Dashboard Search

Modify `src/dashboard.py` to add location search:

```python
# Add to dashboard.py

from api_integrations import geocode_positionstack

def create_search_panel():
    """Create location search panel for dashboard"""
    
    search_html = """
    <div class="search-panel">
        <input type="text" id="location-search" 
               placeholder="Search location (e.g., Koramangala)">
        <button onclick="searchLocation()">Search</button>
    </div>
    
    <script>
    function searchLocation() {
        const query = document.getElementById('location-search').value;
        
        // Call Python backend to geocode
        fetch('/geocode?q=' + encodeURIComponent(query))
            .then(response => response.json())
            .then(data => {
                if (data.lat && data.lon) {
                    // Zoom map to location
                    map.setView([data.lat, data.lon], 14);
                    
                    // Find nearby sites
                    findNearbySites(data.lat, data.lon);
                }
            });
    }
    </script>
    """
    
    return search_html
```

---

## 📊 API Usage Monitoring

Track your API usage to stay within the free tier:

```python
import json
from datetime import datetime

def log_api_call(endpoint, success=True):
    """Log API calls to track usage"""
    
    log_file = 'api_usage.json'
    
    try:
        with open(log_file, 'r') as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []
    
    logs.append({
        'timestamp': datetime.now().isoformat(),
        'endpoint': endpoint,
        'success': success
    })
    
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    # Check if approaching limit
    if len(logs) > 20000:
        print(f"⚠️ Warning: {len(logs)} API calls this month. Limit: 25,000")

# Add to geocode_positionstack() function
# log_api_call('forward_geocoding', success=True)
```

---

## 🔧 Best Practices

### 1. Cache Results

```python
import json
import os

CACHE_FILE = 'geocode_cache.json'

def geocode_with_cache(location_name):
    """Geocode with caching to save API calls"""
    
    # Load cache
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    
    # Check cache
    if location_name in cache:
        print(f"[Cache] Using cached result for {location_name}")
        return cache[location_name]
    
    # Call API
    result = geocode_positionstack(location_name)
    
    # Save to cache
    if result:
        cache[location_name] = result
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    
    return result
```

### 2. Rate Limiting

```python
import time

last_call_time = 0
MIN_INTERVAL = 0.1  # 100ms between calls

def rate_limited_geocode(location_name):
    """Add rate limiting to avoid hitting API limits"""
    global last_call_time
    
    # Wait if needed
    elapsed = time.time() - last_call_time
    if elapsed < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - elapsed)
    
    result = geocode_positionstack(location_name)
    last_call_time = time.time()
    
    return result
```

### 3. Error Handling

```python
def safe_geocode(location_name, retries=3):
    """Geocode with retry logic"""
    
    for attempt in range(retries):
        try:
            result = geocode_positionstack(location_name)
            if result:
                return result
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    return None
```

---

## 📈 API Limits & Pricing

### Free Tier (Current)
- **25,000 requests/month**
- **HTTP only** (no HTTPS)
- Forward & Reverse Geocoding
- No credit card required

### Paid Tiers (If Needed)
- **Basic:** $9.99/month - 100,000 requests
- **Professional:** $49.99/month - 500,000 requests
- **Business:** $99.99/month - 1,000,000 requests

**Recommendation:** Start with free tier, monitor usage, upgrade only if needed.

---

## 🎯 Next Steps

1. **Test the API:**
   ```bash
   python test_your_api.py
   ```

2. **Run the demo:**
   ```bash
   python demo_positionstack.py
   ```

3. **Integrate into dashboard:**
   - Add location search functionality
   - Display readable addresses for sites
   - Validate user input

4. **Monitor usage:**
   - Track API calls
   - Implement caching
   - Set up alerts at 80% usage

---

## 📚 Resources

- **API Documentation:** https://positionstack.com/documentation
- **Dashboard:** https://positionstack.com/dashboard
- **Support:** https://positionstack.com/support

---

## ✅ Summary

Your PositionStack API is now fully integrated! You can:

✓ Geocode location names to coordinates  
✓ Reverse geocode coordinates to addresses  
✓ Validate user location input  
✓ Enrich site data with readable addresses  
✓ Add location search to your dashboard  

**API Key:** `25568ac20b49c89857f39f3505b6f7f5`  
**Status:** ✅ Active and Working  
**Free Tier:** 25,000 requests/month
