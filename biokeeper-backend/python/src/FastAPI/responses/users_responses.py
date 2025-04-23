from pydantic import Field
from responses.base import BasicConflictResponse, BasicNotFoundResponse, BasicForbiddenResponse

class UserNotFoundResponse(BasicNotFoundResponse):
    msg: str = Field(..., example="User not found")
    data: dict | None = Field(..., example={'user_identifier': 5})