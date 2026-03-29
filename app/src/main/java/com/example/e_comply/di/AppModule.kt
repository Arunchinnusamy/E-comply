package com.example.e_comply.di

import android.content.Context
import com.example.e_comply.data.local.EcomplyDatabase
import com.example.e_comply.data.local.dao.ComplianceReportDao
import com.example.e_comply.data.local.dao.ProductDao
import com.example.e_comply.data.remote.ApiService
import com.example.e_comply.data.remote.RetrofitClient
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.storage.FirebaseStorage
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    // ── Firebase ──────────────────────────────────────────────────────────────

    @Provides @Singleton
    fun provideFirebaseAuth(): FirebaseAuth = FirebaseAuth.getInstance()

    @Provides @Singleton
    fun provideFirebaseFirestore(): FirebaseFirestore = FirebaseFirestore.getInstance()

    @Provides @Singleton
    fun provideFirebaseStorage(): FirebaseStorage = FirebaseStorage.getInstance()

    // ── Network ───────────────────────────────────────────────────────────────

    @Provides @Singleton
    fun provideApiService(): ApiService = RetrofitClient.apiService

    // ── Room ──────────────────────────────────────────────────────────────────

    @Provides @Singleton
    fun provideEcomplyDatabase(@ApplicationContext context: Context): EcomplyDatabase =
        EcomplyDatabase.getInstance(context)

    @Provides @Singleton
    fun provideProductDao(db: EcomplyDatabase): ProductDao = db.productDao()

    @Provides @Singleton
    fun provideComplianceReportDao(db: EcomplyDatabase): ComplianceReportDao =
        db.complianceReportDao()
}
