package com.example.e_comply.feature.admin

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
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
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.e_comply.data.remote.InspectorAnalytics
import com.example.e_comply.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnalyticsScreen(
    onBack: () -> Unit,
    onReportClick: (String) -> Unit = {},
    viewModel: AnalyticsViewModel = hiltViewModel()
) {
    val analyticsState by viewModel.analyticsState.collectAsState()
    val dimens = rememberDimensions()
    var contentVisible by remember { mutableStateOf(false) }

    when (val state = analyticsState) {
        is AnalyticsState.Loading -> {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        is AnalyticsState.Error -> {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("Error: ${state.message}", color = MaterialTheme.colorScheme.error)
            }
        }
        is AnalyticsState.Success -> {
            val analytics = state.analytics
            LaunchedEffect(Unit) { contentVisible = true }
            
            val totalScans = analytics.total_reports
            val avgScore = analytics.average_score.toInt()
            
            val riskData = listOf(
                Triple("Low", analytics.risk_distribution.getOrDefault("LOW", 0), ComplianceGreen),
                Triple("Medium", analytics.risk_distribution.getOrDefault("MEDIUM", 0), WarningAmber),
                Triple("High", analytics.risk_distribution.getOrDefault("HIGH", 0), DangerRed),
                Triple("Critical", analytics.risk_distribution.getOrDefault("CRITICAL", 0), CriticalPurple)
            )

            // Category data is currently mock in backend response, but we can simulate or filter
            val categoryData = listOf(
                listOf("Food", "22", "89", "1"),
                listOf("FMCG", "10", "92", "2"),
                listOf("Cosmetics", "8", "78", "3"),
                listOf("Pharma", "4", "95", "4"),
                listOf("Electronics", "3", "67", "5"),
            )

            // Reports are fetched from InspectorDashboard, here we just show the analytics
            val reports = emptyList<List<String>>() // Simplified for now

            Scaffold(
                topBar = {
                    TopAppBar(
                        title = { Text("Analytics", fontWeight = FontWeight.Bold) },
                        navigationIcon = {
                            IconButton(onClick = onBack) {
                                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                            }
                        }
                    )
                },
                containerColor = MaterialTheme.colorScheme.background
            ) { paddingValues ->
                AnimatedVisibility(
                    visible = contentVisible,
                    enter = fadeIn(tween(350)) + slideInVertically(tween(350)) { it / 5 }
                ) {
                    LazyColumn(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(paddingValues)
                            .padding(horizontal = dimens.screenPaddingH),
                        verticalArrangement = Arrangement.spacedBy(dimens.itemSpacing),
                        contentPadding = PaddingValues(vertical = dimens.screenPaddingV)
                    ) {
                        // ── Stat Cards ───────────────────────────────────────
                        item {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(dimens.itemSpacing)
                            ) {
                                GlowStatCard(
                                    Modifier.weight(1f),
                                    Icons.Outlined.DocumentScanner, "Scans",
                                    totalScans.toString(),
                                    listOf(GradientStart, GradientMid), dimens
                                )
                                GlowStatCard(
                                    Modifier.weight(1f),
                                    Icons.Outlined.CheckCircle, "Avg Score",
                                    "$avgScore%",
                                    listOf(ComplianceGreen, ChartCyan), dimens
                                )
                            }
                        }
                        item {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(dimens.itemSpacing)
                            ) {
                                GlowStatCard(
                                    Modifier.weight(1f),
                                    Icons.Outlined.Warning, "Violations",
                                    "${analytics.status_distribution.getOrDefault("NON_COMPLIANT", 0)}", 
                                    listOf(DangerRed, GradientEnd), dimens
                                )
                                GlowStatCard(
                                    Modifier.weight(1f),
                                    Icons.Outlined.TrendingUp, "Trend",
                                    "+12%", listOf(ChartIndigo, CriticalPurple), dimens
                                )
                            }
                        }

                        // ── Risk Distribution ────────────────────────────────
                        item {
                            Text(
                                "Risk Distribution",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold,
                                modifier = Modifier.padding(top = dimens.itemSpacing)
                            )
                        }
                        item {
                            Card(
                                shape = RoundedCornerShape(dimens.cardRadius),
                                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                                elevation = CardDefaults.cardElevation(0.dp)
                            ) {
                                Column(modifier = Modifier.padding(dimens.cardPadding)) {
                                    riskData.forEachIndexed { idx, (label, count, color) ->
                                        val frac = if (totalScans > 0) count.toFloat() / totalScans else 0f
                                        Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) {
                                            Text(label, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
                                            Text("$count (${(frac * 100).toInt()}%)", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                        }
                                        Spacer(Modifier.height(4.dp))
                                        Box(
                                            Modifier
                                                .fillMaxWidth()
                                                .height(8.dp)
                                                .clip(RoundedCornerShape(4.dp))
                                                .background(MaterialTheme.colorScheme.surfaceVariant)
                                        ) {
                                            Box(
                                                Modifier
                                                    .fillMaxHeight()
                                                    .fillMaxWidth(frac)
                                                    .clip(RoundedCornerShape(4.dp))
                                                    .background(Brush.horizontalGradient(listOf(color.copy(alpha = 0.6f), color)))
                                            )
                                        }
                                        if (idx < riskData.lastIndex) Spacer(Modifier.height(dimens.itemSpacing))
                                    }
                                }
                            }
                        }

                        // ── Categories ───────────────────────────────────────
                        item {
                            Text(
                                "Category Compliance",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.SemiBold,
                                modifier = Modifier.padding(top = dimens.itemSpacing)
                            )
                        }
                        item {
                            Card(
                                shape = RoundedCornerShape(dimens.cardRadius),
                                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                                elevation = CardDefaults.cardElevation(0.dp)
                            ) {
                                val catColors = listOf(ComplianceGreen, ChartBlue, ChartPink, ChartIndigo, ChartOrange)
                                Column(modifier = Modifier.padding(dimens.cardPadding)) {
                                    categoryData.forEachIndexed { idx, cat ->
                                        val score = cat[2].toFloat()
                                        val color = catColors[idx % catColors.size]
                                        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                                            Box(
                                                Modifier
                                                    .size(34.dp)
                                                    .clip(RoundedCornerShape(8.dp))
                                                    .background(color.copy(alpha = 0.12f)),
                                                Alignment.Center
                                            ) {
                                                Text(cat[0].first().toString(), style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold, color = color)
                                            }
                                            Spacer(Modifier.width(dimens.itemSpacing))
                                            Column(Modifier.weight(1f)) {
                                                Text(cat[0], style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
                                                Text("${cat[1]} products", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                            }
                                            val scoreColor = if (score >= 80) ComplianceGreen else if (score >= 60) WarningAmber else DangerRed
                                            Surface(
                                                shape = RoundedCornerShape(6.dp),
                                                color = scoreColor.copy(alpha = 0.12f)
                                            ) {
                                                Text(
                                                    "${score.toInt()}%",
                                                    Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
                                                    style = MaterialTheme.typography.labelMedium,
                                                    fontWeight = FontWeight.SemiBold,
                                                    color = scoreColor
                                                )
                                            }
                                        }
                                        if (idx < categoryData.lastIndex) {
                                            HorizontalDivider(
                                                Modifier.padding(vertical = dimens.itemSpacing),
                                                color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.2f),
                                                thickness = 0.5.dp
                                            )
                                        }
                                    }
                                }
                            }
                        }
                        item { Spacer(Modifier.height(dimens.sectionSpacing)) }
                    }
                }
            }
        }
    }
}

@Composable
private fun GlowStatCard(
    modifier: Modifier,
    icon: ImageVector,
    label: String,
    value: String,
    gradient: List<Color>,
    dimens: Dimensions
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(dimens.cardRadius),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(0.dp)
    ) {
        Column(modifier = Modifier.padding(dimens.cardPadding)) {
            Box(
                Modifier
                    .size(36.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(Brush.linearGradient(gradient)),
                Alignment.Center
            ) {
                Icon(icon, null, tint = Color.White, modifier = Modifier.size(18.dp))
            }
            Spacer(Modifier.height(dimens.itemSpacing))
            Text(
                value,
                style = MaterialTheme.typography.headlineMedium.copy(fontSize = 28.sp),
                fontWeight = FontWeight.Bold
            )
            Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}
