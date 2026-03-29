package com.example.e_comply.data.local.dao

import androidx.room.*
import com.example.e_comply.data.local.entity.ComplianceReportEntity
import kotlinx.coroutines.flow.Flow

/**
 * Room DAO for [ComplianceReportEntity].
 *
 * All list queries return [Flow] for reactive, offline-first UI updates.
 */
@Dao
interface ComplianceReportDao {

    // ── Reads ─────────────────────────────────────────────────────────────────

    /** All reports (inspector view), newest first. */
    @Query("SELECT * FROM compliance_reports ORDER BY createdAt DESC")
    fun getAllReports(): Flow<List<ComplianceReportEntity>>

    /** Reports belonging to a specific user / inspector, newest first. */
    @Query("SELECT * FROM compliance_reports WHERE inspectorId = :userId ORDER BY createdAt DESC")
    fun getReportsByUser(userId: String): Flow<List<ComplianceReportEntity>>

    /** Filtered by compliance status (stores enum name). */
    @Query("SELECT * FROM compliance_reports WHERE complianceStatus = :status ORDER BY createdAt DESC")
    fun getReportsByStatus(status: String): Flow<List<ComplianceReportEntity>>

    /** Filtered by risk level (stores enum name). */
    @Query("SELECT * FROM compliance_reports WHERE riskLevel = :riskLevel ORDER BY createdAt DESC")
    fun getReportsByRiskLevel(riskLevel: String): Flow<List<ComplianceReportEntity>>

    /** One-shot lookup by primary key. */
    @Query("SELECT * FROM compliance_reports WHERE id = :reportId LIMIT 1")
    suspend fun getReportById(reportId: String): ComplianceReportEntity?

    /** All rows queued for Firestore upload. */
    @Query("SELECT * FROM compliance_reports WHERE syncStatus = 'PENDING_SYNC' OR syncStatus = 'SYNC_FAILED'")
    suspend fun getPendingSyncReports(): List<ComplianceReportEntity>

    // ── Writes ────────────────────────────────────────────────────────────────

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertReport(report: ComplianceReportEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertReports(reports: List<ComplianceReportEntity>)

    @Query("UPDATE compliance_reports SET syncStatus = :syncStatus, lastUpdated = :timestamp WHERE id = :reportId")
    suspend fun updateSyncStatus(reportId: String, syncStatus: String, timestamp: Long = System.currentTimeMillis())

    /** Inspectors can attach notes to a report (stored locally first). */
    @Query("UPDATE compliance_reports SET inspectorNotes = :notes, syncStatus = 'PENDING_SYNC', updatedAt = :timestamp WHERE id = :reportId")
    suspend fun updateInspectorNotes(reportId: String, notes: String, timestamp: Long = System.currentTimeMillis())

    @Delete
    suspend fun deleteReport(report: ComplianceReportEntity)

    @Query("DELETE FROM compliance_reports WHERE id = :reportId")
    suspend fun deleteReportById(reportId: String)
}
