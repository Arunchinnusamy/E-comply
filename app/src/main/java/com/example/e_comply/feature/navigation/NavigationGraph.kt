package com.example.e_comply.feature.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.example.e_comply.data.model.UserType
import com.example.e_comply.feature.login.*
import com.example.e_comply.feature.dashboard.*
import com.example.e_comply.feature.scanner.*
import com.example.e_comply.feature.validation.*
import com.example.e_comply.feature.admin.*
import com.example.e_comply.feature.reports.*
import com.example.e_comply.feature.ai.*

@Composable
fun NavigationGraph(
    navController: NavHostController,
    authViewModel: AuthViewModel = hiltViewModel()
) {
    val authState by authViewModel.authState.collectAsState()
    val currentUser by authViewModel.currentUser.collectAsState()

    // Handle logout navigation
    androidx.compose.runtime.LaunchedEffect(authState) {
        if (authState is AuthState.Unauthenticated) {
            val currentRoute = navController.currentDestination?.route
            if (currentRoute != Screen.Login.route && 
                currentRoute != Screen.SignUp.route && 
                currentRoute != Screen.Splash.route) {
                
                navController.navigate(Screen.Login.route) {
                    popUpTo(navController.graph.id) { inclusive = true }
                    launchSingleTop = true
                }
            }
        }
    }
    
    NavHost(
        navController = navController,
        startDestination = Screen.Splash.route
    ) {
        // ═════════════════════════════════════════════════════════════
        // Splash Screen
        // ═════════════════════════════════════════════════════════════
        composable(Screen.Splash.route) {
            SplashScreen(
                onNavigateToLogin = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(Screen.Splash.route) { inclusive = true }
                    }
                },
                onNavigateToUserHome = {
                    navController.navigate(Screen.UserHome.route) {
                        popUpTo(Screen.Splash.route) { inclusive = true }
                    }
                },
                onNavigateToInspectorHome = {
                    navController.navigate(Screen.InspectorHome.route) {
                        popUpTo(Screen.Splash.route) { inclusive = true }
                    }
                },
                authViewModel = authViewModel
            )
        }

        // ═════════════════════════════════════════════════════════════
        // Login
        // ═════════════════════════════════════════════════════════════
        composable(Screen.Login.route) {
            LoginScreen(
                onNavigateToSignUp = {
                    navController.navigate(Screen.SignUp.route)
                },
                onLoginSuccess = { userType ->
                    val destination = if (userType == UserType.INSPECTOR) {
                        Screen.InspectorHome.route
                    } else {
                        Screen.UserHome.route
                    }
                    navController.navigate(destination) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }
        
        // ═════════════════════════════════════════════════════════════
        // Register (Sign Up)
        // ═════════════════════════════════════════════════════════════
        composable(Screen.SignUp.route) {
            SignUpScreen(
                onNavigateToLogin = {
                    navController.popBackStack()
                },
                onSignUpSuccess = { userType ->
                    val destination = if (userType == UserType.INSPECTOR) {
                        Screen.InspectorHome.route
                    } else {
                        Screen.UserHome.route
                    }
                    navController.navigate(destination) {
                        popUpTo(Screen.SignUp.route) { inclusive = true }
                    }
                }
            )
        }
        
        // ═════════════════════════════════════════════════════════════
        // User Dashboard (Home)
        // ═════════════════════════════════════════════════════════════
        composable(Screen.UserHome.route) {
            UserHomeScreen(
                onNavigateToCamera = {
                    navController.navigate(Screen.Camera.route)
                },
                onNavigateToReports = {
                    navController.navigate(Screen.Reports.route)
                },
                onNavigateToOcrDemo = {
                    navController.navigate(Screen.TextRecognitionDemo.route)
                },
                onNavigateToSettings = {
                    navController.navigate(Screen.Settings.route)
                },
                onNavigateToAnalytics = {
                    navController.navigate(Screen.Analytics.route)
                },
                onLogout = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(navController.graph.id) { inclusive = true }
                        launchSingleTop = true
                    }
                },
                authViewModel = authViewModel
            )
        }
        
        // ═════════════════════════════════════════════════════════════
        // Admin / Inspector Home
        // ═════════════════════════════════════════════════════════════
        composable(Screen.InspectorHome.route) {
            InspectorHomeScreen(
                onNavigateToDashboard = {
                    navController.navigate(Screen.InspectorDashboard.route)
                },
                onNavigateToReports = {
                    navController.navigate(Screen.ReportsList.route)
                },
                onNavigateToAnalytics = {
                    navController.navigate(Screen.Analytics.route)
                },
                onNavigateToSettings = {
                    navController.navigate(Screen.Settings.route)
                },
                onLogout = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(navController.graph.id) { inclusive = true }
                        launchSingleTop = true
                    }
                },
                authViewModel = authViewModel
            )
        }
        
        // ═════════════════════════════════════════════════════════════
        // Scan Product (Camera)
        // ═════════════════════════════════════════════════════════════
        composable(Screen.Camera.route) {
            CameraScreen(
                onBack = {
                    navController.popBackStack()
                },
                onImageCaptured = {
                    navController.navigate(Screen.ScanResult.route)
                }
            )
        }
        
        // ═════════════════════════════════════════════════════════════
        // Scan Result
        // ═════════════════════════════════════════════════════════════
        composable(Screen.ScanResult.route) {
            ScanResultScreen(
                onBack = {
                    navController.popBackStack()
                },
                onNavigateToReport = { reportId ->
                    navController.navigate(Screen.ComplianceReport.createRoute(reportId))
                }
            )
        }
        
        // ═════════════════════════════════════════════════════════════
        // Validation Report (Compliance Report)
        // ═════════════════════════════════════════════════════════════
        composable(
            route = Screen.ComplianceReport.route,
            arguments = listOf(navArgument("reportId") { type = NavType.StringType })
        ) { backStackEntry ->
            val reportId = backStackEntry.arguments?.getString("reportId") ?: ""
            ComplianceReportScreen(
                reportId = reportId,
                onBack = {
                    navController.popBackStack()
                }
            )
        }
        
        // ═════════════════════════════════════════════════════════════
        // Admin Dashboard (Inspector Dashboard)
        // ═════════════════════════════════════════════════════════════
        composable(Screen.InspectorDashboard.route) {
            InspectorDashboardScreen(
                onBack = {
                    navController.popBackStack()
                },
                onReportClick = { reportId ->
                    navController.navigate(Screen.ComplianceReport.createRoute(reportId))
                }
            )
        }
        
        // ═════════════════════════════════════════════════════════════
        // Reports List
        // ═════════════════════════════════════════════════════════════
        composable(Screen.ReportsList.route) {
            ReportsListScreen(
                onBack = {
                    navController.popBackStack()
                },
                onReportClick = { reportId ->
                    navController.navigate(Screen.ComplianceReport.createRoute(reportId))
                }
            )
        }

        // ═════════════════════════════════════════════════════════════
        // User Reports
        // ═════════════════════════════════════════════════════════════
        composable(Screen.Reports.route) {
            ReportsScreen(
                onBack = {
                    navController.popBackStack()
                }
            )
        }

        // ═════════════════════════════════════════════════════════════
        // Analytics
        // ═════════════════════════════════════════════════════════════
        composable(Screen.Analytics.route) {
            AnalyticsScreen(
                onBack = {
                    navController.popBackStack()
                },
                onReportClick = { reportId ->
                    navController.navigate(Screen.ComplianceReport.createRoute(reportId))
                }
            )
        }

        // ═════════════════════════════════════════════════════════════
        // Settings
        // ═════════════════════════════════════════════════════════════
        composable(Screen.Settings.route) {
            SettingsScreen(
                onBack = {
                    navController.popBackStack()
                },
                onLogout = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(navController.graph.id) { inclusive = true }
                        launchSingleTop = true
                    }
                },
                authViewModel = authViewModel
            )
        }

        // ═════════════════════════════════════════════════════════════
        // OCR Demo
        // ═════════════════════════════════════════════════════════════
        composable(Screen.TextRecognitionDemo.route) {
            TextRecognitionDemoScreen(capturedBitmap = null)
        }
    }
}
