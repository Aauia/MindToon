from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, DateTime, JSON, Column, Relationship
from typing import Optional, List
from sqlalchemy import JSON as SA_JSON
from api.auth.models import User
from enum import Enum

def get_utc_now():
    return datetime.now().replace(tzinfo=timezone.utc)


class ChatMessagePayload(SQLModel):
    # pydantic model
    # validation
    # serializer
    message: str


class ChatMessage(SQLModel, table=True):
    # database table
    # saving,updating,getting,deleting
    # serializer

    id: int | None = Field(default=None, primary_key=True)
    message: str
    created_at: datetime = Field(
        default_factory=get_utc_now,
        sa_type=DateTime(timezone=True),  # timescaledb -> analytics api course
        primary_key=False,
        nullable=False,

    )

class ChatMessageListItem(SQLModel):
    id: int | None = Field(default=None)
    message:str
    created_at: datetime = Field(default=None)

class WorldType(str, Enum):
    """Enum for different world types"""
    DREAM_WORLD = "dream_world"
    MIND_WORLD = "mind_world"
    IMAGINATION_WORLD = "imagination_world"

class ComicsPage(SQLModel, table=True):
    """Model for storing user's created comics"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Basic comic information
    title: str = Field(max_length=200)
    concept: str = Field(max_length=1000)  # Original user prompt
    genre: str = Field(max_length=100)
    art_style: str = Field(max_length=100)
    
    # World assignment - NEW FIELD
    world_type: WorldType = Field(default=WorldType.IMAGINATION_WORLD)
    
    # Comic content
    image_url: str = Field()  # Store the comic image URL from Supabase Storage
    panels_data: str = Field()  # JSON string of panel information
    
    # User relationship
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="comics")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Optional fields
    is_favorite: bool = Field(default=False)
    is_public: bool = Field(default=False)  # For sharing comics publicly
    view_count: int = Field(default=0)
    
    class Config:
        from_attributes = True

class ComicsPageCreate(SQLModel):
    user_message: str
    genre: str
    art_style: str
    scenario: str
    panels: list
    sheet_url: str

class WorldStats(SQLModel, table=True):
    """Model for tracking statistics per world per user"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # User and world
    user_id: int = Field(foreign_key="user.id")
    world_type: WorldType = Field()
    
    # Stats
    total_comics: int = Field(default=0)
    favorite_comics: int = Field(default=0)
    public_comics: int = Field(default=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional[User] = Relationship()

class ComicCollection(SQLModel, table=True):
    """Model for organizing comics into collections within worlds"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: Optional[str] = Field(max_length=500)
    
    # World assignment
    world_type: WorldType = Field()
    
    # User relationship
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship()
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

class ComicCollectionItem(SQLModel, table=True):
    """Junction table for comics in collections"""
    id: Optional[int] = Field(default=None, primary_key=True)
    collection_id: int = Field(foreign_key="comiccollection.id")
    comic_id: int = Field(foreign_key="comicspage.id")
    order_position: int = Field(default=0)
    added_at: datetime = Field(default_factory=datetime.utcnow)
