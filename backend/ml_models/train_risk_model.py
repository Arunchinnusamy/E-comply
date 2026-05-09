"""
train_risk_model.py
────────────────────
Train a Random Forest model to predict compliance risk level
from product features.

Features:
    - missing_field_count
    - total_fields
    - field_completeness_ratio
    - has_mrp, has_manufacturer, has_expiry, has_fssai
    - has_net_quantity, has_mfg_date, has_customer_care
    - has_country_of_origin, has_batch_number, has_barcode
    - is_imported
    - category_risk_weight

Output classes: LOW, MEDIUM, HIGH, CRITICAL

Usage:
    python ml_models/train_risk_model.py

Outputs:
    ml_models/risk_predictor.joblib
    ml_models/risk_label_encoder.joblib
"""

import os
import random
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Risk weight per category
CATEGORY_WEIGHTS = {
    "Food": 1.5,
    "Dairy": 1.8,
    "FMCG": 1.0,
    "Cosmetics": 1.2,
    "Pharma": 2.0,
    "Electronics": 1.0,
    "Pet Care": 1.0,
    "Stationery": 0.5,
    "Packaged Goods": 1.0,
}

FEATURE_NAMES = [
    "missing_field_count",
    "total_fields",
    "field_completeness_ratio",
    "has_mrp",
    "has_manufacturer",
    "has_expiry",
    "has_fssai",
    "has_net_quantity",
    "has_mfg_date",
    "has_customer_care",
    "has_country_of_origin",
    "has_batch_number",
    "has_barcode",
    "is_imported",
    "category_risk_weight",
]


def generate_training_data(n_samples: int = 2000) -> tuple:
    """Generate synthetic training data for risk prediction."""
    random.seed(42)
    np.random.seed(42)

    X = []
    y = []

    categories = list(CATEGORY_WEIGHTS.keys())

    for _ in range(n_samples):
        category = random.choice(categories)
        cat_weight = CATEGORY_WEIGHTS[category]
        total_fields = 16
        is_imported = random.random() > 0.7

        # Randomly decide which fields are present
        has_mrp = random.random() > 0.08
        has_manufacturer = random.random() > 0.05
        has_expiry = random.random() > 0.15
        has_fssai = random.random() > 0.20 if category in ("Food", "Dairy") else random.random() > 0.6
        has_net_quantity = random.random() > 0.10
        has_mfg_date = random.random() > 0.15
        has_customer_care = random.random() > 0.25
        has_country_of_origin = random.random() > 0.20
        has_batch_number = random.random() > 0.30
        has_barcode = random.random() > 0.25

        present_fields = sum([
            has_mrp, has_manufacturer, has_expiry, has_fssai,
            has_net_quantity, has_mfg_date, has_customer_care,
            has_country_of_origin, has_batch_number, has_barcode,
            1, 1, 1, 1,  # product_name, brand, mfg_address, importer assumed
        ])
        missing = total_fields - min(present_fields, total_fields)
        completeness = present_fields / total_fields

        features = [
            missing,
            total_fields,
            completeness,
            int(has_mrp),
            int(has_manufacturer),
            int(has_expiry),
            int(has_fssai),
            int(has_net_quantity),
            int(has_mfg_date),
            int(has_customer_care),
            int(has_country_of_origin),
            int(has_batch_number),
            int(has_barcode),
            int(is_imported),
            cat_weight,
        ]

        # Determine risk level based on rules (training labels)
        severity_score = 0

        # Critical fields
        if not has_mrp:
            severity_score += 25 * cat_weight
        if not has_manufacturer:
            severity_score += 20 * cat_weight
        if not has_net_quantity:
            severity_score += 20 * cat_weight

        # High severity
        if not has_expiry and category in ("Food", "Dairy", "Pharma", "Cosmetics"):
            severity_score += 25 * cat_weight
        if not has_fssai and category in ("Food", "Dairy"):
            severity_score += 30 * cat_weight
        if not has_mfg_date:
            severity_score += 10 * cat_weight
        if not has_customer_care:
            severity_score += 8 * cat_weight
        if not has_country_of_origin and is_imported:
            severity_score += 15 * cat_weight

        # Medium severity
        if not has_batch_number:
            severity_score += 3
        if not has_barcode:
            severity_score += 2

        # Add slight randomness to make it realistic
        severity_score += random.gauss(0, 3)

        if severity_score <= 5:
            risk = "LOW"
        elif severity_score <= 20:
            risk = "MEDIUM"
        elif severity_score <= 45:
            risk = "HIGH"
        else:
            risk = "CRITICAL"

        X.append(features)
        y.append(risk)

    return np.array(X), np.array(y)


def train():
    """Train the risk prediction model."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.preprocessing import LabelEncoder
    import joblib

    print("\n" + "=" * 60)
    print("  E-COMPLY — RISK PREDICTION MODEL TRAINING")
    print("=" * 60)

    # Generate data
    X, y_str = generate_training_data(3000)

    le = LabelEncoder()
    y = le.fit_transform(y_str)

    print(f"\n📊 Training samples: {len(X)}")
    print(f"🏷️  Classes: {list(le.classes_)}")

    # Class distribution
    unique, counts = np.unique(y_str, return_counts=True)
    for cls, cnt in zip(unique, counts):
        print(f"   {cls:<10} {cnt:>5} ({cnt/len(y)*100:.1f}%)")

    # Train model
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    # Cross-validate
    print("\n🔄 Cross-validating...")
    scores = cross_val_score(clf, X, y, cv=5, scoring="accuracy")
    print(f"   Accuracy: {scores.mean():.4f} (+/- {scores.std():.4f})")

    # Train on full data
    print("\n🏋️ Training on full dataset...")
    clf.fit(X, y)

    # Feature importance
    print("\n📈 Feature Importance:")
    importances = sorted(
        zip(FEATURE_NAMES, clf.feature_importances_),
        key=lambda x: x[1], reverse=True
    )
    for fname, imp in importances:
        bar = "█" * int(imp * 50)
        print(f"   {fname:<28} {imp:.4f} {bar}")

    # Save model
    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(model_dir, "risk_predictor.joblib")
    encoder_path = os.path.join(model_dir, "risk_label_encoder.joblib")

    joblib.dump(clf, model_path)
    joblib.dump(le, encoder_path)

    print(f"\n💾 Model saved: {model_path}")
    print(f"💾 Encoder saved: {encoder_path}")

    # Test predictions
    print("\n🧪 Sample predictions:")
    test_cases = [
        ("All fields present (Food)",
         [0, 16, 1.0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1.5]),
        ("Missing MRP + FSSAI (Food)",
         [2, 16, 0.875, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1.5]),
        ("Missing 5 fields (Pharma)",
         [5, 16, 0.69, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 2.0]),
        ("Imported, no origin (Electronics)",
         [3, 16, 0.81, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1.0]),
        ("Nearly empty label",
         [10, 16, 0.375, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1.0]),
    ]
    for desc, features in test_cases:
        pred_idx = clf.predict([features])[0]
        probas = clf.predict_proba([features])[0]
        pred_label = le.inverse_transform([pred_idx])[0]
        confidence = probas[pred_idx] * 100
        print(f"   {desc:<40} → {pred_label:<10} ({confidence:.1f}%)")

    print("\n" + "=" * 60)
    print("  DONE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    train()
