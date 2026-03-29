package com.example.e_comply.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.example.e_comply.data.model.Product
import com.example.e_comply.data.model.ProductSource

/**
 * Room entity that mirrors [Product].
 *
 * [source] is stored as the enum's name string so Room doesn't need a
 * TypeConverter for it.  [syncStatus] tracks whether the row has been
 * uploaded to Firestore yet (see [SyncStatus]).
 */
@Entity(tableName = "products")
data class ProductEntity(
    @PrimaryKey val id: String,
    val name: String,
    val manufacturerName: String,
    val manufacturerAddress: String,
    val netQuantity: String,
    val mrp: String,
    val manufacturingDate: String,
    val expiryDate: String,
    val customerCareDetails: String,
    val countryOfOrigin: String,
    val batchNumber: String,
    val barcode: String,
    val imageUrl: String,
    val scannedText: String,
    /** Stored as [ProductSource.name] */
    val source: String,
    val scannedBy: String,
    val scannedAt: Long,
    /** Stored as [SyncStatus.name] */
    val syncStatus: String = SyncStatus.PENDING_SYNC.name,
    val lastUpdated: Long = System.currentTimeMillis()
) {
    fun toProduct(): Product = Product(
        id = id,
        name = name,
        manufacturerName = manufacturerName,
        manufacturerAddress = manufacturerAddress,
        netQuantity = netQuantity,
        mrp = mrp,
        manufacturingDate = manufacturingDate,
        expiryDate = expiryDate,
        customerCareDetails = customerCareDetails,
        countryOfOrigin = countryOfOrigin,
        batchNumber = batchNumber,
        barcode = barcode,
        imageUrl = imageUrl,
        scannedText = scannedText,
        source = runCatching { ProductSource.valueOf(source) }.getOrDefault(ProductSource.MOBILE_SCAN),
        scannedBy = scannedBy,
        scannedAt = scannedAt
    )

    companion object {
        fun fromProduct(
            product: Product,
            syncStatus: SyncStatus = SyncStatus.PENDING_SYNC
        ): ProductEntity = ProductEntity(
            id = product.id,
            name = product.name,
            manufacturerName = product.manufacturerName,
            manufacturerAddress = product.manufacturerAddress,
            netQuantity = product.netQuantity,
            mrp = product.mrp,
            manufacturingDate = product.manufacturingDate,
            expiryDate = product.expiryDate,
            customerCareDetails = product.customerCareDetails,
            countryOfOrigin = product.countryOfOrigin,
            batchNumber = product.batchNumber,
            barcode = product.barcode,
            imageUrl = product.imageUrl,
            scannedText = product.scannedText,
            source = product.source.name,
            scannedBy = product.scannedBy,
            scannedAt = product.scannedAt,
            syncStatus = syncStatus.name,
            lastUpdated = System.currentTimeMillis()
        )
    }
}
