package com.example.e_comply.data.model

data class ComplianceReport(
    val id: String = "",
    val productId: String = "",
    val productName: String = "",
    val complianceScore: Float = 0f,
    val isCompliant: Boolean = false,
    val complianceStatus: ComplianceStatus = ComplianceStatus.PENDING,
    val missingFields: List<String> = emptyList(),
    val violations: List<Violation> = emptyList(),
    val recommendations: List<String> = emptyList(),
    val riskLevel: RiskLevel = RiskLevel.LOW,
    val aiSummary: String = "",
    val inspectorId: String = "",
    val inspectorNotes: String = "",
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis(),
    // New structured report fields for Legal Metrology compliance
    val validationResults: List<ValidationResult> = emptyList(),
    val category: String = "",
    val brandName: String = "",
    val remarks: String = ""
)

/**
 * Structured validation result for each mandatory field.
 * Maps to the validation_results array in the JSON report.
 */
data class ValidationResult(
    val field: String = "",
    val status: String = "" // "Valid" or "Missing"
)

data class Violation(
    val field: String = "",
    val description: String = "",
    val severity: Severity = Severity.LOW,
    val ruleViolated: String = ""
)

enum class ComplianceStatus {
    PENDING,
    COMPLIANT,
    NON_COMPLIANT,
    PARTIAL_COMPLIANT,
    UNDER_REVIEW
}

enum class RiskLevel {
    LOW,
    MEDIUM,
    HIGH,
    CRITICAL
}

enum class Severity {
    LOW,
    MEDIUM,
    HIGH,
    CRITICAL
}
