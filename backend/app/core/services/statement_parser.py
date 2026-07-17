"""Statement parser service — extracts transactions from CSV and PDF bank statements.

Supports generic CSV/PDF formats with configurable column mapping.
Expected columns (case-insensitive):
  - Date (or Transaction Date, Txn Date, Value Date)
  - Description (or Narration, Particulars, Details, Remarks)
  - Amount (or Debit, Credit, Withdrawal, Deposit)
"""

from __future__ import annotations

import csv
from typing import Optional, Union
import io
import re
from dataclasses import dataclass, field
from datetime import date, datetime

import structlog
import pdfplumber

from app.core.exceptions import ParsingError
from app.core.services.parsers import get_parser_by_name, detect_parser_from_text

logger = structlog.get_logger()

# Common date formats found in Indian and international bank statements
DATE_FORMATS = [
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d %b %Y",
    "%d-%b-%Y",
    "%d/%m/%y",
    "%d-%m-%y",
    "%m/%d/%y",
    "%d%b",
    "%d %b",
    "%d-%b",
]

# Keywords that indicate a line is a summary/balance, not a transaction
SKIP_KEYWORDS = [
    "total",
    "opening balance",
    "closing balance",
    "statement summary",
    "net outstanding balance",
    "amount due",
    "previous balance",
    "payment received",
    "minimum amount due",
    "total amount due",
    "balance carried forward",
    "brought forward",
]

# Column name mappings (lowercase key -> canonical name)
DATE_COLUMNS = {"date", "transaction date", "txn date", "value date", "posting date", "trans date"}
DESCRIPTION_COLUMNS = {
    "description", "narration", "particulars", "details", "remarks",
    "transaction details", "transaction description", "memo",
}
DEBIT_COLUMNS = {"debit", "withdrawal", "debit amount", "dr", "debit amt"}
CREDIT_COLUMNS = {"credit", "deposit", "credit amount", "cr", "credit amt"}
AMOUNT_COLUMNS = {"amount", "transaction amount", "txn amount"}
BALANCE_COLUMNS = {"balance", "closing balance", "running balance", "available balance"}


@dataclass
class ParsedTransaction:
    """A single parsed transaction from a bank statement."""

    transaction_date: date
    description: str
    amount: float
    transaction_type: str  # "DEBIT" or "CREDIT"
    raw_data: dict = field(default_factory=dict)


@dataclass
class ParseResult:
    """Result of parsing a bank statement."""

    transactions: list[ParsedTransaction]
    bank_name: Optional[str] = None
    statement_month: Optional[int] = None
    statement_year: Optional[int] = None
    errors: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


def _parse_date(date_str: str) -> Optional[date]:
    """Try multiple date formats to parse a date string."""
    date_str = date_str.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def _clean_amount(amount_str: str) -> Optional[float]:
    """Parse an amount string, removing currency symbols and commas."""
    if not amount_str or not amount_str.strip():
        return None
    cleaned = re.sub(r"[^\d.\-]", "", amount_str.strip())
    if not cleaned or cleaned == "-" or cleaned == ".":
        return None
    try:
        return abs(float(cleaned))
    except ValueError:
        return None


def _find_column(headers: list[str], candidates: set[str]) -> Optional[int]:
    """Find the index of a column by checking against candidate names."""
    for i, header in enumerate(headers):
        if header and header.lower().strip() in candidates:
            return i
    return None


def _parse_table(rows: list[list[str]], file_type: str) -> ParseResult:
    """Core logic to parse a 2D array of strings into transactions."""
    errors: list[str] = []
    transactions: list[ParsedTransaction] = []

    # Find the header row (skip blank lines and bank metadata)
    headers: list[str] = []
    header_row_idx = -1

    for idx, row in enumerate(rows):
        if not row:
            continue
        # A header row should have at least 3 columns and contain a date-like column
        if len(row) >= 3:
            row_lower = [str(c).lower().strip() if c else "" for c in row]
            has_date = any(c in DATE_COLUMNS for c in row_lower)
            has_desc = any(c in DESCRIPTION_COLUMNS for c in row_lower)
            has_amount = (
                any(c in AMOUNT_COLUMNS for c in row_lower)
                or any(c in DEBIT_COLUMNS for c in row_lower)
                or any(c in CREDIT_COLUMNS for c in row_lower)
            )
            if has_date and (has_desc or has_amount):
                headers = [str(c) if c else "" for c in row]
                header_row_idx = idx
                break

    if not headers:
        raise ParsingError(
            f"Could not detect column headers in the {file_type}. Expected columns like 'Date', 'Description', "
            "'Amount' (or 'Debit'/'Credit')."
        )

    # Detect column positions
    date_col = _find_column(headers, DATE_COLUMNS)
    desc_col = _find_column(headers, DESCRIPTION_COLUMNS)
    amount_col = _find_column(headers, AMOUNT_COLUMNS)
    debit_col = _find_column(headers, DEBIT_COLUMNS)
    credit_col = _find_column(headers, CREDIT_COLUMNS)

    if date_col is None:
        raise ParsingError(f"Could not find a 'Date' column in the {file_type}.")

    has_separate_debit_credit = debit_col is not None or credit_col is not None
    if not has_separate_debit_credit and amount_col is None:
        raise ParsingError(
            f"Could not find an 'Amount', 'Debit', or 'Credit' column in the {file_type}."
        )

    logger.info(
        "columns_detected",
        file_type=file_type,
        date_col=date_col,
        desc_col=desc_col,
        amount_col=amount_col,
        debit_col=debit_col,
        credit_col=credit_col,
        headers=headers,
    )

    # Parse data rows
    data_rows = rows[header_row_idx + 1 :]
    for row_num, row in enumerate(data_rows, start=header_row_idx + 2):
        if not row or all(not str(cell).strip() if cell else True for cell in row):
            continue

        row = [str(c) if c else "" for c in row]

        # Skip summary/footer rows
        row_text = " ".join(row).lower()
        if any(skip in row_text for skip in SKIP_KEYWORDS):
            continue

        try:
            # Parse date
            if date_col >= len(row):
                continue
            txn_date = _parse_date(row[date_col])
            if txn_date is None:
                continue  # Skip rows that don't have a valid date

            # Parse description
            description = ""
            if desc_col is not None and desc_col < len(row):
                description = row[desc_col].strip()
            if not description:
                # Fall back to concatenating non-date, non-amount columns
                skip_cols = {date_col, amount_col, debit_col, credit_col}
                desc_parts = [
                    row[i].strip()
                    for i in range(len(row))
                    if i not in skip_cols and row[i].strip()
                ]
                description = " ".join(desc_parts)

            if not description:
                description = "Unknown Transaction"

            # Parse amount
            txn_type = "DEBIT"
            amount = 0.0

            if has_separate_debit_credit:
                debit_amt = _clean_amount(row[debit_col]) if debit_col is not None and debit_col < len(row) else None
                credit_amt = _clean_amount(row[credit_col]) if credit_col is not None and credit_col < len(row) else None

                if debit_amt and debit_amt > 0:
                    amount = debit_amt
                    txn_type = "DEBIT"
                elif credit_amt and credit_amt > 0:
                    amount = credit_amt
                    txn_type = "CREDIT"
                else:
                    continue  # Skip rows with no amount
            else:
                if amount_col is not None and amount_col < len(row):
                    raw_amount = row[amount_col].strip()
                    parsed = _clean_amount(raw_amount)
                    if parsed is None:
                        continue
                    # Negative amounts are debits, positive are credits (or vice versa)
                    if raw_amount.startswith("-") or raw_amount.startswith("("):
                        txn_type = "DEBIT"
                    else:
                        txn_type = "CREDIT"
                    amount = parsed
                else:
                    continue

            # Build raw_data dict for the original row
            raw_data = {headers[i].strip(): row[i].strip() for i in range(min(len(headers), len(row)))}

            transactions.append(
                ParsedTransaction(
                    transaction_date=txn_date,
                    description=description,
                    amount=amount,
                    transaction_type=txn_type,
                    raw_data=raw_data,
                )
            )

        except Exception as e:
            errors.append(f"Row {row_num}: {e!s}")
            continue

    if not transactions:
        raise ParsingError(
            f"No transactions could be extracted from the {file_type}. "
            "Please check the file format and ensure it contains transaction data."
        )

    # Determine statement month/year from transaction dates
    dates = [t.transaction_date for t in transactions]
    most_common_month = max(set((d.year, d.month) for d in dates), key=lambda x: sum(1 for d in dates if d.year == x[0] and d.month == x[1]))

    # Heuristic for statements with a single Amount column:
    # Expenses (DEBIT) usually vastly outnumber incomes/payments (CREDIT).
    # If the parser initially marked positive amounts as CREDIT and negative as DEBIT,
    # and there are more CREDITs than DEBITs, it means the statement has positive expenses (like a CC statement).
    if not has_separate_debit_credit:
        credit_count = sum(1 for t in transactions if t.transaction_type == "CREDIT")
        debit_count = sum(1 for t in transactions if t.transaction_type == "DEBIT")
        if credit_count > debit_count:
            logger.info("heuristic_flip_types", credit_count=credit_count, debit_count=debit_count)
            for t in transactions:
                t.transaction_type = "DEBIT" if t.transaction_type == "CREDIT" else "CREDIT"

    result = ParseResult(
        transactions=transactions,
        statement_year=most_common_month[0],
        statement_month=most_common_month[1],
        errors=errors,
        metadata={
            "total_rows": len(data_rows),
            "parsed_transactions": len(transactions),
            "parse_errors": len(errors),
            "detected_headers": headers,
        },
    )

    logger.info(
        "table_parsed",
        file_type=file_type,
        transactions=len(transactions),
        month=f"{most_common_month[0]}-{most_common_month[1]:02d}",
        errors=len(errors),
    )

    return result


def parse_csv(file_content: Union[str, bytes], bank_name: Optional[str] = None) -> ParseResult:
    """Parse a CSV bank statement and extract transactions."""
    if isinstance(file_content, bytes):
        # Try UTF-8 first, then latin-1 as fallback
        try:
            file_content_str = file_content.decode("utf-8-sig")
        except UnicodeDecodeError:
            file_content_str = file_content.decode("latin-1")
    else:
        file_content_str = file_content
        
    # Check for specific bank parser
    parser = get_parser_by_name(bank_name)
    if not parser:
        parser = detect_parser_from_text(file_content_str[:5000]) # Use first 5000 chars for detection
        
    if parser:
        logger.info("using_specific_parser", format="csv", parser=parser.__name__)
        try:
            return parser.parse_csv(file_content)
        except Exception as e:
            logger.warning("specific_parser_failed_fallback_to_generic", error=str(e))

    reader = csv.reader(io.StringIO(file_content_str))
    rows = list(reader)
    return _parse_table(rows, "CSV")


def parse_pdf(file_bytes: bytes, bank_name: Optional[str] = None) -> ParseResult:
    """Parse a PDF bank statement using pdfplumber."""
    try:
        # Check for specific bank parser
        parser = get_parser_by_name(bank_name)
        if not parser:
            # Extract some text for detection
            sample_text = ""
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                if len(pdf.pages) > 0:
                    sample_text = pdf.pages[0].extract_text() or ""
            
            parser = detect_parser_from_text(sample_text)
            
        if parser:
            logger.info("using_specific_parser", format="pdf", parser=parser.__name__)
            try:
                return parser.parse_pdf(file_bytes)
            except Exception as e:
                logger.warning("specific_parser_failed_fallback_to_generic", error=str(e))
                
        all_rows = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            # 1. Try standard table extraction first
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row:
                            all_rows.append(row)
            
            try:
                if all_rows:
                    return _parse_table(all_rows, "PDF")
                else:
                    raise ParsingError("No tables extracted")
            except ParsingError:
                # 2. Text heuristic fallback
                transactions = []
                # Matches: "26MAY Description text 1,300.00" or "04/04/2026 Desc 100.00 CR"
                pattern = re.compile(r"^(\d{2}[A-Za-z]{3}|\d{2}/\d{2}/\d{2,4}|\d{2}-\d{2}-\d{2,4})\s+(.+?)\s+([\d,]+\.\d{2}(?:\s*(?:CR|DR))?)$", re.IGNORECASE)
                
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text:
                        continue
                    for line in text.split('\n'):
                        line = line.strip()
                        match = pattern.match(line)
                        if match:
                            date_str, desc, amt_str = match.groups()
                            
                            # Skip summary lines that happened to match the regex (e.g., balance lines)
                            if any(skip in desc.lower() for skip in SKIP_KEYWORDS):
                                continue

                            txn_date = _parse_date(date_str)
                            if not txn_date:
                                continue
                            
                            is_credit = "CR" in amt_str.upper()
                            amt = _clean_amount(amt_str.upper().replace("CR", "").replace("DR", ""))
                            if amt is None:
                                continue
                                
                            # If year is 1900 (missing year parsed), we can try to patch it to current year or statement year
                            if txn_date.year == 1900:
                                txn_date = txn_date.replace(year=datetime.now().year)

                            transactions.append(
                                ParsedTransaction(
                                    transaction_date=txn_date,
                                    description=desc.strip(),
                                    amount=amt,
                                    transaction_type="CREDIT" if is_credit else "DEBIT",
                                    raw_data={"raw_line": line}
                                )
                            )
                
                if not transactions:
                    raise ParsingError("Could not detect column headers or transaction rows in the PDF.")
                
                dates = [t.transaction_date for t in transactions]
                most_common_month = max(set((d.year, d.month) for d in dates), key=lambda x: sum(1 for d in dates if d.year == x[0] and d.month == x[1]))
                
                return ParseResult(
                    transactions=transactions,
                    statement_year=most_common_month[0],
                    statement_month=most_common_month[1],
                    metadata={"parsed_via": "text_heuristic", "total_transactions": len(transactions)}
                )

    except Exception as e:
        if isinstance(e, ParsingError):
            raise
        logger.exception("pdf_parse_error", error=str(e))
        raise ParsingError(f"Failed to read PDF file: {str(e)}")
