"""Parser registry for all bank statement parsers."""

from typing import Type, Optional
import structlog
from .base import BaseBankParser

logger = structlog.get_logger()

# Registry mapping bank_name to its parser class
PARSER_REGISTRY: dict[str, Type[BaseBankParser]] = {}

def register_parser(bank_name: str):
    """Decorator to register a parser class for a specific bank."""
    def decorator(cls: Type[BaseBankParser]):
        PARSER_REGISTRY[bank_name.lower()] = cls
        return cls
    return decorator

def get_parser_by_name(bank_name: str) -> Optional[Type[BaseBankParser]]:
    """Get a registered parser by explicitly providing the bank name."""
    if not bank_name:
        return None
    return PARSER_REGISTRY.get(bank_name.lower().strip())

def detect_parser_from_text(text_content: str) -> Optional[Type[BaseBankParser]]:
    """Iterate through all registered parsers and ask them to detect if they match the text."""
    for bank_name, parser_cls in PARSER_REGISTRY.items():
        try:
            if parser_cls.detect(text_content):
                logger.info("bank_parser_detected", bank=bank_name)
                return parser_cls
        except Exception as e:
            logger.warning("parser_detect_error", bank=bank_name, error=str(e))
    return None

# Import all parsers here so their decorators run
from . import hdfc
from . import axis
