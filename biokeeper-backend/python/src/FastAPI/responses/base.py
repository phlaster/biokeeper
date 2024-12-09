from typing import Any, Type
from fastapi import status
from pydantic import BaseModel

class BasicResponse(BaseModel):
    @classmethod
    def generate_response_example(cls) -> dict[str, Any]:
        # Получаем схему модели и извлекаем примеры
        schema = cls.model_json_schema()
        response_example = dict()
        response_example['msg'] = schema['properties']['msg'].get('example'),
        if 'data' in schema['properties'].keys():
            response_example['data'] = schema['properties']['data'].get('example')
        return response_example

class BasicConflictResponse(BasicResponse):
    @staticmethod
    def get_status_code() -> int:
        return status.HTTP_409_CONFLICT
    
    @staticmethod
    def get_description() -> str:
        return "Conflict"
    
class BasicBadRequestResponse(BasicResponse):
    @staticmethod
    def get_status_code() -> int:
        return status.HTTP_400_BAD_REQUEST
    
    @staticmethod
    def get_description() -> str:
        return "Bad request"

class BasicNotFoundResponse(BasicResponse):
    @staticmethod
    def get_status_code() -> int:
        return status.HTTP_404_NOT_FOUND
    
    @staticmethod
    def get_description() -> str:
        return "Not found"

class BasicForbiddenResponse(BasicResponse):
    @staticmethod
    def get_status_code() -> int:
        return status.HTTP_403_FORBIDDEN
    
    @staticmethod
    def get_description() -> str:
        return "Forbidden"
    
class BasicUnauthorizedResponse(BasicResponse):
    @staticmethod
    def get_status_code() -> int:
        return status.HTTP_401_UNAUTHORIZED
    
    @staticmethod
    def get_description() -> str:
        return "Unauthorized"

def generate_examples(*models: Type[BasicResponse]):
    examples = dict()

    for model in models:
        example_data = model.generate_response_example()
        examples[model.__name__] = {
            'summary': example_data['msg'],
            'value': example_data
        }

    return examples

def generate_responses(*models: Type[BasicResponse]):
    responses = dict()
    codes_data = set((model.get_status_code(), model.get_description()) for model in models)

    for code, description in codes_data:
        code_models = [model for model in models if model.get_status_code() == code]
        responses[code] = {
            'description': description,
            'content': {
                'application/json': {
                    'examples': generate_examples(*code_models)
                }
            }
        }

    return responses

