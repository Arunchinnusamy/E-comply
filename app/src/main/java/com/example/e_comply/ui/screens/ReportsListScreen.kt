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
import com.example.e_comply.ui.viewmodel.AuthViewModel
import com.example.e_comply.ui.viewmodel.ComplianceState
import com.example.e_comply.ui.viewmodel.ComplianceViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReportsListScreen(
    onBack: () -> Unit,
    onReportClick: (String) -> Unit,
    complianceViewModel: ComplianceViewModel = hiltViewModel(),
    authViewModel: AuthViewModel = hiltViewModel()
) {
    val complianceState by complianceViewModel.complianceState.collectAsState()
    val currentUser by authViewModel.currentUser.collectAsState()
    
    var selectedFilter by remember { mutableStateOf<FilterType>(FilterType.ALL) }
    var showFilterMenu by remember { mutableStateOf(false) }
    
    LaunchedEffect(selectedFilter, currentUser) {
        currentUser?.let { user ->
            when (selectedFilter) {
                FilterType.ALL -> complianceViewModel.getAllReports()
                FilterType.COMPLIANT -> complianceViewModel.filterReportsByStatus(ComplianceStatus.COMPLIANT)
                FilterType.NON_COMPLIANT -> complianceViewModel.filterReportsByStatus(ComplianceStatus.NON_COMPLIANT)
                FilterType.HIGH_RISK -> complianceViewModel.filterReportsByRisk(RiskLevel.HIGH)
                FilterType.CRITICAL -> complianceViewModel.filterReportsByRisk(RiskLevel.CRITICAL)
            }
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Compliance Reports") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { showFilterMenu = true }) {
                        Icon(Icons.AutoMirrored.Filled.List, contentDescription = "Filter")
                    }
                    DropdownMenu(
                        expanded = showFilterMenu,
                        onDismissRequest = { showFilterMenu = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("All Reports") },
                            onClick = {
                                selectedFilter = FilterType.ALL
                                showFilterMenu = false
                            },
                            leadingIcon = { Icon(Icons.AutoMirrored.Filled.List, null) }
                        )
                        DropdownMenuItem(
                            text = { Text("Compliant") },
                            onClick = {
                                selectedFilter = FilterType.COMPLIANT
                                showFilterMenu = false
                            },
                            leadingIcon = { Icon(Icons.Default.CheckCircle, null) }
                        )
                        DropdownMenuItem(
                            text = { Text("Non-Compliant") },
                            onClick = {
                                selectedFilter = FilterType.NON_COMPLIANT
                                showFilterMenu = false
                            },
                            leadingIcon = { Icon(Icons.Default.Warning, null) }
                        )
                        DropdownMenuItem(
                            text = { Text("High Risk") },
                            onClick = {
                                selectedFilter = FilterType.HIGH_RISK
                                showFilterMenu = false
                            },
                            leadingIcon = { Icon(Icons.Default.Warning, null) }
                        )
                        DropdownMenuItem(
                            text = { Text("Critical") },
                            onClick = {
                                selectedFilter = FilterType.CRITICAL
                                showFilterMenu = false
                            },
                            leadingIcon = { Icon(Icons.Default.Notifications, null) }
                        )
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
                
                if (reports.isEmpty()) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(paddingValues),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                Icons.Default.Info,
                                contentDescription = null,
                                modifier = Modifier.size(64.dp),
                                tint = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                text = "No reports found",
                                fontSize = 18.sp,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                } else {
                    LazyColumn(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(paddingValues)
                            .padding(horizontal = 16.dp)
                    ) {
                        item {
                            Spacer(modifier = Modifier.height(8.dp))
                            Card(
                                colors = CardDefaults.cardColors(
                                    containerColor = MaterialTheme.colorScheme.primaryContainer
                                )
                            ) {
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(12.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        Icons.Default.Info,
                                        contentDescription = null,
                                        modifier = Modifier.size(20.dp)
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = "Found ${reports.size} report(s)",
                                        fontSize = 14.sp,
                                        fontWeight = FontWeight.Medium
                                    )
                                }
                            }
                            Spacer(modifier = Modifier.height(12.dp))
                        }
                        
                        items(reports) { report ->
                            ReportListItem(
                                productName = report.productName,
                                complianceScore = report.complianceScore,
                                riskLevel = report.riskLevel,
                                timestamp = report.createdAt,
                                onClick = { onReportClick(report.id) }
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                        }
                        
                        item {
                            Spacer(modifier = Modifier.height(8.dp))
                        }
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
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(
                            Icons.Default.Warning,
                            contentDescription = null,
                            modifier = Modifier.size(64.dp),
                            tint = MaterialTheme.colorScheme.error
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = (complianceState as ComplianceState.Error).message,
                            color = MaterialTheme.colorScheme.error,
                            textAlign = TextAlign.Center
                        )
                    }
                }
            }
            
            else -> {}
        }
    }
}

enum class FilterType {
    ALL, COMPLIANT, NON_COMPLIANT, HIGH_RISK, CRITICAL
}
