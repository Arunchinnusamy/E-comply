package com.example.e_comply.data.local.dao

import androidx.room.*
import com.example.e_comply.data.local.entity.ProductEntity
import kotlinx.coroutines.flow.Flow

/**
 * Room DAO for [ProductEntity].
 *
 * List queries return [Flow] so Room emits a new list automatically
 * whenever the underlying table changes – no manual refresh needed.
 */
@Dao
interface ProductDao {

    // ── Reads ─────────────────────────────────────────────────────────────────

    /** Observe all products for a user, newest first. */
    @Query("SELECT * FROM products WHERE scannedBy = :userId ORDER BY scannedAt DESC")
    fun getProductsByUser(userId: String): Flow<List<ProductEntity>>

    /** One-shot lookup by primary key (returns null if not cached). */
    @Query("SELECT * FROM products WHERE id = :productId LIMIT 1")
    suspend fun getProductById(productId: String): ProductEntity?

    /** All rows not yet uploaded to Firestore. */
    @Query("SELECT * FROM products WHERE syncStatus = 'PENDING_SYNC' OR syncStatus = 'SYNC_FAILED'")
    suspend fun getPendingSyncProducts(): List<ProductEntity>

    // ── Writes ────────────────────────────────────────────────────────────────

    /**
     * Insert or fully replace a product.  Use this for both new saves and
     * Firestore-fetched updates so the local copy always reflects the latest.
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertProduct(product: ProductEntity)

    /** Bulk upsert – used when refreshing a list from Firestore. */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertProducts(products: List<ProductEntity>)

    /** Update sync status after a successful or failed Firestore write. */
    @Query("UPDATE products SET syncStatus = :syncStatus, lastUpdated = :timestamp WHERE id = :productId")
    suspend fun updateSyncStatus(productId: String, syncStatus: String, timestamp: Long = System.currentTimeMillis())

    /** Update the Firebase Storage image URL once the upload completes. */
    @Query("UPDATE products SET imageUrl = :imageUrl WHERE id = :productId")
    suspend fun updateImageUrl(productId: String, imageUrl: String)

    @Delete
    suspend fun deleteProduct(product: ProductEntity)

    @Query("DELETE FROM products WHERE id = :productId")
    suspend fun deleteProductById(productId: String)
}
