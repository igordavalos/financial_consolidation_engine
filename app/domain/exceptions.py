class DomainError(Exception):
    """Base exception for domain errors."""

    def __init__(self, message: str = "A domain error occurred"):
        self.message = message
        super().__init__(self.message)


class EntityNotFoundError(DomainError):
    """Raised when a requested entity is not found."""

    def __init__(self, entity_type: str, entity_id: str):
        super().__init__(f"{entity_type} with id '{entity_id}' not found")
        self.entity_type = entity_type
        self.entity_id = entity_id


class DuplicateEntityError(DomainError):
    """Raised when attempting to create a duplicate entity."""

    def __init__(self, entity_type: str, identifier: str):
        super().__init__(f"{entity_type} '{identifier}' already exists")


class ValidationError(DomainError):
    """Raised when domain validation fails."""

    def __init__(self, field: str, reason: str):
        super().__init__(f"Validation error on '{field}': {reason}")
        self.field = field
        self.reason = reason


class ConsolidationError(DomainError):
    """Raised when financial consolidation fails."""

    pass


class InsufficientDataError(DomainError):
    """Raised when there is not enough data for an operation."""

    pass
