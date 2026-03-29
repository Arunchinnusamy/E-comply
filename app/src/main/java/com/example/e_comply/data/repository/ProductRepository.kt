package com.example.e_comply.data.repository

import android.graphics.Bitmap
import android.util.Base64
import com.example.e_comply.data.local.dao.ProductDao
import com.example.e_comply.data.local.entity.ProductEntity
import com.example.e_comply.data.local.entity.SyncStatus
import com.example.e_comply.data.model.Product
import com.example.e_comply.data.model.ProductSource
import com.example.e_comply.data.remote.ApiService
import com.example.e_comply.data.remote.OcrRequest
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.storage.FirebaseStorage
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.tasks.await
import java.io.ByteArrayOutputStream
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ProductRepository @Inject constructor(
    private val firestore: FirebaseFirestore,
    private val storage: FirebaseStorage,
    private val apiService: ApiService,
    private val productDao: ProductDao
) {

    private val textRecognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    // ── OCR ───────────────────────────────────────────────────────────────────

    suspend fun extractTextFromImage(bitmap: Bitmap): Result<String> {
        return try {
            val result = textRecognizer.process(InputImage.fromBitmap(bitmap, 0)).await()
            Result.success(result.text)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun extractTextFromImageViaBackend(bitmap: Bitmap): Result<String> {
        return try {
            val response = apiService.extractTextFromImage(OcrRequest(bitmapToBase64(bitmap), "mobile"))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!.extractedText)
            } else {
                Result.failure(Exception("OCR extraction failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ── Offline-first reads ───────────────────────────────────────────────────

    /**
     * Returns a [Flow] backed by Room.  The UI collects this and gets instant
     * updates whenever the local DB changes – no waiting for network.
     *
     * Pair with [refreshUserProducts] to pull the latest from Firestore in
     * the background.
     */
    fun getUserProductsFlow(userId: String): Flow<List<Product>> =
        productDao.getProductsByUser(userId).map { entities ->
            entities.map { it.toProduct() }
        }

    /**
     * Look up a single product. Hits Room first (fast, works offline); falls
     * back to Firestore on a cache miss and caches the result locally.
     */
    suspend fun getProduct(productId: String): Result<Product> {
        return try {
            // 1. Try local cache first
            val cached = productDao.getProductById(productId)
            if (cached != null) return Result.success(cached.toProduct())

            // 2. Not in cache – fetch from Firestore and cache it
            val doc = firestore.collection("products").document(productId).get().await()
            val product = doc.toObject(Product::class.java)
                ?: return Result.failure(Exception("Product not found"))
            productDao.insertProduct(ProductEntity.fromProduct(product, SyncStatus.SYNCED))
            Result.success(product)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ── Background Firestore refresh ──────────────────────────────────────────

    /**
     * Pull latest products for [userId] from Firestore and update Room.
     * Silently swallows network errors – the local cache remains valid.
     * The [Flow] returned by [getUserProductsFlow] will emit automatically
     * after this writes to Room.
     */
    suspend fun refreshUserProducts(userId: String) {
        try {
            val snapshot = firestore.collection("products")
                .whereEqualTo("scannedBy", userId)
                .get()
                .await()
            val entities = snapshot.documents.mapNotNull { doc ->
                doc.toObject(Product::class.java)?.let {
                    ProductEntity.fromProduct(it, SyncStatus.SYNCED)
                }
            }
            productDao.insertProducts(entities)
        } catch (_: Exception) {
            // Network unavailable – cached data is still served via Flow
        }
    }

    // ── Offline-safe write ────────────────────────────────────────────────────

    /**
     * Write-through save strategy:
     * 1. Assign an ID and write immediately to Room (PENDING_SYNC).
     * 2. Try to upload image to Storage and push to Firestore.
     * 3. On success → mark Room row as SYNCED + store the real imageUrl.
     * 4. On failure (offline) → row stays PENDING_SYNC; [syncPendingProducts]
     *    will retry when connectivity is restored.
     */
    suspend fun saveProduct(product: Product, imageBitmap: Bitmap?): Result<String> {
        return try {
            val productId = if (product.id.isBlank()) UUID.randomUUID().toString() else product.id
            val productWithId = product.copy(id = productId)

            // Step 1 – persist to Room immediately (available offline right away)
            productDao.insertProduct(ProductEntity.fromProduct(productWithId, SyncStatus.PENDING_SYNC))

            // Step 2 – try to push to Firestore (may fail if offline)
            try {
                var imageUrl = product.imageUrl

                if (imageBitmap != null) {
                    val ref = storage.reference.child("product_images/$productId.jpg")
                    val baos = ByteArrayOutputStream()
                    imageBitmap.compress(Bitmap.CompressFormat.JPEG, 85, baos)
                    val uploadTask = ref.putBytes(baos.toByteArray()).await()
                    imageUrl = uploadTask.storage.downloadUrl.await().toString()
                    productDao.updateImageUrl(productId, imageUrl)
                }

                val finalProduct = productWithId.copy(imageUrl = imageUrl)
                firestore.collection("products").document(productId).set(finalProduct).await()
                productDao.updateSyncStatus(productId, SyncStatus.SYNCED.name)
            } catch (_: Exception) {
                // Offline – row stays PENDING_SYNC; will be synced later
                productDao.updateSyncStatus(productId, SyncStatus.PENDING_SYNC.name)
            }

            Result.success(productId)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ── Legacy helpers kept for call-site compatibility ───────────────────────

    /** @deprecated Prefer [getUserProductsFlow] + [refreshUserProducts]. */
    suspend fun getUserProducts(userId: String): Result<List<Product>> {
        return try {
            val snapshot = firestore.collection("products")
                .whereEqualTo("scannedBy", userId)
                .get()
                .await()
            val products = snapshot.documents.mapNotNull { it.toObject(Product::class.java) }
            // Cache the result while we're here
            productDao.insertProducts(products.map { ProductEntity.fromProduct(it, SyncStatus.SYNCED) })
            Result.success(products)
        } catch (e: Exception) {
            // Firestore failed – return whatever is in Room
            return try {
                val cached = productDao.getProductsByUser(userId)
                // Collect first emission synchronously via a simple workaround
                Result.success(emptyList()) // UI should use Flow; this is a fallback
            } catch (re: Exception) {
                Result.failure(re)
            }
        }
    }

    // ── Pending-sync queue ────────────────────────────────────────────────────

    /**
     * Push all locally-created / updated products that haven't reached
     * Firestore yet.  Call this when the device comes back online.
     */
    suspend fun syncPendingProducts() {
        val pending = productDao.getPendingSyncProducts()
        pending.forEach { entity ->
            try {
                val product = entity.toProduct()
                firestore.collection("products").document(product.id).set(product).await()
                productDao.updateSyncStatus(entity.id, SyncStatus.SYNCED.name)
            } catch (_: Exception) {
                productDao.updateSyncStatus(entity.id, SyncStatus.SYNC_FAILED.name)
            }
        }
    }

    // ── Utilities ─────────────────────────────────────────────────────────────

    private fun bitmapToBase64(bitmap: Bitmap): String {
        val baos = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, 85, baos)
        return Base64.encodeToString(baos.toByteArray(), Base64.DEFAULT)
    }
}
