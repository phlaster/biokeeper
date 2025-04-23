from pydantic import BaseModel, Field, field_validator
from datetime import datetime

from schemas.common import validate_identifier

class UserBase(BaseModel):
    id: int
    name: str

class UserResponse(UserBase):
    status: int
    created_at: datetime
    updated_at: datetime
    n_samples_collected: int

class GetUserRequest(BaseModel):
    user_identifier : str | int

    @field_validator('user_identifier', mode="before")
    def validate_user_identifier(cls, v):
        return validate_identifier(v, 'user_identifier must be either an integer or a string')