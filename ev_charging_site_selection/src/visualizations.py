import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

CRITERIA_LABELS = [
    "Roads", "Grid", "Population",
    "Land Cost", "Traffic", "Env. Sensitivity", "Commercial"
]

CRITERIA_KEYS = [
    "proximity_to_roads", "grid_access", "population_density",
    "land_cost", "traffic_volume", "environmental_sensitivity",
    "proximity_to_commercial_areas",
]


def ahp_weights_chart(weights):
    colors = [
        "#2ecc71", "#3498db", "#9b59b6",
        "#e74c3c", "#f39c12", "#1abc9c", "#e67e22"
    ]
    fig = go.Figure(go.Bar(
        x=CRITERIA_LABELS,
        y=[round(w * 100, 2) for w in weights],
        marker_color=colors,
        text=[f"{w*100:.1f}%" for w in weights],
        textposition="outside",
    ))
    fig.update_layout(
        title="AHP Criteria Weights (%)",
        xaxis_title="Criteria",
        yaxis_title="Weight (%)",
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font_color="#e2e8f0",
        title_font_size=16,
        margin=dict(t=60, b=40),
        yaxis=dict(gridcolor="#1e293b"),
    )
    return fig


def score_distribution_chart(gdf):
    fig = make_subplots(rows=1, cols=2, subplot_titles=("AHP Score Distribution", "Predicted Demand Distribution"))
    fig.add_trace(go.Histogram(
        x=gdf["ahp_score"], nbinsx=15,
        marker_color="#3b82f6", name="AHP Score", opacity=0.85
    ), row=1, col=1)
    fig.add_trace(go.Histogram(
        x=gdf["predicted_demand"], nbinsx=15,
        marker_color="#10b981", name="Demand", opacity=0.85
    ), row=1, col=2)
    fig.update_layout(
        plot_bgcolor="#0f172a", paper_bgcolor="#0f172a",
        font_color="#e2e8f0", showlegend=False,
        margin=dict(t=60, b=40),
    )
    fig.update_xaxes(gridcolor="#1e293b")
    fig.update_yaxes(gridcolor="#1e293b")
    return fig


def scatter_ahp_vs_demand(gdf, top_n=10):
    df = gdf.copy()
    df["is_top"] = df["final_rank"] <= top_n
    df["label"] = df.apply(lambda r: r["site_id"] if r["is_top"] else "", axis=1)

    fig = px.scatter(
        df, x="ahp_score", y="predicted_demand",
        color="is_top",
        color_discrete_map={True: "#f59e0b", False: "#64748b"},
        text="label",
        size="final_score",
        size_max=18,
        hover_data={"site_id": True, "final_rank": True, "final_score": ":.3f", "is_top": False},
        title="AHP Score vs Predicted Demand",
    )
    fig.update_traces(textposition="top center", textfont_size=10)
    fig.update_layout(
        plot_bgcolor="#0f172a", paper_bgcolor="#0f172a",
        font_color="#e2e8f0", legend_title="Top 10",
        xaxis=dict(title="AHP Score", gridcolor="#1e293b"),
        yaxis=dict(title="Predicted Demand", gridcolor="#1e293b"),
        margin=dict(t=60, b=40),
    )
    return fig


def feature_importance_chart(importances):
    sorted_idx = np.argsort(importances)
    fig = go.Figure(go.Bar(
        x=[importances[i] for i in sorted_idx],
        y=[CRITERIA_LABELS[i] for i in sorted_idx],
        orientation="h",
        marker_color="#6366f1",
        text=[f"{importances[i]:.3f}" for i in sorted_idx],
        textposition="outside",
    ))
    fig.update_layout(
        title="Random Forest Feature Importance",
        xaxis_title="Importance",
        plot_bgcolor="#0f172a", paper_bgcolor="#0f172a",
        font_color="#e2e8f0",
        xaxis=dict(gridcolor="#1e293b"),
        margin=dict(t=60, b=40, l=140),
    )
    return fig


def top_sites_chart(gdf, top_n=10):
    df = gdf.nsmallest(top_n, "final_rank").sort_values("final_rank", ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["site_id"], x=df["ahp_score"],
        name="AHP Score", orientation="h",
        marker_color="#3b82f6", opacity=0.9,
    ))
    fig.add_trace(go.Bar(
        y=df["site_id"], x=df["predicted_demand"],
        name="Predicted Demand", orientation="h",
        marker_color="#10b981", opacity=0.9,
    ))
    fig.add_trace(go.Bar(
        y=df["site_id"], x=df["final_score"],
        name="Final Score", orientation="h",
        marker_color="#f59e0b", opacity=0.9,
    ))
    fig.update_layout(
        barmode="group",
        title="Top 10 Sites — Score Breakdown",
        xaxis_title="Score",
        plot_bgcolor="#0f172a", paper_bgcolor="#0f172a",
        font_color="#e2e8f0",
        legend=dict(bgcolor="#1e293b"),
        xaxis=dict(gridcolor="#1e293b"),
        margin=dict(t=60, b=40, l=80),
    )
    return fig


def radar_chart(gdf, top_n=3):
    top = gdf.nsmallest(top_n, "final_rank")
    raw_cols = {
        "proximity_to_roads": "traffic_volume",
        "grid_access": "grid_access",
        "population_density": "population_density",
        "traffic_volume": "traffic_volume",
        "commercial_proximity": "commercial_proximity",
    }
    categories = CRITERIA_LABELS + [CRITERIA_LABELS[0]]
    fig = go.Figure()
    colors = ["#f59e0b", "#3b82f6", "#10b981"]
    for i, (_, row) in enumerate(top.iterrows()):
        vals = [
            row.get("traffic_volume", 0),
            row.get("grid_access", 0),
            row.get("population_density", 0),
            row.get("land_cost", 0),
            row.get("traffic_volume", 0),
            row.get("grid_access", 0),
            row.get("commercial_proximity", 0),
        ]
        mn, mx = min(vals), max(vals)
        norm = [(v - mn) / (mx - mn) if mx > mn else 0 for v in vals]
        norm_closed = norm + [norm[0]]
        fig.add_trace(go.Scatterpolar(
            r=norm_closed, theta=categories,
            fill="toself", name=row["site_id"],
            line_color=colors[i % len(colors)],
            opacity=0.75,
        ))
    fig.update_layout(
        polar=dict(
            bgcolor="#1e293b",
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="#334155", color="#94a3b8"),
            angularaxis=dict(gridcolor="#334155", color="#94a3b8"),
        ),
        title="Top 3 Sites — Criteria Radar",
        plot_bgcolor="#0f172a", paper_bgcolor="#0f172a",
        font_color="#e2e8f0",
        legend=dict(bgcolor="#1e293b"),
        margin=dict(t=60, b=40),
    )
    return fig
