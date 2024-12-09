
from fastapi.routing import APIRouter
from pydantic import ValidationError
from db_manager import DBM
from fastapi import Body, Depends, HTTPException, Path, status
from typing import Annotated, Any
from fastapi.responses import JSONResponse
from exceptions import NoUserException, HTTPNotFoundException
from schemas.common import TokenPayload
from schemas.users import GetUserRequest, UserResponse
from schemas.kits import KitsCreatedByAdminResponse, MyKit
from schemas.samples import MySample
from schemas.researches import MyResearch, ResearchesCreatedByAdminResponse
from utils import get_admin, get_current_user

from dependencies.identifiers_validators import user_identifier_validator_dependency

from responses import users_responses
from responses.base import generate_responses

router = APIRouter()

@router.get('/users', response_model=list[UserResponse], tags=['users'])
def get_users(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    users = list(DBM.users.get_all().values())
    return JSONResponse(status_code=status.HTTP_200_OK, content=users)


    

@router.get('/users/{user_identifier}', response_model=UserResponse, 
            tags=['users'],
            responses=generate_responses(
                users_responses.UserNotFoundResponse
            )
        )
def get_user_by_identifier(token_payload: Annotated[TokenPayload, Depends(get_current_user)], user_identifier: Annotated[str, Depends(user_identifier_validator_dependency)]):
    """
    Returns user information for the specified user_id.
    """
    try:
        dbm_user = DBM.users.get_info(user_identifier)
    except NoUserException:
        raise HTTPNotFoundException(msg=f"User not found",data={'user_identifier': user_identifier})
    return dbm_user

@router.get('/me/kits', response_model=list[MyKit], tags=['users'])
def get_user_kits(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content=DBM.kits.get_kits_by_user_identifier(token_payload.id))

@router.get('/me/samples', response_model=list[MySample], tags=['users'])
def get_user_samples(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content=DBM.samples.get_samples_by_user_identifier(token_payload.id))

@router.get('/me/researches', response_model=list[MyResearch], tags=['users'])
def get_user_researches(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content=DBM.researches.get_researches_by_user_identifier(token_payload.id))



@router.get('/me/created_researches/', response_model=list[ResearchesCreatedByAdminResponse], tags=['admin_panel'])
def get_created_researches(token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    created_researches = DBM.researches.get_created_researches_by_user_identifier(token_payload.id)
    return created_researches

@router.get('/me/created_kits/', response_model=list[KitsCreatedByAdminResponse], tags=['admin_panel'])
def get_created_kits(token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    created_kits = DBM.kits.get_created_kits_by_user_identifier(token_payload.id)
    return created_kits