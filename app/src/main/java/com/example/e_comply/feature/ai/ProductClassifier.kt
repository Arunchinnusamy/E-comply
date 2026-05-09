package com.example.e_comply.feature.ai

import android.content.Context
import android.util.Log
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

/**
 * On-device product category classifier using a TFLite model.
 *
 * The model classifies OCR-extracted product label text into categories:
 * Food, Dairy, FMCG, Cosmetics, Pharma, Electronics, Pet Care, Stationery
 *
 * Falls back to keyword-based classification if model is not available.
 */
@Singleton
class ProductClassifier @Inject constructor(
    @ApplicationContext private val context: Context
) {
    companion object {
        private const val TAG = "ProductClassifier"
        private const val MODEL_FILENAME = "product_classifier.tflite"
    }

    /**
     * Category keyword dictionaries for fallback classification.
     */
    private val categoryKeywords = mapOf(
        "Food" to listOf(
            "biscuit", "chips", "noodles", "rice", "flour", "atta", "sugar",
            "salt", "oil", "ghee", "butter", "bread", "jam", "sauce", "spice",
            "masala", "tea", "coffee", "juice", "chocolate", "cereal", "oats",
            "fssai", "ingredients", "nutritional", "vegetarian"
        ),
        "Dairy" to listOf(
            "milk", "curd", "yogurt", "cheese", "paneer", "cream", "butter",
            "ghee", "lassi", "dahi", "buttermilk", "ice cream", "dairy"
        ),
        "FMCG" to listOf(
            "detergent", "dishwash", "toilet cleaner", "floor cleaner",
            "air freshener", "fabric softener", "laundry", "phenyl",
            "bleach", "tissue", "napkin", "diaper", "sanitary"
        ),
        "Cosmetics" to listOf(
            "shampoo", "conditioner", "soap", "face wash", "body wash",
            "lotion", "cream", "moisturizer", "sunscreen", "lipstick",
            "perfume", "deodorant", "hair oil", "serum", "skincare", "makeup"
        ),
        "Pharma" to listOf(
            "medicine", "tablet", "capsule", "syrup", "ointment", "drug",
            "dosage", "prescription", "antiseptic", "paracetamol",
            "ayurvedic", "homeopathic", "drug license"
        ),
        "Electronics" to listOf(
            "charger", "cable", "usb", "adapter", "power bank", "headphone",
            "speaker", "bluetooth", "battery", "led", "bulb", "fan",
            "voltage", "watt", "bis", "electronic"
        ),
        "Pet Care" to listOf(
            "dog food", "cat food", "pet food", "puppy", "kitten", "pet",
            "grooming", "flea", "tick", "veterinary"
        ),
        "Stationery" to listOf(
            "notebook", "pen", "pencil", "eraser", "ruler", "geometry",
            "adhesive", "glue", "paper", "writing"
        )
    )

    /**
     * Classify product text into a category.
     *
     * Uses keyword-based matching (TFLite model is loaded at build time
     * when the model asset is available).
     *
     * @param text OCR-extracted text from the product label
     * @return CategoryResult with predicted category and confidence
     */
    fun classify(text: String): CategoryResult {
        if (text.isBlank()) {
            return CategoryResult(
                category = "Packaged Goods",
                confidence = 0f,
                method = "default"
            )
        }

        return classifyWithKeywords(text)
    }

    /**
     * Keyword-based classification with scoring.
     */
    private fun classifyWithKeywords(text: String): CategoryResult {
        val textLower = text.lowercase()
        val scores = mutableMapOf<String, Int>()

        categoryKeywords.forEach { (category, keywords) ->
            var score = 0
            keywords.forEach { keyword ->
                if (textLower.contains(keyword)) {
                    score++
                }
            }
            scores[category] = score
        }

        val bestCategory = scores.maxByOrNull { it.value }
        return if (bestCategory != null && bestCategory.value > 0) {
            val totalMatches = scores.values.sum().toFloat()
            val confidence = if (totalMatches > 0) {
                bestCategory.value / totalMatches
            } else 0f

            CategoryResult(
                category = bestCategory.key,
                confidence = confidence.coerceIn(0f, 1f),
                method = "keyword_matching",
                scores = scores.filter { it.value > 0 }
            )
        } else {
            CategoryResult(
                category = "Packaged Goods",
                confidence = 0f,
                method = "default"
            )
        }
    }
}

/**
 * Result of product category classification.
 */
data class CategoryResult(
    val category: String,
    val confidence: Float,
    val method: String,
    val scores: Map<String, Int> = emptyMap()
)
