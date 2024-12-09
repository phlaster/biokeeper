from typing import Annotated
from fastapi import Depends, status
from fastapi.responses import JSONResponse, Response
from fastapi.routing import APIRouter
from db_manager import DBM
from datetime import date

from exceptions import HTTPConflictException, HTTPForbiddenException, NoResearchException, HTTPNotFoundException, NoUserException
from schemas.researches import AcceptedParticipantResponse, ApproveResearchRequest, CreateResearchRequest, DeclineResearchRequest, DeleteParticipantRequest, GetResearchRequest, PendingRequestResponse, ResearchBase, ResearchNewStatusResponse, ResearchRequest, ResearchResponse, SendResearchParticipantRequest, MyResearch
from schemas.common import TokenPayload
from utils import get_admin, get_current_user, get_volunteer_or_admin

from responses import researches_responses
from responses.base import generate_responses

from dependencies.identifiers_validators import research_identifier_validator_dependency

router = APIRouter()

@router.get('/researches', response_model=list[ResearchResponse], tags=['researches'])
def get_researches(token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    all_researches = list(DBM.researches.get_all().values())
    return JSONResponse(status_code=status.HTTP_200_OK, content=all_researches)

@router.get('/researches/{research_identifier}',
            response_model=ResearchResponse,
            tags=['researches'],
            responses=generate_responses(researches_responses.ResearchNotFoundResponse)
            )
def get_research(research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)], token_payload: Annotated[TokenPayload, Depends(get_current_user)]):
    try:
        dbm_research = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(msg=f'Research not found',data={'research_identifier': research_identifier})
    return JSONResponse(status_code=status.HTTP_200_OK, content=dbm_research)


@router.get('/researches/{research_identifier}/pending_requests',
            response_model=list[PendingRequestResponse],
            tags=['admin_panel'],
            responses=generate_responses(
                researches_responses.ResearchNotFoundResponse, 
                researches_responses.ApprovalIsNotRequiredResponse,
                researches_responses.UserIsNotCreatorOfTheResearchResponse
                )
            )
def get_pending_requests(research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)], token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    try:
        dbm_research = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(msg=f'Research not found',data={'research_identifier': research_identifier})
    
    if not dbm_research['approval_required']:
        raise HTTPConflictException(msg=f'Approval is not required for research',data={'research_identifier': research_identifier})
    
    if token_payload.id != dbm_research['created_by']:
        raise HTTPForbiddenException(msg=f'User is not creator of research',data={'research_identifier': research_identifier,'user_id': token_payload.id})

    pending_requests = DBM.researches.get_pending_requests(research_identifier)
    return pending_requests


@router.get('/researches/{research_identifier}/accepted_participants',
            response_model=list[AcceptedParticipantResponse],
            tags=['admin_panel'],
            responses=generate_responses(
                researches_responses.ResearchNotFoundResponse, 
                researches_responses.ApprovalIsNotRequiredResponse,
                researches_responses.UserIsNotCreatorOfTheResearchResponse
                )
            )
def get_accepted_participants(research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)], token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    try:
        dbm_research = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(msg=f'Research not found',data={'research_identifier': research_identifier})
    
    if not dbm_research['approval_required']:
        raise HTTPConflictException(msg=f'Approval is not required for research',data={'research_identifier': research_identifier})
    
    if token_payload.id != dbm_research['created_by']:
        raise HTTPForbiddenException(msg=f'User is not creator of research',data={'research_identifier': research_identifier,'user_id': token_payload.id})
    
    accepted_participants = DBM.researches.get_accepted_participants(research_identifier)
    return accepted_participants


@router.post('/researches/{research_identifier}/send_request',
                tags=['researches'],
                responses=generate_responses(
                    researches_responses.ResearchNotFoundResponse,
                    researches_responses.ApprovalIsNotRequiredResponse,
                    researches_responses.ResearchAlreadyEndedResponse,
                    researches_responses.UserAlreadyParticipateInResearchResponse,
                    researches_responses.UserAlreadySentRequestResponse
                    )
                )
def send_request(research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)], 
                token_payload: Annotated[TokenPayload, Depends(get_volunteer_or_admin)]
                ):
    try:
        dbm_research = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(msg=f'Research not found',data={'research_identifier': research_identifier})
    
    if not dbm_research['approval_required']:
        raise HTTPConflictException(msg=f'Approval is not required for research',data={'research_identifier': research_identifier})

    if dbm_research['status'] in ['ended', 'canceled']:
        raise HTTPConflictException(msg=f'Research already ended',data={'research_identifier': research_identifier})
    
    participants = DBM.researches.get_participants_ids(dbm_research['id'])
    if token_payload.id in participants:
        raise HTTPConflictException(msg=f'User already participate in research',data={'research_identifier': research_identifier,'user_id': token_payload.id})
    
    candidates = DBM.researches.get_candidates_ids(dbm_research['id'])
    if token_payload.id in candidates:
        raise HTTPConflictException(msg=f'User already sent request to research ',data={'research_identifier': research_identifier,'user_id': token_payload.id})

    DBM.researches.send_request(dbm_research['id'], token_payload.id, log=False)
    return JSONResponse(status_code=status.HTTP_200_OK, content=f"User {token_payload.id} sent request to research {research_identifier}")


@router.post('/researches/{research_identifier}/approve_request',
                tags=['admin_panel'],
                responses=generate_responses(
                    researches_responses.ResearchNotFoundResponse,
                    researches_responses.UserIsNotCreatorOfTheResearchResponse,
                    researches_responses.ApprovalIsNotRequiredResponse,
                    researches_responses.ResearchAlreadyEndedResponse,
                    researches_responses.CandidateNotFoundResponse,
                    researches_responses.UserAlreadyParticipateInResearchResponse,
                    researches_responses.UserNotSentRequestResponse
                    )
                )
def approve_request(research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)], approve_research_request: ApproveResearchRequest, token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    candidate_identifier = approve_research_request.candidate_identifier
    try:
        dbm_research = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(msg=f'Research not found',data={'research_identifier': research_identifier})
    
    if not dbm_research['created_by'] == token_payload.id:
        raise HTTPForbiddenException(msg=f'User is not creator of research',data={'research_identifier': research_identifier,'user_id': token_payload.id})

    if not dbm_research['approval_required']:
        raise HTTPConflictException(msg=f'Approval is not required for research',data={'research_identifier': research_identifier})

    if dbm_research['status'] in ['ended', 'canceled']:
        raise HTTPConflictException(msg=f'Research already ended',data={'research_identifier': research_identifier})
    
    try:
        candidate_info = DBM.users.get_info(candidate_identifier)
    except NoUserException:
        raise HTTPNotFoundException(msg=f'User not found',data={'candidate_identifier': candidate_identifier})
    
    candidate_id = candidate_info['id']
    research_id = dbm_research['id']
    participants = DBM.researches.get_participants_ids(research_id)
    if candidate_id in participants:
        raise HTTPConflictException(msg=f'User already participate in research',data={'research_identifier': research_identifier,'user_id': candidate_id})
    
    candidates = DBM.researches.get_candidates_ids(research_id)
    if candidate_id not in candidates:
        raise HTTPConflictException(msg=f'User not sent request to research ',data={'research_identifier': research_identifier,'user_id': candidate_id})

    DBM.researches.approve_request(research_id, candidate_id, log=False)
    return JSONResponse(status_code=status.HTTP_200_OK, content=f"User {candidate_id} approved request to research {research_identifier}")

@router.post('/researches/{research_identifier}/decline_request', tags=['admin_panel'],
                responses=generate_responses(
                    researches_responses.ResearchNotFoundResponse,
                    researches_responses.UserIsNotCreatorOfTheResearchResponse,
                    researches_responses.ApprovalIsNotRequiredResponse,
                    researches_responses.ResearchAlreadyEndedResponse,
                    researches_responses.CandidateNotFoundResponse,
                    researches_responses.UserAlreadyParticipateInResearchResponse,
                    researches_responses.UserNotSentRequestResponse
                ))
def decline_request(research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)], decline_research_request: DeclineResearchRequest, token_payload: Annotated[TokenPayload, Depends(get_admin)]):
    candidate_identifier = decline_research_request.candidate_identifier
    try:
        dbm_research = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(msg=f'Research not found',data={'research_identifier': research_identifier})
    
    if not dbm_research['created_by'] == token_payload.id:
        raise HTTPForbiddenException(msg=f'User is not creator of research',data={'research_identifier': research_identifier,'user_id': token_payload.id})

    if not dbm_research['approval_required']:
        raise HTTPConflictException(msg=f'Approval is not required for research',data={'research_identifier': research_identifier})

    if dbm_research['status'] in ['ended', 'canceled']:
        raise HTTPConflictException(msg=f'Research already ended',data={'research_identifier': research_identifier})
    
    try:
        candidate_info = DBM.users.get_info(candidate_identifier)
    except NoUserException:
        raise HTTPNotFoundException(msg=f'User not found',data={'candidate_identifier': candidate_identifier})
    
    candidate_id = candidate_info['id']
    research_id = dbm_research['id']
    participants = DBM.researches.get_participants_ids(research_id)
    if candidate_id in participants:
        raise HTTPConflictException(msg=f'User already participate in research',data={'research_identifier': research_identifier,'user_id': candidate_id})
    
    candidates = DBM.researches.get_candidates_ids(research_id)
    if candidate_id not in candidates:
        raise HTTPConflictException(msg=f'User not sent request to research',data={'research_identifier': research_identifier,'user_id': candidate_id})

    DBM.researches.decline_request(research_id, candidate_id, log=False)
    return Response(status_code=status.HTTP_200_OK, 
                    content=f"User {candidate_id} declined request to research {research_identifier}")


@router.delete('/researches/{research_identifier}/accepted_participants',
               tags=['admin_panel'],
               responses=generate_responses(
                    researches_responses.ResearchNotFoundResponse,
                    researches_responses.UserIsNotCreatorOfTheResearchResponse,
                    researches_responses.ApprovalIsNotRequiredResponse,
                    researches_responses.ResearchAlreadyEndedResponse,
                    researches_responses.CandidateNotFoundResponse,
                    researches_responses.UserNotParticipateInResearchResponse
                    )
                )
def delete_accepted_participant(research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)], 
                                token_payload: Annotated[TokenPayload, Depends(get_admin)],
                                delete_participant_request: DeleteParticipantRequest
                                ):
    participant_identifier = delete_participant_request.participant_identifier
    try:
        dbm_research = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(msg=f'Research not found',data={'research_identifier': research_identifier})
    
    if not dbm_research['created_by'] == token_payload.id:
        raise HTTPForbiddenException(msg=f'User is not creator of research',data={'research_identifier': research_identifier,'user_id': token_payload.id})

    if not dbm_research['approval_required']:
        raise HTTPConflictException(msg=f'Approval is not required for research',data={'research_identifier': research_identifier})

    if dbm_research['status'] in ['ended', 'canceled']:
        raise HTTPConflictException(msg=f'Research already ended',data={'research_identifier': research_identifier})
    
    try:
        participant_info = DBM.users.get_info(participant_identifier)
    except NoUserException:
        raise HTTPNotFoundException(msg=f'User not found',data={'participant_identifier': participant_identifier})
    
    participant_id = participant_info['id']
    research_id = dbm_research['id']

    participants = DBM.researches.get_participants_ids(research_id)
    if participant_id not in participants:
        raise HTTPConflictException(msg=f'User not participate in research',data={'research_identifier': research_identifier,'user_id': participant_id})

    DBM.researches.delete_accepted_participant(research_id, participant_id, log=False)
    return Response(status_code=status.HTTP_200_OK, 
                    content=f"User {participant_id} removed from research {research_identifier}")


@router.put('/researches/{research_identifier}/start',
            response_model=ResearchNewStatusResponse,
            tags=['admin_panel'],
            responses=generate_responses(
                researches_responses.ResearchNotFoundResponse,
                researches_responses.ResearchNotOwnerResponse,
                researches_responses.ResearchAlreadyOnGoingResponse,
                researches_responses.ResearchAlreadyEndedResponse,
                researches_responses.ResearchIsCanceledResponse
                )
            )
def set_research_start(
        research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)],
        token_payload: Annotated[TokenPayload, Depends(get_admin)]
        ):
    try:
        research_info = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(msg=f'Research not found',data={'research_identifier': research_identifier})
    
    if token_payload.id != research_info['created_by']:
        raise HTTPForbiddenException(msg=f'Research owner differs from autorized user')
    
    if  research_info['status'] == 'ongoing':
        raise HTTPConflictException(msg=f'Research already ongoing',data={'research_identifier': research_identifier})
    
    if research_info['status'] == 'ended':
        raise HTTPConflictException(msg=f'Research already ended',data={'research_identifier': research_identifier})
    
    if research_info['status'] == 'canceled':
        raise HTTPConflictException(msg=f'Research is canceled',data={'research_identifier': research_identifier})

    
    DBM.researches.change_status(research_identifier, new_status="ongoing", log=True)

    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={"research_identifier": research_identifier, 
                                 "status": "ongoing"})


@router.put('/researches/{research_identifier}/pause',
            response_model=ResearchNewStatusResponse,
            tags=['admin_panel'],
            responses=generate_responses(
                researches_responses.ResearchNotFoundResponse,
                researches_responses.ResearchNotOwnerResponse,
                researches_responses.ResearchNotStartedResponse,
                researches_responses.ResearchAlreadyPausedResponse,
                researches_responses.ResearchAlreadyEndedResponse,
                researches_responses.ResearchIsCanceledResponse
                )
            )
def set_research_paused(
            research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)],
            token_payload: Annotated[TokenPayload, Depends(get_admin)]
        ):
    try:
        research_info = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(msg=f'Research not found',data={'research_identifier': research_identifier})
    
    if token_payload.id != research_info['created_by']:
        raise HTTPForbiddenException(msg=f'Research owner differs from autorized user')
    
    if  research_info['status'] == 'pending':
        raise HTTPConflictException(msg=f'Research not started yet',data={'research_identifier': research_identifier})

    if  research_info['status'] == 'paused':
        raise HTTPConflictException(msg=f'Research already paused',data={'research_identifier': research_identifier})
    
    if research_info['status'] == 'ended':
        raise HTTPConflictException(msg=f'Research already ended',data={'research_identifier': research_identifier})
    
    if research_info['status'] == 'canceled':
        raise HTTPConflictException(msg=f'Research is canceled',data={'research_identifier': research_identifier})

    DBM.researches.change_status(research_identifier, new_status="paused", log=True)

    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={"research_identifier": research_identifier, 
                                 "status": "paused"})


@router.put('/researches/{research_identifier}/end',
            response_model=ResearchNewStatusResponse,
            tags=['admin_panel'],
            responses=generate_responses(
                researches_responses.ResearchNotFoundResponse,
                researches_responses.ResearchNotOwnerResponse,
                researches_responses.ResearchNotStartedResponse,
                researches_responses.ResearchAlreadyEndedResponse,
                researches_responses.ResearchIsCanceledResponse
                )
            )
def set_research_ended(
        research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)],
        token_payload: Annotated[TokenPayload, Depends(get_admin)]
    ):
    try:
        research_info = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(msg=f'Research not found',data={'research_identifier': research_identifier})
    
    if token_payload.id != research_info['created_by']:
        raise HTTPForbiddenException(msg=f'Research owner differs from autorized user')
    
    if  research_info['status'] == 'pending':
        raise HTTPConflictException(msg=f'Research not started yet',data={'research_identifier': research_identifier})

    if research_info['status'] == 'ended':
        raise HTTPConflictException(msg=f'Research already ended',data={'research_identifier': research_identifier})
    
    if research_info['status'] == 'canceled':
        raise HTTPConflictException(msg=f'Research is canceled',data={'research_identifier': research_identifier})
    
    DBM.researches.change_status(research_identifier, new_status="ended", log=True)
    
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={"research_identifier": research_identifier, 
                                 "status": "ended"})


@router.put('/researches/{research_identifier}/cancel',
            response_model=ResearchNewStatusResponse,
            tags=['admin_panel'],responses=generate_responses(
                researches_responses.ResearchNotFoundResponse,
                researches_responses.ResearchNotOwnerResponse,
                researches_responses.ResearchIsCanceledResponse,
                researches_responses.ResearchAlreadyEndedResponse
                )
            )
def set_research_canceled(
    research_identifier: Annotated[str, Depends(research_identifier_validator_dependency)],
    token_payload: Annotated[TokenPayload, Depends(get_admin)]
):
    try:
        research_info = DBM.researches.get_info(research_identifier)
    except NoResearchException:
        raise HTTPNotFoundException(msg=f'Research not found',data={'research_identifier': research_identifier})
    
    if token_payload.id != research_info['created_by']:
        raise HTTPForbiddenException(msg=f'Research owner differs from autorized user')
    
    if research_info['status'] == 'canceled':
        raise HTTPConflictException(msg=f'Research is canceled',data={'research_identifier': research_identifier})
    
    if research_info['status'] == 'ended':
        raise HTTPConflictException(msg=f'Research already ended',data={'research_identifier': research_identifier})
    
    DBM.researches.change_status(research_identifier, new_status="canceled", log=True)
    
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content={"research_identifier": research_identifier, 
                                 "status": "canceled"})


@router.post('/researches', 
             response_model=ResearchBase,
             tags=['admin_panel'], responses=generate_responses(
                 researches_responses.ResearchAlreadyExistsResponse
                 )
            )
def create_research(
    token_payload: Annotated[TokenPayload, Depends(get_admin)],
    create_research_request : CreateResearchRequest
    ):
    
    user_id = token_payload.id
    research_name = create_research_request.research_name

    try:
        DBM.researches.has(research_name)
    except NoResearchException:
        pass
    else:
        raise HTTPConflictException(msg=f'Research already exists',data={'research_name': research_name})

    new_research_id = DBM.researches.new(research_name=research_name, 
                              user_id=user_id, 
                              day_start=create_research_request.day_start, 
                              research_comment=create_research_request.research_comment, 
                              log=False, 
                              approval_required=create_research_request.approval_required)
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, 
                        content={'id': new_research_id, 'name': research_name}
                        )

