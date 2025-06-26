import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from api.db import init_db, get_session, engine
from api.chat.routing import router as chat_router
from api.auth.routing import router as auth_router
from api.auth.models import User  # Import User model to create table
from api.auth.utils import get_password_hash
from sqlmodel import Session, select
from typing import List

from dotenv import load_dotenv
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    #before app startapp
    init_db()
    # Ensure admin user exists
    with Session(engine) as session:
        admin = session.exec(select(User).where(User.username == "admin")).first()
        if not admin:
            admin_user = User(
                username="admin",
                email="adminof@mindtoon",
                full_name="Admin User",
                hashed_password=get_password_hash("ad123"),
                is_admin=True
            )
            session.add(admin_user)
            session.commit()
    yield
    #after app startapp


app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(chat_router, prefix="/api/chats", tags=["chats"])

MY_PROJECT = os.environ.get("MY_PROJECT") or "this is my project"
API_KEY = os.environ.get("API_KEY")


@app.get("/")
def read_index():
    return {"Hello": "World","project_name": API_KEY}

@app.get("/health")
def healthcheck():
    return {"status": "ok"}



