package com.example.e_comply.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.e_comply.data.model.User
import com.example.e_comply.data.model.UserType
import com.example.e_comply.data.repository.AuthRepository
import com.example.e_comply.data.repository.SignInOutcome
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    private val _authState = MutableStateFlow<AuthState>(AuthState.Initial)
    val authState: StateFlow<AuthState> = _authState.asStateFlow()

    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser.asStateFlow()

    /**
     * True while an inspector has passed email/password auth but has not yet
     * successfully verified their Inspector ID.  The LoginScreen uses this to
     * keep the ID-verification form visible even when the state transitions to
     * [AuthState.Error] after a failed verification attempt.
     */
    private val _isInspectorVerificationPending = MutableStateFlow(false)
    val isInspectorVerificationPending: StateFlow<Boolean> =
        _isInspectorVerificationPending.asStateFlow()
    
    init {
        checkAuthStatus()
    }
    
    private fun checkAuthStatus() {
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            val result = authRepository.getCurrentUser()
            result.onSuccess { user ->
                _currentUser.value = user
                _authState.value = if (user != null) {
                    AuthState.Authenticated(user)
                } else {
                    AuthState.Unauthenticated
                }
            }.onFailure {
                _authState.value = AuthState.Unauthenticated
            }
        }
    }
    
    fun signUp(
        email: String,
        password: String,
        name: String,
        userType: UserType,
        phone: String,
        inspectorId: String = ""
    ) {
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            val result = authRepository.signUp(email, password, name, userType, phone, inspectorId)
            result.onSuccess { user ->
                _currentUser.value = user
                _authState.value = AuthState.Authenticated(user)
            }.onFailure { exception ->
                _authState.value = AuthState.Error(exception.message ?: "Sign up failed")
            }
        }
    }
    
    /**
     * Phase-1: authenticates with email + password.
     * On success, either moves to [AuthState.Authenticated] (regular user) or
     * [AuthState.InspectorIdRequired] (inspector awaiting ID verification).
     */
    fun signIn(email: String, password: String) {
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            val result = authRepository.signIn(email, password)
            result.onSuccess { outcome ->
                when (outcome) {
                    is SignInOutcome.UserLoggedIn -> {
                        _isInspectorVerificationPending.value = false
                        _currentUser.value = outcome.user
                        _authState.value = AuthState.Authenticated(outcome.user)
                    }
                    is SignInOutcome.InspectorNeedsVerification -> {
                        _currentUser.value = outcome.user
                        _isInspectorVerificationPending.value = true
                        _authState.value = AuthState.InspectorIdRequired
                    }
                }
            }.onFailure { exception ->
                _isInspectorVerificationPending.value = false
                _authState.value = AuthState.Error(exception.message ?: "Sign in failed")
            }
        }
    }

    /**
     * Phase-2 (inspector only): verifies the supplied [inspectorId] against
     * the value stored in Firestore.  On success, transitions to
     * [AuthState.Authenticated].
     */
    fun verifyInspectorId(inspectorId: String) {
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            val result = authRepository.verifyInspectorId(inspectorId)
            result.onSuccess { user ->
                _isInspectorVerificationPending.value = false
                _currentUser.value = user
                _authState.value = AuthState.Authenticated(user)
            }.onFailure { exception ->
                // Keep _isInspectorVerificationPending true so the ID form stays visible.
                _authState.value = AuthState.Error(
                    exception.message ?: "Inspector ID verification failed"
                )
            }
        }
    }

    /**
     * Cancels inspector ID verification, signs the Firebase Auth session out,
     * and returns the UI to the unauthenticated state.
     */
    fun cancelInspectorVerification() {
        _isInspectorVerificationPending.value = false
        authRepository.signOut()
        _currentUser.value = null
        _authState.value = AuthState.Unauthenticated
    }
    
    fun signOut() {
        authRepository.signOut()
        _currentUser.value = null
        _authState.value = AuthState.Unauthenticated
    }
    
    fun resetPassword(email: String) {
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            val result = authRepository.resetPassword(email)
            result.onSuccess {
                _authState.value = AuthState.PasswordResetSent
            }.onFailure { exception ->
                _authState.value = AuthState.Error(exception.message ?: "Password reset failed")
            }
        }
    }
    
    fun clearError() {
        if (_authState.value is AuthState.Error) {
            // If inspector verification was pending when the error occurred,
            // go back to the ID-required step rather than fully unauthenticating.
            _authState.value = if (_isInspectorVerificationPending.value) {
                AuthState.InspectorIdRequired
            } else {
                AuthState.Unauthenticated
            }
        }
    }
}

sealed class AuthState {
    object Initial : AuthState()
    object Loading : AuthState()
    object Unauthenticated : AuthState()
    data class Authenticated(val user: User) : AuthState()
    data class Error(val message: String) : AuthState()
    object PasswordResetSent : AuthState()
    /** Inspector has passed email/password auth; must still verify their Inspector ID. */
    object InspectorIdRequired : AuthState()
}
