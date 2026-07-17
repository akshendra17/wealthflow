"""Base class for bank statement parsers."""

from abc import ABC, abstractmethod
from typing import Optional, Union
from dataclasses import dataclass, field
from datetime import date
import re
import datetime

@dataclass
class ParsedTransaction:
    transaction_date: date
    description: str
    amount: float
    transaction_type: str  # "DEBIT" or "CREDIT"
    raw_data: dict = field(default_factory=dict)

@dataclass
class ParseResult:
    transactions: list[ParsedTransaction]
    bank_name: Optional[str] = None
    statement_month: Optional[int] = None
    statement_year: Optional[int] = None
    errors: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class BaseBankParser(ABC):
    """Abstract base class for all bank-specific parsers."""
    
    @classmethod
    @abstractmethod
    def detect(cls, text_content: str) -> bool:
        """Return True if the text content looks like it belongs to this bank."""
        pass
        
    @classmethod
    @abstractmethod
    def parse_pdf(cls, file_bytes: bytes) -> ParseResult:
        """Parse a PDF statement for this bank."""
        pass
        
    @classmethod
    @abstractmethod
    def parse_csv(cls, file_content: Union[str, bytes]) -> ParseResult:
        """Parse a CSV statement for this bank."""
        pass

    @staticmethod
    def _clean_amount(amount_str: str) -> Optional[float]:
        if not amount_str or not amount_str.strip():
            return None
        cleaned = re.sub(r"[^\d.\-]", "", amount_str.strip())
        if not cleaned or cleaned == "-" or cleaned == ".":
            return None
        try:
            return abs(float(cleaned))
        except ValueError:
            return None
            
    @staticmethod
    def _parse_date(date_str: str, formats: list[str]) -> Optional[date]:
        date_str = date_str.strip()
        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None
