from pydantic import BaseModel, field_validator
from datetime import datetime, date

from schemas.common import validate_identifier

class ResearchBase(BaseModel):
    id: int
    name: str

class ResearchResponse(ResearchBase):
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: int
    day_start: datetime
    day_end: datetime
    comment: str | None
    approval_required: bool
    n_samples: int

class ResearchRequest(BaseModel):
    research_identifier : int | str

    @field_validator('research_identifier', mode="before")
    def validate_research_identifier(cls, v):
        return validate_identifier(v, 'research_identifier must be either an integer or a string')
    
class GetResearchRequest(ResearchRequest):
    pass

class SendResearchParticipantRequest(ResearchRequest):
    pass

class CandidateRequest(BaseModel):
    candidate_identifier : int | str

    @field_validator('candidate_identifier', mode="before")
    def validate_candidate_identifier(cls, v):
        return validate_identifier(v, 'candidate_identifier must be either an integer or a string')

class ApproveResearchRequest(BaseModel):
    candidate_identifier : int | str
    @field_validator('candidate_identifier', mode="before")
    def validate_candidate_identifier(cls, v):
        return validate_identifier(v, 'candidate_identifier must be either an integer or a string')

class DeclineResearchRequest(BaseModel):
    candidate_identifier : int | str

    @field_validator('candidate_identifier', mode="before")
    def validate_research_identifier(cls, v):
        return validate_identifier(v, 'candidate_identifier must be either an integer or a string')

class CreateResearchRequest(BaseModel):
    research_name: str
    day_start: date
    research_comment: str | None
    approval_required: bool = True

    @field_validator('research_name', mode="after")
    def validate_name(cls, v):
        if v.strip() == '':
            raise ValueError('research_name cannot be empty')
        return v
            

    @field_validator('research_comment', mode="before")
    def validate_comment(cls, v):
        if v is None:
            return ''
        return v

class ResearchNewStatusResponse(BaseModel):
    research_identifier: int | str
    status: str

class MyResearch(BaseModel):
    research_id: int


class ResearchesCreatedByAdminResponse(ResearchBase):
    status: str


class AcceptedParticipantResponse(BaseModel):
    user_id: int
    username: str

class PendingRequestResponse(BaseModel):
    user_id: int
    username: str

class DeleteParticipantRequest(BaseModel):
    participant_identifier : int | str

    @field_validator('participant_identifier', mode="before")
    def validate_participant_identifier(cls, v):
        return validate_identifier(v, 'participant_identifier must be either an integer or a string')