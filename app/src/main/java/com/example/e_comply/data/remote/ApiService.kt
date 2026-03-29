package com.example.e_comply.data.remote

import com.example.e_comply.data.model.ComplianceReport
import com.example.e_comply.data.model.Product
import retrofit2.Response
import retrofit2.http.*

data class OcrRequest(
    val imageBase64: String,
    val source: String
)

data class OcrResponse(
    val extractedText: String,
    val confidence: Float,
    val structuredData: Map<String, String>
)

data class ComplianceRequest(
    val product: Product,
    val extractedText: String
)

data class ComplianceResponse(
    val report: ComplianceReport,
    val success: Boolean,
    val message: String
)

data class EcommerceProductRequest(
    val url: String,
    val platform: String
)

data class EcommerceProductResponse(
    val product: Product,
    val success: Boolean,
    val message: String
)

data class IoTDataRequest(
    val deviceId: String,
    val imageBase64: String?,
    val sensorData: Map<String, Any>
)

interface ApiService {
    
    @POST("api/ocr/extract")
    suspend fun extractTextFromImage(
        @Body request: OcrRequest
    ): Response<OcrResponse>
    
    @POST("api/compliance/validate")
    suspend fun validateCompliance(
        @Body request: ComplianceRequest
    ): Response<ComplianceResponse>
    
    @POST("api/ecommerce/scrape")
    suspend fun scrapeEcommerceProduct(
        @Body request: EcommerceProductRequest
    ): Response<EcommerceProductResponse>
    
    @POST("api/iot/data")
    suspend fun processIoTData(
        @Body request: IoTDataRequest
    ): Response<ComplianceResponse>
    
    @GET("api/reports/{reportId}")
    suspend fun getReport(
        @Path("reportId") reportId: String
    ): Response<ComplianceReport>
    
    @GET("api/reports/user/{userId}")
    suspend fun getUserReports(
        @Path("userId") userId: String
    ): Response<List<ComplianceReport>>
    
    @GET("api/reports/inspector")
    suspend fun getInspectorReports(
        @Query("status") status: String? = null,
        @Query("riskLevel") riskLevel: String? = null
    ): Response<List<ComplianceReport>>
}
