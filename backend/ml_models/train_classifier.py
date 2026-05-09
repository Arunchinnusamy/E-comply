"""
train_classifier.py
────────────────────
Train a product category classifier using TF-IDF + Random Forest,
then export as a lightweight model for on-device / backend inference.

Categories:
    Food, Dairy, FMCG, Cosmetics, Pharma, Electronics, Pet Care, Stationery

Usage:
    python ml_models/train_classifier.py

Outputs:
    ml_models/product_classifier.joblib   — scikit-learn pipeline
    ml_models/label_encoder.joblib        — label encoder
"""

import os
import sys
import json
import random
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ─── Synthetic training data ──────────────────────────────────────────────────
# Each entry: (sample text snippet, category label)
# Generated from realistic product label text patterns

TRAINING_DATA = [
    # ── Food ──────────────────────────────────────────────────────────────
    ("Tata Salt Iodized Salt Net Wt 1kg MRP Rs 28 FSSAI 10016011000456 Mfg By Tata Consumer Products", "Food"),
    ("Aashirvaad Whole Wheat Atta 5kg nutritional information protein fiber ingredients wheat", "Food"),
    ("Maggi 2-Minute Noodles Masala 70g instant noodles wheat flour spices FSSAI", "Food"),
    ("Kissan Mixed Fruit Jam 500g ingredients sugar fruit pectin best before", "Food"),
    ("MDH Chilli Powder 100g spice masala red chilli FSSAI vegetarian", "Food"),
    ("Haldiram Bhujia Namkeen 400g snack besan ingredients FSSAI", "Food"),
    ("Amul Butter 500g pasteurized butter salt milk fat FSSAI", "Food"),
    ("Fortune Sunflower Oil 1L refined cooking oil vitamin E FSSAI", "Food"),
    ("Bournvita Health Drink 500g chocolate malt nutritional value protein", "Food"),
    ("Parle-G Gold Biscuits 100g wheat flour sugar glucose biscuit FSSAI", "Food"),
    ("Catch Italian Seasoning herbs oregano mixed dried herbs food", "Food"),
    ("Lays Classic Salted Chips 52g potato chips fried snack FSSAI", "Food"),
    ("Real Fruit Power Mixed Fruit Juice 1L no added sugar preservative free FSSAI", "Food"),
    ("Cadbury Dairy Milk Chocolate 50g cocoa sugar milk solids confectionery FSSAI", "Food"),
    ("Saffola Gold Edible Oil 1L blended oil rice bran sunflower FSSAI", "Food"),
    ("Britannia Good Day Cashew Cookies 250g biscuit cookies cashew FSSAI", "Food"),
    ("Patanjali Cow Ghee 500ml pure desi ghee clarified butter FSSAI", "Food"),
    ("Nestle KitKat Wafer 37.3g chocolate wafer crispy FSSAI", "Food"),
    ("Everest Garam Masala 100g blended spice powder coriander cumin FSSAI", "Food"),
    ("MTR Ready To Eat Paneer Butter Masala 300g retort pouch FSSAI", "Food"),

    # ── Dairy ─────────────────────────────────────────────────────────────
    ("Amul Taaza Toned Milk 500ml pasteurized homogenized FSSAI dairy", "Dairy"),
    ("Mother Dairy Classic Curd 400g dahi probiotic fermented milk FSSAI", "Dairy"),
    ("Amul Cheese Slices 200g processed cheese slice milk protein FSSAI", "Dairy"),
    ("Nestle A+ Slim Milk 500ml skimmed milk low fat dairy FSSAI", "Dairy"),
    ("Go Cheese Spread 200g cream cheese spread pasteurized FSSAI", "Dairy"),
    ("Milky Mist Paneer 200g fresh cottage cheese milk product FSSAI", "Dairy"),
    ("Amul Ice Cream Vanilla 750ml frozen dessert milk cream sugar FSSAI", "Dairy"),
    ("Verka Lassi 200ml sweet buttermilk flavored dairy drink FSSAI", "Dairy"),
    ("Mother Dairy Mishti Doi 100g sweetened yogurt Bengali style FSSAI", "Dairy"),
    ("Amul Masti Buttermilk 200ml spiced chaas dairy beverage FSSAI", "Dairy"),

    # ── FMCG ──────────────────────────────────────────────────────────────
    ("Surf Excel Matic Liquid Detergent 1L front load washing machine laundry", "FMCG"),
    ("Vim Dishwash Bar 200g dish cleaning soap grease cutting", "FMCG"),
    ("Harpic Power Plus Toilet Cleaner 500ml disinfectant bathroom 10x clean", "FMCG"),
    ("Lizol Floor Cleaner Citrus 500ml surface disinfectant mopping", "FMCG"),
    ("Ariel Complete Detergent Powder 1kg washing powder stain removal laundry", "FMCG"),
    ("Comfort Fabric Conditioner 800ml after wash softener fragrance", "FMCG"),
    ("Scotch Brite Scrub Pad green nylon dishwash utensil cleaning", "FMCG"),
    ("Domex Fresh Guard Toilet Cleaner 750ml thick liquid bleach disinfectant", "FMCG"),
    ("Godrej Aer Matic Room Freshener 225ml automatic spray air freshener", "FMCG"),
    ("Tide Plus Double Power Detergent 2kg washing powder jasmine rose", "FMCG"),

    # ── Cosmetics ─────────────────────────────────────────────────────────
    ("Dove Deeply Nourishing Body Wash 250ml moisturizing cream skin care", "Cosmetics"),
    ("Lakme Absolute Skin Natural Mousse Foundation 25ml makeup face", "Cosmetics"),
    ("Garnier Micellar Cleansing Water 125ml makeup remover face cleanser", "Cosmetics"),
    ("L'Oreal Paris Shampoo 340ml hair fall repair keratin smooth", "Cosmetics"),
    ("Nivea Soft Moisturizing Cream 200ml jojoba oil vitamin E skin", "Cosmetics"),
    ("Biotique Bio Green Apple Shampoo 190ml herbal natural hair care", "Cosmetics"),
    ("Maybelline New York Colossal Kajal 0.35g eye makeup smudge proof", "Cosmetics"),
    ("Vaseline Intensive Care Body Lotion 400ml deep moisture cocoa butter", "Cosmetics"),
    ("Himalaya Purifying Neem Face Wash 150ml acne pimples herbal", "Cosmetics"),
    ("Pond's White Beauty SPF 30 Day Cream 50g lightening fairness sunscreen", "Cosmetics"),
    ("Sunsilk Hair Fall Solution Shampoo 340ml onion jojoba oil haircare", "Cosmetics"),
    ("Lotus Herbals Safe Sun UV Screen Matte Gel SPF 50 100g sunscreen", "Cosmetics"),

    # ── Pharma ────────────────────────────────────────────────────────────
    ("Crocin Advance Paracetamol 500mg Tablet 15s pain fever headache analgesic drug license", "Pharma"),
    ("Dolo 650 Paracetamol 650mg antipyretic tablet strip of 15 prescription", "Pharma"),
    ("Vicks VapoRub 50ml topical ointment cough cold camphor menthol", "Pharma"),
    ("Strepsils Orange Lozenges 8s sore throat antiseptic lozenge", "Pharma"),
    ("Volini Spray 40g diclofenac pain relief muscle joint spray", "Pharma"),
    ("Benadryl Cough Syrup 100ml diphenhydramine antihistamine", "Pharma"),
    ("Betadine Antiseptic Solution 50ml povidone iodine wound care", "Pharma"),
    ("Dabur Chyawanprash 500g ayurvedic immunity booster herbal supplement", "Pharma"),
    ("Moov Pain Relief Cream 50g back pain muscle ache diclofenac", "Pharma"),
    ("Zandu Balm 8ml headache body pain pain relief ayurvedic", "Pharma"),
    ("Burnol Antiseptic Cream 20g burns cuts wounds first aid drug license", "Pharma"),
    ("Disprin Aspirin 350mg tablet effervescent pain fever blood thinner", "Pharma"),

    # ── Electronics ───────────────────────────────────────────────────────
    ("Duracell AA Alkaline Battery 4 Pack 1.5V long lasting power BIS", "Electronics"),
    ("Syska LED Bulb 9W 6500K Cool White B22 energy saving BIS certified", "Electronics"),
    ("Mi USB Type C Cable 1m braided fast charging data cable", "Electronics"),
    ("Portronics Power Bank 10000mAh dual USB lithium polymer battery", "Electronics"),
    ("boAt Rockerz 450 Bluetooth Headphones wireless over ear 15hr battery", "Electronics"),
    ("Samsung 32GB EVO Plus MicroSD Memory Card Class 10 UHS-I", "Electronics"),
    ("Havells 1200mm Ceiling Fan 75W copper motor ISI marked BIS", "Electronics"),
    ("Philips Trimmer BT1210 beard trimmer cordless USB charging", "Electronics"),
    ("JBL Go 3 Portable Speaker Bluetooth waterproof wireless audio", "Electronics"),
    ("Zebronics Zeb Transformer Gaming Mouse USB wired 3200 DPI RGB LED", "Electronics"),

    # ── Pet Care ──────────────────────────────────────────────────────────
    ("Pedigree Adult Dry Dog Food Chicken Vegetables 3kg pet food nutrition", "Pet Care"),
    ("Whiskas Cat Food Tuna 480g pouch wet cat food feline nutrition", "Pet Care"),
    ("Drools Puppy Chicken Egg 3kg dog food puppy nutrition growth", "Pet Care"),
    ("Royal Canin Maxi Adult Dog Food 4kg breed health nutrition", "Pet Care"),
    ("Himalaya Erina Plus Coat Cleanser 200ml pet shampoo dog grooming", "Pet Care"),
    ("Kennel Kitchen Chicken Chunks in Gravy 100g wet dog food", "Pet Care"),
    ("Me-O Cat Food Tuna 1.2kg kitten adult cat fish flavored pet", "Pet Care"),
    ("Beaphar Tick Flea Spray 150ml pet insect repellent dog cat", "Pet Care"),

    # ── Stationery ────────────────────────────────────────────────────────
    ("Classmate Long Notebook 180 Pages Single Line 29.7cm writing notebook", "Stationery"),
    ("Cello Gripper Ball Pen Blue 0.5mm writing instrument smooth ink flow", "Stationery"),
    ("Faber Castell 9000 Pencil HB drawing writing graphite pencil", "Stationery"),
    ("Camlin Kokuyo Geometry Box compass protractor divider ruler set", "Stationery"),
    ("Fevicol SH 50g white adhesive craft glue synthetic resin adhesive", "Stationery"),
    ("Apsara Non Dust Eraser rubber eraser drawing correction school", "Stationery"),
    ("Navneet Youva Notebook 200 Pages A4 size college exercise book", "Stationery"),
    ("Reynolds 045 Fine Carbure Ball Pen black blue red ink pen", "Stationery"),
]


def augment_data(data: list, multiplier: int = 5) -> list:
    """Generate augmented samples by shuffling words and adding noise."""
    augmented = list(data)
    for text, label in data:
        words = text.split()
        for _ in range(multiplier):
            # Shuffle word order slightly
            shuffled = words.copy()
            if len(shuffled) > 3:
                i = random.randint(0, len(shuffled) - 2)
                shuffled[i], shuffled[i + 1] = shuffled[i + 1], shuffled[i]
            # Randomly drop a word
            if len(shuffled) > 4 and random.random() > 0.5:
                shuffled.pop(random.randint(0, len(shuffled) - 1))
            augmented.append((" ".join(shuffled), label))
    return augmented


def train():
    """Train the product category classifier."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import LabelEncoder
    import joblib

    print("\n" + "=" * 60)
    print("  E-COMPLY — PRODUCT CLASSIFIER TRAINING")
    print("=" * 60)

    # Augment training data
    random.seed(42)
    data = augment_data(TRAINING_DATA, multiplier=8)
    random.shuffle(data)

    texts = [t for t, _ in data]
    labels = [l for _, l in data]

    print(f"\n📊 Training samples: {len(texts)}")
    print(f"📂 Categories: {sorted(set(labels))}")

    # Encode labels
    le = LabelEncoder()
    y = le.fit_transform(labels)
    print(f"🏷️  Label classes: {list(le.classes_)}")

    # Build pipeline
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=3000,
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=2,
            stop_words="english",
        )),
        ("clf", RandomForestClassifier(
            n_estimators=150,
            max_depth=20,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced",
        )),
    ])

    # Cross-validate
    print("\n🔄 Cross-validating...")
    scores = cross_val_score(pipeline, texts, y, cv=5, scoring="accuracy")
    print(f"   Accuracy: {scores.mean():.4f} (+/- {scores.std():.4f})")

    # Train on full data
    print("\n🏋️ Training on full dataset...")
    pipeline.fit(texts, y)

    # Save model
    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(model_dir, "product_classifier.joblib")
    encoder_path = os.path.join(model_dir, "label_encoder.joblib")

    joblib.dump(pipeline, model_path)
    joblib.dump(le, encoder_path)

    print(f"\n💾 Model saved: {model_path}")
    print(f"💾 Encoder saved: {encoder_path}")

    # Test predictions
    print("\n🧪 Sample predictions:")
    test_samples = [
        "Tata Salt 1kg iodized FSSAI license",
        "Dove Shampoo 340ml hair care keratin",
        "Duracell AA Battery 4 pack BIS",
        "Crocin Paracetamol 500mg tablet drug",
        "Pedigree Dog Food Chicken 3kg pet",
        "Classmate Notebook 200 pages ruled",
        "Harpic Toilet Cleaner 500ml disinfectant",
        "Amul Cheese Slices 200g processed milk",
    ]
    for sample in test_samples:
        pred_idx = pipeline.predict([sample])[0]
        probas = pipeline.predict_proba([sample])[0]
        pred_label = le.inverse_transform([pred_idx])[0]
        confidence = probas[pred_idx] * 100
        print(f"   {sample[:50]:<52} → {pred_label:<12} ({confidence:.1f}%)")

    print("\n" + "=" * 60)
    print("  DONE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    train()
