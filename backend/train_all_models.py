from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import (
    KFold,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeRegressor


# =========================================================
# 1. CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "events.csv"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "actual_attendance"

FEATURES = [
    "event_type",
    "duration_hours",
    "expected_attendance",
    "start_hour",
    "day_of_week",
    "month",
]

RANDOM_STATE = 42


# =========================================================
# 2. LOAD AND PREPARE DATA
# =========================================================

print("\n" + "=" * 65)
print("CAMPUSSPACE AI — COMPLETE ML TRAINING PIPELINE")
print("=" * 65)

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

required_columns = [
    "event_type",
    "start_time",
    "duration_hours",
    "expected_attendance",
    "actual_attendance",
]

missing_columns = set(required_columns) - set(df.columns)

if missing_columns:
    raise ValueError(f"Missing columns: {sorted(missing_columns)}")

df["start_time"] = pd.to_datetime(
    df["start_time"],
    errors="coerce",
)

df = df.dropna(subset=required_columns).copy()

df["start_hour"] = df["start_time"].dt.hour
df["day_of_week"] = df["start_time"].dt.dayofweek
df["month"] = df["start_time"].dt.month

X = df[FEATURES]
y = df[TARGET]

print(f"\nDataset: {DATA_PATH.name}")
print(f"Records: {len(df)}")
print(f"Features: {FEATURES}")
print(f"Target: {TARGET}")


# =========================================================
# 3. TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
)

print(f"\nTraining records: {len(X_train)}")
print(f"Testing records:  {len(X_test)}")


# =========================================================
# 4. DEFINE PREPROCESSING
# =========================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            ["event_type"],
        )
    ],
    remainder="passthrough",
)


def create_pipeline(regressor):
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", regressor),
        ]
    )


# =========================================================
# 5. DEFINE CANDIDATE MODELS
# =========================================================

models = {
    "Linear Regression": LinearRegression(),

    "Decision Tree": DecisionTreeRegressor(
        max_depth=6,
        min_samples_leaf=10,
        random_state=RANDOM_STATE,
    ),

    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=5,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),

    "Extra Trees": ExtraTreesRegressor(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=5,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=2,
        loss="squared_error",
        random_state=RANDOM_STATE,
    ),
}


# =========================================================
# 6. BASELINE MODEL
# =========================================================

baseline = DummyRegressor(strategy="mean")
baseline.fit(X_train[["expected_attendance"]], y_train)

baseline_predictions = baseline.predict(
    X_test[["expected_attendance"]]
)

baseline_mae = mean_absolute_error(
    y_test,
    baseline_predictions,
)

baseline_rmse = np.sqrt(
    mean_squared_error(y_test, baseline_predictions)
)

baseline_r2 = r2_score(y_test, baseline_predictions)

print("\n" + "=" * 65)
print("BASELINE RESULTS")
print("=" * 65)
print(f"MAE:  {baseline_mae:.3f}")
print(f"RMSE: {baseline_rmse:.3f}")
print(f"R²:   {baseline_r2:.4f}")


# =========================================================
# 7. CROSS-VALIDATION AND MODEL SELECTION
# =========================================================

cv = KFold(
    n_splits=5,
    shuffle=True,
    random_state=RANDOM_STATE,
)

trained_models = {}
cv_results = []

print("\n" + "=" * 65)
print("TRAINING AND CROSS-VALIDATION")
print("=" * 65)

for name, regressor in models.items():
    print(f"\nTraining: {name}")

    pipeline = create_pipeline(regressor)

    scores = cross_val_score(
        pipeline,
        X_train,
        y_train,
        cv=cv,
        scoring="neg_mean_absolute_error",
        n_jobs=1,
    )

    cv_mae = -scores.mean()

    pipeline.fit(X_train, y_train)

    trained_models[name] = pipeline

    cv_results.append({
        "model": name,
        "cv_mae": float(cv_mae),
        "cv_std": float(scores.std()),
    })

    print(f"Cross-validation MAE: {cv_mae:.3f}")
    print(f"Fold-to-fold variation: {scores.std():.3f}")


# Select using training-set cross-validation, not test results.
cv_results.sort(key=lambda result: result["cv_mae"])

best_name = cv_results[0]["model"]
best_model = trained_models[best_name]


# =========================================================
# 8. EVALUATE SELECTED MODEL ON UNSEEN TEST DATA
# =========================================================

predictions = best_model.predict(X_test)

best_mae = mean_absolute_error(y_test, predictions)

best_rmse = np.sqrt(
    mean_squared_error(y_test, predictions)
)

best_r2 = r2_score(y_test, predictions)

print("\n" + "=" * 65)
print("FINAL TEST RESULTS")
print("=" * 65)

print(f"Selected model: {best_name}")
print(f"Baseline MAE:   {baseline_mae:.3f}")
print(f"Model MAE:      {best_mae:.3f}")
print(f"Model RMSE:     {best_rmse:.3f}")
print(f"Model R²:       {best_r2:.4f}")


# =========================================================
# 9. DISPLAY MODEL COMPARISON
# =========================================================

comparison = pd.DataFrame(cv_results)

print("\n" + "=" * 65)
print("CROSS-VALIDATION MODEL RANKING")
print("=" * 65)

print(
    comparison.to_string(
        index=False,
        formatters={
            "cv_mae": "{:.3f}".format,
            "cv_std": "{:.3f}".format,
        },
    )
)


# =========================================================
# 10. SAVE MODEL AND RESULTS
# =========================================================

model_path = MODEL_DIR / "best_attendance_model.joblib"
results_path = MODEL_DIR / "model_evaluation.json"
comparison_path = MODEL_DIR / "model_comparison.csv"

joblib.dump(best_model, model_path)

comparison.to_csv(comparison_path, index=False)

improvement = (
    (baseline_mae - best_mae) / baseline_mae * 100
    if baseline_mae > 0
    else 0.0
)

results = {
    "target": TARGET,
    "selected_model": best_name,
    "training_records": len(X_train),
    "testing_records": len(X_test),
    "baseline_mae": float(baseline_mae),
    "model_mae": float(best_mae),
    "model_rmse": float(best_rmse),
    "model_r2": float(best_r2),
    "mae_improvement_percent": float(improvement),
    "baseline_beaten": bool(best_mae < baseline_mae),
    "features": FEATURES,
    "cross_validation": cv_results,
}

with open(results_path, "w", encoding="utf-8") as file:
    json.dump(results, file, indent=4)

print("\n" + "=" * 65)
print("FINAL VERDICT")
print("=" * 65)

if best_mae < baseline_mae:
    print(f"The selected model beats the baseline by {improvement:.2f}% MAE.")
    print("Further validation is required before production use.")
else:
    print("No selected model beat the baseline on the test set.")
    print("Do not claim that ML improves attendance prediction.")

print(f"\nSaved model:      {model_path}")
print(f"Evaluation:       {results_path}")
print(f"Model comparison: {comparison_path}")

print("\nTraining pipeline complete.")