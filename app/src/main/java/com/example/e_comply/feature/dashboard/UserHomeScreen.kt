package com.example.e_comply.feature.dashboard

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.e_comply.ui.theme.*
import com.example.e_comply.feature.login.AuthViewModel
import com.example.e_comply.feature.scanner.ScanViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UserHomeScreen(
    onNavigateToCamera: () -> Unit,
    onNavigateToReports: () -> Unit,
    onNavigateToOcrDemo: () -> Unit = {},
    onNavigateToSettings: () -> Unit = {},
    onNavigateToAnalytics: () -> Unit = {},
    onLogout: () -> Unit,
    authViewModel: AuthViewModel = hiltViewModel()
) {
    val currentUser by authViewModel.currentUser.collectAsState()
    val dimens = rememberDimensions()
    var selectedTab by remember { mutableIntStateOf(0) }
    var contentVisible by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) { contentVisible = true }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(32.dp)
                                .clip(CircleShape)
                                .background(
                                    Brush.linearGradient(listOf(GradientStart, GradientMid))
                                ),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                Icons.Outlined.Shield,
                                contentDescription = null,
                                tint = Color.White,
                                modifier = Modifier.size(18.dp)
                            )
                        }
                        Spacer(modifier = Modifier.width(dimens.itemSpacing))
                        Text(
                            "E-Comply",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                    }
                },
                actions = {
                    IconButton(onClick = onNavigateToSettings) {
                        Icon(Icons.Outlined.Settings, contentDescription = "Settings")
                    }
                }
            )
        },
        bottomBar = {
            NavigationBar(
                containerColor = MaterialTheme.colorScheme.surface,
                tonalElevation = 0.dp
            ) {
                NavigationBarItem(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    icon = {
                        Icon(
                            if (selectedTab == 0) Icons.Filled.Home else Icons.Outlined.Home,
                            contentDescription = "Home"
                        )
                    },
                    label = { Text("Home", style = MaterialTheme.typography.labelSmall) }
                )
                NavigationBarItem(
                    selected = selectedTab == 1,
                    onClick = {
                        selectedTab = 1
                        onNavigateToCamera()
                    },
                    icon = {
                        Icon(
                            if (selectedTab == 1) Icons.Filled.CameraAlt
                            else Icons.Outlined.CameraAlt,
                            contentDescription = "Scan"
                        )
                    },
                    label = { Text("Scan", style = MaterialTheme.typography.labelSmall) }
                )
                NavigationBarItem(
                    selected = selectedTab == 2,
                    onClick = {
                        selectedTab = 2
                        onNavigateToReports()
                    },
                    icon = {
                        Icon(
                            if (selectedTab == 2) Icons.Filled.Description
                            else Icons.Outlined.Description,
                            contentDescription = "Reports"
                        )
                    },
                    label = { Text("Reports", style = MaterialTheme.typography.labelSmall) }
                )
                NavigationBarItem(
                    selected = selectedTab == 3,
                    onClick = {
                        selectedTab = 3
                        onNavigateToAnalytics()
                    },
                    icon = {
                        Icon(
                            if (selectedTab == 3) Icons.Filled.BarChart
                            else Icons.Outlined.BarChart,
                            contentDescription = "Analytics"
                        )
                    },
                    label = { Text("Analytics", style = MaterialTheme.typography.labelSmall) }
                )
            }
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = onNavigateToCamera,
                containerColor = MaterialTheme.colorScheme.primary,
                contentColor = MaterialTheme.colorScheme.onPrimary,
                shape = RoundedCornerShape(dimens.cardRadius)
            ) {
                Icon(Icons.Default.PhotoCamera, contentDescription = "Scan")
            }
        },
        containerColor = MaterialTheme.colorScheme.background
    ) { paddingValues ->
        AnimatedVisibility(
            visible = contentVisible,
            enter = fadeIn(tween(400)) + slideInVertically(tween(400)) { it / 5 }
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(paddingValues)
                    .padding(horizontal = dimens.screenPaddingH)
                    .padding(top = dimens.screenPaddingV)
            ) {
                // ── Hero Card ────────────────────────────────────────
                Card(
                    shape = RoundedCornerShape(dimens.cardRadius),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Box(
                        modifier = Modifier
                            .background(
                                brush = Brush.linearGradient(
                                    colors = listOf(GradientStart, GradientMid, GradientEnd)
                                )
                            )
                            .padding(dimens.cardPadding + 4.dp)
                    ) {
                        Column {
                            Text(
                                text = "Hello, ${currentUser?.name ?: "there"} 👋",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                            Spacer(modifier = Modifier.height(6.dp))
                            Text(
                                text = "Scan product labels to verify compliance\nwith Legal Metrology Rules, 2011",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color.White.copy(alpha = 0.75f),
                                lineHeight = 20.sp
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(dimens.sectionSpacing))

                // ── Stats Row ────────────────────────────────────────
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(dimens.itemSpacing)
                ) {
                    MiniStatCard(
                        modifier = Modifier.weight(1f),
                        label = "Scans",
                        value = "12",
                        color = ChartBlue,
                        dimens = dimens
                    )
                    MiniStatCard(
                        modifier = Modifier.weight(1f),
                        label = "Passed",
                        value = "9",
                        color = ComplianceGreen,
                        dimens = dimens
                    )
                    MiniStatCard(
                        modifier = Modifier.weight(1f),
                        label = "Failed",
                        value = "3",
                        color = DangerRed,
                        dimens = dimens
                    )
                }

                Spacer(modifier = Modifier.height(dimens.sectionSpacing))

                Text(
                    text = "Quick Actions",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.padding(bottom = dimens.itemSpacing)
                )

                val scanViewModel: com.example.e_comply.ui.viewmodel.ScanViewModel = hiltViewModel()
                val scanState by scanViewModel.scanState.collectAsState()

                ActionCard(
                    icon = Icons.Default.AutoFixHigh,
                    title = "Quick Demo Scan",
                    subtitle = "Instant scan & report (Invigilator Demo)",
                    gradient = listOf(BrandPrimary, BrandSecondary),
                    dimens = dimens,
                    onClick = {
                        scanViewModel.triggerDemoScan { reportId ->
                            // Small delay to show "Processing"
                            onNavigateToReports() // Navigation to individual report is handled by passing reportId usually, 
                            // for this demo we'll assume we navigate to a screen that shows the latest report
                        }
                    }
                )

                if (scanState is com.example.e_comply.ui.viewmodel.ScanState.Extracting) {
                    LinearProgressIndicator(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                        color = BrandPrimary
                    )
                }

                Spacer(modifier = Modifier.height(dimens.itemSpacing))

                ActionCard(
                    icon = Icons.Default.PhotoCamera,
                    title = "Scan Product",
                    subtitle = "Capture label and validate compliance",
                    gradient = listOf(GradientStart, GradientMid),
                    dimens = dimens,
                    onClick = onNavigateToCamera
                )

                Spacer(modifier = Modifier.height(dimens.itemSpacing))

                ActionCard(
                    icon = Icons.AutoMirrored.Filled.List,
                    title = "My Reports",
                    subtitle = "View past compliance reports",
                    gradient = listOf(ChartIndigo, CriticalPurple),
                    dimens = dimens,
                    onClick = onNavigateToReports
                )

                Spacer(modifier = Modifier.height(dimens.itemSpacing))

                ActionCard(
                    icon = Icons.Outlined.BarChart,
                    title = "Analytics",
                    subtitle = "Trends, risk distribution, insights",
                    gradient = listOf(ComplianceGreen, ChartCyan),
                    dimens = dimens,
                    onClick = onNavigateToAnalytics
                )

                Spacer(modifier = Modifier.height(dimens.itemSpacing))

                ActionCard(
                    icon = Icons.Default.DocumentScanner,
                    title = "OCR Demo",
                    subtitle = "Test ML Kit text recognition",
                    gradient = listOf(WarningAmber, ChartOrange),
                    dimens = dimens,
                    onClick = onNavigateToOcrDemo
                )

                Spacer(modifier = Modifier.height(dimens.sectionSpacing))

                // ── Tip Card ─────────────────────────────────────────
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.5f)
                    ),
                    shape = RoundedCornerShape(dimens.cardRadius)
                ) {
                    Row(
                        modifier = Modifier.padding(dimens.cardPadding),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("💡", fontSize = 20.sp)
                        Spacer(modifier = Modifier.width(dimens.itemSpacing))
                        Text(
                            text = "Tip: Hold the label steady in good light for best OCR results.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                Spacer(modifier = Modifier.height(80.dp))
            }
        }
    }
}

// ─── Components ──────────────────────────────────────────────────────────────

@Composable
private fun MiniStatCard(
    modifier: Modifier = Modifier,
    label: String,
    value: String,
    color: Color,
    dimens: Dimensions
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(dimens.cardRadius),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(dimens.cardPadding),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .clip(CircleShape)
                    .background(color)
            )
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = value,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = color
            )
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ActionCard(
    icon: ImageVector,
    title: String,
    subtitle: String,
    gradient: List<Color>,
    dimens: Dimensions,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(dimens.cardRadius),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(dimens.cardPadding),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(dimens.iconSizeLg + 4.dp)
                    .clip(RoundedCornerShape(dimens.cardRadius - 4.dp))
                    .background(Brush.linearGradient(gradient)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    icon,
                    contentDescription = null,
                    tint = Color.White,
                    modifier = Modifier.size(dimens.iconSize)
                )
            }
            Spacer(modifier = Modifier.width(dimens.itemSpacing + 2.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Icon(
                Icons.Outlined.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.4f),
                modifier = Modifier.size(20.dp)
            )
        }
    }
}

// Keep FeatureCard for backward compat
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FeatureCard(
    icon: ImageVector,
    title: String,
    description: String,
    onClick: () -> Unit
) {
    val dimens = rememberDimensions()
    ActionCard(
        icon = icon,
        title = title,
        subtitle = description,
        gradient = listOf(GradientStart, GradientMid),
        dimens = dimens,
        onClick = onClick
    )
}
