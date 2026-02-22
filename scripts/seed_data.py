"""Create database tables and insert minimal seed data for local development."""
import asyncio
from decimal import Decimal
from datetime import date

from sqlalchemy import text

from app.infrastructure.database import AsyncSessionLocal, init_db

# Import enums para usar valores válidos

# Import Account and Transaction ONLY from infrastructure.models
from app.infrastructure.models import Account, Transaction
# Import enums ONLY from domain.models.account
from app.domain.models.account import AccountCategory, AccountType


async def seed() -> None:
    await init_db()
    async with AsyncSessionLocal() as session:
        # Always clear tables before seeding to avoid legacy/invalid data
        await session.execute(text("TRUNCATE transactions, accounts RESTART IDENTITY CASCADE;"))
        await session.commit()

        # Usar enums para evitar errores de typo
        a1 = Account(
            code="4000",
            name="SaaS Revenue",
            category=str(AccountCategory.OPERATING_REVENUE.value),
            account_type=str(AccountType.REVENUE.value)
        )
        a2 = Account(
            code="6000",
            name="COGS",
            category=str(AccountCategory.COST_OF_GOODS_SOLD.value),
            account_type=str(AccountType.EXPENSE.value)
        )
        session.add_all([a1, a2])
        await session.flush()

        t1 = Transaction(account_id=a1.id, date=date.today(), amount=Decimal("10000.00"), description="Monthly subscription")
        t2 = Transaction(account_id=a2.id, date=date.today(), amount=Decimal("3000.00"), description="Hosting costs")
        session.add_all([t1, t2])

        await session.commit()
        # Print inserted values for verification
        print(f"Seed: inserted accounts (in-memory): {a1.code} {a1.category} {a1.account_type}, {a2.code} {a2.category} {a2.account_type}")

        # Query DB directly to show what was actually stored
        result = await session.execute(text("SELECT id, code, name, category, account_type FROM accounts;"))
        rows = result.fetchall()
        print("Seed: DB values after insert:")
        for row in rows:
            print(dict(row._mapping))


if __name__ == "__main__":
    asyncio.run(seed())
