import datetime
import bcrypt
from schemas import UserResponse
from config import JWT_PRIVATE_KEY, JWT_PUBLIC_KEY, REFRESH_TOKEN_HASH_SALT
import jwt

from hashlib import sha256

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    return hashed_password

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_jwt_token(user: UserResponse, type : str = 'access'):
    if type == 'access':
        time_delta = datetime.timedelta(minutes=10)
        payload = user.model_dump(exclude={'email'})
    else:
        time_delta = datetime.timedelta(days=20)
        payload = user.model_dump(exclude={'email', 'username', 'role'})
    payload['exp'] = datetime.datetime.now(datetime.timezone.utc) + time_delta
    # Подписываем токен приватным ключом
    token = jwt.encode(payload, JWT_PRIVATE_KEY, algorithm='RS256')
    return token, payload['exp']

def create_access_token(user: UserResponse):
    return create_jwt_token(user, type='access')[0]
    # token, exp = create_jwt_token(user, type='access')
    # return JWTToken(token=token, expires_at = exp)

def create_refresh_token(user: UserResponse):
    return create_jwt_token(user, type='refresh')[0]
    # token, exp = create_jwt_token(user, type='refresh')
    # return JWTToken(token=token, expires_at = exp)

def verify_jwt_token(token):
    # Проверяем токен с использованием публичного ключа
    payload = jwt.decode(token, JWT_PUBLIC_KEY, algorithms=['RS256'])
    return payload
    



def hash_token(token):
    return sha256(token.encode('utf-8') + REFRESH_TOKEN_HASH_SALT.encode('utf-8')).hexdigest()
