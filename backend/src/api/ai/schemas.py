from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessagePayload(BaseModel):
    message: str

class ChatMessage(BaseModel):
    id: int
    message: str

class ChatMessageListItem(BaseModel):
    id: int
    message: str

class EmailMessageSchema(BaseModel):
    subject: str
    contents: str
    invalid_request: Optional[bool] = False

class ScenarioSchema(BaseModel):
    genre: str
    scenario: str
    art_style: Optional[str] = None
    invalid_request: Optional[bool] = False

class ComicPanelSchema(BaseModel):
    panel: int
    image_prompt: str
    dialogue: Optional[str] = None

class ComicPanelsResponseSchema(BaseModel):
    panels: List[ComicPanelSchema]
    invalid_request: Optional[bool] = False

class ComicPanelWithImageSchema(BaseModel):
    panel: int
    image_prompt: str
    image_url: str
    dialogue: Optional[str] = None

class ComicPanelsWithImagesResponseSchema(BaseModel):
    panels: List[ComicPanelWithImageSchema]
    invalid_request: Optional[bool] = False

class ComicsPageSchema(BaseModel):
    genre: str
    art_style: str
    panels: List[ComicPanelWithImageSchema]
    invalid_request: Optional[bool] = False
