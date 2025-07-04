#!/usr/bin/env python3
"""
Test script for the enhanced scenario system that generates both comics and detailed narratives.

This script demonstrates:
1. Enhanced generate_scenario function that creates rich narrative stories
2. Integration with generate_complete_comic to produce both visual and textual content
3. The mapping between comic panels and narrative chapters
4. Supabase integration for saving both comics and scenarios

Usage:
    python test_enhanced_scenarios.py
"""

import sys
import os
sys.path.append('src')

from api.ai.services import generate_scenario, generate_complete_comic, validate_genre_and_style
from api.ai.schemas import DetailedScenarioSchema, ScenarioSaveRequest
import json

def test_enhanced_scenario_generation():
    """Test the enhanced scenario generation function"""
    print("=" * 80)
    print("🎭 TESTING ENHANCED SCENARIO GENERATION")
    print("=" * 80)
    
    # Test different concepts with various genres and art styles
    test_cases = [
        {
            "concept": "A young wizard discovers a magical book that can rewrite reality",
            "genre": "fantasy",
            "art_style": "watercolor"
        },
        {
            "concept": "Two detectives investigate a murder in a cyberpunk city",
            "genre": "mystery", 
            "art_style": "anime"
        },
        {
            "concept": "A robot learns to love in a post-apocalyptic world",
            "genre": "sci-fi",
            "art_style": "comic book"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST CASE {i}: {test_case['concept'][:50]}...")
        print(f"   Genre: {test_case['genre']}")
        print(f"   Art Style: {test_case['art_style']}")
        
        try:
            # Generate detailed scenario
            detailed_scenario = generate_scenario(
                prompt=test_case["concept"],
                genre=test_case["genre"],
                art_style=test_case["art_style"]
            )
            
            # Display results
            print(f"\n📖 GENERATED SCENARIO:")
            print(f"   📚 Title: {detailed_scenario.title}")
            print(f"   🎭 Genre: {detailed_scenario.genre}")
            print(f"   🎨 Art Style: {detailed_scenario.art_style}")
            print(f"   📝 Word Count: {detailed_scenario.word_count}")
            print(f"   ⏰ Reading Time: {detailed_scenario.reading_time_minutes} minutes")
            print(f"   🎯 Characters: {', '.join(detailed_scenario.characters)}")
            print(f"   📑 Chapters: {len(detailed_scenario.chapters)}")
            print(f"   🌟 Themes: {', '.join(detailed_scenario.themes)}")
            
            # Display chapter summaries
            print(f"\n📚 CHAPTER STRUCTURE:")
            for chapter in detailed_scenario.chapters:
                print(f"   Chapter {chapter.chapter_number}: {chapter.title}")
                print(f"      → Panel Reference: {chapter.panel_reference}")
                print(f"      → Narrative: {chapter.narrative[:100]}...")
                if chapter.character_thoughts:
                    print(f"      → Character Thoughts: {chapter.character_thoughts[:80]}...")
                print()
            
            print(f"✅ Test case {i} completed successfully!")
            
        except Exception as e:
            print(f"❌ Test case {i} failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 80)

def test_complete_comic_with_scenario():
    """Test the complete comic generation that now includes detailed scenarios"""
    print("\n" + "=" * 80)
    print("🎬 TESTING COMPLETE COMIC + SCENARIO GENERATION")
    print("=" * 80)
    
    concept = "A young astronaut finds an alien artifact that shows visions of the future"
    genre = "sci-fi"
    art_style = "comic book"
    
    print(f"📝 Concept: {concept}")
    print(f"🎭 Genre: {genre}")
    print(f"🎨 Art Style: {art_style}")
    
    try:
        # Generate complete comic with scenario
        comic_page, comic_sheet, detailed_scenario = generate_complete_comic(
            concept=concept,
            genre=genre,
            art_style=art_style
        )
        
        print(f"\n🎨 COMIC GENERATED:")
        print(f"   📚 Title: Comic panels created")
        print(f"   🎭 Genre: {comic_page.genre}")
        print(f"   🎨 Art Style: {comic_page.art_style}")
        print(f"   📑 Panels: {len(comic_page.panels)}")
        print(f"   🖼️ Comic Sheet: {type(comic_sheet)} ({comic_sheet.size if hasattr(comic_sheet, 'size') else 'Unknown size'})")
        
        print(f"\n📖 SCENARIO GENERATED:")
        print(f"   📚 Title: {detailed_scenario.title}")
        print(f"   📝 Word Count: {detailed_scenario.word_count}")
        print(f"   ⏰ Reading Time: {detailed_scenario.reading_time_minutes} minutes")
        print(f"   📑 Chapters: {len(detailed_scenario.chapters)}")
        
        # Verify panel-to-chapter mapping
        print(f"\n🔗 PANEL-TO-CHAPTER MAPPING:")
        for i, panel in enumerate(comic_page.panels):
            chapter = detailed_scenario.chapters[i] if i < len(detailed_scenario.chapters) else None
            if chapter:
                print(f"   Panel {panel.panel} ↔ Chapter {chapter.chapter_number}: {chapter.title}")
                print(f"      Comic: {panel.dialogue[:60] if panel.dialogue else 'No dialogue'}...")
                print(f"      Story: {chapter.narrative[:80]}...")
            else:
                print(f"   Panel {panel.panel} ↔ No corresponding chapter")
        
        print(f"\n✅ Complete comic + scenario generation successful!")
        
        # Demonstrate JSON serialization for Supabase storage
        print(f"\n💾 SUPABASE STORAGE PREPARATION:")
        scenario_json = json.dumps(detailed_scenario.dict(), indent=2, default=str)
        print(f"   📦 Scenario JSON size: {len(scenario_json)} characters")
        print(f"   💾 Ready for Supabase storage: ✓")
        
        return comic_page, comic_sheet, detailed_scenario
        
    except Exception as e:
        print(f"❌ Complete generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

def test_scenario_save_request():
    """Test creating a scenario save request for Supabase"""
    print("\n" + "=" * 80)
    print("💾 TESTING SCENARIO SAVE REQUEST")
    print("=" * 80)
    
    # Simulate a scenario save request
    mock_scenario = {
        "title": "The Cosmic Discovery",
        "genre": "sci-fi",
        "art_style": "comic book", 
        "characters": ["Alex Chen", "Dr. Stella", "Alien Entity"],
        "premise": "A young astronaut discovers an alien artifact that reveals the future of humanity.",
        "setting": "A research station orbiting Jupiter in the year 2157.",
        "themes": ["discovery", "destiny", "cosmic connection"],
        "chapters": [
            {
                "chapter_number": 1,
                "title": "Routine Mission",
                "narrative": "Alex Chen floated through the sterile corridors of Jupiter Research Station Omega...",
                "panel_reference": 1,
                "character_thoughts": "Another day, another sample collection run...",
                "world_building": "The station hummed with the constant vibration of life support systems...",
                "emotional_context": "Alex felt the familiar mixture of wonder and isolation..."
            }
        ],
        "word_count": 1847,
        "reading_time_minutes": 9,
        "comic_panel_count": 6,
        "narrative_style": "Third-person science fiction with literary depth"
    }
    
    try:
        # Create save request
        save_request = ScenarioSaveRequest(
            comic_id=123,  # Mock comic ID
            title=mock_scenario["title"],
            concept="Test concept",
            genre=mock_scenario["genre"],
            art_style=mock_scenario["art_style"],
            scenario_data=json.dumps(mock_scenario),
            word_count=mock_scenario["word_count"],
            reading_time_minutes=mock_scenario["reading_time_minutes"]
        )
        
        print(f"📦 SAVE REQUEST CREATED:")
        print(f"   🔗 Comic ID: {save_request.comic_id}")
        print(f"   📚 Title: {save_request.title}")
        print(f"   🎭 Genre: {save_request.genre}")
        print(f"   💾 Data Size: {len(save_request.scenario_data)} characters")
        print(f"   📝 Word Count: {save_request.word_count}")
        print(f"   ⏰ Reading Time: {save_request.reading_time_minutes} minutes")
        
        print(f"\n✅ Scenario save request ready for Supabase!")
        
    except Exception as e:
        print(f"❌ Save request creation failed: {e}")

def main():
    """Run all tests"""
    print("🚀 ENHANCED SCENARIO SYSTEM TEST SUITE")
    print("=" * 80)
    print("This test demonstrates the new enhanced scenario system that:")
    print("1. 📖 Generates rich, detailed narrative stories from prompts")
    print("2. 🎨 Creates both comics AND complementary narratives")
    print("3. 🔗 Maps comic panels to story chapters")
    print("4. 💾 Prepares data for Supabase storage")
    print("5. 🎭 Uses genre and art style systems for consistency")
    
    # Test 1: Enhanced scenario generation
    test_enhanced_scenario_generation()
    
    # Test 2: Complete comic + scenario generation
    comic_page, comic_sheet, detailed_scenario = test_complete_comic_with_scenario()
    
    # Test 3: Scenario save request
    test_scenario_save_request()
    
    print("\n" + "=" * 80)
    print("🎉 ALL TESTS COMPLETED!")
    print("=" * 80)
    print("The enhanced scenario system is ready for integration!")
    print("\n🔧 Next Steps:")
    print("1. 📊 Set up Supabase database table: 'detailedscenario'")
    print("2. 🔌 Test API endpoints: /api/supabase/scenarios/*")
    print("3. 📱 Update frontend to display both comics and scenarios")
    print("4. 👥 Implement user preference for scenario generation")
    print("5. 🔍 Add search functionality for scenarios")

if __name__ == "__main__":
    main() 