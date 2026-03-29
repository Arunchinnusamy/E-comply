package com.example.e_comply.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
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
import com.example.e_comply.data.model.*
import com.example.e_comply.ui.viewmodel.ComplianceState
import com.example.e_comply.ui.viewmodel.ComplianceViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ComplianceReportScreen(
    reportId: String,
    onBack: () -> Unit,
    complianceViewModel: ComplianceViewModel = hiltViewModel()
) {
    val complianceState by complianceViewModel.complianceState.collectAsState()
    val currentReport by complianceViewModel.currentReport.collectAsState()
    
    LaunchedEffect(reportId) {
        if (reportId.isNotBlank()) {
            complianceViewModel.getReport(reportId)
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Compliance Report") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        when {
            complianceState is ComplianceState.Loading || complianceState is ComplianceState.Validating -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }

            complianceState is ComplianceState.Error -> {
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
            
            currentReport != null -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues)
                        .padding(16.dp)
                        .verticalScroll(rememberScrollState())
                ) {
                    val report = currentReport!!
                    
                    // Compliance Score Card
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = when (report.riskLevel) {
                                RiskLevel.LOW -> MaterialTheme.colorScheme.primaryContainer
                                RiskLevel.MEDIUM -> MaterialTheme.colorScheme.secondaryContainer
                                RiskLevel.HIGH -> MaterialTheme.colorScheme.tertiaryContainer
                                RiskLevel.CRITICAL -> MaterialTheme.colorScheme.errorContainer
                            }
                        )
                    ) {
                        Column(
                            modifier = Modifier.padding(20.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text(
                                text = "Compliance Score",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Medium
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "${report.complianceScore.toInt()}%",
                                fontSize = 48.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Chip(
                                label = report.complianceStatus.name.replace("_", " ")
                            )
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Risk Level Card
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                when (report.riskLevel) {
                                    RiskLevel.LOW -> Icons.Default.CheckCircle
                                    RiskLevel.MEDIUM -> Icons.Default.Warning
                                    RiskLevel.HIGH, RiskLevel.CRITICAL -> Icons.Default.Warning
                                },
                                contentDescription = null,
                                tint = when (report.riskLevel) {
                                    RiskLevel.LOW -> MaterialTheme.colorScheme.primary
                                    RiskLevel.MEDIUM -> MaterialTheme.colorScheme.secondary
                                    RiskLevel.HIGH, RiskLevel.CRITICAL -> MaterialTheme.colorScheme.error
                                },
                                modifier = Modifier.size(32.dp)
                            )
                            Spacer(modifier = Modifier.width(12.dp))
                            Column {
                                Text(
                                    text = "Risk Level",
                                    fontSize = 14.sp,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                                Text(
                                    text = report.riskLevel.name,
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.SemiBold
                                )
                            }
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(20.dp))
                    
                    // AI Summary
                    if (report.aiSummary.isNotBlank()) {
                        Text(
                            text = "AI Summary",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Card(
                            colors = CardDefaults.cardColors(
                                containerColor = MaterialTheme.colorScheme.surfaceVariant
                            )
                        ) {
                            Text(
                                text = report.aiSummary,
                                modifier = Modifier.padding(16.dp),
                                fontSize = 14.sp,
                                lineHeight = 20.sp
                            )
                        }
                        Spacer(modifier = Modifier.height(16.dp))
                    }
                    
                    // Missing Fields
                    if (report.missingFields.isNotEmpty()) {
                        Text(
                            text = "Missing Fields (${report.missingFields.size})",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Card {
                            Column(modifier = Modifier.padding(16.dp)) {
                                report.missingFields.forEach { field ->
                                    Row(
                                        modifier = Modifier.padding(vertical = 4.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Icon(
                                            Icons.Default.Close,
                                            contentDescription = null,
                                            tint = MaterialTheme.colorScheme.error,
                                            modifier = Modifier.size(20.dp)
                                        )
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(field, fontSize = 14.sp)
                                    }
                                }
                            }
                        }
                        Spacer(modifier = Modifier.height(16.dp))
                    }
                    
                    // Violations
                    if (report.violations.isNotEmpty()) {
                        Text(
                            text = "Violations (${report.violations.size})",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        report.violations.forEach { violation ->
                            ViolationCard(violation)
                            Spacer(modifier = Modifier.height(8.dp))
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                    }
                    
                    // Recommendations
                    if (report.recommendations.isNotEmpty()) {
                        Text(
                            text = "Recommendations",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Card {
                            Column(modifier = Modifier.padding(16.dp)) {
                                report.recommendations.forEachIndexed { index, recommendation ->
                                    Row(
                                        modifier = Modifier.padding(vertical = 4.dp)
                                    ) {
                                        Text(
                                            text = "${index + 1}. ",
                                            fontWeight = FontWeight.SemiBold
                                        )
                                        Text(
                                            text = recommendation,
                                            fontSize = 14.sp,
                                            lineHeight = 20.sp
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            else -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues),
                    contentAlignment = Alignment.Center
                ) {
                    Text("No report available")
                }
            }
        }
    }
}

@Composable
fun ViolationCard(violation: Violation) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = when (violation.severity) {
                Severity.LOW -> MaterialTheme.colorScheme.surfaceVariant
                Severity.MEDIUM -> MaterialTheme.colorScheme.secondaryContainer
                Severity.HIGH, Severity.CRITICAL -> MaterialTheme.colorScheme.errorContainer
            }
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = violation.field,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.SemiBold
                )
                Chip(label = violation.severity.name)
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = violation.description,
                fontSize = 14.sp,
                lineHeight = 18.sp
            )
            if (violation.ruleViolated.isNotBlank()) {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Rule: ${violation.ruleViolated}",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
fun Chip(label: String) {
    Surface(
        shape = MaterialTheme.shapes.small,
        color = MaterialTheme.colorScheme.primary
    ) {
        Text(
            text = label,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            fontSize = 12.sp,
            fontWeight = FontWeight.Medium,
            color = MaterialTheme.colorScheme.onPrimary
        )
    }
}
