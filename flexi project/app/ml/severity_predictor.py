"""
app/ml/severity_predictor.py
Unit 4 — Classical ML-based defect severity predictor.

Uses scikit-learn Random Forest to classify defects as:
  Low | Medium | High | Critical

Features used:
  - component (categorical → encoded)
  - error_type (categorical → encoded)
  - user_impact (1–5 integer scale)
  - frequency (1–5 integer scale)
  - reproducibility (1–5 integer scale)

Trained model is saved to disk as severity_model.joblib.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = os.getenv("MODEL_PATH", "./app/ml/severity_model.joblib")
ENCODER_PATH = "./app/ml/label_encoders.joblib"

# Severity ordinal mapping for display
SEVERITY_COLORS = {
    "Low": "🟢",
    "Medium": "🟡",
    "High": "🟠",
    "Critical": "🔴",
}

# Valid components and error types (used for encoding)
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


def _encode_feature(value: str, vocab: list[str]) -> int:
    """Encode a categorical string as an integer index."""
    value = str(value).strip()
    if value in vocab:
        return vocab.index(value)
    return len(vocab)  # 'Other' / unknown → last index


def _build_features(
    component: str,
    error_type: str,
    user_impact: int,
    frequency: int,
    reproducibility: int,
) -> np.ndarray:
    """Build the feature vector for prediction."""
    return np.array([[
        _encode_feature(component, COMPONENTS),
        _encode_feature(error_type, ERROR_TYPES),
        int(user_impact),
        int(frequency),
        int(reproducibility),
    ]])


def predict_severity(
    component: str,
    error_type: str,
    user_impact: int,
    frequency: int,
    reproducibility: int,
) -> dict:
    """
    Predict defect severity using the trained Random Forest model.

    Args:
        component: Software component (e.g., 'Authentication', 'Payment')
        error_type: Type of error (e.g., 'NullPointer', 'Crash')
        user_impact: How severely users are affected (1=minimal, 5=critical)
        frequency: How often the defect occurs (1=rare, 5=always)
        reproducibility: How easily it can be reproduced (1=hard, 5=always)

    Returns:
        dict with keys: severity, confidence, priority_score, explanation
    """
    if not os.path.exists(MODEL_PATH):
        # Fallback: rule-based prediction if model not trained yet
        return _rule_based_prediction(component, error_type, user_impact, frequency, reproducibility)

    try:
        model = joblib.load(MODEL_PATH)
        features = _build_features(component, error_type, user_impact, frequency, reproducibility)
        
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        classes = model.classes_
        
        confidence = float(max(probabilities)) * 100
        priority_score = user_impact * frequency + reproducibility

        return {
            "severity": prediction,
            "icon": SEVERITY_COLORS.get(prediction, "⚪"),
            "confidence": round(confidence, 1),
            "priority_score": priority_score,
            "probabilities": {c: round(float(p) * 100, 1) for c, p in zip(classes, probabilities)},
            "explanation": (
                f"Based on: component={component}, error_type={error_type}, "
                f"user_impact={user_impact}/5, frequency={frequency}/5, "
                f"reproducibility={reproducibility}/5. "
                f"Priority score: {priority_score}/30."
            ),
            "model": "Random Forest (sklearn)",
        }
    except Exception as e:
        return _rule_based_prediction(component, error_type, user_impact, frequency, reproducibility)


def _rule_based_prediction(
    component: str,
    error_type: str,
    user_impact: int,
    frequency: int,
    reproducibility: int,
) -> dict:
    """Rule-based fallback predictor when ML model is unavailable."""
    priority = user_impact * frequency + reproducibility

    if priority >= 22 or error_type in ["SecurityVuln", "DataCorruption", "Crash"]:
        severity = "Critical"
    elif priority >= 16 or error_type in ["ConnectionFail", "ServerError500", "DataLoss"]:
        severity = "High"
    elif priority >= 10:
        severity = "Medium"
    else:
        severity = "Low"

    return {
        "severity": severity,
        "icon": SEVERITY_COLORS.get(severity, "⚪"),
        "confidence": 75.0,
        "priority_score": priority,
        "probabilities": {},
        "explanation": (
            f"Rule-based prediction (ML model not yet trained). "
            f"Priority score: {priority}/30. "
            f"Run `python app/ml/train_model.py` to enable ML predictions."
        ),
        "model": "Rule-based fallback",
    }


def get_severity_tool_definition() -> dict:
    """Return tool definition for agent function calling."""
    return {
        "name": "predict_severity",
        "description": (
            "Predict the severity of a software defect using a trained Machine Learning model. "
            "Returns severity level (Low/Medium/High/Critical) with confidence score."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "component": {
                    "type": "string",
                    "description": f"Affected component. One of: {', '.join(COMPONENTS)}",
                },
                "error_type": {
                    "type": "string",
                    "description": f"Type of error. One of: {', '.join(ERROR_TYPES[:10])}...",
                },
                "user_impact": {
                    "type": "integer",
                    "description": "User impact scale 1-5 (1=minimal, 5=all users affected)",
                },
                "frequency": {
                    "type": "integer",
                    "description": "Occurrence frequency scale 1-5 (1=rare, 5=always)",
                },
                "reproducibility": {
                    "type": "integer",
                    "description": "Reproducibility scale 1-5 (1=hard to reproduce, 5=always)",
                },
            },
            "required": ["component", "error_type", "user_impact", "frequency", "reproducibility"],
        },
        "function": predict_severity,
    }


if __name__ == "__main__":
    # Test prediction
    result = predict_severity(
        component="Authentication",
        error_type="NullPointer",
        user_impact=5,
        frequency=4,
        reproducibility=5,
    )
    print(json.dumps(result, indent=2))
