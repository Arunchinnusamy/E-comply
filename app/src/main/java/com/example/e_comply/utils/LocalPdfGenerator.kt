package com.example.e_comply.utils

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Typeface
import android.graphics.pdf.PdfDocument
import com.example.e_comply.data.model.ComplianceReport
import com.example.e_comply.data.model.RiskLevel
import com.google.zxing.BarcodeFormat
import com.google.zxing.qrcode.QRCodeWriter
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.*

object LocalPdfGenerator {
    fun generate(context: Context, report: ComplianceReport): File? {
        val pdfDocument = PdfDocument()
        
        // Page Configuration (A4 size at 72dpi)
        val pageWidth = 595
        val pageHeight = 842
        val margin = 50f
        val contentWidth = pageWidth - (2 * margin)
        val col1X = margin + 10f
        val col2X = margin + 160f // Fixed tab for values
        
        val pageInfo = PdfDocument.PageInfo.Builder(pageWidth, pageHeight, 1).create()
        val page = pdfDocument.startPage(pageInfo)
        val canvas: Canvas = page.canvas

        // Paints
        val titlePaint = Paint().apply {
            color = Color.parseColor("#1A237E")
            textSize = 22f
            typeface = Typeface.create("sans-serif", Typeface.BOLD)
            textAlign = Paint.Align.CENTER
        }
        val sectionHeaderPaint = Paint().apply {
            color = Color.BLACK
            textSize = 14f
            typeface = Typeface.create("sans-serif", Typeface.BOLD)
        }
        val labelPaint = Paint().apply {
            color = Color.parseColor("#424242")
            textSize = 11f
            typeface = Typeface.create("sans-serif", Typeface.BOLD)
        }
        val valuePaint = Paint().apply {
            color = Color.BLACK
            textSize = 11f
            typeface = Typeface.create("sans-serif", Typeface.NORMAL)
        }
        val dividerPaint = Paint().apply {
            color = Color.LTGRAY
            strokeWidth = 1f
        }
        val statusPaint = Paint().apply {
            textSize = 11f
            typeface = Typeface.create("sans-serif", Typeface.BOLD)
        }

        var currentY = 60f

        // ── 1. HEADER ────────────────────────────────────────────────────────
        canvas.drawText("LEGAL METROLOGY REPORT", (pageWidth / 2).toFloat(), currentY, titlePaint)
        currentY += 15f
        canvas.drawLine(margin, currentY, pageWidth - margin, currentY, dividerPaint)
        currentY += 30f

        // Metadata
        val timestamp = SimpleDateFormat("dd-MM-yyyy", Locale.getDefault()).format(Date())
        drawRow(canvas, "Report ID", ": ${report.id.take(15).uppercase()}", col1X, col2X, currentY, labelPaint, valuePaint)
        currentY += 20f
        drawRow(canvas, "Generated Date", ": $timestamp", col1X, col2X, currentY, labelPaint, valuePaint)
        currentY += 20f
        drawRow(canvas, "Scan Type", ": OCR Product Validation", col1X, col2X, currentY, labelPaint, valuePaint)
        currentY += 35f

        // ── 2. PRODUCT DETAILS ───────────────────────────────────────────────
        canvas.drawLine(margin, currentY, pageWidth - margin, currentY, dividerPaint)
        currentY += 25f
        canvas.drawText("PRODUCT DETAILS", margin, currentY, sectionHeaderPaint)
        currentY += 10f
        canvas.drawLine(margin, currentY, pageWidth - margin, currentY, dividerPaint)
        currentY += 25f

        drawRow(canvas, "Product Name", ": ${report.productName}", col1X, col2X, currentY, labelPaint, valuePaint)
        currentY += 20f
        drawRow(canvas, "Brand Name", ": ${report.brandName}", col1X, col2X, currentY, labelPaint, valuePaint)
        currentY += 20f
        drawRow(canvas, "Category", ": ${report.category}", col1X, col2X, currentY, labelPaint, valuePaint)
        currentY += 35f

        // ── 3. VALIDATION RESULTS ──────────────────────────────────────────
        canvas.drawLine(margin, currentY, pageWidth - margin, currentY, dividerPaint)
        currentY += 25f
        canvas.drawText("VALIDATION RESULTS", margin, currentY, sectionHeaderPaint)
        currentY += 10f
        canvas.drawLine(margin, currentY, pageWidth - margin, currentY, dividerPaint)
        currentY += 25f

        val fields = listOf(
            "MRP" to true,
            "Manufacturer" to report.manufacturerName.isNotBlank(),
            "Net Quantity" to report.netQuantity.isNotBlank(),
            "Expiry Date" to report.expiryDate.isNotBlank(),
            "Batch Number" to report.batchNumber.isNotBlank()
        )

        fields.forEach { (field, isValid) ->
            canvas.drawText(field, col1X, currentY, labelPaint)
            statusPaint.color = if (isValid) Color.parseColor("#2E7D32") else Color.RED
            canvas.drawText(if (isValid) "✔ Valid" else "✘ Missing", col2X, currentY, statusPaint)
            currentY += 20f
        }
        currentY += 15f

        // ── 4. COMPLIANCE SUMMARY ──────────────────────────────────────────
        canvas.drawLine(margin, currentY, pageWidth - margin, currentY, dividerPaint)
        currentY += 25f
        canvas.drawText("COMPLIANCE SUMMARY", margin, currentY, sectionHeaderPaint)
        currentY += 10f
        canvas.drawLine(margin, currentY, pageWidth - margin, currentY, dividerPaint)
        currentY += 25f

        drawRow(canvas, "Compliance Score", ": ${report.complianceScore.toInt()}%", col1X, col2X, currentY, labelPaint, valuePaint)
        currentY += 20f
        
        val riskColor = when (report.riskLevel) {
            RiskLevel.LOW -> Color.parseColor("#2E7D32")
            RiskLevel.MEDIUM -> Color.parseColor("#F57F17")
            else -> Color.RED
        }
        statusPaint.color = riskColor
        canvas.drawText("Risk Level", col1X, currentY, labelPaint)
        canvas.drawText(": ${report.riskLevel.name} RISK", col2X, currentY, statusPaint)
        currentY += 35f

        // ── 5. MISSING FIELDS ──────────────────────────────────────────────
        if (report.missingFields.isNotEmpty()) {
            canvas.drawLine(margin, currentY, pageWidth - margin, currentY, dividerPaint)
            currentY += 25f
            canvas.drawText("MISSING FIELDS", margin, currentY, sectionHeaderPaint)
            currentY += 10f
            canvas.drawLine(margin, currentY, pageWidth - margin, currentY, dividerPaint)
            currentY += 25f

            valuePaint.color = Color.RED
            report.missingFields.forEach { field ->
                canvas.drawText("• $field", col1X, currentY, valuePaint)
                currentY += 18f
            }
            valuePaint.color = Color.BLACK
            currentY += 17f
        }

        // ── 6. AI REMARKS ──────────────────────────────────────────────────
        canvas.drawLine(margin, currentY, pageWidth - margin, currentY, dividerPaint)
        currentY += 25f
        canvas.drawText("AI REMARKS", margin, currentY, sectionHeaderPaint)
        currentY += 10f
        canvas.drawLine(margin, currentY, pageWidth - margin, currentY, dividerPaint)
        currentY += 25f

        val remarks = report.aiSummary
        val words = remarks.split(" ")
        var line = ""
        valuePaint.typeface = Typeface.create("sans-serif", Typeface.ITALIC)
        for (word in words) {
            if (valuePaint.measureText(line + word) > contentWidth - 20f) {
                canvas.drawText(line, col1X, currentY, valuePaint)
                currentY += 18f
                line = "$word "
            } else {
                line += "$word "
            }
        }
        canvas.drawText(line, col1X, currentY, valuePaint)
        currentY += 40f

        // ── 7. FOOTER ──────────────────────────────────────────────────────
        canvas.drawLine(margin, currentY, pageWidth - margin, currentY, dividerPaint)
        currentY += 25f
        titlePaint.textSize = 14f
        titlePaint.color = Color.GRAY
        canvas.drawText("---------------- END OF REPORT ----------------", (pageWidth / 2).toFloat(), currentY, titlePaint)

        pdfDocument.finishPage(page)

        val file = File(context.cacheDir, "ComplianceReport_${report.id}.pdf")
        return try {
            pdfDocument.writeTo(FileOutputStream(file))
            pdfDocument.close()
            file
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    private fun drawRow(canvas: Canvas, label: String, value: String, x1: Float, x2: Float, y: Float, lp: Paint, vp: Paint) {
        canvas.drawText(label, x1, y, lp)
        canvas.drawText(value, x2, y, vp)
    }
}
