"""Accounts endpoints (placeholder for future database integration)."""

import uuid

from fastapi import APIRouter, HTTPException, status

from app.api.v1.schemas import AccountCreate, AccountListResponse, AccountResponse, AccountUpdate
from app.api.constants import INVALID_ID
from app.infrastructure.database import AsyncSessionLocal
from app.infrastructure.repositories.account_repository import AccountRepository

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get(
    "",
    response_model=AccountListResponse,
    summary="List all accounts",
    description="Retrieve a list of all accounts",
)
async def list_accounts() -> AccountListResponse:
    """List all accounts from the database."""
    async with AsyncSessionLocal() as session:
        repo = AccountRepository(session)
        items = await repo.list()
        accounts = []
        from app.domain.models.account import AccountCategory, AccountType
        for a in items:
                aid = a.id
                # Convert DB string to Enum for validation
                category = a.category
                account_type = a.account_type
                try:
                    category_enum = AccountCategory(category)
                except Exception:
                    category_enum = category
                try:
                    account_type_enum = AccountType(account_type)
                except Exception:
                    account_type_enum = account_type
                accounts.append(
                    AccountResponse(
                        id=uuid.UUID(int=int(aid)),
                        code=str(a.code),
                        name=str(a.name),
                        category=category_enum,
                        account_type=account_type_enum,
                        description=a.description if hasattr(a, "description") else None,
                    )
                )
        return AccountListResponse(accounts=accounts, total=len(accounts))


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
    description="Create a new account",
)
async def create_account(account: AccountCreate) -> AccountResponse:
    """Create a new account in the database."""
    async with AsyncSessionLocal() as session:
        repo = AccountRepository(session)
        db_obj = await repo.create(account.model_dump())
        dbid = db_obj.id
        from app.domain.models.account import AccountCategory, AccountType
        category = db_obj.category
        account_type = db_obj.account_type
        try:
            category_enum = AccountCategory(category)
        except Exception:
            category_enum = category
        try:
            account_type_enum = AccountType(account_type)
        except Exception:
            account_type_enum = account_type
        return AccountResponse(
            id=uuid.UUID(int=int(dbid)),
            code=str(db_obj.code),
            name=str(db_obj.name),
            category=category_enum,
            account_type=account_type_enum,
            description=db_obj.description if hasattr(db_obj, "description") else None,
        )


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Get account by ID",
    description="Retrieve a single account by ID",
)
async def get_account(account_id: str) -> AccountResponse:
    """Retrieve a single account by ID."""
    try:
        uid = uuid.UUID(account_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_ID) from None
    int_id = uid.int
    async with AsyncSessionLocal() as session:
        repo = AccountRepository(session)
        db_obj = await repo.get(int_id)
        if not db_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        dbid = db_obj.id
        from app.domain.models.account import AccountCategory, AccountType
        category = db_obj.category
        account_type = db_obj.account_type
        try:
            category_enum = AccountCategory(category)
        except Exception:
            category_enum = category
        try:
            account_type_enum = AccountType(account_type)
        except Exception:
            account_type_enum = account_type
        return AccountResponse(
            id=uuid.UUID(int=int(dbid)),
            code=str(db_obj.code),
            name=str(db_obj.name),
            category=category_enum,
            account_type=account_type_enum,
            description=db_obj.description if hasattr(db_obj, "description") else None,
        )


@router.put(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Update an account",
    description="Update an existing account",
)
async def update_account(account_id: str, account: AccountUpdate) -> AccountResponse:
    """Update an existing account."""
    try:
        uid = uuid.UUID(account_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_ID) from None
    int_id = uid.int
    async with AsyncSessionLocal() as session:
        repo = AccountRepository(session)
        db_obj = await repo.get(int_id)
        if not db_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        updated = await repo.update(db_obj, account.model_dump(exclude_none=True))
        uidb = updated.id
        from app.domain.models.account import AccountCategory, AccountType
        category = updated.category
        account_type = updated.account_type
        try:
            category_enum = AccountCategory(category)
        except Exception:
            category_enum = category
        try:
            account_type_enum = AccountType(account_type)
        except Exception:
            account_type_enum = account_type
        return AccountResponse(
            id=uuid.UUID(int=int(uidb)),
            code=str(updated.code),
            name=str(updated.name),
            category=category_enum,
            account_type=account_type_enum,
            description=updated.description if hasattr(updated, "description") else None,
        )


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an account",
    description="Delete an account",
)
async def delete_account(account_id: str) -> None:
    """Delete an account by ID."""
    try:
        uid = uuid.UUID(account_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_ID) from None
    int_id = uid.int
    async with AsyncSessionLocal() as session:
        repo = AccountRepository(session)
        obj = await repo.delete(int_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return None
