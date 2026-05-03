import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

FEATURE_COLS = [
    "proximity_to_roads",
    "grid_access",
    "population_density",
    "land_cost",
    "traffic_volume",
    "environmental_sensitivity",
    "proximity_to_commercial_areas",
]


def generate_training_data(n=500, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "proximity_to_roads":          rng.uniform(0, 1, n),
        "grid_access":                 rng.uniform(0, 1, n),
        "population_density":          rng.uniform(0, 1, n),
        "land_cost":                   rng.uniform(0, 1, n),
        "traffic_volume":              rng.uniform(0, 1, n),
        "environmental_sensitivity":   rng.uniform(0, 1, n),
        "proximity_to_commercial_areas": rng.uniform(0, 1, n),
    })
    # Demand is a weighted combination of features + noise
    df["demand"] = (
        0.25 * df["traffic_volume"] +
        0.20 * df["population_density"] +
        0.15 * df["proximity_to_commercial_areas"] +
        0.15 * df["grid_access"] +
        0.10 * df["proximity_to_roads"] +
        0.10 * (1 - df["land_cost"]) +
        0.05 * (1 - df["environmental_sensitivity"]) +
        rng.normal(0, 0.03, n)
    ).clip(0, 1)
    return df


def train_model(df):
    X, y = df[FEATURE_COLS], df["demand"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Random Forest with Indian population metadata parameters
    # Matching: ntree=500, mtry=19, nodesize=length(y)/1000
    n_samples = len(y_train)
    model = RandomForestRegressor(
        n_estimators=500,
        max_features=min(19, len(FEATURE_COLS)),  # mtry parameter
        min_samples_leaf=max(1, int(n_samples / 1000)),  # nodesize parameter
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, preds)
    r2  = r2_score(y_test, preds)
    mse = mean_squared_error(y_test, preds)
    var_explained = r2 * 100
    
    print(f"[ML] Random Forest (Indian Population Metadata Config)")
    print(f"     Number of trees: {model.n_estimators}")
    print(f"     Variables at each split: {model.max_features}")
    print(f"     Min samples per leaf: {model.min_samples_leaf}")
    print(f"     Mean Squared Residuals: {mse:.4f}")
    print(f"     % Variance Explained: {var_explained:.2f}%")
    print(f"     MAE: {mae:.4f} | R²: {r2:.4f}")
    
    return model, mae, r2


def prepare_features(gdf):
    """Normalize GIS columns into 0–1 feature range for the model."""
    df = gdf.copy()
    if "proximity_to_roads" not in df.columns:
        df["proximity_to_roads"] = df["traffic_volume"]
    if "environmental_sensitivity" not in df.columns:
        df["environmental_sensitivity"] = 1 - df["grid_access"]

    for col in ["population_density", "traffic_volume"]:
        mn, mx = df[col].min(), df[col].max()
        df[col] = (df[col] - mn) / (mx - mn) if mx > mn else 0.0

    for col in ["land_cost"]:
        mn, mx = df[col].min(), df[col].max()
        df[col] = 1 - ((df[col] - mn) / (mx - mn)) if mx > mn else 1.0

    # Rename GIS column to match model feature name
    if "commercial_proximity" in df.columns and "proximity_to_commercial_areas" not in df.columns:
        df = df.rename(columns={"commercial_proximity": "proximity_to_commercial_areas"})

    return df


def run_demand_forecasting(gdf):
    training_data = generate_training_data()
    model, mae, r2 = train_model(training_data)

    df = prepare_features(gdf)
    gdf = gdf.copy()
    gdf["predicted_demand"] = model.predict(df[FEATURE_COLS]).round(4)
    importances = model.feature_importances_
    return gdf, importances, {"mae": round(mae, 4), "r2": round(r2, 4)}
