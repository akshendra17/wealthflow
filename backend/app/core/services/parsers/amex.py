from typing import Union
from .base import BaseBankParser, ParseResult, ParsedTransaction
from . import register_parser
from app.core.exceptions import ParsingError

@register_parser("amex")
class AmexParser(BaseBankParser):
    @classmethod
    def detect(cls, text_content: str) -> bool:
        lower_text = text_content.lower()
        return "american express" in lower_text or "amex" in lower_text
        
    @classmethod
    def parse_pdf(cls, file_bytes: bytes) -> ParseResult:
        raise ParsingError("Amex specific PDF parsing not fully implemented yet.")
        
    @classmethod
    def parse_csv(cls, file_content: Union[str, bytes]) -> ParseResult:
        raise ParsingError("Amex specific CSV parsing not fully implemented yet.")
