"""Example usage for Autonomous Corporate Expense Policy Auditor & Receipt Reconciler."""
from client import ExpensePolicyAuditor

if __name__ == "__main__":
    # Case 1: Clean approved transaction with receipt
    tx_clean = {
        "id": "tx_001",
        "merchant": "Sweetgreen",
        "category": "restaurants",
        "amount": 22.50,
    }
    receipt_clean = "SWEETGREEN\nDate: 2026-10-18\nKale Salad: $18.50\nTax: $4.00\nTotal: $22.50"
    res1 = ExpensePolicyAuditor.audit_and_reconcile_expense(tx_clean, receipt_clean)
    print("Case 1 (Clean Expense):", res1["audit_status"], "| Autonomous Approval:", res1["autonomous_approval"])

    # Case 2: Expense with alcohol flag and missing memo
    tx_bar = {
        "id": "tx_002",
        "merchant": "Skyline Lounge",
        "category": "restaurants",
        "amount": 88.00,
    }
    receipt_bar = "SKYLINE LOUNGE\n2x Appetizers: $40.00\n1x Red Wine Bottle: $48.00\nTotal: $88.00"
    res2 = ExpensePolicyAuditor.audit_and_reconcile_expense(tx_bar, receipt_bar)
    print("\nCase 2 (Alcohol Flag):", res2["audit_status"])
    for v in res2["violations"]:
        print(f"  - [{v['severity']}] {v['rule']}: {v['detail']}")
