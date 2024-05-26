from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt
import httpx

from fastapi.routing import APIRouter

from database import SessionLocal, engine
from models import Base, User
from schemas import Token, TokenData, UserInDB
from utils import verify_password, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

Base.metadata.create_all(bind=engine)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class InvalidPasswordException(Exception):
    pass

async def authenticate_user(username: str, password: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://62.109.17.249:8000/users/password_match/{username}/{password}")
        if response.status_code == 200:
            return {'user_id': response.json().get("user_id"), 'user_status': response.json().get("user_status")}
        elif (response.status_code == 401):
            raise InvalidPasswordException
        else:
            raise Exception("Something went wrong")

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user_data = await authenticate_user(form_data.username, form_data.password)
    except InvalidPasswordException:
        return JSONResponse(status_code=401, content={"message": "Wrong password"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        user = User(username=form_data.username)
        db.add(user)
        db.commit()
        db.refresh(user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"user_id": user.username, "user_status": user_data['user_status']}, expires_delta=access_token_expires)
    refresh_token = create_access_token(data={"user_id": user.username, "user_status": user_data['user_status']}, expires_delta=timedelta(days=7))
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired refresh token")

    username = payload.get("user_id")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if user is None or user.refresh_token != refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"user_id": user.username, "user_status": payload.get('user_status')}, expires_delta=access_token_expires)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/revoke", status_code=204)
async def revoke_refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("user_id")
    user = db.query(User).filter(User.username == username).first()
    if user and user.refresh_token == refresh_token:
        user.refresh_token = None
        db.commit()


@router.get('/check/{token}')
async def check_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
