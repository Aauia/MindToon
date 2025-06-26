from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from api.db import get_session
from .models import User, UserCreate, UserRead, Token
from .utils import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user
)
from typing import List

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    # Check if username already exists
    existing_user = session.exec(
        select(User).where(User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = session.exec(
        select(User).where(User.email == user.email)
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password)
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/users", response_model=List[UserRead])
def get_all_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users 