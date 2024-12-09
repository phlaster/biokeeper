import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from fastapi.testclient import TestClient
from src.main import app, create_access_token, create_refresh_token
from src.crypto import hash_password
from sqlalchemy.orm import Session
from src.models import User, UserRole
import src.crud as crud

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    # Создайте временную базу данных для тестирования
    from src.database import engine, SessionLocal
    from src.models import Base
    db = SessionLocal()
    yield db
    db.close()

#Пока что закомментил эти фикстуры, их надо переписать
@pytest.fixture(scope="module")
def test_user(db: Session):
    role = UserRole(name="test_role")
    db.add(role)
    db.commit()
    db.refresh(role)
    user = User(username="testuser", email="testuser@example.com", password_hash=hash_password("c0Rrect_password!"), role_id=role.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    user.raw_password = "c0Rrect_password!"
    return user

@pytest.fixture(scope="module")
def access_token(test_user):
    return create_access_token(test_user)

@pytest.fixture(scope="module")
def refresh_token(test_user):
    return create_refresh_token(test_user)
# Пока что закомментил эти тесты, так как хз, нужны ли они

# 1. Тесты для запросов с отсутствующими полями (все комбинации)
@pytest.mark.parametrize("missing_field", [
    {"email": "user@example.com", "password": "password123", "password2": "password123"},
    {"username": "user", "password": "password123", "password2": "password123"},
    {"username": "user", "email": "user@example.com", "password2": "password123"},
    {"username": "user", "email": "user@example.com", "password": "password123"}
])
def test_create_user_missing_fields(missing_field):
    response = client.post("/create", json=missing_field)
    assert response.status_code == 422

# 2. Тесты для запросов с невалидным паролем
@pytest.mark.parametrize("password", [
    "short",                # недостаточное количество символов
    "noSpecialChar123",     # нет спецсимвола
    "NoNumberSpecial!",     # нет цифры
])
def test_create_user_invalid_password(password):
    response = client.post("/create", json={
        "username": "user", "email": "user@example.com",
        "password": password, "password2": password
    })
    assert response.status_code == 422

# 3. Тест для запроса с уже зарегистрированным юзернеймом

def test_create_user_existing_username():
    client.post("/create", json={
        "username": "existing_user", "email": "new_user@example.com",
        "password": "c0Rrect_password!", "password2": "c0Rrect_password!"
    })
    response = client.post("/create", json={
        "username": "existing_user", "email": "another_user@example.com",
        "password": "c0Rrect_password!", "password2": "c0Rrect_password!"
    })
    assert response.status_code == 400

# 4. Тест для запроса с уже зарегистрированным email

def test_create_user_existing_email():
    client.post("/create", json={
        "username": "new_user", "email": "existing_user@example.com",
        "password": "c0Rrect_password!", "password2": "c0Rrect_password!"
    })
    response = client.post("/create", json={
        "username": "another_user", "email": "existing_user@example.com",
        "password": "c0Rrect_password!", "password2": "c0Rrect_password!"
    })
    assert response.status_code == 400

# 5. Тест для запроса с разными паролями

def test_create_user_different_passwords():
    response = client.post("/create", json={
        "username": "user", "email": "user@example.com",
        "password": "c0Rrect_password!", "password2": "different_password!"
    })
    assert response.status_code == 422

# 6. Тест для полностью валидного запроса
def test_create_user_valid():
    response = client.post("/create", json={
        "username": "correct_user", "email": "correct_user@example.com",
        "password": "c0Rrect_password!", "password2": "c0Rrect_password!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "correct_user"
    assert data["email"] == "correct_user@example.com"
# Тест логина с неправильным паролем

def test_login_incorrect_password(test_user):
    response = client.post("/token", data={"username": test_user.username, "password": "incorrect_password"})
    assert response.status_code == 401

#Тест логина с правильным паролем
def test_login_correct_password(test_user):
    response = client.post("/token", data={"username": test_user.username, "password": test_user.raw_password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # TODO
    # не нужно передавать захешированный пароль, это тест логина, 
    # он просто по паролю производится, надо передавать такой же пароль как 
    # и в предыдущем тесте (при создании пользователя)
    # здесь надо протестить:
    # 1) Тест логина с неправильным паролем
    # 2) Тест логина с правильным паролем
    #
    # Точнее разделить это на несколько тестов, те которые ожидаем провальными делать 
    # c декоратором @pytest.mark.xfail

# def test_refresh_token(db, refresh_token):
#     # TODO: разобраться как соединять разные тесты между собой, 
#     # в частности как взять рефреш токен сюда, разобраться в ФИКСТУРАХ
#     response = client.post("/refresh", json={"refresh_token": refresh_token})
#     assert response.status_code == 200
#     data = response.json()
#     assert "access_token" in data

# def test_get_my_sessions(db, access_token):
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = client.get("/my_sessions", headers=headers)
#     assert response.status_code == 200
#     data = response.json()
#     assert "sessions" in data

# def test_logout(db, access_token, refresh_token):
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = client.post("/logout", headers=headers, json={"refresh_token": refresh_token})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["message"] == "Session was successfully deleted"

# def test_revoke_session(db, access_token, test_user):
#     # Сначала создаем сессию
#     hashed_refresh_token = hash_token(refresh_token)
#     session = crud.create_session(db, test_user.id, hashed_refresh_token, "127.0.0.1", "Test User Agent")
    
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = client.post("/revoke", headers=headers, json={"sessionId": session.id})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["message"] == "Session was successfully deleted"
