from typing import Optional, List
from fastapi import APIRouter, Depends, Body, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlmodel import Session, select, func
from .models import ComicsPage, ComicCollection, ComicCollectionItem, WorldType
from api.db import get_session
from api.auth.models import User
from api.auth.utils import get_current_user
from api.ai.schemas import ScenarioSchema, ComicsPageSchema, ScenarioSchema2, ComicGenerationRequest, ComicSaveRequest, ComicGenerationResponse, WorldComicsRequest, WorldStatsResponse, ComicCollectionRequest, ComicCollectionResponse
from api.ai.services import generate_scenario, generate_comic_scenario, generate_complete_comic, generate_image_from_prompt
from pydantic import BaseModel
from datetime import datetime
import io
import base64
import json

router = APIRouter()

# Request/Response models
class ComicsPagePayload(BaseModel):
    message: str
    genre: Optional[str] = None
    art_style: Optional[str] = None

class ComicRequest(BaseModel):
    concept: str  # Changed from description to concept to match usage
    genre: str
    art_style: str

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
@router.post("/scenario/", response_model=ScenarioSchema)
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
        
        # Generate the complete comic
        comic_page, comic_image = generate_complete_comic(
            concept=request.concept,
            genre=request.genre,
            art_style=request.art_style
        )
        
        # Convert image to base64 for saving
        img_byte_arr = io.BytesIO()
        comic_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode()
        
        # Save comic to database
        try:
            new_comic = ComicsPage(
                title=f"Comic: {request.concept[:50]}...",
                concept=request.concept,
                genre=request.genre,
                art_style=request.art_style,
                image_base64=img_base64,
                panels_data=json.dumps([panel.dict() for panel in comic_page.panels]),
                user_id=current_user.id
            )
            session.add(new_comic)
            session.commit()
            session.refresh(new_comic)
            print(f"✅ Comic saved to database with ID: {new_comic.id}")
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
        print(f"🎨 Generating comic with data for: {request.concept}")
        
        # Generate the complete comic
        comic_page, comic_image = generate_complete_comic(
            concept=request.concept,
            genre=request.genre,
            art_style=request.art_style
        )
        
        # Convert image to base64
        img_byte_arr = io.BytesIO()
        comic_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode()
        
        # Save comic to database with world type
        new_comic = ComicsPage(
            title=request.title,
            concept=request.concept,
            genre=request.genre,
            art_style=request.art_style,
            world_type=request.world_type,  # NEW: Add world type
            image_base64=img_base64,
            panels_data=json.dumps([panel.dict() for panel in comic_page.panels]),
            user_id=current_user.id,
            is_favorite=request.is_favorite or False,
            is_public=request.is_public or False
        )
        session.add(new_comic)
        session.commit()
        session.refresh(new_comic)
        
        return {
            "title": new_comic.title,
            "concept": new_comic.concept,
            "genre": new_comic.genre,
            "art_style": new_comic.art_style,
            "world_type": new_comic.world_type.value,  # NEW: Include world type
            "image_base64": img_base64,
            "panels_data": json.loads(new_comic.panels_data) if new_comic.panels_data else {},
            "created_at": new_comic.created_at.isoformat()
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
    Generate just the story scenario without images
    Returns structured story data with frames and dialogue
    """
    try:
        print(f"📝 Generating scenario for: {request.concept}")
        
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
    """Test the improved comic generation with a sample concept"""
    try:
        # Test with an engaging concept
        test_concept = "A student's drawing comes to life during art class"
        test_genre = "comedy"
        test_art_style = "manga"
        
        print(f"🧪 Testing improved comic generation...")
        
        # Generate the complete comic
        comic_page, comic_image = generate_complete_comic(
            concept=test_concept,
            genre=test_genre,
            art_style=test_art_style
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
            "X-Improvements": "Better prompts, character consistency, professional layout"
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
            "/generate-scenario": "Generate story scenario only (returns JSON)",
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
        
        # Execute query
        comics = session.exec(query).all()
        
        # Convert to response format
        return [
            ComicGenerationResponse(
                title=comic.title,
                concept=comic.concept,
                genre=comic.genre,
                art_style=comic.art_style,
                world_type=comic.world_type,
                image_base64=comic.image_base64,
                panels_data=json.loads(comic.panels_data) if comic.panels_data else {},
                created_at=comic.created_at.isoformat()
            )
            for comic in comics
        ]
        
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
        
        return WorldStatsResponse(
            world_type=world_type,
            total_comics=total_comics,
            favorite_comics=favorite_comics,
            public_comics=public_comics
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


