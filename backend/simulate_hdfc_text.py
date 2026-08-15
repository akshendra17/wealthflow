# Simulating what pdfplumber.extract_text() would produce for HDFC CC statement
# based on the screenshot
sample_text = """Domestic Transactions
Date Transaction Description Amount (in Rs.)
AKASH KUNDU
25/09/2024 LIC BILLDESK MUMBAI 14,257.59
27/09/2024 NETBANKING TRANSFER (Ref# 000000000000927019211667) 27,000.00 Cr
27/09/2024 Techno International N kolkata 66,155.76
28/09/2024 FLIPKART PAYMENTS BANGALORE 22,107.00
15/10/2024 BOOKMYSHOW MUMBAI 470.80
22/10/2024 CASHBACK FOR REDEMPTION OF PO221024 (Ref# ST242980084000103992991) 1,921.00 Cr
23/10/2024 Cashback Redemption Fee (Ref# ST242980084000010910479) 50.00
"""

import re

# New: dedicated HDFC CC parser logic
DATE_FORMATS = [
    "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y",
    "%d %b %Y", "%d-%b-%Y", "%d-%b-%y", "%d%b", "%d %b", "%d-%b",
]

SKIP_KEYWORDS = ["opening balance", "closing balance", "total", "statement summary",
                 "net outstanding balance", "amount due", "previous balance",
                 "minimum amount due", "balance carried forward", "brought forward"]

def parse_date(s):
    from datetime import datetime
    s = s.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None

# HDFC CC pattern: DD/MM/YYYY <description> <amount> [Cr]
hdfc_txn = re.compile(
    r"^(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([\d,]+\.\d{2})\s*(Cr)?$",
    re.IGNORECASE
)

transactions = []
for line in sample_text.splitlines():
    line = line.strip()
    m = hdfc_txn.match(line)
    if m:
        date_str, desc, amt_str, cr = m.groups()
        txn_date = parse_date(date_str)
        if txn_date is None:
            continue
        if any(k in desc.lower() for k in SKIP_KEYWORDS):
            continue
        amt = float(amt_str.replace(',', ''))
        txn_type = "CREDIT" if cr else "DEBIT"
        transactions.append({
            "date": txn_date,
            "desc": desc.strip(),
            "amount": amt,
            "type": txn_type
        })

for t in transactions:
    print(t)
print(f"\nTotal: {len(transactions)} transactions")
