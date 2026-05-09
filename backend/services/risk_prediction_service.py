"""
risk_prediction_service.py
──────────────────────────
ML-powered risk level prediction using a pre-trained Random Forest model.

Predicts compliance risk (LOW / MEDIUM / HIGH / CRITICAL) from product
features extracted during the analysis pipeline.

Falls back to rule-based scoring if the ML model is not available.
"""

import os
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Feature names must match training order
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
    "Household Products": 1.0,
    "Medical Products": 2.0,
    "Health Supplements": 1.3,
}


class RiskPredictionService:
    """ML-based compliance risk prediction."""

    def __init__(self):
        self.model = None
        self.label_encoder = None
        self._loaded = False
        self._load_model()

    def _load_model(self):
        """Load the pre-trained Random Forest model."""
        try:
            import joblib

            model_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "ml_models",
            )
            model_path = os.path.join(model_dir, "risk_predictor.joblib")
            encoder_path = os.path.join(model_dir, "risk_label_encoder.joblib")

            if os.path.exists(model_path) and os.path.exists(encoder_path):
                self.model = joblib.load(model_path)
                self.label_encoder = joblib.load(encoder_path)
                self._loaded = True
                logger.info("RiskPredictionService: ML model loaded successfully")
            else:
                logger.warning(
                    "Risk model files not found at %s — using rule-based fallback. "
                    "Run: python ml_models/train_risk_model.py",
                    model_dir,
                )
        except ImportError:
            logger.warning("joblib not installed — using rule-based risk prediction")
        except Exception as e:
            logger.error(f"Failed to load risk model: {e}")

    @property
    def is_ml_available(self) -> bool:
        return self._loaded and self.model is not None

    def predict(self, fields: dict[str, str], category: str = "") -> dict[str, Any]:
        """
        Predict risk level from extracted product fields.

        Args:
            fields: dict of field_name → value (from extraction pipeline)
            category: product category string

        Returns:
            {
                "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
                "confidence": 0.0–1.0,
                "method": "ml" | "rule_based",
                "contributing_factors": [...],
                "feature_vector": [...]
            }
        """
        features = self._build_features(fields, category)

        if self.is_ml_available:
            return self._predict_ml(features, fields)
        else:
            return self._predict_rule_based(features, fields)

    def _build_features(self, fields: dict[str, str], category: str) -> list[float]:
        """Build feature vector from extracted fields."""

        def has(key: str) -> int:
            val = fields.get(key, "")
            return 1 if val and str(val).strip() else 0

        total_fields = 16
        present_count = sum([
            has("product_name"), has("brand_name"),
            has("manufacturer_name"), has("manufacturer_address"),
            has("importer_name"), has("importer_address"),
            has("mrp"), has("net_quantity"),
            has("manufacturing_date"), has("expiry_date"),
            has("batch_number"), has("customer_care"),
            has("country_of_origin"), has("barcode"),
            has("license_number"),
            1,  # category itself
        ])
        missing = total_fields - min(present_count, total_fields)
        completeness = present_count / total_fields

        is_imported = 1 if has("importer_name") or has("importer_address") else 0
        cat_weight = CATEGORY_WEIGHTS.get(category, 1.0)

        return [
            missing,
            total_fields,
            completeness,
            has("mrp"),
            has("manufacturer_name"),
            has("expiry_date"),
            has("license_number"),      # FSSAI
            has("net_quantity"),
            has("manufacturing_date"),
            has("customer_care"),
            has("country_of_origin"),
            has("batch_number"),
            has("barcode"),
            is_imported,
            cat_weight,
        ]

    def _predict_ml(self, features: list[float], fields: dict) -> dict[str, Any]:
        """Use ML model for prediction."""
        try:
            import numpy as np

            X = np.array([features])
            pred_idx = self.model.predict(X)[0]
            probas = self.model.predict_proba(X)[0]
            risk_level = self.label_encoder.inverse_transform([pred_idx])[0]
            confidence = float(probas[pred_idx])

            # Identify contributing factors
            factors = self._get_contributing_factors(features, fields)

            return {
                "risk_level": risk_level,
                "confidence": round(confidence, 4),
                "method": "ml",
                "contributing_factors": factors,
                "feature_vector": features,
                "probabilities": {
                    label: round(float(prob), 4)
                    for label, prob in zip(
                        self.label_encoder.classes_, probas
                    )
                },
            }
        except Exception as e:
            logger.error(f"ML prediction failed, falling back: {e}")
            return self._predict_rule_based(features, fields)

    def _predict_rule_based(self, features: list[float], fields: dict) -> dict[str, Any]:
        """Rule-based fallback when ML model unavailable."""
        completeness = features[2]
        has_mrp = features[3]
        has_manufacturer = features[4]
        has_expiry = features[5]
        has_fssai = features[6]
        cat_weight = features[14]

        score = completeness * 100

        # Penalties for critical missing fields
        if not has_mrp:
            score -= 20
        if not has_manufacturer:
            score -= 15
        if not has_expiry:
            score -= 10
        if not has_fssai:
            score -= 15

        score *= (1.0 / max(cat_weight, 0.5))

        if score >= 85:
            risk = "LOW"
        elif score >= 65:
            risk = "MEDIUM"
        elif score >= 40:
            risk = "HIGH"
        else:
            risk = "CRITICAL"

        factors = self._get_contributing_factors(features, fields)

        return {
            "risk_level": risk,
            "confidence": 0.75,
            "method": "rule_based",
            "contributing_factors": factors,
            "feature_vector": features,
            "score": round(score, 2),
        }

    def _get_contributing_factors(
        self, features: list[float], fields: dict
    ) -> list[str]:
        """Identify the main risk-contributing factors."""
        factors = []

        critical_fields = {
            "mrp": ("MRP", 3),
            "manufacturer_name": ("Manufacturer Name", 4),
            "expiry_date": ("Expiry Date", 5),
            "license_number": ("FSSAI/License Number", 6),
            "net_quantity": ("Net Quantity", 7),
        }

        for field_key, (display_name, feat_idx) in critical_fields.items():
            if features[feat_idx] == 0:
                factors.append(f"Missing: {display_name}")

        if features[0] > 4:
            factors.append(f"High missing field count: {int(features[0])}")

        if features[14] >= 1.5:
            factors.append("High-risk product category")

        return factors
