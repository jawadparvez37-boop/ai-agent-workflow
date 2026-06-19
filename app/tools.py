from datetime import date

ACCOUNTS = {
    "ACME": {"name": "Acme Corp", "tier": "enterprise", "owner": "Jordan Lee"},
    "NORTH": {"name": "Northwind LLC", "tier": "standard", "owner": "Sam Patel"},
}

INVOICES = {
    "ACME": [
        {"id": "INV-1001", "amount": 3200, "status": "open", "due": "2026-03-01"},
        {"id": "INV-1008", "amount": 7400, "status": "open", "due": "2026-03-15"},
        {"id": "INV-1012", "amount": 900, "status": "paid", "due": "2026-02-01"},
    ],
    "NORTH": [
        {"id": "INV-2002", "amount": 1800, "status": "open", "due": "2026-03-05"},
    ],
}


def lookup_account(code: str) -> dict:
    key = code.strip().upper()
    if key not in ACCOUNTS:
        return {"found": False, "code": key}
    return {"found": True, "code": key, **ACCOUNTS[key]}


def list_invoices(code: str, status: str = "open") -> dict:
    key = code.strip().upper()
    rows = INVOICES.get(key, [])
    filtered = [row for row in rows if row["status"] == status]
    return {"code": key, "status": status, "invoices": filtered, "as_of": date.today().isoformat()}


def calculate_total(values: list[float]) -> dict:
  total = round(sum(values), 2)
  return {"count": len(values), "total": total}
