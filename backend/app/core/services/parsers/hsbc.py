from typing import Union
from .base import BaseBankParser, ParseResult, ParsedTransaction
from . import register_parser
from app.core.exceptions import ParsingError

@register_parser("hsbc")
class HSBCParser(BaseBankParser):
    @classmethod
    def detect(cls, text_content: str) -> bool:
        lower_text = text_content.lower()
        return "hsbc" in lower_text or "hongkong and shanghai banking corporation" in lower_text
        
    @classmethod
    def parse_pdf(cls, file_bytes: bytes) -> ParseResult:
        raise ParsingError("HSBC specific PDF parsing not fully implemented yet.")
        
    @classmethod
    def parse_csv(cls, file_content: Union[str, bytes]) -> ParseResult:
        raise ParsingError("HSBC specific CSV parsing not fully implemented yet.")
