from pydantic import BaseModel, ValidationError
import datetime

class Role(BaseModel):
    id  : int
    name: str
    info: str

class TokenPayload(BaseModel):
    id: int
    username: str
    role : Role
    exp: datetime.datetime

def validate_identifier(v, message=None):
    if isinstance(v, int):
        return v
    elif isinstance(v, str):
        if v.isdigit():
            return int(v)
        else:
            return v
    raise ValidationError(message)