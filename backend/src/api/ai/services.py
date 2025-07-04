import os, math, requests, base64
from PIL import Image
from io import BytesIO
from api.ai.llms import get_openai_llm
from api.ai.schemas import (
    ScenarioSchema, ComicPanelsResponseSchema,
    ComicPanelsWithImagesResponseSchema, ComicPanelWithImageSchema, ComicsPageSchema,
    ScenarioSchema2, Dialogue, DetailedScenarioSchema, DetailedScenarioChapter
)

from api.utils.image_utils import create_comic_sheet, add_dialogues_and_sfx_to_panel, extract_character_details
from dotenv import load_dotenv

load_dotenv()
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

# 🎨 Genre → Mood → Palette System
GENRE_MAPPINGS = {
    "horror": {
        "mood": "tense, eerie, dark, foreboding",
        "palette": "desaturated colors, cold tones, deep shadows, muted reds and blacks",
        "lighting": "dramatic shadows, harsh contrasts, moonlight, flickering light",
        "font_style": "cracked serif, gothic",
        "atmosphere": "sinister, unsettling, mysterious",
        "visual_cues": "gothic architecture, shadowed figures, unsettling textures, decayed environments"
    },
    "romance": {
        "mood": "tender, dreamy, warm, intimate",
        "palette": "pastels, warm lighting, soft pinks and golds, gentle hues",
        "lighting": "soft golden hour, warm ambient light, gentle shadows",
        "font_style": "cursive handwritten, elegant",
        "atmosphere": "romantic, cozy, heartwarming",
        "visual_cues": "cozy interiors, blooming flowers, soft focus, gentle expressions"
    },
    "sci-fi": {
        "mood": "futuristic, technological, vast, wonder",
        "palette": "neon blues and cyans, metallic silvers, electric purples",
        "lighting": "artificial lighting, glowing screens, laser effects, starlight",
        "font_style": "clean modern, digital",
        "atmosphere": "technological, expansive, alien",
        "visual_cues": "sleek spaceships, chrome surfaces, glowing circuitry, alien landscapes"
    },
    "fantasy": {
        "mood": "magical, mystical, adventurous, enchanting",
        "palette": "rich jewel tones, deep purples and golds, magical glows",
        "lighting": "magical glows, ethereal light, torch flames, crystal luminescence",
        "font_style": "ornate serif, mystical",
        "atmosphere": "enchanted, otherworldly, epic",
        "visual_cues": "ancient castles, magical creatures, enchanted forests, glowing runes"
    },
    "comedy": {
        "mood": "lighthearted, playful, energetic, cheerful",
        "palette": "bright vibrant colors, bold contrasts, cheerful yellows and oranges",
        "lighting": "bright even lighting, cheerful sunlight, colorful highlights",
        "font_style": "rounded bubble letters, playful",
        "atmosphere": "fun, energetic, upbeat",
        "visual_cues": "exaggerated expressions, dynamic poses, cartoon physics, simple backgrounds"
    },
    "action": {
        "mood": "intense, dynamic, powerful, explosive",
        "palette": "bold reds and oranges, high contrast, dramatic colors",
        "lighting": "dynamic lighting, explosion glows, dramatic spotlights",
        "font_style": "bold angular, impact",
        "atmosphere": "intense, fast-paced, dramatic",
        "visual_cues": "motion blur, impact lines, detailed explosions, epic scale"
    },
    "mystery": {
        "mood": "suspenseful, intriguing, noir, contemplative",
        "palette": "muted grays and blues, noir black and white, subtle colors",
        "lighting": "film noir lighting, venetian blind shadows, dim ambiance",
        "font_style": "classic serif, noir",
        "atmosphere": "mysterious, contemplative, noir",
        "visual_cues": "shadows and fog, detective office, city at night, rain-slicked streets"
    },
    "drama": {
        "mood": "emotional, realistic, character-focused, poignant",
        "palette": "realistic natural colors, subtle emotional tones, gray and blue tones",
        "lighting": "natural lighting, realistic shadows, mood-appropriate ambiance",
        "font_style": "clean readable, classical",
        "atmosphere": "realistic, emotional, human",
        "visual_cues": "natural settings, expressive faces, everyday objects, soft lighting"
    }
}

# 🎨 Art Style System
CONSISTENT_STYLES = {
    "cartoon": "Disney-style 2D animation, cartoon illustration, cel-shaded artwork, bold black outlines, vibrant flat colors, exaggerated expressions, simplified character designs, clean vector art style, animated movie aesthetic, family-friendly cartoon style",
    "comic book": "classic American comic book art, bold inks, primary colors, dynamic panels, superhero comic style, clear line art, comic book illustration",
    "manga": "Japanese manga style, clean linework, screentones, black and white with selective color, expressive anime-style characters, detailed backgrounds",
    "anime": "modern anime style, vibrant colors, large expressive eyes, detailed character designs, cel-shaded animation style, Japanese animation aesthetic",
    "realistic": "photorealistic digital painting, highly detailed, naturalistic lighting, realistic proportions, lifelike textures, cinematic realism",
    "watercolor": "watercolor painting style, soft brush strokes, flowing paint, artistic paper texture, delicate color blending, traditional art medium",
    "sketch": "pencil sketch style, hand-drawn lines, artistic shading, sketchy linework, black and white illustration, traditional drawing",
    "pixel art": "pixel art style, 8-bit aesthetic, retro game graphics, blocky sprites, limited color palette, digital pixel illustration",
    "minimalist": "minimalist art style, clean simple lines, geometric shapes, limited color palette, modern flat design, vector illustration",
    "vintage": "vintage illustration style, retro aesthetic, aged paper texture, classic advertising art, nostalgic color palette"
}

def generate_scenario(prompt: str, genre: str = None, art_style: str = None) -> DetailedScenarioSchema:
    """Generate a detailed narrative scenario that complements the comic panels.
    
    This creates a rich, literary story that users can read after viewing the comics
    to get deeper context, character development, and world-building details.
    """
    llm_base = get_openai_llm()
    llm = llm_base.with_structured_output(DetailedScenarioSchema)

    # Validate and normalize genre and art style
    validated_genre, validated_art_style = validate_genre_and_style(genre, art_style)
    
    # Get genre-specific guidance for rich storytelling
    genre_guide = GENRE_MAPPINGS.get(validated_genre.lower(), GENRE_MAPPINGS["action"])
    
    # Create comprehensive system prompt for detailed narrative generation
    system_prompt = f"""YOU ARE A MASTER STORYTELLER creating a detailed, immersive narrative that complements a 6-panel comic.

CONCEPT: {prompt}
GENRE: {validated_genre}
ART STYLE: {validated_art_style}

🎨 GENRE-SPECIFIC NARRATIVE GUIDANCE:
- MOOD & TONE: {genre_guide['mood']} - Every sentence should breathe this emotional atmosphere
- ATMOSPHERE: {genre_guide['atmosphere']} - The entire narrative world should feel {genre_guide['atmosphere']}
- THEMES: Explore deep {validated_genre} themes with literary sophistication
- EMOTIONAL DEPTH: {genre_guide['mood']} should permeate character psychology and world description

📚 NARRATIVE STRUCTURE REQUIREMENTS:

Your task is to create a LITERARY COMPANION to a 6-panel comic. This is NOT a comic script - it's a rich, flowing narrative story that readers experience AFTER viewing the comic panels.

STORY STRUCTURE (6 chapters corresponding to 6 comic panels):

Chapter 1 - "The Ordinary World" (Panel 1 Reference)
- Rich character introduction with psychological depth
- Detailed world-building and atmospheric description  
- Establish the protagonist's normal life, desires, and internal conflicts
- Literary description of setting with sensory details
- 200-300 words of flowing narrative prose

Chapter 2 - "The Call to Adventure" (Panel 2 Reference)  
- The inciting incident told with dramatic tension
- Character's emotional reaction and internal struggle
- Detailed description of the moment everything changes
- Rich dialogue and character voice development
- 250-350 words of immersive storytelling

Chapter 3 - "Crossing the Threshold" (Panel 3 Reference)
- The protagonist's decision and first major action
- Explore character motivation and psychology
- Detailed action sequences with emotional weight
- World-building expansion and new environment introduction
- 250-350 words of dynamic narrative

Chapter 4 - "The Ordeal" (Panel 4 Reference)
- The climactic confrontation with maximum emotional stakes
- Character's deepest fears and greatest strength revealed
- Rich sensory details and psychological tension
- Peak dramatic moment with literary sophistication  
- 300-400 words of intense, literary prose

Chapter 5 - "The Revelation" (Panel 5 Reference)
- Immediate aftermath and character realization
- Process the climax with emotional depth
- Character growth and transformation moment
- Begin resolution with literary reflection
- 250-350 words of contemplative narrative

Chapter 6 - "The Return" (Panel 6 Reference)
- Satisfying conclusion showing character change
- Tie themes together with literary elegance
- Show how the protagonist's world has changed
- Memorable ending that echoes the opening
- 200-300 words of reflective, conclusive prose

📝 LITERARY STYLE REQUIREMENTS:
- Write in third-person narrative with rich literary voice
- Use advanced vocabulary and sophisticated sentence structure
- Include sensory details, metaphors, and emotional subtext
- Create flowing, immersive prose that reads like a short story
- Each chapter should have internal monologue/character thoughts
- Include world-building details that expand beyond the comic panels
- Total target: 1,500-2,000 words of polished narrative prose

🎭 CHARACTER & WORLD DEVELOPMENT:
- Create complex, three-dimensional characters with clear motivations
- Develop rich backstories and psychological depth
- Build an immersive world with history, culture, and atmosphere
- Include character thoughts, emotions, and internal conflicts
- Show character relationships and dynamics
- Explore themes relevant to {validated_genre} genre

🌟 THEMATIC DEPTH:
Based on {validated_genre} genre, explore themes such as:
- Character growth and transformation
- Good vs. evil / moral complexity  
- Love, sacrifice, and relationships
- Power, responsibility, and consequences
- Identity, belonging, and purpose
- Hope, redemption, and second chances

The final narrative should be a compelling literary work that enhances and deepens the comic reading experience."""

    messages = [
        ("system", system_prompt),
        ("human", f"Create a detailed literary narrative for: {prompt}")
    ]

    result = llm.invoke(messages)
    
    # Calculate word count and reading time
    total_words = sum(len(chapter.narrative.split()) for chapter in result.chapters)
    # Add character thoughts and world building from chapters
    for chapter in result.chapters:
        if chapter.character_thoughts:
            total_words += len(chapter.character_thoughts.split())
        if chapter.world_building:
            total_words += len(chapter.world_building.split())
    
    result.word_count = total_words
    result.reading_time_minutes = max(1, total_words // 200)  # Average reading speed is 200 words per minute
    
    print(f"📖 DETAILED SCENARIO GENERATED:")
    print(f"   📚 Title: {result.title}")
    print(f"   🎭 Genre: {result.genre}")
    print(f"   🎨 Art Style: {result.art_style}")
    print(f"   📝 Word Count: {result.word_count}")
    print(f"   ⏰ Reading Time: {result.reading_time_minutes} minutes")
    print(f"   📑 Chapters: {len(result.chapters)}")
    print(f"   🎯 Characters: {', '.join(result.characters)}")
    
    return result

def generate_comic_scenario(prompt: str, genre: str = None, art_style: str = None) -> ScenarioSchema2:
    """Generate comic scenario with proper narrative pacing and structure."""
    llm_base = get_openai_llm()
    llm = llm_base.with_structured_output(ScenarioSchema2)

    # Get genre-specific guidance
    genre_lower = (genre or 'action').lower()
    art_style_lower = (art_style or 'comic book').lower()
    genre_guide = GENRE_MAPPINGS.get(genre_lower, GENRE_MAPPINGS["action"])
    art_style_guide = CONSISTENT_STYLES.get(art_style_lower, CONSISTENT_STYLES["comic book"])

    # ABSOLUTE requirement for exactly 6 panels with user's structure
    system_prompt = f"""YOU MUST CREATE EXACTLY 6 PANELS. NO MORE, NO LESS.

CONCEPT: {prompt}
GENRE: {genre or 'determine from the concept'}
ART STYLE: {art_style or 'determine from the genre'}

🎨 GENRE-SPECIFIC CREATIVE GUIDANCE:
- MOOD: {genre_guide['mood']} - Every dialogue and action must reflect this emotional tone
- ATMOSPHERE: {genre_guide['atmosphere']} - The entire story world should feel {genre_guide['atmosphere']}
- VISUAL STYLE: {art_style_guide}
- COLOR PALETTE: {genre_guide['palette']} - This influences the visual description of every scene
- LIGHTING: {genre_guide['lighting']} - Describe lighting that creates {genre_guide['mood']} mood
- VISUAL ELEMENTS: {genre_guide['visual_cues']} - Include these environmental and atmospheric details

The story MUST be written in the {genre_lower} genre with {genre_guide['mood']} tone throughout.

MANDATORY 6-PANEL STRUCTURE:

INTRODUCTION (Panels 1-2):
Panel 1: SETUP & CHARACTER INTRODUCTION
- Introduce main characters and setting in normal, peaceful environment
- Show characters in their typical daily routine
- Genre-appropriate atmosphere: {genre or 'adventure'} mood and tone
- Dialogue: Character greeting/introduction + world establishment
- Keep tone light and conversational

Panel 2: INCITING INCIDENT  
- Something unexpected happens that changes everything
- Show the moment that disrupts the normal world
- Characters react with surprise, confusion, or concern
- Dialogue: Character expressing surprise + questioning what's happening
- Dialogue should show personality and relationship dynamics

MAIN ACTION (Panels 3-5):
Panel 3: RISING ACTION - FIRST CHALLENGE
- Characters actively engage with the conflict/problem
- Show them taking action or making important decisions
- Build tension through character choices and obstacles
- Dialogue: Character determination + addressing the challenge directly
- Show character personality through how they handle pressure

Panel 4: CLIMAX - PEAK CONFLICT
- The most intense, dramatic moment of the entire story
- Highest emotional stakes and maximum tension
- Genre-specific peak action (comedy: biggest joke, drama: emotional peak, adventure: major confrontation)
- Dialogue: Intense emotions + crucial decision-making
- Characters reveal their true nature under pressure

Panel 5: FALLING ACTION - CONSEQUENCES
- Immediate results and aftermath of the climax
- Characters process what just happened
- Begin to understand the implications
- Dialogue: Reflection on events + emotional processing
- Show character growth or change from the experience

CONCLUSION (Panel 6):
Panel 6: RESOLUTION & ENDING
- Story conclusion with clear, satisfying outcome
- Show how characters have been changed by the experience
- Genre-appropriate ending (comedy: final joke/punchline, drama: emotional resolution, adventure: victory/discovery)
- Dialogue: Final reflection + memorable closing line that ties back to the opening
- Leave reader satisfied with character journey

CRITICAL DIALOGUE & CHARACTER REQUIREMENTS:
- Each character must have a CONSISTENT voice, personality, and speaking style throughout all 6 panels
- Character names must be consistent across all panels
- Dialogue must reflect each character's unique personality traits
- Genre "{genre or 'adventure'}" MUST heavily influence: dialogue tone, character reactions, emotional depth
- Art style "{art_style or 'cartoon'}" MUST be identical across all panels - same color palette, lighting, character design
- Panel progression must show clear character development from introduction to conclusion

STRUCTURAL REQUIREMENTS:
- Your response MUST contain exactly 6 frames in the frames array
- Each panel needs exactly 2 dialogues that advance the narrative
- Dialogue should flow naturally between panels showing character relationship evolution
- Characters must react authentically to events based on their established personalities"""

    messages = [
        ("system", system_prompt),
        ("human", prompt)
    ]

    result = llm.invoke(messages)
    
    # CRITICAL DEBUG: Check how many panels were actually generated
    panel_count = len(result.frames) if result.frames else 0
    print(f"🎬 SCENARIO DEBUG: Generated {panel_count} frames (REQUIRED: 6)")
    if panel_count != 6:
        print(f"❌ ERROR: Only {panel_count} panels generated instead of 6!")
        print(f"📝 Generated panels: {[f'Panel {i+1}: {frame.description[:50]}...' for i, frame in enumerate(result.frames)]}")
    else:
        print(f"✅ SUCCESS: Exactly 6 panels generated as required")
    
    print(f"✅ Comic: {result.title}")
    print(f"📖 Narrative structure: Setup (1-2) → Action (3-5) → Resolution (6)")
    return result

def generate_image_from_prompt(prompt: str, character_lora: str = None, lora_strength: float = 0.8, style_variant: str = None, width: int = 1024, height: int = 1024, negative_prompt: str = None, seed: int = None) -> Image.Image:
    """Generate image using Stability AI Stable Diffusion with LoRA support for character consistency and specific dimensions"""
    try:
        print(f"🖼️ Generating {width}x{height} image with Stable Diffusion: {prompt[:100]}...")
        if character_lora:
            print(f"🎭 Using character LoRA: {character_lora} (strength: {lora_strength})")
        if style_variant:
            print(f"🎨 Using style variant: {style_variant}")

        # Check if STABILITY_API_KEY is available
        if not STABILITY_API_KEY:
            print("❌ STABILITY_API_KEY not found in environment variables")
            raise Exception("STABILITY_API_KEY not configured")

        # Prepare headers and payload for Stability AI v1 (SDXL)
        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Use custom negative prompt if provided, otherwise use minimal default
        if negative_prompt is None:
            strong_negative_prompt = "text, blurry"
        else:
            strong_negative_prompt = negative_prompt

        # SDXL v1 payload format
        payload = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                },
                {
                    "text": strong_negative_prompt,
                    "weight": -1
                }
            ],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 20  # Lower steps = cheaper
        }
        
        # Add seed for consistency if provided
        if seed is not None:
            payload["seed"] = seed
            print(f"🎯 Using seed for consistency: {seed}")

        # Make request to Stability AI v1 SDXL
        response = requests.post(STABILITY_API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"❌ Stability AI request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"Stability AI request failed: {response.status_code}")

        # The v1 API returns JSON with base64 image data
        data = response.json()
        if 'artifacts' not in data or len(data['artifacts']) == 0:
            raise Exception("No image generated in response")
        
        # Decode base64 image
        image_base64 = data['artifacts'][0]['base64']
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_bytes))
        
        print(f"✅ Image generated successfully: {image.size}")
        return image
        
    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        # Return a placeholder image with frame-specific dimensions
        placeholder = Image.new('RGB', (width, height), color='lightgray')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(placeholder)
        try:
            font = ImageFont.load_default()
            center_x, center_y = width // 2, height // 2
            draw.text((center_x, center_y), f"Image Generation Failed\n{str(e)[:100]}", fill='black', font=font, anchor="mm")
        except:
            pass
        return placeholder

def generate_character_reference(character_name: str, character_description: str, art_style: str = "comic book") -> str:
    """Enhanced character reference using detailed character description for consistency."""
    # Use the extracted character details instead of ignoring them
    return f"{character_description}, {art_style} style, consistent character design throughout comic"

def get_dynamic_style_variant(art_style: str, genre: str, panel_number: int, total_panels: int) -> str:
    """Generate comprehensive style guidance based on genre mood system and art style"""
    
    # Get genre-specific style elements
    genre_lower = genre.lower() if genre else "action"
    art_style_lower = art_style.lower() if art_style else "comic book"
    
    # Get genre mappings
    genre_style = GENRE_MAPPINGS.get(genre_lower, GENRE_MAPPINGS["action"])
    art_style_desc = CONSISTENT_STYLES.get(art_style_lower, CONSISTENT_STYLES["comic book"])
    
    # Build comprehensive style prompt based on panel position in narrative
    style_elements = []
    
    # Core art style foundation
    style_elements.append(art_style_desc)
    
    # Genre-specific mood and atmosphere
    style_elements.append(f"with {genre_style['mood']} mood")
    style_elements.append(f"{genre_style['atmosphere']} atmosphere")
    
    # Genre-specific color palette
    style_elements.append(f"color palette: {genre_style['palette']}")
    
    # Genre-specific lighting
    style_elements.append(f"lighting: {genre_style['lighting']}")
    
    # Genre-specific visual cues
    style_elements.append(f"visual elements: {genre_style['visual_cues']}")
    
    # Panel-specific mood enhancement based on narrative position
    if panel_number <= 2:
        # Introduction panels - establish mood
        style_elements.append("establishing tone, character introduction, world-building elements")
    elif panel_number <= 4:
        # Action/climax panels - intensify mood  
        style_elements.append("intensified dramatic tension, heightened emotional stakes")
    else:
        # Resolution panels - conclude mood
        style_elements.append("resolution mood, emotional conclusion, satisfying closure")
    
    # Combine all elements into a cohesive style description
    complete_style = ", ".join(style_elements)
    
    print(f"🎨 Panel {panel_number} Style: {art_style} + {genre} → {genre_style['mood']} mood")
    
    return complete_style

def map_to_allowed_sdxl_dimensions(width: int, height: int) -> tuple:
    """Map dimensions to allowed SDXL dimension pairs"""
    # Allowed SDXL dimension pairs
    allowed_dimensions = [
        (1024, 1024),  # Square
        (1152, 896),   # Landscape
        (1216, 832),   # Landscape  
        (1344, 768),   # Landscape
        (1536, 640),   # Wide landscape
        (640, 1536),   # Portrait
        (768, 1344),   # Portrait
        (832, 1216),   # Portrait
        (896, 1152),   # Portrait
    ]
    
    # Calculate aspect ratio of input
    input_ratio = width / height
    
    # Find the closest matching dimension pair based on aspect ratio and total area
    best_match = (1024, 1024)
    best_score = float('inf')
    
    for allowed_w, allowed_h in allowed_dimensions:
        allowed_ratio = allowed_w / allowed_h
        
        # Score based on aspect ratio difference and area difference
        ratio_diff = abs(input_ratio - allowed_ratio)
        area_diff = abs((width * height) - (allowed_w * allowed_h)) / (width * height)
        
        # Combined score (prioritize aspect ratio)
        score = ratio_diff * 2 + area_diff
        
        if score < best_score:
            best_score = score
            best_match = (allowed_w, allowed_h)
    
    print(f"📏 Mapped {width}x{height} (ratio: {input_ratio:.2f}) → {best_match[0]}x{best_match[1]} (ratio: {best_match[0]/best_match[1]:.2f})")
    return best_match

def get_frame_dimensions(panel_number: int, total_panels: int = 6) -> tuple:
    """Calculate frame dimensions for a specific panel in the comic layout"""
    
    if total_panels == 6:
        # NEW NARRATIVE-FOCUSED 6-panel layout with specific SDXL dimensions
        panel_dimensions = {
            1: (768, 1344),     # Strong vertical intro
            2: (1344, 768),     # Establishing shot or zoom
            3: (1536, 640),     # Reveal / climax
            4: (1152, 896),     # Aftermath
            5: (1216, 832),     # Emotion / character moment
            6: (1024, 1024),    # Closing beat
        }

                
        return panel_dimensions.get(panel_number, (1024, 1024))
    
    else:
        # Fallback for other panel counts - MAPPED TO ALLOWED SDXL DIMENSIONS
        cols = 2 if total_panels <= 4 else 3
        sheet_target_width = 2400
        gutter = 20
        outer_margin = 35
        calculated_panel_width = (sheet_target_width - (cols + 1) * gutter - 2 * outer_margin) // cols
        calculated_panel_height = int(calculated_panel_width * 0.75)  # 4:3 aspect ratio
        
        return map_to_allowed_sdxl_dimensions(calculated_panel_width, calculated_panel_height)

def generate_complete_comic(concept: str, genre: str = None, art_style: str = None, include_detailed_scenario: bool = False) -> tuple:
    """Generate a complete comic from concept to final page with comprehensive genre and style system.
    
    Returns (comic_page, comic_sheet, detailed_scenario) - detailed_scenario is None if not requested.
    """
    
    # Validate and normalize genre and art style
    validated_genre, validated_art_style = validate_genre_and_style(genre, art_style)
    
    # SHOW USER REQUIREMENTS CLEARLY
    print("🎯 COMIC GENERATION REQUEST:")
    print(f"   📝 Concept: {concept}")
    print(f"   🎭 Genre: {validated_genre} {'(validated)' if genre != validated_genre else ''}")
    print(f"   🎨 Art Style: {validated_art_style} {'(validated)' if art_style != validated_art_style else ''}")
    
    # Show genre and style combination details
    combo_info = get_genre_art_style_combination(validated_genre, validated_art_style)
    print(f"   🎨 Style Combination: {combo_info['genre_details']['mood']} mood with {combo_info['art_style']} style")
    print(f"   🌈 Color Palette: {combo_info['genre_details']['palette']}")
    print(f"   💡 Lighting: {combo_info['genre_details']['lighting']}")
    print("   🔒 THESE REQUIREMENTS WILL BE STRICTLY ENFORCED")
    
    # Step 1: Generate frame-size-aware story scenario with validated preferences
    print("🎬 Generating FRAME-SIZE-AWARE 6-panel story scenario...")
    scenario = generate_comic_scenario(concept, validated_genre, validated_art_style)
    
    # VERIFY COMPLIANCE WITH USER REQUIREMENTS
    print("✅ SCENARIO VERIFICATION:")
    print(f"   🎭 Generated Genre: {scenario.genre} {'✓ MATCHES USER' if genre and scenario.genre.lower() == genre.lower() else '⚠ AUTO-DETECTED' if not genre else '❌ MISMATCH!'}")
    print(f"   🎨 Generated Art Style: {scenario.art_style} {'✓ MATCHES USER' if art_style and scenario.art_style.lower() == art_style.lower() else '⚠ AUTO-DETECTED' if not art_style else '❌ MISMATCH!'}")
    
    # Step 2: Create character LoRA reference for consistency
    print("🎭 Creating character LoRA reference...")
    
    character_lora_reference = None
    main_character_name = None
    
    if scenario.characters and len(scenario.characters) > 0:
        main_character_name = scenario.characters[0]
        
        # Extract character description from the first frame
        # Use description of the character from the first frame for initial LoRA training context
        first_frame_desc = scenario.frames[0].description if scenario.frames else ""
        
        # Create detailed character description for LoRA
        character_details = extract_character_details(first_frame_desc, main_character_name)
        
        # Generate LoRA reference
        character_lora_reference = generate_character_reference(
            main_character_name, 
            character_details, 
            scenario.art_style or "comic book" # Use scenario's determined style
        )
        
        print(f"🎯 Character LoRA reference created for {main_character_name}")
        print(f"📝 Reference: {character_lora_reference[:100]}...")
    
    # Step 3: Generate images for each frame with LoRA consistency and dynamic styles
    print("🎨 Generating comic panels with dynamic styles and character consistency...")
    panels_with_images = []
    
    # Use a consistent seed for the entire comic to aid overall visual coherence,
    # or consider per-character seeds if you have multiple distinct characters with LoRAs.
    # For now, a single seed for overall coherence is a good start.
    import random
    # Use the same seed for all panels to maximize visual consistency across frames
    global_image_seed = random.randint(1, 2**32 - 1)
    print(f"Seed for image generation (global): {global_image_seed}")
    
    for i, frame in enumerate(scenario.frames):
        panel_number = i + 1
        
        # Get dynamic style variant for this panel
        # Pass the actual art_style and genre determined by the LLM
        style_variant = get_dynamic_style_variant(
            art_style=scenario.art_style, # Use LLM's determined style
            genre=scenario.genre,     # Use LLM's determined genre
            panel_number=panel_number,
            total_panels=len(scenario.frames)
        )
        
        # --- OPTIMIZED Frame-Size-Aware Prompt Generation ---
        # Calculate frame-specific dimensions and aspect ratio
        frame_width, frame_height = get_frame_dimensions(panel_number, len(scenario.frames))
        aspect_ratio = frame_width / frame_height
        
        # Advanced aspect ratio and composition analysis
        def get_composition_guidance(width, height, panel_num):
            ratio = width / height
            
            # Detailed composition guidance based on aspect ratio
            if ratio >= 2.0:  # Ultra-wide (21:9, 16:9)
                return {
                    "format": "ultra-wide cinematic",
                    "composition": "panoramic vista, sweeping horizontal composition, cinematic letterbox format",
                    "framing": "wide establishing shot, expansive horizontal movement, epic scale",
                    "camera": "anamorphic lens, wide-angle cinematography, panoramic perspective",
                    "focus": "environmental storytelling, grand scale, horizontal visual flow",
                    "details": "rich background details, multiple depth layers, atmospheric perspective"
                }
            elif ratio >= 1.5:  # Wide landscape (3:2, 16:10)
                return {
                    "format": "wide landscape",
                    "composition": "rule of thirds horizontal, balanced wide frame, landscape orientation",
                    "framing": "medium-wide shot, comfortable horizontal space, natural wide view",
                    "camera": "standard wide lens, balanced perspective, horizontal emphasis",
                    "focus": "character and environment balance, narrative flow, spatial relationships",
                    "details": "detailed background, clear subject hierarchy, visual breathing room"
                }
            elif ratio >= 1.1:  # Slightly wide (5:4, 4:3)
                return {
                    "format": "standard format",
                    "composition": "centered balanced composition, traditional comic panel, stable framing",
                    "framing": "medium shot, balanced proportions, classic comic format",
                    "camera": "standard lens, neutral perspective, balanced viewpoint",
                    "focus": "character-centric, clear visual hierarchy, focused storytelling",
                    "details": "balanced detail distribution, clear focal points, readable composition"
                }
            elif ratio >= 0.8:  # Square to slightly tall (1:1, 4:5)
                return {
                    "format": "square portrait",
                    "composition": "centered vertical emphasis, portrait orientation, intimate framing",
                    "framing": "close-up to medium shot, vertical composition, focused view",
                    "camera": "portrait lens, tight framing, intimate perspective",
                    "focus": "character emotion, facial expressions, personal moments",
                    "details": "facial detail emphasis, emotional clarity, minimal background distraction"
                }
            else:  # Tall portrait (2:3, 9:16)
                return {
                    "format": "tall portrait",
                    "composition": "vertical column layout, portrait aspect, tall narrow frame",
                    "framing": "close-up shot, vertical emphasis, tight vertical composition",
                    "camera": "telephoto portrait, compressed perspective, vertical focus",
                    "focus": "character detail, emotional intensity, vertical visual flow",
                    "details": "high detail on subject, soft background, vertical leading lines"
                }
        
        # Get composition guidance for this frame
        comp_guide = get_composition_guidance(frame_width, frame_height, panel_number)
        
        # Removed complex guidance to save tokens
        
        # ENHANCED image prompt with COMPREHENSIVE genre and style system
        
        # Get genre-specific elements for this panel
        genre_lower = scenario.genre.lower() if scenario.genre else "action"
        genre_elements = GENRE_MAPPINGS.get(genre_lower, GENRE_MAPPINGS["action"])
        
        # Build character-specific consistency
        character_consistency = ""
        if scenario.characters and len(scenario.characters) > 0:
            char_names = ", ".join(scenario.characters[:2])  # Use first 2 character names
            character_consistency = f"featuring {char_names} with consistent character design"
        
        # Construct comprehensive image prompt using style variant
        image_prompt = f"{frame.description}, {style_variant}, {character_consistency}"
        
        # Add genre-specific atmospheric details
        image_prompt += f", {genre_elements['atmosphere']} mood, {genre_elements['lighting']}"
        
        # Add SFX to the visual description if present (for visual cues, not text)
        if frame.sfx:
            sfx_description_visual = ", ".join([f"visual representation of {sfx}" for sfx in frame.sfx])
            image_prompt += f", with visual emphasis on: {sfx_description_visual}"
        
        # Add character LoRA reference if available
        if character_lora_reference:
            image_prompt += f", {character_lora_reference}"
        
        # Add panel-specific consistency based on position in story
        if panel_number <= 2:
            image_prompt += ", establishing scene, introduction mood"
        elif panel_number <= 5:
            image_prompt += ", action scene, tension building"
        else:
            image_prompt += ", resolution scene, conclusion mood"
        
        # Clean up and format the prompt
        image_prompt = " ".join(image_prompt.split())
        
        # Enhanced genre-aware negative prompt for maximum consistency
        base_negative = "text, letters, words, inconsistent art style, mixed styles, different character design, poor quality, blurry, style variations"
        
        # Add genre-specific negative elements
        genre_negative = {
            "horror": "bright cheerful colors, cartoon style, overly bright lighting",
            "romance": "dark gothic elements, horror imagery, aggressive poses",
            "sci-fi": "medieval fantasy elements, primitive technology, natural only lighting",
            "fantasy": "modern technology, urban settings, realistic only styling",
            "comedy": "dark horror elements, serious dramatic poses, muted colors",
            "action": "static poses, peaceful settings, soft gentle lighting",
            "mystery": "bright cheerful colors, obvious solutions, cartoon comedy",
            "drama": "exaggerated cartoon features, unrealistic proportions"
        }
        
        genre_specific_negative = genre_negative.get(genre_lower, "")
        negative_prompt = f"{base_negative}, {genre_specific_negative}" if genre_specific_negative else base_negative
        
        print(f"Panel {panel_number}: {frame.description[:30]}...")
        
        # Generate image with enhanced prompting and frame-specific dimensions
        try:
            image = generate_image_from_prompt(
                prompt=image_prompt,
                character_lora=character_lora_reference,  # Pass character LoRA for consistency
                width=frame_width,
                height=frame_height,
                negative_prompt=negative_prompt,
                seed=global_image_seed  # Use consistent seed for all panels
            )
            print(f"  ✅ Panel {panel_number} generated successfully")
        except Exception as e:
            print(f"  ❌ Panel {panel_number} failed: {e}")
            # Create placeholder image for failed generations with frame-specific dimensions
            image = Image.new('RGB', (frame_width, frame_height), color='lightgray')
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(image)
            try:
                font = ImageFont.truetype("arial.ttf", max(20, min(frame_width, frame_height) // 30)) # Scale font to frame
                center_x, center_y = frame_width // 2, frame_height // 2
                draw.text((center_x, center_y), f"Panel {panel_number}\nGeneration Failed\n{str(e)[:100]}", 
                          fill='black', font=font, anchor="mm") # Anchor for centering
            except Exception as font_e:
                print(f"Font loading failed: {font_e}")
                center_x, center_y = frame_width // 2, frame_height // 2
                draw.text((center_x, center_y), f"Panel {panel_number}\nGeneration Failed", fill='black', anchor="mm")
        
        # Store image with dialogue info
        enhanced_dialogues = []
        for dialogue in frame.dialogues:
            enhanced_dialogue = Dialogue(
                speaker=dialogue.speaker,
                text=dialogue.text,
                type=dialogue.type,
                emotion=dialogue.emotion,
                position=dialogue.position
            )
            enhanced_dialogues.append(enhanced_dialogue)
        
        # Add SFX as special dialogue entries for post-processing if needed
        # (Already included in image_prompt for visual, but can be separate for text overlay)
        # for sfx in frame.sfx:
        #     sfx_dialogue = Dialogue(
        #         speaker="",
        #         text=sfx,
        #         type="sound_effect",
        #         emotion="normal",
        #         position="center" # Placeholder position
        #     )
        #     enhanced_dialogues.append(sfx_dialogue)
        
        panels_with_images.append((image, enhanced_dialogues))
    
    # Step 4: Create comic sheet with enhanced layout and smart positioning
    print("📄 Assembling final comic pages with smart text positioning...")
    try:
        # Pass character information for smart positioning and frame-specific bubble sizing
        comic_sheet, final_panel_locations = create_comic_sheet(
            panels_with_images, 
            character_names=scenario.characters  # Pass character list for smart positioning
        )
        print("✅ Comic sheet assembled successfully with smart positioning")
    except Exception as e:
        print(f"❌ Comic sheet assembly failed: {e}")
        # Create a simple layout as fallback
        comic_sheet = create_simple_comic_grid([img for img, _ in panels_with_images])
        final_panel_locations = [] # Clear locations if fallback is used

    # Create final response with enhanced panel data
    comic_page_panels = []
    for i, frame in enumerate(scenario.frames):
        panel_location_data = next((loc for loc in final_panel_locations if loc["panel"] == i + 1), {})
        comic_page_panels.append(
            ComicPanelWithImageSchema(
                panel=i+1,
                image_prompt=f"Panel {i+1} ({frame.camera_shot}): {frame.description[:50]}...",
                image_url="", # This would be populated after image upload
                dialogue="; ".join([f"{d.speaker}: {d.text}" if d.speaker else d.text for d in frame.dialogues]) if frame.dialogues else None,
                x_coord=panel_location_data.get("x", 0),
                y_coord=panel_location_data.get("y", 0),
                panel_width=panel_location_data.get("width", 1024), # Default to generated image size
                panel_height=panel_location_data.get("height", 1024)
            )
        )

    comic_page = ComicsPageSchema(
        genre=scenario.genre,
        art_style=scenario.art_style,
        panels=comic_page_panels,
        invalid_request=False
    )

    # Step 5: Generate detailed narrative scenario (OPTIONAL)
    detailed_scenario = None
    if include_detailed_scenario:
        print("📖 Generating detailed narrative scenario to complement the comic...")
        try:
            # Generate scenario based on the actual comic content, not just the original concept
            comic_content = f"Comic Title: {scenario.title}\n"
            comic_content += f"Genre: {scenario.genre}, Art Style: {scenario.art_style}\n"
            comic_content += f"Characters: {', '.join(scenario.characters) if scenario.characters else 'Unknown'}\n\n"
            
            # Include the actual comic panel descriptions for richer narrative
            for i, frame in enumerate(scenario.frames):
                comic_content += f"Panel {i+1}: {frame.description}\n"
                if frame.dialogues:
                    for dialogue in frame.dialogues:
                        speaker_text = f"{dialogue.speaker}: " if dialogue.speaker else ""
                        comic_content += f"  - {speaker_text}{dialogue.text}\n"
            
            detailed_scenario = generate_scenario(
                prompt=f"Based on this generated comic:\n\n{comic_content}\n\nOriginal concept: {concept}",
                genre=validated_genre, 
                art_style=validated_art_style
            )
            print("✅ Detailed narrative scenario generated successfully")
            print(f"   📚 Scenario: {detailed_scenario.title}")
            print(f"   📝 Word Count: {detailed_scenario.word_count}")
            print(f"   ⏰ Reading Time: {detailed_scenario.reading_time_minutes} minutes")
        except Exception as e:
            print(f"❌ Detailed scenario generation failed: {e}")
            # Create a minimal fallback scenario
            from api.ai.schemas import DetailedScenarioChapter
            detailed_scenario = DetailedScenarioSchema(
                title=scenario.title or "Untitled Story",
                genre=validated_genre,
                art_style=validated_art_style,
                characters=scenario.characters or ["Unknown"],
                premise=f"A {validated_genre} story: {concept}",
                setting="Unknown setting",
                themes=[validated_genre],
                chapters=[
                    DetailedScenarioChapter(
                        chapter_number=i+1,
                        title=f"Chapter {i+1}",
                        narrative=f"This chapter corresponds to panel {i+1} of the comic.",
                        panel_reference=i+1,
                        character_thoughts="Character thoughts unavailable.",
                        world_building="World details unavailable.",
                        emotional_context="Emotional context unavailable."
                    ) for i in range(len(scenario.frames))
                ],
                narrative_style=f"{validated_genre} narrative",
                word_count=50,
                reading_time_minutes=1
            )
    else:
        print("⏭️ Skipping detailed narrative scenario generation (not requested)")

    return comic_page, comic_sheet, detailed_scenario

def generate_detailed_scenario_from_comic(comic_scenario: ScenarioSchema2, original_concept: str, genre: str = None, art_style: str = None) -> DetailedScenarioSchema:
    """Generate a detailed narrative scenario based on an already generated comic.
    
    This allows users to request a rich narrative story after viewing their comic,
    based on the actual comic content rather than just the original concept.
    """
    
    # Validate and normalize genre and art style
    validated_genre, validated_art_style = validate_genre_and_style(genre, art_style)
    
    print("📖 Generating detailed narrative scenario based on existing comic...")
    
    try:
        # Build detailed comic content description
        comic_content = f"Comic Title: {comic_scenario.title}\n"
        comic_content += f"Genre: {comic_scenario.genre}, Art Style: {comic_scenario.art_style}\n"
        comic_content += f"Characters: {', '.join(comic_scenario.characters) if comic_scenario.characters else 'Unknown'}\n\n"
        
        # Include the actual comic panel descriptions and dialogues
        for i, frame in enumerate(comic_scenario.frames):
            comic_content += f"Panel {i+1}: {frame.description}\n"
            if frame.dialogues:
                for dialogue in frame.dialogues:
                    speaker_text = f"{dialogue.speaker}: " if dialogue.speaker else ""
                    comic_content += f"  - {speaker_text}{dialogue.text}\n"
            if frame.sfx:
                comic_content += f"  - Sound effects: {', '.join(frame.sfx)}\n"
            comic_content += "\n"
        
        # Generate rich narrative based on the actual comic
        detailed_scenario = generate_scenario(
            prompt=f"Based on this complete comic story:\n\n{comic_content}\n\nOriginal concept: {original_concept}\n\nCreate a rich literary narrative that expands on this comic story.",
            genre=validated_genre, 
            art_style=validated_art_style
        )
        
        print("✅ Detailed narrative scenario generated from comic successfully")
        print(f"   📚 Scenario: {detailed_scenario.title}")
        print(f"   📝 Word Count: {detailed_scenario.word_count}")
        print(f"   ⏰ Reading Time: {detailed_scenario.reading_time_minutes} minutes")
        
        return detailed_scenario
        
    except Exception as e:
        print(f"❌ Detailed scenario generation from comic failed: {e}")
        # Create a minimal fallback scenario
        from api.ai.schemas import DetailedScenarioChapter
        fallback_scenario = DetailedScenarioSchema(
            title=comic_scenario.title or "Untitled Story",
            genre=validated_genre,
            art_style=validated_art_style,
            characters=comic_scenario.characters or ["Unknown"],
            premise=f"A {validated_genre} story based on generated comic: {original_concept}",
            setting="Setting based on comic panels",
            themes=[validated_genre],
            chapters=[
                DetailedScenarioChapter(
                    chapter_number=i+1,
                    title=f"Chapter {i+1}",
                    narrative=f"This chapter expands on panel {i+1}: {frame.description[:100]}...",
                    panel_reference=i+1,
                    character_thoughts="Character thoughts based on comic dialogue.",
                    world_building="World details derived from comic visuals.",
                    emotional_context="Emotional context from comic narrative."
                ) for i, frame in enumerate(comic_scenario.frames)
            ],
            narrative_style=f"{validated_genre} narrative based on comic",
            word_count=100,
            reading_time_minutes=1
        )
        return fallback_scenario
    
def create_simple_comic_grid(images):
    """Create a simple comic grid layout as fallback when comic sheet creation fails"""
    try:
        num_images = len(images)
        
        if num_images == 5:
            # Special 5-panel layout: 2 on top, 3 on bottom
            panel_size = (350, 280)
            grid_width = panel_size[0] * 3 + 40  # 3 panels wide with spacing
            grid_height = panel_size[1] * 2 + 30  # 2 panels high with spacing
            comic_grid = Image.new('RGB', (grid_width, grid_height), 'white')
            
            # Top row: 2 panels centered
            positions = [
                (panel_size[0] // 2 + 10, 10),  # Top left (centered)
                (panel_size[0] * 1.5 + 30, 10),  # Top right (centered)
                (10, panel_size[1] + 20),  # Bottom left
                (panel_size[0] + 20, panel_size[1] + 20),  # Bottom center
                (panel_size[0] * 2 + 30, panel_size[1] + 20)   # Bottom right
            ]
        elif num_images == 6:
            # 3x2 grid
            panel_size = (300, 250)
            grid_width = panel_size[0] * 3 + 40
            grid_height = panel_size[1] * 2 + 30
            comic_grid = Image.new('RGB', (grid_width, grid_height), 'white')
            
            positions = []
            for i in range(6):
                col = i % 3
                row = i // 3
                x = col * (panel_size[0] + 10) + 10
                y = row * (panel_size[1] + 10) + 10
                positions.append((x, y))
        else:
            # Default grid for other numbers (including 4 panels)
            panel_size = (400, 300)
            cols = 2 if num_images <= 4 else 3
            rows = (num_images + cols - 1) // cols
            
            grid_width = panel_size[0] * cols + (cols + 1) * 10
            grid_height = panel_size[1] * rows + (rows + 1) * 10
            comic_grid = Image.new('RGB', (grid_width, grid_height), 'white')
            
            positions = []
            for i in range(num_images):
                col = i % cols
                row = i // cols
                x = col * (panel_size[0] + 10) + 10
                y = row * (panel_size[1] + 10) + 10
                positions.append((x, y))
        
        # Resize and place all images
        for i, img in enumerate(images[:len(positions)]):
            if i < len(positions):
                resized_img = img.resize(panel_size, Image.Resampling.LANCZOS)
                comic_grid.paste(resized_img, positions[i])
                
                # Add simple border
                from PIL import ImageDraw
                draw = ImageDraw.Draw(comic_grid)
                x, y = positions[i]
                border_coords = (x-2, y-2, x + panel_size[0] + 2, y + panel_size[1] + 2)
                draw.rectangle(border_coords, outline="black", width=3)
        
        return comic_grid
        
    except Exception as e:
        print(f"❌ Simple grid creation failed: {e}")
        # Ultimate fallback - single color image with text
        fallback_image = Image.new('RGB', (800, 600), color='lightblue')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(fallback_image)
        try:
            font = ImageFont.load_default()
            draw.text((50, 250), f"Comic Generation Fallback\n{len(images)} panels created\nLayout creation failed", 
                     fill='black', font=font, align='center')
        except:
            pass
        return fallback_image

def get_available_genres() -> dict:
    """Get all available genres with their mood and style descriptions"""
    return {
        genre: {
            "mood": info["mood"],
            "atmosphere": info["atmosphere"],
            "palette": info["palette"],
            "lighting": info["lighting"],
            "visual_cues": info["visual_cues"],
            "font_style": info["font_style"]
        }
        for genre, info in GENRE_MAPPINGS.items()
    }

def get_available_art_styles() -> dict:
    """Get all available art styles with their descriptions"""
    return CONSISTENT_STYLES.copy()

def get_genre_art_style_combination(genre: str, art_style: str) -> dict:
    """Get the complete style combination for a specific genre and art style"""
    genre_lower = genre.lower() if genre else "action"
    art_style_lower = art_style.lower() if art_style else "comic book"
    
    genre_info = GENRE_MAPPINGS.get(genre_lower, GENRE_MAPPINGS["action"])
    art_style_info = CONSISTENT_STYLES.get(art_style_lower, CONSISTENT_STYLES["comic book"])
    
    return {
        "genre": genre_lower,
        "art_style": art_style_lower,
        "genre_details": genre_info,
        "art_style_description": art_style_info,
        "combined_description": f"{art_style_info}, {genre_info['mood']} mood, {genre_info['atmosphere']} atmosphere, {genre_info['palette']}, {genre_info['lighting']}"
    }

def validate_genre_and_style(genre: str = None, art_style: str = None) -> tuple:
    """Validate and normalize genre and art style inputs"""
    
    # Normalize genre
    if genre:
        genre_lower = genre.lower()
        if genre_lower not in GENRE_MAPPINGS:
            print(f"⚠️ Unknown genre '{genre}', using 'action' as fallback")
            genre = "action"
        else:
            genre = genre_lower
    else:
        genre = "action"
    
    # Normalize art style
    if art_style:
        art_style_lower = art_style.lower()
        if art_style_lower not in CONSISTENT_STYLES:
            print(f"⚠️ Unknown art style '{art_style}', using 'comic book' as fallback")
            art_style = "comic book"
        else:
            art_style = art_style_lower
    else:
        art_style = "comic book"
    
    return genre, art_style


