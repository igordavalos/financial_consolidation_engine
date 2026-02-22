from __future__ import annotations
import uuid
from datetime import date
from decimal import Decimal
from app.domain.models.account import Account, AccountCategory, AccountType
from app.domain.models.company import Company, Currency, Subsidiary
from app.domain.models.transaction import Transaction

PARENT_ENTITY_ID = uuid.UUID('00000000-0000-0000-0000-000000000001')
SUB_EU_ENTITY_ID = uuid.UUID('00000000-0000-0000-0000-000000000002')
ACCT_REVENUE_ID = uuid.UUID('10000000-0000-0000-0000-000000000001')
ACCT_COGS_ID = uuid.UUID('10000000-0000-0000-0000-000000000003')
ACCT_SALARIES_ID = uuid.UUID('10000000-0000-0000-0000-000000000004')
ACCT_RENT_ID = uuid.UUID('10000000-0000-0000-0000-000000000005')
ACCT_EU_REVENUE_ID = uuid.UUID('20000000-0000-0000-0000-000000000001')
ACCT_EU_COGS_ID = uuid.UUID('20000000-0000-0000-0000-000000000002')

def create_sample_company():
    company = Company(id=PARENT_ENTITY_ID, name='Acme Corp', base_currency=Currency.USD)
    eu_sub = Subsidiary(id=SUB_EU_ENTITY_ID, name='Acme EU', currency=Currency.EUR)
    company.add_subsidiary(eu_sub)
    return company

def create_sample_accounts():
    return [
        Account(id=ACCT_REVENUE_ID, code='4000', name='Revenue', account_type=AccountType.REVENUE, category=AccountCategory.OPERATING_REVENUE, entity_id=PARENT_ENTITY_ID),
        Account(id=ACCT_COGS_ID, code='5000', name='COGS', account_type=AccountType.EXPENSE, category=AccountCategory.COST_OF_GOODS_SOLD, entity_id=PARENT_ENTITY_ID),
        Account(id=ACCT_SALARIES_ID, code='6100', name='Salaries', account_type=AccountType.EXPENSE, category=AccountCategory.OPERATING_EXPENSE, entity_id=PARENT_ENTITY_ID),
        Account(id=ACCT_RENT_ID, code='6200', name='Rent', account_type=AccountType.EXPENSE, category=AccountCategory.OPERATING_EXPENSE, entity_id=PARENT_ENTITY_ID),
        Account(id=ACCT_EU_REVENUE_ID, code='4000', name='Revenue', account_type=AccountType.REVENUE, category=AccountCategory.OPERATING_REVENUE, entity_id=SUB_EU_ENTITY_ID),
        Account(id=ACCT_EU_COGS_ID, code='5000', name='COGS', account_type=AccountType.EXPENSE, category=AccountCategory.COST_OF_GOODS_SOLD, entity_id=SUB_EU_ENTITY_ID),
    ]

def create_sample_transactions():
    return [
        Transaction(account_id=ACCT_REVENUE_ID, entity_id=PARENT_ENTITY_ID, transaction_date=date(2026, 1, 31), amount=Decimal('500000'), currency='USD', description='Revenue'),
        Transaction(account_id=ACCT_COGS_ID, entity_id=PARENT_ENTITY_ID, transaction_date=date(2026, 1, 31), amount=Decimal('200000'), currency='USD', description='COGS'),
        Transaction(account_id=ACCT_SALARIES_ID, entity_id=PARENT_ENTITY_ID, transaction_date=date(2026, 1, 31), amount=Decimal('300000'), currency='USD', description='Salaries'),
        Transaction(account_id=ACCT_EU_REVENUE_ID, entity_id=SUB_EU_ENTITY_ID, transaction_date=date(2026, 1, 31), amount=Decimal('200000'), currency='EUR', description='Revenue'),
    ]
