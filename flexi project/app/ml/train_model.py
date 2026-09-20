"""
app/ml/train_model.py
Unit 4 — Train, evaluate, and save the defect severity prediction model.

Models trained:
  1. Linear Regression (for priority_score prediction — regression task)
  2. Random Forest Classifier (for severity label — classification task)
  3. XGBoost Classifier (for severity label — comparison)

Evaluation metrics: Accuracy, Classification Report, R² (regression)
"""

import os
import sys
import json
import warnings
import pandas as pd
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    r2_score, mean_absolute_error, mean_squared_error
)
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "defect_dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "severity_model.joblib")
PLOT_PATH = os.path.join(BASE_DIR, "training_results.png")

COMPONENTS = [
    "Authentication", "Payment", "Database", "API",
    "Dashboard", "Search", "UI", "Notifications",
    "Reports", "Settings", "Other"
]
ERROR_TYPES = [
    "NullPointer", "Crash", "DataCorruption", "SecurityVuln",
    "Timeout", "ConnectionFail", "ServerError500", "DataLoss",
    "WrongPassword", "RenderError", "WrongResults", "NotSending",
    "SlowResponse", "LoadSlow", "FormatError", "AlignmentIssue",
    "SaveFail", "WrongLabel", "ColorIssue", "UXConfusing", "Other"
]


def encode_feature(value: str, vocab: list) -> int:
    try:
        return vocab.index(str(value).strip())
    except ValueError:
        return len(vocab)


def load_and_preprocess(path: str) -> tuple:
    """Load CSV, encode categoricals, return X, y_class, y_reg."""
    print(f"\n📂 Loading dataset: {path}")
    df = pd.read_csv(path)
    print(f"   Rows: {len(df)} | Columns: {list(df.columns)}")

    # Encode categorical features
    df["component_enc"] = df["component"].apply(lambda x: encode_feature(x, COMPONENTS))
    df["error_type_enc"] = df["error_type"].apply(lambda x: encode_feature(x, ERROR_TYPES))

    feature_cols = ["component_enc", "error_type_enc", "user_impact", "frequency", "reproducibility"]
    X = df[feature_cols].values

    y_class = df["severity"].values          # Classification target
    y_reg = df["priority_score"].values      # Regression target

    print(f"   Severity distribution:\n{df['severity'].value_counts().to_string()}\n")
    return X, y_class, y_reg, df


def train_random_forest(X_train, X_test, y_train, y_test) -> RandomForestClassifier:
    """Train and evaluate Random Forest classifier."""
    print("🌲 Training Random Forest Classifier...")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight="balanced",
    )
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cv_scores = cross_val_score(rf, X_train, y_train, cv=5, scoring="accuracy")

    print(f"   Test Accuracy:    {acc:.4f} ({acc*100:.1f}%)")
    print(f"   CV Accuracy:      {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(f"\n   Classification Report:\n{classification_report(y_test, y_pred)}")
    return rf, y_pred


def train_linear_regression(X_train, X_test, y_train, y_test) -> LinearRegression:
    """Train and evaluate Linear Regression for priority score."""
    print("📈 Training Linear Regression (priority_score prediction)...")
    lr = LinearRegression()
    lr.fit(X_train, y_train)

    y_pred = lr.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)

    print(f"   R² Score:  {r2:.4f}")
    print(f"   MAE:       {mae:.4f}")
    print(f"   MSE:       {mse:.4f}\n")
    return lr


def plot_results(rf_model, X_test, y_test, y_pred, df, save_path: str):
    """Generate and save evaluation plots."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("AI-Based Defect Reporting System — ML Model Evaluation", fontsize=14, fontweight="bold")

    # 1. Confusion matrix
    labels = ["Low", "Medium", "High", "Critical"]
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=labels, yticklabels=labels,
                cmap="YlOrRd", ax=axes[0, 0])
    axes[0, 0].set_title("Confusion Matrix — Random Forest")
    axes[0, 0].set_ylabel("True Label")
    axes[0, 0].set_xlabel("Predicted Label")

    # 2. Feature importance
    feature_names = ["Component", "Error Type", "User Impact", "Frequency", "Reproducibility"]
    importances = rf_model.feature_importances_
    axes[0, 1].barh(feature_names, importances, color=["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"])
    axes[0, 1].set_title("Feature Importance — Random Forest")
    axes[0, 1].set_xlabel("Importance Score")

    # 3. Severity distribution in dataset
    severity_counts = df["severity"].value_counts()
    colors = {"Critical": "#e74c3c", "High": "#f39c12", "Medium": "#3498db", "Low": "#2ecc71"}
    bar_colors = [colors.get(s, "#95a5a6") for s in severity_counts.index]
    axes[1, 0].bar(severity_counts.index, severity_counts.values, color=bar_colors)
    axes[1, 0].set_title("Dataset Severity Distribution")
    axes[1, 0].set_ylabel("Count")

    # 4. Priority score distribution by severity
    for sev, color in colors.items():
        subset = df[df["severity"] == sev]["priority_score"]
        if len(subset) > 0:
            axes[1, 1].hist(subset, bins=8, alpha=0.6, label=sev, color=color)
    axes[1, 1].set_title("Priority Score Distribution by Severity")
    axes[1, 1].set_xlabel("Priority Score")
    axes[1, 1].set_ylabel("Count")
    axes[1, 1].legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"📊 Training plots saved: {save_path}")


def main():
    print("=" * 60)
    print("  AI-Based Defect Reporting System — ML Training")
    print("  Unit 4: CrewAI + Classical ML (sklearn)")
    print("=" * 60)

    # Load data
    X, y_class, y_reg, df = load_and_preprocess(DATASET_PATH)

    # Split
    X_train, X_test, yc_train, yc_test = train_test_split(
        X, y_class, test_size=0.2, random_state=42, stratify=y_class
    )
    _, _, yr_train, yr_test = train_test_split(
        X, y_reg, test_size=0.2, random_state=42
    )

    # Train models
    rf_model, y_pred_rf = train_random_forest(X_train, X_test, yc_train, yc_test)
    lr_model = train_linear_regression(X_train, X_test, yr_train, yr_test)

    # Save Random Forest (primary model for predictions)
    joblib.dump(rf_model, MODEL_PATH)
    print(f"✅ Random Forest model saved: {MODEL_PATH}")

    # Plot results
    try:
        plot_results(rf_model, X_test, yc_test, y_pred_rf, df, PLOT_PATH)
    except Exception as e:
        print(f"⚠️  Could not generate plots: {e}")

    # Summary
    acc = accuracy_score(yc_test, y_pred_rf)
    print(f"\n{'='*60}")
    print(f"  ✅ Training Complete!")
    print(f"  Model: Random Forest (100 trees)")
    print(f"  Test Accuracy: {acc*100:.1f}%")
    print(f"  Saved to: {MODEL_PATH}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
