"""
firestore_service.py
--------------------
Centralised Firestore helper covering all six collections:

    users/          — user profiles (general users & inspectors)
    products/       — scanned / crawled product records
    reports/        — compliance analysis reports
    violations/     — individual violation records (linked to reports)
    rules/          — Legal Metrology rule definitions
    categories/     — product category definitions & field requirements

Every other service imports this single, already-initialised client.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

import firebase_admin
from firebase_admin import firestore

logger = logging.getLogger(__name__)


class FirestoreService:
    """Full-featured Firestore wrapper for E-Comply."""

    # ══════════════════════════════════════════════════════════════════════
    # Collection names
    # ══════════════════════════════════════════════════════════════════════
    USERS_COLLECTION        = "users"
    PRODUCTS_COLLECTION     = "products"
    REPORTS_COLLECTION      = "reports"
    VIOLATIONS_COLLECTION   = "violations"
    RULES_COLLECTION        = "rules"
    CATEGORIES_COLLECTION   = "categories"

    # Legacy names kept for backward compatibility
    IOT_DEVICES_COLLECTION  = "iot_devices"
    IOT_LOGS_COLLECTION     = "iot_logs"

    def __init__(self):
        # firebase_admin must already be initialised (done in app.py)
        self.db = firestore.client()
        logger.info("FirestoreService initialised — 6 collections ready")

    # ══════════════════════════════════════════════════════════════════════
    # Generic CRUD helpers
    # ══════════════════════════════════════════════════════════════════════

    def _now_ms(self) -> int:
        """Current epoch in milliseconds."""
        return int(datetime.now().timestamp() * 1000)

    def save_document(self, collection: str, doc_id: str, data: dict) -> bool:
        """Create or overwrite a document."""
        try:
            data["updatedAt"] = self._now_ms()
            self.db.collection(collection).document(doc_id).set(data)
            return True
        except Exception as e:
            logger.error(f"save_document failed [{collection}/{doc_id}]: {e}")
            return False

    def get_document(self, collection: str, doc_id: str) -> dict | None:
        """Return a document dict or None if not found."""
        try:
            doc = self.db.collection(collection).document(doc_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error(f"get_document failed [{collection}/{doc_id}]: {e}")
            return None

    def update_document(self, collection: str, doc_id: str, data: dict) -> bool:
        """Merge-update specific fields."""
        try:
            data["updatedAt"] = self._now_ms()
            self.db.collection(collection).document(doc_id).update(data)
            return True
        except Exception as e:
            logger.error(f"update_document failed [{collection}/{doc_id}]: {e}")
            return False

    def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document."""
        try:
            self.db.collection(collection).document(doc_id).delete()
            return True
        except Exception as e:
            logger.error(f"delete_document failed [{collection}/{doc_id}]: {e}")
            return False

    def query_collection(
        self,
        collection: str,
        filters: list[tuple] | None = None,
        order_by: str | None = None,
        direction: str = "DESCENDING",
        limit: int | None = None,
    ) -> list[dict]:
        """
        Query a collection with optional filters.

        ``filters`` is a list of (field, operator, value) tuples, e.g.:
            [("userId", "==", "abc123"), ("riskLevel", "==", "HIGH")]
        """
        try:
            ref = self.db.collection(collection)
            if filters:
                for field, op, value in filters:
                    ref = ref.where(field, op, value)
            if order_by:
                dir_enum = (
                    firestore.Query.ASCENDING
                    if direction == "ASCENDING"
                    else firestore.Query.DESCENDING
                )
                ref = ref.order_by(order_by, direction=dir_enum)
            if limit:
                ref = ref.limit(limit)

            return [doc.to_dict() for doc in ref.stream()]
        except Exception as e:
            logger.error(f"query_collection failed [{collection}]: {e}")
            return []

    def count_collection(self, collection: str, filters: list[tuple] | None = None) -> int:
        """Count documents in a collection with optional filters."""
        try:
            ref = self.db.collection(collection)
            if filters:
                for field, op, value in filters:
                    ref = ref.where(field, op, value)
            return len(list(ref.stream()))
        except Exception as e:
            logger.error(f"count_collection failed [{collection}]: {e}")
            return 0

    def batch_write(self, operations: list[dict]) -> bool:
        """
        Perform batch writes.

        Each operation dict should have:
            {"action": "set"|"update"|"delete", "collection": str,
             "doc_id": str, "data": dict (optional for delete)}
        """
        try:
            batch = self.db.batch()
            for op in operations:
                ref = self.db.collection(op["collection"]).document(op["doc_id"])
                action = op["action"]
                if action == "set":
                    op_data = op.get("data", {})
                    op_data["updatedAt"] = self._now_ms()
                    batch.set(ref, op_data)
                elif action == "update":
                    op_data = op.get("data", {})
                    op_data["updatedAt"] = self._now_ms()
                    batch.update(ref, op_data)
                elif action == "delete":
                    batch.delete(ref)
            batch.commit()
            logger.info(f"Batch write committed: {len(operations)} operations")
            return True
        except Exception as e:
            logger.error(f"batch_write failed: {e}")
            return False

    # ══════════════════════════════════════════════════════════════════════
    # 1. USERS COLLECTION
    # ══════════════════════════════════════════════════════════════════════
    # Document ID = Firebase Auth UID
    # Schema:
    #   uid, email, displayName, userType (GENERAL_USER | INSPECTOR),
    #   phone, inspectorId, profileImageUrl,
    #   totalScans, totalReports, createdAt, updatedAt

    def save_user(self, user: dict) -> bool:
        """Create or update a user profile."""
        uid = user.get("uid") or user.get("id")
        if not uid:
            logger.error("save_user: uid is required")
            return False
        if "createdAt" not in user:
            user["createdAt"] = self._now_ms()
        return self.save_document(self.USERS_COLLECTION, uid, user)

    def get_user(self, uid: str) -> dict | None:
        return self.get_document(self.USERS_COLLECTION, uid)

    def update_user(self, uid: str, data: dict) -> bool:
        return self.update_document(self.USERS_COLLECTION, uid, data)

    def get_inspectors(self) -> list[dict]:
        return self.query_collection(
            self.USERS_COLLECTION,
            filters=[("userType", "==", "INSPECTOR")],
        )

    def increment_user_scans(self, uid: str) -> bool:
        """Atomically increment the user's totalScans counter."""
        try:
            ref = self.db.collection(self.USERS_COLLECTION).document(uid)
            ref.update({
                "totalScans": firestore.Increment(1),
                "updatedAt": self._now_ms(),
            })
            return True
        except Exception as e:
            logger.error(f"increment_user_scans failed [{uid}]: {e}")
            return False

    # ══════════════════════════════════════════════════════════════════════
    # 2. PRODUCTS COLLECTION
    # ══════════════════════════════════════════════════════════════════════
    # Document ID = auto-generated UUID
    # Schema:
    #   productId, name, brandName, category,
    #   manufacturerName, manufacturerAddress,
    #   importerName, importerAddress,
    #   netQuantity, mrp, manufacturingDate, expiryDate,
    #   customerCareDetails, countryOfOrigin,
    #   batchNumber, barcode, licenseNumber, fssaiLicense,
    #   imageUrl, scannedText,
    #   source (MOBILE_SCAN | ECOMMERCE | IOT_DEVICE | WEB_CRAWLER),
    #   sourceUrl, scannedBy (uid), scannedAt,
    #   complianceStatus, reportId,
    #   createdAt, updatedAt

    def save_product(self, product: dict) -> str | None:
        """Save a product and return the product ID."""
        try:
            product_id = product.get("productId") or f"PRD-{uuid.uuid4().hex[:12].upper()}"
            product["productId"] = product_id
            if "createdAt" not in product:
                product["createdAt"] = self._now_ms()
            self.save_document(self.PRODUCTS_COLLECTION, product_id, product)
            return product_id
        except Exception as e:
            logger.error(f"save_product failed: {e}")
            return None

    def get_product(self, product_id: str) -> dict | None:
        return self.get_document(self.PRODUCTS_COLLECTION, product_id)

    def update_product(self, product_id: str, data: dict) -> bool:
        return self.update_document(self.PRODUCTS_COLLECTION, product_id, data)

    def get_user_products(self, uid: str) -> list[dict]:
        return self.query_collection(
            self.PRODUCTS_COLLECTION,
            filters=[("scannedBy", "==", uid)],
            order_by="createdAt",
        )

    def get_products_by_category(self, category: str) -> list[dict]:
        return self.query_collection(
            self.PRODUCTS_COLLECTION,
            filters=[("category", "==", category)],
            order_by="createdAt",
        )

    def get_products_by_status(self, status: str) -> list[dict]:
        return self.query_collection(
            self.PRODUCTS_COLLECTION,
            filters=[("complianceStatus", "==", status)],
            order_by="createdAt",
        )

    def search_products(self, name: str, limit: int = 20) -> list[dict]:
        """Simple prefix search on product name."""
        return self.query_collection(
            self.PRODUCTS_COLLECTION,
            filters=[
                ("name", ">=", name),
                ("name", "<=", name + "\uf8ff"),
            ],
            limit=limit,
        )

    # ══════════════════════════════════════════════════════════════════════
    # 3. REPORTS COLLECTION
    # ══════════════════════════════════════════════════════════════════════
    # Document ID = report_id (RPT-XXXXXXXX)
    # Schema:
    #   reportId, productId, productName, userId,
    #   complianceScore, complianceStatus, riskLevel,
    #   isCompliant, missingFields[], violations[],
    #   validationResults[], recommendations[],
    #   category, brandName, remarks, aiSummary,
    #   dataSource (MOBILE | ECOMMERCE | IOT | CRAWLER),
    #   sourceUrl, inspectorId, inspectorNotes,
    #   pdfUrl, createdAt, updatedAt

    def save_report(self, report: dict) -> bool:
        report_id = (
            report.get("report_id")
            or report.get("reportId")
            or report.get("id")
        )
        if not report_id:
            report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
            report["reportId"] = report_id
        return self.save_document(self.REPORTS_COLLECTION, report_id, report)

    def get_report(self, report_id: str) -> dict | None:
        return self.get_document(self.REPORTS_COLLECTION, report_id)

    def get_user_reports(self, user_id: str) -> list[dict]:
        return self.query_collection(
            self.REPORTS_COLLECTION,
            filters=[("userId", "==", user_id)],
            order_by="createdAt",
        )

    def get_inspector_reports(
        self,
        status: str | None = None,
        risk_level: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        filters = []
        if status:
            filters.append(("complianceStatus", "==", status))
        if risk_level:
            filters.append(("riskLevel", "==", risk_level))
        return self.query_collection(
            self.REPORTS_COLLECTION,
            filters=filters or None,
            order_by="createdAt",
            limit=limit,
        )

    def get_reports_by_product(self, product_id: str) -> list[dict]:
        return self.query_collection(
            self.REPORTS_COLLECTION,
            filters=[("productId", "==", product_id)],
            order_by="createdAt",
        )

    def get_reports_by_risk(self, risk_level: str) -> list[dict]:
        return self.query_collection(
            self.REPORTS_COLLECTION,
            filters=[("riskLevel", "==", risk_level)],
            order_by="createdAt",
        )

    # ══════════════════════════════════════════════════════════════════════
    # 4. VIOLATIONS COLLECTION
    # ══════════════════════════════════════════════════════════════════════
    # Document ID = auto-generated UUID
    # Schema:
    #   violationId, reportId, productId, productName,
    #   field, description, severity (LOW | MEDIUM | HIGH | CRITICAL),
    #   ruleViolated, ruleId (FK to rules/),
    #   category, status (OPEN | RESOLVED | APPEALED),
    #   resolvedAt, resolvedBy, inspectorNotes,
    #   createdAt, updatedAt

    def save_violation(self, violation: dict) -> str | None:
        """Save a violation record and return the violation ID."""
        try:
            vid = violation.get("violationId") or f"VIO-{uuid.uuid4().hex[:10].upper()}"
            violation["violationId"] = vid
            if "status" not in violation:
                violation["status"] = "OPEN"
            if "createdAt" not in violation:
                violation["createdAt"] = self._now_ms()
            self.save_document(self.VIOLATIONS_COLLECTION, vid, violation)
            return vid
        except Exception as e:
            logger.error(f"save_violation failed: {e}")
            return None

    def save_violations_from_report(self, report: dict) -> list[str]:
        """
        Extract violations from a compliance report and save each
        as an individual document in the violations collection.
        Returns list of violation IDs created.
        """
        violations_list = report.get("violations", [])
        report_id = report.get("report_id") or report.get("reportId") or report.get("id", "")
        product_id = report.get("productId", "")
        product_name = report.get("productName", report.get("product_details", {}).get("product_name", ""))
        category = report.get("category", report.get("product_details", {}).get("category", ""))

        created_ids = []
        for v in violations_list:
            violation = {
                "reportId": report_id,
                "productId": product_id,
                "productName": product_name,
                "field": v.get("field", ""),
                "description": v.get("description", ""),
                "severity": v.get("severity", "MEDIUM"),
                "ruleViolated": v.get("ruleViolated") or v.get("rule_violated", ""),
                "category": category,
                "status": "OPEN",
            }
            vid = self.save_violation(violation)
            if vid:
                created_ids.append(vid)

        logger.info(f"Saved {len(created_ids)} violations for report {report_id}")
        return created_ids

    def get_violation(self, violation_id: str) -> dict | None:
        return self.get_document(self.VIOLATIONS_COLLECTION, violation_id)

    def get_violations_by_report(self, report_id: str) -> list[dict]:
        return self.query_collection(
            self.VIOLATIONS_COLLECTION,
            filters=[("reportId", "==", report_id)],
            order_by="createdAt",
        )

    def get_violations_by_severity(self, severity: str) -> list[dict]:
        return self.query_collection(
            self.VIOLATIONS_COLLECTION,
            filters=[("severity", "==", severity)],
            order_by="createdAt",
        )

    def get_open_violations(self, limit: int = 50) -> list[dict]:
        return self.query_collection(
            self.VIOLATIONS_COLLECTION,
            filters=[("status", "==", "OPEN")],
            order_by="createdAt",
            limit=limit,
        )

    def resolve_violation(self, violation_id: str, resolved_by: str, notes: str = "") -> bool:
        return self.update_document(self.VIOLATIONS_COLLECTION, violation_id, {
            "status": "RESOLVED",
            "resolvedAt": self._now_ms(),
            "resolvedBy": resolved_by,
            "inspectorNotes": notes,
        })

    # ══════════════════════════════════════════════════════════════════════
    # 5. RULES COLLECTION
    # ══════════════════════════════════════════════════════════════════════
    # Document ID = rule slug (e.g., "rule_mrp")
    # Schema:
    #   ruleId, fieldName, section, description,
    #   isMandatory, applicableCategories[],
    #   validationPattern, errorMessage,
    #   severity (default severity for violations of this rule),
    #   penaltyInfo, isActive, createdAt, updatedAt

    def save_rule(self, rule: dict) -> bool:
        rule_id = rule.get("ruleId")
        if not rule_id:
            logger.error("save_rule: ruleId is required")
            return False
        if "createdAt" not in rule:
            rule["createdAt"] = self._now_ms()
        return self.save_document(self.RULES_COLLECTION, rule_id, rule)

    def get_rule(self, rule_id: str) -> dict | None:
        return self.get_document(self.RULES_COLLECTION, rule_id)

    def get_all_rules(self) -> list[dict]:
        return self.query_collection(
            self.RULES_COLLECTION,
            order_by="section",
            direction="ASCENDING",
        )

    def get_active_rules(self) -> list[dict]:
        return self.query_collection(
            self.RULES_COLLECTION,
            filters=[("isActive", "==", True)],
            order_by="section",
            direction="ASCENDING",
        )

    def get_rules_by_category(self, category: str) -> list[dict]:
        """Get rules applicable to a specific product category."""
        return self.query_collection(
            self.RULES_COLLECTION,
            filters=[("applicableCategories", "array_contains", category)],
        )

    # ══════════════════════════════════════════════════════════════════════
    # 6. CATEGORIES COLLECTION
    # ══════════════════════════════════════════════════════════════════════
    # Document ID = category slug (e.g., "food", "cosmetics")
    # Schema:
    #   categoryId, name, displayName, description,
    #   mandatoryFields[], optionalFields[],
    #   additionalLicenses[] (e.g., FSSAI for food),
    #   riskWeight, isActive, iconName,
    #   productCount, createdAt, updatedAt

    def save_category(self, category: dict) -> bool:
        cat_id = category.get("categoryId")
        if not cat_id:
            logger.error("save_category: categoryId is required")
            return False
        if "createdAt" not in category:
            category["createdAt"] = self._now_ms()
        return self.save_document(self.CATEGORIES_COLLECTION, cat_id, category)

    def get_category(self, category_id: str) -> dict | None:
        return self.get_document(self.CATEGORIES_COLLECTION, category_id)

    def get_all_categories(self) -> list[dict]:
        return self.query_collection(
            self.CATEGORIES_COLLECTION,
            order_by="name",
            direction="ASCENDING",
        )

    def get_active_categories(self) -> list[dict]:
        return self.query_collection(
            self.CATEGORIES_COLLECTION,
            filters=[("isActive", "==", True)],
            order_by="name",
            direction="ASCENDING",
        )

    # ══════════════════════════════════════════════════════════════════════
    # IoT Devices (legacy — kept for backward compatibility)
    # ══════════════════════════════════════════════════════════════════════

    def is_device_registered(self, device_id: str) -> bool:
        doc = self.get_document(self.IOT_DEVICES_COLLECTION, device_id)
        return doc is not None and doc.get("active", False)

    def register_device(self, device_id: str, device_info: dict) -> bool:
        payload = {
            "deviceId": device_id,
            "active": True,
            "registeredAt": self._now_ms(),
            **device_info,
        }
        return self.save_document(self.IOT_DEVICES_COLLECTION, device_id, payload)

    def log_iot_activity(self, device_id: str, result: dict) -> None:
        """Append an activity log entry (new document per scan)."""
        try:
            log_id = str(uuid.uuid4())
            payload = {
                "deviceId": device_id,
                "success": result.get("success"),
                "message": result.get("message"),
                "timestamp": result.get("timestamp"),
                "hasReport": result.get("report") is not None,
            }
            self.save_document(self.IOT_LOGS_COLLECTION, log_id, payload)
        except Exception as e:
            logger.error(f"log_iot_activity failed: {e}")

    # ══════════════════════════════════════════════════════════════════════
    # Analytics helpers
    # ══════════════════════════════════════════════════════════════════════

    def get_analytics_summary(self) -> dict:
        """Get aggregate analytics across all collections."""
        try:
            total_users = self.count_collection(self.USERS_COLLECTION)
            total_products = self.count_collection(self.PRODUCTS_COLLECTION)
            total_reports = self.count_collection(self.REPORTS_COLLECTION)
            total_violations = self.count_collection(self.VIOLATIONS_COLLECTION)
            open_violations = self.count_collection(
                self.VIOLATIONS_COLLECTION,
                filters=[("status", "==", "OPEN")],
            )

            # Risk distribution
            risk_dist = {}
            for level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
                risk_dist[level] = self.count_collection(
                    self.REPORTS_COLLECTION,
                    filters=[("riskLevel", "==", level)],
                )

            # Status distribution
            status_dist = {}
            for status in ["COMPLIANT", "PARTIAL_COMPLIANT", "NON_COMPLIANT"]:
                status_dist[status] = self.count_collection(
                    self.REPORTS_COLLECTION,
                    filters=[("complianceStatus", "==", status)],
                )

            return {
                "total_users": total_users,
                "total_products": total_products,
                "total_reports": total_reports,
                "total_violations": total_violations,
                "open_violations": open_violations,
                "risk_distribution": risk_dist,
                "status_distribution": status_dist,
                "generated_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"get_analytics_summary failed: {e}")
            return {}
