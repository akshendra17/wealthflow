import io
import re
from datetime import datetime
from typing import Union
import pdfplumber

from .base import BaseBankParser, ParseResult, ParsedTransaction
from . import register_parser
from app.core.exceptions import ParsingError

@register_parser("axis")
class AxisParser(BaseBankParser):
    @classmethod
    def detect(cls, text_content: str) -> bool:
        return "axis bank" in text_content.lower()
        
    @classmethod
    def parse_pdf(cls, file_bytes: bytes) -> ParseResult:
        transactions = []
        errors = []
        
        # Regex for Axis Bank Credit Card transaction line
        # Example: 15/06/2026 PLAYSTATION,SONY PSN MISC STORE 749.00 Dr 7.00 Cr
        # Sometimes Merchant Category is empty.
        # So we match Date, then everything until Amount + Dr/Cr + Cashback + Dr/Cr
        pattern = re.compile(
            r"^(\d{2}/\d{2}/\d{4})\s+"             # Date: DD/MM/YYYY
            r"(.+?)\s+"                            # Description & Merchant
            r"([\d,]+\.\d{2})\s+(Dr|Cr)\s+"        # Amount and Dr/Cr
            r"([\d,]+\.\d{2})\s+(Cr|Dr)$",         # Cashback and Cr/Dr
            re.IGNORECASE
        )
        
        statement_year, statement_month = None, None
        
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                # Try to extract the Statement Period end date (e.g. "17/05/2026 - 15/06/2026")
                if not statement_year:
                    period_match = re.search(r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/(\d{2})/(\d{4}))", text)
                    if period_match:
                        statement_month = int(period_match.group(3))
                        statement_year = int(period_match.group(4))
                        
                for line in text.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Stop if we hit Account Summary end or Reward points table
                    if "End of Statement" in line or "Reward Points Balance" in line:
                        break
                        
                    match = pattern.match(line)
                    if match:
                        date_str, desc_and_merchant, amt_str, dr_cr, cb_amt, cb_dr_cr = match.groups()
                        
                        try:
                            txn_date = datetime.strptime(date_str, "%d/%m/%Y").date()
                        except ValueError:
                            continue
                            
                        # Clean amount
                        amt_clean = float(amt_str.replace(",", ""))
                        if amt_clean == 0:
                            continue
                            
                        is_debit = (dr_cr.lower() == "dr")
                        txn_type = "DEBIT" if is_debit else "CREDIT"
                        
                        transactions.append(
                            ParsedTransaction(
                                transaction_date=txn_date,
                                description=desc_and_merchant.strip(),
                                amount=amt_clean,
                                transaction_type=txn_type,
                                raw_data={"raw_line": line}
                            )
                        )

        if not transactions:
            raise ParsingError("Could not extract any transactions from Axis Bank PDF.")
            
        if not statement_year or not statement_month:
            dates = [t.transaction_date for t in transactions]
            max_date = max(dates)
            statement_year = max_date.year
            statement_month = max_date.month
            
        return ParseResult(
            transactions=transactions,
            bank_name="axis",
            statement_year=statement_year,
            statement_month=statement_month,
            errors=errors,
            metadata={"parsed_via": "axis_pdf_parser", "total_transactions": len(transactions)}
        )
        
    @classmethod
    def parse_csv(cls, file_content: Union[str, bytes]) -> ParseResult:
        # Placeholder for Axis specific CSV parsing logic
        raise ParsingError("Axis specific CSV parsing not fully implemented yet.")
