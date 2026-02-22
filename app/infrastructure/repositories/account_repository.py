from .base import BaseRepository
from app.infrastructure.models import Account


class AccountRepository(BaseRepository[Account]):
    def __init__(self, session):
        super().__init__(session, Account)
