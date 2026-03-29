package com.example.e_comply.ui.navigation

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
import com.example.e_comply.ui.screens.*
import com.example.e_comply.ui.viewmodel.AuthState
import com.example.e_comply.ui.viewmodel.AuthViewModel

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
            // Check if we are currently on a screen that requires authentication
            // or if we simply need to be redirected to login.
            // We avoid redirecting if we are already on Login, SignUp, or Splash.
            val currentRoute = navController.currentDestination?.route
            if (currentRoute != Screen.Login.route && 
                currentRoute != Screen.SignUp.route && 
                currentRoute != Screen.Splash.route) {
                
                navController.navigate(Screen.Login.route) {
                    // Clear the entire back stack
                    popUpTo(navController.graph.id) { inclusive = true }
                    launchSingleTop = true
                }
            }
        }
    }
    
    val startDestination = when (authState) {
        is AuthState.Authenticated -> {
            if (currentUser?.userType == UserType.INSPECTOR) {
                Screen.InspectorHome.route
            } else {
                Screen.UserHome.route
            }
        }
        else -> Screen.Login.route
    }
    
    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
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
        
        composable(Screen.UserHome.route) {
            UserHomeScreen(
                onNavigateToCamera = {
                    navController.navigate(Screen.Camera.route)
                },
                onNavigateToReports = {
                    navController.navigate(Screen.ReportsList.route)
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
        
        composable(Screen.InspectorHome.route) {
            InspectorHomeScreen(
                onNavigateToDashboard = {
                    navController.navigate(Screen.InspectorDashboard.route)
                },
                onNavigateToReports = {
                    navController.navigate(Screen.ReportsList.route)
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
    }
}
