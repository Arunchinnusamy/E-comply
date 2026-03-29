package com.example.e_comply.ui.viewmodel

import android.graphics.Bitmap
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.e_comply.data.model.Product
import com.example.e_comply.data.model.ProductSource
import com.example.e_comply.data.repository.ProductRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ScanViewModel @Inject constructor(
    private val productRepository: ProductRepository
) : ViewModel() {
    
    private val _scanState = MutableStateFlow<ScanState>(ScanState.Initial)
    val scanState: StateFlow<ScanState> = _scanState.asStateFlow()
    
    private val _extractedText = MutableStateFlow("")
    val extractedText: StateFlow<String> = _extractedText.asStateFlow()
    
    private val _capturedImage = MutableStateFlow<Bitmap?>(null)
    val capturedImage: StateFlow<Bitmap?> = _capturedImage.asStateFlow()
    
    fun setCapturedImage(bitmap: Bitmap) {
        _capturedImage.value = bitmap
    }
    
    fun extractText(bitmap: Bitmap, useBackend: Boolean = false) {
        viewModelScope.launch {
            _scanState.value = ScanState.Extracting
            
            val result = if (useBackend) {
                productRepository.extractTextFromImageViaBackend(bitmap)
            } else {
                productRepository.extractTextFromImage(bitmap)
            }
            
            result.onSuccess { text ->
                _extractedText.value = text
                _scanState.value = ScanState.TextExtracted(text)
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
