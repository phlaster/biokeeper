
from fastapi.routing import APIRouter
from db_manager import DBM

router = APIRouter()

@router.get('/users')
def get_users():
    """
    Retrieves all users.
    Returns a dictionary containing information about all users.
    """
    return DBM.users.get_all()

@router.get('/users/{user_name}')
def get_user(user_name):
    """
    Returns user information for the specified user_name.
    """
    return DBM.users.get_info(user_name)

@router.get('/users/{user_name}/status')
def get_user_status(user_name):
    return DBM.users.status_of(user_name)

@router.post('/users')
def create_user(user_name, password):
    return DBM.users.new(user_name, password)

@router.get('/users/{user_name}/score')
def get_user_score(user_name):
    return DBM.users.get_info(user_name)['n_samples_collected']

