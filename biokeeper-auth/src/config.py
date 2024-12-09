import base64
import os

def is_running_in_docker():
    return os.getenv('DOCKER_CONTAINER') is not None


if is_running_in_docker():
    POSTGRES_HOST = os.environ['POSTGRES_HOST']
    POSTGRES_PORT = os.environ['POSTGRES_PORT']
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from load_dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, 'biokeeper_auth', '.db.env'))
    load_dotenv(os.path.join(BASE_DIR, 'biokeeper_auth', '.rtoken.salt.env'))
    load_dotenv(os.path.join(BASE_DIR, 'jwt_keys', '.jwt.private.env'))
    load_dotenv(os.path.join(BASE_DIR, 'jwt_keys', '.jwt.public.env'))
    POSTGRES_HOST = 'localhost'
    POSTGRES_PORT = '5555'

REFRESH_TOKEN_HASH_SALT = os.getenv('REFRESH_TOKEN_HASH_SALT')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
JWT_PRIVATE_KEY = os.environ['JWT_PRIVATE_KEY']
JWT_PUBLIC_KEY = os.environ['JWT_PUBLIC_KEY']

database_url = f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'


RABBITMQ_AUTH_USER = os.getenv('RABBITMQ_AUTH_USER')
RABBITMQ_AUTH_PASS = os.getenv('RABBITMQ_AUTH_PASS')

PASSWORD_FOR_FASTAPI_DOCS = os.environ['PASSWORD_FOR_FASTAPI_DOCS']