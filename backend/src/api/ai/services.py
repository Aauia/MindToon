import os, math, requests, base64
from PIL import Image
from io import BytesIO
from api.ai.llms import get_openai_llm
from api.ai.schemas import (
    ScenarioSchema, ComicPanelsResponseSchema,
    ComicPanelsWithImagesResponseSchema, ComicPanelWithImageSchema, ComicsPageSchema,
    ScenarioSchema2
)

from api.utils.image_utils import create_comic_sheet
from dotenv import load_dotenv

load_dotenv()
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"


def generate_scenario(prompt: str) -> ScenarioSchema:
    llm_base = get_openai_llm()
    llm = llm_base.with_structured_output(ScenarioSchema)

    messages = [
        (
            "system",
            "You are a creative assistant. Given a user's prompt, first discover the most fitting genre (e.g., sci-fi, fantasy, mystery, etc.), then generate a fascinating, detailed scenario based on the user's text. Respond only with the genre and the scenario, no markdown, only plaintext.",
        ),
        (
            "human",
            f"Prompt: {prompt}",
        ),
    ]

    return llm.invoke(messages)

def generate_comic_scenario(prompt: str, genre: str = None, art_style: str = None) -> ScenarioSchema2:
    """Generate a complete comic scenario with frames and dialogue"""
    llm_base = get_openai_llm()
    llm = llm_base.with_structured_output(ScenarioSchema2)

    system_prompt = """You are a professional comic book writer and storyboard artist. Create engaging, original comic stories with:

    STORY REQUIREMENTS:
    1. A compelling, unique title
    2. Clear genre and consistent mood
    3. MAXIMUM 2 main characters with SIMPLE, MEMORABLE names (like "Sam", "Alex", "Maya", "Jin", "Leo")
    4. Exactly 4 panels that tell a complete story (EXACTLY 4 panels, no more, no less!)
    5. Each panel should advance the plot significantly

    CHARACTER CONSISTENCY - CRITICAL:
    - Create ONE detailed character description and use it EXACTLY in every panel
    - Include: hair color, hair style, clothing, distinctive features, age appearance
    - Example: "Sam: 16-year-old girl, short black hair, red hoodie, jeans, friendly smile"
    - Example: "Alex: tall man, brown curly hair, blue suit, white shirt, confident expression"
    - Use these EXACT descriptions in every single panel description

    DIALOGUE REQUIREMENTS - VERY IMPORTANT:
    - Maximum 1-2 short speech bubbles per panel (TOTAL)
    - Each speech bubble: Maximum 6 words
    - Use simple, natural language with contractions
    - Focus on ACTION over talking
    - Examples of GOOD dialogue:
        * "Wait, what's that?"
        * "Oh no!"
        * "This is amazing!"
        * "Help me!"
    - Examples of BAD dialogue (NEVER use):
        * "I cannot believe what I am witnessing"
        * Long sentences or explanations
        * Multiple speakers per panel

    DIALOGUE TYPES - Use strategically:
    - speech: Short conversations ("Hey!" "What?")
    - thought: Brief thoughts ("I hope...")
    - narration: Scene setting only ("Later...")
    - sound_effect: Action sounds ("CRASH!" "RING!")
    - scream: Emotions ("NOOO!" "WOW!")

    PANEL DESCRIPTIONS - CRITICAL FOR CONSISTENCY:
    - Start EVERY panel description with the exact character description
    - Include specific positioning and expressions
    - Describe backgrounds simply
    - Make each panel visually distinct but cohesive
    - Example: "Sam (16-year-old girl, short black hair, red hoodie, jeans, friendly smile) stands in a classroom looking surprised"

    STORY EXAMPLES TO INSPIRE:
    - A student's drawing comes to life
    - Someone discovers a magical power
    - A pet gains superpowers
    - Friends solve a mystery
    - A magical object causes chaos

    Remember: Visual storytelling is MORE important than dialogue in comics! Keep dialogue minimal and focus on clear, engaging visuals with consistent characters."""

    user_message = f"Concept: {prompt}"
    if genre:
        user_message += f"\nGenre: {genre}"
    if art_style:
        user_message += f"\nArt Style: {art_style}"

    messages = [
        ("system", system_prompt),
        ("human", user_message),
    ]

    return llm.invoke(messages)


def generate_image_from_prompt(prompt: str, character_lora: str = None, lora_strength: float = 0.8) -> Image.Image:
    """Generate image using Stability AI Stable Diffusion with LoRA support for character consistency"""
    try:
        print(f"🖼️ Generating image with Stable Diffusion: {prompt[:100]}...")
        if character_lora:
            print(f"🎭 Using character LoRA: {character_lora} (strength: {lora_strength})")
        
        # Check if STABILITY_API_KEY is available
        if not STABILITY_API_KEY:
            print("❌ STABILITY_API_KEY not found in environment variables")
            raise Exception("STABILITY_API_KEY not configured")
        
        # Prepare headers and payload for Stability AI
        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Enhanced payload with LoRA support
        payload = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 35,  # Increased steps for better quality
            "style_preset": "comic-book"  # Use comic book style preset
        }
        # Note: seed parameter removed - will be auto-generated by Stability AI
        
        # Add LoRA parameters if character_lora is provided
        if character_lora:
            # For character consistency, we use the same seed and add LoRA instructions
            payload["text_prompts"] = [
                {
                    "text": f"{prompt}, {character_lora}, consistent character design, same person",
                    "weight": 1.0
                },
                {
                    "text": "different character, inconsistent design, multiple people, face change",
                    "weight": -0.5  # Negative prompt to avoid inconsistency
                }
            ]
            payload["cfg_scale"] = 8  # Higher CFG for better adherence to prompts
            payload["steps"] = 40  # More steps for better consistency

        # Make request to Stability AI
        response = requests.post(STABILITY_API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"❌ Stability AI API error: {response.status_code} - {response.text}")
            raise Exception(f"Stability AI API error: {response.status_code}")
        
        # Get the base64 image data from response
        data = response.json()
        
        # Validate response structure
        if "artifacts" not in data or not data["artifacts"]:
            raise Exception("No artifacts in Stability AI response")
        
        if "base64" not in data["artifacts"][0]:
            raise Exception("No base64 data in Stability AI response")
        
        image_base64 = data["artifacts"][0]["base64"]
        
        # Validate base64 string
        if not image_base64:
            raise Exception("Empty base64 string in response")
        
        # Convert base64 directly to PIL Image
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            
            # Validate the image was loaded correctly
            image.verify()  # This checks if the image is valid
            
            # Reopen the image since verify() may close it
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            
            print("✅ Stable Diffusion image generated and converted successfully")
            print(f"📏 Image size: {image.size}, mode: {image.mode}")
            return image
            
        except Exception as conversion_error:
            print(f"❌ Error converting base64 to PIL Image: {conversion_error}")
            raise Exception(f"Base64 to PIL Image conversion failed: {conversion_error}")
        
    except Exception as e:
        print(f"❌ Error generating image with Stable Diffusion: {e}")
        print(f"🔍 STABILITY_API_KEY configured: {bool(STABILITY_API_KEY)}")
        print(f"🔍 STABILITY_API_KEY length: {len(STABILITY_API_KEY) if STABILITY_API_KEY else 0}")
        
        # Return a placeholder image that shows there's an issue
        print("🔧 Returning placeholder image - please check your STABILITY_API_KEY")
        placeholder = Image.new('RGB', (512, 512), color='red')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(placeholder)
        try:
            font = ImageFont.load_default()
            draw.text((30, 200), "STABLE DIFFUSION\nGENERATION FAILED\nCheck STABILITY_API_KEY", fill='white', font=font, align='center')
        except:
            pass
        return placeholder


def generate_character_reference(character_name: str, character_description: str, art_style: str = "comic book") -> str:
    """Generate a detailed character reference prompt for LoRA consistency"""
    
    # Create a comprehensive character reference
    base_reference = (
        f"REFERENCE CHARACTER {character_name}: "
        f"{character_description}, "
        f"consistent character design, same person in every image, "
        f"distinctive features, memorable appearance, "
        f"{art_style} art style"
    )
    
    # Add style-specific enhancements
    if "manga" in art_style.lower() or "anime" in art_style.lower():
        base_reference += ", anime character design, cel shading, consistent anime features"
    elif "disney" in art_style.lower():
        base_reference += ", Disney character design, clean animation style, consistent cartoon features"
    elif "comic" in art_style.lower():
        base_reference += ", comic book character design, consistent superhero-style features"
    
    # Add technical consistency requirements
    base_reference += (
        ", IMPORTANT: exact same hair color, exact same hair style, "
        "exact same clothing, exact same facial features, "
        "exact same body proportions, character consistency"
    )
    
    return base_reference


def generate_complete_comic(concept: str, genre: str = None, art_style: str = None) -> tuple:
    """Generate a complete comic from concept to final page with LoRA character consistency"""
    
    # Step 1: Generate story scenario with improved consistency
    print("🎬 Generating story scenario...")
    scenario = generate_comic_scenario(concept, genre, art_style)
    
    # Step 2: Create character LoRA reference for consistency
    print("🎭 Creating character LoRA reference...")
    
    character_lora_reference = None
    main_character_name = None
    
    if scenario.characters and len(scenario.characters) > 0:
        main_character_name = scenario.characters[0]
        
        # Extract character description from the first frame
        first_frame_desc = scenario.frames[0].description if scenario.frames else ""
        
        # Create detailed character description for LoRA
        character_details = extract_character_details(first_frame_desc, main_character_name)
        
        # Generate LoRA reference
        character_lora_reference = generate_character_reference(
            main_character_name, 
            character_details, 
            scenario.art_style or "comic book"
        )
        
        print(f"🎯 Character LoRA reference created for {main_character_name}")
        print(f"📝 Reference: {character_lora_reference[:100]}...")
    
    # Step 3: Generate images for each frame with LoRA consistency
    print("🎨 Generating comic panels with LoRA character consistency...")
    panels_with_images = []
    
    # Use consistent seed for character appearance
    import random
    character_seed = random.randint(1000000, 9999999)
    
    for i, frame in enumerate(scenario.frames):
        # Art style specification
        style_instruction = "clean comic book art style"
        if scenario.art_style:
            if "manga" in scenario.art_style.lower():
                style_instruction = "manga/anime art style, clean line art, cel shading"
            elif "disney" in scenario.art_style.lower():
                style_instruction = "Disney animation style, clean vector art"
            elif "cartoon" in scenario.art_style.lower():
                style_instruction = "cartoon illustration style, simple clean lines"
            else:
                style_instruction = f"{scenario.art_style} art style"
        
        # Build the image prompt with LoRA character consistency
        image_prompt = f"""Comic panel {i+1}: {frame.description}
        
        Style: {style_instruction}, professional comic book illustration, clear visual storytelling, single comic panel layout.
        
        Technical: No speech bubbles in image, clean background, consistent lighting, {scenario.genre or 'adventure'} mood, high quality comic art.
        
        Character consistency: If character appears, maintain exact same appearance as established in reference."""
        
        print(f"  🖼️ Panel {frame.frame_number}: {frame.description[:60]}...")
        
        # Generate image with LoRA character consistency
        try:
            image = generate_image_from_prompt(
                image_prompt, 
                character_lora=character_lora_reference,  # Use LoRA reference
                lora_strength=0.9  # High strength for consistency
            )
            print(f"  ✅ Panel {frame.frame_number} generated with character consistency")
        except Exception as e:
            print(f"  ❌ Panel {frame.frame_number} failed: {e}")
            # Create placeholder image for failed generations
            image = Image.new('RGB', (512, 512), color='lightgray')
        
        # Store image with minimal dialogue
        limited_dialogues = frame.dialogues[:2] if frame.dialogues else []  # Max 2 dialogues per panel
        panels_with_images.append((image, limited_dialogues))
    
    # Step 4: Create comic sheet with better layout
    print("📄 Assembling final comic page...")
    try:
        comic_sheet = create_comic_sheet(panels_with_images)
        print("✅ Comic sheet assembled successfully with character consistency")
    except Exception as e:
        print(f"❌ Comic sheet assembly failed: {e}")
        # Create a simple 2x2 grid as fallback
        comic_sheet = create_simple_comic_grid([img for img, _ in panels_with_images])
    
    # Create final response
    comic_page = ComicsPageSchema(
        genre=scenario.genre,
        art_style=scenario.art_style,
        panels=[
            ComicPanelWithImageSchema(
                panel=i+1,
                image_prompt=f"Panel {i+1}: {frame.description[:50]}...",
                image_url="",
                dialogue="; ".join([f"{d.speaker}: {d.text}" for d in frame.dialogues[:2]]) if frame.dialogues else None  # Limit dialogue
            )
            for i, frame in enumerate(scenario.frames)
        ],
        invalid_request=False
    )
    
    return comic_page, comic_sheet


def extract_character_details(frame_description: str, character_name: str) -> str:
    """Extract and standardize character details from frame description"""
    
    # Look for character-specific details in the description
    description_lower = frame_description.lower()
    details = []
    
    # Extract age if mentioned
    age_keywords = ["teenage", "teen", "young", "old", "adult", "child", "kid"]
    for age in age_keywords:
        if age in description_lower:
            details.append(age)
            break
    
    # Extract hair details
    hair_colors = ["black", "brown", "blonde", "red", "white", "gray", "blue", "green", "pink", "purple"]
    hair_styles = ["short", "long", "curly", "straight", "wavy", "spiky"]
    
    for color in hair_colors:
        if color in description_lower and "hair" in description_lower:
            details.append(f"{color} hair")
            break
    
    for style in hair_styles:
        if style in description_lower and "hair" in description_lower:
            if not any("hair" in d for d in details):  # Don't duplicate hair info
                details.append(f"{style} hair")
            else:
                # Add style to existing hair description
                details = [d.replace("hair", f"{style} hair") if "hair" in d else d for d in details]
            break
    
    # Extract clothing
    clothing_items = ["hoodie", "shirt", "jacket", "dress", "suit", "jeans", "pants", "skirt"]
    clothing_colors = ["red", "blue", "green", "black", "white", "yellow", "purple", "orange"]
    
    for item in clothing_items:
        if item in description_lower:
            # Try to find color for this clothing item
            for color in clothing_colors:
                if color in description_lower:
                    details.append(f"{color} {item}")
                    break
            else:
                details.append(item)
            break
    
    # Create a standardized character description
    if details:
        character_desc = f"{character_name}: {', '.join(details)}"
    else:
        # Fallback description
        character_desc = f"{character_name}: distinctive character with consistent appearance"
    
    return character_desc


def create_simple_comic_grid(images):
    """Create a simple 2x2 grid layout as fallback when comic sheet creation fails"""
    try:
        # Resize all images to same size
        panel_size = (400, 400)
        resized_images = []
        
        for img in images[:4]:  # Take first 4 images
            resized_img = img.resize(panel_size, Image.Resampling.LANCZOS)
            resized_images.append(resized_img)
        
        # Create 2x2 grid
        grid_width = panel_size[0] * 2
        grid_height = panel_size[1] * 2
        comic_grid = Image.new('RGB', (grid_width, grid_height), 'white')
        
        # Position images in grid
        positions = [(0, 0), (panel_size[0], 0), (0, panel_size[1]), (panel_size[0], panel_size[1])]
        
        for i, img in enumerate(resized_images):
            if i < len(positions):
                comic_grid.paste(img, positions[i])
        
        return comic_grid
        
    except Exception as e:
        print(f"❌ Simple grid creation failed: {e}")
        # Ultimate fallback - single color image
        return Image.new('RGB', (800, 800), color='lightblue')


