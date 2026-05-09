package com.example.e_comply.feature.navigation

sealed class Screen(val route: String) {
    object Splash : Screen("splash")
    object Login : Screen("login")
    object SignUp : Screen("signup")
    object UserHome : Screen("user_home")
    object InspectorHome : Screen("inspector_home")
    object Camera : Screen("camera")
    object ScanResult : Screen("scan_result")
    object Reports : Screen("reports")
    object ComplianceReport : Screen("compliance_report/{reportId}") {
        fun createRoute(reportId: String) = "compliance_report/$reportId"
    }
    object ProductDetails : Screen("product_details/{productId}") {
        fun createRoute(productId: String) = "product_details/$productId"
    }
    object InspectorDashboard : Screen("inspector_dashboard")
    object ReportsList : Screen("reports_list")
    object Settings : Screen("settings")
    object Analytics : Screen("analytics")
    object TextRecognitionDemo : Screen("text_recognition_demo")
}
