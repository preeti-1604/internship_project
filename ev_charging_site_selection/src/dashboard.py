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


def build_dashboard(gdf, charts, map_path, output_path, model_stats, ev_stations_count=None):
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


    # Read map HTML
    map_srcdoc = _read_map_html(map_path)
    
    # Read the modern template
    template_path = output_path.replace('dashboard.html', 'dashboard_modern_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Replace placeholders with actual data
    html = html.replace('{total}', str(total))
    html = html.replace('{top1_site_id}', str(top1['site_id']))
    html = html.replace('{top1_score}', f"{top1['final_score']:.3f}")
    html = html.replace('{avg_score}', f"{avg_score:.3f}")
    html = html.replace('{r2}', f"{r2:.3f}")
    html = html.replace('{ev_stations_count}', str(ev_stations_count) if ev_stations_count else '200')
    html = html.replace('SITES_JSON_PLACEHOLDER', sites_json)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[Dashboard] Interactive dashboard saved → {output_path}")
