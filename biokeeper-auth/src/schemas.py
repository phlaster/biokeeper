from datetime import datetime
from typing_extensions import Self
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class RoleBase(BaseModel):
    id  : int
    name: str

class Role(RoleBase):
    info: str | None = None

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=16)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field()
    password2: str = Field()

    @field_validator('password')
    def password_validation(cls, v):
        errors = []
        if len(v) < 8 or len(v) > 64:
            errors.append("Password must be between 8 to 64 characters long.")
        if not any(char.isdigit() for char in v):
            errors.append("Password must contain at least one digit.")
        if not any(char.islower() for char in v):
            errors.append("Password must contain at least one lowercase letter.")
        if not any(char.isupper() for char in v):
            errors.append("Password must contain at least one uppercase letter.")
        if not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in v):
            errors.append("Password must contain at least one special character.")
        if errors:
            raise ValueError(" ".join(errors))
        return v
    
    @model_validator(mode='after')
    def passwords_match(self) -> Self:
        pw1 = self.password
        pw2 = self.password2
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('Passwords do not match')
        return self
    

class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=16)
    password: str = Field()



class UserResponse(UserBase):
    id: int
    role : Role

    class Config:
        from_attributes = True


class UserCreatedMqMessage(BaseModel):
    id: int
    username: str
    


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'Bearer'

class UpdateTokenResponse(BaseModel):
    access_token: str
    token_type: str = 'Bearer'

class RevokeTokenRequest(BaseModel):
    sessionId: int

class LogoutRequest(BaseModel):
    refresh_token: str

class RefreshRequest(BaseModel):
    refresh_token: str

class CreatedAtResponse(BaseModel):
    created_at: datetime


class SessionBase(BaseModel):
    id: int
    user_id: int
    device_ip: str
    device_info: str
    created_at: datetime
    updated_at: datetime

class MySessionsResponse(BaseModel):
    sessions: list[SessionBase] = []

