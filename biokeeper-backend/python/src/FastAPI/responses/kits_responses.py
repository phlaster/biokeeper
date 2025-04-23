from pydantic import Field
from responses.base import BasicConflictResponse, BasicNotFoundResponse, BasicForbiddenResponse

from config import MAX_NUMBER_OF_QRS

class KitNotFoundResponse(BasicNotFoundResponse):
    msg: str = Field(..., example="Kit not found")
    data: dict | None = Field(..., example={"kit_identifier": 5})

class UserIsNotOwnerOfKit(BasicConflictResponse):
    msg: str = Field(..., example="User is not an owner of kit")
    data: dict | None = Field(..., example={"kit_identifier": 5, "user_id": 1})

class NewOwnerNotFoundResponse(BasicNotFoundResponse):
    msg: str = Field(..., example="New owner user not found")
    data: dict | None = Field(..., example={'new_owner_identifier': 5})

class UserIsNotVolunteerOrAdminResponse(BasicForbiddenResponse):
    msg: str = Field(..., example="User is not volunteer or admin")
    data: dict | None = Field(..., example={'new_owner_identifier': 5})

class UserIsNotCreatorOfTheKitResponse(BasicForbiddenResponse):
    msg: str = Field(..., example="User is not creator of kit")
    data: dict | None = Field(..., example={'kit_identifier': 5, 'user_id': 1})

class KitAlreadyHasOwnerResponse(BasicConflictResponse):
    msg: str = Field(..., example="Kit already has owner")
    data: dict | None = Field(..., example={'kit_identifier': 5})

class KitAlreadySentResponse(BasicConflictResponse):
    msg: str = Field(..., example="Kit already sent")
    data: dict | None = Field(..., example={'kit_identifier': 5})

class KitAlreadyActivatedResponse(BasicConflictResponse):
    msg: str = Field(..., example="Kit already activated")
    data: dict | None = Field(..., example={'kit_identifier': 5})


class NumberOfQRsLessThanZeroResponse(BasicConflictResponse):
    msg: str = Field(..., example="Number of QRs must be greater than zero")

class NumberOfQRsTooBigResponse(BasicConflictResponse):
    msg: str = Field(..., example="Number of QRs is too big")
    data: dict | None = Field(..., example={'max_number_of_qrs': MAX_NUMBER_OF_QRS})