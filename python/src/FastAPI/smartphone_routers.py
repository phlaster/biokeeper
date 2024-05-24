from fastapi.routing import APIRouter
from db_manager import DBM
from datetime import datetime


router = APIRouter()

@router.post("/react/login")
async def react_login(username: str, password: str):
    user_id = DBM.users.password_match(username, password)
    if not user_id:
        return {
        "result" : False,
        "response": "Failed authentication"
    }
    
    return {
        "result" : True,
        "response": f"Successfull log in for user {user_id}"
    }


@router.post("/react/researches")
async def react_ongoing_researches(username: str, password: str):
    user_id = DBM.users.password_match(username, password)
    if not user_id:
        return {
        "result" : False,
        "response": "Failed authentication"
    }

    researches = DBM.researches.get_all()
    if not researches:
        return {
        "result" : False,
        "response": "No researches found"
    }
    
    filtered_researches = {k: v for k, v in researches.items() if v['status'] == 'ongoing'}
    if not filtered_researches:
        return {
        "result" : False,
        "response": "No ongoing researches found"
    }

    return {
        "result" : True,
        "response": filtered_researches
    }


@router.post("/react/user_stats")
async def react_user_stats(username: str, password: str):
    user_id = DBM.users.password_match(username, password)
    if not user_id:
        return {
        "result" : False,
        "response": "Failed authentication"
    }

    return {
        "result" : True,
        "response": DBM.users.get_info(username)
    }


@router.post("/react/push_sample")
async def react_push_sample(
    username: str,
    password: str,
    qr_unique_hex:str,
    research_name:str,
    collected_at:str,
    latitude:float,
    longitude:float
):
    user_id = DBM.users.password_match(username, password)
    if not user_id:
        return {
        "result" : False,
        "response": "Failed authentication"
    }
    
    # '2023-10-12T14:30:00+02:00'
    try:
        collected_at = datetime.fromisoformat(collected_at)
    except ValueError:
        return {
        "result" : False,
        "response": "Incorrect datetime format. Use ISO: '2000-12-31T12:34:56+07:00'"
    }

    response = DBM.samples.new(
        qr_unique_hex,
        research_name,
        collected_at,
        (latitude, longitude),
        log=True
    )
    return {
        "result" : bool(response),
        "response": response
    }