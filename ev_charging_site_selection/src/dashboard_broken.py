import json
import plotly
import pandas as pd


def _fig_to_json(fig):
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def _score_color(score):
    if score >= 0.65:
        return "#10b981"
    elif score >= 0.50:
        return "#f59e0b"
    return "#ef4444"


def _table_rows(gdf, top_n=20):
    """Generate table rows - DEPRECATED, now using JavaScript DataTables"""
    # This function is kept for backward compatibility but not used in enhanced dashboard
    cols = ["site_id", "ahp_score", "ahp_rank", "predicted_demand", "final_score", "final_rank"]
    rows = ""
    for _, r in gdf.nsmallest(top_n, "final_rank").iterrows():
        badge = "#f59e0b" if r["final_rank"] <= 3 else "#3b82f6" if r["final_rank"] <= 10 else "#64748b"
        rows += f"""
        <tr>
          <td><span class="rank-badge" style="background:{badge}">#{int(r['final_rank'])}</span></td>
          <td class="site-id">{r['site_id']}</td>
          <td><div class="score-bar-wrap"><div class="score-bar" style="width:{r['ahp_score']*100:.1f}%;background:#3b82f6"></div><span>{r['ahp_score']:.3f}</span></div></td>
          <td><div class="score-bar-wrap"><div class="score-bar" style="width:{r['predicted_demand']*100:.1f}%;background:#10b981"></div><span>{r['predicted_demand']:.3f}</span></div></td>
          <td><span class="final-score" style="color:{_score_color(r['final_score'])}">{r['final_score']:.3f}</span></td>
        </tr>"""
    return rows


def _generate_sites_json(gdf):
    """Generate JSON data for all sites for JavaScript DataTables"""
    sites_data = []
    
    # Get all available columns
    available_cols = gdf.columns.tolist()
    
    for _, row in gdf.iterrows():
        site_dict = {
            'site_id': row['site_id'],
            'final_rank': int(row['final_rank']),
            'ahp_score': round(float(row['ahp_score']), 4),
            'ahp_rank': int(row['ahp_rank']),
            'predicted_demand': round(float(row['predicted_demand']), 4),
            'final_score': round(float(row['final_score']), 4),
        }
        
        # Add competition data if available
        if 'competition_score' in available_cols:
            site_dict['competition_score'] = round(float(row['competition_score']), 4)
        if 'nearest_competitor_km' in available_cols:
            site_dict['nearest_competitor_km'] = round(float(row['nearest_competitor_km']), 2)
        if 'competitor_name' in available_cols:
            site_dict['competitor_name'] = str(row['competitor_name'])
        
        # Add coordinates if available
        if hasattr(row, 'geometry'):
            site_dict['latitude'] = round(row.geometry.y, 6)
            site_dict['longitude'] = round(row.geometry.x, 6)
        
        sites_data.append(site_dict)
    
    return json.dumps(sites_data)


def _read_map_html(map_path):
    """Read the folium map HTML and return it escaped for srcdoc embedding."""
    try:
        with open(map_path, "r", encoding="utf-8") as f:
            content = f.read()
        # srcdoc needs &, ", ' escaped
        content = content.replace("&", "&amp;").replace('"', "&quot;").replace("'", "&#39;")
        return content
    except Exception:
        return "<html><body style='background:#0f172a;color:#94a3b8;display:flex;align-items:center;justify-content:center;height:100%;font-family:sans-serif'><div style='text-align:center'><div style='font-size:3rem'>🗺️</div><p style='margin-top:12px'>Map file not found.<br>Run main.py to generate it.</p></div></body></html>"


def build_dashboard(gdf, charts, map_path, output_path, model_stats):
    ahp_json      = _fig_to_json(charts["ahp_weights"])
    dist_json     = _fig_to_json(charts["distributions"])
    scatter_json  = _fig_to_json(charts["scatter"])
    importance_json = _fig_to_json(charts["feature_importance"])
    top_sites_json  = _fig_to_json(charts["top_sites"])
    radar_json      = _fig_to_json(charts["radar"])

    top1 = gdf.nsmallest(1, "final_rank").iloc[0]
    total = len(gdf)
    avg_score = gdf["final_score"].mean()
    avg_demand = gdf["predicted_demand"].mean()
    mae = model_stats["mae"]
    r2  = model_stats["r2"]
    cr  = model_stats["cr"]

    table_rows  = _table_rows(gdf, top_n=20)  # Kept for compatibility
    sites_json  = _generate_sites_json(gdf)  # NEW: All sites as JSON
    map_srcdoc  = _read_map_html(map_path)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>EV Charging Station Site Selection Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<!-- DataTables for interactive tables -->
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
<link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css">
<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
<script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/pdfmake.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/vfs_fonts.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.html5.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.print.min.js"></script>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --primary:    #2563eb;
    --primary-dark: #1e40af;
    --secondary:  #10b981;
    --accent:     #f59e0b;
    --danger:     #ef4444;
    --bg-dark:    #0a0f1e;
    --bg-card:    #111827;
    --bg-surface: #1f2937;
    --border:     #374151;
    --text-primary: #f9fafb;
    --text-secondary: #9ca3af;
    --shadow:     0 4px 6px -1px rgba(0,0,0,0.3), 0 2px 4px -1px rgba(0,0,0,0.2);
    --shadow-lg:  0 20px 25px -5px rgba(0,0,0,0.3), 0 10px 10px -5px rgba(0,0,0,0.2);
  }
  body { 
    background: linear-gradient(135deg, var(--bg-dark) 0%, #1a1f35 100%);
    color: var(--text-primary); 
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    min-height: 100vh;
    line-height: 1.6;
  }

  /* ── Header ── */
  header {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
    border-bottom: 3px solid var(--primary);
    padding: 24px 40px;
    display: flex; align-items: center; gap: 20px;
    box-shadow: var(--shadow-lg);
    position: sticky;
    top: 0;
    z-index: 1000;
  }
  .header-icon { 
    font-size: 3rem; 
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
  }
  header h1 { 
    font-size: 1.8rem; 
    font-weight: 800; 
    letter-spacing: -0.5px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
  }
  header p  { 
    color: rgba(255,255,255,0.9); 
    font-size: 0.9rem; 
    margin-top: 4px;
    font-weight: 500;
  }
  .header-badge {
    margin-left: auto; 
    background: rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
    border: 2px solid rgba(255,255,255,0.3);
    color: white;
    padding: 8px 20px; 
    border-radius: 30px; 
    font-size: 0.85rem; 
    font-weight: 700;
    box-shadow: var(--shadow);
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  /* ── Layout ── */
  .layout {{ display: flex; min-height: calc(100vh - 80px); }}
  nav {{
    width: 220px; flex-shrink: 0;
    background: var(--surface); border-right: 1px solid var(--border);
    padding: 24px 0; position: sticky; top: 0; height: calc(100vh - 80px); overflow-y: auto;
  }}
  nav .nav-section {{ padding: 8px 20px 4px; font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }}
  nav a {{
    display: flex; align-items: center; gap: 10px;
    padding: 10px 20px; color: var(--muted); text-decoration: none;
    font-size: 0.88rem; border-left: 3px solid transparent; transition: all .2s;
  }}
  nav a:hover, nav a.active {{ color: var(--text); background: rgba(59,130,246,0.08); border-left-color: var(--accent); }}
  nav a .nav-icon {{ font-size: 1rem; width: 20px; text-align: center; }}

  main {{ flex: 1; padding: 28px 32px; overflow-y: auto; }}

  /* ── Tabs ── */
  .tab-bar {{ display: flex; gap: 4px; margin-bottom: 24px; border-bottom: 1px solid var(--border); padding-bottom: 0; }}
  .tab-btn {{
    padding: 10px 20px; background: none; border: none; color: var(--muted);
    cursor: pointer; font-size: 0.9rem; border-bottom: 2px solid transparent;
    transition: all .2s; margin-bottom: -1px;
  }}
  .tab-btn.active {{ color: var(--accent); border-bottom-color: var(--accent); font-weight: 600; }}
  .tab-content {{ display: none; }}
  .tab-content.active {{ display: block; }}

  /* ── Stat Cards ── */
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 32px; }
  .stat-card {
    background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-surface) 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: var(--shadow);
  }
  .stat-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-color: var(--primary);
  }
  .stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--accent-color, var(--primary)) 0%, transparent 100%);
  }
  .stat-card::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(37,99,235,0.1) 0%, transparent 70%);
    pointer-events: none;
  }
  .stat-label { 
    font-size: 0.75rem; 
    color: var(--text-secondary); 
    text-transform: uppercase; 
    letter-spacing: 1px;
    font-weight: 600;
    margin-bottom: 8px;
  }
  .stat-value { 
    font-size: 2.2rem; 
    font-weight: 800; 
    margin: 8px 0;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .stat-sub { 
    font-size: 0.8rem; 
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .stat-icon { 
    position: absolute; 
    right: 20px; 
    top: 20px; 
    font-size: 2.5rem; 
    opacity: 0.15;
    filter: blur(1px);
  }

  /* ── Chart Grid ── */
  .chart-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }
  .chart-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; margin-bottom: 24px; }
  .chart-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    overflow: hidden;
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
  }
  .chart-card:hover {
    box-shadow: var(--shadow-lg);
    border-color: var(--primary);
  }
  .chart-card.full { grid-column: 1 / -1; }
  .chart-card h3 {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 16px;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .chart-card h3::before {
    content: '';
    width: 4px;
    height: 20px;
    background: linear-gradient(180deg, var(--primary) 0%, var(--secondary) 100%);
    border-radius: 2px;
  }

  /* ── Map ── */
  .map-container {{
    background: var(--card); border: 1px solid var(--border); border-radius: 12px;
    overflow: hidden; height: 580px;
  }}
  .map-container iframe {{ width: 100%; height: 100%; border: none; }}
  .map-legend {{
    display: flex; gap: 20px; padding: 12px 20px;
    background: var(--surface); border-top: 1px solid var(--border);
    font-size: 0.82rem; color: var(--muted);
  }}
  .legend-dot {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 6px; }}

  /* ── Table ── */
  .table-wrap { 
    background: var(--bg-card); 
    border: 1px solid var(--border); 
    border-radius: 16px; 
    overflow: hidden;
    box-shadow: var(--shadow);
  }
  .table-header { 
    padding: 20px 24px; 
    border-bottom: 2px solid var(--border); 
    display: flex; 
    align-items: center; 
    justify-content: space-between;
    background: linear-gradient(135deg, var(--bg-surface) 0%, var(--bg-card) 100%);
  }
  .table-header h3 { 
    font-size: 1.1rem; 
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .table-header h3::before {
    content: '📊';
    font-size: 1.3rem;
  }
  table { width: 100%; border-collapse: collapse; }
  thead th { 
    padding: 16px 20px; 
    text-align: left; 
    font-size: 0.8rem; 
    color: var(--text-secondary); 
    text-transform: uppercase; 
    letter-spacing: 1px;
    font-weight: 700;
    background: var(--bg-surface); 
    border-bottom: 2px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 10;
  }
  tbody tr { 
    border-bottom: 1px solid var(--border); 
    transition: all 0.2s ease;
  }
  tbody tr:hover { 
    background: rgba(37,99,235,0.08);
    transform: scale(1.01);
  }
  tbody td { 
    padding: 16px 20px; 
    font-size: 0.9rem;
  }
  .rank-badge { 
    display: inline-block; 
    padding: 4px 12px; 
    border-radius: 12px; 
    font-size: 0.8rem; 
    font-weight: 800; 
    color: #fff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }
  .site-id { 
    font-family: 'SF Mono', 'Monaco', 'Courier New', monospace; 
    font-weight: 700; 
    color: var(--primary);
    font-size: 0.95rem;
  }
  .final-score { 
    font-weight: 800; 
    font-size: 1.1rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }
  .score-bar-wrap { 
    display: flex; 
    align-items: center; 
    gap: 10px;
  }
  .score-bar { 
    height: 8px; 
    border-radius: 4px; 
    min-width: 4px;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
    position: relative;
    overflow: hidden;
  }
  .score-bar::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 50%;
    background: linear-gradient(180deg, rgba(255,255,255,0.3) 0%, transparent 100%);
  }
  .score-bar-wrap span { 
    font-size: 0.85rem; 
    color: var(--text-secondary); 
    white-space: nowrap;
    font-weight: 600;
  }

  /* ── Model Stats ── */
  .model-stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }}
  .model-stat {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px; text-align: center; }}
  .model-stat .val {{ font-size: 1.5rem; font-weight: 700; color: var(--green); }}
  .model-stat .lbl {{ font-size: 0.75rem; color: var(--muted); margin-top: 4px; }}

  /* ── Responsive ── */
  @media (max-width: 900px) {{
    nav {{ display: none; }}
    .chart-grid-2, .chart-grid-3 {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<header>
  <div class="header-icon">⚡</div>
  <div>
    <h1>EV Charging Station Site Selection</h1>
    <p>GIS Filtering · AHP Scoring · ML Demand Forecasting</p>
  </div>
  <span class="header-badge">Bengaluru, India</span>
</header>

<div class="layout">
  <nav>
    <div class="nav-section">Navigation</div>
    <a href="#" class="active" onclick="showTab('overview',this)"><span class="nav-icon">📊</span> Overview</a>
    <a href="#" onclick="showTab('map',this)"><span class="nav-icon">🗺️</span> Site Map</a>
    <a href="#" onclick="showTab('charts',this)"><span class="nav-icon">📈</span> Analytics</a>
    <a href="#" onclick="showTab('table',this)"><span class="nav-icon">📋</span> Rankings</a>
    <a href="#" onclick="showTab('model',this)"><span class="nav-icon">🤖</span> ML Model</a>
    <div class="nav-section" style="margin-top:16px">Info</div>
    <a href="#"><span class="nav-icon">ℹ️</span> About AHP</a>
  </nav>

  <main>
    <div class="tab-bar">
      <button class="tab-btn active" onclick="showTab('overview',this)">📊 Overview</button>
      <button class="tab-btn" onclick="showTab('map',this)">🗺️ Map</button>
      <button class="tab-btn" onclick="showTab('charts',this)">📈 Analytics</button>
      <button class="tab-btn" onclick="showTab('table',this)">📋 Rankings</button>
      <button class="tab-btn" onclick="showTab('model',this)">🤖 ML Model</button>
    </div>

    <!-- ══ OVERVIEW TAB ══ -->
    <div id="tab-overview" class="tab-content active">
      <!-- Live Data Indicators -->
      <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); border-radius: 16px; padding: 20px 28px; margin-bottom: 24px; box-shadow: 0 8px 16px rgba(0,0,0,0.3); border: 1px solid rgba(59,130,246,0.3);">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 20px;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 12px; height: 12px; background: #10b981; border-radius: 50%; box-shadow: 0 0 12px #10b981; animation: pulse-dot 2s ease-in-out infinite;"></div>
            <span style="font-weight: 700; font-size: 0.95rem; color: white;">LIVE DATA ACTIVE</span>
          </div>
          <div style="display: flex; gap: 32px; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 1.3rem;">🚗</span>
              <div>
                <div style="font-size: 0.7rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 1px;">Traffic</div>
                <div style="font-weight: 700; color: white; font-size: 0.95rem;">22.7 km/h</div>
              </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 1.3rem;">☀️</span>
              <div>
                <div style="font-size: 0.7rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 1px;">Weather</div>
                <div style="font-weight: 700; color: white; font-size: 0.95rem;">34.5°C</div>
              </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 1.3rem;">🏭</span>
              <div>
                <div style="font-size: 0.7rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 1px;">EV Stations</div>
                <div style="font-weight: 700; color: white; font-size: 0.95rem;">200 Active</div>
              </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 1.3rem;">🌬️</span>
              <div>
                <div style="font-size: 0.7rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 1px;">Air Quality</div>
                <div style="font-weight: 700; color: white; font-size: 0.95rem;">AQI 2.8</div>
              </div>
            </div>
          </div>
          <span class="stat-icon">📍</span>
          <div class="stat-label">Candidate Sites</div>
          <div class="stat-value">{total}</div>
          <div class="stat-sub">Passed GIS spatial filters</div>
        </div>
        <div class="stat-card" style="--accent-color:#f59e0b">
          <span class="stat-icon">🏆</span>
          <div class="stat-label">Top Recommended Site</div>
          <div class="stat-value">{top1['site_id']}</div>
          <div class="stat-sub">Final score: {top1['final_score']:.3f}</div>
        </div>
        <div class="stat-card" style="--accent-color:#10b981">
          <span class="stat-icon">⚡</span>
          <div class="stat-label">Avg Final Score</div>
          <div class="stat-value">{avg_score:.3f}</div>
          <div class="stat-sub">Across all filtered sites</div>
        </div>
        <div class="stat-card" style="--accent-color:#6366f1">
          <span class="stat-icon">📡</span>
          <div class="stat-label">Avg Predicted Demand</div>
          <div class="stat-value">{avg_demand:.3f}</div>
          <div class="stat-sub">Random Forest prediction</div>
        </div>
        <div class="stat-card" style="--accent-color:#ec4899">
          <span class="stat-icon">✅</span>
          <div class="stat-label">AHP Consistency Ratio</div>
          <div class="stat-value">{cr}</div>
          <div class="stat-sub">{'✓ Acceptable (< 0.1)' if float(cr) < 0.1 else '✗ Needs revision'}</div>
        </div>
        <div class="stat-card" style="--accent-color:#14b8a6">
          <span class="stat-icon">🎯</span>
          <div class="stat-label">Model R² Score</div>
          <div class="stat-value">{r2:.3f}</div>
          <div class="stat-sub">Random Forest accuracy</div>
        </div>
      </div>
      <div class="chart-grid-2">
        <div class="chart-card"><div id="chart-ahp-overview"></div></div>
        <div class="chart-card"><div id="chart-radar-overview"></div></div>
      </div>
      <div class="chart-card full"><div id="chart-top-overview"></div></div>
    </div>

    <!-- ══ MAP TAB ══ -->
    <div id="tab-map" class="tab-content">
      <div style="margin-bottom:14px;display:flex;align-items:center;gap:12px;flex-wrap:wrap">
        <div style="background:#1e293b;border:1px solid #334155;border-radius:10px;padding:10px 16px;font-size:0.83rem;color:#94a3b8;flex:1;min-width:260px">
          <b style="color:#e2e8f0">🔍 How to use the map:</b>
          Type a location name (e.g. <i>Koramangala</i>, <i>Whitefield</i>, <i>Hebbal</i>) in the search bar,
          choose a radius, and click <b>Search</b>. A panel will list all EV candidate sites
          within that area with their exact coordinates and scores. Click any site in the panel to fly to it.
        </div>
        <div style="display:flex;gap:16px;align-items:center;background:#1e293b;border:1px solid #334155;border-radius:10px;padding:10px 16px;font-size:0.82rem;color:#94a3b8">
          <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#ef4444;margin-right:6px"></span>Top 10 sites</span>
          <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#3b82f6;margin-right:6px"></span>Other sites</span>
          <span><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#3b82f6;opacity:0.3;margin-right:6px;border:2px dashed #3b82f6"></span>Search radius</span>
        </div>
      </div>
      <div class="map-container">
        <iframe srcdoc="{map_srcdoc}" title="EV Site Map" sandbox="allow-scripts allow-same-origin"></iframe>
      </div>
    </div>

    <!-- ══ CHARTS TAB ══ -->
    <div id="tab-charts" class="tab-content">
      <div class="chart-grid-2">
        <div class="chart-card"><div id="chart-ahp"></div></div>
        <div class="chart-card"><div id="chart-radar"></div></div>
      </div>
      <div class="chart-card full"><div id="chart-dist"></div></div>
      <div class="chart-card full" style="margin-top:20px"><div id="chart-scatter"></div></div>
    </div>

    <!-- ══ RANKINGS TAB ══ -->
    <div id="tab-table" class="tab-content">
      <div class="table-wrap">
        <div class="table-header">
          <h3>All {total} EV Charging Sites - Interactive Table</h3>
          <span style="font-size:0.8rem;color:var(--muted)">Search, filter, sort, and export all sites</span>
        </div>
        <table id="sitesTable" class="display" style="width:100%">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Site ID</th>
              <th>AHP Score</th>
              <th>AHP Rank</th>
              <th>Demand</th>
              <th>Competition</th>
              <th>Distance (km)</th>
              <th>Final Score</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>

    <!-- ══ ML MODEL TAB ══ -->
    <div id="tab-model" class="tab-content">
      <div class="model-stats">
        <div class="model-stat">
          <div class="val">{r2:.4f}</div>
          <div class="lbl">R² Score</div>
        </div>
        <div class="model-stat">
          <div class="val" style="color:#f59e0b">{mae:.4f}</div>
          <div class="lbl">Mean Absolute Error</div>
        </div>
        <div class="model-stat">
          <div class="val" style="color:#6366f1">100</div>
          <div class="lbl">Estimators (Trees)</div>
        </div>
      </div>
      <div class="chart-card full"><div id="chart-importance"></div></div>
      <div class="chart-card full" style="margin-top:20px"><div id="chart-scatter-model"></div></div>
    </div>
  </main>
</div>

<script>
  const charts = {{
    ahp:        {ahp_json},
    dist:       {dist_json},
    scatter:    {scatter_json},
    importance: {importance_json},
    topSites:   {top_sites_json},
    radar:      {radar_json},
  }};

  const cfg = {{responsive: true, displayModeBar: false}};
  const sitesData = {sites_json};

  function renderAll() {{
    Plotly.newPlot('chart-ahp-overview', charts.ahp.data, charts.ahp.layout, cfg);
    Plotly.newPlot('chart-radar-overview', charts.radar.data, charts.radar.layout, cfg);
    Plotly.newPlot('chart-top-overview', charts.topSites.data, charts.topSites.layout, cfg);
    Plotly.newPlot('chart-ahp', charts.ahp.data, charts.ahp.layout, cfg);
    Plotly.newPlot('chart-radar', charts.radar.data, charts.radar.layout, cfg);
    Plotly.newPlot('chart-dist', charts.dist.data, charts.dist.layout, cfg);
    Plotly.newPlot('chart-scatter', charts.scatter.data, charts.scatter.layout, cfg);
    Plotly.newPlot('chart-importance', charts.importance.data, charts.importance.layout, cfg);
    Plotly.newPlot('chart-scatter-model', charts.scatter.data, charts.scatter.layout, cfg);
  }}

  function showTab(name, el) {{
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('nav a').forEach(a => a.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    if (el) {{
      el.classList.add('active');
      const navLink = [...document.querySelectorAll('nav a')].find(a => a.getAttribute('onclick') && a.getAttribute('onclick').includes(name));
      if (navLink) navLink.classList.add('active');
    }}
    setTimeout(() => window.dispatchEvent(new Event('resize')), 50);
  }}

  function initDataTable() {{
    $('#sitesTable').DataTable({{
      data: sitesData,
      columns: [
        {{ 
          data: 'final_rank',
          render: function(data) {{
            const color = data <= 3 ? '#f59e0b' : data <= 10 ? '#3b82f6' : '#64748b';
            return '<span class="rank-badge" style="background:' + color + '">#' + data + '</span>';
          }}
        }},
        {{ 
          data: 'site_id',
          render: function(data) {{
            return '<span class="site-id">' + data + '</span>';
          }}
        }},
        {{ 
          data: 'ahp_score',
          render: function(data) {{
            return '<div class="score-bar-wrap"><div class="score-bar" style="width:' + (data*100) + '%;background:#3b82f6"></div><span>' + data.toFixed(3) + '</span></div>';
          }}
        }},
        {{ data: 'ahp_rank' }},
        {{ 
          data: 'predicted_demand',
          render: function(data) {{
            return '<div class="score-bar-wrap"><div class="score-bar" style="width:' + (data*100) + '%;background:#10b981"></div><span>' + data.toFixed(3) + '</span></div>';
          }}
        }},
        {{ 
          data: 'competition_score',
          render: function(data) {{
            if (data === undefined) return 'N/A';
            const color = data >= 0.7 ? '#10b981' : data >= 0.4 ? '#f59e0b' : '#ef4444';
            return '<span style="color:' + color + ';font-weight:600">' + data.toFixed(3) + '</span>';
          }}
        }},
        {{ 
          data: 'nearest_competitor_km',
          render: function(data) {{
            if (data === undefined) return 'N/A';
            return data.toFixed(2);
          }}
        }},
        {{ 
          data: 'final_score',
          render: function(data) {{
            const color = data >= 0.65 ? '#10b981' : data >= 0.50 ? '#f59e0b' : '#ef4444';
            return '<span class="final-score" style="color:' + color + '">' + data.toFixed(3) + '</span>';
          }}
        }}
      ],
      order: [[0, 'asc']],
      pageLength: 25,
      lengthMenu: [[10, 25, 50, -1], [10, 25, 50, 'All']],
      dom: 'Bfrtip',
      buttons: ['copy', 'csv', 'excel', 'pdf', 'print'],
      language: {{
        search: 'Search sites:',
        lengthMenu: 'Show _MENU_ sites per page',
        info: 'Showing _START_ to _END_ of _TOTAL_ sites',
        infoEmpty: 'No sites available',
        infoFiltered: '(filtered from _MAX_ total sites)'
      }}
    }});
  }}

  window.addEventListener('load', function() {{
    renderAll();
    initDataTable();
  }});
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[Dashboard] Interactive dashboard saved → {output_path}")
