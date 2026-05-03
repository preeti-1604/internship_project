import os
import folium
from src.gis_filtering import run_gis_filtering
from src.data_loader import load_real_world_features, print_data_guide
from src.ahp_scoring import run_ahp_scoring, compute_ahp_weights, compute_consistency_ratio, PAIRWISE_MATRIX
from src.demand_forecasting import run_demand_forecasting
from src.competition_analysis import analyze_competition, get_underserved_areas, save_competition_report
from src.traffic_weather_api import enrich_with_all_realworld_data
from src.visualizations import (
    ahp_weights_chart, score_distribution_chart, scatter_ahp_vs_demand,
    feature_importance_chart, top_sites_chart, radar_chart,
)
from src.dashboard import build_dashboard

OUTPUT_DIR     = "outputs"
MAP_PATH       = "outputs/maps/ev_sites_map.html"
DASHBOARD_PATH = "outputs/dashboard.html"
CSV_PATH       = "outputs/ranked_sites.csv"

# Bangalore bounding box
CITY_BOUNDS = {
    "north": 13.15,
    "south": 12.85,
    "east": 77.75,
    "west": 77.45,
}


def build_folium_map(gdf, top_n=10):
    import json
    center = [gdf.geometry.y.mean(), gdf.geometry.x.mean()]
    m = folium.Map(location=center, zoom_start=12, tiles="CartoDB positron")
    top_sites = set(gdf.nsmallest(top_n, "final_rank")["site_id"])

    # Build site data as JSON for JS search panel
    sites_data = []
    for _, row in gdf.iterrows():
        is_top = row["site_id"] in top_sites
        sites_data.append({
            "id":       row["site_id"],
            "lat":      round(row.geometry.y, 6),
            "lon":      round(row.geometry.x, 6),
            "ahp":      round(float(row["ahp_score"]), 3),
            "demand":   round(float(row["predicted_demand"]), 3),
            "score":    round(float(row["final_score"]), 3),
            "rank":     int(row["final_rank"]),
            "is_top":   is_top,
        })

    for s in sites_data:
        color  = "#ef4444" if s["is_top"] else "#3b82f6"
        radius = 10 if s["is_top"] else 6
        folium.CircleMarker(
            location=[s["lat"], s["lon"]],
            radius=radius,
            color=color,
            fill=True,
            fill_opacity=0.85,
            popup=folium.Popup(
                f"<div style='font-family:sans-serif;min-width:180px;padding:4px'>"
                f"<b style='font-size:1.05em;color:#1e293b'>{s['id']}</b>"
                f"{'<br><span style=\"color:#d97706;font-weight:700\">⭐ Top 10 Site</span>' if s['is_top'] else ''}"
                f"<hr style='margin:6px 0;border-color:#e2e8f0'>"
                f"<table style='font-size:0.85em;width:100%'>"
                f"<tr><td><b>Lat / Lon</b></td><td>{s['lat']}, {s['lon']}</td></tr>"
                f"<tr><td><b>AHP Score</b></td><td>{s['ahp']}</td></tr>"
                f"<tr><td><b>Demand</b></td><td>{s['demand']}</td></tr>"
                f"<tr><td><b>Final Score</b></td><td><b style='color:#16a34a'>{s['score']}</b></td></tr>"
                f"<tr><td><b>Rank</b></td><td><b>#{s['rank']}</b></td></tr>"
                f"</table></div>",
                max_width=240,
            ),
            tooltip=f"{s['id']} | Rank #{s['rank']} | Score {s['score']}",
        ).add_to(m)

    # Inject search UI + nearby-sites panel as custom HTML
    sites_json = json.dumps(sites_data)
    search_html = f"""
    <style>
      #ev-search-box {{
        position: absolute; top: 16px; left: 50%; transform: translateX(-50%);
        z-index: 9999; display: flex; gap: 8px; align-items: center;
        background: #0f172a; border: 1px solid #334155; border-radius: 12px;
        padding: 10px 14px; box-shadow: 0 4px 24px rgba(0,0,0,0.5);
        min-width: 380px;
      }}
      #ev-search-box input {{
        flex: 1; background: #1e293b; border: 1px solid #475569; border-radius: 8px;
        color: #e2e8f0; padding: 8px 12px; font-size: 0.9rem; outline: none;
      }}
      #ev-search-box input::placeholder {{ color: #64748b; }}
      #ev-search-box button {{
        background: #3b82f6; color: #fff; border: none; border-radius: 8px;
        padding: 8px 16px; cursor: pointer; font-size: 0.88rem; font-weight: 600;
        white-space: nowrap;
      }}
      #ev-search-box button:hover {{ background: #2563eb; }}
      #radius-select {{
        background: #1e293b; border: 1px solid #475569; border-radius: 8px;
        color: #e2e8f0; padding: 8px 8px; font-size: 0.85rem; cursor: pointer;
      }}
      #ev-results-panel {{
        position: absolute; top: 76px; right: 16px; z-index: 9998;
        background: #0f172a; border: 1px solid #334155; border-radius: 12px;
        width: 320px; max-height: 480px; overflow-y: auto;
        box-shadow: 0 4px 24px rgba(0,0,0,0.5); display: none;
      }}
      #ev-results-panel .panel-header {{
        padding: 12px 16px; border-bottom: 1px solid #334155;
        font-size: 0.85rem; color: #94a3b8; display: flex;
        justify-content: space-between; align-items: center;
        position: sticky; top: 0; background: #0f172a;
      }}
      #ev-results-panel .panel-header b {{ color: #e2e8f0; font-size: 0.95rem; }}
      #ev-results-panel .close-btn {{
        cursor: pointer; color: #64748b; font-size: 1.1rem; line-height: 1;
        background: none; border: none; padding: 0;
      }}
      #ev-results-panel .close-btn:hover {{ color: #e2e8f0; }}
      .ev-site-card {{
        padding: 12px 16px; border-bottom: 1px solid #1e293b;
        cursor: pointer; transition: background 0.15s;
      }}
      .ev-site-card:hover {{ background: #1e293b; }}
      .ev-site-card .site-name {{
        font-weight: 700; color: #3b82f6; font-size: 0.92rem;
        display: flex; justify-content: space-between; align-items: center;
      }}
      .ev-site-card .site-coords {{
        font-size: 0.75rem; color: #64748b; margin-top: 2px; font-family: monospace;
      }}
      .ev-site-card .site-scores {{
        display: flex; gap: 10px; margin-top: 6px; font-size: 0.78rem;
      }}
      .ev-site-card .score-pill {{
        background: #1e293b; border: 1px solid #334155; border-radius: 6px;
        padding: 2px 8px; color: #94a3b8;
      }}
      .ev-site-card .score-pill b {{ color: #e2e8f0; }}
      .top-badge {{
        background: #92400e; color: #fcd34d; font-size: 0.7rem;
        padding: 1px 6px; border-radius: 4px; font-weight: 700;
      }}
      .dist-badge {{
        background: #1e3a5f; color: #93c5fd; font-size: 0.7rem;
        padding: 1px 6px; border-radius: 4px;
      }}
      #ev-search-status {{
        position: absolute; top: 76px; left: 50%; transform: translateX(-50%);
        z-index: 9997; background: #0f172a; border: 1px solid #334155;
        border-radius: 8px; padding: 8px 16px; font-size: 0.82rem;
        color: #94a3b8; display: none; white-space: nowrap;
      }}
    </style>

    <div id="ev-search-box">
      <input id="ev-location-input" type="text"
             placeholder="Search location (e.g. Koramangala, Whitefield…)"
             onkeydown="if(event.key==='Enter') searchLocation()" />
      <select id="radius-select">
        <option value="2">2 km</option>
        <option value="5" selected>5 km</option>
        <option value="10">10 km</option>
        <option value="20">20 km</option>
      </select>
      <button onclick="searchLocation()">🔍 Search</button>
    </div>
    <div id="ev-search-status"></div>
    <div id="ev-results-panel">
      <div class="panel-header">
        <div><b id="panel-title">Nearby EV Sites</b><br><span id="panel-subtitle"></span></div>
        <button class="close-btn" onclick="closePanel()">✕</button>
      </div>
      <div id="panel-body"></div>
    </div>

    <script>
      const EV_SITES = {sites_json};
      let searchCircle = null;
      let searchMarker = null;

      function haversine(lat1, lon1, lat2, lon2) {{
        const R = 6371;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2)**2 +
                  Math.cos(lat1*Math.PI/180) * Math.cos(lat2*Math.PI/180) *
                  Math.sin(dLon/2)**2;
        return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
      }}

      function setStatus(msg) {{
        const el = document.getElementById('ev-search-status');
        el.textContent = msg;
        el.style.display = msg ? 'block' : 'none';
      }}

      function closePanel() {{
        document.getElementById('ev-results-panel').style.display = 'none';
      }}

      function flyToSite(lat, lon, siteId) {{
        const map = Object.values(window).find(v => v && v._leaflet_id && v.setView);
        if (map) map.setView([lat, lon], 16);
      }}

      function renderPanel(locationName, lat, lon, radius, nearby) {{
        document.getElementById('panel-title').textContent =
          `${{nearby.length}} EV Site${{nearby.length !== 1 ? 's' : ''}} within ${{radius}} km`;
        document.getElementById('panel-subtitle').textContent = locationName;

        const body = document.getElementById('panel-body');
        if (nearby.length === 0) {{
          body.innerHTML = `<div style="padding:20px;text-align:center;color:#64748b">
            <div style="font-size:2rem">📍</div>
            <div style="margin-top:8px">No EV sites found within ${{radius}} km of this location.</div>
            <div style="font-size:0.78rem;margin-top:4px">Try increasing the radius.</div>
          </div>`;
        }} else {{
          body.innerHTML = nearby.map(s => `
            <div class="ev-site-card" onclick="flyToSite(${{s.lat}},${{s.lon}},'${{s.id}}')">
              <div class="site-name">
                <span>${{s.id}}</span>
                <span style="display:flex;gap:4px;align-items:center">
                  ${{s.is_top ? '<span class="top-badge">⭐ TOP 10</span>' : ''}}
                  <span class="dist-badge">${{s.dist.toFixed(1)}} km</span>
                </span>
              </div>
              <div class="site-coords">📍 ${{s.lat}}, ${{s.lon}}</div>
              <div class="site-scores">
                <span class="score-pill">AHP <b>${{s.ahp}}</b></span>
                <span class="score-pill">Demand <b>${{s.demand}}</b></span>
                <span class="score-pill">Score <b style="color:#10b981">${{s.score}}</b></span>
                <span class="score-pill">Rank <b>#${{s.rank}}</b></span>
              </div>
            </div>`).join('');
        }}
        document.getElementById('ev-results-panel').style.display = 'block';
      }}

      function drawSearchArea(lat, lon, radiusKm) {{
        const map = Object.values(window).find(v => v && v._leaflet_id && v.setView);
        if (!map) return;
        if (searchCircle)  {{ searchCircle.remove(); }}
        if (searchMarker) {{ searchMarker.remove(); }}
        searchCircle = L.circle([lat, lon], {{
          radius: radiusKm * 1000,
          color: '#3b82f6', fillColor: '#3b82f6',
          fillOpacity: 0.08, weight: 2, dashArray: '6 4'
        }}).addTo(map);
        searchMarker = L.marker([lat, lon], {{
          icon: L.divIcon({{
            html: `<div style="background:#3b82f6;color:#fff;border-radius:50%;width:28px;height:28px;
                          display:flex;align-items:center;justify-content:center;
                          font-size:14px;border:2px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,0.4)">📍</div>`,
            iconSize: [28, 28], iconAnchor: [14, 14], className: ''
          }})
        }}).addTo(map);
        map.setView([lat, lon], 13);
      }}

      async function searchLocation() {{
        const query = document.getElementById('ev-location-input').value.trim();
        const radius = parseFloat(document.getElementById('radius-select').value);
        if (!query) return;

        setStatus('🔍 Searching for "' + query + '"…');
        closePanel();

        try {{
          // Try PositionStack API first (your API key)
          const psUrl = `http://api.positionstack.com/v1/forward?access_key=25568ac20b49c89857f39f3505b6f7f5&query=${{encodeURIComponent(query + ', Bangalore')}}&limit=1`;
          let res = await fetch(psUrl);
          let data = await res.json();
          
          let lat, lon, displayName;
          
          if (data.data && data.data.length > 0) {{
            // PositionStack success
            lat = data.data[0].latitude;
            lon = data.data[0].longitude;
            displayName = data.data[0].label.split(',').slice(0,2).join(', ');
          }} else {{
            // Fallback to Nominatim (free, no key needed)
            const nomUrl = `https://nominatim.openstreetmap.org/search?q=${{encodeURIComponent(query + ', Bengaluru')}}&format=json&limit=1`;
            res = await fetch(nomUrl, {{ headers: {{ 'Accept-Language': 'en' }} }});
            data = await res.json();
            
            if (!data.length) {{
              setStatus('❌ Location not found. Try a different name.');
              setTimeout(() => setStatus(''), 3000);
              return;
            }}
            
            lat = parseFloat(data[0].lat);
            lon = parseFloat(data[0].lon);
            displayName = data[0].display_name.split(',').slice(0,2).join(', ');
          }}

          drawSearchArea(lat, lon, radius);
          setStatus('');

          const nearby = EV_SITES
            .map(s => ({{ ...s, dist: haversine(lat, lon, s.lat, s.lon) }}))
            .filter(s => s.dist <= radius)
            .sort((a, b) => a.dist - b.dist);

          renderPanel(displayName, lat, lon, radius, nearby);

        }} catch(e) {{
          setStatus('❌ Search failed. Check your internet connection.');
          setTimeout(() => setStatus(''), 3000);
        }}
      }}
    </script>
    """
    m.get_root().html.add_child(folium.Element(search_html))
    return m


def main():
    print("=" * 52)
    print("  EV Charging Station Site Selection System")
    print("=" * 52)

    os.makedirs(f"{OUTPUT_DIR}/maps", exist_ok=True)

    # Step 1: GIS spatial filtering
    gdf = run_gis_filtering(n_sites=200)

    # Step 1b: Enrich with real-world data (OSM + CSVs)
    print_data_guide()
    gdf = load_real_world_features(gdf)
    
    # Step 1c: Enrich with TomTom Traffic & OpenWeatherMap data
    gdf = enrich_with_all_realworld_data(gdf)

    # Step 1d: Competition analysis (Open Charge Map API)
    from src.api_integrations import fetch_open_charge_map_stations
    existing_stations = fetch_open_charge_map_stations(CITY_BOUNDS)
    ev_stations_count = len(existing_stations) if existing_stations is not None else 0
    gdf = analyze_competition(gdf, CITY_BOUNDS, existing_stations=existing_stations)
    underserved = get_underserved_areas(gdf, threshold_km=5.0)

    # Step 2: AHP scoring
    gdf = run_ahp_scoring(gdf)

    # Step 3: Demand forecasting
    gdf, importances, model_stats = run_demand_forecasting(gdf)

    # Step 4: Composite final score (50% AHP + 30% demand + 20% competition)
    gdf["final_score"] = (
        0.50 * gdf["ahp_score"] + 
        0.30 * gdf["predicted_demand"] +
        0.20 * gdf["competition_score"]
    )
    gdf["final_rank"]  = gdf["final_score"].rank(ascending=False).astype(int)
    gdf = gdf.sort_values("final_rank").reset_index(drop=True)

    # Step 5: Save CSV
    cols = ["site_id", "ahp_score", "ahp_rank", "predicted_demand", 
            "competition_score", "nearest_competitor_km", "final_score", "final_rank"]
    gdf[cols].to_csv(CSV_PATH, index=False)
    print(f"[Output] Ranked sites saved → {CSV_PATH}")
    
    # Save competition report
    save_competition_report(gdf)

    # Step 6: Save Folium map
    build_folium_map(gdf).save(MAP_PATH)
    print(f"[Output] Folium map saved    → {MAP_PATH}")

    # Step 7: Build charts
    weights = compute_ahp_weights()
    cr      = compute_consistency_ratio(PAIRWISE_MATRIX, weights)
    model_stats["cr"] = cr

    charts = {
        "ahp_weights":       ahp_weights_chart(weights),
        "distributions":     score_distribution_chart(gdf),
        "scatter":           scatter_ahp_vs_demand(gdf),
        "feature_importance": feature_importance_chart(importances),
        "top_sites":         top_sites_chart(gdf),
        "radar":             radar_chart(gdf),
    }

    # Step 8: Build dashboard
    build_dashboard(gdf, charts, MAP_PATH, DASHBOARD_PATH, model_stats, ev_stations_count=ev_stations_count)

    print(f"\nTop 10 Recommended EV Charging Sites:")
    print(gdf[cols].head(10).to_string(index=False))
    print("=" * 52)
    print(f"\n✅ Open in browser: {DASHBOARD_PATH}")


if __name__ == "__main__":
    main()
