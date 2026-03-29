package com.example.e_comply.data.local.entity

/**
 * Tracks whether a locally-written record has been pushed to Firestore yet.
 *
 * PENDING_SYNC – written offline; needs to be uploaded on next connectivity.
 * SYNCED       – already persisted in Firestore.
 * SYNC_FAILED  – upload was attempted but failed; will be retried.
 */
enum class SyncStatus {
    PENDING_SYNC,
    SYNCED,
    SYNC_FAILED
}
