# genpark-autonomous-expense-policy-auditor-and-receipt-reconciler-skill

Autonomous corporate expense auditor, receipt-to-ledger reconciler, and multi-tier spend policy compliance engine.

100% Python Standard Library implementation with zero external dependencies.

## Key Capabilities

- **Autonomous Policy Compliance Auditing**: Automatically enforces corporate expense guidelines (meal per-diem caps, mandatory receipt thresholds, restricted MCC categories).
- **OCR Receipt Reconciler**: Cross-checks raw OCR text against card clearing transactions, validating totals and flagging alcohol or non-business items.
- **Finance Team Exception Routing**: Auto-approves compliant transactions within thresholds while routing edge-case policy deviations with detailed audit logs.

## Architecture

```
[Card Transaction + Receipt OCR Text]
                 │
                 ▼
┌──────────────────────────────────────────────────┐
│             ExpensePolicyAuditor                 │
│  - OCR Amount & Line-Item Entity Extractor       │
│  - Per-Diem & Weekend Spend Boundary Check       │
│  - Restricted MCC & Alcohol Detection Rules      │
└──────────────────────────────────────────────────┘
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
[AUTONOMOUS_APPROVED]  [FLAGGED_FOR_FINANCE_REVIEW]
```

## MCP Server Integration

Run standard MCP stdio server:
```bash
python mcp_server.py
```

Exposed Tools:
- `audit_expense_transaction`: Audits corporate card expenses against spend policy limits and cross-references OCR receipt data.

## Quickstart (Python API)

```python
from client import ExpensePolicyAuditor

tx = {"id": "1", "merchant": "Sweetgreen", "category": "restaurants", "amount": 22.0}
res = ExpensePolicyAuditor.audit_and_reconcile_expense(tx, "SWEETGREEN Total: $22.00")
print("Status:", res["audit_status"])
```

---

## GenPark Ecosystem

- **Official Website**: [https://www.genpark.ai](https://www.genpark.ai)
- **LinkedIn Page**: [https://www.linkedin.com/company/92955550](https://www.linkedin.com/company/92955550)
