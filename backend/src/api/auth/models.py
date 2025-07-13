from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr

if TYPE_CHECKING:
    from api.chat.models import ComicsPage

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    disabled: bool = False


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    comics: List["ComicsPage"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime

class UserDeletionConfirmation(SQLModel):
    """Schema for confirming account deletion - requires explicit confirmation"""
    confirm_deletion: bool = Field(description="Must be true to confirm deletion")
    username_confirmation: str = Field(description="Must match the user's username exactly")
    understanding_acknowledgment: str = Field(
        description="Must be exactly 'I understand this action is permanent and irreversible'"
    )

class UserDeletionSummary(SQLModel):
    """Summary of what was deleted"""
    success: bool
    username: str
    message: str
    deletion_summary: dict
    warning: str

class Token(SQLModel):
    access_token: str
    refresh_token: str 
    token_type: str

class TokenData(SQLModel):
    username: Optional[str] = None 