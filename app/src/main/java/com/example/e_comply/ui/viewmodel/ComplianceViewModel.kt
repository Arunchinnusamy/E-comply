package com.example.e_comply.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.e_comply.data.model.ComplianceReport
import com.example.e_comply.data.model.ComplianceStatus
import com.example.e_comply.data.model.Product
import com.example.e_comply.data.model.RiskLevel
import com.example.e_comply.data.repository.ComplianceRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ComplianceViewModel @Inject constructor(
    private val complianceRepository: ComplianceRepository
) : ViewModel() {
    
    private val _complianceState = MutableStateFlow<ComplianceState>(ComplianceState.Initial)
    val complianceState: StateFlow<ComplianceState> = _complianceState.asStateFlow()
    
    private val _currentReport = MutableStateFlow<ComplianceReport?>(null)
    val currentReport: StateFlow<ComplianceReport?> = _currentReport.asStateFlow()
    
    fun validateCompliance(product: Product, extractedText: String) {
        viewModelScope.launch {
            _complianceState.value = ComplianceState.Validating
            val result = complianceRepository.validateCompliance(product, extractedText)
            result.onSuccess { report ->
                _currentReport.value = report
                // Save the report
                complianceRepository.saveReport(report)
                _complianceState.value = ComplianceState.Validated(report)
            }.onFailure { exception ->
                _complianceState.value = ComplianceState.Error(exception.message ?: "Validation failed")
            }
        }
    }
    
    fun getReport(reportId: String) {
        viewModelScope.launch {
            _complianceState.value = ComplianceState.Loading
            val result = complianceRepository.getReport(reportId)
            result.onSuccess { report ->
                _currentReport.value = report
                _complianceState.value = ComplianceState.ReportLoaded(report)
            }.onFailure { exception ->
                _complianceState.value = ComplianceState.Error(exception.message ?: "Failed to load report")
            }
        }
    }
    
    fun getUserReports(userId: String) {
        viewModelScope.launch {
            _complianceState.value = ComplianceState.Loading
            val result = complianceRepository.getUserReports(userId)
            result.onSuccess { reports ->
                _complianceState.value = ComplianceState.ReportsLoaded(reports)
            }.onFailure { exception ->
                _complianceState.value = ComplianceState.Error(exception.message ?: "Failed to load reports")
            }
        }
    }
    
    fun getAllReports() {
        viewModelScope.launch {
            _complianceState.value = ComplianceState.Loading
            val result = complianceRepository.getAllReports()
            result.onSuccess { reports ->
                _complianceState.value = ComplianceState.ReportsLoaded(reports)
            }.onFailure { exception ->
                _complianceState.value = ComplianceState.Error(exception.message ?: "Failed to load reports")
            }
        }
    }
    
    fun filterReportsByStatus(status: ComplianceStatus) {
        viewModelScope.launch {
            _complianceState.value = ComplianceState.Loading
            val result = complianceRepository.getReportsByStatus(status)
            result.onSuccess { reports ->
                _complianceState.value = ComplianceState.ReportsLoaded(reports)
            }.onFailure { exception ->
                _complianceState.value = ComplianceState.Error(exception.message ?: "Failed to filter reports")
            }
        }
    }
    
    fun filterReportsByRisk(riskLevel: RiskLevel) {
        viewModelScope.launch {
            _complianceState.value = ComplianceState.Loading
            val result = complianceRepository.getReportsByRiskLevel(riskLevel)
            result.onSuccess { reports ->
                _complianceState.value = ComplianceState.ReportsLoaded(reports)
            }.onFailure { exception ->
                _complianceState.value = ComplianceState.Error(exception.message ?: "Failed to filter reports")
            }
        }
    }
    
    fun reset() {
        _complianceState.value = ComplianceState.Initial
        _currentReport.value = null
    }
}

sealed class ComplianceState {
    object Initial : ComplianceState()
    object Loading : ComplianceState()
    object Validating : ComplianceState()
    data class Validated(val report: ComplianceReport) : ComplianceState()
    data class ReportLoaded(val report: ComplianceReport) : ComplianceState()
    data class ReportsLoaded(val reports: List<ComplianceReport>) : ComplianceState()
    data class Error(val message: String) : ComplianceState()
}
