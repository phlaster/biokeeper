from pydantic import BaseModel, Field, field_validator
from datetime import datetime

from schemas.users import UserBase
from schemas.common import validate_identifier

class QR(BaseModel):
    id: int
    unique_hex: str

class KitInfo(BaseModel):
    id: int
    unique_hex: str
    created_at: datetime
    updated_at: datetime
    status: str
    creator_id: int
    owner_id: int |  None
    owner: UserBase | None
    qrs: list[QR]

class MyKit(BaseModel):
    id: int

class KitRequest(BaseModel):
    kit_identifier : int | str

    @field_validator('kit_identifier', mode="before")
    def validate_kit_identifier(cls, v):
        return validate_identifier(v, 'kit_identifier must be either an integer or a string')


class SendKitRequest(BaseModel):
    new_owner_identifier: int | str

    @field_validator('new_owner_identifier', mode="before")
    def validate_new_owner_id(cls, v):
        return validate_identifier(v, 'new_owner_identifier must be either an integer or a string')

class CreateKitRequest(BaseModel):
    n_qrs : int

class KitsCreatedByAdminResponse(BaseModel):
    id: int
    n_qrs: int
    unique_hex: str
    created_at: datetime
    owner_id: int | None
    owner_name: str | None