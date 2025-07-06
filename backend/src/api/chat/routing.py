from typing import Optional, List
from fastapi import APIRouter, Depends, Body, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlmodel import Session, select, func
from .models import ComicsPage, ComicCollection, ComicCollectionItem, WorldType
from api.db import get_session
from api.auth.models import User
from api.auth.utils import get_current_user
from api.ai.schemas import ScenarioSchema, ComicsPageSchema, ScenarioSchema2, ComicGenerationRequest, ComicSaveRequest, ComicGenerationResponse, WorldComicsRequest, WorldStatsResponse, ComicCollectionRequest, ComicCollectionResponse, ScenarioSaveRequest, DetailedScenarioSchema
from api.ai.services import generate_scenario, generate_comic_scenario, generate_complete_comic, generate_image_from_prompt, generate_detailed_scenario_from_comic
from pydantic import BaseModel
from datetime import datetime
import io
import base64
import json
from api.chat.models import ChatMessage, DetailedScenario

router = APIRouter()

# Request/Response models
class ComicsPagePayload(BaseModel):
    message: str
    genre: Optional[str] = None
    art_style: Optional[str] = None

class ComicRequest(BaseModel):
    concept: str  # The user's prompt - can be short or long
    genre: Optional[str] = None  # Optional, AI will determine if not provided
    art_style: Optional[str] = None  # Optional, AI will determine if not provided
    include_detailed_scenario: bool = False  # Optional, generate detailed narrative story

# Note: ComicSaveRequest is imported from api.ai.schemas and includes world_type field

class ComicResponse(BaseModel):
    id: int
    title: str
    concept: str
    genre: str
    art_style: str
    image_base64: str
    panels_data: str
    created_at: datetime
    is_favorite: bool
    is_public: bool
    view_count: int

class ComicListResponse(BaseModel):
    id: int
    title: str
    concept: str
    genre: str
    art_style: str
    created_at: datetime
    is_favorite: bool
    is_public: bool
    view_count: int
    # Excluding image_base64 for list view to reduce payload size

class ScenarioRequest(BaseModel):
    concept: str
    genre: Optional[str] = None
    art_style: Optional[str] = None

class ImageRequest(BaseModel):
    prompt: str

class ChatMessagePayload(BaseModel):
    message: str

# Existing scenario endpoint
@router.post("/scenario/", response_model=DetailedScenarioSchema)
def create_scenario(payload: ChatMessagePayload):
    response = generate_scenario(payload.message)
    return response

# Enhanced comic generation endpoint with saving
@router.post("/generate-comic")
async def generate_comic_endpoint(
    request: ComicRequest, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Generate a complete comic from a text concept and automatically save it
    Returns the comic as a PNG image
    """
    try:
        print(f"🎨 Generating comic for concept: {request.concept}")
        
        # Generate the complete comic (AI determines genre and art_style from concept)
        comic_page, comic_image, detailed_scenario = generate_complete_comic(
            concept=request.concept,
            genre=request.genre,
            art_style=request.art_style,
            include_detailed_scenario=request.include_detailed_scenario
        )
        
        # Upload comic image to Supabase Storage
        from api.supabase.client import supabase_client
        
        try:
            if supabase_client:
                # Upload to Supabase Storage
                supabase_image_url = supabase_client.upload_comic_image(current_user.id, comic_image)
                print(f"✅ Comic uploaded to Supabase Storage: {supabase_image_url}")
            else:
                supabase_image_url = None
                print("⚠️ Supabase client not available, saving base64 locally")
        except Exception as upload_error:
            print(f"⚠️ Failed to upload to Supabase: {upload_error}")
            supabase_image_url = None
        
        # Convert image to base64 as backup
        img_byte_arr = io.BytesIO()
        comic_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode()
        
        # Save comic to database using AI-determined values
        try:
            new_comic = ComicsPage(
                title=f"Comic: {request.concept[:50]}...",
                concept=request.concept,
                genre=comic_page.genre,  # Use AI-determined genre
                art_style=comic_page.art_style,  # Use AI-determined art_style
                image_url=supabase_image_url,  # Store Supabase URL
                image_base64=img_base64,  # Always store base64 as backup (database requires NOT NULL)
                panels_data=json.dumps([panel.dict() for panel in comic_page.panels]),
                user_id=current_user.id
            )
            session.add(new_comic)
            session.commit()
            session.refresh(new_comic)
            print(f"✅ Comic saved to database with ID: {new_comic.id}")
            
            # Save the detailed scenario linked to this comic (only if generated)
            if detailed_scenario:
                new_scenario = DetailedScenario(
                    comic_id=new_comic.id,
                    title=detailed_scenario.title,
                    concept=request.concept,
                    genre=detailed_scenario.genre,
                    art_style=detailed_scenario.art_style,
                    world_type=WorldType.IMAGINATION_WORLD,  # Default world type
                    scenario_data=json.dumps(detailed_scenario.dict()),
                    word_count=detailed_scenario.word_count,
                    reading_time_minutes=detailed_scenario.reading_time_minutes,
                    user_id=current_user.id
                )
                session.add(new_scenario)
                session.commit()
                session.refresh(new_scenario)
                print(f"✅ Detailed scenario saved to database with ID: {new_scenario.id}")
            else:
                print("⏭️ No detailed scenario to save (not requested)")
            
            if supabase_image_url:
                print(f"🌐 Comic accessible via Supabase URL: {supabase_image_url}")
        except Exception as save_error:
            print(f"⚠️ Failed to save comic to database: {save_error}")
            # Continue with image response even if saving fails
        
        # Prepare image response
        img_byte_arr.seek(0)
        
        # Add headers with comic metadata
        headers = {
            "X-Comic-Genre": comic_page.genre or "Unknown",
            "X-Comic-Art-Style": comic_page.art_style or "Unknown",
            "X-Comic-Panels": str(len(comic_page.panels)),
            "X-Generated-At": datetime.now().isoformat(),
            "X-Comic-ID": str(new_comic.id) if 'new_comic' in locals() else "unsaved"
        }
        
        return StreamingResponse(
            img_byte_arr, 
            media_type="image/png",
            headers=headers
        )
        
    except Exception as e:
        print(f"❌ Error generating comic: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate comic: {str(e)}")

# Comic generation with data response (for iOS)
@router.post("/generate-comic-with-data")
async def generate_comic_with_data_endpoint(
    request: ComicSaveRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Generate a complete comic and return both the image and metadata (iOS-friendly)
    """
    try:
        print(f"Received genre: {request.genre}, art_style: {request.art_style}")
        print(f"Type of genre: {type(request.genre)}, Type of art_style: {type(request.art_style)}")
        print(f"Full request: {request}")
        print(f"🎨 Generating comic with data for: {request.concept}")
        
        # Generate the complete comic (AI determines genre and art_style from concept)
        comic_page, comic_image, detailed_scenario = generate_complete_comic(
            concept=request.concept,
            genre=request.genre,
            art_style=request.art_style,
            include_detailed_scenario=request.include_detailed_scenario
        )
        
        # Upload comic image to Supabase Storage
        from api.supabase.client import supabase_client
        
        try:
            if supabase_client:
                # Upload to Supabase Storage
                supabase_image_url = supabase_client.upload_comic_image(current_user.id, comic_image)
                print(f"✅ Comic uploaded to Supabase Storage: {supabase_image_url}")
            else:
                supabase_image_url = None
                print("⚠️ Supabase client not available, saving base64 locally")
        except Exception as upload_error:
            print(f"⚠️ Failed to upload to Supabase: {upload_error}")
            supabase_image_url = None
        
        # Convert image to base64 as backup
        img_byte_arr = io.BytesIO()
        comic_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode()
        
        # Overwrite genre and art_style with user input if provided
        user_genre = request.genre.strip().lower() if request.genre else comic_page.genre
        user_art_style = request.art_style.strip().lower() if request.art_style else comic_page.art_style
        comic_page.genre = user_genre
        comic_page.art_style = user_art_style
        if detailed_scenario:
            detailed_scenario.genre = user_genre
            detailed_scenario.art_style = user_art_style
        
        # Use provided image_base64 if available, otherwise use generated one
        final_image_base64 = request.image_base64 if request.image_base64 else img_base64
        
        # Save comic to database with world type using AI-determined values
        new_comic = ComicsPage(
            title=request.title,
            concept=request.concept,
            genre=user_genre,  # Always use user genre
            art_style=user_art_style,  # Always use user art style
            world_type=request.world_type,  # NEW: Add world type
            image_url=supabase_image_url,  # Store Supabase URL
            image_base64=final_image_base64,  # Use final image base64
            panels_data=json.dumps([panel.dict() for panel in comic_page.panels]),
            user_id=current_user.id,
            is_favorite=request.is_favorite or False,
            is_public=request.is_public or False
        )
        session.add(new_comic)
        session.commit()
        session.refresh(new_comic)
        
        # Save the detailed scenario linked to this comic (only if generated)
        if detailed_scenario:
            new_scenario = DetailedScenario(
                comic_id=new_comic.id,
                title=detailed_scenario.title,
                concept=request.concept,
                genre=user_genre,  # Always use user genre
                art_style=user_art_style,  # Always use user art style
                world_type=request.world_type,
                scenario_data=json.dumps(detailed_scenario.dict()),
                word_count=detailed_scenario.word_count,
                reading_time_minutes=detailed_scenario.reading_time_minutes,
                user_id=current_user.id
            )
            session.add(new_scenario)
            session.commit()
            session.refresh(new_scenario)
            print(f"✅ Detailed scenario saved to database with ID: {new_scenario.id}")
        else:
            print("⏭️ No detailed scenario to save (not requested)")
        
        # Check if a detailed scenario exists for this comic
        has_detailed_scenario = session.exec(
            select(DetailedScenario).where(DetailedScenario.comic_id == new_comic.id)
        ).first() is not None
        
        return {
            "id": new_comic.id,
            "title": new_comic.title,
            "concept": new_comic.concept,
            "genre": user_genre,
            "art_style": user_art_style,
            "world_type": new_comic.world_type.value,
            "created_at": new_comic.created_at.isoformat(),
            "is_favorite": new_comic.is_favorite,
            "is_public": new_comic.is_public,
            "has_detailed_scenario": has_detailed_scenario
        }
        
    except Exception as e:
        print(f"❌ Error generating comic with data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate comic: {str(e)}")

# Get user's comics
@router.get("/my-comics", response_model=List[ComicListResponse])
async def get_my_comics(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    limit: int = 20,
    offset: int = 0,
    genre: Optional[str] = None,
    art_style: Optional[str] = None,
    is_favorite: Optional[bool] = None
):
    """Get current user's comics with optional filtering"""
    try:
        query = select(ComicsPage).where(ComicsPage.user_id == current_user.id)
        
        # Apply filters
        if genre:
            query = query.where(ComicsPage.genre == genre)
        if art_style:
            query = query.where(ComicsPage.art_style == art_style)
        if is_favorite is not None:
            query = query.where(ComicsPage.is_favorite == is_favorite)
        
        # Apply pagination and ordering
        query = query.order_by(ComicsPage.created_at.desc()).offset(offset).limit(limit)
        
        comics = session.exec(query).all()
        
        return [
            ComicListResponse(
                id=comic.id,
                title=comic.title,
                concept=comic.concept,
                genre=comic.genre,
                art_style=comic.art_style,
                created_at=comic.created_at,
                is_favorite=comic.is_favorite,
                is_public=comic.is_public,
                view_count=comic.view_count
            )
            for comic in comics
        ]
        
    except Exception as e:
        print(f"❌ Error fetching user comics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch comics")

# Get specific comic by ID
@router.get("/comic/{comic_id}", response_model=ComicResponse)
async def get_comic(
    comic_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get a specific comic by ID"""
    try:
        comic = session.get(ComicsPage, comic_id)
        
        if not comic:
            raise HTTPException(status_code=404, detail="Comic not found")
        
        # Check if user owns the comic or if it's public
        if comic.user_id != current_user.id and not comic.is_public:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Increment view count
        comic.view_count += 1
        session.add(comic)
        session.commit()
        
        return ComicResponse(
            id=comic.id,
            title=comic.title,
            concept=comic.concept,
            genre=comic.genre,
            art_style=comic.art_style,
            image_base64=comic.image_base64,
            panels_data=comic.panels_data,
            created_at=comic.created_at,
            is_favorite=comic.is_favorite,
            is_public=comic.is_public,
            view_count=comic.view_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching comic: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch comic")

# Update comic
@router.put("/comic/{comic_id}")
async def update_comic(
    comic_id: int,
    title: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    is_public: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update comic metadata"""
    try:
        comic = session.get(ComicsPage, comic_id)
        
        if not comic:
            raise HTTPException(status_code=404, detail="Comic not found")
        
        if comic.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update fields
        if title is not None:
            comic.title = title
        if is_favorite is not None:
            comic.is_favorite = is_favorite
        if is_public is not None:
            comic.is_public = is_public
        
        comic.updated_at = datetime.utcnow()
        
        session.add(comic)
        session.commit()
        
        return {"success": True, "message": "Comic updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating comic: {e}")
        raise HTTPException(status_code=500, detail="Failed to update comic")

# Delete comic
@router.delete("/comic/{comic_id}")
async def delete_comic(
    comic_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a comic"""
    try:
        comic = session.get(ComicsPage, comic_id)
        
        if not comic:
            raise HTTPException(status_code=404, detail="Comic not found")
        
        if comic.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        session.delete(comic)
        session.commit()
        
        return {"success": True, "message": "Comic deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting comic: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete comic")

# Get public comics (for browsing)
@router.get("/public-comics", response_model=List[ComicListResponse])
async def get_public_comics(
    session: Session = Depends(get_session),
    limit: int = 20,
    offset: int = 0,
    genre: Optional[str] = None,
    art_style: Optional[str] = None
):
    """Get public comics for browsing"""
    try:
        query = select(ComicsPage).where(ComicsPage.is_public == True)
        
        # Apply filters
        if genre:
            query = query.where(ComicsPage.genre == genre)
        if art_style:
            query = query.where(ComicsPage.art_style == art_style)
        
        # Apply pagination and ordering
        query = query.order_by(ComicsPage.view_count.desc(), ComicsPage.created_at.desc()).offset(offset).limit(limit)
        
        comics = session.exec(query).all()
        
        return [
            ComicListResponse(
                id=comic.id,
                title=comic.title,
                concept=comic.concept,
                genre=comic.genre,
                art_style=comic.art_style,
                created_at=comic.created_at,
                is_favorite=False,  # Not applicable for public view
                is_public=comic.is_public,
                view_count=comic.view_count
            )
            for comic in comics
        ]
        
    except Exception as e:
        print(f"❌ Error fetching public comics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch public comics")

# Story scenario generation endpoint
@router.post("/generate-scenario", response_model=ScenarioSchema2)
async def generate_scenario_endpoint(request: ScenarioRequest):
    """
    Generate frame-size-aware story scenario without images
    Returns structured story data with frames and dialogue optimized for panel dimensions
    """
    try:
        print(f"📝 Generating FRAME-AWARE scenario for: {request.concept}")
        
        scenario = generate_comic_scenario(
            prompt=request.concept,
            genre=request.genre,
            art_style=request.art_style
        )
        
        return scenario
        
    except Exception as e:
        print(f"❌ Error generating scenario: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate scenario: {str(e)}")

# Single image generation endpoint
@router.post("/generate-image")
async def generate_image_endpoint(request: ImageRequest):
    """
    Generate a single image from a text prompt
    Returns the image as PNG
    """
    try:
        print(f"🖼️ Generating image for: {request.prompt}")
        
        image = generate_image_from_prompt(request.prompt)
        
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return StreamingResponse(img_byte_arr, media_type="image/png")
        
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate image: {str(e)}")

# Test endpoint for improved comic generation
@router.post("/test-improved-comic")
async def test_improved_comic():
    """Test the new 8-frame optimization approach where AI determines genre and art style"""
    try:
        # Test with an engaging concept - AI will optimize and determine genre/style
        test_concept = "A detective finds a mysterious music box that plays different melodies, each revealing clues to an unsolved case"
        
        print(f"🧪 Testing 6-panel custom layout comic generation...")
        print(f"📝 Concept: {test_concept}")
        print("🤖 AI will optimize this into 6 panels and determine genre/art style")
        
        # Generate the complete comic (AI determines genre and art_style)
        comic_page, comic_image, detailed_scenario = generate_complete_comic(
            concept=test_concept,
            genre=None,  # Let AI determine
            art_style=None,  # Let AI determine
            include_detailed_scenario=False  # Test without detailed scenario
        )
        
        # Convert image to bytes for response
        img_byte_arr = io.BytesIO()
        comic_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Add headers with comic metadata
        headers = {
            "X-Comic-Genre": comic_page.genre or "Unknown",
            "X-Comic-Art-Style": comic_page.art_style or "Unknown", 
            "X-Comic-Panels": str(len(comic_page.panels)),
            "X-Test-Concept": test_concept,
            "X-AI-Determined": f"Genre: {comic_page.genre}, Style: {comic_page.art_style}",
            "X-New-Features": "8-frame optimization, AI-determined genre/style, emotional progression"
        }
        
        return StreamingResponse(
            img_byte_arr, 
            media_type="image/png",
            headers=headers
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Improved comic generation test failed",
                "improvements": [
                    "Enhanced story prompts for originality",
                    "Better character consistency with LoRA",
                    "Professional comic layout",
                    "Improved dialogue positioning"
                ]
            }
        )

# Test endpoint for debugging image generation
@router.get("/test-image-generation")
async def test_image_generation():
    """Test if Stable Diffusion image generation is working"""
    try:
        # Test with a simple prompt optimized for Stable Diffusion
        test_image = generate_image_from_prompt("a cute red apple on a clean white background, photorealistic style")
        
        # Convert to bytes and return
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return StreamingResponse(
            img_byte_arr, 
            media_type="image/png",
            headers={"X-Test": "Stable Diffusion image generation working"}
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Stable Diffusion image generation test failed",
                "check": "Verify your STABILITY_API_KEY in .env file"
            }
        )

# Chat/Comics router information endpoint
@router.get("/info")
async def chat_router_info():
    """Get chat/comics router information and available endpoints"""
    return {
        "service": "MindToon Chat & Comics API",
        "version": "1.0.0",
        "endpoints": {
            "/scenario/": "Generate story scenario from message",
            "/generate-comic": "Generate complete comic (returns PNG image)",
            "/generate-comic-with-data": "Generate comic with metadata (returns JSON)",
            "/generate-scenario": "Generate frame-aware story scenario only (returns JSON)",
            "/generate-image": "Generate single image (returns PNG)",
            "/my-comics": "Get user's comics",
            "/comic/{id}": "Get specific comic by ID",
            "/public-comics": "Get public comics for browsing",
            "/test-improved-comic": "Test comic generation",
            "/test-image-generation": "Test image generation",
            "/info": "Router information"
        },
        "supported_genres": [
            "Comedy", "Action", "Sci-fi", "Fantasy", "Horror", 
            "Romance", "Mystery", "Adventure", "Drama"
        ],
        "supported_art_styles": [
            "Manga style", "Disney animation", "Marvel comics", 
            "Pixar 3D", "Watercolor painting", "Minimalist line art",
            "Realistic", "Cartoon", "Anime"
        ]
    }

@router.post("/world-comics", response_model=List[ComicGenerationResponse])
async def get_world_comics(
    request: WorldComicsRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get comics from a specific world for the current user"""
    try:
        # Calculate offset for pagination
        offset = (request.page - 1) * request.per_page
        
        # Build query
        query = select(ComicsPage).where(
            ComicsPage.user_id == current_user.id,
            ComicsPage.world_type == request.world_type
        )
        
        # Add favorites filter if requested
        if request.favorites_only:
            query = query.where(ComicsPage.is_favorite == True)
        
        # Add pagination and ordering
        query = query.offset(offset).limit(request.per_page).order_by(ComicsPage.created_at.desc())
        
        # Execute query with limit to prevent large data loads
        comics = session.exec(query).all()
        
        # Convert to response format with error handling
        result = []
        for comic in comics:
            try:
                panels_data = json.loads(comic.panels_data) if comic.panels_data else {}
                # Check if a detailed scenario exists for this comic
                has_detailed_scenario = session.exec(
                    select(DetailedScenario).where(DetailedScenario.comic_id == comic.id)
                ).first() is not None
                result.append(ComicGenerationResponse(
                    id=comic.id,
                    title=comic.title,
                    concept=comic.concept,
                    genre=comic.genre,
                    art_style=comic.art_style,
                    world_type=comic.world_type,
                    image_url=comic.image_url, 
                    panels_data=panels_data,
                    created_at=comic.created_at.isoformat(),
                    is_favorite=comic.is_favorite,
                    is_public=comic.is_public,
                    has_detailed_scenario=has_detailed_scenario
                ))
            except Exception as e:
                print(f"⚠️ Error processing comic {comic.id}: {e}")
                # Skip problematic comics instead of failing the entire request
                continue
        
        return result
        
    except Exception as e:
        print(f"❌ Error fetching world comics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch comics: {str(e)}"
        )

@router.get("/world-stats/{world_type}", response_model=WorldStatsResponse)
async def get_world_stats(
    world_type: WorldType,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for a specific world"""
    try:
        # Count comics in this world
        total_comics = session.exec(
            select(func.count(ComicsPage.id)).where(
                ComicsPage.user_id == current_user.id,
                ComicsPage.world_type == world_type
            )
        ).one()
        
        # Count favorite comics
        favorite_comics = session.exec(
            select(func.count(ComicsPage.id)).where(
                ComicsPage.user_id == current_user.id,
                ComicsPage.world_type == world_type,
                ComicsPage.is_favorite == True
            )
        ).one()
        
        # Count public comics
        public_comics = session.exec(
            select(func.count(ComicsPage.id)).where(
                ComicsPage.user_id == current_user.id,
                ComicsPage.world_type == world_type,
                ComicsPage.is_public == True
            )
        ).one()
        
        # Count collections for this world
        total_collections = session.exec(
            select(func.count(ComicCollection.id)).where(
                ComicCollection.user_id == current_user.id,
                ComicCollection.world_type == world_type
            )
        ).one()
        
        return WorldStatsResponse(
            world_type=world_type,
            total_comics=total_comics,
            favorite_comics=favorite_comics,
            public_comics=public_comics,
            total_collections=total_collections
        )
        
    except Exception as e:
        print(f"❌ Error fetching world stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch world stats: {str(e)}"
        )

@router.post("/collections", response_model=ComicCollectionResponse)
async def create_collection(
    request: ComicCollectionRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new comic collection in a specific world"""
    try:
        collection = ComicCollection(
            name=request.name,
            description=request.description,
            world_type=request.world_type,
            user_id=current_user.id
        )
        
        session.add(collection)
        session.commit()
        session.refresh(collection)
        
        return ComicCollectionResponse(
            id=collection.id,
            name=collection.name,
            description=collection.description,
            world_type=collection.world_type,
            comic_count=0,
            created_at=collection.created_at.isoformat()
        )
        
    except Exception as e:
        print(f"❌ Error creating collection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create collection: {str(e)}"
        )

@router.get("/collections/{world_type}", response_model=List[ComicCollectionResponse])
async def get_world_collections(
    world_type: WorldType,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all collections for a specific world"""
    try:
        collections = session.exec(
            select(ComicCollection).where(
                ComicCollection.user_id == current_user.id,
                ComicCollection.world_type == world_type
            ).order_by(ComicCollection.created_at.desc())
        ).all()
        
        result = []
        for collection in collections:
            # Count comics in this collection
            comic_count = session.exec(
                select(func.count(ComicCollectionItem.id)).where(
                    ComicCollectionItem.collection_id == collection.id
                )
            ).one()
            
            result.append(ComicCollectionResponse(
                id=collection.id,
                name=collection.name,
                description=collection.description,
                world_type=collection.world_type,
                comic_count=comic_count,
                created_at=collection.created_at.isoformat()
            ))
        
        return result
        
    except Exception as e:
        print(f"❌ Error fetching collections: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch collections: {str(e)}"
        )

# TEST ENDPOINTS (NO AUTHENTICATION REQUIRED)
@router.post("/test/generate-comic-no-auth")
async def test_generate_comic_no_auth(request: ComicRequest):
    """
    TEST ENDPOINT: Generate a comic without authentication
    For testing purposes only - remove in production
    """
    try:
        print(f"🧪 TEST: Generating comic for concept: {request.concept}")
        
        # Generate the complete comic
        comic_page, comic_image, detailed_scenario = generate_complete_comic(
            concept=request.concept,
            genre=request.genre,
            art_style=request.art_style,
            include_detailed_scenario=request.include_detailed_scenario
        )
        
        # Convert image to base64
        img_byte_arr = io.BytesIO()
        comic_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode()
        
        return {
            "success": True,
            "title": f"Test Comic: {request.concept[:50]}...",
            "concept": request.concept,
            "genre": comic_page.genre,
            "art_style": comic_page.art_style,
            "image_base64": img_base64,
            "panels_data": [panel.dict() for panel in comic_page.panels],
            "created_at": datetime.now().isoformat(),
            "note": "This is a test endpoint - comic not saved to database"
        }
        
    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@router.post("/test/generate-scenario-no-auth")
async def test_generate_scenario_no_auth(request: ScenarioRequest):
    """
    TEST ENDPOINT: Generate a frame-aware scenario without authentication
    """
    try:
        print(f"🧪 TEST: Generating FRAME-AWARE scenario for: {request.concept}")
        
        # Generate frame-aware scenario using enhanced function
        scenario = generate_comic_scenario(
            prompt=request.concept,
            genre=request.genre,
            art_style=request.art_style
        )
        
        return {
            "success": True,
            "scenario": scenario.dict(),
            "note": "This is a test endpoint"
        }
        
    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Test scenario failed: {str(e)}")

@router.get("/test/health")
async def test_health():
    """
    TEST ENDPOINT: Simple health check
    """
    return {
        "status": "ok",
        "service": "MindToon Chat API",
        "timestamp": datetime.now().isoformat(),
        "note": "This endpoint requires no authentication"
    }

# GENRE AND ART STYLE INFORMATION ENDPOINTS
@router.get("/genres")
async def get_available_genres():
    """Get all available genres with their mood and style descriptions"""
    from api.ai.services import get_available_genres
    
    try:
        genres = get_available_genres()
        return {
            "success": True,
            "genres": genres,
            "total_genres": len(genres),
            "description": "Available comic genres with comprehensive mood and style system"
        }
    except Exception as e:
        print(f"❌ Error fetching genres: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch genres: {str(e)}")

@router.get("/art-styles")
async def get_available_art_styles():
    """Get all available art styles with their descriptions"""
    from api.ai.services import get_available_art_styles
    
    try:
        art_styles = get_available_art_styles()
        return {
            "success": True,
            "art_styles": art_styles,
            "total_art_styles": len(art_styles),
            "description": "Available comic art styles with detailed descriptions"
        }
    except Exception as e:
        print(f"❌ Error fetching art styles: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch art styles: {str(e)}")

@router.get("/style-combination/{genre}/{art_style}")
async def get_style_combination(genre: str, art_style: str):
    """Get the complete style combination for a specific genre and art style"""
    from api.ai.services import get_genre_art_style_combination
    
    try:
        combination = get_genre_art_style_combination(genre, art_style)
        return {
            "success": True,
            "combination": combination,
            "description": f"Complete style combination for {genre} genre with {art_style} art style"
        }
    except Exception as e:
        print(f"❌ Error fetching style combination: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch style combination: {str(e)}")

# Scenario Management Endpoints (Local PostgreSQL)

@router.post("/scenarios/save")
def save_scenario(
    scenario_request: ScenarioSaveRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Save a detailed scenario to local PostgreSQL database"""
    
    # Create new scenario record
    new_scenario = DetailedScenario(
        comic_id=scenario_request.comic_id,
        title=scenario_request.title,
        concept=scenario_request.concept,
        genre=scenario_request.genre,
        art_style=scenario_request.art_style,
        world_type=scenario_request.world_type,
        scenario_data=scenario_request.scenario_data,
        word_count=scenario_request.word_count,
        reading_time_minutes=scenario_request.reading_time_minutes,
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        is_favorite=False,
        is_public=False
    )
    
    session.add(new_scenario)
    session.commit()
    session.refresh(new_scenario)
    
    return {
        "success": True,
        "message": "Scenario saved successfully",
        "scenario_id": new_scenario.id,
        "data": new_scenario
    }

@router.get("/scenarios/comic/{comic_id}")
def get_scenario_by_comic(
    comic_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> DetailedScenario:
    """Get the detailed scenario for a specific comic"""
    
    scenario = session.query(DetailedScenario).filter(
        DetailedScenario.comic_id == comic_id,
        DetailedScenario.user_id == current_user.id
    ).first()
    
    if not scenario:
        raise HTTPException(
            status_code=404,
            detail=f"No scenario found for comic {comic_id}"
        )
    
    return scenario

@router.get("/scenarios/user")
def get_user_scenarios(
    limit: int = 20,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> List[DetailedScenario]:
    """Get all scenarios for the current user"""
    
    scenarios = session.query(DetailedScenario).filter(
        DetailedScenario.user_id == current_user.id
    ).order_by(DetailedScenario.created_at.desc()).offset(offset).limit(limit).all()
    
    return scenarios

@router.put("/scenarios/{scenario_id}")
def update_scenario(
    scenario_id: int,
    updates: dict,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Update a scenario (e.g., mark as favorite, make public)"""
    
    scenario = session.query(DetailedScenario).filter(
        DetailedScenario.id == scenario_id,
        DetailedScenario.user_id == current_user.id
    ).first()
    
    if not scenario:
        raise HTTPException(
            status_code=404,
            detail=f"Scenario {scenario_id} not found"
        )
    
    # Update allowed fields
    allowed_updates = ['is_favorite', 'is_public', 'title']
    for key, value in updates.items():
        if key in allowed_updates and hasattr(scenario, key):
            setattr(scenario, key, value)
    
    scenario.updated_at = datetime.utcnow()
    
    session.commit()
    session.refresh(scenario)
    
    return {
        "success": True,
        "message": "Scenario updated successfully",
        "data": scenario
    }

@router.delete("/scenarios/{scenario_id}")
def delete_scenario(
    scenario_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Delete a scenario"""
    
    scenario = session.query(DetailedScenario).filter(
        DetailedScenario.id == scenario_id,
        DetailedScenario.user_id == current_user.id
    ).first()
    
    if not scenario:
        raise HTTPException(
            status_code=404,
            detail=f"Scenario {scenario_id} not found"
        )
    
    session.delete(scenario)
    session.commit()
    
    return {
        "success": True,
        "message": "Scenario deleted successfully"
    }

# Get scenario with linked comic data
@router.get("/scenarios/{scenario_id}/with-comic")
def get_scenario_with_comic(
    scenario_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get scenario along with its linked comic data"""
    
    # Join query to get both scenario and comic
    result = session.query(DetailedScenario, ComicsPage).join(
        ComicsPage, DetailedScenario.comic_id == ComicsPage.id
    ).filter(
        DetailedScenario.id == scenario_id,
        DetailedScenario.user_id == current_user.id
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Scenario {scenario_id} not found"
        )
    
    scenario, comic = result
    
    return {
        "scenario": scenario,
        "comic": comic,
        "combined_title": f"{comic.title} - Story"
    }

@router.post("/comic/{comic_id}/generate-detailed-scenario")
def generate_detailed_scenario_for_comic(
    comic_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Generate a detailed narrative scenario for an existing comic.
    
    This allows users to request a rich literary story based on their already created comic,
    rather than generating it during comic creation.
    """
    try:
        print(f"📖 Generating detailed scenario for comic ID: {comic_id}")
        
        # Get the comic
        comic = session.query(ComicsPage).filter(
            ComicsPage.id == comic_id,
            ComicsPage.user_id == current_user.id
        ).first()
        
        if not comic:
            raise HTTPException(status_code=404, detail="Comic not found")
        
        # Check if a detailed scenario already exists for this comic
        existing_scenario = session.query(DetailedScenario).filter(
            DetailedScenario.comic_id == comic_id
        ).first()
        
        if existing_scenario:
            print(f"⚠️ Detailed scenario already exists for comic {comic_id}")
            return {
                "message": "Detailed scenario already exists for this comic",
                "scenario_id": existing_scenario.id,
                "existing": True
            }
        
        # Parse the comic panels data to reconstruct the scenario
        panels_data = json.loads(comic.panels_data) if comic.panels_data else []
        
        # Reconstruct a scenario object from the comic data
        from api.ai.schemas import ScenarioSchema2, FrameDescription, Dialogue
        
        # Create frame descriptions from comic panels
        frames = []
        for panel in panels_data:
            # Parse dialogues (this might be a simple string, so we need to handle it)
            dialogues = []
            if panel.get('dialogue'):
                # Simple case: single dialogue string, create a basic dialogue object
                dialogues.append(Dialogue(
                    speaker="Character",
                    text=panel['dialogue'],
                    type="speech",
                    emotion="normal",
                    position="center"
                ))
            
            frame = FrameDescription(
                frame_number=panel.get('panel', 1),
                description=panel.get('image_prompt', ''),
                dialogues=dialogues,
                camera_shot="medium shot",
                speaker_position_in_panel="center",
                dialogue_emotion="normal",
                sfx=[],
                panel_emphasis=False,
                mood="dramatic"
            )
            frames.append(frame)
        
        # Create a scenario object
        comic_scenario = ScenarioSchema2(
            title=comic.title,
            genre=comic.genre,
            characters=["Character"],  # We don't have character info, use generic
            art_style=comic.art_style,
            frames=frames
        )
        
        # Generate the detailed scenario based on the comic
        detailed_scenario = generate_detailed_scenario_from_comic(
            comic_scenario=comic_scenario,
            original_concept=comic.concept,
            genre=comic.genre,
            art_style=comic.art_style
        )
        
        # Save the detailed scenario to database
        new_scenario = DetailedScenario(
            comic_id=comic.id,
            title=detailed_scenario.title,
            concept=comic.concept,
            genre=detailed_scenario.genre,
            art_style=detailed_scenario.art_style,
            world_type=comic.world_type,
            scenario_data=json.dumps(detailed_scenario.dict()),
            word_count=detailed_scenario.word_count,
            reading_time_minutes=detailed_scenario.reading_time_minutes,
            user_id=current_user.id
        )
        session.add(new_scenario)
        session.commit()
        session.refresh(new_scenario)
        
        print(f"✅ Detailed scenario generated and saved with ID: {new_scenario.id}")
        
        return {
            "message": "Detailed scenario generated successfully",
            "scenario_id": new_scenario.id,
            "title": detailed_scenario.title,
            "word_count": detailed_scenario.word_count,
            "reading_time_minutes": detailed_scenario.reading_time_minutes,
            "created_at": new_scenario.created_at.isoformat(),
            "existing": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating detailed scenario for comic: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate detailed scenario: {str(e)}")


