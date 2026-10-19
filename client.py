"""Autonomous Corporate Expense Policy Auditor and Receipt Reconciler.
100% Python Standard Library.
"""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime


class ExpensePolicyAuditor:
    """Audits corporate expenses against company policy rules (per diem caps, MCC restrictions,
    weekend spend, required receipt attachments) and reconciles OCR receipt text with card ledger items."""

    # Default corporate expense policy limits
    DEFAULT_POLICY = {
        "meal_per_diem_cap": 75.0,
        "single_tx_receipt_required_threshold": 25.0,
        "alcohol_allowed_without_memo": False,
        "restricted_mcc_categories": ["gambling", "crypto", "nightclub", "luxury_retail"],
        "max_autonomous_approval_limit": 500.0,
    }

    @staticmethod
    def extract_receipt_fields(ocr_text: str) -> Dict[str, Any]:
        """Extracts merchant name, total amount, date, and line item clues from receipt OCR text."""
        # Find currency amounts ($XX.YY)
        amounts = re.findall(r'\$\s*(\d+(?:\.\d{2})?)', ocr_text)
        max_amount = max([float(a) for a in amounts]) if amounts else None

        # Detect merchant name (usually top 2 lines)
        lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
        merchant = lines[0] if lines else "Unknown Merchant"

        # Detect dates (YYYY-MM-DD or MM/DD/YYYY)
        date_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', ocr_text)
        date_str = date_match.group(1) if date_match else None

        # Detect alcohol keyword presence
        has_alcohol = bool(re.search(r'\b(beer|wine|cocktail|vodka|whiskey|bar|liquor)\b', ocr_text, re.IGNORECASE))

        return {
            "merchant": merchant,
            "detected_total": max_amount,
            "detected_date": date_str,
            "contains_alcohol": has_alcohol,
            "line_count": len(lines),
        }

    @classmethod
    def audit_and_reconcile_expense(
        cls,
        card_transaction: Dict[str, Any],
        receipt_ocr_text: Optional[str] = None,
        custom_policy: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Validates a card transaction against company spend policies and cross-references receipt data."""
        policy = dict(cls.DEFAULT_POLICY)
        if custom_policy:
            policy.update(custom_policy)

        tx_id = card_transaction.get("id", "tx_unknown")
        amount = float(card_transaction.get("amount", 0.0))
        mcc_category = str(card_transaction.get("category", "")).lower()
        merchant_name = str(card_transaction.get("merchant", ""))

        policy_violations = []
        requires_human_approval = False

        # 1. Check MCC Category Restrictions
        if mcc_category in policy["restricted_mcc_categories"]:
            policy_violations.append({
                "rule": "RESTRICTED_CATEGORY",
                "severity": "CRITICAL_VIOLATION",
                "detail": f"Merchant category '{mcc_category}' is explicitly banned by corporate spend policy.",
            })
            requires_human_approval = True

        # 2. Check Receipt Requirement
        receipt_required = amount >= policy["single_tx_receipt_required_threshold"]
        receipt_attached = bool(receipt_ocr_text and receipt_ocr_text.strip())

        reconciliation_match = None
        if receipt_required and not receipt_attached:
            policy_violations.append({
                "rule": "MISSING_RECEIPT",
                "severity": "POLICY_WARNING",
                "detail": f"Transactions over ${policy['single_tx_receipt_required_threshold']:.2f} require an itemized receipt.",
            })
            requires_human_approval = True
        elif receipt_attached:
            # 3. Cross-reference OCR receipt against card transaction
            extracted = cls.extract_receipt_fields(receipt_ocr_text)
            receipt_total = extracted.get("detected_total")

            amount_delta = abs(amount - receipt_total) if receipt_total else None
            is_matched = (amount_delta is not None and amount_delta <= 1.0)  # tolerate small tip/tax delta

            if not is_matched and receipt_total:
                policy_violations.append({
                    "rule": "RECEIPT_TOTAL_MISMATCH",
                    "severity": "AUDIT_FLAG",
                    "detail": f"Receipt total (${receipt_total:.2f}) does not match card charge (${amount:.2f}).",
                })
                requires_human_approval = True

            if extracted.get("contains_alcohol") and not policy["alcohol_allowed_without_memo"]:
                policy_violations.append({
                    "rule": "ALCOHOL_MEMO_REQUIRED",
                    "severity": "POLICY_FLAG",
                    "detail": "Alcohol detected on itemized receipt; business purpose justification memo required.",
                })
                requires_human_approval = True

            reconciliation_match = {
                "receipt_matched": is_matched,
                "extracted_merchant": extracted.get("merchant"),
                "extracted_total": receipt_total,
                "alcohol_detected": extracted.get("contains_alcohol"),
            }

        # 4. Meal Per-Diem Cap Check
        if mcc_category in ["restaurants", "dining", "meals"] and amount > policy["meal_per_diem_cap"]:
            policy_violations.append({
                "rule": "MEAL_PER_DIEM_EXCEEDED",
                "severity": "WARNING",
                "detail": f"Meal amount ${amount:.2f} exceeds per-diem limit of ${policy['meal_per_diem_cap']:.2f}.",
            })
            requires_human_approval = True

        # 5. Autonomous Approval Ceiling Check
        if amount > policy["max_autonomous_approval_limit"]:
            requires_human_approval = True

        status = "AUTONOMOUSLY_APPROVED" if (not policy_violations and not requires_human_approval) else "FLAGGED_FOR_FINANCE_REVIEW"

        return {
            "transaction_id": tx_id,
            "merchant": merchant_name,
            "amount": amount,
            "audit_status": status,
            "autonomous_approval": status == "AUTONOMOUSLY_APPROVED",
            "violations_count": len(policy_violations),
            "violations": policy_violations,
            "reconciliation": reconciliation_match,
        }
