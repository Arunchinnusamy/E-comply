package com.example.e_comply.data.model

data class Product(
    val id: String = "",
    val name: String = "",
    val brandName: String = "",
    val category: String = "",
    val manufacturerName: String = "",
    val manufacturerAddress: String = "",
    val importerName: String = "",
    val importerAddress: String = "",
    val netQuantity: String = "",
    val mrp: String = "",
    val manufacturingDate: String = "",
    val expiryDate: String = "",
    val customerCareDetails: String = "",
    val countryOfOrigin: String = "",
    val batchNumber: String = "",
    val barcode: String = "",
    val licenseNumber: String = "",
    val imageUrl: String = "",
    val scannedText: String = "",
    val source: ProductSource = ProductSource.MOBILE_SCAN,
    val scannedBy: String = "",
    val scannedAt: Long = System.currentTimeMillis()
)

enum class ProductSource {
    MOBILE_SCAN,
    ECOMMERCE,
    IOT_DEVICE,
    WEB_CRAWLER
}
