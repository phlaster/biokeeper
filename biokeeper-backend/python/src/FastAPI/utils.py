from typing import Annotated
from exceptions import NotFoundException
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from schemas.common import TokenPayload
from crypto import verify_jwt_token
from exceptions import NoUserException, HTTPNotEnoughPermissionsException
import jwt


external_token_url = "https://auth.biokeeper.ru/token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=external_token_url)



async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenPayload:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Access token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    no_user_in_db_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_jwt_token(token)
        if not payload:
            raise credentials_exception
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        from db_manager import DBM
        DBM.users.has(username)
    except jwt.ExpiredSignatureError:
        raise expired_exception
    except jwt.InvalidTokenError as error:
        print(error)
        raise credentials_exception
    except NoUserException:
        print("User not found")
        raise no_user_in_db_exception
    return TokenPayload(**payload)

def role_is(token: Annotated[TokenPayload, Depends(get_current_user)], role_name):
    return token.role.name == role_name

def is_admin(token: Annotated[TokenPayload, Depends(get_current_user)]):
    return role_is(token, "admin")

def is_observer(token: Annotated[TokenPayload, Depends(get_current_user)]):
    return role_is(token, "observer")

def is_volunteer(token: Annotated[TokenPayload, Depends(get_current_user)]):
    return role_is(token, "volunteer")

async def get_admin(token: Annotated[TokenPayload, Depends(get_current_user)]) -> TokenPayload:
    if not is_admin(token):
        raise HTTPNotEnoughPermissionsException(detail='Not enough permissions. Only admins can perform this action.')
    return token

async def get_volunteer(token: Annotated[TokenPayload, Depends(get_current_user)]) -> TokenPayload:
    if not is_volunteer(token):
        raise HTTPNotEnoughPermissionsException(detail='Not enough permissions. Only volunteers can perform this action.')
    return token

async def get_volunteer_or_admin(token: Annotated[TokenPayload, Depends(get_current_user)]) -> TokenPayload:
    if not is_admin(token) and not is_volunteer(token):
        raise HTTPNotEnoughPermissionsException(detail='Not enough permissions. Only admins and volunteers can perform this action.')
    return token

async def get_observer(token: Annotated[TokenPayload, Depends(get_current_user)]) -> TokenPayload:
    if not is_observer(token):
        raise HTTPNotEnoughPermissionsException(detail='Not enough permissions. Only observers can perform this action.')
    return token

def validate_return_from_db(data,
                      search_param_name,
                      search_param_value,
                      logger=None,
                      exception=NotFoundException):
    key,value = list(data.items())[0]
    if not value:
        print(f"Error: Can't find {key} using {search_param_name} with {search_param_value}.")
        if logger:
            logger.log(f"Error: Can't find {key} using {search_param_name} with {search_param_value}.", 0)
        raise exception(f"Can't find {key} using {search_param_name} with {search_param_value}.")
    return value


from geopy.geocoders import Nominatim
def get_closest_toponym(lat, lon):
    geolocator = Nominatim(user_agent="Biokeeper")
    try:
        location = geolocator.reverse(f"{lat}, {lon}")
        return location.raw['display_name']
    except Exception as e:
        return f"{lat},{lon}"