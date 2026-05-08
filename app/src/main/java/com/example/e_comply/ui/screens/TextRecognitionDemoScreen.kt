package com.example.e_comply.ui.screens

import android.graphics.Bitmap
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.e_comply.ui.viewmodel.ScanViewModel

@Composable
fun TextRecognitionDemoScreen(
    capturedBitmap: Bitmap?,
    scanViewModel: ScanViewModel = hiltViewModel()
) {
    var detectedText by remember { mutableStateOf("") }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var isLoading by remember { mutableStateOf(false) }
    var saveMessage by remember { mutableStateOf<String?>(null) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Top
    ) {
        Text(
            text = "ML Kit Text Recognition",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.SemiBold
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                val bitmap = capturedBitmap ?: return@Button
                isLoading = true
                errorMessage = null
                saveMessage = null

                scanViewModel.detectText(bitmap) { result ->
                    isLoading = false
                    result.onSuccess { text ->
                        detectedText = text
                        saveMessage = "Saved to Firestore reports collection"
                    }.onFailure { throwable ->
                        errorMessage = throwable.message ?: "Failed to detect text"
                    }
                }
            },
            enabled = capturedBitmap != null && !isLoading,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Detect Text")
        }

        Spacer(modifier = Modifier.height(16.dp))

        if (isLoading) {
            CircularProgressIndicator()
            Spacer(modifier = Modifier.height(16.dp))
        }

        if (!errorMessage.isNullOrBlank()) {
            Text(
                text = errorMessage.orEmpty(),
                color = MaterialTheme.colorScheme.error
            )
            Spacer(modifier = Modifier.height(12.dp))
        }

        if (!saveMessage.isNullOrBlank()) {
            Text(
                text = saveMessage.orEmpty(),
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(12.dp))
        }

        Text(
            text = "Detected text:",
            style = MaterialTheme.typography.titleMedium
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = if (detectedText.isBlank()) "No text detected yet" else detectedText,
            style = MaterialTheme.typography.bodyMedium
        )
    }
}
