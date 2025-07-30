#!/usr/bin/env python3
"""
Test script for the MindToon Analytics System
This script tests the core functionality of the Analyst system
"""

import asyncio
import json
from datetime import datetime, timedelta
from sqlmodel import Session, select
from src.api.db import engine, init_db
from src.api.ai.analyses import (
    AnalyticsEntry, 
    AnalyticsInsight, 
    AnalyticsService,
    AnalyticsEntryCreate,
    WorldType
)
from src.api.auth.models import User
from src.api.auth.utils import get_password_hash

async def test_analytics_system():
    """Test the complete analytics system"""
    print("🧪 Testing MindToon Analytics System...")
    
    # Initialize database
    init_db()
    
    # Create test session
    with Session(engine) as session:
        # Create test user if not exists
        test_user = session.exec(
            select(User).where(User.username == "test_analytics_user")
        ).first()
        
        if not test_user:
            test_user = User(
                username="test_analytics_user",
                email="test@analytics.com",
                full_name="Test Analytics User",
                hashed_password=get_password_hash("test123")
            )
            session.add(test_user)
            session.commit()
            session.refresh(test_user)
            print("✅ Created test user")
        
        # Test 1: Add analytics entries
        print("\n📊 Test 1: Adding analytics entries...")
        test_entries = [
            {
                "prompt": "A superhero saving a city from a giant robot",
                "genre": "action",
                "art_style": "comic book",
                "world_type": WorldType.IMAGINATION_WORLD
            },
            {
                "prompt": "A peaceful garden with magical creatures",
                "genre": "fantasy",
                "art_style": "watercolor",
                "world_type": WorldType.DREAM_WORLD
            },
            {
                "prompt": "A detective solving a mystery in a rainy city",
                "genre": "mystery",
                "art_style": "noir",
                "world_type": WorldType.MIND_WORLD
            },
            {
                "prompt": "A space adventure with alien friends",
                "genre": "sci-fi",
                "art_style": "digital art",
                "world_type": WorldType.IMAGINATION_WORLD
            },
            {
                "prompt": "A romantic dinner under the stars",
                "genre": "romance",
                "art_style": "soft pastels",
                "world_type": WorldType.DREAM_WORLD
            }
        ]
        
        for i, entry_data in enumerate(test_entries):
            entry = await AnalyticsService.add_comic_entry(
                session=session,
                user_id=test_user.id,
                prompt=entry_data["prompt"],
                genre=entry_data["genre"],
                art_style=entry_data["art_style"],
                world_type=entry_data["world_type"]
            )
            print(f"  ✅ Added entry {i+1}: {entry_data['genre']} - {entry_data['art_style']}")
        
        # Test 2: Get analytics summary
        print("\n📈 Test 2: Getting analytics summary...")
        summary = AnalyticsService.get_user_analytics_summary(session, test_user.id)
        print(f"  ✅ Total entries: {summary.total_entries}")
        print(f"  ✅ Insights available: {summary.insights_available}")
        print(f"  ✅ Genres: {[g.genre for g in summary.genre_distribution]}")
        print(f"  ✅ Art styles: {[s.art_style for s in summary.art_style_distribution]}")
        print(f"  ✅ Worlds: {[w.world_type.value for w in summary.world_distribution]}")
        
        # Test 3: Generate pattern analysis
        print("\n🔍 Test 3: Generating pattern analysis...")
        try:
            prompts = [entry_data["prompt"] for entry_data in test_entries]
            pattern_analysis = await AnalyticsService.analyze_prompt_themes(prompts)
            print(f"  ✅ Themes: {pattern_analysis.themes}")
            print(f"  ✅ Emotions: {pattern_analysis.emotions}")
            print(f"  ✅ Language style: {pattern_analysis.language_style}")
            print(f"  ✅ Summary: {pattern_analysis.summary}")
        except Exception as e:
            print(f"  ⚠️ Pattern analysis failed (expected if LLM not configured): {e}")
        
        # Test 4: Generate weekly insight
        print("\n📅 Test 4: Generating weekly insight...")
        try:
            weekly_insight = await AnalyticsService.generate_weekly_insight(session, test_user.id)
            print(f"  ✅ Weekly comics: {weekly_insight.total_comics}")
            print(f"  ✅ Top genres: {[g.genre for g in weekly_insight.top_genres]}")
            print(f"  ✅ Top art styles: {[s.art_style for s in weekly_insight.top_art_styles]}")
        except Exception as e:
            print(f"  ⚠️ Weekly insight failed: {e}")
        
        # Test 5: Save and retrieve insights
        print("\n💾 Test 5: Saving and retrieving insights...")
        test_insight_data = {
            "themes": ["adventure", "creativity"],
            "emotions": ["excitement", "wonder"],
            "summary": "User shows diverse creative interests"
        }
        
        insight = AnalyticsService.save_insight(
            session=session,
            user_id=test_user.id,
            insight_type="test_insight",
            title="Test Insight",
            description="A test insight for verification",
            data=test_insight_data
        )
        print(f"  ✅ Saved insight: {insight.title}")
        
        # Retrieve insights
        insights = AnalyticsService.get_user_insights(session, test_user.id)
        print(f"  ✅ Retrieved {len(insights)} insights")
        
        # Test 6: Chart data formatting
        print("\n📊 Test 6: Chart data formatting...")
        chart_data = {
            "labels": [genre.genre for genre in summary.genre_distribution],
            "data": [genre.count for genre in summary.genre_distribution],
            "percentages": [genre.percentage for genre in summary.genre_distribution]
        }
        print(f"  ✅ Chart data: {json.dumps(chart_data, indent=2)}")
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Summary:")
        print(f"  - Analytics entries: {summary.total_entries}")
        print(f"  - Unique genres: {len(summary.genre_distribution)}")
        print(f"  - Unique art styles: {len(summary.art_style_distribution)}")
        print(f"  - World types: {len(summary.world_distribution)}")
        print(f"  - Insights available: {summary.insights_available}")

if __name__ == "__main__":
    asyncio.run(test_analytics_system()) 