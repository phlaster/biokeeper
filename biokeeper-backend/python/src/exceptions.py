from typing import Any
from fastapi import HTTPException, status

class NotFoundException(Exception):
    pass

class NoUserException(NotFoundException):
    pass

class NoSampleException(NotFoundException):
    pass

class NoQrCodeException(NotFoundException):
    pass

class NoResearchException(NotFoundException):
    pass

class NoKitException(NotFoundException):
    pass

class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, msg: str, data: dict[str, Any] = None):
        super().__init__(status_code=status_code, detail={"msg": msg, "data": data})

class HTTPForbiddenException(CustomHTTPException):
    def __init__(self, msg: str, data: dict[str, Any] = None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, msg=msg, data=data)

class HTTPNotFoundException(CustomHTTPException):
    def __init__(self, msg: str, data: dict[str, Any] = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, msg=msg, data=data)

class HTTPConflictException(CustomHTTPException):
    def __init__(self, msg: str, data: dict[str, Any] = None):
        super().__init__(status_code=status.HTTP_409_CONFLICT, msg=msg, data=data)

class HTTPNotEnoughPermissionsException(HTTPException):
        status_code=status.HTTP_403_FORBIDDEN
        detail = "Not enough permissions"
        def __init__(self, detail, *args, **kwargs):
            super().__init__(status_code=self.status_code, detail=detail, *args, **kwargs)

