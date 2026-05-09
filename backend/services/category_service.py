"""
category_service.py
-------------------
AI-based product category detection for Legal Metrology compliance.

Automatically identifies product category from OCR-extracted text using
keyword matching and contextual analysis.

Categories:
    Food, Cosmetics, Electronics, Packaged Goods,
    Medical Products, Health Supplements, Household Products
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Category keyword dictionaries
# ──────────────────────────────────────────────────────────────────────────────

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Food": [
        "biscuit", "biscuits", "cookie", "cookies", "chips", "namkeen",
        "snack", "snacks", "noodle", "noodles", "pasta", "rice", "flour",
        "atta", "sugar", "salt", "oil", "ghee", "butter", "cheese",
        "milk", "curd", "yogurt", "bread", "jam", "sauce", "ketchup",
        "pickle", "spice", "masala", "turmeric", "tea", "coffee",
        "juice", "chocolate", "candy", "sweet", "cereal", "oats",
        "protein bar", "energy bar", "rusk", "cake", "muffin",
        "instant mix", "ready to eat", "frozen food", "ice cream",
        "paneer", "tofu", "dal", "pulses", "lentil", "honey",
        "vinegar", "soya", "corn", "wheat", "maida", "suji", "besan",
        "poha", "muesli", "granola", "fssai", "food safety",
        "nutritional information", "ingredients", "allergen",
        "vegetarian", "non-vegetarian", "veg", "non veg",
    ],
    "Cosmetics": [
        "shampoo", "conditioner", "soap", "face wash", "body wash",
        "lotion", "cream", "moisturizer", "sunscreen", "spf",
        "lipstick", "mascara", "foundation", "concealer", "eyeliner",
        "nail polish", "perfume", "deodorant", "deo", "hair oil",
        "hair gel", "hair spray", "serum", "toner", "cleanser",
        "face pack", "face mask", "scrub", "exfoliant", "beauty",
        "cosmetic", "makeup", "make-up", "kajal", "sindoor",
        "fairness", "brightening", "anti-aging", "anti aging",
        "skin care", "skincare", "hair care", "haircare",
        "body lotion", "hand cream", "foot cream", "lip balm",
        "talcum powder", "talc", "compact powder", "blush",
    ],
    "Electronics": [
        "charger", "cable", "usb", "adapter", "power bank",
        "headphone", "headphones", "earphone", "earphones", "earbuds",
        "speaker", "bluetooth", "wifi", "router", "mouse", "keyboard",
        "monitor", "laptop", "mobile", "phone", "tablet", "smartwatch",
        "watch", "camera", "lens", "battery", "batteries", "led",
        "bulb", "fan", "remote", "controller", "hdmi", "pendrive",
        "pen drive", "memory card", "sd card", "hard disk", "ssd",
        "printer", "scanner", "projector", "tv", "television",
        "refrigerator", "washing machine", "microwave", "oven",
        "iron", "mixer", "grinder", "blender", "juicer",
        "air conditioner", "ac", "heater", "geyser",
        "voltage", "watt", "ampere", "electric", "electronic",
        "bis", "bureau of indian standards",
    ],
    "Medical Products": [
        "medicine", "tablet", "capsule", "syrup", "injection",
        "ointment", "gel", "drops", "inhaler", "bandage", "gauze",
        "surgical", "medical", "pharmaceutical", "drug", "dosage",
        "prescription", "otc", "antiseptic", "disinfectant",
        "thermometer", "bp monitor", "glucometer", "oximeter",
        "mask", "n95", "gloves", "syringe", "saline",
        "ayurvedic", "homeopathic", "unani", "siddha",
        "composition", "contraindication", "side effect",
        "drug license", "mfg lic", "manufacturing license",
    ],
    "Health Supplements": [
        "supplement", "vitamin", "mineral", "protein powder",
        "whey", "bcaa", "creatine", "omega", "fish oil",
        "multivitamin", "calcium", "iron", "zinc", "magnesium",
        "probiotic", "prebiotic", "fiber", "fibre",
        "dietary supplement", "nutraceutical", "health drink",
        "energy drink", "electrolyte", "collagen", "biotin",
        "ashwagandha", "giloy", "tulsi", "amla", "moringa",
        "herbal", "ayurvedic supplement", "immunity booster",
        "weight gainer", "mass gainer", "fat burner",
        "suggested use", "serving size", "daily value",
    ],
    "Household Products": [
        "detergent", "soap bar", "dish wash", "dishwash",
        "floor cleaner", "toilet cleaner", "glass cleaner",
        "surface cleaner", "air freshener", "room freshener",
        "insecticide", "mosquito", "repellent", "pesticide",
        "phenyl", "bleach", "disinfectant spray",
        "fabric softener", "stain remover", "laundry",
        "broom", "mop", "sponge", "scrubber",
        "tissue", "paper towel", "napkin", "diaper",
        "sanitary pad", "sanitary napkin", "incense", "agarbatti",
        "candle", "matchbox", "lighter",
        "bucket", "dustbin", "hanger",
        "household", "home care",
    ],
}

# Catch-all when no specific category is detected
DEFAULT_CATEGORY = "Packaged Goods"


class CategoryService:
    """Detect product category from OCR-extracted text."""

    def detect_category(self, text: str) -> str:
        """
        Analyse *text* and return the best-matching product category.

        Args:
            text: OCR-extracted or product-description text

        Returns:
            str: One of the seven standard categories
        """
        if not text or not text.strip():
            return DEFAULT_CATEGORY

        text_lower = text.lower()

        scores: dict[str, int] = {cat: 0 for cat in CATEGORY_KEYWORDS}

        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                # Use word-boundary matching to avoid partial hits
                pattern = rf'\b{re.escape(keyword)}\b'
                matches = re.findall(pattern, text_lower)
                scores[category] += len(matches)

        best_category = max(scores, key=scores.get)  # type: ignore[arg-type]

        if scores[best_category] == 0:
            logger.info("No category keywords matched — defaulting to '%s'", DEFAULT_CATEGORY)
            return DEFAULT_CATEGORY

        logger.info(
            "Category detected: %s (score %d) — scores: %s",
            best_category,
            scores[best_category],
            {k: v for k, v in scores.items() if v > 0},
        )
        return best_category

    def detect_category_from_product_name(self, product_name: str) -> str:
        """
        Lightweight variant that tries to categorise from the product name
        alone (useful when full OCR text is unavailable).
        """
        return self.detect_category(product_name)
