from typing import Annotated
from fastapi import Depends, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from db_manager import DBM
from datetime import datetime
from exceptions import HTTPConflictException, HTTPNotFoundException, NoSampleException, HTTPForbiddenException, NoResearchException, NoQrCodeException
from schemas.common import TokenPayload
from schemas.samples import CreateSampleRequest, GpsModel, MySample, SampleBase, SampleInfo
from utils import get_current_user, get_volunteer_or_admin, is_admin, is_observer

from responses import samples_responses
from responses.base import generate_responses

router = APIRouter()


@router.get('/samples', response_model = list[SampleInfo], tags=['samples'])
def get_samples(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    all_samples = list(DBM.samples.get_all().values())
    for sample in all_samples:
        latitude, longitude = sample['gps'][1:-1].split(',')
        sample['gps'] = GpsModel(latitude=latitude, longitude=longitude)
    return all_samples

@router.get('/samples/{sample_id}',
            response_model = SampleInfo,
            tags=['samples'],
            responses=generate_responses(
                samples_responses.SampleNotFoundResponse,
                samples_responses.SampleNotOwnerResponse
                )
            )
def get_sample(sample_id:  int, token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    try:
        dbm_sample = DBM.samples.get_info(sample_id)
    except NoSampleException:
        raise HTTPNotFoundException(msg=f'Sample not found',data={'sample_id': sample_id})
    if not is_admin(token_payload) and dbm_sample['owner_id'] != token_payload.id or is_observer(token_payload):
        raise HTTPForbiddenException(msg=f'Sample owner differs from autorized user')
    
    latitude, longitude = dbm_sample['gps'][1:-1].split(',')
    dbm_sample['gps'] = GpsModel(latitude=latitude, longitude=longitude)
    return dbm_sample

@router.post('/samples',
            response_model = SampleBase,
            tags=['samples'],
            responses=generate_responses(
                samples_responses.ResearchWithIDNotFoundResponse,
                samples_responses.UserNotInResearchResponse,
                samples_responses.ResearchNotOngoingResponse,
                samples_responses.QRNotFoundResponse,
                samples_responses.QRAlreadyUsedResponse,
                samples_responses.QRIsNotAssignedToKitResponse,
                samples_responses.KitNotFoundResponse,
                samples_responses.KitIsNotAssignedToUserResponse,
                samples_responses.UserDoesNotOwnKitResponse,
                samples_responses.KitIsNotActivatedResponse
                )
            )
def create_sample(
    create_request : CreateSampleRequest,
    token_payload: Annotated[TokenPayload, Depends(get_volunteer_or_admin)]
):
    try:
        dbm_research = DBM.researches.get_info(create_request.research_id)
    except NoResearchException:
        raise HTTPNotFoundException(msg=f'Research with this id not found',data={'research_id': create_request.research_id})
    
    if dbm_research['approval_required']:
        user_researches = DBM.users.get_user_participated_researches(token_payload.id)
        if not dbm_research['id'] in user_researches:
            raise HTTPForbiddenException(msg=f"User does not participate in research",data={'research_id': dbm_research['id'],'user_id': token_payload.id})
        
    if not dbm_research['status'] != 'ongoing':
        raise HTTPConflictException(msg='Research is not in ongoing status',data={'research_id': dbm_research['id']})

    try:
        dbm_qr_info = DBM.samples.get_qr_info(create_request.qr_hex)
    except NoQrCodeException:
        raise HTTPNotFoundException(msg=f'Qr not found',data={'qr_hex': create_request.qr_hex})

    if dbm_qr_info['is_used']:
        raise HTTPConflictException(msg=f'Qr is already used',data={'qr_hex': create_request.qr_hex})
    
    if not dbm_qr_info['kit_id']:
        raise HTTPConflictException(msg=f'Qr is not assigned to any kit',data={'qr_hex': create_request.qr_hex})
    
    try:
        dbm_kit = DBM.kits.get_info(dbm_qr_info['kit_id'])
    except NoQrCodeException:
        raise HTTPNotFoundException(msg=f'Kit not found (very strange)',data={'kit_id': dbm_qr_info['kit_id']})
    
    if not dbm_kit['owner']:
        raise HTTPForbiddenException(msg=f'Kit is not assigned to any user',data={'kit_id': dbm_qr_info['kit_id']})
    
    if not dbm_kit['owner']['id'] == token_payload.id:
        raise HTTPForbiddenException(msg=f"User does not own kit",data={'kit_id': dbm_qr_info['kit_id'],'user_id': token_payload.id})
    
    if not dbm_kit['status'] == 'activated':
        raise HTTPConflictException(msg=f"Kit hasn't been activated",data={'kit_id': dbm_kit["id"]})


    dbm_new_sample_id = DBM.samples.new(qr_id=int(dbm_qr_info['id']), 
                        research_id=int(dbm_research['id']), 
                        owner_id = int(token_payload.id),
                        collected_at=create_request.collected_at,
                        gps=create_request.gps,
                        weather=create_request.weather, 
                        user_comment=create_request.user_comment,
                        photo_hex_string = create_request.photo_hex_string,
                        log = False)
    
    return JSONResponse(status_code=status.HTTP_200_OK, content = {'id': dbm_new_sample_id})
        
    