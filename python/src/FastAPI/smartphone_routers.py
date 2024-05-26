from fastapi.routing import APIRouter
from db_manager import DBM
from datetime import datetime
from fastapi.responses import JSONResponse


router = APIRouter()

@router.post("/react/login")
async def react_login(username: str, password: str):
    user_id = DBM.users.password_match(username, password)
    if not user_id:
        return JSONResponse(
            content={
                "result": False,
                "response": "Failed authentication"
            },
            status_code=401
        )
    
    return JSONResponse(
        content={
            "result": True,
            "response": f"Successful log in for user {user_id}"
        },
        status_code=200
    )


@router.post("/react/researches")
async def react_ongoing_researches(username: str, password: str):
    user_id = DBM.users.password_match(username, password)
    if not user_id:
        return JSONResponse(
            content={
                "result": False,
                "response": "Failed authentication"
            },
            status_code=401
        )

    researches = DBM.researches.get_all()
    if not researches:
        return JSONResponse(
            content={
                "result": False,
                "response": "No researches found"
            },
            status_code=404
        )
    
    filtered_researches = {k: v for k, v in researches.items() if v['status'] == 'ongoing'}
    if not filtered_researches:
        return JSONResponse(
            content={
                "result": False,
                "response": "No ongoing researches found"
            },
            status_code=404
        )

    return JSONResponse(
        content={
            "result": True,
            "response": filtered_researches
        },
        status_code=200
    )


@router.post("/react/user_stats")
async def react_user_stats(username: str, password: str):
    user_id = DBM.users.password_match(username, password)
    if not user_id:
        return JSONResponse(
            content={
                "result": False,
                "response": "Failed authentication"
            },
            status_code=401
        )

    return JSONResponse(
        content={
            "result": True,
            "response": DBM.users.get_info(username)
        },
        status_code=200
    )


@router.post("/react/push_sample")
async def react_push_sample(
    username: str,
    password: str,
    qr_unique_hex: str,
    research_name: str,
    collected_at: str,
    latitude: float,
    longitude: float
):
    user_id = DBM.users.password_match(username, password)
    if not user_id:
        return JSONResponse(
            content={
                "result": False,
                "response": "Failed authentication"
            },
            status_code=401
        )
    
    # '2023-10-12T14:30:00+02:00'
    try:
        collected_at = datetime.fromisoformat(collected_at)
    except ValueError:
        return JSONResponse(
            content={
                "result": False,
                "response": "Incorrect datetime format. Use ISO: '2000-12-31T12:34:56+07:00'"
            },
            status_code=400
        )

    response = DBM.samples.new(
        qr_unique_hex,
        research_name,
        collected_at,
        (latitude, longitude),
        log=True
    )
    if response:
        return JSONResponse(
            content={
                "result": True,
                "response": response
            },
            status_code=201
        )
    else:
        return JSONResponse(
            content={
                "result": False,
                "response": response
            },
            status_code=500
        )