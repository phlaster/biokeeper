from sqlalchemy.orm import Session, joinedload
import models, schemas
import datetime
from crypto import hash_password, check_password

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).\
        options(joinedload(models.User.role)).\
        filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).\
        options(joinedload(models.User.role)).\
        filter(models.User.username == username).first()
    
def get_user_by_id(db: Session, id: int):
    return db.query(models.User).\
        options(joinedload(models.User.role)).\
        filter(models.User.id == id).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash= hash_password(user.password),
        role_id = None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_session(db, user_id, refresh_token, devide_ip, device_info):
    db_session = models.Session(
        user_id = user_id,
        refresh_token_hash = refresh_token,
        device_ip = devide_ip,
        device_info = device_info,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session_by_refresh_token_hash(db, refresh_token_hash : str):
    return db.query(models.Session).\
            options(joinedload(models.Session.user)).\
            filter(models.Session.refresh_token_hash == refresh_token_hash).first()

def get_session_by_id(db, sessionId : int):
    return db.query(models.Session).\
            options(joinedload(models.Session.user)).\
            filter(models.Session.id == sessionId).first()

def get_sessions_by_user_id(db, user_id : int):
    return db.query(models.Session).\
            filter(models.Session.user_id == user_id).all()

def update_session_timestamp(db: Session, session: models.Session):
    session.updated_at = datetime.datetime.now(datetime.timezone.utc)  # Устанавливаем текущее время в UTC формате
    db.commit()  # Сохраняем изменения в базе данных
    db.refresh(session)  # Обновляем объект session в текущей сессии
    return session

def get_role_by_name(db: Session, name):
    return db.query(models.UserRole).filter(models.UserRole.name == name).first()