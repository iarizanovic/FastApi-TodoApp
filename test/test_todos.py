from routers.api_todos import get_db, get_current_user
from fastapi import status
from test.utils import *

app.dependency_overrides[get_db] = get_db_test
app.dependency_overrides[get_current_user] = get_current_user_test


def test_read_all_authenticated(fake_db):
    response = client.get("/api/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}]


def test_read_one_authenticated(fake_db):
    response = client.get("/api/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}


def test_read_one_authenticated_not_found():
    response = client.get("/api/todo/999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


def test_create_todo(fake_db):
    request_data={
        'title': 'New Todo!',
        'description':'New todo description',
        'priority': 5,
        'complete': False,
    }

    response = client.post('/api/todo/', json=request_data)
    assert response.status_code == 201

    model = fake_db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_update_todo(fake_db):
    request_data={
        'title':'Change the title of the todo already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/api/todo/1', json=request_data)
    assert response.status_code == 204
    model = fake_db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == 'Change the title of the todo already saved!'

def test_update_todo_not_found(fake_db):
    request_data={
        'title':'Change the title of the todo already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/api/todo/999', json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


def test_delete_todo(fake_db):
    response = client.delete('/api/todo/1')
    assert response.status_code == 204
    model = fake_db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete('/api/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}




