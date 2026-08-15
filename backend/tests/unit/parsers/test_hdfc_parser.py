"""Unit tests for HDFC statement parser strategies."""
from datetime import date
from pathlib import Path

import pytest

from app.core.exceptions import ParsingError
from app.core.services.parsers.hdfc import (
    _CC_PDF_ERROR,
    _CSV_ERROR,
    _extract_period,
    parse_millennia_cc_text,
    parse_regalia_cc_text,
    parse_structural_heuristic,
    HDFCParser,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class TestRegaliaStrategy:
    def test_parses_regalia_excerpt(self):
        text = _load_fixture("hdfc_regalia_cc_excerpt.txt")
        txns = parse_regalia_cc_text(text)

        assert len(txns) == 6

    def test_credit_payment_classified_correctly(self):
        text = _load_fixture("hdfc_regalia_cc_excerpt.txt")
        txns = parse_regalia_cc_text(text)

        payment = next(t for t in txns if t.amount == 22457.0)
        assert payment.transaction_type == "CREDIT"
        assert "BPPY CC PAYMENT" in payment.description

    def test_debit_purchase_classified_correctly(self):
        text = _load_fixture("hdfc_regalia_cc_excerpt.txt")
        txns = parse_regalia_cc_text(text)

        netflix = next(t for t in txns if t.amount == 649.0)
        assert netflix.transaction_type == "DEBIT"
        assert "NETFLIXMUMBAI" in netflix.description

    def test_multiline_description_with_ref(self):
        text = _load_fixture("hdfc_regalia_cc_excerpt.txt")
        txns = parse_regalia_cc_text(text)

        igst = next(t for t in txns if t.amount == 90.54)
        assert igst.transaction_date == date(2026, 6, 19)
        assert "IGST-VPS2717151210984" in igst.description
        assert "09999999980619014462723)" in igst.description

    def test_inline_description_on_same_line(self):
        text = _load_fixture("hdfc_regalia_cc_excerpt.txt")
        txns = parse_regalia_cc_text(text)

        emi = next(t for t in txns if t.amount == 9375.0)
        assert "OFFUS EMI" in emi.description
        assert emi.transaction_type == "DEBIT"


class TestMillenniaStrategy:
    def test_parses_millennia_excerpt(self):
        text = _load_fixture("hdfc_millennia_cc_excerpt.txt")
        txns = parse_millennia_cc_text(text)

        assert len(txns) == 4

    def test_credit_with_cr_suffix(self):
        text = _load_fixture("hdfc_millennia_cc_excerpt.txt")
        txns = parse_millennia_cc_text(text)

        payment = next(t for t in txns if "PAYMENT RECEIVED" in t.description)
        assert payment.transaction_type == "CREDIT"
        assert "PAYMENT RECEIVED" in payment.description

    def test_debit_without_cr_suffix(self):
        text = _load_fixture("hdfc_millennia_cc_excerpt.txt")
        txns = parse_millennia_cc_text(text)

        purchase = next(t for t in txns if t.amount == 1299.0)
        assert purchase.transaction_type == "DEBIT"


class TestPeriodExtraction:
    def test_extracts_statement_date_with_comma(self):
        text = "Statement Date 19 Jul, 2026\nBilling Period 20 Jun, 2026 - 19 Jul, 2026"
        year, month = _extract_period(text)
        assert year == 2026
        assert month == 7

    def test_billing_period_end_date(self):
        text = "Billing Period 20 Jun, 2026 - 19 Jul, 2026"
        year, month = _extract_period(text)
        assert year == 2026
        assert month == 7


class TestStructuralHeuristic:
    def test_parses_regalia_lines_as_fallback(self):
        text = _load_fixture("hdfc_regalia_cc_excerpt.txt")
        txns = parse_structural_heuristic(text)
        assert len(txns) >= 3


class TestErrorMessages:
    def test_invalid_pdf_raises_parsing_error(self):
        with pytest.raises(ParsingError):
            HDFCParser.parse_pdf(b"%PDF-1.4\ninvalid")

    def test_cc_pdf_error_message_mentions_credit_card(self):
        assert "credit card" in _CC_PDF_ERROR.lower()

    def test_csv_error_message_mentions_savings(self):
        assert "savings" in _CSV_ERROR.lower() or "csv" in _CSV_ERROR.lower()

    def test_empty_csv_raises_csv_error(self):
        with pytest.raises(ParsingError) as exc:
            HDFCParser.parse_csv("Date,Narration,Debit,Credit\n")

        assert "Could not extract" in str(exc.value)
