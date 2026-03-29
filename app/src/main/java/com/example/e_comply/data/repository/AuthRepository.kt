package com.example.e_comply.data.repository

import com.example.e_comply.data.model.User
import com.example.e_comply.data.model.UserType
import com.google.firebase.auth.ActionCodeSettings
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.FirebaseUser
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.firestore.FirebaseFirestoreException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Outcome of a successful email/password sign-in.
 * - [UserLoggedIn]              — regular user, fully authenticated.
 * - [InspectorNeedsVerification] — inspector role; caller must still verify
 *   the Inspector ID via [AuthRepository.verifyInspectorId] before granting
 *   access to the inspector dashboard.
 */
sealed class SignInOutcome {
    data class UserLoggedIn(val user: User) : SignInOutcome()
    data class InspectorNeedsVerification(val user: User) : SignInOutcome()
}

@Singleton
class AuthRepository @Inject constructor(
    private val auth: FirebaseAuth,
    private val firestore: FirebaseFirestore
) {
    // Long-lived scope for fire-and-forget background writes that must not
    // block the caller.  SupervisorJob ensures a failing child never cancels
    // the scope itself.
    private val appScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    val currentUser: FirebaseUser?
        get() = auth.currentUser

    /**
     * Creates a new account in Firebase Auth and persists the user profile in
     * Firestore.  For inspector accounts, [inspectorId] is stored and later
     * validated on every sign-in as a second verification factor.
     */
    suspend fun signUp(
        email: String,
        password: String,
        name: String,
        userType: UserType,
        phone: String,
        inspectorId: String = ""
    ): Result<User> {
        return try {
            val authResult = auth.createUserWithEmailAndPassword(email, password).await()
            val firebaseUser = authResult.user ?: throw Exception("User ID not found")
            val userId = firebaseUser.uid
            val normalizedEmail = email.trim()
            val normalizedName = name.trim()
            val normalizedPhone = phone.trim()
            val normalizedInspectorId = inspectorId.trim()
            val createdAt = System.currentTimeMillis()
            val role = userTypeToRole(userType)
            val userTypeValue = userType.name

            val newUser = User(
                id = userId,
                email = normalizedEmail,
                name = normalizedName,
                userType = userType,
                phone = normalizedPhone,
                inspectorId = if (userType == UserType.INSPECTOR) normalizedInspectorId else "",
                createdAt = createdAt
            )

            // Persist the profile in the background so the caller is unblocked
            // as soon as Firebase Auth creation succeeds.
            appScope.launch {
                try {
                    val profileData = mutableMapOf<String, Any>(
                        "id" to userId,
                        "email" to normalizedEmail,
                        "name" to normalizedName,
                        "phone" to normalizedPhone,
                        "createdAt" to createdAt,
                        "role" to role,
                        "userType" to userTypeValue
                    )
                    if (userType == UserType.INSPECTOR && normalizedInspectorId.isNotBlank()) {
                        profileData["inspectorId"] = normalizedInspectorId
                    }
                    firestore.collection("users")
                        .document(userId)
                        .set(profileData)
                        .await()
                } catch (e: Exception) {
                    // Profile write failed; tolerated - next login will retry.
                }
            }

            Result.success(newUser)
        } catch (e: Exception) {
            Result.failure(mapAuthException(e))
        }
    }

    /**
     * Phase-1 sign-in: validates email + password with Firebase Auth and reads
     * the user's role from Firestore.
     *
     * Returns [SignInOutcome.UserLoggedIn] for regular users (fully authenticated)
     * or [SignInOutcome.InspectorNeedsVerification] for inspectors, indicating
     * that the caller must follow up with [verifyInspectorId] before granting
     * access to protected inspector screens.
     */
    suspend fun signIn(email: String, password: String): Result<SignInOutcome> {
        return try {
            val authResult = auth.signInWithEmailAndPassword(email, password).await()
            val firebaseUser = authResult.user ?: throw Exception("User ID not found")
            val userId = firebaseUser.uid

            val userDoc = firestore.collection("users")
                .document(userId)
                .get()
                .await()

            // Guard against the race window where a just-signed-up user tries
            // to sign in before the background profile write has landed.
            val resolvedDoc = if (!userDoc.exists()) {
                delay(2_000)
                firestore.collection("users").document(userId).get().await()
            } else {
                userDoc
            }
            if (!resolvedDoc.exists()) throw Exception("User profile not found")

            val user = mapUserDocumentToUser(firebaseUser, resolvedDoc.data.orEmpty())
            val outcome: SignInOutcome = if (user.userType == UserType.INSPECTOR) {
                SignInOutcome.InspectorNeedsVerification(user)
            } else {
                SignInOutcome.UserLoggedIn(user)
            }
            Result.success(outcome)
        } catch (e: Exception) {
            Result.failure(mapAuthException(e))
        }
    }

    /**
     * Phase-2 sign-in for inspectors: verifies the provided [inspectorId]
     * against the value stored in Firestore for the currently authenticated
     * Firebase user.
     *
     * Must only be called after [signIn] returns
     * [SignInOutcome.InspectorNeedsVerification].
     */
    suspend fun verifyInspectorId(inspectorId: String): Result<User> {
        return try {
            val firebaseUser = auth.currentUser
                ?: throw Exception("Not authenticated. Please sign in again.")

            val userDoc = firestore.collection("users")
                .document(firebaseUser.uid)
                .get()
                .await()

            if (!userDoc.exists()) throw Exception("User profile not found.")

            val data = userDoc.data.orEmpty()
            val storedId = (data["inspectorId"] as? String).orEmpty().trim()
            val providedId = inspectorId.trim()

            if (storedId.isBlank()) {
                throw Exception("No Inspector ID is registered for this account. Contact your administrator.")
            }
            // Case-sensitive comparison — Inspector IDs are treated as opaque tokens.
            if (storedId != providedId) {
                throw Exception("Invalid Inspector ID. Access denied.")
            }

            Result.success(mapUserDocumentToUser(firebaseUser, data))
        } catch (e: Exception) {
            Result.failure(mapAuthException(e))
        }
    }

    suspend fun getCurrentUser(): Result<User?> {
        return try {
            val userId = currentUser?.uid
            if (userId == null) {
                Result.success(null)
            } else {
                val firebaseUser = currentUser ?: return Result.success(null)
                val userDoc = firestore.collection("users")
                    .document(userId)
                    .get()
                    .await()

                // Same background-write race guard as signIn().
                val resolvedDoc = if (!userDoc.exists()) {
                    delay(2_000)
                    firestore.collection("users").document(userId).get().await()
                } else {
                    userDoc
                }
                if (!resolvedDoc.exists()) {
                    Result.failure(Exception("User profile not found"))
                } else {
                    Result.success(mapUserDocumentToUser(firebaseUser, resolvedDoc.data.orEmpty()))
                }
            }
        } catch (e: Exception) {
            Result.failure(mapAuthException(e))
        }
    }

    fun signOut() {
        auth.signOut()
    }

    suspend fun resetPassword(email: String): Result<Unit> {
        return try {
            val actionCodeSettings = ActionCodeSettings.newBuilder()
                .setHandleCodeInApp(false)
                .setUrl("https://e-comply.firebaseapp.com")
                .build()

            auth.sendPasswordResetEmail(email.trim(), actionCodeSettings).await()
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun roleToUserType(role: String): UserType {
        return when (role.lowercase().trim()) {
            "inspector" -> UserType.INSPECTOR
            "admin"     -> UserType.INSPECTOR  // backward-compat for existing data
            "user"      -> UserType.GENERAL_USER
            else -> throw Exception("Invalid role: $role")
        }
    }

    private fun userTypeToRole(userType: UserType): String {
        return if (userType == UserType.INSPECTOR) "inspector" else "user"
    }

    private fun mapUserDocumentToUser(firebaseUser: FirebaseUser, data: Map<String, Any>): User {
        val roleValue = (data["role"] as? String).orEmpty()
        val legacyUserType = (data["userType"] as? String).orEmpty()
        val resolvedUserType = when {
            roleValue.isNotBlank() -> roleToUserType(roleValue)
            legacyUserType.isNotBlank() -> legacyToUserType(legacyUserType)
            else -> throw Exception("Role missing")
        }

        val createdAt = when (val raw = data["createdAt"]) {
            is Long -> raw
            is Number -> raw.toLong()
            else -> System.currentTimeMillis()
        }

        return User(
            id = firebaseUser.uid,
            email = (data["email"] as? String).orEmpty().ifBlank { firebaseUser.email.orEmpty() },
            name = (data["name"] as? String).orEmpty().ifBlank { firebaseUser.displayName.orEmpty() },
            userType = resolvedUserType,
            phone = (data["phone"] as? String).orEmpty().ifBlank { firebaseUser.phoneNumber.orEmpty() },
            inspectorId = (data["inspectorId"] as? String).orEmpty().trim(),
            createdAt = createdAt
        )
    }

    private fun legacyToUserType(value: String): UserType {
        return when (value.uppercase().trim()) {
            "INSPECTOR" -> UserType.INSPECTOR
            "GENERAL_USER" -> UserType.GENERAL_USER
            else -> throw Exception("Invalid userType: $value")
        }
    }

    private fun mapAuthException(e: Exception): Exception {
        return if (e is FirebaseFirestoreException && e.code == FirebaseFirestoreException.Code.PERMISSION_DENIED) {
            Exception("Firestore permission denied. Check Firestore rules for users/{uid} create/read/write.")
        } else {
            e
        }
    }
}
