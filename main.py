from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from routers import api_auth, api_todos, api_admin, api_users
from routers import gui_user, gui_todos

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


app.include_router(api_auth.router)
app.include_router(api_todos.router)
app.include_router(api_admin.router)
app.include_router(api_users.router)


app.include_router(gui_user.router)
app.include_router(gui_todos.router)
# app.include_router(gui_users.router)
