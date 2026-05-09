package com.example.e_comply.feature.validation

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.e_comply.data.model.Product
import com.example.e_comply.data.model.ProductSource
import com.example.e_comply.feature.login.AuthViewModel
import com.example.e_comply.feature.scanner.ScanState
import com.example.e_comply.feature.scanner.ScanViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ScanResultScreen(
    onBack: () -> Unit,
    onNavigateToReport: (String) -> Unit,
    scanViewModel: ScanViewModel = hiltViewModel(),
    complianceViewModel: ComplianceViewModel = hiltViewModel(),
    authViewModel: AuthViewModel = hiltViewModel()
) {
    val capturedImage by scanViewModel.capturedImage.collectAsState()
    val extractedText by scanViewModel.extractedText.collectAsState()
    val scanState by scanViewModel.scanState.collectAsState()
    val currentUser by authViewModel.currentUser.collectAsState()
    
    var productName by remember { mutableStateOf("") }
    var brandName by remember { mutableStateOf("") }
    var manufacturerName by remember { mutableStateOf("") }
    var manufacturerAddress by remember { mutableStateOf("") }
    var importerName by remember { mutableStateOf("") }
    var importerAddress by remember { mutableStateOf("") }
    var netQuantity by remember { mutableStateOf("") }
    var mrp by remember { mutableStateOf("") }
    var manufacturingDate by remember { mutableStateOf("") }
    var expiryDate by remember { mutableStateOf("") }
    var batchNumber by remember { mutableStateOf("") }
    var customerCare by remember { mutableStateOf("") }
    var countryOfOrigin by remember { mutableStateOf("") }
    var barcode by remember { mutableStateOf("") }
    var licenseNumber by remember { mutableStateOf("") }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Scan Result") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        },
        bottomBar = {
            if (scanState !is ScanState.Extracting && scanState !is ScanState.Saving) {
                BottomAppBar {
                    Button(
                        onClick = {
                            val product = Product(
                                name = productName,
                                brandName = brandName,
                                manufacturerName = manufacturerName,
                                manufacturerAddress = manufacturerAddress,
                                importerName = importerName,
                                importerAddress = importerAddress,
                                netQuantity = netQuantity,
                                mrp = mrp,
                                manufacturingDate = manufacturingDate,
                                expiryDate = expiryDate,
                                batchNumber = batchNumber,
                                customerCareDetails = customerCare,
                                countryOfOrigin = countryOfOrigin,
                                barcode = barcode,
                                licenseNumber = licenseNumber,
                                scannedText = extractedText,
                                source = ProductSource.MOBILE_SCAN,
                                scannedBy = currentUser?.id ?: ""
                            )
                            
                            scanViewModel.saveProduct(product, capturedImage)
                            complianceViewModel.validateCompliance(product, extractedText)
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        enabled = productName.isNotBlank()
                    ) {
                        Icon(Icons.Default.Check, contentDescription = null)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Validate Compliance")
                    }
                }
            }
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp)
                .verticalScroll(rememberScrollState())
        ) {
            if (capturedImage != null) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp)
                ) {
                    Image(
                        bitmap = capturedImage!!.asImageBitmap(),
                        contentDescription = "Captured product",
                        modifier = Modifier.fillMaxSize()
                    )
                }
                Spacer(modifier = Modifier.height(16.dp))
            }
            
            when (scanState) {
                is ScanState.Extracting -> {
                    Box(
                        modifier = Modifier.fillMaxWidth(),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            CircularProgressIndicator()
                            Spacer(modifier = Modifier.height(8.dp))
                            Text("Extracting text from image...")
                        }
                    }
                }
                is ScanState.Saving -> {
                    Box(
                        modifier = Modifier.fillMaxWidth(),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            CircularProgressIndicator()
                            Spacer(modifier = Modifier.height(8.dp))
                            Text("Validating compliance...")
                        }
                    }
                }
                is ScanState.Saved -> {
                    LaunchedEffect(Unit) {
                        // Wait for compliance validation to complete
                        kotlinx.coroutines.delay(1000)
                        val productId = (scanState as ScanState.Saved).productId
                        // Assuming report ID is same as product ID for simplicity
                        onNavigateToReport(productId)
                    }
                }
                is ScanState.Error -> {
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.errorContainer
                        )
                    ) {
                        Text(
                            text = (scanState as ScanState.Error).message,
                            color = MaterialTheme.colorScheme.error,
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            textAlign = TextAlign.Center
                        )
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                }
                else -> {}
            }
            
            if (extractedText.isNotBlank()) {
                Text(
                    text = "Extracted Text",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Card {
                    Text(
                        text = extractedText,
                        modifier = Modifier.padding(12.dp),
                        fontSize = 14.sp
                    )
                }
                Spacer(modifier = Modifier.height(24.dp))
            }
            
            // ── Product Information Section ───────────────────────────────
            Text(
                text = "Product Information",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(12.dp))
            
            OutlinedTextField(
                value = productName,
                onValueChange = { productName = it },
                label = { Text("Product Name *") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(12.dp))

            OutlinedTextField(
                value = brandName,
                onValueChange = { brandName = it },
                label = { Text("Brand Name") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(12.dp))
            
            // ── Manufacturer Details ──────────────────────────────────────
            Text(
                text = "Manufacturer Details",
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(8.dp))

            OutlinedTextField(
                value = manufacturerName,
                onValueChange = { manufacturerName = it },
                label = { Text("Manufacturer Name") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(12.dp))
            
            OutlinedTextField(
                value = manufacturerAddress,
                onValueChange = { manufacturerAddress = it },
                label = { Text("Manufacturer Address") },
                modifier = Modifier.fillMaxWidth(),
                minLines = 2
            )
            Spacer(modifier = Modifier.height(12.dp))

            // ── Importer Details ──────────────────────────────────────────
            Text(
                text = "Importer Details",
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(8.dp))

            OutlinedTextField(
                value = importerName,
                onValueChange = { importerName = it },
                label = { Text("Importer Name") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(12.dp))

            OutlinedTextField(
                value = importerAddress,
                onValueChange = { importerAddress = it },
                label = { Text("Importer Address") },
                modifier = Modifier.fillMaxWidth(),
                minLines = 2
            )
            Spacer(modifier = Modifier.height(12.dp))

            // ── Pricing & Quantity ────────────────────────────────────────
            Text(
                text = "Pricing & Quantity",
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(8.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedTextField(
                    value = netQuantity,
                    onValueChange = { netQuantity = it },
                    label = { Text("Net Quantity") },
                    modifier = Modifier.weight(1f)
                )
                
                OutlinedTextField(
                    value = mrp,
                    onValueChange = { mrp = it },
                    label = { Text("MRP") },
                    modifier = Modifier.weight(1f)
                )
            }
            Spacer(modifier = Modifier.height(12.dp))
            
            // ── Dates ─────────────────────────────────────────────────────
            Text(
                text = "Dates",
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedTextField(
                    value = manufacturingDate,
                    onValueChange = { manufacturingDate = it },
                    label = { Text("Mfg. Date") },
                    modifier = Modifier.weight(1f)
                )
                
                OutlinedTextField(
                    value = expiryDate,
                    onValueChange = { expiryDate = it },
                    label = { Text("Expiry Date") },
                    modifier = Modifier.weight(1f)
                )
            }
            Spacer(modifier = Modifier.height(12.dp))

            // ── Identification ────────────────────────────────────────────
            Text(
                text = "Product Identification",
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(8.dp))

            OutlinedTextField(
                value = batchNumber,
                onValueChange = { batchNumber = it },
                label = { Text("Batch Number") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedTextField(
                    value = barcode,
                    onValueChange = { barcode = it },
                    label = { Text("Barcode / QR Code") },
                    modifier = Modifier.weight(1f)
                )

                OutlinedTextField(
                    value = licenseNumber,
                    onValueChange = { licenseNumber = it },
                    label = { Text("License Number") },
                    modifier = Modifier.weight(1f)
                )
            }
            Spacer(modifier = Modifier.height(12.dp))

            // ── Customer & Origin ─────────────────────────────────────────
            Text(
                text = "Customer & Origin",
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(8.dp))
            
            OutlinedTextField(
                value = customerCare,
                onValueChange = { customerCare = it },
                label = { Text("Customer Care Details") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(12.dp))
            
            OutlinedTextField(
                value = countryOfOrigin,
                onValueChange = { countryOfOrigin = it },
                label = { Text("Country of Origin") },
                modifier = Modifier.fillMaxWidth()
            )
            
            Spacer(modifier = Modifier.height(80.dp))
        }
    }
}
