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
import asyncio
import aiohttp 
import random

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
        "adventure": {
        "mood": "exploratory, thrilling, discovery-driven, heroic",
        "palette": "earthy browns, greens, deep blues, vibrant golds",
        "lighting": "sun-drenched, dappled light through foliage, torchlight in caves, bright daylight for open scenes",
        "font_style": "rugged, classic adventure",
        "atmosphere": "vast, mysterious, wondrous, untamed",
        "visual_cues": "ancient ruins, hidden pathways, exotic creatures, maps and compasses, grand landscapes, treasure chests, iconic landmarks"
    },
        "slice-of-life": {
        "mood": "calm, heartwarming, reflective, charming, cozy",
        "palette": "soft pastels, warm muted tones, gentle natural colors",
        "lighting": "gentle ambient light, warm sunlight through windows, soft indoor lighting",
        "font_style": "friendly, rounded, casual",
        "atmosphere": "everyday, comfortable, intimate, relatable",
        "visual_cues": "cozy cafes, familiar homes, mundane objects with charm, subtle details of daily routine, changing seasons, relatable character interactions"
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
    "cartoon": "Vibrant, expressive cartoon illustration. Features bold, clean outlines, simplified forms, and bright, flat colors with minimal shading. Characters have exaggerated features and dynamic poses. The style should evoke a modern animated series or a stylized graphic novel, distinct from classic Disney or traditional cel animation. Focus on clear visual storytelling and energetic composition.",
    
    "comic book": "Classic American comic book art style. Characterized by strong, impactful linework, dynamic action poses, and a vibrant, high-contrast color palette often with distinct black inks. Panels are designed for dramatic effect, with clear visual hierarchy and a focus on impactful storytelling typical of superhero or adventure comics. Features clear muscle definition, detailed expressions, and a bold, iconic aesthetic.",
    
    "manga": "Authentic Japanese manga illustration style. Defined by precise, sharp linework, a predominant use of black and white tones with occasional selective spot colors (often muted). Characters feature large, expressive eyes, nuanced facial expressions, and dynamic motion effects. Backgrounds can range from highly detailed to abstract, utilizing screentones for shading and texture. Emphasizes character emotion and narrative flow.",
    
    "anime": "Modern Japanese anime visual style. Characterized by vibrant, often saturated colors, detailed character designs with large expressive eyes, and dynamic compositions. Shading is typically cel-shaded (flat blocks of color for shadows and highlights). The aesthetic is clean, polished, and suitable for action or emotional drama, resembling high-quality animated series or feature films.",
    
    "realistic": "Photorealistic digital painting style. Focuses on highly detailed rendering, accurate anatomy, naturalistic lighting with subtle shadows and highlights, and lifelike textures. Proportions are realistic, and the overall impression is one of cinematic realism or a finely detailed classical painting, executed digitally. High fidelity to real-world appearance.",
    
    "watercolor": "Evocative watercolor painting style. Features soft, translucent washes of color with visible brushstrokes and a delicate, often ethereal quality. Outlines are minimal or entirely absent, allowing colors to blend naturally. The paper texture may be subtle. The mood is often calm, artistic, and flowing, reminiscent of traditional art mediums.",
    
    "sketch": "Expressive pencil sketch or charcoal drawing style. Characterized by visible, energetic hand-drawn lines, cross-hatching or subtle smudged shading for depth. The artwork feels raw and immediate, showcasing the artist's hand. Typically black and white or sepia-toned, with a focus on form and texture over detailed color.",
    
    "pixel art": "Distinctive pixel art style. Employs a low-resolution aesthetic with clearly visible square pixels, reminiscent of classic 8-bit or 16-bit video game graphics. Features blocky, stylized sprites, a limited color palette, and often strong, simple outlines. Can include isometric or side-scrolling perspectives. The charm lies in its retro, digital blocky aesthetic.",
    
    "minimalist": "Clean and sleek minimalist art style. Characterized by simple, geometric shapes, a very limited and often muted color palette, and abundant use of negative space. Focuses on conveying essence with few elements, resulting in a modern, abstract, and often serene aesthetic. Emphasizes clarity, functionality, and simplicity over detail.",
    
    "vintage": "Nostalgic vintage illustration style. Evokes a retro aesthetic, often inspired by mid-20th century advertising or children's book illustrations. Features muted or sepia-toned color palettes, subtle grain or aged paper textures, and stylized figures. The linework can vary but generally aims for a charming, classic, and slightly distressed look.",

    "noir": "Gritty, high-contrast film noir style. Dominated by deep shadows, dramatic chiaroscuro lighting, and a predominantly monochrome (black, white, grays) or desaturated color palette with occasional splashes of bold color. Focuses on mystery, tension, and dramatic silhouettes, reflecting classic detective comics or films.",
    
    "storybook": "Whimsical and warm storybook illustration style. Features soft, inviting colors, gentle outlines (or painterly edges), and a focus on charming character designs. The style often has a slightly textured or painterly feel, suitable for children's literature, evoking a cozy and imaginative atmosphere.",
    
    "pop art": "Bold and graphic Pop Art style. Inspired by comic books and advertising, it uses strong outlines, bright, often unmixed colors, and sometimes incorporates halftone dot patterns or speech bubbles. Focuses on iconic imagery and everyday objects, with a flat, graphic, and energetic feel."
}

def generate_scenario(scenario_description: str, *, title: str = '', genre: str = '', art_style: str = '', characters: list = None, setting: str = '', themes: list = None, narrative_style: str = 'Immersive, Literary') -> DetailedScenarioSchema:
    """
    Generate a detailed, immersive literary narrative from comic context.
    Returns a story of at least 800 words using retry mechanism if needed.
    """
    llm = get_openai_llm()

    system_prompt = (
        "You are a master storyteller. Based on the following comic setting, write a detailed, emotionally rich, immersive story. "
        "Do not split into chapters. Do not return bullet points. Write in a flowing, third-person narrative of about 100  words. "
        "Include sensory description, inner thoughts, emotional arcs, and vivid world-building."
    )

    messages = [
        ("system", system_prompt),
        ("human", f"{scenario_description}")
    ]

    # Retry loop if word count too low
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        print(f"\n🌀 Attempt {attempt}: Generating scenario...")
        output = llm.invoke(messages)
        story = output.content.strip()
        word_count = len(story.split())
        print(f"📝 Word count: {word_count}")

        if word_count >= 50:
            print("✅ Story meets word count requirement.")
            break
        else:
            print("⚠️ Story too short. Retrying...")

    # Calculate reading time before using it
    reading_time_minutes = max(1, word_count // 200)

    # Optional: Print a short preview of the result
    print("\n📖 Story Preview:")
    print(story[:30] + "..." if len(story) > 30 else story)

    return DetailedScenarioSchema(
        title=title or '',
        genre=genre or '',
        art_style=art_style or '',
        characters=characters or [],
        premise=story,
        setting=setting or '',
        themes=themes or [],
        chapters=[],
        narrative_style=narrative_style,
        word_count=word_count,
        reading_time_minutes=reading_time_minutes
    )



def generate_comic_scenario(prompt: str, genre: str = None, art_style: str = None) -> ScenarioSchema2:
    """Generate comic scenario with proper narrative pacing and structure."""
    llm_base = get_openai_llm()
    llm = llm_base.with_structured_output(ScenarioSchema2)

    # Get genre-specific guidance
    genre_lower = (genre or 'action').lower()
    art_style_lower = (art_style or 'comic book').lower()
    genre_guide = GENRE_MAPPINGS.get(genre_lower, GENRE_MAPPINGS["action"])
    art_style_guide = CONSISTENT_STYLES.get(art_style_lower, CONSISTENT_STYLES["manga"])

    # ABSOLUTE requirement for exactly 6 panels with user's structure
    system_prompt = f"""YOU MUST CREATE EXACTLY 6 PANELS. NO MORE, NO LESS.

CONCEPT: {prompt}
GENRE: {genre or 'determine from the concept'}
ART STYLE: {art_style or 'determine from the genre'}

CHARACTER DESIGN GUIDE (ABSOLUTELY ESSENTIAL FOR CONSISTENCY):
- Based on the 'CONCEPT', identify the main characters and provide a detailed visual description for EACH of them.
- For each character, include specific physical attributes (e.g., hair color, clothing, body type, unique features, accessories).
- Example format: "For [Character Name]: [Detailed visual description of character's appearance, ensuring consistency]."


IMPORTANT: These character designs MUST remain 100% consistent across all 6 panels. Their size, shape, color, costume details, and unique features must NOT change unless explicitly part of a transformation in the narrative.


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
- Introduce main characters  and setting in a normal, peaceful environment, perhaps a cozy, dream-like kitchen or a peaceful city backdrop.
- Show characters in their typical daily routine or relaxed state.
- Genre-appropriate atmosphere: {genre or 'adventure'} mood and tone.
- Dialogue: One line for character introduction/greeting, one line establishing the world or their routine. Keep tone light and conversational.
- VISUAL FRAMING: Establish shot or wide shot to introduce the full setting and all main characters clearly. Clear view of characters in their environment.
- NARRATIVE PURPOSE: Establish the status quo and character dynamics BEFORE any conflict. Do NOT introduce the inciting incident here.
- VISUAL DETAILS: Ensure all characters are present, clearly rendered according to their design guide.

Panel 2: INCITING INCIDENT  
- Something unexpected happens that changes everything. This should be the 'cinnamon on the crust' incident.
- Show the moment that disrupts the normal world. Characters react with surprise, confusion, or concern.
- Dialogue: One line expressing surprise/reaction to the incident, one line questioning or acknowledging the disruption. Dialogue should show personality and relationship dynamics.
- VISUAL FRAMING: Medium shot or close-up on the inciting incident itself (e.g., an object being defiled), showing characters' immediate reactions clearly. Focus on the object or event causing the disruption and the characters' expressions.
- NARRATIVE PURPOSE: Introduce the core conflict. This panel MUST pivot the story. Do NOT resolve anything here.
- VISUAL DETAILS: Highlight the source of the problem, and ensure characters show appropriate surprise/disgust.

MAIN ACTION (Panels 3-5):
Panel 3: RISING ACTION - FIRST CHALLENGE
- Characters actively engage with the conflict/problem. Show them taking action or making important decisions.
- Build tension through character choices and obstacles.
- Dialogue: One line showing character determination or strategy, one line directly addressing the challenge. Show character personality through how they handle pressure.
- VISUAL FRAMING: Action shot or medium shot. Clearly depict the characters interacting with the challenge (e.g., confronting an antagonist or strategizing). Show their full bodies if engaged in physical action, but keep their faces visible.
- NARRATIVE PURPOSE: Show the characters attempting to overcome the conflict, encountering initial obstacles. Tension should build.
- VISUAL DETAILS: Characters should be in dynamic poses, reflecting their action or decision. Maintain consistent character designs.

Panel 4: CLIMAX - PEAK CONFLICT
- The most intense, dramatic moment of the entire story. Highest emotional stakes and maximum tension.
- Genre-specific peak action (e.g., a major confrontation or a powerful attack).
- Dialogue: One line expressing intense emotions or a crucial decision, one line related to the core conflict's peak. Characters reveal their true nature under pressure.
- VISUAL FRAMING: Close-up on the characters' faces to capture intense emotions, or a dynamic wide/medium shot highlighting the peak action. The focal point must be the most dramatic element. Show the impact of the climax.
- NARRATIVE PURPOSE: This is the single most intense moment. All previous tension culminates here. Do NOT begin the resolution in this panel.
- VISUAL DETAILS: Exaggerate expressions if appropriate for genre. Show environmental damage or dramatic effects caused by the climax.

Panel 5: FALLING ACTION - CONSEQUENCES
- Immediate results and aftermath of the climax. Characters process what just happened. Begin to understand the implications.
- Dialogue: One line reflecting on events, one line showing emotional processing or the immediate consequence. Show character growth or change from the experience.
- VISUAL FRAMING: Medium shot to show characters reacting to the aftermath. Can include elements of the destroyed or changed environment. Focus on their emotional state and the immediate results of the climax.
- NARRATIVE PURPOSE: Show the immediate fallout of the climax. Characters begin to understand the new reality. Do NOT fully resolve the story here.
- VISUAL DETAILS: Characters might be weary, bruised, or showing relief/shock. The environment should reflect the recent conflict.

CONCLUSION (Panel 6):
Panel 6: RESOLUTION & ENDING
- Story conclusion with clear, satisfying outcome. Show how characters have been changed by the experience.
- Genre-appropriate ending (e.g., comedic resolution with a final joke, emotional resolution, adventure victory).
- Dialogue: One line for final reflection, one memorable closing line that ties back to the opening or theme. Leave reader satisfied with character journey.
- VISUAL FRAMING: Wide shot or medium shot showing the characters in their new, resolved state or environment. A sense of peace or finality should be conveyed.
- NARRATIVE PURPOSE: Provide a clear, satisfying conclusion to the main plot and character arcs. This is the final state of the story.
- VISUAL DETAILS: Characters should appear content or changed, and the environment should reflect the resolution.

CRITICAL DIALOGUE & CHARACTER REQUIREMENTS:
- Each character must have a CONSISTENT voice, personality, and speaking style throughout all 6 panels.
- Character names must be consistent across all panels.
- Dialogue must reflect each character's unique personality traits.
- The "{genre_lower}" genre MUST profoundly influence: dialogue tone, character reactions, emotional depth, and narrative progression.
- The art style "{art_style_lower}" MUST be identical across ALL panels. This includes a consistent color palette, lighting, line work, shading, and the EXACT character designs specified in the 'CHARACTER DESIGN GUIDE' above. NO DEVIATION IN ART STYLE OR CHARACTER APPEARANCE IS PERMITTED.
- Panel progression must show clear character development from introduction to conclusion.

STRUCTURAL REQUIREMENTS (ABSOLUTELY CRITICAL):
- Your response MUST contain EXACTLY 6 frames in the frames array. Any deviation will result in failure.
- Each panel MUST have exactly 2 dialogue lines that are concise and directly advance the narrative. Do NOT add more or less dialogue.
- Dialogue should flow naturally between panels, clearly showing the evolution of character relationships and the plot.
- Characters must react authentically to events based on their established personalities and motivations.
- ENSURE that the narrative pacing perfectly matches the 6-panel breakdown: Panels 1-2 for Introduction, Panels 3-5 for Main Action, and Panel 6 for Conclusion.

ABSOLUTE MANDATES FOR SCENARIO GENERATION:
- ENSURE that the visual descriptions for each panel explicitly reference the established character designs to reinforce consistency.
- EVERY panel description must include details about the specific 'VISUAL STYLE', 'COLOR PALETTE', and 'LIGHTING' from the creative guidance to ensure stylistic uniformity.
- Avoid introducing new characters or significant changes to the environment unless explicitly part of the 6-panel structure.
- The panel descriptions should be rich enough to directly inform an image generation model, focusing on clear visual elements, character poses, and expressions.
- AVOID: Narrator boxes, internal thoughts (unless conveyed via facial expression/body language), or lengthy prose that doesn't translate directly into a comic panel's visual or dialogue. Focus on "show, don't tell" for the comic scenario.
"""

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
        # Print a more detailed summary of generated panels for debugging
        print(f"📝 Generated panels: {[f'Panel {frame.panel_number}: {frame.description[:50]}...' for frame in result.frames if hasattr(frame, 'description')]}")
    else:
        print(f"✅ SUCCESS: Exactly 6 panels generated as required")
    
    print(f"✅ Comic: {result.title}")
    print(f"📖 Narrative structure: Setup (1-2) → Action (3-5) → Resolution (6)")
    return result


async def generate_image_from_prompt(session: aiohttp.ClientSession, prompt: str, width: int, height: int, negative_prompt: str, seed: int) -> Image.Image:
# 4 spaces for the first level of indentation
    try:
        # 8 spaces for the second level of indentation
        print(f"🚀 Launching async image request for: {prompt[:50]}...")
        
        if not STABILITY_API_KEY:
            raise Exception("STABILITY_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        strong_negative_prompt = negative_prompt or "text, blurry"

        payload = {
            "text_prompts": [{"text": prompt, "weight": 1}, {"text": strong_negative_prompt, "weight": -1}],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 20,
            "seed": seed
        }

        # THIS IS YOUR ERROR LINE. IT MUST HAVE 8 SPACES IN FRONT OF IT.
        async with session.post(STABILITY_API_URL, headers=headers, json=payload, timeout=90) as response:
            # 12 spaces for the code inside this 'async with' block
            if response.status != 200:
                error_text = await response.text()
                print(f"❌ Stability AI async request failed with status {response.status}: {error_text}")
                raise Exception(f"Stability AI request failed: {response.status}")
            
            data = await response.json()
            if 'artifacts' not in data or len(data['artifacts']) == 0:
                raise Exception("No image generated in response")

            image_base64 = data['artifacts'][0]['base64']
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_bytes))
            
            print(f"✅ Async image received for: {prompt[:50]}...")
            return image
            
# 4 spaces for the 'except' block, aligning it with 'try'
    except Exception as e:
        # 8 spaces for the code inside the 'except' block
        print(f"❌ Async image generation failed for '{prompt[:50]}...': {e}")
        placeholder = Image.new('RGB', (width, height), color='lightgray')
        return placeholder
        
    except Exception as e:
        print(f"❌ Async image generation failed for '{prompt[:50]}...': {e}")
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
            3: (1344, 768),     # Reveal / climax (updated for better aspect ratio)
            4: (1344, 768),     # Aftermath (updated for better aspect ratio)
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

async def generate_complete_comic(concept: str, genre: str = None, art_style: str = None, include_detailed_scenario: bool = False) -> tuple:
    """
    Asynchronously generates a complete comic from concept to final page.
    """
    
    # --------------------------------------------------------------------------
    #                       INITIAL SETUP AND SCENARIO
    # This part of your code was correct and remains the same.
    # --------------------------------------------------------------------------
    
    # Validate and normalize genre and art style
    validated_genre, validated_art_style = validate_genre_and_style(genre, art_style)
    
    # SHOW USER REQUIREMENTS CLEARLY
    print("🎯 COMIC GENERATION REQUEST (ASYNC):")
    print(f"   📝 Concept: {concept}")
    print(f"   🎭 Genre: {validated_genre}")
    print(f"   🎨 Art Style: {validated_art_style}")
    
    combo_info = get_genre_art_style_combination(validated_genre, validated_art_style)
    print(f"   🎨 Style Combination: {combo_info['genre_details']['mood']} mood...")
    
    # Step 1: Generate story scenario
    print("🎬 Generating FRAME-SIZE-AWARE 6-panel story scenario...")
    scenario = generate_comic_scenario(concept, validated_genre, validated_art_style)
    
    print("✅ SCENARIO VERIFICATION:")
    print(f"   🎭 Generated Genre: {scenario.genre}")
    print(f"   🎨 Generated Art Style: {scenario.art_style}")
    
    # Step 2: Create character LoRA reference
    print("🎭 Creating character LoRA reference...")
    character_lora_reference = None
    if scenario.characters and len(scenario.characters) > 0:
        main_character_name = scenario.characters[0]
        first_frame_desc = scenario.frames[0].description if scenario.frames else ""
        character_details = extract_character_details(first_frame_desc, main_character_name)
        character_lora_reference = generate_character_reference(
            main_character_name, character_details, scenario.art_style or "comic book"
        )
        print(f"🎯 Character LoRA reference created for {main_character_name}")


    # --------------------------------------------------------------------------
    #            FIXED: STEP 3 - ASYNCHRONOUS IMAGE GENERATION
    # The following block is now correctly indented to be part of the function
    # and has the complete logic.
    # --------------------------------------------------------------------------
    
    print("🎨 Preparing all panel image generation tasks...")
    panels_with_images = []

    global_image_seed = random.randint(1, 2**32 - 1)
    print(f"Seed for image generation (global): {global_image_seed}")

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, frame in enumerate(scenario.frames):
            
            panel_number = i + 1
            
            style_variant = get_dynamic_style_variant(
                art_style=scenario.art_style,
                genre=scenario.genre,
                panel_number=panel_number,
                total_panels=len(scenario.frames)
            )
            
            frame_width, frame_height = get_frame_dimensions(panel_number, len(scenario.frames))
            
            character_consistency = ""
            if scenario.characters and len(scenario.characters) > 0:
                char_names = ", ".join(scenario.characters[:2])
                character_consistency = f"featuring {char_names} with consistent character design"

            # Use scenario's actual genre, defaulting to 'action' if somehow missing
            current_genre = scenario.genre.lower() if scenario.genre else "action"

            image_prompt = (
                f"{frame.description}, {style_variant}, {character_consistency}, "
                f"{GENRE_MAPPINGS[current_genre]['atmosphere']} mood, "
                f"{GENRE_MAPPINGS[current_genre]['lighting']}"
            )
            
            if frame.sfx:
                sfx_visual = ", ".join([f"visual representation of {sfx}" for sfx in frame.sfx])
                image_prompt += f", with visual emphasis on: {sfx_visual}"
                
            if character_lora_reference:
                image_prompt += f", {character_lora_reference}"
                
            if panel_number <= 2: image_prompt += ", establishing scene, introduction mood"
            elif panel_number <= 5: image_prompt += ", action scene, tension building"
            else: image_prompt += ", resolution scene, conclusion mood"
                
            image_prompt = " ".join(image_prompt.split())

            base_negative = "text, letters, words, inconsistent art style, mixed styles, different character design, poor quality, blurry, style variations"
            
            # FIXED: Completed the genre_negative_map dictionary
            genre_negative_map = {
                "horror": "bright cheerful colors, cartoon style, overly bright lighting",
                "romance": "dark gothic elements, horror imagery, aggressive poses",
                "sci-fi": "medieval fantasy elements, primitive technology, natural only lighting",
                "fantasy": "modern technology, urban settings, realistic only styling",
                "comedy": "dark horror elements, serious dramatic poses, muted colors",
                "action": "static poses, peaceful settings, soft gentle lighting",
                "mystery": "bright cheerful colors, obvious solutions, cartoon comedy",
                "drama": "exaggerated cartoon features, unrealistic proportions"
            }
            genre_specific_negative = genre_negative_map.get(current_genre, "")
            negative_prompt = f"{base_negative}, {genre_specific_negative}" if genre_specific_negative else base_negative
            
            print(f"  - Panel {panel_number}: Preparing task for '{frame.description[:30]}...'")
            
            task = asyncio.create_task(
                generate_image_from_prompt(
                    session=session,
                    prompt=image_prompt,
                    width=frame_width,
                    height=frame_height,
                    negative_prompt=negative_prompt,
                    seed=global_image_seed
                )
            )
            tasks.append(task)
            
        print("\n⏳ Concurrently executing all tasks. Waiting for completion...")
        generated_images = await asyncio.gather(*tasks)
        print("\n✅ All images have been successfully generated!")

    for i, image in enumerate(generated_images):
        frame = scenario.frames[i]
        enhanced_dialogues = [Dialogue(**d.dict()) for d in frame.dialogues]
        panels_with_images.append((image, enhanced_dialogues))

    # --------------------------------------------------------------------------
    #                FIXED: STEP 4 & 5 - ASSEMBLY AND FINAL OUTPUT
    # This block is also now correctly indented to be part of the function.
    # --------------------------------------------------------------------------

    print("📄 Assembling final comic pages...")
    try:
        comic_sheet, final_panel_locations = create_comic_sheet(
            panels_with_images, 
            character_names=scenario.characters
        )
        print("✅ Comic sheet assembled successfully.")
    except Exception as e:
        print(f"❌ Comic sheet assembly failed: {e}")
        comic_sheet = create_simple_comic_grid([img for img, _ in panels_with_images])
        final_panel_locations = []

    comic_page_panels = []
    for i, frame in enumerate(scenario.frames):
        panel_location_data = next((loc for loc in final_panel_locations if loc["panel"] == i + 1), {})
        comic_page_panels.append(
            ComicPanelWithImageSchema(
                panel=i+1,
                image_prompt=f"Panel {i+1} ({frame.camera_shot}): {frame.description[:50]}...",
                image_url="",
                dialogue="; ".join([f"{d.speaker}: {d.text}" for d in frame.dialogues]),
                x_coord=panel_location_data.get("x", 0),
                y_coord=panel_location_data.get("y", 0),
                panel_width=panel_location_data.get("width", 1024),
                panel_height=panel_location_data.get("height", 1024)
            )
        )

    comic_page = ComicsPageSchema(
        genre=scenario.genre,
        art_style=scenario.art_style,
        panels=comic_page_panels,
        invalid_request=False
    )

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
                scenario_description=f"Based on this generated comic:\n\n{comic_content}\n\nOriginal concept: {concept}"
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


    return comic_page, comic_sheet, detailed_scenario

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
        genre_lower = genre.strip().lower()
        if genre_lower not in GENRE_MAPPINGS:
            print(f"⚠️ Unknown genre '{genre}', using 'action' as fallback")
            genre = "action"
        else:
            genre = genre_lower
    else:
        genre = "action"
    
    # Normalize art style
    if art_style:
        art_style_lower = art_style.strip().lower()
        if art_style_lower not in CONSISTENT_STYLES:
            print(f"⚠️ Unknown art style '{art_style}', using 'comic book' as fallback")
            art_style = "comic book"
        else:
            art_style = art_style_lower
    else:
        art_style = "comic book"
    
    return genre, art_style

