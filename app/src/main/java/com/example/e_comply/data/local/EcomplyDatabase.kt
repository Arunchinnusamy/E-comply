package com.example.e_comply.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.example.e_comply.data.local.converter.Converters
import com.example.e_comply.data.local.dao.ComplianceReportDao
import com.example.e_comply.data.local.dao.ProductDao
import com.example.e_comply.data.local.entity.ComplianceReportEntity
import com.example.e_comply.data.local.entity.ProductEntity

/**
 * Single Room database for the entire app.
 *
 * Version history
 * ───────────────
 * 1 – initial schema (products + compliance_reports)
 *
 * Hilt provides this as a singleton via [com.example.e_comply.di.AppModule].
 * Do NOT access [getInstance] directly – always inject the DAOs.
 */
@Database(
    entities = [
        ProductEntity::class,
        ComplianceReportEntity::class
    ],
    version = 1,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class EcomplyDatabase : RoomDatabase() {

    abstract fun productDao(): ProductDao
    abstract fun complianceReportDao(): ComplianceReportDao

    companion object {
        private const val DATABASE_NAME = "ecomply_db"

        // Kept for convenience during manual testing; prefer DI in production.
        @Volatile
        private var INSTANCE: EcomplyDatabase? = null

        fun getInstance(context: Context): EcomplyDatabase =
            INSTANCE ?: synchronized(this) {
                INSTANCE ?: buildDatabase(context).also { INSTANCE = it }
            }

        private fun buildDatabase(context: Context) =
            Room.databaseBuilder(
                context.applicationContext,
                EcomplyDatabase::class.java,
                DATABASE_NAME
            ).build()
    }
}
