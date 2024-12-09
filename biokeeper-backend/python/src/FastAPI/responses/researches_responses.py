from pydantic import  Field
from responses.base import BasicConflictResponse, BasicNotFoundResponse, BasicForbiddenResponse

class ResearchNotFoundResponse(BasicNotFoundResponse): 
    msg: str = Field(..., example="Research not found")
    data: dict | None = Field(..., example={"research_identifier": 5})

class UserIsNotCreatorOfTheResearchResponse(BasicForbiddenResponse): 
    msg: str = Field(..., example="User is not creator of research")
    data: dict | None = Field(..., example={'research_identifier': 5, 'user_id': 1})

class ApprovalIsNotRequiredResponse(BasicConflictResponse): 
    msg: str = Field(..., example="Approval is not required for research")
    data: dict | None = Field(..., example={'research_identifier': 5})

class ResearchAlreadyEndedResponse(BasicConflictResponse): 
    msg: str = Field(..., example="Research already ended")
    data: dict | None = Field(..., example={'research_identifier': 5})

class UserAlreadyParticipateInResearchResponse(BasicConflictResponse): 
    msg: str = Field(..., example="User already participate in research")
    data: dict | None = Field(..., example={'research_identifier': 5, 'user_id': 1})

class UserAlreadySentRequestResponse(BasicConflictResponse): 
    msg: str = Field(..., example="User already sent request to research")
    data: dict | None = Field(..., example={'research_identifier': 5, 'user_id': 1})

class UserNotSentRequestResponse(BasicConflictResponse): 
    msg: str = Field(..., example="User not sent request to research")
    data: dict | None = Field(..., example={'research_identifier': 5, 'user_id': 1})

class ResearchNotOwnerResponse(BasicForbiddenResponse):
    msg: str = Field(..., example="Research owner differs from autorized user")

class ResearchIsCanceledResponse(BasicConflictResponse):  
    msg: str = Field(..., example="Research is canceled")
    data: dict | None = Field(..., example={'research_identifier': 5})

class ResearchAlreadyOnGoingResponse(BasicConflictResponse): 
    msg: str = Field(..., example="Research already ongoing")
    data: dict | None = Field(..., example={'research_identifier': 5})

class ResearchNotStartedResponse(BasicConflictResponse): 
    msg: str = Field(..., example="Research not started yet")
    data: dict | None = Field(..., example={'research_identifier': 5})

class ResearchAlreadyExistsResponse(BasicConflictResponse):
    msg: str = Field(..., example="Research already exists")
    data: dict | None = Field(..., example={'research_name': "Some research name"})

class UserNotFoundResponse(BasicNotFoundResponse): 
    msg: str = Field(..., example="User not found")
    data: dict | None = Field(..., example={'user_id': 5})

class CandidateNotFoundResponse(BasicNotFoundResponse): 
    msg: str = Field(..., example="User not found")
    data: dict | None = Field(..., example={'candidate_identifier': 5})

class UserNotParticipateInResearchResponse(BasicNotFoundResponse): 
    msg: str = Field(..., example="User not participate in research")
    data: dict | None = Field(..., example={'research_identifier': 5, 'user_id': 5})

class ResearchAlreadyPausedResponse(BasicConflictResponse): 
    msg: str = Field(..., example="Research already paused")
    data: dict | None = Field(..., example={'research_identifier': 5})