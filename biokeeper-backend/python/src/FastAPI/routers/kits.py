from typing import Annotated
from fastapi import Depends, Body, status
from fastapi.routing import APIRouter
from db_manager import DBM
from exceptions import NoKitException, HTTPNotFoundException,HTTPForbiddenException,HTTPConflictException, NoUserException
from schemas.common import TokenPayload
from schemas.kits import CreateKitRequest, KitInfo, KitRequest, MyKit, SendKitRequest
from utils import get_admin, get_current_user, get_volunteer, get_volunteer_or_admin
from fastapi.responses import JSONResponse, Response
from schemas.common import TokenPayload
from utils import get_current_user

from config import MAX_NUMBER_OF_QRS

from responses import kits_responses
from responses.base import generate_responses

from dependencies.identifiers_validators import kit_identifier_validator_dependency

router = APIRouter()

@router.get('/kits', response_model=list[KitInfo], tags=['kits'])
def get_kits(token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    all_kits = list(DBM.kits.get_all().values())
    return JSONResponse(status_code=status.HTTP_200_OK, content=all_kits)

@router.get('/kits/{kit_identifier}',
            response_model=KitInfo,
            tags=['kits'],
            responses=generate_responses(
                kits_responses.KitNotFoundResponse,
                kits_responses.UserIsNotOwnerOfKit
            ))
def get_kit(kit_identifier: Annotated[str, Depends(kit_identifier_validator_dependency)], 
            token_payload: Annotated[TokenPayload, Depends(get_volunteer_or_admin)]):
    try:
        dbm_kit = DBM.kits.get_info(kit_identifier)
    except NoKitException:
        raise HTTPNotFoundException(msg=f'Kit not found',data={'kit_identifier': kit_identifier})
    if token_payload.id != dbm_kit['owner_id']:
        raise HTTPForbiddenException(msg=f'User is not an owner of kit',data={'kit_identifier': kit_identifier,'user_id': token_payload.id})
    return JSONResponse(status_code=status.HTTP_200_OK, content=dbm_kit)

@router.put('/kits/{kit_identifier}/send', 
            tags=['admin_panel'],
            responses=generate_responses(
                kits_responses.KitNotFoundResponse,
                kits_responses.NewOwnerNotFoundResponse,
                kits_responses.UserIsNotVolunteerOrAdminResponse,
                kits_responses.UserIsNotCreatorOfTheKitResponse,
                kits_responses.KitAlreadyHasOwnerResponse,
                kits_responses.KitAlreadySentResponse,
            ))
def update_owner(
    token_payload: Annotated[TokenPayload, Depends(get_admin)],
    kit_identifier: Annotated[str, Depends(kit_identifier_validator_dependency)],
    send_kit_request: SendKitRequest
    ):
    new_owner_identifier = send_kit_request.new_owner_identifier
    try:
        kit_info = DBM.kits.get_info(kit_identifier)
    except NoKitException:
        raise HTTPNotFoundException(msg=f'Kit not found',data={'kit_identifier': kit_identifier})     

    try:
        new_owner_info = DBM.users.get_info(new_owner_identifier)
    except NoUserException:
        raise HTTPNotFoundException(msg=f'New owner user not found',data={'new_owner_identifier': new_owner_identifier})
    
    new_owner_id = new_owner_info['id']
    
    if new_owner_info['status'] != 'volunteer' and new_owner_info['status'] != 'admin':
        raise HTTPForbiddenException(msg=f'User is not volunteer or admin',data={'new_owner_identifier': new_owner_identifier})

    if kit_info['creator_id']!= token_payload.id:
        raise HTTPForbiddenException(msg=f'User  is not creator of kit',data={'kit_identifier': kit_identifier,'user_id': token_payload.id})
    
    if kit_info['owner_id'] is not None:
        raise HTTPConflictException(msg=f'Kit already has owner',data={'kit_identifier': kit_identifier})
    
    if kit_info['status'] == 'sent':
        raise HTTPConflictException(msg=f'Kit already sent',data={'kit_identifier': kit_identifier})
    
    DBM.kits.send_kit(kit_info['id'], new_owner_id, log=True)
    return Response(status_code=status.HTTP_200_OK, content=f"Kit {kit_identifier} owner changed to {new_owner_id}")
    


@router.put('/kits/{kit_identifier}/activate', 
            tags=['kits'],
            responses=generate_responses(
                kits_responses.KitNotFoundResponse,
                kits_responses.UserIsNotOwnerOfKit,
                kits_responses.KitAlreadyActivatedResponse
            ))
def activate_kit(
    kit_identifier: Annotated[str, Depends(kit_identifier_validator_dependency)],
    token_payload: Annotated[TokenPayload, Depends(get_volunteer_or_admin)]
    ):
    try:
        kit_info = DBM.kits.get_info(kit_identifier)
    except NoKitException:
        raise HTTPNotFoundException(msg=f'Kit not found',data={'kit_identifier': kit_identifier})
    
    if kit_info['owner_id'] != token_payload.id:
        raise HTTPConflictException(msg=f'User is not an owner of kit',data={'kit_identifier': kit_identifier,'user_id': token_payload.id})
    
    if kit_info['status'] == 'activated':
        raise HTTPConflictException(msg=f'Kit already activated',data={'kit_identifier': kit_identifier})
    
    DBM.kits.activate(kit_info['id'], log=True)

    return Response(status_code=status.HTTP_200_OK, content=f"Kit {kit_identifier} is activated")
    
@router.post('/kits', response_model=KitInfo, 
             tags=['admin_panel'],
             responses = generate_responses(
                 kits_responses.NumberOfQRsLessThanZeroResponse,
                 kits_responses.NumberOfQRsTooBigResponse
                ) 
             )
def create_kit(create_kit_request: CreateKitRequest, token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    if create_kit_request.n_qrs <= 0:
        raise HTTPConflictException(msg=f'Number of QRs must be greater than zero')
    if create_kit_request.n_qrs > MAX_NUMBER_OF_QRS:
        raise HTTPConflictException(msg=f'Number of QRs is too big', data={'max_number_of_qrs': MAX_NUMBER_OF_QRS})
    kit_id = DBM.kits.new(create_kit_request.n_qrs, token_payload.id, log=True)
    kit_info = DBM.kits.get_info(kit_id)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=kit_info)
