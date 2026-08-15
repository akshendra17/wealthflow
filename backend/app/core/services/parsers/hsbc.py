"""
HSBC Credit Card Statement Parser
Format (from actual PDF text extraction):
  - Date format: DDMMM (e.g., 26MAY, 01JUN) — no year, year is inferred from statement period
  - Transaction line: DDMMM <description> <amount> [CR]
  - CR suffix = CREDIT (payment), no suffix = DEBIT (purchase)
  - Summary lines like TOTAL, OPENING BALANCE, NET OUTSTANDING BALANCE are skipped
"""
import io
import re
from datetime import datetime
from typing import Optional, Union

import pdfplumber

from . import register_parser
from .base import BaseBankParser, ParsedTransaction, ParseResult
from app.core.exceptions import ParsingError

_SKIP_KW = {
    "opening balance", "closing balance", "total", "net outstanding",
    "purchases & installments", "total purchase", "total cash",
    "total balance transfer", "total loan", "interest rate",
    "minimum amount due", "amount due", "payment received",
    "brought forward", "finance charges", "statement summary",
}

# DDMMM <description> <amount>[CR]
# e.g.: 26MAY RSP*MANAM CHOCOLATE MALKAJGIRI TEL 1,300.00
# e.g.: 29MAY BBPS PMT BBPSDP016149190450ghHfvn 94,480.71 CR
_HSBC_TXN_RE = re.compile(
    r"^(\d{2}[A-Z]{3})\s+(.+?)\s+([\d,]+\.\d{2})\s*(CR)?$",
    re.IGNORECASE,
)

# Statement period: "22 MAY 2026 To 21 JUN 2026"
_PERIOD_RE = re.compile(
    r"(\d{2}\s+[A-Z]+\s+(\d{4}))\s+To\s+(\d{2}\s+[A-Z]+\s+(\d{4}))",
    re.IGNORECASE,
)


def _infer_year(month_str: str, statement_year: int, statement_month: int) -> int:
    """Given a 3-letter month, infer the correct year using the statement period."""
    try:
        txn_month = datetime.strptime(month_str, "%b").month
    except ValueError:
        return statement_year
    # If txn month is after the statement end month by a big gap, it's the previous year
    if statement_month < 6 and txn_month > 9:
        return statement_year - 1
    return statement_year


@register_parser("hsbc")
class HSBCParser(BaseBankParser):

    @classmethod
    def detect(cls, text_content: str) -> bool:
        lower = text_content.lower()
        return "hsbc" in lower or "hongkong and shanghai banking corporation" in lower

    @classmethod
    def parse_pdf(cls, file_bytes: bytes, password: Optional[str] = None) -> ParseResult:
        transactions: list[ParsedTransaction] = []
        errors: list[str] = []
        statement_year: Optional[int] = None
        statement_month: Optional[int] = None

        try:
            kwargs = {"password": password} if password else {}
            with pdfplumber.open(io.BytesIO(file_bytes), **kwargs) as pdf:
                full_text = ""
                for page in pdf.pages:
                    full_text += (page.extract_text() or "") + "\n"

                # Extract statement period to infer year
                period_match = _PERIOD_RE.search(full_text)
                if period_match:
                    try:
                        end_dt = datetime.strptime(period_match.group(3), "%d %B %Y")
                        statement_year = end_dt.year
                        statement_month = end_dt.month
                    except ValueError:
                        try:
                            end_dt = datetime.strptime(period_match.group(3), "%d %b %Y")
                            statement_year = end_dt.year
                            statement_month = end_dt.month
                        except ValueError:
                            pass

                if not statement_year:
                    # Fallback: grab any 4-digit year from the text
                    yr_match = re.search(r"\b(20\d{2})\b", full_text)
                    if yr_match:
                        statement_year = int(yr_match.group(1))
                        statement_month = 12  # conservative fallback

                for line in full_text.splitlines():
                    line = line.strip()
                    if not line:
                        continue

                    lo = line.lower()
                    if any(kw in lo for kw in _SKIP_KW):
                        continue

                    match = _HSBC_TXN_RE.match(line)
                    if not match:
                        continue

                    date_str, desc, amt_str, cr_flag = match.groups()

                    # Parse DDMMM → full date
                    day_str = date_str[:2]
                    month_str = date_str[2:]
                    year = _infer_year(month_str, statement_year or datetime.now().year, statement_month or 12)

                    try:
                        txn_date = datetime.strptime(f"{day_str} {month_str} {year}", "%d %b %Y").date()
                    except ValueError:
                        errors.append(f"Bad date: {date_str}")
                        continue

                    amt = float(amt_str.replace(",", ""))
                    if amt == 0:
                        continue

                    # CR = payment/refund (CREDIT), no suffix = purchase (DEBIT)
                    txn_type = "CREDIT" if cr_flag else "DEBIT"

                    transactions.append(
                        ParsedTransaction(
                            transaction_date=txn_date,
                            description=desc.strip(),
                            amount=amt,
                            transaction_type=txn_type,
                            raw_data={"raw_line": line},
                        )
                    )

        except Exception as e:
            if "password" in str(e).lower() or type(e).__name__ == "PdfminerException":
                raise ParsingError(
                    "This HSBC PDF is password-protected. Please provide the correct password."
                )
            raise ParsingError(f"Failed to read HSBC PDF: {e}")

        if not transactions:
            raise ParsingError("Could not extract any transactions from HSBC PDF statement.")

        if not statement_year:
            dates = [t.transaction_date for t in transactions]
            statement_year = max(dates).year
            statement_month = max(dates).month

        return ParseResult(
            transactions=transactions,
            bank_name="hsbc",
            statement_year=statement_year,
            statement_month=statement_month,
            errors=errors,
            metadata={"parsed_via": "hsbc_cc_pdf", "total_transactions": len(transactions)},
        )

    @classmethod
    def parse_csv(cls, file_content: Union[str, bytes]) -> ParseResult:
        raise ParsingError("HSBC CSV parsing is not supported. Please upload the PDF statement.")

