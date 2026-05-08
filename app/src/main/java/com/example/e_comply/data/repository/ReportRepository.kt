package com.example.e_comply.data.repository

import com.google.firebase.Timestamp
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.FirebaseFirestore
import com.example.e_comply.data.model.ReportItem
import kotlinx.coroutines.tasks.await
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ReportRepository @Inject constructor(
    private val firestore: FirebaseFirestore,
    private val auth: FirebaseAuth
) {

    suspend fun saveDetectedTextReport(detectedText: String): Result<String> {
        return try {
            val userId = auth.currentUser?.uid
                ?: return Result.failure(IllegalStateException("User is not authenticated"))

            if (detectedText.isBlank()) {
                return Result.failure(IllegalArgumentException("Detected text is empty"))
            }

            val reportRef = firestore.collection("reports").document()
            val payload = hashMapOf(
                "id" to reportRef.id,
                "text" to detectedText,
                "userId" to userId,
                "timestamp" to Timestamp.now()
            )

            reportRef.set(payload).await()
            Result.success(reportRef.id)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchReportsForCurrentUser(): Result<List<ReportItem>> {
        return try {
            val userId = auth.currentUser?.uid
                ?: return Result.failure(IllegalStateException("User is not authenticated"))

            val snapshot = firestore.collection("reports")
                .whereEqualTo("userId", userId)
                .get()
                .await()

            val reports = snapshot.documents.mapNotNull { document ->
                val text = document.getString("text") ?: return@mapNotNull null
                val ownerId = document.getString("userId") ?: userId
                val timestampValue = when (val rawTimestamp = document.get("timestamp")) {
                    is Long -> rawTimestamp
                    is Timestamp -> rawTimestamp.toDate().time
                    else -> 0L
                }

                ReportItem(
                    id = document.id,
                    userId = ownerId,
                    text = text,
                    timestamp = timestampValue
                )
            }.sortedByDescending { it.timestamp }

            Result.success(reports)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}