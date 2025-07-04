from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Dict, List, Optional
from api.db import get_session
from api.auth.utils import get_current_user
from api.auth.models import User
from api.supabase.client import supabase_client
from api.ai.schemas import ScenarioSaveRequest, DetailedScenarioSchema
import json
from datetime import datetime

router = APIRouter()

@router.get("/test-connection")
def test_supabase_connection() -> Dict:
    """Test the Supabase connection and return status"""
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not initialized. Check environment variables."
        )
    
    connection_status = supabase_client.test_connection()
    
    if not connection_status["connected"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=connection_status
        )
    
    return connection_status

@router.get("/storage/user/{user_id}/usage")
def get_user_storage_usage(
    user_id: int,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Get storage usage statistics for the current user"""
    # Users can only access their own storage stats
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only view your own storage usage."
        )
    
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not available"
        )
    
    usage_stats = supabase_client.get_user_comics_storage_usage(user_id)
    return usage_stats

@router.get("/storage/user/{user_id}/comics")
def list_user_comics_storage(
    user_id: int,
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """List all comic images in storage for the current user"""
    # Users can only access their own comics
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only view your own comics."
        )
    
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not available"
        )
    
    comics = supabase_client.list_user_comics(user_id)
    return comics

@router.get("/health")
def supabase_health_check() -> Dict:
    """Health check endpoint for Supabase services"""
    if not supabase_client:
        return {
            "status": "error",
            "message": "Supabase client not initialized",
            "services": {
                "database": "unknown",
                "storage": "unknown"
            }
        }
    
    try:
        connection_status = supabase_client.test_connection()
        
        return {
            "status": "ok" if connection_status["connected"] else "error",
            "message": connection_status["message"],
            "services": {
                "database": "connected" if connection_status["connected"] else "disconnected",
                "storage": "available" if connection_status["bucket_exists"] else "bucket_missing"
            },
            "details": {
                "bucket_exists": connection_status["bucket_exists"],
                "total_buckets": connection_status["total_buckets"]
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "services": {
                "database": "error",
                "storage": "error"
            }
        }

# Scenario Management Endpoints

@router.post("/scenarios/save")
def save_scenario(
    scenario_request: ScenarioSaveRequest,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Save a detailed scenario to the database"""
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not available"
        )
    
    # Prepare scenario data for database
    scenario_data = {
        "comic_id": scenario_request.comic_id,
        "title": scenario_request.title,
        "concept": scenario_request.concept,
        "genre": scenario_request.genre,
        "art_style": scenario_request.art_style,
        "world_type": scenario_request.world_type.value,
        "scenario_data": scenario_request.scenario_data,
        "word_count": scenario_request.word_count,
        "reading_time_minutes": scenario_request.reading_time_minutes,
        "user_id": current_user.id,
        "created_at": datetime.utcnow().isoformat(),
        "is_favorite": False,
        "is_public": False
    }
    
    result = supabase_client.save_scenario_to_database(scenario_data)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save scenario: {result.get('error', 'Unknown error')}"
        )
    
    return {
        "success": True,
        "message": "Scenario saved successfully",
        "scenario_id": result["data"]["id"],
        "data": result["data"]
    }

@router.get("/scenarios/comic/{comic_id}")
def get_scenario_by_comic(
    comic_id: int,
    current_user: User = Depends(get_current_user)
) -> Optional[Dict]:
    """Get the detailed scenario for a specific comic"""
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not available"
        )
    
    scenario = supabase_client.get_scenario_by_comic_id(comic_id)
    
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No scenario found for comic {comic_id}"
        )
    
    # Check if user has access to this scenario
    if scenario["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only view your own scenarios."
        )
    
    return scenario

@router.get("/scenarios/user/{user_id}")
def get_user_scenarios(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """Get all scenarios for a specific user"""
    # Users can only access their own scenarios
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only view your own scenarios."
        )
    
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not available"
        )
    
    scenarios = supabase_client.get_user_scenarios_from_database(user_id, limit, offset)
    return scenarios

@router.put("/scenarios/{scenario_id}")
def update_scenario(
    scenario_id: int,
    updates: Dict,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Update a scenario (e.g., mark as favorite, make public)"""
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not available"
        )
    
    # First check if the scenario exists and user has access
    scenario = supabase_client.get_scenario_by_comic_id(scenario_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )
    
    if scenario["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only update your own scenarios."
        )
    
    # Add updated timestamp
    updates["updated_at"] = datetime.utcnow().isoformat()
    
    result = supabase_client.update_scenario_in_database(scenario_id, updates)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scenario: {result.get('error', 'Unknown error')}"
        )
    
    return {
        "success": True,
        "message": "Scenario updated successfully",
        "data": result["data"]
    }

@router.delete("/scenarios/{scenario_id}")
def delete_scenario(
    scenario_id: int,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Delete a scenario"""
    if not supabase_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client not available"
        )
    
    # First check if the scenario exists and user has access
    scenario = supabase_client.get_scenario_by_comic_id(scenario_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario {scenario_id} not found"
        )
    
    if scenario["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only delete your own scenarios."
        )
    
    result = supabase_client.delete_scenario_from_database(scenario_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete scenario: {result.get('error', 'Unknown error')}"
        )
    
    return {
        "success": True,
        "message": "Scenario deleted successfully"
    }