from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import json

from api.db import get_session
from api.auth.models import User
from api.ai.analyses import (
    AnalyticsService,
    AnalyticsEntryCreate,
    AnalyticsSummary,
    WeeklyInsight,
    InsightResponse,
    AnalyticsEntry,
    AnalyticsInsight,
    CrossWorldPsychologicalAssumption,
    ComicRecommendation,
    ComicRecommendationsResponse,
    DigestPeriod
)
from api.chat.models import WorldType, ComicsPage

router = APIRouter()

@router.get("/analytics/summary/{user_id}", response_model=AnalyticsSummary)
async def get_analytics_summary(
    user_id: int,
    world_type: Optional[WorldType] = None,
    session: Session = Depends(get_session)
):
    """Get comprehensive analytics summary for a specific user based on existing comics, optionally filtered by world type"""
    try:
        # Check if user exists
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            # Return a default summary if user does not exist
            return AnalyticsSummary(
                total_entries=0,
                genre_distribution=[],
                art_style_distribution=[],
                world_distribution=[],
                time_series=[],
                recent_prompts=[],
                insights_available=False
            )
        summary = AnalyticsService.get_user_analytics_summary(session, user_id, world_type)
        return summary
    except Exception as e:
        # Always return a valid AnalyticsSummary on error
        return AnalyticsSummary(
            total_entries=0,
            genre_distribution=[],
            art_style_distribution=[],
            world_distribution=[],
            time_series=[],
            recent_prompts=[],
            insights_available=False
        )

@router.get("/analytics/insights/weekly/{user_id}", response_model=WeeklyInsight)
async def get_weekly_insight(
    user_id: int,
    world_type: Optional[WorldType] = None,
    session: Session = Depends(get_session)
):
    """Get weekly insight based on a specific user's comic generation patterns, optionally filtered by world type"""
    try:
        insight = await AnalyticsService.generate_weekly_insight(session, user_id, world_type)
        return insight
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate weekly insight: {str(e)}"
        )

@router.get("/analytics/insights/{user_id}", response_model=WeeklyInsight)
async def get_insight_by_period(
    user_id: int,
    period: DigestPeriod = DigestPeriod.WEEKLY,
    world_type: Optional[WorldType] = None,
    session: Session = Depends(get_session)
):
    """Get insight for a specific user based on period (weekly, monthly, all_time) and optionally filtered by world type"""
    try:
        insight = await AnalyticsService.generate_insight_by_period(session, user_id, period, world_type)
        return insight
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate {period.value} insight: {str(e)}"
        )

@router.post("/analytics/insights/patterns/{user_id}", response_model=InsightResponse)
async def generate_pattern_insight(
    user_id: int,
    world_type: Optional[WorldType] = None,
    session: Session = Depends(get_session)
):
    """Generate pattern analysis insight using LLM for a specific user, optionally filtered by world type"""
    try:
        # Get user's recent comics for analysis
        recent_comics = session.exec(
            select(ComicsPage)
            .where(ComicsPage.user_id == user_id)
            .where(ComicsPage.world_type == world_type if world_type else True)
            .order_by(ComicsPage.created_at.desc())
            .limit(20)
        ).all()
        
        if not recent_comics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No comic data available for pattern analysis"
            )
        
        # Analyze concept patterns
        concepts = [comic.concept for comic in recent_comics]
        prompt_analysis = await AnalyticsService.analyze_prompt_themes(concepts)
        
        # Create insight data
        insight_data = {
            "themes": prompt_analysis.themes,
            "emotions": prompt_analysis.emotions,
            "language_style": prompt_analysis.language_style,
            "creativity_indicators": prompt_analysis.creativity_indicators,
            "summary": prompt_analysis.summary,
            "total_comics_analyzed": len(concepts),
            "world_type": world_type.value if world_type else "all",
            "analysis_date": datetime.now().isoformat()
        }
        
        # Save insight to database
        insight = AnalyticsService.save_insight(
            session=session,
            user_id=user_id,
            insight_type="pattern_analysis",
            title="Your Creative Patterns",
            description="Analysis of your comic generation themes and creative expression",
            data=insight_data
        )
        
        return InsightResponse(
            success=True,
            insight_type="pattern_analysis",
            title="Your Creative Patterns",
            description="Analysis of your comic generation themes and creative expression",
            data=insight_data,
            created_at=insight.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate pattern insight: {str(e)}"
        )

# Comic Recommendations Endpoints (replacing psychological assumptions)
@router.post("/analytics/comic-recommendations/{user_id}", response_model=ComicRecommendationsResponse)
async def generate_comic_recommendations(
    user_id: int,
    world_type: Optional[WorldType] = None,
    limit: int = 5,
    session: Session = Depends(get_session)
):
    """Generate comic recommendations based on user's genre, art style, and prompt patterns"""
    try:
        print(f"🔍 DEBUG ROUTER: Starting comic recommendations for user {user_id}, world_type: {world_type}")
        
        # Check if user has comics
        if world_type:
            total_comics = session.exec(
                select(ComicsPage).where(
                    ComicsPage.user_id == user_id,
                    ComicsPage.world_type == world_type
                )
            ).all()
        else:
            total_comics = session.exec(
                select(ComicsPage).where(ComicsPage.user_id == user_id)
            ).all()
        
        if not total_comics:
            world_name = world_type.value if world_type else "any world"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No comic data available for recommendations in {world_name}"
            )
        
        # Generate recommendations
        recommendations = await AnalyticsService.generate_comic_recommendations(session, user_id, world_type, limit)
        
        # Save insight to database
        insight_data = {
            "recommendations": [
                {
                    "title": rec.title,
                    "concept": rec.concept,
                    "genre": rec.genre,
                    "art_style": rec.art_style,
                    "confidence_score": rec.confidence_score,
                    "reasoning": rec.reasoning,
                    "similar_to_user_patterns": rec.similar_to_user_patterns
                }
                for rec in recommendations.recommendations
            ],
            "based_on": recommendations.based_on,
            "total_recommendations": recommendations.total_recommendations
        }
        
        # Save to database
        insight_type = f"comic_recommendations_{world_type.value}" if world_type else "comic_recommendations_all"
        title = f"Your Comic Recommendations - {world_type.value.replace('_', ' ').title()}" if world_type else "Your Comic Recommendations"
        description = f"AI-generated comic recommendations based on your creation patterns in {world_type.value.replace('_', ' ')}" if world_type else "AI-generated comic recommendations based on your creation patterns across all worlds"
        
        AnalyticsService.save_insight(
            session=session,
            user_id=user_id,
            insight_type=insight_type,
            title=title,
            description=description,
            data=insight_data
        )
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate comic recommendations: {str(e)}"
        )

# World-specific comic recommendation endpoints
@router.post("/analytics/comic-recommendations/imagination-world/{user_id}", response_model=ComicRecommendationsResponse)
async def generate_imagination_world_comic_recommendations(
    user_id: int,
    limit: int = 5,
    session: Session = Depends(get_session)
):
    """Generate comic recommendations based on user's patterns in Imagination World only"""
    try:
        return await generate_comic_recommendations(user_id, WorldType.IMAGINATION_WORLD, limit, session)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Imagination World comic recommendations: {str(e)}"
        )

@router.post("/analytics/comic-recommendations/mind-world/{user_id}", response_model=ComicRecommendationsResponse)
async def generate_mind_world_comic_recommendations(
    user_id: int,
    limit: int = 5,
    session: Session = Depends(get_session)
):
    """Generate comic recommendations based on user's patterns in Mind World only"""
    try:
        return await generate_comic_recommendations(user_id, WorldType.MIND_WORLD, limit, session)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Mind World comic recommendations: {str(e)}"
        )

@router.post("/analytics/comic-recommendations/dream-world/{user_id}", response_model=ComicRecommendationsResponse)
async def generate_dream_world_comic_recommendations(
    user_id: int,
    limit: int = 5,
    session: Session = Depends(get_session)
):
    """Generate comic recommendations based on user's patterns in Dream World only"""
    try:
        return await generate_comic_recommendations(user_id, WorldType.DREAM_WORLD, limit, session)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Dream World comic recommendations: {str(e)}"
        )

# Compatibility route for old psychological endpoints (redirect to comic recommendations)
@router.post("/analytics/psychological-assumptions/{user_id}", response_model=ComicRecommendationsResponse)
async def generate_psychological_assumptions_compat(
    user_id: int,
    world_type: Optional[WorldType] = None,
    session: Session = Depends(get_session)
):
    """Compatibility endpoint - redirects to comic recommendations"""
    return await generate_comic_recommendations(user_id, world_type, 5, session)

@router.get("/analytics/insights/{user_id}", response_model=List[InsightResponse])
async def get_user_insights(
    user_id: int,
    insight_type: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get all insights for a specific user"""
    try:
        insights = AnalyticsService.get_user_insights(session, user_id, insight_type)
        
        insight_responses = []
        for insight in insights:
            try:
                data = json.loads(insight.data)
            except:
                data = {"error": "Could not parse insight data"}
            
            insight_responses.append(InsightResponse(
                success=True,
                insight_type=insight.insight_type,
                title=insight.title,
                description=insight.description,
                data=data,
                created_at=insight.created_at.isoformat()
            ))
        
        return insight_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get insights: {str(e)}"
        )

@router.get("/analytics/charts/genre-distribution/{user_id}")
async def get_genre_chart_data(
    user_id: int,
    world_type: Optional[WorldType] = None,
    session: Session = Depends(get_session)
):
    """Get genre distribution data for chart rendering for a specific user, optionally filtered by world type"""
    try:
        summary = AnalyticsService.get_user_analytics_summary(session, user_id, world_type)
        
        # Format for bar chart
        chart_data = {
            "labels": [genre.genre for genre in summary.genre_distribution],
            "data": [genre.count for genre in summary.genre_distribution],
            "percentages": [genre.percentage for genre in summary.genre_distribution]
        }
        
        return {
            "success": True,
            "chart_type": "bar",
            "title": "Your Genre Preferences",
            "world_type": world_type.value if world_type else "all",
            "data": chart_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get genre chart data: {str(e)}"
        )

@router.get("/analytics/charts/art-style-distribution/{user_id}")
async def get_art_style_chart_data(
    user_id: int,
    world_type: Optional[WorldType] = None,
    session: Session = Depends(get_session)
):
    """Get art style distribution data for chart rendering for a specific user, optionally filtered by world type"""
    try:
        summary = AnalyticsService.get_user_analytics_summary(session, user_id, world_type)
        
        # Format for pie chart
        chart_data = {
            "labels": [style.art_style for style in summary.art_style_distribution],
            "data": [style.count for style in summary.art_style_distribution],
            "percentages": [style.percentage for style in summary.art_style_distribution]
        }
        
        return {
            "success": True,
            "chart_type": "pie",
            "title": "Your Art Style Preferences",
            "world_type": world_type.value if world_type else "all",
            "data": chart_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get art style chart data: {str(e)}"
        )

@router.get("/analytics/charts/world-distribution/{user_id}")
async def get_world_distribution_chart_data(
    user_id: int,
    session: Session = Depends(get_session)
):
    """Get world distribution data for chart rendering for a specific user"""
    try:
        summary = AnalyticsService.get_user_analytics_summary(session, user_id)
        
        # Format for pie chart
        chart_data = {
            "labels": [world.world_type.value for world in summary.world_distribution],
            "data": [world.count for world in summary.world_distribution],
            "percentages": [world.percentage for world in summary.world_distribution]
        }
        
        return {
            "success": True,
            "chart_type": "pie",
            "title": "Your World Preferences",
            "data": chart_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get world distribution chart data: {str(e)}"
        )

@router.get("/analytics/charts/time-series/{user_id}")
async def get_time_series_chart_data(
    user_id: int,
    world_type: Optional[WorldType] = None,
    session: Session = Depends(get_session)
):
    """Get time series data for trend chart rendering for a specific user, optionally filtered by world type"""
    try:
        summary = AnalyticsService.get_user_analytics_summary(session, user_id, world_type)
        
        # Format for line chart
        chart_data = {
            "labels": [day.date for day in summary.time_series],
            "data": [day.count for day in summary.time_series],
            "genres": [day.genres for day in summary.time_series],
            "art_styles": [day.art_styles for day in summary.time_series]
        }
        
        return {
            "success": True,
            "chart_type": "line",
            "title": "Your Comic Generation Trends",
            "world_type": world_type.value if world_type else "all",
            "data": chart_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get time series chart data: {str(e)}"
        )

@router.get("/analytics/insights/available/{user_id}")
async def check_insights_available(
    user_id: int,
    world_type: Optional[WorldType] = None,
    session: Session = Depends(get_session)
):
    """Check if insights are available for a specific user (every 5 comics), optionally filtered by world type"""
    try:
        summary = AnalyticsService.get_user_analytics_summary(session, user_id, world_type)
        
        return {
            "insights_available": summary.insights_available,
            "total_comics": summary.total_entries,
            "next_insight_at": (summary.total_entries // 5 + 1) * 5 if summary.total_entries > 0 else 5,
            "world_type": world_type.value if world_type else "all"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check insights availability: {str(e)}"
        )

# World-specific analytics endpoints
@router.get("/analytics/imagination-world/{user_id}")
async def get_imagination_world_analytics(
    user_id: int,
    session: Session = Depends(get_session)
):
    """Get analytics summary for Imagination World comics only for a specific user"""
    try:
        summary = AnalyticsService.get_user_analytics_summary(
            session, user_id, WorldType.IMAGINATION_WORLD
        )
        return {
            "world_type": "imagination_world",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Imagination World analytics: {str(e)}"
        )

@router.get("/analytics/mind-world/{user_id}")
async def get_mind_world_analytics(
    user_id: int,
    session: Session = Depends(get_session)
):
    """Get analytics summary for Mind World comics only for a specific user"""
    try:
        summary = AnalyticsService.get_user_analytics_summary(
            session, user_id, WorldType.MIND_WORLD
        )
        return {
            "world_type": "mind_world",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Mind World analytics: {str(e)}"
        )

@router.get("/analytics/dream-world/{user_id}")
async def get_dream_world_analytics(
    user_id: int,
    session: Session = Depends(get_session)
):
    """Get analytics summary for Dream World comics only for a specific user"""
    try:
        summary = AnalyticsService.get_user_analytics_summary(
            session, user_id, WorldType.DREAM_WORLD
        )
        return {
            "world_type": "dream_world",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Dream World analytics: {str(e)}"
        )

# Additional analytics endpoints for better functionality
@router.get("/analytics/user/{user_id}/overview")
async def get_user_analytics_overview(
    user_id: int,
    session: Session = Depends(get_session)
):
    """Get a comprehensive overview of user's analytics across all worlds"""
    try:
        # Get analytics for each world
        imagination_summary = AnalyticsService.get_user_analytics_summary(
            session, user_id, WorldType.IMAGINATION_WORLD
        )
        mind_summary = AnalyticsService.get_user_analytics_summary(
            session, user_id, WorldType.MIND_WORLD
        )
        dream_summary = AnalyticsService.get_user_analytics_summary(
            session, user_id, WorldType.DREAM_WORLD
        )
        all_summary = AnalyticsService.get_user_analytics_summary(session, user_id)
        
        return {
            "user_id": user_id,
            "total_comics": all_summary.total_entries,
            "worlds": {
                "imagination_world": {
                    "total_comics": imagination_summary.total_entries,
                    "top_genre": imagination_summary.genre_distribution[0].genre if imagination_summary.genre_distribution else "None",
                    "top_art_style": imagination_summary.art_style_distribution[0].art_style if imagination_summary.art_style_distribution else "None"
                },
                "mind_world": {
                    "total_comics": mind_summary.total_entries,
                    "top_genre": mind_summary.genre_distribution[0].genre if mind_summary.genre_distribution else "None",
                    "top_art_style": mind_summary.art_style_distribution[0].art_style if mind_summary.art_style_distribution else "None"
                },
                "dream_world": {
                    "total_comics": dream_summary.total_entries,
                    "top_genre": dream_summary.genre_distribution[0].genre if dream_summary.genre_distribution else "None",
                    "top_art_style": dream_summary.art_style_distribution[0].art_style if dream_summary.art_style_distribution else "None"
                }
            },
            "overall_stats": {
                "top_genre": all_summary.genre_distribution[0].genre if all_summary.genre_distribution else "None",
                "top_art_style": all_summary.art_style_distribution[0].art_style if all_summary.art_style_distribution else "None",
                "insights_available": all_summary.insights_available
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user analytics overview: {str(e)}"
        )

@router.get("/analytics/user/{user_id}/recent-activity")
async def get_user_recent_activity(
    user_id: int,
    world_type: Optional[WorldType] = None,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    """Get user's recent comic creation activity"""
    try:
        comics = AnalyticsService.get_user_comics_for_analytics(session, user_id, world_type)
        
        recent_activity = []
        for comic in comics[:limit]:
            recent_activity.append({
                "id": comic.id,
                "title": comic.title,
                "concept": comic.concept,
                "genre": comic.genre,
                "art_style": comic.art_style,
                "world_type": comic.world_type.value,
                "created_at": comic.created_at.isoformat(),
                "is_favorite": comic.is_favorite,
                "view_count": comic.view_count
            })
        
        return {
            "user_id": user_id,
            "world_type": world_type.value if world_type else "all",
            "total_comics": len(comics),
            "recent_activity": recent_activity
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent activity: {str(e)}"
        )

@router.get("/analytics/user/{user_id}/creativity-score")
async def get_user_creativity_score(
    user_id: int,
    world_type: Optional[WorldType] = None,
    session: Session = Depends(get_session)
):
    """Calculate a creativity score based on user's comic diversity and patterns"""
    try:
        comics = AnalyticsService.get_user_comics_for_analytics(session, user_id, world_type)
        
        if not comics:
            return {
                "user_id": user_id,
                "creativity_score": 0,
                "factors": {
                    "genre_diversity": 0,
                    "art_style_diversity": 0,
                    "concept_complexity": 0,
                    "activity_level": 0
                },
                "message": "No comics found for analysis"
            }
        
        # Calculate diversity factors
        unique_genres = len(set(comic.genre for comic in comics))
        unique_art_styles = len(set(comic.art_style for comic in comics))
        total_comics = len(comics)
        
        # Calculate concept complexity (average length of concepts)
        avg_concept_length = sum(len(comic.concept) for comic in comics) / total_comics
        
        # Calculate scores (0-100 scale)
        genre_diversity_score = min(unique_genres * 20, 100)  # 5+ genres = 100
        art_style_diversity_score = min(unique_art_styles * 25, 100)  # 4+ styles = 100
        concept_complexity_score = min(avg_concept_length / 10, 100)  # 1000+ chars = 100
        activity_level_score = min(total_comics * 10, 100)  # 10+ comics = 100
        
        # Overall creativity score (weighted average)
        creativity_score = (
            genre_diversity_score * 0.3 +
            art_style_diversity_score * 0.3 +
            concept_complexity_score * 0.2 +
            activity_level_score * 0.2
        )
        
        return {
            "user_id": user_id,
            "world_type": world_type.value if world_type else "all",
            "creativity_score": round(creativity_score, 1),
            "factors": {
                "genre_diversity": round(genre_diversity_score, 1),
                "art_style_diversity": round(art_style_diversity_score, 1),
                "concept_complexity": round(concept_complexity_score, 1),
                "activity_level": round(activity_level_score, 1)
            },
            "stats": {
                "total_comics": total_comics,
                "unique_genres": unique_genres,
                "unique_art_styles": unique_art_styles,
                "avg_concept_length": round(avg_concept_length, 1)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate creativity score: {str(e)}"
        )

# Debug endpoint to test data fetching
@router.get("/analytics/debug/user/{user_id}/comics")
async def debug_user_comics(
    user_id: int,
    world_type: Optional[WorldType] = None,
    session: Session = Depends(get_session)
):
    """Debug endpoint to check what comics are available for a user"""
    try:
        print(f"🔍 DEBUG ENDPOINT: Checking comics for user {user_id}, world_type: {world_type}")
        
        if world_type:
            comics = session.exec(
                select(ComicsPage).where(
                    ComicsPage.user_id == user_id,
                    ComicsPage.world_type == world_type
                ).order_by(ComicsPage.created_at.desc())
            ).all()
        else:
            comics = session.exec(
                select(ComicsPage).where(ComicsPage.user_id == user_id)
                .order_by(ComicsPage.created_at.desc())
            ).all()
        
        print(f"🔍 DEBUG ENDPOINT: Found {len(comics)} comics")
        
        # Group by world type
        world_counts = {}
        for comic in comics:
            world = comic.world_type.value
            if world not in world_counts:
                world_counts[world] = 0
            world_counts[world] += 1
        
        # Sample comics for each world
        sample_comics = {}
        for world in world_counts.keys():
            world_comics = [c for c in comics if c.world_type.value == world]
            sample_comics[world] = [
                {
                    "id": comic.id,
                    "concept": comic.concept[:100] + "..." if len(comic.concept) > 100 else comic.concept,
                    "genre": comic.genre,
                    "art_style": comic.art_style,
                    "created_at": comic.created_at.isoformat(),
                    "is_favorite": comic.is_favorite,
                    "is_public": comic.is_public
                }
                for comic in world_comics[:5]  # First 5 comics
            ]
        
        return {
            "user_id": user_id,
            "world_type_filter": world_type.value if world_type else "all",
            "total_comics": len(comics),
            "world_counts": world_counts,
            "sample_comics": sample_comics,
            "debug_info": {
                "query_executed": f"user_id={user_id}, world_type={world_type.value if world_type else 'all'}",
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        print(f"❌ DEBUG ENDPOINT: Exception: {e}")
        import traceback
        print(f"❌ DEBUG ENDPOINT: Full traceback: {traceback.format_exc()}")
        
        return {
            "error": str(e),
            "user_id": user_id,
            "world_type_filter": world_type.value if world_type else "all",
            "total_comics": 0,
            "world_counts": {},
            "sample_comics": {},
            "debug_info": {
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            }
        }

# Compatibility route for /analytics/weekly-insight/{user_id}
@router.get("/analytics/weekly-insight/{user_id}", response_model=WeeklyInsight)
async def get_weekly_insight_compat(
    user_id: int,
    world_type: Optional[WorldType] = None,
    session: Session = Depends(get_session)
):
    return await get_weekly_insight(user_id, world_type, session)

# Compatibility route for /analytics/psychological-assumptions/imagination_world/{user_id}
@router.post("/analytics/psychological-assumptions/imagination_world/{user_id}", response_model=CrossWorldPsychologicalAssumption)
async def generate_imagination_world_psychological_assumptions_compat(
    user_id: int,
    session: Session = Depends(get_session)
):
    return await generate_imagination_world_psychological_assumptions(user_id, session)
