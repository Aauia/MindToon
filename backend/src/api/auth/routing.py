from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from api.db import get_session
from .models import User, UserCreate, UserRead, Token, UserDeletionConfirmation, UserDeletionSummary
from .utils import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user
)
from typing import List
import logging
import os

# Set up logging
logger = logging.getLogger(__name__)

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
 
 

    return {
        "access_token": access_token,
       
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/users", response_model=List[UserRead])
def get_all_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@router.delete("/delete-account", response_model=UserDeletionSummary)
async def delete_user_account(
    confirmation: UserDeletionConfirmation,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Delete the current user's account and ALL associated data.
    
    This includes:
    - All comics created by the user
    - All detailed scenarios 
    - All comic images in Supabase storage
    - All collections
    - All world stats
    - The user account itself
    
    WARNING: This action is IRREVERSIBLE!
    """
    # Validate deletion confirmation
    if not confirmation.confirm_deletion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account deletion must be explicitly confirmed by setting 'confirm_deletion' to true."
        )
    
    if confirmation.username_confirmation != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username confirmation does not match. Expected: '{current_user.username}'"
        )
    
    expected_acknowledgment = "I understand this action is permanent and irreversible"
    if confirmation.understanding_acknowledgment != expected_acknowledgment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Understanding acknowledgment must be exactly: '{expected_acknowledgment}'"
        )

    try:
        logger.info(f"🗑️ Starting account deletion for user: {current_user.username} (ID: {current_user.id})")
        
        # Import models here to avoid circular imports
        from api.chat.models import ComicsPage, DetailedScenario, ComicCollection, ComicCollectionItem, WorldStats
        
        deletion_stats = {
            "user_id": current_user.id,
            "username": current_user.username,
            "comics_deleted": 0,
            "scenarios_deleted": 0,
            "images_deleted": 0,
            "collections_deleted": 0,
            "collection_items_deleted": 0,
            "world_stats_deleted": 0,
            "storage_cleanup_errors": []
        }
        
        # Step 1: Delete comic images from Supabase Storage
        logger.info("🗑️ Step 1: Deleting comic images from Supabase Storage...")
        try:
            from api.supabase.client import supabase_client
            
            # Get all user's comics first to see what we're working with
            user_comics = session.exec(
                select(ComicsPage).where(ComicsPage.user_id == current_user.id)
            ).all()
            
            logger.info(f"📊 Found {len(user_comics)} total comics for user {current_user.username}")
            
            # Count comics with URLs vs base64 only
            comics_with_urls = [comic for comic in user_comics if comic.image_url]
            comics_base64_only = [comic for comic in user_comics if not comic.image_url and comic.image_base64]
            
            logger.info(f"   📁 Comics with Supabase URLs: {len(comics_with_urls)}")
            logger.info(f"   💾 Comics with base64 only: {len(comics_base64_only)}")
            
            if supabase_client:
                logger.info("✅ Supabase client is available")
                
                if comics_with_urls:
                    logger.info(f"🗑️ Attempting to delete {len(comics_with_urls)} images from Supabase Storage...")
                    
                    for i, comic in enumerate(comics_with_urls, 1):
                        logger.info(f"   🗑️ Deleting image {i}/{len(comics_with_urls)}: {comic.image_url}")
                        try:
                            success = supabase_client.delete_comic_image(comic.image_url)
                            if success:
                                deletion_stats["images_deleted"] += 1
                                logger.info(f"   ✅ Successfully deleted image {i}: {comic.image_url}")
                            else:
                                error_msg = f"Failed to delete image {i}: {comic.image_url}"
                                deletion_stats["storage_cleanup_errors"].append(error_msg)
                                logger.warning(f"   ⚠️ {error_msg}")
                        except Exception as img_error:
                            error_msg = f"Error deleting image {i} ({comic.image_url}): {str(img_error)}"
                            deletion_stats["storage_cleanup_errors"].append(error_msg)
                            logger.error(f"   ❌ {error_msg}")
                    
                    logger.info(f"📊 Supabase deletion summary: {deletion_stats['images_deleted']} deleted, {len(deletion_stats['storage_cleanup_errors'])} errors")
                else:
                    logger.info("📭 No comics with Supabase URLs found - nothing to delete from storage")
                    
            else:
                logger.warning("❌ Supabase client not available! This indicates a configuration issue.")
                logger.warning("   Check your SUPABASE_URL, SUPABASE_ANON_KEY, and SUPABASE_SERVICE_ROLE_KEY environment variables")
                deletion_stats["storage_cleanup_errors"].append("Supabase client not initialized - check environment variables")
            
            # Log what will happen to base64-only comics
            if comics_base64_only:
                logger.info(f"💾 {len(comics_base64_only)} comics with base64-only data will be deleted from database (no Supabase cleanup needed)")
                
        except Exception as storage_error:
            logger.error(f"❌ Critical storage cleanup error: {storage_error}")
            logger.error(f"   This may indicate Supabase import or initialization issues")
            deletion_stats["storage_cleanup_errors"].append(f"Critical error: {str(storage_error)}")
            
            # Try to get more debug info
            try:
                import traceback
                logger.error(f"   Full traceback: {traceback.format_exc()}")
            except:
                pass
        
        # Step 2: Delete collection items (junction table)
        logger.info("🗑️ Step 2: Deleting collection items...")
        collection_items = session.exec(
            select(ComicCollectionItem).join(ComicCollection).where(ComicCollection.user_id == current_user.id)
        ).all()
        
        for item in collection_items:
            session.delete(item)
            deletion_stats["collection_items_deleted"] += 1
        
        logger.info(f"✅ Deleted {deletion_stats['collection_items_deleted']} collection items")
        
        # Step 3: Delete collections
        logger.info("🗑️ Step 3: Deleting collections...")
        collections = session.exec(
            select(ComicCollection).where(ComicCollection.user_id == current_user.id)
        ).all()
        
        for collection in collections:
            session.delete(collection)
            deletion_stats["collections_deleted"] += 1
        
        logger.info(f"✅ Deleted {deletion_stats['collections_deleted']} collections")
        
        # Step 4: Delete detailed scenarios
        logger.info("🗑️ Step 4: Deleting detailed scenarios...")
        scenarios = session.exec(
            select(DetailedScenario).where(DetailedScenario.user_id == current_user.id)
        ).all()
        
        for scenario in scenarios:
            session.delete(scenario)
            deletion_stats["scenarios_deleted"] += 1
        
        logger.info(f"✅ Deleted {deletion_stats['scenarios_deleted']} scenarios")
        
        # Step 5: Delete comics (this will automatically handle foreign key constraints)
        logger.info("🗑️ Step 5: Deleting comics...")
        comics = session.exec(
            select(ComicsPage).where(ComicsPage.user_id == current_user.id)
        ).all()
        
        for comic in comics:
            session.delete(comic)
            deletion_stats["comics_deleted"] += 1
        
        logger.info(f"✅ Deleted {deletion_stats['comics_deleted']} comics")
        
        # Step 6: Delete world stats
        logger.info("🗑️ Step 6: Deleting world stats...")
        world_stats = session.exec(
            select(WorldStats).where(WorldStats.user_id == current_user.id)
        ).all()
        
        for stat in world_stats:
            session.delete(stat)
            deletion_stats["world_stats_deleted"] += 1
        
        logger.info(f"✅ Deleted {deletion_stats['world_stats_deleted']} world stats")
        
        # Step 7: Delete the user account
        logger.info("🗑️ Step 7: Deleting user account...")
        session.delete(current_user)
        
        # Commit all deletions
        session.commit()
        
        logger.info(f"✅ Account deletion completed successfully for user: {current_user.username}")
        
        return UserDeletionSummary(
            success=True,
            username=current_user.username,
            message=f"Account '{current_user.username}' and all associated data have been permanently deleted.",
            deletion_summary=deletion_stats,
            warning="This action was irreversible. All your comics, stories, and account data have been permanently removed."
        )
        
    except Exception as e:
        logger.error(f"❌ Error during account deletion: {e}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}. No data was deleted due to this error."
        )

@router.get("/supabase-status")
async def get_supabase_status(current_user: User = Depends(get_current_active_user)):
    """
    Check Supabase connection status and storage configuration.
    Useful for debugging why account deletion might not work properly.
    """
    try:
        from api.supabase.client import supabase_client
        from api.chat.models import ComicsPage
        from sqlmodel import func
        
        # Get session for counting
        session = next(get_session())
        
        # Count user's comics and their storage types
        user_comics = session.exec(
            select(ComicsPage).where(ComicsPage.user_id == current_user.id)
        ).all()
        
        comics_with_urls = len([c for c in user_comics if c.image_url])
        comics_base64_only = len([c for c in user_comics if not c.image_url and c.image_base64])
        comics_no_image = len([c for c in user_comics if not c.image_url and not c.image_base64])
        
        # Check Supabase client status
        supabase_status = {
            "client_initialized": supabase_client is not None,
            "connection_test": None,
            "bucket_exists": False,
            "environment_variables": {
                "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
                "SUPABASE_ANON_KEY": bool(os.getenv("SUPABASE_ANON_KEY")),
                "SUPABASE_SERVICE_ROLE_KEY": bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
            }
        }
        
        if supabase_client:
            try:
                connection_test = supabase_client.test_connection()
                supabase_status["connection_test"] = connection_test
                supabase_status["bucket_exists"] = connection_test.get("bucket_exists", False)
            except Exception as e:
                supabase_status["connection_test"] = {
                    "error": str(e),
                    "connected": False
                }
        
        return {
            "user_info": {
                "username": current_user.username,
                "user_id": current_user.id
            },
            "comics_storage_breakdown": {
                "total_comics": len(user_comics),
                "comics_with_supabase_urls": comics_with_urls,
                "comics_base64_only": comics_base64_only,
                "comics_no_image": comics_no_image,
                "supabase_images_to_delete": comics_with_urls
            },
            "supabase_status": supabase_status,
            "deletion_impact": {
                "will_delete_from_supabase": comics_with_urls > 0 and supabase_client is not None,
                "supabase_deletion_possible": supabase_status["client_initialized"] and supabase_status.get("bucket_exists", False),
                "fallback_mode": not supabase_status["client_initialized"]
            },
            "recommendations": _get_supabase_recommendations(supabase_status, comics_with_urls)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting Supabase status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Supabase status: {str(e)}"
        )

def _get_supabase_recommendations(supabase_status: dict, comics_with_urls: int) -> list:
    """Generate recommendations based on Supabase status"""
    recommendations = []
    
    if not supabase_status["client_initialized"]:
        recommendations.append("🔧 Supabase client is not initialized - check environment variables")
        
        env_vars = supabase_status["environment_variables"]
        missing_vars = [var for var, present in env_vars.items() if not present]
        if missing_vars:
            recommendations.append(f"❌ Missing environment variables: {', '.join(missing_vars)}")
    
    elif supabase_status["connection_test"] and not supabase_status["connection_test"].get("connected", False):
        recommendations.append("🔌 Supabase connection test failed - check credentials")
        
    elif not supabase_status.get("bucket_exists", False):
        recommendations.append("🪣 'comics' storage bucket does not exist - create it in Supabase dashboard")
    
    elif comics_with_urls > 0:
        recommendations.append(f"✅ Supabase is configured correctly - {comics_with_urls} images can be deleted from storage")
    
    else:
        recommendations.append("💾 All your comics use base64 storage only - no Supabase cleanup needed")
    
    if not recommendations:
        recommendations.append("✅ Supabase configuration looks good!")
    
    return recommendations

@router.get("/deletion-info")
async def get_deletion_info(current_user: User = Depends(get_current_active_user)):
    """
    Get information about what will be deleted if the user deletes their account.
    This allows users to see the scope of deletion before confirming.
    """
    try:
        from api.chat.models import ComicsPage, DetailedScenario, ComicCollection, WorldStats
        from sqlmodel import func
        
        # Get session for counting
        session = next(get_session())
        
        # Count user's data
        comics_count = session.exec(
            select(func.count(ComicsPage.id)).where(ComicsPage.user_id == current_user.id)
        ).one()
        
        scenarios_count = session.exec(
            select(func.count(DetailedScenario.id)).where(DetailedScenario.user_id == current_user.id)
        ).one()
        
        collections_count = session.exec(
            select(func.count(ComicCollection.id)).where(ComicCollection.user_id == current_user.id)
        ).one()
        
        world_stats_count = session.exec(
            select(func.count(WorldStats.id)).where(WorldStats.user_id == current_user.id)
        ).one()
        
        # Count images in storage
        comics_with_images = session.exec(
            select(func.count(ComicsPage.id)).where(
                ComicsPage.user_id == current_user.id,
                ComicsPage.image_url.isnot(None)
            )
        ).one()
        
        return {
            "user_info": {
                "username": current_user.username,
                "email": current_user.email,
                "account_created": current_user.created_at.isoformat(),
                "full_name": current_user.full_name
            },
            "data_to_be_deleted": {
                "comics": comics_count,
                "detailed_scenarios": scenarios_count,
                "collections": collections_count,
                "world_statistics": world_stats_count,
                "images_in_storage": comics_with_images
            },
            "warning": {
                "message": "Account deletion is PERMANENT and IRREVERSIBLE",
                "consequences": [
                    "All your comics will be permanently deleted",
                    "All your detailed stories will be permanently deleted", 
                    "All your collections will be permanently deleted",
                    "All your uploaded images will be permanently deleted from storage",
                    "Your account and login credentials will be permanently deleted",
                    "This action cannot be undone"
                ]
            },
            "deletion_endpoint": "DELETE /api/auth/delete-account"
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting deletion info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deletion information: {str(e)}"
        )  