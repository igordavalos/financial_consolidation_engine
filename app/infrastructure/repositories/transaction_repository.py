from .base import BaseRepository
from app.infrastructure.models import Transaction


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session):
        super().__init__(session, Transaction)
