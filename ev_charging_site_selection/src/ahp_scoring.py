import numpy as np
import pandas as pd

CRITERIA = [
    "proximity_to_roads",
    "grid_access",
    "population_density",
    "land_cost",
    "traffic_volume",
    "environmental_sensitivity",
    "proximity_to_commercial_areas",
]

# Pairwise comparison matrix (7x7) — values based on Saaty's 1–9 scale
# Row i vs Col j: how much more important is criterion i over j
PAIRWISE_MATRIX = np.array([
    [1,   2,   3,   4,   3,   5,   2],   # proximity_to_roads
    [1/2, 1,   2,   3,   2,   4,   2],   # grid_access
    [1/3, 1/2, 1,   2,   2,   3,   1],   # population_density
    [1/4, 1/3, 1/2, 1,   1/2, 2,   1/2], # land_cost
    [1/3, 1/2, 1/2, 2,   1,   3,   1],   # traffic_volume
    [1/5, 1/4, 1/3, 1/2, 1/3, 1,   1/3], # environmental_sensitivity
    [1/2, 1/2, 1,   2,   1,   3,   1],   # proximity_to_commercial_areas
], dtype=float)

# Saaty's Random Consistency Index for n=7
RI = 1.32


def compute_ahp_weights(matrix=PAIRWISE_MATRIX):
    col_sums = matrix.sum(axis=0)
    normalized = matrix / col_sums
    weights = normalized.mean(axis=1)
    return weights


def compute_consistency_ratio(matrix, weights):
    n = len(weights)
    weighted_sum = matrix @ weights
    lambda_max = np.mean(weighted_sum / weights)
    ci = (lambda_max - n) / (n - 1)
    cr = ci / RI
    return round(cr, 4)


def normalize_criteria(gdf):
    df = gdf.copy()
    # Higher is better: normalize 0–1 (min-max)
    for col in ["proximity_to_roads", "grid_access", "population_density",
                "traffic_volume", "proximity_to_commercial_areas"]:
        if col in df.columns:
            mn, mx = df[col].min(), df[col].max()
            df[col] = (df[col] - mn) / (mx - mn) if mx > mn else 0.0

    # Lower is better: invert normalization
    for col in ["land_cost", "environmental_sensitivity"]:
        if col in df.columns:
            mn, mx = df[col].min(), df[col].max()
            df[col] = 1 - ((df[col] - mn) / (mx - mn)) if mx > mn else 1.0

    return df


def map_gdf_to_criteria(gdf):
    """Map GIS columns to AHP criteria columns."""
    df = gdf.copy()
    if "proximity_to_roads" not in df.columns:
        df["proximity_to_roads"] = df["traffic_volume"]
    if "environmental_sensitivity" not in df.columns:
        df["environmental_sensitivity"] = 1 - df["grid_access"]
    if "commercial_proximity" in df.columns and "proximity_to_commercial_areas" not in df.columns:
        df = df.rename(columns={"commercial_proximity": "proximity_to_commercial_areas"})
    return df


def run_ahp_scoring(gdf):
    weights = compute_ahp_weights()
    cr = compute_consistency_ratio(PAIRWISE_MATRIX, weights)
    print(f"[AHP] Weights: { {c: round(w, 4) for c, w in zip(CRITERIA, weights)} }")
    print(f"[AHP] Consistency Ratio: {cr} {'✓ Acceptable' if cr < 0.1 else '✗ Revise matrix'}")

    df = map_gdf_to_criteria(gdf)
    df = normalize_criteria(df)

    scores = sum(df[c] * w for c, w in zip(CRITERIA, weights) if c in df.columns)
    gdf = gdf.copy()
    gdf["ahp_score"] = scores.values
    gdf["ahp_rank"] = gdf["ahp_score"].rank(ascending=False).astype(int)
    return gdf.sort_values("ahp_rank").reset_index(drop=True)
