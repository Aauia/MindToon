from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, DateTime, JSON, Column
from typing import Optional
from sqlalchemy import JSON as SA_JSON

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

class ComicsPage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_message: str
    genre: str
    art_style: str
    scenario: str
    panels: list = Field(sa_column=Column(SA_JSON))
    sheet_url: str

class ComicsPageCreate(SQLModel):
    user_message: str
    genre: str
    art_style: str
    scenario: str
    panels: list
    sheet_url: str
