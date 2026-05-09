package com.example.e_comply.data.ocr

import android.graphics.Bitmap
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.tasks.await
import javax.inject.Inject
import javax.inject.Singleton

/**
 * ML Kit Text Recognizer with confidence scoring.
 *
 * Enhancements over basic recognizer:
 * - Per-block and per-line confidence scores
 * - Structured result with text blocks metadata
 * - Overall confidence aggregation
 */
@Singleton
class MlKitTextRecognizer @Inject constructor() {

    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    /**
     * Simple text detection — returns raw text.
     */
    suspend fun detectText(bitmap: Bitmap): String {
        val inputImage = InputImage.fromBitmap(bitmap, 0)
        val result = recognizer.process(inputImage).await()
        return result.text
    }

    /**
     * Detect text with Result wrapper.
     */
    suspend fun detectTextResult(bitmap: Bitmap): Result<String> {
        return try {
            val text = detectText(bitmap)
            if (text.isBlank()) {
                Result.failure(IllegalStateException("No text detected in image"))
            } else {
                Result.success(text)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Enhanced detection — returns structured result with confidence scores.
     */
    suspend fun detectTextWithConfidence(bitmap: Bitmap): Result<OcrResult> {
        return try {
            val inputImage = InputImage.fromBitmap(bitmap, 0)
            val visionText = recognizer.process(inputImage).await()

            if (visionText.text.isBlank()) {
                return Result.failure(IllegalStateException("No text detected in image"))
            }

            val blocks = visionText.textBlocks.map { block ->
                val lines = block.lines.map { line ->
                    OcrLine(
                        text = line.text,
                        confidence = line.confidence ?: 0f,
                        boundingBox = line.boundingBox?.let { rect ->
                            OcrBoundingBox(
                                left = rect.left,
                                top = rect.top,
                                right = rect.right,
                                bottom = rect.bottom
                            )
                        }
                    )
                }
                OcrBlock(
                    text = block.text,
                    confidence = block.lines
                        .mapNotNull { it.confidence }
                        .average()
                        .toFloat()
                        .takeIf { !it.isNaN() } ?: 0f,
                    lines = lines,
                    language = block.recognizedLanguage
                )
            }

            // Calculate overall confidence
            val allConfidences = blocks.flatMap { block ->
                block.lines.map { it.confidence }
            }
            val overallConfidence = if (allConfidences.isNotEmpty()) {
                allConfidences.average().toFloat()
            } else 0f

            Result.success(
                OcrResult(
                    fullText = visionText.text,
                    blocks = blocks,
                    overallConfidence = overallConfidence,
                    blockCount = blocks.size,
                    lineCount = blocks.sumOf { it.lines.size }
                )
            )
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Callback-based text detection (legacy support).
     */
    fun detectText(
        bitmap: Bitmap,
        onSuccess: (String) -> Unit,
        onError: (Throwable) -> Unit
    ) {
        val inputImage = InputImage.fromBitmap(bitmap, 0)
        recognizer.process(inputImage)
            .addOnSuccessListener { visionText ->
                val text = visionText.text
                if (text.isBlank()) {
                    onError(IllegalStateException("No text detected in image"))
                } else {
                    onSuccess(text)
                }
            }
            .addOnFailureListener(onError)
    }
}

/**
 * Structured OCR result with confidence metadata.
 */
data class OcrResult(
    val fullText: String,
    val blocks: List<OcrBlock>,
    val overallConfidence: Float,
    val blockCount: Int,
    val lineCount: Int
)

data class OcrBlock(
    val text: String,
    val confidence: Float,
    val lines: List<OcrLine>,
    val language: String
)

data class OcrLine(
    val text: String,
    val confidence: Float,
    val boundingBox: OcrBoundingBox? = null
)

data class OcrBoundingBox(
    val left: Int,
    val top: Int,
    val right: Int,
    val bottom: Int
)