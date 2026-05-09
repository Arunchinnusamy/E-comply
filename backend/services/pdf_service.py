"""
pdf_service.py
--------------
Professional PDF report generation for Legal Metrology compliance.

Generates government/inspection-grade PDF reports with:
    - Report Header
    - Product Details
    - Validation Results
    - Compliance Summary
    - Missing Fields
    - AI Remarks
    - Footer

Uses reportlab for PDF generation.
"""

import io
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab not installed — PDF generation disabled")


class PDFService:
    """Generate professional PDF compliance reports."""

    def __init__(self):
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Define custom paragraph styles for the report."""
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Title'],
            fontSize=20,
            spaceAfter=6,
            textColor=colors.HexColor('#1a237e'),
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            name='ReportSubtitle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            textColor=colors.HexColor('#455a64'),
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=13,
            spaceBefore=14,
            spaceAfter=6,
            textColor=colors.HexColor('#1565c0'),
            borderWidth=0,
            borderPadding=0,
        ))
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#616161'),
        ))
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#212121'),
        ))
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#9e9e9e'),
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            name='RemarksText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#37474f'),
            leading=14,
        ))

    def generate_pdf(self, report: dict[str, Any]) -> bytes:
        """
        Generate a professional PDF from a structured compliance report.

        Args:
            report: Structured report dictionary (standard JSON format)

        Returns:
            bytes: PDF file content

        Raises:
            RuntimeError: If reportlab is not installed
        """
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError(
                "reportlab is required for PDF generation. "
                "Install with: pip install reportlab"
            )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        elements: list = []

        # ── Report Header ─────────────────────────────────────────────
        elements.extend(self._build_header(report))

        # ── Product Details ───────────────────────────────────────────
        elements.extend(self._build_product_details(report))

        # ── Manufacturer & Importer Details ───────────────────────────
        elements.extend(self._build_manufacturer_details(report))

        # ── Pricing & Date Details ────────────────────────────────────
        elements.extend(self._build_pricing_date_details(report))

        # ── Product Identification ────────────────────────────────────
        elements.extend(self._build_identification_details(report))

        # ── Validation Results ────────────────────────────────────────
        elements.extend(self._build_validation_results(report))

        # ── Compliance Summary ────────────────────────────────────────
        elements.extend(self._build_compliance_summary(report))

        # ── Missing Fields ────────────────────────────────────────────
        elements.extend(self._build_missing_fields(report))

        # ── AI Remarks ────────────────────────────────────────────────
        elements.extend(self._build_remarks(report))

        # ── Footer ────────────────────────────────────────────────────
        elements.extend(self._build_footer(report))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(
            "PDF generated for report %s (%d bytes)",
            report.get("report_id", "?"),
            len(pdf_bytes),
        )
        return pdf_bytes

    # ──────────────────────────────────────────────────────────────────
    # Section builders
    # ──────────────────────────────────────────────────────────────────

    def _build_header(self, report: dict) -> list:
        """Report Header section."""
        elements = []
        elements.append(Paragraph(
            "LEGAL METROLOGY REPORT",
            self.styles['ReportTitle']
        ))
        elements.append(Paragraph(
            "Automated Compliance Validation — E-Comply System",
            self.styles['ReportSubtitle']
        ))
        elements.append(HRFlowable(
            width="100%", thickness=1.5,
            color=colors.HexColor('#1a237e'),
            spaceAfter=6, spaceBefore=4,
        ))

        # Report metadata
        meta_data = [
            ["Report ID:", report.get("report_id", report.get("reportId", "N/A"))],
            ["Generated Date:", report.get("generated_date", datetime.now().strftime("%d-%m-%Y"))],
        ]
        meta_table = Table(meta_data, colWidths=[100, 380])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#616161')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 12))
        return elements

    def _build_product_details(self, report: dict) -> list:
        """Product Details section."""
        elements = []
        elements.append(Paragraph("Product Details", self.styles['SectionHeader']))

        data = [
            ["Product Name:", report.get("product_name", "N/A")],
            ["Brand Name:", report.get("brand_name", "N/A")],
            ["Category:", report.get("category", "N/A")],
            ["Country of Origin:", report.get("country_of_origin", "N/A")],
        ]
        elements.append(self._make_detail_table(data))
        elements.append(Spacer(1, 8))
        return elements

    def _build_manufacturer_details(self, report: dict) -> list:
        """Manufacturer & Importer Details section."""
        elements = []
        mfg = report.get("manufacturer_details", {})
        imp = report.get("importer_details", {})

        elements.append(Paragraph("Manufacturer Details", self.styles['SectionHeader']))
        data = [
            ["Manufacturer Name:", mfg.get("name", "N/A")],
            ["Manufacturer Address:", mfg.get("address", "N/A")],
        ]
        elements.append(self._make_detail_table(data))

        imp_name = imp.get("name", "")
        if imp_name:
            elements.append(Paragraph("Importer Details", self.styles['SectionHeader']))
            data = [
                ["Importer Name:", imp_name],
                ["Importer Address:", imp.get("address", "N/A")],
            ]
            elements.append(self._make_detail_table(data))
        
        elements.append(Spacer(1, 8))
        return elements

    def _build_pricing_date_details(self, report: dict) -> list:
        """Pricing & Date Details section."""
        elements = []
        pricing = report.get("pricing_details", {})
        dates = report.get("date_details", {})
        cs = report.get("customer_support", {})

        elements.append(Paragraph("Pricing & Date Details", self.styles['SectionHeader']))
        data = [
            ["MRP:", pricing.get("mrp", "N/A")],
            ["Net Quantity:", pricing.get("net_quantity", "N/A")],
            ["Manufacturing Date:", dates.get("manufacturing_date", "N/A")],
            ["Expiry Date:", dates.get("expiry_date", "N/A")],
            ["Customer Care:", cs.get("customer_care", "N/A")],
        ]
        elements.append(self._make_detail_table(data))
        elements.append(Spacer(1, 8))
        return elements

    def _build_identification_details(self, report: dict) -> list:
        """Product Identification section."""
        elements = []
        pid = report.get("product_identification", {})

        elements.append(Paragraph("Product Identification", self.styles['SectionHeader']))
        data = [
            ["Batch Number:", pid.get("batch_number", "N/A")],
            ["Barcode:", pid.get("barcode", "N/A")],
            ["License Number:", pid.get("license_number", "N/A")],
        ]
        elements.append(self._make_detail_table(data))
        elements.append(Spacer(1, 8))
        return elements

    def _build_validation_results(self, report: dict) -> list:
        """Validation Results table section."""
        elements = []
        results = report.get("validation_results", {})
        if not results:
            return elements

        elements.append(Paragraph("Validation Results", self.styles['SectionHeader']))

        table_data = [["Field Analysis", "Status"]]
        for field, status in results.items():
            display_field = field.replace('_', ' ').title()
            table_data.append([display_field, status])

        table = Table(table_data, colWidths=[330, 140])
        style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]

        for row_idx in range(1, len(table_data)):
            status = table_data[row_idx][1].lower()
            if "valid" in status or "present" in status or "yes" in status:
                style_commands.append(('TEXTCOLOR', (1, row_idx), (1, row_idx), colors.darkgreen))
            else:
                style_commands.append(('TEXTCOLOR', (1, row_idx), (1, row_idx), colors.red))

        table.setStyle(TableStyle(style_commands))
        elements.append(table)
        elements.append(Spacer(1, 12))
        return elements

    def _build_compliance_summary(self, report: dict) -> list:
        """Compliance Summary section."""
        elements = []
        
        elements.append(Paragraph("Compliance Summary", self.styles['SectionHeader']))

        score = report.get("compliance_score", "0")
        risk = report.get("risk_level", "UNKNOWN")
        status = report.get("overall_status", report.get("status", "UNKNOWN"))

        risk_color = colors.darkgreen if "LOW" in risk.upper() else colors.orange if "MEDIUM" in risk.upper() else colors.red

        data = [
            ["Compliance Score:", f"{score}%"],
            ["Risk Level:", risk],
            ["Overall Status:", status.upper()],
        ]
        table = Table(data, colWidths=[150, 320])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (1, 0), (1, 0), risk_color),
            ('TEXTCOLOR', (1, 1), (1, 1), risk_color),
            ('TEXTCOLOR', (1, 2), (1, 2), risk_color),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))
        return elements

    def _build_missing_fields(self, report: dict) -> list:
        """Missing Fields section."""
        elements = []
        missing = report.get("missing_fields", [])
        if not missing:
            return elements

        elements.append(Paragraph("Missing Fields", self.styles['SectionHeader']))
        for field in missing:
            elements.append(Paragraph(f"• {field}", self.styles['RemarksText']))
        elements.append(Spacer(1, 8))
        return elements

    def _build_remarks(self, report: dict) -> list:
        """AI Remarks section."""
        elements = []
        remarks = report.get("remarks", "")
        if not remarks:
            return elements

        elements.append(Paragraph("Inspector Remarks", self.styles['SectionHeader']))
        elements.append(Paragraph(remarks, self.styles['RemarksText']))
        elements.append(Spacer(1, 12))
        return elements

    def _build_footer(self, report: dict) -> list:
        """Report Footer."""
        elements = []
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
        elements.append(Paragraph(
            f"Generated by E-Comply AI Validator on {datetime.now().strftime('%d %b %Y at %I:%M %p')}",
            self.styles['Footer']
        ))
        return elements

    # ──────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────

    def _make_detail_table(self, data: list[list[str]]) -> Table:
        """Create a simple label-value detail table."""
        table = Table(data, colWidths=[140, 330])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#616161')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#212121')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        return table
