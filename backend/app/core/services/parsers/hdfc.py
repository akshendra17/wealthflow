"""
HDFC Bank Statement Parser

PDF layouts supported via ordered strategy chain:

1. Regalia / newer credit card — DATE & TIME | DESCRIPTION | AMOUNT (C/₹ glyph, + credit)
2. Millennia / older credit card — DD/MM/YYYY description amount [Cr]
3. Table extraction — when pdfplumber yields proper multi-column tables
4. Structural heuristic — last-resort date-anchored line scan

CSV: HDFC Savings Account NetBanking export (Date, Narration, Debit, Credit, ...)
"""
import csv
import io
import re
from datetime import datetime
from typing import Callable, Optional, Union

import pdfplumber

from . import register_parser
from .base import BaseBankParser, ParsedTransaction, ParseResult
from app.core.exceptions import ParsingError

# ── Skip keywords (case-insensitive substring match) ────────────────────────
_SKIP_KW = {
    "opening balance", "closing balance", "total", "net outstanding",
    "statement summary", "minimum amount due", "amount due", "previous balance",
    "balance carried forward", "brought forward", "finance charges",
    "account summary", "past dues", "cash points", "payment due",
    "credit limit", "minimum payment", "total outstanding", "payment summary",
    "purchases/debit", "payments/credits", "reward points", "billing period",
    "previous statement", "finance charge", "total amount due",
    "domestic transactions", "date & time", "transaction description",
    "smart emi", "gst summary", "loan number", "programs bonus",
    "eligible for emi", "convert to emi", "transaction total",
    "important information", "purchase indicator",
}

_PAGE_RE = re.compile(r"^page\s+\d+\s+of\s+\d+", re.IGNORECASE)
_HEADER_LINE_RE = re.compile(
    r"^date\s*&\s*time\s+transaction\s+description",
    re.IGNORECASE,
)

# Regalia CC: "19/06/2026| 00:00 NETFLIXMUMBAI + C 22,457.00 l"
_REGALIA_CC_RE = re.compile(
    r"^(\d{2}/\d{2}/\d{4})"
    r"(?:\s*\|\s*\d{2}:\d{2})?"
    r"(?:\s+(?P<desc>[A-Za-z].+?))?"
    r"\s*(?P<credit>\+)?\s*(?:[C₹]|Rs\.?)\s*(?P<amount>[\d,]+\.\d{2})"
    r"(?:\s+[a-z])?"
    r"\s*$",
    re.IGNORECASE,
)

# Millennia CC: "25/09/2024  LIC BILLDESK MUMBAI  14,257.59 [Cr]"
_MILLENNIA_CC_RE = re.compile(
    r"^(\d{2}/\d{2}/\d{4})\s+"
    r"([A-Za-z].+?)\s+"
    r"([\d,]+\.\d{2})\s*(Cr)?$",
    re.IGNORECASE,
)

_STATEMENT_DATE_RE = re.compile(
    r"Statement Date\s+(\d{1,2}\s+[A-Za-z]{3},?\s+\d{4})",
    re.IGNORECASE,
)
_BILLING_PERIOD_RE = re.compile(
    r"Billing Period\s+.+?-\s*(\d{1,2}\s+[A-Za-z]{3},?\s+\d{4})",
    re.IGNORECASE,
)
_PERIOD_FALLBACK_RE = re.compile(
    r"(?:Statement Date|Billing Period|Period)[:\s]+"
    r"(\d{2}[- ][A-Za-z0-9]{2,9}[- ]\d{2,4}|\d{2}/\d{2}/\d{4})",
    re.IGNORECASE,
)

_CC_PDF_ERROR = (
    "Could not extract transactions from this HDFC credit card statement.\n"
    "Tip: Ensure the PDF is not scanned/image-only. If the format recently changed, "
    "try re-downloading the latest statement from HDFC NetBanking."
)

_GENERIC_PDF_ERROR = (
    "Could not extract transactions from this HDFC statement.\n"
    "Tip: For savings accounts, try uploading the CSV export from HDFC NetBanking."
)

_CSV_ERROR = (
    "Could not extract transactions from this HDFC savings account CSV.\n"
    "Tip: Download the account statement CSV from HDFC NetBanking "
    "(Date, Narration, Debit, Credit columns)."
)


def _skip(line: str) -> bool:
    lo = line.lower().strip()
    if not lo:
        return True
    if _PAGE_RE.match(lo):
        return True
    if _HEADER_LINE_RE.match(lo):
        return True
    return any(kw in lo for kw in _SKIP_KW)


def _clean_amt(s: str) -> Optional[float]:
    s = re.sub(r"[₹Rs,\s]", "", s.strip())
    try:
        return float(s) if s else None
    except ValueError:
        return None


def _parse_date_str(s: str) -> Optional[datetime]:
    normalized = re.sub(r",", "", s.strip())
    for fmt in (
        "%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y",
        "%d %b %Y", "%d-%b-%Y", "%d %b %y", "%d-%b-%y",
    ):
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            pass
    return None


def _extract_period(full_text: str) -> tuple[Optional[int], Optional[int]]:
    for pattern in (_STATEMENT_DATE_RE, _BILLING_PERIOD_RE, _PERIOD_FALLBACK_RE):
        m = pattern.search(full_text)
        if m:
            dt = _parse_date_str(m.group(1))
            if dt:
                return dt.year, dt.month
    yr = re.search(r"\b(20\d{2})\b", full_text)
    return (int(yr.group(1)), None) if yr else (None, None)


def _append_desc_buffer(transactions: list[ParsedTransaction], desc_buffer: list[str]) -> None:
    if desc_buffer and transactions:
        extra = " ".join(desc_buffer).strip()
        if extra:
            transactions[-1].description = f"{transactions[-1].description} {extra}".strip()


def _is_likely_cardholder_name(line: str) -> bool:
    """Skip standalone cardholder name lines that appear above the txn table."""
    s = line.strip()
    return (
        bool(re.match(r"^[A-Z][A-Z\s'.]+$", s))
        and len(s) < 50
        and not any(c.isdigit() for c in s)
    )


def _is_ref_continuation(line: str) -> bool:
    """Lines like '09999999980619014462723)' that continue a Ref# from above."""
    stripped = line.strip()
    return bool(stripped) and stripped[0].isdigit() and ")" in stripped


def parse_regalia_cc_text(full_text: str) -> list[ParsedTransaction]:
    """Parse newer HDFC Regalia / credit card PDF text layout."""
    transactions: list[ParsedTransaction] = []
    desc_buffer: list[str] = []

    for line in full_text.splitlines():
        line = line.strip()
        if not line or _skip(line):
            desc_buffer.clear()
            continue

        m = _REGALIA_CC_RE.match(line)
        if m:
            date_str = m.group(1)
            middle = m.group("desc")
            plus_sign = m.group("credit")
            amt_str = m.group("amount")
            dt = _parse_date_str(date_str)
            if dt is None:
                desc_buffer.append(line)
                continue

            inline_desc = (middle or "").strip()
            full_desc = (" ".join(desc_buffer) + " " + inline_desc).strip()
            desc_buffer = []

            if _skip(full_desc):
                continue

            amt = _clean_amt(amt_str)
            if not amt:
                continue

            is_credit = plus_sign is not None
            transactions.append(ParsedTransaction(
                transaction_date=dt.date(),
                description=full_desc or "HDFC Transaction",
                amount=amt,
                transaction_type="CREDIT" if is_credit else "DEBIT",
                raw_data={"raw_line": line, "layout": "regalia"},
            ))
            continue

        if _is_ref_continuation(line):
            if transactions:
                transactions[-1].description = (
                    f"{transactions[-1].description} {line.strip()}"
                ).strip()
            else:
                desc_buffer.append(line)
            continue

        if not _is_likely_cardholder_name(line):
            desc_buffer.append(line)

    _append_desc_buffer(transactions, desc_buffer)
    return transactions


def parse_millennia_cc_text(full_text: str) -> list[ParsedTransaction]:
    """Parse older HDFC Millennia / credit card PDF text layout."""
    transactions: list[ParsedTransaction] = []
    desc_buffer: list[str] = []

    for line in full_text.splitlines():
        line = line.strip()
        if not line or _skip(line):
            desc_buffer.clear()
            continue

        m = _MILLENNIA_CC_RE.match(line)
        if m:
            date_str, desc, amt_str, cr_flag = m.groups()
            dt = _parse_date_str(date_str)
            if dt is None:
                desc_buffer.append(line)
                continue

            full_desc = (" ".join(desc_buffer) + " " + desc.strip()).strip()
            desc_buffer = []

            if _skip(full_desc):
                continue

            amt = _clean_amt(amt_str)
            if not amt:
                continue

            transactions.append(ParsedTransaction(
                transaction_date=dt.date(),
                description=full_desc,
                amount=amt,
                transaction_type="CREDIT" if cr_flag else "DEBIT",
                raw_data={"raw_line": line, "layout": "millennia"},
            ))
            continue

        desc_buffer.append(line)

    _append_desc_buffer(transactions, desc_buffer)
    return transactions


def _parse_cc_table_row(
    row: list,
    date_col: int,
    desc_col: Optional[int],
    amt_col: int,
) -> Optional[ParsedTransaction]:
    if date_col >= len(row) or amt_col >= len(row):
        return None

    date_str = str(row[date_col] or "").strip()
    if not date_str:
        return None

    # Regalia tables may embed time in date cell: "19/06/2026| 00:00"
    date_part = date_str.split("|")[0].strip()
    dt = _parse_date_str(date_part)
    if dt is None:
        return None

    desc = ""
    if desc_col is not None and desc_col < len(row):
        desc = str(row[desc_col] or "").strip()

    amt_raw = str(row[amt_col] or "").strip()
    is_credit = "+" in amt_raw or amt_raw.lower().endswith("cr")
    amt = _clean_amt(amt_raw)
    if not amt:
        return None

    if _skip(desc):
        return None

    return ParsedTransaction(
        transaction_date=dt.date(),
        description=desc or "HDFC Transaction",
        amount=amt,
        transaction_type="CREDIT" if is_credit else "DEBIT",
        raw_data={"raw_table_row": str(row), "layout": "table"},
    )


def parse_cc_table(pdf: pdfplumber.PDF) -> list[ParsedTransaction]:
    """Extract transactions from properly structured pdfplumber tables."""
    transactions: list[ParsedTransaction] = []

    for page in pdf.pages:
        for table in page.extract_tables() or []:
            if not table or len(table) < 2:
                continue

            header = None
            header_idx = 0
            for i, row in enumerate(table):
                flat = [str(c or "").lower().strip() for c in row]
                if any("date" in c for c in flat) and any(
                    "amount" in c or "description" in c for c in flat
                ):
                    header = flat
                    header_idx = i
                    break

            if header is None:
                # Savings-style embedded table
                if len(table[0]) >= 6:
                    hdr = [str(h).lower().strip() for h in table[0]]
                    if "narration" in hdr and "value dt" in hdr:
                        for row in table[1:]:
                            if len(row) < 6 or not row[0]:
                                continue
                            dt = _parse_date_str(str(row[0]))
                            if not dt:
                                continue
                            desc = str(row[1]).strip()
                            if _skip(desc):
                                continue
                            debit_val = _clean_amt(str(row[4])) or 0.0
                            credit_val = _clean_amt(str(row[5])) or 0.0
                            if credit_val > 0:
                                transactions.append(ParsedTransaction(
                                    transaction_date=dt.date(),
                                    description=desc,
                                    amount=credit_val,
                                    transaction_type="CREDIT",
                                    raw_data={"raw_table_row": str(row), "layout": "table_savings"},
                                ))
                            elif debit_val > 0:
                                transactions.append(ParsedTransaction(
                                    transaction_date=dt.date(),
                                    description=desc,
                                    amount=debit_val,
                                    transaction_type="DEBIT",
                                    raw_data={"raw_table_row": str(row), "layout": "table_savings"},
                                ))
                continue

            date_col = next((i for i, h in enumerate(header) if "date" in h), None)
            desc_col = next(
                (i for i, h in enumerate(header)
                 if "description" in h or "narration" in h or "particular" in h),
                None,
            )
            amt_col = next((i for i, h in enumerate(header) if "amount" in h), None)

            if date_col is None or amt_col is None:
                continue

            for row in table[header_idx + 1:]:
                txn = _parse_cc_table_row(row, date_col, desc_col, amt_col)
                if txn:
                    transactions.append(txn)

    return transactions


def parse_structural_heuristic(full_text: str) -> list[ParsedTransaction]:
    """Last-resort: find date-anchored lines with currency+amount tokens."""
    transactions: list[ParsedTransaction] = []
    line_re = re.compile(
        r"^(\d{2}/\d{2}/\d{4})"
        r"(?:\s*\|\s*\d{2}:\d{2})?"
        r"(?:\s+(?P<desc>[A-Za-z].+?))?"
        r"\s*(?P<credit>\+)?\s*(?:[C₹]|Rs\.?)\s*(?P<amount>[\d,]+\.\d{2})"
        r"(?:\s+[a-z])?"
        r"\s*$",
        re.IGNORECASE,
    )

    for line in full_text.splitlines():
        line = line.strip()
        if not line or _skip(line):
            continue

        m = line_re.match(line)
        if not m:
            continue

        date_str = m.group(1)
        middle = m.group("desc")
        plus_sign = m.group("credit")
        amt_str = m.group("amount")
        dt = _parse_date_str(date_str)
        if dt is None:
            continue

        desc = (middle or "").strip()
        if _skip(desc):
            continue

        amt = _clean_amt(amt_str)
        if not amt:
            continue

        transactions.append(ParsedTransaction(
            transaction_date=dt.date(),
            description=desc or "HDFC Transaction",
            amount=amt,
            transaction_type="CREDIT" if plus_sign else "DEBIT",
            raw_data={"raw_line": line, "layout": "heuristic"},
        ))

    return transactions


_PDF_STRATEGIES: list[tuple[str, Callable[..., list[ParsedTransaction]]]] = [
    ("hdfc_regalia_cc_text", parse_regalia_cc_text),
    ("hdfc_millennia_cc_text", parse_millennia_cc_text),
    ("hdfc_cc_table", parse_cc_table),
    ("hdfc_structural_heuristic", parse_structural_heuristic),
]


def _run_pdf_strategies(
    pdf: pdfplumber.PDF,
    full_text: str,
) -> tuple[list[ParsedTransaction], str]:
    """Run strategies in order; return first non-empty result."""
    for strategy_name, strategy_fn in _PDF_STRATEGIES:
        if strategy_fn is parse_cc_table:
            result = strategy_fn(pdf)
        else:
            result = strategy_fn(full_text)

        if result:
            return result, strategy_name

    return [], ""


def _is_credit_card_statement(full_text: str) -> bool:
    lower = full_text.lower()
    return (
        "credit card" in lower
        or "date & time" in lower
        or "transaction description" in lower
    )


@register_parser("hdfc")
class HDFCParser(BaseBankParser):

    @classmethod
    def detect(cls, text_content: str) -> bool:
        return "hdfc" in text_content.lower()

    @classmethod
    def parse_pdf(cls, file_bytes: bytes, password: Optional[str] = None) -> ParseResult:
        transactions: list[ParsedTransaction] = []
        parsed_via = ""
        stmt_year: Optional[int] = None
        stmt_month: Optional[int] = None
        full_text = ""
        is_cc = False

        try:
            clean_pwd = password.strip() if password else None
            kwargs = {"password": clean_pwd} if clean_pwd else {}
            with pdfplumber.open(io.BytesIO(file_bytes), **kwargs) as pdf:
                full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                stmt_year, stmt_month = _extract_period(full_text)
                is_cc = _is_credit_card_statement(full_text)
                transactions, parsed_via = _run_pdf_strategies(pdf, full_text)

        except ParsingError:
            raise
        except Exception as e:
            err = str(e)
            if "password" in err.lower() or type(e).__name__ in (
                "PdfminerException", "PDFPasswordIncorrect",
            ):
                raise ParsingError(
                    "This HDFC PDF is password-protected. "
                    "Please enter the password (usually your Date of Birth: DDMMYYYY)."
                )
            raise ParsingError(f"Failed to read HDFC PDF: {e}")

        if not transactions:
            raise ParsingError(_CC_PDF_ERROR if is_cc else _GENERIC_PDF_ERROR)

        if not stmt_year:
            dates = [t.transaction_date for t in transactions]
            stmt_year = max(dates).year
            stmt_month = max(dates).month

        return ParseResult(
            transactions=transactions,
            bank_name="hdfc",
            statement_year=stmt_year,
            statement_month=stmt_month,
            errors=[],
            metadata={"parsed_via": parsed_via, "total_transactions": len(transactions)},
        )

    @classmethod
    def parse_csv(cls, file_content: Union[str, bytes]) -> ParseResult:
        if isinstance(file_content, bytes):
            try:
                text = file_content.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = file_content.decode("latin-1")
        else:
            text = file_content

        transactions: list[ParsedTransaction] = []
        errors: list[str] = []
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)

        header_idx, headers = None, []
        for i, row in enumerate(rows):
            flat = [c.lower().strip() for c in row if c]
            if "narration" in flat or ("date" in flat and "debit" in flat):
                headers = [c.strip().lower() for c in row]
                header_idx = i
                break

        if header_idx is None:
            raise ParsingError("Could not find a header row in the HDFC CSV.")

        def col(*names: str) -> Optional[int]:
            for name in names:
                try:
                    return headers.index(name)
                except ValueError:
                    pass
            return None

        date_col = col("date")
        narr_col = col("narration", "description", "particulars")
        debit_col = col("debit", "withdrawal amt.", "debit amount")
        credit_col = col("credit", "deposit amt.", "credit amount")

        if date_col is None or narr_col is None:
            raise ParsingError("HDFC CSV is missing expected Date/Narration columns.")

        for row_num, row in enumerate(rows[header_idx + 1:], start=header_idx + 2):
            if not row or not any(c.strip() for c in row):
                continue

            date_str = row[date_col].strip() if date_col < len(row) else ""
            narr = row[narr_col].strip() if narr_col < len(row) else ""
            if not date_str or not narr:
                continue

            dt = _parse_date_str(date_str)
            if dt is None:
                errors.append(f"Row {row_num}: bad date '{date_str}'")
                continue
            if _skip(narr):
                continue

            debit_str = row[debit_col].strip() if debit_col is not None and debit_col < len(row) else ""
            credit_str = row[credit_col].strip() if credit_col is not None and credit_col < len(row) else ""

            dv = _clean_amt(debit_str) or 0.0
            cv = _clean_amt(credit_str) or 0.0

            if dv > 0:
                transactions.append(ParsedTransaction(
                    dt.date(), narr, dv, "DEBIT", {"raw": ",".join(row)},
                ))
            elif cv > 0:
                transactions.append(ParsedTransaction(
                    dt.date(), narr, cv, "CREDIT", {"raw": ",".join(row)},
                ))

        if not transactions:
            raise ParsingError(_CSV_ERROR)

        dates = [t.transaction_date for t in transactions]
        return ParseResult(
            transactions=transactions,
            bank_name="hdfc",
            statement_year=max(dates).year,
            statement_month=max(dates).month,
            errors=errors,
            metadata={"parsed_via": "hdfc_sa_csv", "total_transactions": len(transactions)},
        )
