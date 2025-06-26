import os
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise NotImplementedError("`DATABASE_URL` environment variable is not set")


DATABASE_URL

engine = create_engine(DATABASE_URL)


# database models — does not create db migrations
def init_db():
    print("creating database models")
    SQLModel.metadata.create_all(engine)


# api routes
def get_session():
    with Session(engine) as session:
        yield session
from sqlmodel import SQLModel

def init_db():
    SQLModel.metadata.create_all(engine)
