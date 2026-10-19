"""MCP server for Autonomous Corporate Expense Policy Auditor & Receipt Reconciler."""
import sys
import json
from client import ExpensePolicyAuditor


def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "audit_expense_transaction",
                    "description": "Audits corporate card expenses against spend policy limits and cross-references OCR receipt data",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "card_transaction": {
                                "type": "object",
                                "description": "Transaction record containing id, amount, category, merchant, and date",
                            },
                            "receipt_ocr_text": {
                                "type": "string",
                                "description": "Optional raw OCR text from receipt photo",
                            },
                            "custom_policy": {
                                "type": "object",
                                "description": "Optional custom limits (e.g. meal_per_diem_cap, receipt_threshold)",
                            },
                        },
                        "required": ["card_transaction"],
                    },
                }
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "audit_expense_transaction":
            res = ExpensePolicyAuditor.audit_and_reconcile_expense(
                args.get("card_transaction", {}),
                receipt_ocr_text=args.get("receipt_ocr_text"),
                custom_policy=args.get("custom_policy"),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
    return {"error": "Method not found"}


if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(handle_request(json.loads(line))))
            sys.stdout.flush()
