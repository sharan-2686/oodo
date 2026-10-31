from typing import Any, Optional


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class BadRequestError(AppException):
    def __init__(
        self,
        message: str = "Bad request",
        code: str = "BAD_REQUEST",
        details: Optional[Any] = None,
    ):
        super().__init__(message, code=code, status_code=400, details=details)


class UnauthorizedError(AppException):
    def __init__(
        self,
        message: str = "Authentication required or invalid credentials",
        code: str = "UNAUTHORIZED",
        details: Optional[Any] = None,
    ):
        super().__init__(message, code=code, status_code=401, details=details)


class ForbiddenError(AppException):
    def __init__(
        self,
        message: str = "You do not have permission to perform this action",
        code: str = "FORBIDDEN",
        details: Optional[Any] = None,
    ):
        super().__init__(message, code=code, status_code=403, details=details)


class NotFoundError(AppException):
    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        details: Optional[Any] = None,
    ):
        super().__init__(message, code=code, status_code=404, details=details)


class ConflictError(AppException):
    def __init__(
        self,
        message: str = "Resource conflict or duplicate record",
        code: str = "CONFLICT",
        details: Optional[Any] = None,
    ):
        super().__init__(message, code=code, status_code=409, details=details)


class UnprocessableEntityError(AppException):
    def __init__(
        self,
        message: str = "Validation failed",
        code: str = "UNPROCESSABLE_ENTITY",
        details: Optional[Any] = None,
    ):
        super().__init__(message, code=code, status_code=422, details=details)

