from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from werkzeug.security import generate_password_hash

from database import Base, Todos, Users
import pytest

DATABASE_URL_TEST = 'sqlite:///./todosapp_test.db'
engine_test = create_engine(
    DATABASE_URL_TEST,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
    future=True
)

SessionLocal_test = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)
Base.metadata.create_all(bind=engine_test)


def get_db_test():
    db = SessionLocal_test()
    try:
        yield db
    finally:
        db.close()


# Fixture starts on start of the testing.
# It generates first entries and removes all entries on the end
@pytest.fixture
def fake_db():
    todo = Todos(
        title="Learn to code!",
        description="Need to learn everyday!",
        priority=5,
        complete=False,
        owner_id=1,
    )
    user = Users(
        username="ivan",
        email="ivan@email.com",
        first_name="Ivan",
        last_name="Arizanovic",
        hashed_password=generate_password_hash("testpassword"),
        role="admin",
        phone_number="(111)-111-1111"
    )
    db = SessionLocal_test()
    db.add(user)
    db.add(todo)
    db.commit()
    yield db
    with engine_test.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.execute(text("DELETE FROM users;"))
        connection.commit()

