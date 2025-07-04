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
    x_coord: Optional[int] = 0
    y_coord: Optional[int] = 0
    panel_width: Optional[int] = 400
    panel_height: Optional[int] = 300

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
    emotion: Literal["normal", "shouting", "whispering", "thoughtful", "angry", "excited", "sad"] = "normal"
    position: Literal["left", "right", "center", "top", "bottom"] = "center"
    x_coord: Optional[int] = None
    y_coord: Optional[int] = None

class FrameDescription(BaseModel):
    frame_number: int
    description: str
    dialogues: List[Dialogue]
    camera_shot: Literal["close-up", "medium shot", "wide shot", "dutch angle", "bird's eye", "worm's eye", "over-shoulder"] = "medium shot"
    speaker_position_in_panel: Literal["left_character", "right_character", "center", "background", "foreground"] = "center"
    dialogue_emotion: Literal["normal", "shouting", "whispering", "thoughtful", "angry", "excited", "sad"] = "normal"
    sfx: List[str] = Field(default_factory=list)  # Sound effects like ["CRASH", "ZAP"]
    panel_emphasis: bool = False  # Whether this panel should be larger/more prominent
    mood: Literal["dramatic", "comedic", "mysterious", "action", "peaceful", "tense", "romantic"] = "dramatic"

class ScenarioSchema2(BaseModel):
    title: str
    genre: str
    characters: List[str]
    art_style: str
    frames: List[FrameDescription]
    story_arc: str = "complete"  # Whether it's a complete story or part of series
    target_audience: Literal["all_ages", "teen", "adult"] = "all_ages"

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
    image_base64: Optional[str] = None  # Made optional since backend generates the image
    panels_data: str = "{}"
    is_favorite: bool = False
    is_public: bool = False
    include_detailed_scenario: bool = False  # Optional, generate detailed narrative story

class DetailedScenarioChapter(BaseModel):
    """Represents a chapter/section of the detailed narrative that corresponds to comic panels"""
    chapter_number: int
    title: str
    narrative: str  # Rich, detailed narrative text
    panel_reference: int  # Which comic panel this corresponds to
    character_thoughts: Optional[str] = None  # Internal monologue/thoughts
    world_building: Optional[str] = None  # Environmental and world details
    emotional_context: Optional[str] = None  # Emotional subtext and character development

class DetailedScenarioSchema(BaseModel):
    """Enhanced narrative scenario that complements the comic"""
    title: str
    genre: str
    art_style: str
    characters: List[str]
    
    # Story structure
    premise: str  # Detailed story premise
    setting: str  # Rich world and setting description
    themes: List[str]  # Major themes explored
    
    # Narrative chapters (corresponding to comic panels)
    chapters: List[DetailedScenarioChapter]
    
    # Story metadata
   
    word_count: int = 0
    reading_time_minutes: int = 0
    
    # Connection to comic
    comic_panel_count: int = 6
    narrative_style: str  # Literary style description

class ScenarioSaveRequest(BaseModel):
    """Request model for saving detailed scenarios to database"""
    comic_id: int  # Links to the comic this scenario complements
    title: str
    concept: str
    genre: str
    art_style: str
    world_type: WorldType = WorldType.IMAGINATION_WORLD
    scenario_data: str  # JSON string of the detailed scenario
    word_count: int = 0
    reading_time_minutes: int = 0

class ComicGenerationResponse(BaseModel):
    id: Optional[int] = None  # Add comic ID
    title: str
    concept: str
    genre: str
    art_style: str
    world_type: WorldType
    image_url: Optional[str] = None
    image_base64: Optional[str] = None 
    panels_data: List[dict]
    created_at: str
    is_favorite: Optional[bool] = None
    is_public: Optional[bool] = None
    has_detailed_scenario: Optional[bool] = None

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
    total_collections: int = 0  # Add missing field

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