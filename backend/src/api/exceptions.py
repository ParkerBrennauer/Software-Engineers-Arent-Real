class AppException(Exception):

    def __init__(self, detail: str, status_code: int=400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)

class NotFoundError(AppException):

    def __init__(self, detail: str):
        super().__init__(detail, status_code=404)

class ValidationError(AppException):

    def __init__(self, detail: str):
        super().__init__(detail, status_code=400)

class ConflictError(AppException):

    def __init__(self, detail: str):
        super().__init__(detail, status_code=409)

class UnauthorizedError(AppException):

    def __init__(self, detail: str):
        super().__init__(detail, status_code=401)

class ForbiddenError(AppException):

    def __init__(self, detail: str):
        super().__init__(detail, status_code=403)
