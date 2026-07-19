from typing import Union
from .base import BaseBankParser, ParseResult, ParsedTransaction
from . import register_parser
from app.core.exceptions import ParsingError

@register_parser("canara")
class CanaraParser(BaseBankParser):
    @classmethod
    def detect(cls, text_content: str) -> bool:
        lower_text = text_content.lower()
        return "canara bank" in lower_text
        
    @classmethod
    def parse_pdf(cls, file_bytes: bytes) -> ParseResult:
        raise ParsingError("Canara specific PDF parsing not fully implemented yet.")
        
    @classmethod
    def parse_csv(cls, file_content: Union[str, bytes]) -> ParseResult:
        raise ParsingError("Canara specific CSV parsing not fully implemented yet.")
