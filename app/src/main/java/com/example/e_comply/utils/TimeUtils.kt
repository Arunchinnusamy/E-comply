package com.example.e_comply.utils

import com.google.firebase.Timestamp
import java.util.concurrent.TimeUnit

fun formatRelativeTime(timestamp: Timestamp): String {
    return formatRelativeTime(timestamp.toDate().time)
}

fun formatRelativeTime(timestampMillis: Long): String {
    val now = System.currentTimeMillis()
    val diffMillis = now - timestampMillis

    if (diffMillis < TimeUnit.MINUTES.toMillis(1)) {
        return "Just now"
    }

    val minutes = TimeUnit.MILLISECONDS.toMinutes(diffMillis)
    if (minutes < 60) {
        return if (minutes == 1L) "1 minute ago" else "$minutes minutes ago"
    }

    val hours = TimeUnit.MILLISECONDS.toHours(diffMillis)
    if (hours < 24) {
        return if (hours == 1L) "1 hour ago" else "$hours hours ago"
    }

    val days = TimeUnit.MILLISECONDS.toDays(diffMillis)
    return if (days == 1L) "1 day ago" else "$days days ago"
}