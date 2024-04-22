from fastapi import APIRouter, Depends, HTTPException, Path, status, Query, Body
# Parameters
from typing import Annotated
from pydantic import BaseModel, Field
# Database
from database import get_db, Users
from sqlalchemy.orm import Session
# Auth
from .api_auth import get_current_user
from werkzeug.security import generate_password_hash, check_password_hash

router = APIRouter(
    prefix='/api/user',
    tags=['api_user']
)

# Set dependencies
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# Models
class ModelCreateUser(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


class ModelUserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


@router.post("/test_fastapi1", status_code=status.HTTP_201_CREATED)
async def test_fastapi1(
    user: user_dependency,                         # inherent param (not able to change in api)
    db: db_dependency,                             # inherent param (not able to change in api)
    required_param: str,
    optional_param: str | None = None,
    param_with_default: int = 0,
    book_id: int = Path(gt=0),                     # Required and greater then 0
    published_date: int = Query(gt=1999, lt=2031)  # Required and in range 2000-2030
):
    pass


@router.post("/test_fastapi2", status_code=status.HTTP_201_CREATED)
async def test_fastapi2(user_pass: ModelUserVerification):   # Required param as string/json (Request body)
    pass



# Routers
@router.get('/get_user', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: ModelCreateUser, q1: str, q2: str | None = None, skip: int = 0):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=generate_password_hash(create_user_request.password),
        is_active=True,
        phone_number=create_user_request.phone_number
    )
    db.add(create_user_model)
    try:
        db.commit()
    except:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Username exists')


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency,
                          user_verification: ModelUserVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    # if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
    if not check_password_hash(user_model.hashed_password, user_verification.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Error on password change')
    # user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    user_model.hashed_password = generate_password_hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phonenumber(user: user_dependency, db: db_dependency,
                          phone_number: str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()






