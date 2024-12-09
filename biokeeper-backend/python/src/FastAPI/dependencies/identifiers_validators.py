from fastapi import HTTPException, Path, status
from pydantic import ValidationError
from schemas.common import validate_identifier

async def user_identifier_validator_dependency(user_identifier: int | str = Path(...)):
    try:
        user_identifier = validate_identifier(user_identifier)
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{user_identifier} must be int or str")
    return user_identifier

async def research_identifier_validator_dependency(research_identifier: int | str = Path(...)):
    try:
        research_identifier = validate_identifier(research_identifier)
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{research_identifier} must be int or str")
    return research_identifier

async def kit_identifier_validator_dependency(kit_identifier: int | str = Path(...)):
    try:
        kit_identifier = validate_identifier(kit_identifier)
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{kit_identifier} must be int or str")
    return kit_identifier

async def qr_identifier_validator_dependency(qr_identifier: int | str = Path(...)):
    try:
        qr_identifier = validate_identifier(qr_identifier)
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{qr_identifier} must be int or str")
    return qr_identifier