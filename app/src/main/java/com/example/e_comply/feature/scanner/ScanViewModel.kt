package com.example.e_comply.feature.scanner

import android.graphics.Bitmap
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.e_comply.data.model.Product
import com.example.e_comply.data.model.ReportItem
import com.example.e_comply.data.model.ProductSource
import com.example.e_comply.feature.database.ProductRepository
import com.example.e_comply.feature.database.ReportRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ScanViewModel @Inject constructor(
    private val productRepository: ProductRepository,
    private val reportRepository: ReportRepository
) : ViewModel() {
    
    private val _scanState = MutableStateFlow<ScanState>(ScanState.Initial)
    val scanState: StateFlow<ScanState> = _scanState.asStateFlow()
    
    private val _extractedText = MutableStateFlow("")
    val extractedText: StateFlow<String> = _extractedText.asStateFlow()
    
    private val _capturedImage = MutableStateFlow<Bitmap?>(null)
    val capturedImage: StateFlow<Bitmap?> = _capturedImage.asStateFlow()

    private val _lastSavedReportId = MutableStateFlow<String?>(null)
    val lastSavedReportId: StateFlow<String?> = _lastSavedReportId.asStateFlow()

    private val _reports = MutableStateFlow<List<ReportItem>>(emptyList())
    val reports: StateFlow<List<ReportItem>> = _reports.asStateFlow()

    private val _reportsLoading = MutableStateFlow(false)
    val reportsLoading: StateFlow<Boolean> = _reportsLoading.asStateFlow()

    private val _reportsError = MutableStateFlow<String?>(null)
    val reportsError: StateFlow<String?> = _reportsError.asStateFlow()
    
    fun setCapturedImage(bitmap: Bitmap) {
        _capturedImage.value = bitmap
    }

    fun detectText(bitmap: Bitmap) {
        extractText(bitmap)
    }

    fun detectText(bitmap: Bitmap, onResult: (Result<String>) -> Unit) {
        viewModelScope.launch {
            _scanState.value = ScanState.Extracting
            val result = productRepository.extractTextFromImage(bitmap)
            result.onSuccess { rawText ->
                val cleanedText = cleanOcrText(rawText)
                _extractedText.value = cleanedText
                _scanState.value = ScanState.TextExtracted(cleanedText)
                saveDetectedTextToFirestore(cleanedText)
            }.onFailure { exception ->
                _scanState.value = ScanState.Error(exception.message ?: "Text extraction failed")
            }
            onResult(result)
        }
    }

    private fun cleanOcrText(rawText: String): String {
        return rawText.replace("[^A-Za-z0-9:,.%/- \n]".toRegex(), "")
    }

    fun triggerDemoScan(onResult: (String) -> Unit) {
        viewModelScope.launch {
            _scanState.value = ScanState.Extracting
            // Simulate processing delay for "Wow" factor
            kotlinx.coroutines.delay(1000)
            
            val demoText = """
                Dove Intense Repair Shampoo 340ml
                Mfd by: Unilever India Pvt Ltd
                Unit No. 501, B-Wing, Mumbai 400063
                Batch No: BN4459021
                Mfd Date: 12/2023
                Use before: 24 months from mfd
                MRP Rs. 350.00 (incl of all taxes)
                Net Qty: 340 ml
                Customer Care: 1800-10-22-221
                Email: lever.care@unilever.com
                Country of Origin: India
            """.trimIndent()
            
            _extractedText.value = demoText
            _scanState.value = ScanState.TextExtracted(demoText)
            
            val saveResult = reportRepository.saveDetectedTextReport(demoText)
            saveResult.onSuccess { reportId ->
                _lastSavedReportId.value = reportId
                onResult(reportId)
            }
        }
    }

    fun saveDetectedTextToFirestore(detectedText: String, onResult: ((Result<String>) -> Unit)? = null) {
        viewModelScope.launch {
            val saveResult = reportRepository.saveDetectedTextReport(detectedText)
            saveResult.onSuccess { reportId ->
                _lastSavedReportId.value = reportId
            }
            onResult?.invoke(saveResult)
        }
    }

    fun loadReports() {
        viewModelScope.launch {
            _reportsLoading.value = true
            _reportsError.value = null

            val result = reportRepository.fetchReportsForCurrentUser()
            result.onSuccess { reports ->
                _reports.value = reports
            }.onFailure { exception ->
                _reportsError.value = exception.message ?: "Failed to load reports"
                _reports.value = emptyList()
            }

            _reportsLoading.value = false
        }
    }
    
    fun extractText(bitmap: Bitmap, useBackend: Boolean = false) {
        viewModelScope.launch {
            _scanState.value = ScanState.Extracting
            
            val result = if (useBackend) {
                productRepository.extractTextFromImageViaBackend(bitmap)
            } else {
                productRepository.extractTextFromImage(bitmap)
            }
            
            result.onSuccess { rawText ->
                val cleanedText = cleanOcrText(rawText)
                _extractedText.value = cleanedText
                _scanState.value = ScanState.TextExtracted(cleanedText)
                saveDetectedTextToFirestore(cleanedText)
            }.onFailure { exception ->
                _scanState.value = ScanState.Error(exception.message ?: "Text extraction failed")
            }
        }
    }
    
    fun saveProduct(
        product: Product,
        imageBitmap: Bitmap?
    ) {
        viewModelScope.launch {
            _scanState.value = ScanState.Saving
            val result = productRepository.saveProduct(product, imageBitmap)
            result.onSuccess { productId ->
                _scanState.value = ScanState.Saved(productId)
            }.onFailure { exception ->
                _scanState.value = ScanState.Error(exception.message ?: "Failed to save product")
            }
        }
    }
    
    fun getUserProducts(userId: String) {
        viewModelScope.launch {
            _scanState.value = ScanState.Loading
            val result = productRepository.getUserProducts(userId)
            result.onSuccess { products ->
                _scanState.value = ScanState.ProductsLoaded(products)
            }.onFailure { exception ->
                _scanState.value = ScanState.Error(exception.message ?: "Failed to load products")
            }
        }
    }
    
    fun reset() {
        _scanState.value = ScanState.Initial
        _extractedText.value = ""
        _capturedImage.value = null
        _lastSavedReportId.value = null
        _reports.value = emptyList()
        _reportsError.value = null
        _reportsLoading.value = false
    }
}

sealed class ScanState {
    object Initial : ScanState()
    object Loading : ScanState()
    object Extracting : ScanState()
    data class TextExtracted(val text: String) : ScanState()
    object Saving : ScanState()
    data class Saved(val productId: String) : ScanState()
    data class ProductsLoaded(val products: List<Product>) : ScanState()
    data class Error(val message: String) : ScanState()
}
