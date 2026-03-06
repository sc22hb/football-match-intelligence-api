"""shared service-level exceptions for business logic."""

class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class ServiceValidationError(Exception):
    pass
