package com.example.e_comply.data.remote

import com.example.e_comply.data.model.ComplianceReport
import com.example.e_comply.data.model.Product
import com.example.e_comply.data.model.StructuredComplianceReport
import okhttp3.ResponseBody
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

/** Request for the new /api/compliance/analyze endpoint */
data class ComplianceAnalyzeRequest(
    val ocrText: String? = null,
    val imageBase64: String? = null,
    val source: String = "mobile"
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

/** Request for /api/category/detect */
data class CategoryDetectRequest(
    val text: String
)

data class CategoryDetectResponse(
    val category: String
)

/** Request for /api/crawler/scan */
data class CrawlerScanRequest(
    val url: String
)

/** Response for /api/inspector/analytics */
data class InspectorAnalytics(
    val total_reports: Int = 0,
    val average_score: Float = 0f,
    val risk_distribution: Map<String, Int> = emptyMap(),
    val status_distribution: Map<String, Int> = emptyMap()
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

    /** New: Full compliance analysis pipeline (OCR text → structured report) */
    @POST("api/compliance/analyze")
    suspend fun analyzeCompliance(
        @Body request: ComplianceAnalyzeRequest
    ): Response<StructuredComplianceReport>
    
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

    /** New: Download compliance report as PDF */
    @GET("api/reports/{reportId}/pdf")
    suspend fun downloadReportPdf(
        @Path("reportId") reportId: String
    ): Response<ResponseBody>

    /** New: Generate PDF from report JSON */
    @POST("api/reports/pdf/generate")
    suspend fun generatePdfFromReport(
        @Body report: StructuredComplianceReport
    ): Response<ResponseBody>

    /** New: Detect product category from text */
    @POST("api/category/detect")
    suspend fun detectCategory(
        @Body request: CategoryDetectRequest
    ): Response<CategoryDetectResponse>

    /** New: Crawl a URL and return compliance report */
    @POST("api/crawler/scan")
    suspend fun crawlerScan(
        @Body request: CrawlerScanRequest
    ): Response<StructuredComplianceReport>

    /** New: Get inspector analytics */
    @GET("api/inspector/analytics")
    suspend fun getInspectorAnalytics(): Response<InspectorAnalytics>
}
