from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Cookie
# Parameters
from typing import Annotated
from pydantic import BaseModel
# Database
from database import get_db, Users
from sqlalchemy.orm import Session
# Auth
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime

router = APIRouter(
    prefix='/api/auth',
    tags=['api_auth']
)

# JWT configuration
# Key is got from: openssl rand -hex 32
SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'

# Configure authentication in docs page
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/api/auth/token')
# Set dependencies
db_dependency = Annotated[Session, Depends(get_db)]


# Models
class ModelToken(BaseModel):
    access_token: str
    token_type: str


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    # If token is not present return None
    if token is None:
        return

    # Check the token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('user_name')
        user_id: int = payload.get('user_id')
        user_role: str = payload.get('user_role')
        if username is None or user_id is None:
            return
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        return


# Routers
@router.get("/get_user_from_token/", status_code=status.HTTP_200_OK)
async def get_user_from_token(token: Annotated[str, Depends(oauth2_bearer)]):
    current_user = get_current_user(token)
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    return current_user


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    # if not bcrypt_context.verify(password, user.hashed_password):
    if not check_password_hash(user.hashed_password, password):
        return False
    return user


@router.post("/token", response_model=ModelToken)
async def create_token(#response: Response,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')

    token = jwt.encode({
        'user_name': user.username,
        'user_id': user.id,
        'user_role': user.role,
        'exp': datetime.now() + timedelta(minutes=20)
    }, SECRET_KEY, algorithm=ALGORITHM)

    # response.set_cookie(key="access_token", value=token, httponly=True)
    return {'access_token': token, 'token_type': 'bearer'}

