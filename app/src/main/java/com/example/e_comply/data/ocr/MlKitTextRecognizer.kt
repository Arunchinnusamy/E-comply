package com.example.e_comply.data.ocr

import android.graphics.Bitmap
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.tasks.await
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class MlKitTextRecognizer @Inject constructor() {

    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    suspend fun detectText(bitmap: Bitmap): String {
        val inputImage = InputImage.fromBitmap(bitmap, 0)
        val result = recognizer.process(inputImage).await()
        return result.text
    }

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