# Enhanced Scenario System

## Overview

The Enhanced Scenario System transforms the MindToon comic generation experience by providing users with **both visual comics AND rich, detailed narrative stories**. When a user creates a comic, they now receive:

1. **🎨 Visual Comic**: The traditional 6-panel comic with images and dialogue
2. **📖 Detailed Narrative**: A complementary literary story (1,500-2,000 words) that expands on the comic with rich character development, world-building, and thematic depth

## What's New

### 📚 Enhanced `generate_scenario()` Function

The `generate_scenario()` function has been completely redesigned:

**Before:**
```python
def generate_scenario(prompt: str) -> ScenarioSchema
# Simple genre/scenario output
```

**After:**
```python  
def generate_scenario(prompt: str, genre: str = None, art_style: str = None) -> DetailedScenarioSchema
# Rich, literary narrative with 6 chapters mapping to comic panels
```

### 🎯 Key Features

1. **Literary Quality**: Generates 1,500-2,000 word narratives with sophisticated prose
2. **Panel Mapping**: Each narrative chapter corresponds to a comic panel
3. **Genre Integration**: Uses the same genre/art style system as comics for consistency
4. **Character Development**: Includes character thoughts, emotions, and growth arcs
5. **World Building**: Rich environmental descriptions and atmospheric details
6. **Supabase Storage**: Full database integration for saving and retrieving scenarios

## Architecture

### 📝 New Database Models

#### `DetailedScenario` (SQLModel)
```python
class DetailedScenario(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    comic_id: int = Field(foreign_key="comicspage.id")  # Links to comic
    title: str
    concept: str 
    genre: str
    art_style: str
    world_type: WorldType
    scenario_data: str  # JSON of DetailedScenarioSchema
    word_count: int
    reading_time_minutes: int
    user_id: int = Field(foreign_key="user.id")
    # ... timestamps and metadata
```

### 🔗 New API Schemas

#### `DetailedScenarioSchema`
```python
class DetailedScenarioSchema(BaseModel):
    title: str
    genre: str
    art_style: str
    characters: List[str]
    premise: str  # Rich story premise
    setting: str  # Detailed world description
    themes: List[str]  # Story themes
    chapters: List[DetailedScenarioChapter]  # 6 chapters = 6 panels
    word_count: int
    reading_time_minutes: int
    narrative_style: str
```

#### `DetailedScenarioChapter`
```python
class DetailedScenarioChapter(BaseModel):
    chapter_number: int
    title: str
    narrative: str  # Rich narrative text (200-400 words)
    panel_reference: int  # Which comic panel this maps to
    character_thoughts: Optional[str]  # Internal monologue
    world_building: Optional[str]  # Environmental details
    emotional_context: Optional[str]  # Character emotions
```

## Integration

### 🎬 Enhanced Comic Generation

The `generate_complete_comic()` function now returns **three items**:

```python
comic_page, comic_sheet, detailed_scenario = generate_complete_comic(
    concept="A young wizard discovers a magical book",
    genre="fantasy",
    art_style="watercolor"
)
```

**Returns:**
- `comic_page`: Traditional comic panel data
- `comic_sheet`: Visual comic image
- `detailed_scenario`: Rich narrative story (NEW!)

### 🔌 New API Endpoints

All endpoints require authentication and follow RESTful patterns:

#### Save Scenario
```
POST /api/supabase/scenarios/save
Body: ScenarioSaveRequest
```

#### Get Scenario by Comic
```
GET /api/supabase/scenarios/comic/{comic_id}
```

#### Get User Scenarios
```
GET /api/supabase/scenarios/user/{user_id}?limit=20&offset=0
```

#### Update Scenario
```
PUT /api/supabase/scenarios/{scenario_id}
Body: {"is_favorite": true, "is_public": false}
```

#### Delete Scenario  
```
DELETE /api/supabase/scenarios/{scenario_id}
```

## Panel-to-Chapter Mapping

The system creates a **perfect 1:1 mapping** between comic panels and narrative chapters:

| Comic Panel | Narrative Chapter | Purpose |
|-------------|------------------|---------|
| Panel 1 | Chapter 1: "The Ordinary World" | Character/world introduction |
| Panel 2 | Chapter 2: "The Call to Adventure" | Inciting incident |
| Panel 3 | Chapter 3: "Crossing the Threshold" | Character takes action |
| Panel 4 | Chapter 4: "The Ordeal" | Climactic confrontation |
| Panel 5 | Chapter 5: "The Revelation" | Aftermath and realization |
| Panel 6 | Chapter 6: "The Return" | Resolution and conclusion |

## Genre Integration

The scenario system uses the **same genre system** as comics:

- **Horror**: Dark, foreboding narratives with psychological tension
- **Romance**: Tender, emotional stories with relationship focus  
- **Sci-Fi**: Futuristic tales with technological and cosmic themes
- **Fantasy**: Magical narratives with mystical world-building
- **Comedy**: Lighthearted, humorous stories with wit
- **Action**: Dynamic, intense narratives with excitement
- **Mystery**: Suspenseful stories with investigative elements
- **Drama**: Character-focused, emotionally rich narratives

## Usage Examples

### Basic Scenario Generation
```python
from api.ai.services import generate_scenario

detailed_scenario = generate_scenario(
    prompt="A robot learns to love in a post-apocalyptic world",
    genre="sci-fi", 
    art_style="comic book"
)

print(f"Title: {detailed_scenario.title}")
print(f"Word Count: {detailed_scenario.word_count}")
print(f"Reading Time: {detailed_scenario.reading_time_minutes} minutes")

for chapter in detailed_scenario.chapters:
    print(f"Chapter {chapter.chapter_number}: {chapter.title}")
    print(f"Narrative: {chapter.narrative[:100]}...")
```

### Complete Comic + Scenario
```python
from api.ai.services import generate_complete_comic

comic_page, comic_sheet, scenario = generate_complete_comic(
    concept="Two detectives solve a cyberpunk murder",
    genre="mystery",
    art_style="anime"
)

# Save comic image
comic_sheet.save("my_comic.png")

# Access narrative
print(f"Story: {scenario.title}")
for chapter in scenario.chapters:
    print(f"Chapter {chapter.chapter_number}: {chapter.narrative}")
```

### Supabase Integration
```python
from api.ai.schemas import ScenarioSaveRequest
import json

# Prepare scenario for storage
save_request = ScenarioSaveRequest(
    comic_id=123,
    title=scenario.title,
    concept="Original user prompt",
    genre=scenario.genre,
    art_style=scenario.art_style,
    scenario_data=json.dumps(scenario.dict()),
    word_count=scenario.word_count,
    reading_time_minutes=scenario.reading_time_minutes
)

# Save via API endpoint (requires authentication)
response = requests.post("/api/supabase/scenarios/save", json=save_request.dict())
```

## Testing

Run the comprehensive test suite:

```bash
cd backend
python test_enhanced_scenarios.py
```

This will test:
- ✅ Enhanced scenario generation with different genres
- ✅ Complete comic + scenario generation  
- ✅ Panel-to-chapter mapping verification
- ✅ Supabase storage preparation
- ✅ API request formatting

## Database Setup

### 1. Create Supabase Table

```sql
CREATE TABLE detailedscenario (
    id SERIAL PRIMARY KEY,
    comic_id INTEGER REFERENCES comicspage(id),
    title VARCHAR(200) NOT NULL,
    concept VARCHAR(1000) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    art_style VARCHAR(100) NOT NULL,
    world_type VARCHAR(50) NOT NULL,
    scenario_data TEXT NOT NULL,
    word_count INTEGER DEFAULT 0,
    reading_time_minutes INTEGER DEFAULT 0,
    user_id INTEGER REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    is_favorite BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE
);
```

### 2. Set Up Indexes
```sql
CREATE INDEX idx_detailedscenario_comic_id ON detailedscenario(comic_id);
CREATE INDEX idx_detailedscenario_user_id ON detailedscenario(user_id);
CREATE INDEX idx_detailedscenario_genre ON detailedscenario(genre);
```

## Frontend Integration

The enhanced system enables new frontend features:

### 📱 Dual Content Display
- **Comic View**: Traditional comic panel display
- **Story View**: Rich text narrative with chapter navigation
- **Split View**: Side-by-side comic and corresponding chapter

### 🔄 Interactive Features
- **Panel Highlighting**: Click comic panel → highlight corresponding chapter
- **Chapter Navigation**: Click chapter → highlight corresponding panel  
- **Reading Mode**: Immersive full-screen narrative reading
- **Favorites**: Save favorite scenarios separately from comics

### 📊 Analytics
- **Reading Time Tracking**: Monitor how long users spend reading
- **Engagement Metrics**: Which genres get read most
- **Content Preferences**: Comic vs. narrative preference patterns

## Benefits

### 👥 For Users
- **Richer Experience**: Get both visual and literary content
- **Deeper Engagement**: More time spent with created content
- **Better Understanding**: Narrative explains comic context
- **Replay Value**: Read scenario after viewing comic for new insights

### 🎯 For the Platform  
- **Differentiation**: Unique feature not available elsewhere
- **Engagement**: Longer session times with dual content
- **Content Value**: More content per generation request
- **Educational**: Helps users understand storytelling structure

## Future Enhancements

### 🔮 Planned Features
1. **Audio Narration**: Text-to-speech of scenarios
2. **Interactive Stories**: Choose-your-own-adventure scenarios  
3. **Character Deep Dives**: Extended character background stories
4. **World Expansion**: Multi-comic narrative universes
5. **Collaborative Stories**: Multiple users contributing to scenarios
6. **Scenario Sharing**: Public scenario library
7. **Genre Mixing**: Hybrid genre narratives
8. **Custom Themes**: User-defined story themes

---

## Quick Start

1. **Generate Enhanced Scenario:**
   ```python
   scenario = generate_scenario("Your prompt", "genre", "art_style")
   ```

2. **Generate Complete Comic + Scenario:**
   ```python
   comic, image, story = generate_complete_comic("prompt", "genre", "style")
   ```

3. **Test the System:**
   ```bash
   python test_enhanced_scenarios.py
   ```

4. **Set Up Database:**
   ```sql
   -- Run the CREATE TABLE statement above in Supabase
   ```

The Enhanced Scenario System is now ready to provide users with an unprecedented storytelling experience that combines visual comics with rich literary narratives! 🎉 