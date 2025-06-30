import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from api.db import init_db, get_session, engine, recreate_tables
from api.chat.routing import router as chat_router
from api.auth.routing import router as auth_router
from api.auth.models import User  # Import User model to create table
from api.auth.utils import get_password_hash
from sqlmodel import Session, select
from typing import List

from dotenv import load_dotenv

from pydantic import BaseModel

load_dotenv()

# Check for database reset command
if len(sys.argv) > 1 and sys.argv[1] == "--reset-db":
    print("Resetting database...")
    recreate_tables()
    # Create admin user
    with Session(engine) as session:
        admin_user = User(
            username="admin",
            email="adminof@mindtoon.com",
            full_name="Admin User",
            hashed_password=get_password_hash("ad123")
        )
        session.add(admin_user)
        session.commit()
    print("Database reset complete. Admin user created.")
    sys.exit(0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    #before app start
    init_db()
    
    # Ensure admin user exists
    with Session(engine) as session:
        admin = session.exec(select(User).where(User.username == "admin")).first()
        if not admin:
            admin_user = User(
                username="admin",
                email="adminof@mindtoon.com",
                full_name="Admin User",
                hashed_password=get_password_hash("ad123")
            )
            session.add(admin_user)
            session.commit()
            print("Created admin user successfully")
    
    yield
    #after app start


app = FastAPI(
    title="MindToon API",
    description="API for MindToon iOS App - Comic Generation and Chat Services",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for iOS app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development
        "http://localhost:8080",  # Local development
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "capacitor://localhost",   # Capacitor iOS
        "ionic://localhost",       # Ionic iOS
        "*"  # Allow all for development - remove in production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api/chats", tags=["Chat & Comics"])

MY_PROJECT = os.environ.get("MY_PROJECT") or "this is my project"
API_KEY = os.environ.get("API_KEY")

# iOS-specific endpoints
@app.get("/")
def read_index():
    return {
        "app_name": "MindToon API",
        "version": "1.0.0",
        "status": "running",
        "project_name": MY_PROJECT,
        "endpoints": {
            "auth": "/api/auth",
            "chat": "/api/chats",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
def healthcheck():
    return {"status": "ok", "service": "mindtoon-api"}

@app.get("/api/ios/config")
def get_ios_config():
    """Return iOS app configuration"""
    return {
        "api_version": "1.0.0",
        "base_url": os.environ.get("BASE_URL", "http://localhost:8000"),
        "features": {
            "authentication": True,
            "comic_generation": True,
            "chat": True
        },
        "endpoints": {
            "login": "/api/auth/token",
            "register": "/api/auth/register",
            "profile": "/api/auth/me",
            "comics": "/api/chats/scenario/comic/sheet/",
            "scenarios": "/api/chats/scenario/"
        }
    }

# Custom OpenAPI schema for better iOS documentation
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="MindToon API",
        version="1.0.0",
        description="API for MindToon iOS App - Comic Generation and Chat Services",
        routes=app.routes,
    )
    
    # Add iOS-specific info
    openapi_schema["info"]["x-ios-app"] = {
        "name": "MindToon",
        "bundle_id": "com.mindtoon.app",
        "version": "1.0.0"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

class StableDiffusionPrompt(BaseModel):
    prompt: str

