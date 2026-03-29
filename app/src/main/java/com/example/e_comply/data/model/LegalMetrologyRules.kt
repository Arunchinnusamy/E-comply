package com.example.e_comply.data.model

data class LegalMetrologyRule(
    val fieldName: String,
    val isMandatory: Boolean,
    val description: String,
    val validationPattern: String? = null,
    val errorMessage: String
)

object LegalMetrologyRules {
    val mandatoryFields = listOf(
        LegalMetrologyRule(
            fieldName = "Manufacturer Name",
            isMandatory = true,
            description = "Name of manufacturer or packer or importer",
            errorMessage = "Manufacturer name is missing"
        ),
        LegalMetrologyRule(
            fieldName = "Manufacturer Address",
            isMandatory = true,
            description = "Complete address of manufacturer",
            errorMessage = "Manufacturer address is missing"
        ),
        LegalMetrologyRule(
            fieldName = "Net Quantity",
            isMandatory = true,
            description = "Net quantity or net content in standard units",
            validationPattern = "\\d+\\s*(kg|g|l|ml|unit|pcs|piece)",
            errorMessage = "Net quantity is missing or invalid"
        ),
        LegalMetrologyRule(
            fieldName = "MRP",
            isMandatory = true,
            description = "Maximum Retail Price (MRP) inclusive of all taxes",
            validationPattern = "(?:MRP|Rs\\.?|₹)\\s*\\d+",
            errorMessage = "MRP is missing"
        ),
        LegalMetrologyRule(
            fieldName = "Manufacturing/Packing Date",
            isMandatory = true,
            description = "Month and year of manufacture or packing",
            errorMessage = "Manufacturing or packing date is missing"
        ),
        LegalMetrologyRule(
            fieldName = "Customer Care Details",
            isMandatory = true,
            description = "Customer care contact number or email",
            errorMessage = "Customer care details are missing"
        ),
        LegalMetrologyRule(
            fieldName = "Country of Origin",
            isMandatory = true,
            description = "Country of origin for imported goods",
            errorMessage = "Country of origin is missing"
        )
    )
    
    val optionalFields = listOf(
        LegalMetrologyRule(
            fieldName = "Expiry Date",
            isMandatory = false,
            description = "Best before or use by date (mandatory for certain products)",
            errorMessage = "Expiry date recommended for perishable products"
        ),
        LegalMetrologyRule(
            fieldName = "Batch Number",
            isMandatory = false,
            description = "Batch or lot number for traceability",
            errorMessage = "Batch number recommended"
        ),
        LegalMetrologyRule(
            fieldName = "Barcode",
            isMandatory = false,
            description = "Unique barcode for product identification",
            errorMessage = "Barcode recommended"
        )
    )
}
