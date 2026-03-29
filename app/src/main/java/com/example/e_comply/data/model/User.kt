package com.example.e_comply.data.model

data class User(
    val id: String = "",
    val email: String = "",
    val name: String = "",
    val userType: UserType = UserType.GENERAL_USER,
    val phone: String = "",
    val inspectorId: String = "",
    val createdAt: Long = System.currentTimeMillis()
)

enum class UserType {
    GENERAL_USER,
    INSPECTOR
}
