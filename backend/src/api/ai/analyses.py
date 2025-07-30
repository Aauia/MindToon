from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, select
from pydantic import BaseModel
from enum import Enum
from api.chat.models import WorldType, ComicsPage
from api.auth.models import User
from api.ai.llms import get_openai_llm
import json
import re

class DigestPeriod(str, Enum):
    """Enum for different digest periods"""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"

def get_utc_now():
    return datetime.now().replace(tzinfo=timezone.utc)

class AnalyticsEntry(SQLModel, table=True):
    """Model for tracking user comic generation analytics"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # User relationship
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship()
    
    # Comic generation data
    prompt: str = Field(max_length=2000)  # User's original prompt
    genre: str = Field(max_length=100)
    art_style: str = Field(max_length=100)
    world_type: WorldType = Field()
    
    # Comic reference (optional - links to the actual comic)
    comic_id: Optional[int] = Field(default=None, foreign_key="comicspage.id")
    
    # Analytics metadata
    created_at: datetime = Field(default_factory=get_utc_now)
    
    # Analysis results (cached)
    prompt_analysis: Optional[str] = Field(default=None)  # LLM analysis of prompt themes
    emotion_tags: Optional[str] = Field(default=None)  # JSON array of detected emotions
    creativity_score: Optional[float] = Field(default=None)  # 0-1 score
    
    class Config:
        from_attributes = True

class AnalyticsInsight(SQLModel, table=True):
    """Model for storing user insights and patterns"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # User relationship
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship()
    
    # Insight metadata
    insight_type: str = Field(max_length=100)  # "pattern_analysis", "weekly_summary", etc.
    title: str = Field(max_length=200)
    description: str = Field(max_length=2000)
    
    # Insight data (JSON)
    data: str = Field()  # JSON string containing insight data
    
    # Timestamps
    created_at: datetime = Field(default_factory=get_utc_now)
    expires_at: Optional[datetime] = Field(default=None)  # For temporary insights
    
    class Config:
        from_attributes = True


# Pydantic schemas for API requests/responses
class AnalyticsEntryCreate(BaseModel):
    prompt: str
    genre: str
    art_style: str
    world_type: WorldType
    comic_id: Optional[int] = None

class GenreStats(BaseModel):
    genre: str
    count: int
    percentage: float

class ArtStyleStats(BaseModel):
    art_style: str
    count: int
    percentage: float

class WorldStats(BaseModel):
    world_type: WorldType
    count: int
    percentage: float

class TimeSeriesData(BaseModel):
    date: str
    count: int
    genres: List[str]
    art_styles: List[str]

class PromptAnalysis(BaseModel):
    themes: List[str]
    emotions: List[str]
    language_style: str
    creativity_indicators: List[str]
    summary: str

class WeeklyInsight(BaseModel):
    top_genres: List[GenreStats]
    top_art_styles: List[ArtStyleStats]
    world_distribution: List[WorldStats]
    prompt_patterns: PromptAnalysis
    total_comics: int
    week_start: str
    week_end: str

class AnalyticsSummary(BaseModel):
    total_entries: int
    genre_distribution: List[GenreStats]
    art_style_distribution: List[ArtStyleStats]
    world_distribution: List[WorldStats]
    time_series: List[TimeSeriesData]
    recent_prompts: List[str]
    insights_available: bool

class InsightResponse(BaseModel):
    success: bool
    insight_type: str
    title: str
    description: str
    data: Dict[str, Any]
    created_at: str

# New psychological analysis models
class WorldPsychologicalProfile(BaseModel):
    world_type: str
    dominant_emotional_tone: str
    most_common_genres: List[str]
    recurring_symbols: List[str]
    typical_character_role: str
    psychological_theme: str
    comic_count: int

class CrossWorldPsychologicalAssumption(BaseModel):
    user_id: int
    analysis_date: str
    world_profiles: Dict[str, WorldPsychologicalProfile]
    cross_world_patterns: Dict[str, Any]
    psychological_assumption: str
    confidence_level: float
    recommendation_areas: List[str]

class ComicRecommendation(BaseModel):
    """Model for AI-generated comic concepts based on user preferences"""
    title: str
    concept: str
    suggested_author: str  # AI suggests who could write this
    recommended_platform: str  # Where users could read this type of comic
    genre: str
    art_style: str
    main_character: str
    setting: str
    plot_summary: str
    unique_elements: List[str]
    confidence_score: float
    reasoning: str
    similar_to_user_patterns: List[str]

class ComicRecommendationsResponse(BaseModel):
    """Response model for comic recommendations"""
    user_id: int
    recommendations: List[ComicRecommendation]
    based_on: Dict[str, Any]  # What the recommendations are based on
    total_recommendations: int

# Analytics Service Functions
class AnalyticsService:
    """Service class for handling analytics operations based on existing comics data"""
    
    @staticmethod
    def get_user_comics_for_analytics(session, user_id: int, world_type: Optional[WorldType] = None) -> List[ComicsPage]:
        """Get user's comics for analytics analysis, optionally filtered by world type"""
        query = select(ComicsPage).where(ComicsPage.user_id == user_id)
        
        # Filter by world type if specified
        if world_type:
            query = query.where(ComicsPage.world_type == world_type)
        
        # Order by creation date for time series analysis
        query = query.order_by(ComicsPage.created_at.desc())
        
        return session.exec(query).all()
    
    @staticmethod
    def get_user_analytics_summary(session, user_id: int, world_type: Optional[WorldType] = None) -> AnalyticsSummary:
        """Get comprehensive analytics summary for a user based on existing comics, optionally filtered by world type"""
        # Get user's comics for analysis
        comics = AnalyticsService.get_user_comics_for_analytics(session, user_id, world_type)
        
        if not comics:
            return AnalyticsSummary(
                total_entries=0,
                genre_distribution=[],
                art_style_distribution=[],
                world_distribution=[],
                time_series=[],
                recent_prompts=[],
                insights_available=False
            )
        
        # Calculate genre distribution
        genre_counts = {}
        for comic in comics:
            # Normalize genre to lowercase to prevent duplicates like 'drama' and 'Drama'
            normalized_genre = comic.genre.lower().strip()
            genre_counts[normalized_genre] = genre_counts.get(normalized_genre, 0) + 1
        
        total = len(comics)
        genre_distribution = [
            GenreStats(
                genre=genre,
                count=count,
                percentage=round((count / total) * 100, 2)
            )
            for genre, count in genre_counts.items()
        ]
        
        # Calculate art style distribution
        style_counts = {}
        for comic in comics:
            # Normalize art style to lowercase to prevent duplicates
            normalized_style = comic.art_style.lower().strip()
            style_counts[normalized_style] = style_counts.get(normalized_style, 0) + 1
        
        art_style_distribution = [
            ArtStyleStats(
                art_style=style,
                count=count,
                percentage=round((count / total) * 100, 2)
            )
            for style, count in style_counts.items()
        ]
        
        # Calculate world distribution (only if not filtered by world)
        world_distribution = []
        if not world_type:
            world_counts = {}
            for comic in comics:
                world_counts[comic.world_type] = world_counts.get(comic.world_type, 0) + 1
    
            world_distribution = [
                WorldStats(
                    world_type=world_type,
                    count=count,
                    percentage=round((count / total) * 100, 2)
                )
                for world_type, count in world_counts.items()
            ]
        else:
            # If filtered by world, show 100% for that world
            world_distribution = [
                WorldStats(
                    world_type=world_type,
                    count=total,
                    percentage=100.0
                )
            ]
        
        # Generate time series data (last 30 days)
        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        time_series = []
        current_date = start_date
        while current_date <= end_date:
            day_comics = [
                comic for comic in comics 
                if comic.created_at.date() == current_date.date()
            ]
            
            if day_comics:
                time_series.append(TimeSeriesData(
                    date=current_date.strftime("%Y-%m-%d"),
                    count=len(day_comics),
                    genres=[comic.genre for comic in day_comics],
                    art_styles=[comic.art_style for comic in day_comics]
                ))
            
            current_date += timedelta(days=1)
        
        # Get recent prompts (last 10)
        recent_prompts = [comic.concept for comic in comics[:10]]
        
        # Check if insights are available (every 5 comics)
        insights_available = len(comics) % 5 == 0 and len(comics) > 0
        
        return AnalyticsSummary(
            total_entries=total,
            genre_distribution=genre_distribution,
            art_style_distribution=art_style_distribution,
            world_distribution=world_distribution,
            time_series=time_series,
            recent_prompts=recent_prompts,
            insights_available=insights_available
        )
    
    @staticmethod
    async def analyze_prompt_themes(concepts: List[str]) -> PromptAnalysis:
        """Use LLM to analyze comic concepts and patterns"""
        try:
            llm = get_openai_llm()
            
            # Combine recent concepts for analysis
            combined_concepts = "\n".join([f"- {concept}" for concept in concepts[:20]])  # Last 20 concepts
            
            analysis_prompt = f"""
            Analyze the following comic concepts from a user. Focus on:
            1. Recurring themes and topics
            2. Emotional patterns and moods
            3. Language style and creativity indicators
            4. Overall creative expression patterns
            
            Comic Concepts:
            {combined_concepts}
            
            Provide your analysis in the following JSON format:
            {{
                "themes": ["theme1", "theme2"],
                "emotions": ["emotion1", "emotion2"],
                "language_style": "descriptive/concise/creative/etc",
                "creativity_indicators": ["indicator1", "indicator2"],
                "summary": "Brief summary of the user's creative patterns"
            }}
            
            Focus on the user's creative intent and expression, not the content of the comics themselves.
            """
            
            response = await llm.ainvoke(analysis_prompt)
            analysis_data = json.loads(response.content)
            
            return PromptAnalysis(**analysis_data)
            
        except Exception as e:
            # Fallback analysis
            return PromptAnalysis(
                themes=["creative expression"],
                emotions=["enthusiasm"],
                language_style="descriptive",
                creativity_indicators=["imaginative concepts"],
                summary="User shows creative engagement with comic generation"
            )
    
    @staticmethod
    async def generate_weekly_insight(session, user_id: int, world_type: Optional[WorldType] = None) -> WeeklyInsight:
        """Legacy function for backward compatibility - uses weekly period"""
        return await AnalyticsService.generate_insight_by_period(session, user_id, DigestPeriod.WEEKLY, world_type)
    
    @staticmethod
    async def generate_psychological_assumptions(session, user_id: int, world_type: Optional[WorldType] = None) -> CrossWorldPsychologicalAssumption:
        """Generate psychological assumptions based on user's comic prompts for a specific world or all worlds"""
        try:
            print(f"🔍 DEBUG: Starting psychological analysis for user {user_id}, world_type: {world_type}")
            llm = get_openai_llm()
            
            if world_type:
                # Analyze specific world only
                print(f"🔍 DEBUG: Fetching comics for specific world: {world_type.value}")
                world_comics = AnalyticsService.get_user_comics_for_analytics(session, user_id, world_type)
                print(f"🔍 DEBUG: Found {len(world_comics)} comics for {world_type.value}")
                
                if not world_comics:
                    print(f"❌ DEBUG: No comics found for {world_type.value}")
                    raise ValueError(f"No comic data available for {world_type.value}")
                
                # Log sample comics for debugging
                print(f"🔍 DEBUG: Sample comics for {world_type.value}:")
                for i, comic in enumerate(world_comics[:5]):  # Show first 5
                    print(f"  Comic {i+1}: '{comic.concept[:50]}...' (Genre: {comic.genre})")
                
                # Prepare data for single world analysis
                world_data = {
                    world_type.value: {
                        "concepts": [comic.concept for comic in world_comics],
                        "genres": [comic.genre for comic in world_comics],
                        "count": len(world_comics)
                    }
                }
                
                print(f"🔍 DEBUG: Prepared data for {world_type.value}: {len(world_data[world_type.value]['concepts'])} concepts, {len(world_data[world_type.value]['genres'])} genres")
                
                # Create analysis prompt for single world
                analysis_prompt = f"""
                Analyze the user's comic creation patterns in the {world_type.value} world. Identify:

                1. **Dominant emotional tone** - What emotional atmosphere prevails?
                2. **Most common genre(s)** - What story types does the user prefer?
                3. **Recurring symbols or story elements** - What motifs appear repeatedly?
                4. **Typical character role** - What character archetypes dominate (hero, observer, victim, wanderer, etc.)?

                Then synthesize a psychologically informed assumption about the user based on their patterns in this specific world.

                **{world_type.value.replace('_', ' ').title()} Data:**
                Concepts: {world_data[world_type.value]['concepts']}
                Genres: {world_data[world_type.value]['genres']}
                Count: {world_data[world_type.value]['count']}

                Provide your analysis in the following JSON format:
                {{
                    "world_profiles": {{
                        "{world_type.value}": {{
                            "dominant_emotional_tone": "string",
                            "most_common_genres": ["genre1", "genre2"],
                            "recurring_symbols": ["symbol1", "symbol2"],
                            "typical_character_role": "string",
                            "psychological_theme": "string"
                        }}
                    }},
                    "cross_world_patterns": {{
                        "emotional_consistency": "Analysis of emotional patterns in this world",
                        "genre_evolution": "Analysis of genre preferences in this world",
                        "character_development": "Analysis of character roles in this world",
                        "symbolic_connections": "Analysis of recurring symbols in this world"
                    }},
                    "psychological_assumption": "string",
                    "confidence_level": 0.85,
                    "recommendation_areas": ["area1", "area2", "area3"]
                }}

                Focus on psychological insights specific to the {world_type.value} world that could be:
                - Visualized in a dashboard
                - Used to suggest stories
                - Trigger recommendations or reflections
                """
                
                print(f"🔍 DEBUG: Created analysis prompt for {world_type.value} (length: {len(analysis_prompt)} characters)")
                
            else:
                # Analyze all worlds (original functionality)
                print(f"🔍 DEBUG: Fetching comics for all worlds")
                imagination_comics = AnalyticsService.get_user_comics_for_analytics(
                    session, user_id, WorldType.IMAGINATION_WORLD
                )
                mind_comics = AnalyticsService.get_user_comics_for_analytics(
                    session, user_id, WorldType.MIND_WORLD
                )
                dream_comics = AnalyticsService.get_user_comics_for_analytics(
                    session, user_id, WorldType.DREAM_WORLD
                )
                
                print(f"🔍 DEBUG: Found comics - Imagination: {len(imagination_comics)}, Mind: {len(mind_comics)}, Dream: {len(dream_comics)}")
                
                # Prepare data for analysis
                world_data = {
                    "imagination_world": {
                        "concepts": [comic.concept for comic in imagination_comics],
                        "genres": [comic.genre for comic in imagination_comics],
                        "count": len(imagination_comics)
                    },
                    "mind_world": {
                        "concepts": [comic.concept for comic in mind_comics],
                        "genres": [comic.genre for comic in mind_comics],
                        "count": len(mind_comics)
                    },
                    "dream_world": {
                        "concepts": [comic.concept for comic in dream_comics],
                        "genres": [comic.genre for comic in dream_comics],
                        "count": len(dream_comics)
                    }
                }
                
                print(f"🔍 DEBUG: Prepared data for all worlds:")
                for world, data in world_data.items():
                    print(f"  {world}: {data['count']} comics, {len(data['concepts'])} concepts")
                
                # Create analysis prompt for all worlds
                analysis_prompt = f"""
                Analyze the user's comic creation patterns across three psychological worlds. For each world, identify:

                1. **Dominant emotional tone** - What emotional atmosphere prevails?
                2. **Most common genre(s)** - What story types does the user prefer?
                3. **Recurring symbols or story elements** - What motifs appear repeatedly?
                4. **Typical character role** - What character archetypes dominate (hero, observer, victim, wanderer, etc.)?

                Then synthesize a single, psychologically informed assumption about the user based on cross-world patterns.

                **Imagination World Data:**
                Concepts: {world_data['imagination_world']['concepts']}
                Genres: {world_data['imagination_world']['genres']}
                Count: {world_data['imagination_world']['count']}

                **Mind World Data:**
                Concepts: {world_data['mind_world']['concepts']}
                Genres: {world_data['mind_world']['genres']}
                Count: {world_data['mind_world']['count']}

                **Dream World Data:**
                Concepts: {world_data['dream_world']['concepts']}
                Genres: {world_data['dream_world']['genres']}
                Count: {world_data['dream_world']['count']}

                Provide your analysis in the following JSON format:
                {{
                    "world_profiles": {{
                        "imagination_world": {{
                            "dominant_emotional_tone": "string",
                            "most_common_genres": ["genre1", "genre2"],
                            "recurring_symbols": ["symbol1", "symbol2"],
                            "typical_character_role": "string",
                            "psychological_theme": "string"
                        }},
                        "mind_world": {{
                            "dominant_emotional_tone": "string",
                            "most_common_genres": ["genre1", "genre2"],
                            "recurring_symbols": ["symbol1", "symbol2"],
                            "typical_character_role": "string",
                            "psychological_theme": "string"
                        }},
                        "dream_world": {{
                            "dominant_emotional_tone": "string",
                            "most_common_genres": ["genre1", "genre2"],
                            "recurring_symbols": ["symbol1", "symbol2"],
                            "typical_character_role": "string",
                            "psychological_theme": "string"
                        }}
                    }},
                    "cross_world_patterns": {{
                        "emotional_consistency": "string",
                        "genre_evolution": "string",
                        "character_development": "string",
                        "symbolic_connections": "string"
                    }},
                    "psychological_assumption": "string",
                    "confidence_level": 0.85,
                    "recommendation_areas": ["area1", "area2", "area3"]
                }}

                Focus on psychological insights that could be:
                - Visualized in a dashboard
                - Used to suggest stories
                - Trigger recommendations or reflections
                """
                
                print(f"🔍 DEBUG: Created analysis prompt for all worlds (length: {len(analysis_prompt)} characters)")
            
            print(f"🔍 DEBUG: Calling LLM with prompt...")
            try:
                response = await llm.ainvoke(analysis_prompt)
                print(f"🔍 DEBUG: LLM response received (length: {len(response.content)} characters)")
                print(f"🔍 DEBUG: LLM response preview: {response.content[:200]}...")
                
                import re
                raw_content = response.content.strip()
                # Remove code block markers (```json or ``` at start, ``` at end)
                lines = raw_content.splitlines()
                if lines and lines[0].strip().startswith('```'):
                    lines = lines[1:]
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                cleaned_content = '\n'.join(lines).strip()
                analysis_data = json.loads(cleaned_content)
                print(f"🔍 DEBUG: Successfully parsed LLM response as JSON")
                print(f"🔍 DEBUG: Analysis data keys: {list(analysis_data.keys())}")
                
            except json.JSONDecodeError as e:
                print(f"❌ DEBUG: Failed to parse LLM response as JSON: {e}")
                print(f"❌ DEBUG: Raw LLM response: {response.content}")
                raise Exception(f"LLM returned invalid JSON: {e}")
            except Exception as e:
                print(f"❌ DEBUG: LLM call failed: {e}")
                raise e
            
            # Create world profiles
            world_profiles = {}
            print(f"🔍 DEBUG: Creating world profiles from analysis data...")
            
            for world_name, profile_data in analysis_data["world_profiles"].items():
                print(f"🔍 DEBUG: Processing world profile for {world_name}")
                world_profiles[world_name] = WorldPsychologicalProfile(
                    world_type=world_name,
                    dominant_emotional_tone=profile_data["dominant_emotional_tone"],
                    most_common_genres=profile_data["most_common_genres"],
                    recurring_symbols=profile_data["recurring_symbols"],
                    typical_character_role=profile_data["typical_character_role"],
                    psychological_theme=profile_data["psychological_theme"],
                    comic_count=world_data[world_name]["count"] if world_name in world_data else 0
                )
                print(f"🔍 DEBUG: Created profile for {world_name} with {world_profiles[world_name].comic_count} comics")
            
            result = CrossWorldPsychologicalAssumption(
                user_id=user_id,
                analysis_date=datetime.now().isoformat(),
                world_profiles=world_profiles,
                cross_world_patterns=analysis_data["cross_world_patterns"],
                psychological_assumption=analysis_data["psychological_assumption"],
                confidence_level=analysis_data["confidence_level"],
                recommendation_areas=analysis_data["recommendation_areas"]
            )
            
            print(f"🔍 DEBUG: Successfully created psychological assumption with {len(world_profiles)} world profiles")
            print(f"🔍 DEBUG: Confidence level: {result.confidence_level}")
            print(f"🔍 DEBUG: Psychological assumption preview: {result.psychological_assumption[:100]}...")
            
            return result
            
        except Exception as e:
            print(f"❌ DEBUG: Exception in generate_psychological_assumptions: {e}")
            print(f"❌ DEBUG: Exception type: {type(e).__name__}")
            import traceback
            print(f"❌ DEBUG: Full traceback: {traceback.format_exc()}")
            
            # Fallback response
            world_name = world_type.value if world_type else "all worlds"
            print(f"🔍 DEBUG: Returning fallback response for {world_name}")
            
            return CrossWorldPsychologicalAssumption(
                user_id=user_id,
                analysis_date=datetime.now().isoformat(),
                world_profiles={},
                cross_world_patterns={
                    "emotional_consistency": f"Insufficient data for analysis in {world_name}",
                    "genre_evolution": f"Insufficient data for analysis in {world_name}",
                    "character_development": f"Insufficient data for analysis in {world_name}",
                    "symbolic_connections": f"Insufficient data for analysis in {world_name}"
                },
                psychological_assumption=f"User shows creative engagement in {world_name}",
                confidence_level=0.3,
                recommendation_areas=["Create more comics to enable deeper analysis"]
            )
    
    @staticmethod
    async def generate_insight_by_period(session, user_id: int, period: DigestPeriod = DigestPeriod.WEEKLY, world_type: Optional[WorldType] = None) -> WeeklyInsight:
        """Generate insight based on user's comic generation patterns for specified period"""
        from datetime import timedelta
        
        # Calculate date range based on period
        now = datetime.now()
        if period == DigestPeriod.WEEKLY:
            start_date = now - timedelta(days=7)
            period_name = "This Week"
        elif period == DigestPeriod.MONTHLY:
            start_date = now - timedelta(days=30)
            period_name = "This Month"
        else:  # ALL_TIME
            start_date = datetime.min.replace(tzinfo=timezone.utc)
            period_name = "All Time"
        
        # Get comics from the specified period
        query = select(ComicsPage).where(ComicsPage.user_id == user_id)
        
        if period != DigestPeriod.ALL_TIME:
            query = query.where(ComicsPage.created_at >= start_date)
            
        if world_type:
            query = query.where(ComicsPage.world_type == world_type)
            
        period_comics = session.exec(query).all()
        
        if not period_comics:
            raise ValueError(f"No data available for {period.value} insight")
        
        # Calculate period stats
        genre_counts = {}
        style_counts = {}
        world_counts = {}
        
        for comic in period_comics:
            # Normalize genre to lowercase to prevent duplicates like 'drama' and 'Drama'
            normalized_genre = comic.genre.lower().strip()
            genre_counts[normalized_genre] = genre_counts.get(normalized_genre, 0) + 1
            
            # Normalize art style as well
            normalized_style = comic.art_style.lower().strip()
            style_counts[normalized_style] = style_counts.get(normalized_style, 0) + 1
            
            world_counts[comic.world_type] = world_counts.get(comic.world_type, 0) + 1
        
        total = len(period_comics)
        
        # Top genres
        top_genres = [
            GenreStats(genre=genre, count=count, percentage=round((count/total)*100, 2))
            for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Top art styles
        top_art_styles = [
            ArtStyleStats(art_style=style, count=count, percentage=round((count/total)*100, 2))
            for style, count in sorted(style_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # World distribution
        world_distribution = [
            WorldStats(world_type=world_type, count=count, percentage=round((count/total)*100, 2))
            for world_type, count in world_counts.items()
        ]
        
        # Analyze concept patterns
        concepts = [comic.concept for comic in period_comics]
        prompt_patterns = await AnalyticsService.analyze_prompt_themes(concepts)
        
        # Calculate period start and end dates
        if period == DigestPeriod.ALL_TIME:
            period_start = "All Time"
            period_end = now.strftime("%Y-%m-%d")
        else:
            period_start = start_date.strftime("%Y-%m-%d")
            period_end = now.strftime("%Y-%m-%d")
        
        return WeeklyInsight(
            top_genres=top_genres,
            top_art_styles=top_art_styles,
            world_distribution=world_distribution,
            prompt_patterns=prompt_patterns,
            total_comics=total,
            week_start=period_start,
            week_end=period_end
        )
    
    @staticmethod
    def save_insight(session, user_id: int, insight_type: str, title: str, description: str, data: Dict[str, Any]) -> AnalyticsInsight:
        """Save an insight to the database"""
        insight = AnalyticsInsight(
            user_id=user_id,
            insight_type=insight_type,
            title=title,
            description=description,
            data=json.dumps(data)
        )
        session.add(insight)
        session.commit()
        session.refresh(insight)
        return insight
    
    @staticmethod
    def get_user_insights(session, user_id: int, insight_type: Optional[str] = None) -> List[AnalyticsInsight]:
        """Get insights for a user"""
        query = select(AnalyticsInsight).where(AnalyticsInsight.user_id == user_id)
        if insight_type:
            query = query.where(AnalyticsInsight.insight_type == insight_type)
        
        return session.exec(query).all()

    @staticmethod
    async def generate_comic_recommendations(session, user_id: int, world_type: Optional[WorldType] = None, limit: int = 5) -> ComicRecommendationsResponse:
        """Generate comic recommendations based on user's genre, art style, and prompt patterns"""
        try:
            llm = get_openai_llm()
            
            # Get user's comics for analysis
            if world_type:
                user_comics = AnalyticsService.get_user_comics_for_analytics(session, user_id, world_type)
            else:
                user_comics = AnalyticsService.get_user_comics_for_analytics(session, user_id)
            
            if not user_comics:
                raise ValueError(f"No comic data available for recommendations")
            
            # Analyze user patterns
            genres = [comic.genre for comic in user_comics]
            art_styles = [comic.art_style for comic in user_comics]
            concepts = [comic.concept for comic in user_comics]
            
            # Get most common preferences
            genre_counts = {}
            for genre in genres:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            art_style_counts = {}
            for style in art_styles:
                art_style_counts[style] = art_style_counts.get(style, 0) + 1
            
            top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            top_art_styles = sorted(art_style_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Create recommendation prompt
            analysis_prompt = f"""
            You are a recommendation engine for real, existing comic books and graphic novels.

            Based on the user's comic creation history, recommend {limit} *real* published comics that match their preferences.

            User's Patterns:
            - Most used genres: {[genre for genre, count in top_genres]}
            - Most used art styles: {[style for style, count in top_art_styles]}
            - Recent concepts: {concepts[:10]}

            Instructions:
            - Recommend real, published comics (no AI-generated content)
            - Match the user’s dominant genres, art styles, and story elements
            - For each recommendation, include:
                - Title
                - Author(s)
                - Description or plot summary
                - Genre
                - Art style or format
                - Publication date (if known)
                - Platform (e.g., "Webtoon", "Comixology", "Physical Graphic Novel", "Manga", etc.)
                - Similarity score (0.0–1.0): how well it fits user's past preferences
                - Reasoning: why this comic matches user's pattern

            Important:
            - ONLY recommend real, existing comic books, manga, or webtoons
            - Prefer well-known works but can include lesser-known gems
            - Recommendations can be from different regions (US, Japan, Korea, Europe, etc.)
            - Make sure the response is valid JSON. No extra explanations or markdown formatting.

            Output must follow this exact JSON structure:
            {{
                "recommendations": [
                    {{
                        "title": "Comic Title",
                        "author": "Author Name",
                        "description": "Short plot summary",
                        "genre": "Genre",
                        "art_style": "Art style or format",
                        "publication_date": "YYYY-MM-DD",
                        "platform": "Platform name",
                        "similarity_score": 0.87,
                        "reasoning": "Explanation of why this fits the user's patterns"
                    }}
                ]
            }}
            """

            
            # Generate recommendations using LLM
            response = await llm.ainvoke(analysis_prompt)
            
            # Parse the response
            try:
                import json
                # Handle different response types
                if isinstance(response, str):
                    response_text = response
                elif hasattr(response, 'content'):
                    # Handle AIMessage objects
                    content = response.content
                    if isinstance(content, str):
                        response_text = content
                    else:
                        # If content is not a string, try to convert it
                        response_text = str(content)
                else:
                    # Try to convert to string and parse
                    response_text = str(response)
                
                # Extract JSON from the response
                recommendations_data = AnalyticsService._extract_json_from_response(response_text)
                
                recommendations = []
                for rec_data in recommendations_data.get("recommendations", []):
                    recommendation = ComicRecommendation(
                        title=rec_data.get("title", "Unknown Title"),
                        concept=rec_data.get("description", rec_data.get("concept", "No description available")),
                        suggested_author=rec_data.get("author", rec_data.get("suggested_author", "Unknown Author")),
                        recommended_platform=rec_data.get("platform", rec_data.get("recommended_platform", "Comic platforms")),
                        genre=rec_data.get("genre", "Unknown Genre"),
                        art_style=rec_data.get("art_style", "Unknown Style"),
                        main_character=rec_data.get("main_character", "Various characters"),
                        setting=rec_data.get("setting", "Various settings"),
                        plot_summary=rec_data.get("plot_summary", rec_data.get("description", "No plot summary available")),
                        unique_elements=rec_data.get("unique_elements", ["Engaging storytelling"]),
                        confidence_score=rec_data.get("similarity_score", rec_data.get("confidence_score", 0.7)),
                        reasoning=rec_data.get("reasoning", "Recommended based on user preferences"),
                        similar_to_user_patterns=rec_data.get("similar_to_user_patterns", ["Matches user preferences"])
                    )
                    recommendations.append(recommendation)
                
                # Create response
                based_on = {
                    "total_comics_analyzed": len(user_comics),
                    "top_genres": [{"genre": genre, "count": count} for genre, count in top_genres],
                    "top_art_styles": [{"style": style, "count": count} for style, count in top_art_styles],
                    "world_type": world_type.value if world_type else "all_worlds",
                    "analysis_date": datetime.now().isoformat()
                }
                
                return ComicRecommendationsResponse(
                    user_id=user_id,
                    recommendations=recommendations,
                    based_on=based_on,
                    total_recommendations=len(recommendations)
                )
                
            except Exception as parse_error:
                print(f"❌ DEBUG: Error parsing LLM response: {parse_error}")
                print(f"❌ DEBUG: Response type: {type(response)}")
                print(f"❌ DEBUG: Response content: {response}")
                # Fallback: generate simple recommendations
                return AnalyticsService._generate_fallback_recommendations(user_id, top_genres, top_art_styles, limit, world_type)
                
        except Exception as e:
            print(f"❌ DEBUG: Error in generate_comic_recommendations: {e}")
            raise e
    
    @staticmethod
    def _generate_fallback_recommendations(user_id: int, top_genres: List[tuple], top_art_styles: List[tuple], limit: int, world_type: Optional[WorldType] = None) -> ComicRecommendationsResponse:
        """Generate fallback recommendations when LLM fails"""
        recommendations = []
        
        # Simple fallback recommendations based on user's top preferences
        for i in range(min(limit, len(top_genres) * len(top_art_styles))):
            genre_idx = i % len(top_genres)
            style_idx = (i // len(top_genres)) % len(top_art_styles)
            
            genre = top_genres[genre_idx][0]
            art_style = top_art_styles[style_idx][0]
            
            # Generate simple concept based on genre
            concept_templates = {
                "action": f"A thrilling {genre} adventure with dynamic characters and intense battles",
                "romance": f"A heartwarming {genre} story about love and relationships",
                "horror": f"A spine-chilling {genre} tale with supernatural elements",
                "sci-fi": f"A futuristic {genre} exploration of technology and space",
                "fantasy": f"A magical {genre} journey through enchanted realms",
                "drama": f"An emotional {genre} story exploring human relationships and conflicts",
                "comedy": f"A hilarious {genre} story with witty humor and fun characters",
                "adventure": f"An exciting {genre} quest with exploration and discovery"
            }
            
            # Author suggestions based on genre
            author_suggestions = {
                "action": "Stan Lee",
                "romance": "Natsuki Takaya",
                "horror": "Junji Ito",
                "sci-fi": "Katsuhiro Otomo",
                "fantasy": "Hiromu Arakawa",
                "drama": "Naoki Urasawa",
                "comedy": "Akira Toriyama",
                "adventure": "Eiichiro Oda"
            }
            
            # Platform suggestions based on genre
            platform_suggestions = {
                "action": "Comixology",
                "romance": "Webtoon",
                "horror": "Physical Graphic Novel",
                "sci-fi": "Digital Comics",
                "fantasy": "Manga",
                "drama": "Comixology",
                "comedy": "Webtoon",
                "adventure": "Manga"
            }
            
            concept = concept_templates.get(genre.lower(), f"An engaging {genre} story with {art_style} art style")
            suggested_author = author_suggestions.get(genre.lower(), "Various Authors")
            recommended_platform = platform_suggestions.get(genre.lower(), "Comic platforms")
            
            # Create a simple AI-generated concept
            recommendation = ComicRecommendation(
                title=f"The {genre.title()} Adventure",
                concept=concept,
                suggested_author=suggested_author,
                recommended_platform=recommended_platform,
                genre=genre,
                art_style=art_style,
                main_character=f"A brave protagonist in a {genre} world",
                setting=f"A mysterious {genre} setting with unique elements",
                plot_summary=f"An exciting journey through a {genre} world with {art_style} visuals",
                unique_elements=[f"{genre} elements", f"{art_style} art style", "Imaginative storytelling"],
                confidence_score=0.7,
                reasoning=f"Based on your preference for {genre} genre and {art_style} art style",
                similar_to_user_patterns=[f"Uses {genre} genre", f"Uses {art_style} style"]
            )
            
            recommendations.append(recommendation)
        
        based_on = {
            "total_comics_analyzed": 0,
            "top_genres": [{"genre": genre, "count": count} for genre, count in top_genres],
            "top_art_styles": [{"style": style, "count": count} for style, count in top_art_styles],
            "world_type": world_type.value if world_type else "all_worlds",
            "analysis_date": datetime.now().isoformat(),
            "fallback_generated": True,
            "note": "AI service unavailable - try again for personalized comic concepts"
        }
        
        return ComicRecommendationsResponse(
            user_id=user_id,
            recommendations=recommendations,
            based_on=based_on,
            total_recommendations=len(recommendations)
        )

    @staticmethod
    def _extract_json_from_response(response_text: str) -> dict:
        """Extract JSON from LLM response that might contain extra text"""
        import json
        import re
        
        # Try to find JSON in the response
        # Look for content between curly braces
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, response_text, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        
        # If no JSON found, try to parse the entire response
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            raise ValueError(f"Could not extract valid JSON from response: {response_text[:200]}...")
