package com.example.e_comply.data.model

/**
 * Structured compliance report matching the backend JSON format.
 *
 * Used for parsing the response from /api/compliance/analyze
 * and for PDF generation / display in the Android UI.
 */
data class StructuredComplianceReport(
    val report_id: String = "",
    val generated_date: String = "",

    val product_details: ProductDetails = ProductDetails(),
    val manufacturer_details: ManufacturerDetails = ManufacturerDetails(),
    val importer_details: ImporterDetails = ImporterDetails(),
    val pricing_details: PricingDetails = PricingDetails(),
    val date_details: DateDetails = DateDetails(),
    val product_identification: ProductIdentification = ProductIdentification(),
    val customer_support: CustomerSupport = CustomerSupport(),

    val country_of_origin: String = "",

    val validation_results: List<FieldValidation> = emptyList(),
    val missing_fields: List<String> = emptyList(),

    val compliance_summary: ComplianceSummary = ComplianceSummary(),
    val remarks: String = ""
)

data class ProductDetails(
    val product_name: String = "",
    val brand_name: String = "",
    val category: String = ""
)

data class ManufacturerDetails(
    val name: String = "",
    val address: String = ""
)

data class ImporterDetails(
    val name: String = "",
    val address: String = ""
)

data class PricingDetails(
    val mrp: String = "",
    val net_quantity: String = ""
)

data class DateDetails(
    val manufacturing_date: String = "",
    val expiry_date: String = ""
)

data class ProductIdentification(
    val batch_number: String = "",
    val barcode: String = "",
    val license_number: String = ""
)

data class CustomerSupport(
    val customer_care: String = ""
)

data class FieldValidation(
    val field: String = "",
    val status: String = "" // "Valid" or "Missing"
)

data class ComplianceSummary(
    val compliance_score: String = "0",
    val risk_level: String = "LOW",
    val overall_status: String = "PENDING"
)
