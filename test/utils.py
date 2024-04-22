from main import app
from fastapi.testclient import TestClient
from test.database import get_db_test, fake_db, Todos, Users


client = TestClient(app)

def get_current_user_test():
    return {'username': 'ivan', 'id': 1, 'user_role': 'admin'}


