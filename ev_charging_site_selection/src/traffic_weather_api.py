"""
TomTom Traffic & OpenWeatherMap Integration
Real-world traffic and weather data for EV site selection
"""

import requests
import pandas as pd
from datetime import datetime

# API Keys — set via environment variables or replace with your keys
import os
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY", "YOUR_TOMTOM_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_OPENWEATHER_API_KEY")


# ═══════════════════════════════════════════════════════════════════════════
# TOMTOM TRAFFIC API
# ═══════════════════════════════════════════════════════════════════════════

def get_tomtom_traffic_flow(lat, lon, zoom=15):
    """
    Get real-time traffic flow data from TomTom
    
    Args:
        lat: Latitude
        lon: Longitude
        zoom: Zoom level (10-22, higher = more detail)
    
    Returns:
        dict with traffic metrics
    """
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/{zoom}/json"
    
    params = {
        "key": TOMTOM_API_KEY,
        "point": f"{lat},{lon}",
        "unit": "KMPH"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "flowSegmentData" in data:
            flow = data["flowSegmentData"]
            
            # Extract traffic metrics
            current_speed = flow.get("currentSpeed", 0)
            free_flow_speed = flow.get("freeFlowSpeed", 50)
            current_travel_time = flow.get("currentTravelTime", 0)
            free_flow_travel_time = flow.get("freeFlowTravelTime", 0)
            confidence = flow.get("confidence", 0.5)
            
            # Calculate traffic congestion ratio (0 = free flow, 1 = heavy congestion)
            if free_flow_speed > 0:
                congestion_ratio = 1 - (current_speed / free_flow_speed)
            else:
                congestion_ratio = 0.5
            
            # Calculate traffic volume score (higher speed = higher volume capacity)
            traffic_volume_score = min(1.0, current_speed / 60)  # Normalize to 0-1
            
            return {
                "current_speed_kmh": current_speed,
                "free_flow_speed_kmh": free_flow_speed,
                "congestion_ratio": max(0, min(1, congestion_ratio)),
                "traffic_volume_score": traffic_volume_score,
                "current_travel_time_sec": current_travel_time,
                "confidence": confidence,
                "road_closure": flow.get("roadClosure", False)
            }
        
        return None
        
    except Exception as e:
        print(f"[TomTom] Traffic flow error: {e}")
        return None


def get_tomtom_traffic_incidents(lat, lon, radius_km=2):
    """
    Get traffic incidents (accidents, construction, etc.) near location
    
    Args:
        lat: Latitude
        lon: Longitude
        radius_km: Search radius in kilometers
    
    Returns:
        dict with incident data
    """
    url = "https://api.tomtom.com/traffic/services/5/incidentDetails"
    
    # Calculate bounding box
    lat_offset = radius_km / 111  # 1 degree lat ≈ 111 km
    lon_offset = radius_km / (111 * abs(lat))
    
    bbox = f"{lon - lon_offset},{lat - lat_offset},{lon + lon_offset},{lat + lat_offset}"
    
    params = {
        "key": TOMTOM_API_KEY,
        "bbox": bbox,
        "fields": "{incidents{type,geometry{type,coordinates},properties{iconCategory,magnitudeOfDelay,events{description,code}}}}"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "incidents" in data:
            incidents = data["incidents"]
            
            # Count incidents by severity
            incident_count = len(incidents)
            major_incidents = sum(1 for i in incidents if i.get("properties", {}).get("magnitudeOfDelay", 0) > 2)
            
            # Calculate incident impact score (0 = no incidents, 1 = many incidents)
            incident_impact = min(1.0, incident_count / 10)
            
            return {
                "total_incidents": incident_count,
                "major_incidents": major_incidents,
                "incident_impact_score": incident_impact,
                "has_road_closure": any(i.get("properties", {}).get("iconCategory") == 1 for i in incidents)
            }
        
        return {"total_incidents": 0, "major_incidents": 0, "incident_impact_score": 0, "has_road_closure": False}
        
    except Exception as e:
        print(f"[TomTom] Traffic incidents error: {e}")
        return {"total_incidents": 0, "major_incidents": 0, "incident_impact_score": 0, "has_road_closure": False}


# ═══════════════════════════════════════════════════════════════════════════
# OPENWEATHERMAP API
# ═══════════════════════════════════════════════════════════════════════════

def get_current_weather(lat, lon):
    """
    Get current weather conditions
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        dict with weather data
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "temperature_c": data["main"]["temp"],
            "feels_like_c": data["main"]["feels_like"],
            "humidity_percent": data["main"]["humidity"],
            "pressure_hpa": data["main"]["pressure"],
            "weather_condition": data["weather"][0]["main"],
            "weather_description": data["weather"][0]["description"],
            "wind_speed_ms": data["wind"]["speed"],
            "clouds_percent": data["clouds"]["all"],
            "visibility_m": data.get("visibility", 10000),
            "rain_1h_mm": data.get("rain", {}).get("1h", 0)
        }
        
    except Exception as e:
        print(f"[OpenWeather] Current weather error: {e}")
        return None


def get_weather_forecast(lat, lon, days=5):
    """
    Get weather forecast for next 5 days
    
    Args:
        lat: Latitude
        lon: Longitude
        days: Number of days (max 5 for free tier)
    
    Returns:
        dict with forecast data
    """
    url = "https://api.openweathermap.org/data/2.5/forecast"
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "list" in data:
            forecasts = data["list"]
            
            # Calculate average conditions
            temps = [f["main"]["temp"] for f in forecasts]
            rain_hours = sum(1 for f in forecasts if f.get("rain", {}).get("3h", 0) > 0)
            
            return {
                "avg_temp_c": sum(temps) / len(temps),
                "min_temp_c": min(temps),
                "max_temp_c": max(temps),
                "rainy_periods": rain_hours,
                "rain_probability": rain_hours / len(forecasts)
            }
        
        return None
        
    except Exception as e:
        print(f"[OpenWeather] Forecast error: {e}")
        return None


def get_air_quality(lat, lon):
    """
    Get air quality index (AQI)
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        dict with air quality data
    """
    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "list" in data and len(data["list"]) > 0:
            aqi_data = data["list"][0]
            
            return {
                "aqi": aqi_data["main"]["aqi"],  # 1=Good, 5=Very Poor
                "pm2_5": aqi_data["components"]["pm2_5"],
                "pm10": aqi_data["components"]["pm10"],
                "no2": aqi_data["components"]["no2"],
                "o3": aqi_data["components"]["o3"],
                "co": aqi_data["components"]["co"]
            }
        
        return None
        
    except Exception as e:
        print(f"[OpenWeather] Air quality error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# SITE ENRICHMENT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def enrich_with_traffic_data(gdf):
    """
    Enrich sites with real-time traffic data from TomTom
    
    Args:
        gdf: GeoDataFrame with candidate sites
    
    Returns:
        GeoDataFrame with traffic data added
    """
    print("[TomTom] Fetching real-time traffic data...")
    
    traffic_data = []
    incident_data = []
    
    for idx, row in gdf.iterrows():
        lat, lon = row.geometry.y, row.geometry.x
        
        # Get traffic flow
        traffic = get_tomtom_traffic_flow(lat, lon)
        traffic_data.append(traffic)
        
        # Get traffic incidents
        incidents = get_tomtom_traffic_incidents(lat, lon, radius_km=2)
        incident_data.append(incidents)
        
        if (idx + 1) % 5 == 0:
            print(f"[TomTom] Processed {idx + 1}/{len(gdf)} sites...")
    
    # Add to dataframe
    if traffic_data and traffic_data[0]:
        gdf["tomtom_current_speed"] = [t["current_speed_kmh"] if t else 30 for t in traffic_data]
        gdf["tomtom_congestion"] = [t["congestion_ratio"] if t else 0.5 for t in traffic_data]
        gdf["tomtom_traffic_volume"] = [t["traffic_volume_score"] if t else 0.5 for t in traffic_data]
        gdf["tomtom_confidence"] = [t["confidence"] if t else 0.5 for t in traffic_data]
        
        # Update existing traffic_volume with real data
        gdf["traffic_volume"] = gdf["tomtom_traffic_volume"] * 10000
    
    if incident_data:
        gdf["tomtom_incidents"] = [i["total_incidents"] for i in incident_data]
        gdf["tomtom_incident_impact"] = [i["incident_impact_score"] for i in incident_data]
    
    print(f"[TomTom] ✓ Enriched {len(gdf)} sites with traffic data")
    print(f"[TomTom]   Avg speed: {gdf['tomtom_current_speed'].mean():.1f} km/h")
    print(f"[TomTom]   Avg congestion: {gdf['tomtom_congestion'].mean():.3f}")
    print(f"[TomTom]   Avg incidents: {gdf['tomtom_incidents'].mean():.1f}")
    
    return gdf


def enrich_with_weather_data(gdf):
    """
    Enrich sites with weather and air quality data from OpenWeatherMap
    
    Args:
        gdf: GeoDataFrame with candidate sites
    
    Returns:
        GeoDataFrame with weather data added
    """
    print("[OpenWeather] Fetching weather and air quality data...")
    
    weather_data = []
    forecast_data = []
    aqi_data = []
    
    for idx, row in gdf.iterrows():
        lat, lon = row.geometry.y, row.geometry.x
        
        # Get current weather
        weather = get_current_weather(lat, lon)
        weather_data.append(weather)
        
        # Get forecast
        forecast = get_weather_forecast(lat, lon)
        forecast_data.append(forecast)
        
        # Get air quality
        aqi = get_air_quality(lat, lon)
        aqi_data.append(aqi)
        
        if (idx + 1) % 5 == 0:
            print(f"[OpenWeather] Processed {idx + 1}/{len(gdf)} sites...")
    
    # Add to dataframe
    if weather_data and weather_data[0]:
        gdf["weather_temp_c"] = [w["temperature_c"] if w else 25 for w in weather_data]
        gdf["weather_humidity"] = [w["humidity_percent"] if w else 60 for w in weather_data]
        gdf["weather_condition"] = [w["weather_condition"] if w else "Clear" for w in weather_data]
        gdf["weather_rain_1h"] = [w["rain_1h_mm"] if w else 0 for w in weather_data]
        gdf["weather_wind_speed"] = [w["wind_speed_ms"] if w else 3 for w in weather_data]
    
    if forecast_data and forecast_data[0]:
        gdf["weather_avg_temp"] = [f["avg_temp_c"] if f else 25 for f in forecast_data]
        gdf["weather_rain_prob"] = [f["rain_probability"] if f else 0.2 for f in forecast_data]
    
    if aqi_data and aqi_data[0]:
        gdf["weather_aqi"] = [a["aqi"] if a else 3 for a in aqi_data]
        gdf["weather_pm25"] = [a["pm2_5"] if a else 50 for a in aqi_data]
    
    # Calculate weather suitability score (0-1)
    # Good weather = higher EV usage
    gdf["weather_suitability"] = 1.0
    if "weather_temp_c" in gdf.columns:
        # Optimal temp: 15-30°C
        gdf["weather_suitability"] *= gdf["weather_temp_c"].apply(
            lambda t: 1.0 if 15 <= t <= 30 else 0.7 if 10 <= t <= 35 else 0.5
        )
    if "weather_rain_prob" in gdf.columns:
        # Less rain = better
        gdf["weather_suitability"] *= (1 - gdf["weather_rain_prob"] * 0.3)
    
    print(f"[OpenWeather] ✓ Enriched {len(gdf)} sites with weather data")
    print(f"[OpenWeather]   Avg temperature: {gdf['weather_temp_c'].mean():.1f}°C")
    print(f"[OpenWeather]   Avg humidity: {gdf['weather_humidity'].mean():.1f}%")
    print(f"[OpenWeather]   Avg AQI: {gdf['weather_aqi'].mean():.1f}")
    print(f"[OpenWeather]   Avg suitability: {gdf['weather_suitability'].mean():.3f}")
    
    return gdf


def enrich_with_all_realworld_data(gdf):
    """
    Enrich sites with both traffic and weather data
    
    Args:
        gdf: GeoDataFrame with candidate sites
    
    Returns:
        GeoDataFrame with all real-world data
    """
    print("\n" + "="*70)
    print("  ENRICHING WITH REAL-WORLD DATA")
    print("="*70 + "\n")
    
    # Add traffic data
    gdf = enrich_with_traffic_data(gdf)
    
    print()  # Blank line
    
    # Add weather data
    gdf = enrich_with_weather_data(gdf)
    
    print("\n" + "="*70)
    print("  REAL-WORLD DATA ENRICHMENT COMPLETE")
    print("="*70 + "\n")
    
    return gdf


if __name__ == "__main__":
    # Test the APIs
    print("Testing TomTom and OpenWeatherMap APIs...\n")
    
    # Test location: MG Road, Bangalore
    lat, lon = 12.9756, 77.6069
    
    print("="*70)
    print("TOMTOM TRAFFIC API TEST")
    print("="*70)
    
    traffic = get_tomtom_traffic_flow(lat, lon)
    if traffic:
        print(f"✓ Current Speed: {traffic['current_speed_kmh']:.1f} km/h")
        print(f"✓ Free Flow Speed: {traffic['free_flow_speed_kmh']:.1f} km/h")
        print(f"✓ Congestion Ratio: {traffic['congestion_ratio']:.3f}")
        print(f"✓ Traffic Volume Score: {traffic['traffic_volume_score']:.3f}")
    else:
        print("✗ Traffic flow test failed")
    
    incidents = get_tomtom_traffic_incidents(lat, lon)
    print(f"\n✓ Total Incidents: {incidents['total_incidents']}")
    print(f"✓ Major Incidents: {incidents['major_incidents']}")
    
    print("\n" + "="*70)
    print("OPENWEATHERMAP API TEST")
    print("="*70)
    
    weather = get_current_weather(lat, lon)
    if weather:
        print(f"✓ Temperature: {weather['temperature_c']:.1f}°C")
        print(f"✓ Humidity: {weather['humidity_percent']}%")
        print(f"✓ Condition: {weather['weather_description']}")
        print(f"✓ Wind Speed: {weather['wind_speed_ms']:.1f} m/s")
    else:
        print("✗ Weather test failed")
    
    forecast = get_weather_forecast(lat, lon)
    if forecast:
        print(f"\n✓ 5-Day Avg Temp: {forecast['avg_temp_c']:.1f}°C")
        print(f"✓ Rain Probability: {forecast['rain_probability']*100:.1f}%")
    
    aqi = get_air_quality(lat, lon)
    if aqi:
        print(f"\n✓ Air Quality Index: {aqi['aqi']} (1=Good, 5=Very Poor)")
        print(f"✓ PM2.5: {aqi['pm2_5']:.1f} μg/m³")
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)
