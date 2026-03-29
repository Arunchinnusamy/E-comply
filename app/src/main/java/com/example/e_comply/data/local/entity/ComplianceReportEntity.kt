package com.example.e_comply.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.TypeConverters
import com.example.e_comply.data.local.converter.Converters
import com.example.e_comply.data.model.*

/**
 * Room entity that mirrors [ComplianceReport].
 *
 * Complex fields ([missingFields], [violations], [recommendations]) are
 * serialised to JSON by [Converters].  Enum fields are stored as their
 * [name] strings.
 */
@Entity(tableName = "compliance_reports")
@TypeConverters(Converters::class)
data class ComplianceReportEntity(
    @PrimaryKey val id: String,
    val productId: String,
    val productName: String,
    val complianceScore: Float,
    val isCompliant: Boolean,
    /** Stored as [ComplianceStatus.name] */
    val complianceStatus: String,
    /** TypeConverter serialises this to/from JSON */
    val missingFields: List<String>,
    /** TypeConverter serialises this to/from JSON */
    val violations: List<Violation>,
    /** TypeConverter serialises this to/from JSON */
    val recommendations: List<String>,
    /** Stored as [RiskLevel.name] */
    val riskLevel: String,
    val aiSummary: String,
    val inspectorId: String,
    val inspectorNotes: String,
    val createdAt: Long,
    val updatedAt: Long,
    /** Stored as [SyncStatus.name] */
    val syncStatus: String = SyncStatus.PENDING_SYNC.name,
    val lastUpdated: Long = System.currentTimeMillis()
) {
    fun toComplianceReport(): ComplianceReport = ComplianceReport(
        id = id,
        productId = productId,
        productName = productName,
        complianceScore = complianceScore,
        isCompliant = isCompliant,
        complianceStatus = runCatching { ComplianceStatus.valueOf(complianceStatus) }
            .getOrDefault(ComplianceStatus.PENDING),
        missingFields = missingFields,
        violations = violations,
        recommendations = recommendations,
        riskLevel = runCatching { RiskLevel.valueOf(riskLevel) }.getOrDefault(RiskLevel.LOW),
        aiSummary = aiSummary,
        inspectorId = inspectorId,
        inspectorNotes = inspectorNotes,
        createdAt = createdAt,
        updatedAt = updatedAt
    )

    companion object {
        fun fromComplianceReport(
            report: ComplianceReport,
            syncStatus: SyncStatus = SyncStatus.PENDING_SYNC
        ): ComplianceReportEntity = ComplianceReportEntity(
            id = report.id,
            productId = report.productId,
            productName = report.productName,
            complianceScore = report.complianceScore,
            isCompliant = report.isCompliant,
            complianceStatus = report.complianceStatus.name,
            missingFields = report.missingFields,
            violations = report.violations,
            recommendations = report.recommendations,
            riskLevel = report.riskLevel.name,
            aiSummary = report.aiSummary,
            inspectorId = report.inspectorId,
            inspectorNotes = report.inspectorNotes,
            createdAt = report.createdAt,
            updatedAt = report.updatedAt,
            syncStatus = syncStatus.name,
            lastUpdated = System.currentTimeMillis()
        )
    }
}
