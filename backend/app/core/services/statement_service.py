"""Statement service — orchestrates upload, parsing, categorization, and storage."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Optional

import structlog
from sqlalchemy import delete, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, UnsupportedFormatError
from app.core.services.categorizer import categorize_transaction
from app.core.services.statement_parser import ParseResult, parse_csv, parse_pdf
from app.db.models.monthly_summary import MonthlySummary
from app.db.models.statement import Statement
from app.db.models.transaction import Transaction

logger = structlog.get_logger()


class StatementService:
    """Handles statement upload, parsing, and transaction management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_and_parse(
        self,
        filename: str,
        file_content: bytes,
        user_id: uuid.UUID,
        bank_name: Optional[str] = None,
    ) -> Statement:
        """Upload a statement file, parse it, categorize transactions, and store everything."""
        # Validate file type
        file_ext = Path(filename).suffix.lower()
        if file_ext not in {".csv", ".pdf"}:
            raise UnsupportedFormatError(file_ext)

        # Do not save the uploaded file to disk per user request, just parse it.

        # Parse the file
        if file_ext == ".pdf":
            result: ParseResult = parse_pdf(file_content, bank_name=bank_name)
        else:
            result: ParseResult = parse_csv(file_content, bank_name=bank_name)

        # Create the statement record
        statement = Statement(
            user_id=user_id,
            original_filename=filename,
            file_type=file_ext.upper().lstrip("."),
            bank_name=result.bank_name or bank_name,
            statement_month=result.statement_month,
            statement_year=result.statement_year,
            raw_metadata=result.metadata,
            total_transactions=len(result.transactions),
        )

        total_debit = 0.0
        total_credit = 0.0

        # Create transaction records with categorization
        for parsed_txn in result.transactions:
            category = categorize_transaction(parsed_txn.description)

            txn = Transaction(
                statement_id=statement.id,
                transaction_date=parsed_txn.transaction_date,
                description=parsed_txn.description,
                amount=parsed_txn.amount,
                transaction_type=parsed_txn.transaction_type,
                category=category,
                raw_data=parsed_txn.raw_data,
            )
            statement.transactions.append(txn)

            if parsed_txn.transaction_type == "DEBIT":
                total_debit += parsed_txn.amount
            else:
                total_credit += parsed_txn.amount

        statement.total_debit = total_debit
        statement.total_credit = total_credit

        self.db.add(statement)
        await self.db.flush()
        await self.db.refresh(statement)

        # Rebuild monthly summaries for the affected month
        if result.statement_year and result.statement_month:
            await self._rebuild_monthly_summaries(
                result.statement_year, result.statement_month, user_id
            )

        await self.db.commit()

        logger.info(
            "statement_processed",
            statement_id=str(statement.id),
            user_id=str(user_id),
            transactions=len(result.transactions),
            debit=total_debit,
            credit=total_credit,
        )

        return statement

    async def list_statements(self, user_id: uuid.UUID) -> list[Statement]:
        """List all uploaded statements for a user, ordered by upload date descending."""
        result = await self.db.execute(
            select(Statement)
            .where(Statement.user_id == user_id)
            .order_by(Statement.uploaded_at.desc())
        )
        return list(result.scalars().all())

    async def get_statement(
        self, statement_id: uuid.UUID, user_id: uuid.UUID
    ) -> Statement:
        """Get a single statement by ID, scoped to the user."""
        result = await self.db.execute(
            select(Statement).where(
                Statement.id == statement_id,
                Statement.user_id == user_id,
            )
        )
        statement = result.scalar_one_or_none()
        if not statement:
            raise NotFoundError("Statement", str(statement_id))
        return statement

    async def delete_statement(
        self, statement_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        """Delete a statement and all its transactions (cascade)."""
        statement = await self.get_statement(statement_id, user_id)
        year = statement.statement_year
        month = statement.statement_month

        await self.db.delete(statement)
        await self.db.flush()

        # Rebuild summaries for the affected month
        if year and month:
            await self._rebuild_monthly_summaries(year, month, user_id)

        await self.db.commit()
        logger.info("statement_deleted", statement_id=str(statement_id))

    async def delete_all_statements(self, user_id: uuid.UUID) -> None:
        """Delete all statements, transactions, and monthly summaries for a user."""
        await self.db.execute(
            delete(Statement).where(Statement.user_id == user_id)
        )
        await self.db.execute(
            delete(MonthlySummary).where(MonthlySummary.user_id == user_id)
        )
        await self.db.flush()
        await self.db.commit()
        logger.info("all_statements_deleted", user_id=str(user_id))

    async def _rebuild_monthly_summaries(
        self, year: int, month: int, user_id: uuid.UUID
    ) -> None:
        """Rebuild the monthly_summaries table for a given month and user.

        Deletes existing summaries for the month and re-aggregates from transactions.
        """
        # Delete existing summaries for this month and user
        await self.db.execute(
            delete(MonthlySummary).where(
                MonthlySummary.year == year,
                MonthlySummary.month == month,
                MonthlySummary.user_id == user_id,
            )
        )

        # Aggregate transactions for this month (debits only for expense tracking)
        # Join through Statement to filter by user_id
        result = await self.db.execute(
            select(
                Transaction.category,
                func.sum(Transaction.amount).label("total_amount"),
                func.count(Transaction.id).label("transaction_count"),
                func.avg(Transaction.amount).label("avg_transaction"),
                func.max(Transaction.amount).label("max_transaction"),
            )
            .join(Statement, Transaction.statement_id == Statement.id)
            .where(
                Statement.user_id == user_id,
                extract("year", Transaction.transaction_date) == year,
                extract("month", Transaction.transaction_date) == month,
                Transaction.transaction_type == "DEBIT",
            )
            .group_by(Transaction.category)
        )

        for row in result.all():
            summary = MonthlySummary(
                user_id=user_id,
                year=year,
                month=month,
                category=row.category,
                total_amount=float(row.total_amount or 0),
                transaction_count=row.transaction_count,
                avg_transaction=float(row.avg_transaction or 0),
                max_transaction=float(row.max_transaction or 0),
            )
            self.db.add(summary)

        await self.db.flush()
        logger.info("monthly_summaries_rebuilt", year=year, month=month)
