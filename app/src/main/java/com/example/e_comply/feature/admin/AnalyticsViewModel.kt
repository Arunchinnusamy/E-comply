package com.example.e_comply.feature.admin

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.e_comply.data.remote.InspectorAnalytics
import com.example.e_comply.feature.database.ComplianceRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AnalyticsViewModel @Inject constructor(
    private val complianceRepository: ComplianceRepository
) : ViewModel() {

    private val _analyticsState = MutableStateFlow<AnalyticsState>(AnalyticsState.Loading)
    val analyticsState: StateFlow<AnalyticsState> = _analyticsState.asStateFlow()

    init {
        fetchAnalytics()
    }

    fun fetchAnalytics() {
        viewModelScope.launch {
            _analyticsState.value = AnalyticsState.Loading
            val result = complianceRepository.getInspectorAnalytics()
            result.onSuccess { analytics ->
                _analyticsState.value = AnalyticsState.Success(analytics)
            }.onFailure { exception ->
                _analyticsState.value = AnalyticsState.Error(exception.message ?: "Unknown error")
            }
        }
    }
}

sealed class AnalyticsState {
    object Loading : AnalyticsState()
    data class Success(val analytics: InspectorAnalytics) : AnalyticsState()
    data class Error(val message: String) : AnalyticsState()
}
