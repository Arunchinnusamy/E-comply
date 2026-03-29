package com.example.e_comply.data.repository

import android.graphics.Bitmap
import android.util.Base64
import com.example.e_comply.data.local.dao.ComplianceReportDao
import com.example.e_comply.data.local.entity.ComplianceReportEntity
import com.example.e_comply.data.local.entity.SyncStatus
import com.example.e_comply.data.model.*
import com.example.e_comply.data.remote.ApiService
import com.example.e_comply.data.remote.ComplianceRequest
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.firestore.Query
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.tasks.await
import java.io.ByteArrayOutputStream
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ComplianceRepository @Inject constructor(
    private val firestore: FirebaseFirestore,
    private val apiService: ApiService,
    private val reportDao: ComplianceReportDao
) {
    
    suspend fun validateCompliance(product: Product, extractedText: String): Result<ComplianceReport> {
        return try {
            // First, perform local validation
            val localReport = performLocalValidation(product, extractedText)
            
            // Then, enhance with backend AI validation
            try {
                val request = ComplianceRequest(product, extractedText)
                val response = apiService.validateCompliance(request)
                
                if (response.isSuccessful && response.body() != null) {
                    val enhancedReport = response.body()!!.report
                    Result.success(enhancedReport)
                } else {
                    // If backend fails, return local validation
                    Result.success(localReport)
                }
            } catch (e: Exception) {
                // If backend is unavailable, return local validation
                Result.success(localReport)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    private fun performLocalValidation(product: Product, extractedText: String): ComplianceReport {
        val missingFields = mutableListOf<String>()
        val violations = mutableListOf<Violation>()
        
        // Check mandatory fields
        LegalMetrologyRules.mandatoryFields.forEach { rule ->
            val fieldValue = when (rule.fieldName) {
                "Manufacturer Name" -> product.manufacturerName
                "Manufacturer Address" -> product.manufacturerAddress
                "Net Quantity" -> product.netQuantity
                "MRP" -> product.mrp
                "Manufacturing/Packing Date" -> product.manufacturingDate
                "Customer Care Details" -> product.customerCareDetails
                "Country of Origin" -> product.countryOfOrigin
                else -> ""
            }
            
            if (fieldValue.isBlank()) {
                missingFields.add(rule.fieldName)
                violations.add(
                    Violation(
                        field = rule.fieldName,
                        description = rule.errorMessage,
                        severity = Severity.HIGH,
                        ruleViolated = "Legal Metrology (Packaged Commodities) Rules, 2011"
                    )
                )
            } else {
                // Validate pattern if specified
                rule.validationPattern?.let { pattern ->
                    if (!fieldValue.matches(Regex(pattern, RegexOption.IGNORE_CASE))) {
                        violations.add(
                            Violation(
                                field = rule.fieldName,
                                description = "Invalid format for ${rule.fieldName}",
                                severity = Severity.MEDIUM,
                                ruleViolated = "Legal Metrology (Packaged Commodities) Rules, 2011"
                            )
                        )
                    }
                }
            }
        }
        
        // Calculate compliance score
        val totalFields = LegalMetrologyRules.mandatoryFields.size
        val compliantFields = totalFields - missingFields.size
        val complianceScore = (compliantFields.toFloat() / totalFields.toFloat()) * 100
        
        // Determine risk level
        val riskLevel = when {
            complianceScore >= 90 -> RiskLevel.LOW
            complianceScore >= 70 -> RiskLevel.MEDIUM
            complianceScore >= 50 -> RiskLevel.HIGH
            else -> RiskLevel.CRITICAL
        }
        
        // Determine compliance status
        val complianceStatus = when {
            complianceScore == 100f -> ComplianceStatus.COMPLIANT
            complianceScore >= 70 -> ComplianceStatus.PARTIAL_COMPLIANT
            else -> ComplianceStatus.NON_COMPLIANT
        }
        
        // Generate recommendations
        val recommendations = generateRecommendations(missingFields, violations)
        
        return ComplianceReport(
            id = UUID.randomUUID().toString(),
            productId = product.id,
            productName = product.name,
            complianceScore = complianceScore,
            isCompliant = complianceScore == 100f,
            complianceStatus = complianceStatus,
            missingFields = missingFields,
            violations = violations,
            recommendations = recommendations,
            riskLevel = riskLevel,
            aiSummary = generateSummary(product, complianceScore, violations),
            createdAt = System.currentTimeMillis(),
            updatedAt = System.currentTimeMillis()
        )
    }
    
    private fun generateRecommendations(
        missingFields: List<String>,
        violations: List<Violation>
    ): List<String> {
        val recommendations = mutableListOf<String>()
        
        if (missingFields.isNotEmpty()) {
            recommendations.add("Add the following mandatory fields: ${missingFields.joinToString(", ")}")
        }
        
        if (violations.any { it.severity == Severity.HIGH || it.severity == Severity.CRITICAL }) {
            recommendations.add("Address high-severity violations immediately to ensure compliance")
        }
        
        recommendations.add("Ensure all information is clearly visible and legible on the package")
        recommendations.add("Verify that MRP is inclusive of all taxes")
        recommendations.add("Include customer care contact information prominently")
        
        return recommendations
    }
    
    private fun generateSummary(
        product: Product,
        complianceScore: Float,
        violations: List<Violation>
    ): String {
        val status = when {
            complianceScore == 100f -> "fully compliant"
            complianceScore >= 70 -> "partially compliant"
            else -> "non-compliant"
        }
        
        return """
            Product '${product.name}' is $status with Legal Metrology regulations (${complianceScore.toInt()}% compliance score).
            ${if (violations.isNotEmpty()) "Found ${violations.size} violation(s) that need attention." else "All mandatory requirements are met."}
            ${if (violations.any { it.severity == Severity.HIGH || it.severity == Severity.CRITICAL }) 
                "Critical issues detected requiring immediate action." 
            else ""}
        """.trimIndent()
    }
    
    /**
     * Write-through save:
     * 1. Persist to Room immediately (PENDING_SYNC) → instant offline availability.
     * 2. Push to Firestore in the same call.
     * 3. On success → mark SYNCED; on failure → stays PENDING_SYNC for retry.
     */
    suspend fun saveReport(report: ComplianceReport): Result<String> {
        return try {
            val reportId = if (report.id.isBlank()) UUID.randomUUID().toString() else report.id
            val finalReport = report.copy(id = reportId, updatedAt = System.currentTimeMillis())

            // Step 1 – Room write (always succeeds, even offline)
            reportDao.insertReport(
                ComplianceReportEntity.fromComplianceReport(finalReport, SyncStatus.PENDING_SYNC)
            )

            // Step 2 – Firestore write
            try {
                firestore.collection("compliance_reports")
                    .document(reportId)
                    .set(finalReport)
                    .await()
                reportDao.updateSyncStatus(reportId, SyncStatus.SYNCED.name)
            } catch (_: Exception) {
                // Offline – row stays PENDING_SYNC; synced later
            }

            Result.success(reportId)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Cache-first lookup: Room → Firestore on cache miss.
     */
    suspend fun getReport(reportId: String): Result<ComplianceReport> {
        return try {
            // 1. Room first (instant, works offline)
            val cached = reportDao.getReportById(reportId)
            if (cached != null) return Result.success(cached.toComplianceReport())

            // 2. Firestore fallback
            val doc = firestore.collection("compliance_reports")
                .document(reportId)
                .get()
                .await()
            val report = doc.toObject(ComplianceReport::class.java)
                ?: return Result.failure(Exception("Report not found"))
            reportDao.insertReport(
                ComplianceReportEntity.fromComplianceReport(report, SyncStatus.SYNCED)
            )
            Result.success(report)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // ── Reactive (Flow) accessors ────────────────────────────────────────────

    /** Live stream of reports for [userId]. Room emits on every local change. */
    fun getUserReportsFlow(userId: String): Flow<List<ComplianceReport>> =
        reportDao.getReportsByUser(userId).map { it.map { e -> e.toComplianceReport() } }

    /** Live stream of all reports (inspector dashboard). */
    fun getAllReportsFlow(): Flow<List<ComplianceReport>> =
        reportDao.getAllReports().map { it.map { e -> e.toComplianceReport() } }

    /** Filtered live stream by [ComplianceStatus]. */
    fun getReportsByStatusFlow(status: ComplianceStatus): Flow<List<ComplianceReport>> =
        reportDao.getReportsByStatus(status.name).map { it.map { e -> e.toComplianceReport() } }

    /** Filtered live stream by [RiskLevel]. */
    fun getReportsByRiskLevelFlow(riskLevel: RiskLevel): Flow<List<ComplianceReport>> =
        reportDao.getReportsByRiskLevel(riskLevel.name).map { it.map { e -> e.toComplianceReport() } }

    // ── Background Firestore refresh ─────────────────────────────────────────

    /**
     * Pull fresh reports for [userId] from Firestore and upsert into Room.
     * The Flows above will emit the updated list automatically.
     * Silently swallows network errors.
     */
    suspend fun refreshUserReports(userId: String) {
        try {
            val snapshot = firestore.collection("compliance_reports")
                .whereEqualTo("inspectorId", userId)
                .orderBy("createdAt", Query.Direction.DESCENDING)
                .get()
                .await()
            val entities = snapshot.documents.mapNotNull { doc ->
                doc.toObject(ComplianceReport::class.java)?.let {
                    ComplianceReportEntity.fromComplianceReport(it, SyncStatus.SYNCED)
                }
            }
            reportDao.insertReports(entities)
        } catch (_: Exception) { /* offline – cached data still streams */ }
    }

    suspend fun refreshAllReports() {
        try {
            val snapshot = firestore.collection("compliance_reports")
                .orderBy("createdAt", Query.Direction.DESCENDING)
                .limit(100)
                .get()
                .await()
            val entities = snapshot.documents.mapNotNull { doc ->
                doc.toObject(ComplianceReport::class.java)?.let {
                    ComplianceReportEntity.fromComplianceReport(it, SyncStatus.SYNCED)
                }
            }
            reportDao.insertReports(entities)
        } catch (_: Exception) { /* offline */ }
    }

    // ── Legacy suspend helpers (kept for existing call sites) ────────────────

    /** @deprecated Prefer [getUserReportsFlow] + [refreshUserReports]. */
    suspend fun getUserReports(userId: String): Result<List<ComplianceReport>> {
        return try {
            val snapshot = firestore.collection("compliance_reports")
                .whereEqualTo("inspectorId", userId)
                .orderBy("createdAt", Query.Direction.DESCENDING)
                .get()
                .await()
            val reports = snapshot.documents.mapNotNull { it.toObject(ComplianceReport::class.java) }
            reportDao.insertReports(reports.map { ComplianceReportEntity.fromComplianceReport(it, SyncStatus.SYNCED) })
            Result.success(reports)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /** @deprecated Prefer [getAllReportsFlow] + [refreshAllReports]. */
    suspend fun getAllReports(): Result<List<ComplianceReport>> {
        return try {
            val snapshot = firestore.collection("compliance_reports")
                .orderBy("createdAt", Query.Direction.DESCENDING)
                .limit(100)
                .get()
                .await()
            val reports = snapshot.documents.mapNotNull { it.toObject(ComplianceReport::class.java) }
            reportDao.insertReports(reports.map { ComplianceReportEntity.fromComplianceReport(it, SyncStatus.SYNCED) })
            Result.success(reports)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /** @deprecated Prefer [getReportsByStatusFlow]. */
    suspend fun getReportsByStatus(status: ComplianceStatus): Result<List<ComplianceReport>> {
        return try {
            val snapshot = firestore.collection("compliance_reports")
                .whereEqualTo("complianceStatus", status.name)
                .orderBy("createdAt", Query.Direction.DESCENDING)
                .get()
                .await()
            val reports = snapshot.documents.mapNotNull { it.toObject(ComplianceReport::class.java) }
            reportDao.insertReports(reports.map { ComplianceReportEntity.fromComplianceReport(it, SyncStatus.SYNCED) })
            Result.success(reports)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /** @deprecated Prefer [getReportsByRiskLevelFlow]. */
    suspend fun getReportsByRiskLevel(riskLevel: RiskLevel): Result<List<ComplianceReport>> {
        return try {
            val snapshot = firestore.collection("compliance_reports")
                .whereEqualTo("riskLevel", riskLevel.name)
                .orderBy("createdAt", Query.Direction.DESCENDING)
                .get()
                .await()
            val reports = snapshot.documents.mapNotNull { it.toObject(ComplianceReport::class.java) }
            reportDao.insertReports(reports.map { ComplianceReportEntity.fromComplianceReport(it, SyncStatus.SYNCED) })
            Result.success(reports)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ── Pending-sync queue ────────────────────────────────────────────────────

    /**
     * Push all PENDING_SYNC / SYNC_FAILED reports to Firestore.
     * Call from a [androidx.work.CoroutineWorker] when connectivity is restored.
     */
    suspend fun syncPendingReports() {
        val pending = reportDao.getPendingSyncReports()
        pending.forEach { entity ->
            try {
                val report = entity.toComplianceReport()
                firestore.collection("compliance_reports").document(report.id).set(report).await()
                reportDao.updateSyncStatus(entity.id, SyncStatus.SYNCED.name)
            } catch (_: Exception) {
                reportDao.updateSyncStatus(entity.id, SyncStatus.SYNC_FAILED.name)
            }
        }
    }
}
