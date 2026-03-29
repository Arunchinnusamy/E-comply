package com.example.e_comply.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.e_comply.data.model.ComplianceStatus
import com.example.e_comply.data.model.RiskLevel
import com.example.e_comply.ui.viewmodel.ComplianceState
import com.example.e_comply.ui.viewmodel.ComplianceViewModel
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun InspectorDashboardScreen(
    onBack: () -> Unit,
    onReportClick: (String) -> Unit,
    complianceViewModel: ComplianceViewModel = hiltViewModel()
) {
    val complianceState by complianceViewModel.complianceState.collectAsState()
    
    LaunchedEffect(Unit) {
        complianceViewModel.getAllReports()
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Dashboard") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        when (complianceState) {
            is ComplianceState.Loading -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
            
            is ComplianceState.ReportsLoaded -> {
                val reports = (complianceState as ComplianceState.ReportsLoaded).reports
                
                // Calculate statistics
                val totalReports = reports.size
                val compliantCount = reports.count { it.complianceStatus == ComplianceStatus.COMPLIANT }
                val nonCompliantCount = reports.count { it.complianceStatus == ComplianceStatus.NON_COMPLIANT }
                val criticalCount = reports.count { it.riskLevel == RiskLevel.CRITICAL }
                val highRiskCount = reports.count { it.riskLevel == RiskLevel.HIGH }
                
                val averageScore = if (reports.isNotEmpty()) {
                    reports.map { it.complianceScore }.average()
                } else 0.0
                
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues)
                        .padding(16.dp)
                ) {
                    item {
                        Text(
                            text = "Statistics Overview",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(bottom = 16.dp)
                        )
                    }
                    
                    item {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            StatCard(
                                title = "Total Reports",
                                value = totalReports.toString(),
                                icon = Icons.AutoMirrored.Filled.List,
                                modifier = Modifier.weight(1f)
                            )
                            
                            StatCard(
                                title = "Avg. Score",
                                value = "${averageScore.toInt()}%",
                                icon = Icons.Default.Info,
                                modifier = Modifier.weight(1f)
                            )
                        }
                        Spacer(modifier = Modifier.height(12.dp))
                    }
                    
                    item {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            StatCard(
                                title = "Compliant",
                                value = compliantCount.toString(),
                                icon = Icons.Default.CheckCircle,
                                containerColor = MaterialTheme.colorScheme.primaryContainer,
                                modifier = Modifier.weight(1f)
                            )
                            
                            StatCard(
                                title = "Non-Compliant",
                                value = nonCompliantCount.toString(),
                                icon = Icons.Default.Warning,
                                containerColor = MaterialTheme.colorScheme.errorContainer,
                                modifier = Modifier.weight(1f)
                            )
                        }
                        Spacer(modifier = Modifier.height(12.dp))
                    }
                    
                    item {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            StatCard(
                                title = "Critical Risk",
                                value = criticalCount.toString(),
                                icon = Icons.Default.Warning,
                                containerColor = MaterialTheme.colorScheme.errorContainer,
                                modifier = Modifier.weight(1f)
                            )
                            
                            StatCard(
                                title = "High Risk",
                                value = highRiskCount.toString(),
                                icon = Icons.Default.Notifications,
                                containerColor = MaterialTheme.colorScheme.tertiaryContainer,
                                modifier = Modifier.weight(1f)
                            )
                        }
                        Spacer(modifier = Modifier.height(24.dp))
                    }
                    
                    item {
                        Text(
                            text = "Recent Reports",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(bottom = 12.dp)
                        )
                    }
                    
                    items(reports.take(10)) { report ->
                        ReportListItem(
                            productName = report.productName,
                            complianceScore = report.complianceScore,
                            riskLevel = report.riskLevel,
                            timestamp = report.createdAt,
                            onClick = { onReportClick(report.id) }
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                    }
                }
            }
            
            is ComplianceState.Error -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues)
                        .padding(16.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = (complianceState as ComplianceState.Error).message,
                        color = MaterialTheme.colorScheme.error,
                        modifier = Modifier.fillMaxWidth(),
                        textAlign = TextAlign.Center
                    )
                }
            }
            
            else -> {}
        }
    }
}

@Composable
fun StatCard(
    title: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    modifier: Modifier = Modifier,
    containerColor: androidx.compose.ui.graphics.Color = MaterialTheme.colorScheme.surfaceVariant
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = containerColor)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Icon(
                icon,
                contentDescription = null,
                modifier = Modifier.size(32.dp),
                tint = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = value,
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = title,
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
fun ReportListItem(
    productName: String,
    complianceScore: Float,
    riskLevel: RiskLevel,
    timestamp: Long,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = productName.ifBlank { "Unknown Product" },
                    fontSize = 16.sp,
                    fontWeight = FontWeight.SemiBold
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = formatTimestamp(timestamp),
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = "${complianceScore.toInt()}%",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = when {
                        complianceScore >= 90 -> MaterialTheme.colorScheme.primary
                        complianceScore >= 70 -> MaterialTheme.colorScheme.tertiary
                        else -> MaterialTheme.colorScheme.error
                    }
                )
                Surface(
                    shape = MaterialTheme.shapes.small,
                    color = when (riskLevel) {
                        RiskLevel.LOW -> MaterialTheme.colorScheme.primaryContainer
                        RiskLevel.MEDIUM -> MaterialTheme.colorScheme.secondaryContainer
                        RiskLevel.HIGH -> MaterialTheme.colorScheme.tertiaryContainer
                        RiskLevel.CRITICAL -> MaterialTheme.colorScheme.errorContainer
                    }
                ) {
                    Text(
                        text = riskLevel.name,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        }
    }
}

fun formatTimestamp(timestamp: Long): String {
    val sdf = SimpleDateFormat("MMM dd, yyyy HH:mm", Locale.getDefault())
    return sdf.format(Date(timestamp))
}
