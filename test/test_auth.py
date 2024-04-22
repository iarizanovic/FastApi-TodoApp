from fastapi import status, HTTPException
import pytest
from jose import jwt

from test.utils import *
from routers.api_auth import get_db, authenticate_user, create_token, SECRET_KEY, ALGORITHM, get_current_user, get_user_from_token

app.dependency_overrides[get_db] = get_db_test


def test_authenticate_user(fake_db):
    user = fake_db.query(Users).filter(Users.id == 1).first()

    authenticated_user = authenticate_user(user.username, 'testpassword', fake_db)
    assert authenticated_user is not None
    assert authenticated_user.username == user.username

    non_existent_user = authenticate_user('WrongUserName', 'testpassword', fake_db)
    assert non_existent_user is False

    wrong_password_user = authenticate_user(user.username, 'wrongpassword', fake_db)
    assert wrong_password_user is False

# If you test async functions, you need to use "@pytest.mark.asyncio"
@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {'user_name': 'testuser', 'user_id': 1, 'user_role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'user_role': 'admin'}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_user_from_token(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Could not validate user.'





