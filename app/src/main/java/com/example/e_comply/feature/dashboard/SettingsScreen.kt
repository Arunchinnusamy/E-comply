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
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ExitToApp
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
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.e_comply.data.model.UserType
import com.example.e_comply.ui.theme.*
import com.example.e_comply.ui.viewmodel.AuthViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    onBack: () -> Unit,
    onLogout: () -> Unit,
    authViewModel: AuthViewModel = hiltViewModel()
) {
    val currentUser by authViewModel.currentUser.collectAsState()
    val dimens = rememberDimensions()
    var showLogoutDialog by remember { mutableStateOf(false) }
    var darkModeEnabled by remember { mutableStateOf(false) }
    var notificationsEnabled by remember { mutableStateOf(true) }
    var contentVisible by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) { contentVisible = true }

    if (showLogoutDialog) {
        AlertDialog(
            onDismissRequest = { showLogoutDialog = false },
            icon = {
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(CircleShape)
                        .background(DangerRedLight),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        Icons.AutoMirrored.Filled.ExitToApp,
                        contentDescription = null,
                        tint = DangerRed,
                        modifier = Modifier.size(24.dp)
                    )
                }
            },
            title = { Text("Sign Out", fontWeight = FontWeight.Bold) },
            text = { Text("You'll need to log in again to access your reports.") },
            confirmButton = {
                Button(
                    onClick = {
                        showLogoutDialog = false
                        authViewModel.signOut()
                        onLogout()
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = DangerRed),
                    shape = RoundedCornerShape(dimens.cardRadius - 4.dp)
                ) { Text("Sign Out") }
            },
            dismissButton = {
                OutlinedButton(
                    onClick = { showLogoutDialog = false },
                    shape = RoundedCornerShape(dimens.cardRadius - 4.dp)
                ) { Text("Cancel") }
            },
            shape = RoundedCornerShape(dimens.cardRadius + 4.dp)
        )
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Settings", fontWeight = FontWeight.Bold) },
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
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(paddingValues)
                    .padding(horizontal = dimens.screenPaddingH)
            ) {
                // ── Profile Card ─────────────────────────────────────
                Card(
                    shape = RoundedCornerShape(dimens.cardRadius),
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = dimens.screenPaddingV)
                ) {
                    Column(
                        modifier = Modifier
                            .background(
                                Brush.linearGradient(
                                    colors = listOf(GradientStart, GradientMid)
                                )
                            )
                            .padding(dimens.cardPadding + 4.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Box(
                            modifier = Modifier
                                .size(dimens.avatarSize)
                                .clip(CircleShape)
                                .background(Color.White.copy(alpha = 0.2f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = currentUser?.name?.firstOrNull()?.uppercase() ?: "U",
                                style = MaterialTheme.typography.headlineMedium,
                                color = Color.White,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        Spacer(modifier = Modifier.height(dimens.itemSpacing))
                        Text(
                            text = currentUser?.name ?: "User",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                        Text(
                            text = currentUser?.email ?: "",
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color.White.copy(alpha = 0.7f)
                        )
                        Spacer(modifier = Modifier.height(dimens.itemSpacing))
                        val isInspector = currentUser?.userType == UserType.INSPECTOR
                        Surface(
                            shape = RoundedCornerShape(dimens.chipHeight),
                            color = Color.White.copy(alpha = 0.2f)
                        ) {
                            Text(
                                text = if (isInspector) "🔍 Inspector" else "👤 User",
                                modifier = Modifier.padding(
                                    horizontal = dimens.cardPadding,
                                    vertical = 4.dp
                                ),
                                style = MaterialTheme.typography.labelMedium,
                                color = Color.White
                            )
                        }
                        if (isInspector && !currentUser?.inspectorId.isNullOrBlank()) {
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "ID: ${currentUser?.inspectorId}",
                                style = MaterialTheme.typography.labelSmall,
                                color = Color.White.copy(alpha = 0.5f)
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(dimens.sectionSpacing))

                // ── Preferences ──────────────────────────────────────
                SectionTitle("Preferences")
                Card(
                    shape = RoundedCornerShape(dimens.cardRadius),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                    elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
                ) {
                    ToggleItem(
                        icon = Icons.Outlined.DarkMode,
                        title = "Dark Mode",
                        subtitle = "Use dark theme",
                        checked = darkModeEnabled,
                        onCheckedChange = { darkModeEnabled = it },
                        dimens = dimens
                    )
                    ThinDivider(dimens)
                    ToggleItem(
                        icon = Icons.Outlined.Notifications,
                        title = "Notifications",
                        subtitle = "Compliance alerts",
                        checked = notificationsEnabled,
                        onCheckedChange = { notificationsEnabled = it },
                        dimens = dimens
                    )
                }

                Spacer(modifier = Modifier.height(dimens.sectionSpacing))

                // ── About ────────────────────────────────────────────
                SectionTitle("About")
                Card(
                    shape = RoundedCornerShape(dimens.cardRadius),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                    elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
                ) {
                    InfoRow(Icons.Outlined.Info, "Version", "1.0.0", dimens)
                    ThinDivider(dimens)
                    InfoRow(Icons.Outlined.Gavel, "Framework", "LM Rules 2011", dimens)
                    ThinDivider(dimens)
                    InfoRow(Icons.Outlined.Policy, "Privacy", "", dimens)
                    ThinDivider(dimens)
                    InfoRow(Icons.Outlined.Description, "Terms", "", dimens)
                }

                Spacer(modifier = Modifier.height(dimens.sectionSpacing))

                // ── Logout ───────────────────────────────────────────
                OutlinedButton(
                    onClick = { showLogoutDialog = true },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(dimens.buttonHeight),
                    shape = RoundedCornerShape(dimens.cardRadius),
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = DangerRed),
                    border = androidx.compose.foundation.BorderStroke(1.dp, DangerRed.copy(alpha = 0.4f))
                ) {
                    Icon(
                        Icons.AutoMirrored.Filled.ExitToApp,
                        contentDescription = null,
                        modifier = Modifier.size(dimens.iconSize - 4.dp)
                    )
                    Spacer(modifier = Modifier.width(dimens.itemSpacing))
                    Text("Sign Out", fontWeight = FontWeight.SemiBold)
                }

                Spacer(modifier = Modifier.height(dimens.sectionSpacing * 2))
            }
        }
    }
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

@Composable
private fun SectionTitle(text: String) {
    val dimens = rememberDimensions()
    Text(
        text = text,
        style = MaterialTheme.typography.titleMedium,
        fontWeight = FontWeight.SemiBold,
        modifier = Modifier.padding(bottom = dimens.itemSpacing)
    )
}

@Composable
private fun ThinDivider(dimens: Dimensions) {
    HorizontalDivider(
        modifier = Modifier.padding(horizontal = dimens.cardPadding),
        color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.3f),
        thickness = 0.5.dp
    )
}

@Composable
private fun ToggleItem(
    icon: ImageVector,
    title: String,
    subtitle: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
    dimens: Dimensions
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = dimens.cardPadding, vertical = dimens.itemSpacing),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(dimens.iconSize))
        Spacer(modifier = Modifier.width(dimens.itemSpacing + 2.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(title, style = MaterialTheme.typography.bodyLarge)
            Text(subtitle, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        Switch(checked = checked, onCheckedChange = onCheckedChange)
    }
}

@Composable
private fun InfoRow(
    icon: ImageVector,
    title: String,
    value: String,
    dimens: Dimensions
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = dimens.cardPadding, vertical = dimens.itemSpacing + 2.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(dimens.iconSize))
        Spacer(modifier = Modifier.width(dimens.itemSpacing + 2.dp))
        Text(title, style = MaterialTheme.typography.bodyLarge, modifier = Modifier.weight(1f))
        if (value.isNotEmpty()) {
            Text(value, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
        Icon(
            Icons.Outlined.ChevronRight, null,
            tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.35f),
            modifier = Modifier.size(18.dp)
        )
    }
}
