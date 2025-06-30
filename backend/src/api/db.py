import os
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import text

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise NotImplementedError("`DATABASE_URL` environment variable is not set")

engine = create_engine(DATABASE_URL)

def recreate_tables():
    """Drop and recreate all tables - use with caution as this destroys data"""
    print("WARNING: Dropping and recreating all tables...")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    print("Tables recreated successfully")

def init_db():
    print("Creating database models...")
    try:
        SQLModel.metadata.create_all(engine)
        print("Database models created successfully")
    except Exception as e:
        print(f"Error creating database models: {e}")
        raise

# api routes
def get_session():
    with Session(engine) as session:
        yield session
