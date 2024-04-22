from test.utils import *
from routers.api_users import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = get_db_test
app.dependency_overrides[get_current_user] = get_current_user_test


def test_return_user(fake_db):
    response = client.get("/api/user/get_user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'ivan'
    assert response.json()['email'] == 'ivan@email.com'
    assert response.json()['first_name'] == 'Ivan'
    assert response.json()['last_name'] == 'Arizanovic'
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '(111)-111-1111'


def test_change_password_success(fake_db):
    response = client.put("/api/user/password", json={"password": "testpassword",
                                                  "new_password": "newpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_current_password(fake_db):
    response = client.put("/api/user/password", json={"password": "wrong_password",
                                                  "new_password": "newpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change'}


def test_change_phone_number_success(fake_db):
    response = client.put("/api/user/phonenumber/2222222222")
    assert response.status_code == status.HTTP_204_NO_CONTENT


