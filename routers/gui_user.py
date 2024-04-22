from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
# Parameters
from typing import Optional
from pydantic import BaseModel, Field
# Database
from database import get_db, Todos, Users
from sqlalchemy.orm import Session
# Auth
from routers.api_auth import create_token, get_current_user
from werkzeug.security import generate_password_hash, check_password_hash

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={401: {"user": "Not authorized"}}
)
templates = Jinja2Templates(directory="templates")


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str = Field(min_length=6)


# Routers
@router.get("/login", response_class=HTMLResponse)
async def authentication_page(request: Request):
    # print("login_get", request.cookies.get("access_token"))
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, email: str = Form(...),
                password: str = Form(...), db: Session = Depends(get_db)):
    try:
        form = OAuth2PasswordRequestForm(username=email, password=password)
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        token = await create_token(form_data=form, db=db)
        if token:
            # print("login_post", token['access_token'])
            response.set_cookie(key="access_token", value=token['access_token'], httponly=True)
            return response
        else:
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@router.get("/logout")
async def logout(request: Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, email: str = Form(...), username: str = Form(...),
                        firstname: str = Form(...), lastname: str = Form(...),
                        password: str = Form(...), password_verify: str = Form(...),
                        db: Session = Depends(get_db)):
    validation_username = db.query(Users).filter(Users.username == username).first()
    validation_email = db.query(Users).filter(Users.email == email).first()

    if password != password_verify or validation_username is not None or validation_email is not None:
        msg = "Invalid registration request"
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})

    user_model = Users()
    user_model.username = username
    user_model.email = email
    user_model.first_name = firstname
    user_model.last_name = lastname

    hash_password = generate_password_hash(password)
    user_model.hashed_password = hash_password
    user_model.is_active = True

    db.add(user_model)
    db.commit()

    msg = "User successfully created"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@router.get("/password", response_class=HTMLResponse)
async def change_password_get(request: Request):
    user = get_current_user(request.cookies.get("access_token"))
    if user is None:
        return RedirectResponse(url="/user/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("change_pass.html", {"request": request, "user": user})


@router.post("/password", response_class=HTMLResponse)
async def change_password_post(request: Request, username: str = Form(...),
                               old_pass: str = Form(...), new_pass: str = Form(...),
                               db: Session = Depends(get_db)):
    user = get_current_user(request.cookies.get("access_token"))
    if user is None:
        return RedirectResponse(url="/user/login", status_code=status.HTTP_302_FOUND)

    msg = "Invalid username or password"

    user_data = db.query(Users).filter(Users.username == username).first()
    if user_data is not None:
        if username == user_data.username and check_password_hash(user_data.hashed_password, old_pass):
            user_data.hashed_password = generate_password_hash(new_pass)
            db.add(user_data)
            db.commit()
            msg = 'Password updated'

    return templates.TemplateResponse("change_pass.html", {"request": request, "user": user, "msg": msg})

