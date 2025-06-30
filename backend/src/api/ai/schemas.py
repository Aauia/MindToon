from pydantic import BaseModel, Field
from typing import List, Optional, Any, Literal
from enum import Enum
from api.chat.models import WorldType

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

class Dialogue(BaseModel):
    speaker: str
    text: str
    type: Literal["speech", "thought", "narration", "sound_effect", "scream"] = "speech"

class FrameDescription(BaseModel):
    frame_number: int
    description: str
    dialogues: List[Dialogue]

class ScenarioSchema2(BaseModel):
    title: str
    genre: str
    characters: List[str]
    art_style: str
    frames: List[FrameDescription]

class ComicGenerationRequest(BaseModel):
    concept: str
    genre: str = "adventure"
    art_style: str = "comic book"
    world_type: WorldType = WorldType.IMAGINATION_WORLD

class ComicSaveRequest(BaseModel):
    title: str
    concept: str
    genre: str = "adventure"
    art_style: str = "comic book"
    world_type: WorldType = WorldType.IMAGINATION_WORLD
    image_base64: str
    panels_data: str = "{}"
    is_favorite: bool = False
    is_public: bool = False

class ComicGenerationResponse(BaseModel):
    title: str
    concept: str
    genre: str
    art_style: str
    world_type: WorldType
    image_base64: str
    panels_data: dict
    created_at: str

class WorldComicsRequest(BaseModel):
    world_type: WorldType
    page: int = 1
    per_page: int = 10
    favorites_only: bool = False

class WorldStatsResponse(BaseModel):
    world_type: WorldType
    total_comics: int
    favorite_comics: int
    public_comics: int

class ComicCollectionRequest(BaseModel):
    name: str
    description: Optional[str] = None
    world_type: WorldType

class ComicCollectionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    world_type: WorldType
    comic_count: int
    created_at: str