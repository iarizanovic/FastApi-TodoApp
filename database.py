from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite
DATABASE_URL = 'sqlite:///./todosapp.db'
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

# PostgreSQL
# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:samsung1@localhost:5432/TodoAppDatabase'
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# MySQL
# SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:samsung1@127.0.0.1:3306/TodoAppDatabase'
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create the session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)


# Start the session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)


class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
