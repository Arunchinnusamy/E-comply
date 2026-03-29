package com.example.e_comply.data.local.converter

import androidx.room.TypeConverter
import com.example.e_comply.data.model.Violation
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

/**
 * Room TypeConverters for non-primitive fields stored in the local database.
 *
 * All list types are serialised to/from JSON using Gson.  A single [Gson]
 * instance is shared; Room creates one [Converters] instance per database.
 */
class Converters {

    private val gson = Gson()

    // ── List<String> ──────────────────────────────────────────────────────────

    @TypeConverter
    fun fromStringList(value: List<String>): String = gson.toJson(value)

    @TypeConverter
    fun toStringList(value: String): List<String> {
        val type = object : TypeToken<List<String>>() {}.type
        return gson.fromJson(value, type) ?: emptyList()
    }

    // ── List<Violation> ───────────────────────────────────────────────────────

    @TypeConverter
    fun fromViolationList(value: List<Violation>): String = gson.toJson(value)

    @TypeConverter
    fun toViolationList(value: String): List<Violation> {
        val type = object : TypeToken<List<Violation>>() {}.type
        return gson.fromJson(value, type) ?: emptyList()
    }
}
