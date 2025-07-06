from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional
from api.ai.schemas import Dialogue # Make sure to import the updated Dialogue schema
import platform
import os
import math
import random
import textwrap # Import textwrap for better text wrapping
import sys
import glob
# Define fonts - Mac-compatible system fonts with comic font priorities
def get_system_font(font_name: str, size: int, fallback_font_name: str = "arial", fallback_size: int = 20):
    """
    Enhanced font loading with prioritized uploaded fonts and robust fallbacks.
    
    IMPORTANT NOTE:
    The 'uploaded_fonts' mapping currently points all font_name keys to 'Merriweather-Light.otf'.
    For a more diverse comic book look, you should upload and map different .otf/.ttf
    files for 'comic_speech', 'impact', 'thought', 'narration', 'comic_bold', etc.
    For example:
    uploaded_fonts = {
        "arial": ["Merriweather-Light.otf"],
        "comic_speech": ["ComicSansMS.ttf"], # Or a custom comic font you upload
        "comic_bold": ["Bangers-Regular.ttf"], # Example for a bold, impactful font
        "impact": ["Impact.ttf"],
        # ... and so on for other font types
    }
    """
    # FIRST PRIORITY: Check for uploaded fonts in our fonts directory
    fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
    uploaded_fonts = {
        "arial": ["Merriweather-Light.otf"],
        "arial_bold": ["Merriweather-Light.otf"],  # Use Merriweather for all text
        "arial_black": ["Merriweather-Light.otf"],
        "times": ["Merriweather-Light.otf"],
        "comic_speech": ["Merriweather-Light.otf"],
        "comic_bold": ["Merriweather-Light.otf"],
        "impact": ["Merriweather-Light.otf"],
        "thought": ["Merriweather-Light.otf"],
        "narration": ["Merriweather-Light.otf"]
    }
    
    # Try uploaded fonts first
    if font_name in uploaded_fonts:
        for font_file in uploaded_fonts[font_name]:
            font_path = os.path.join(fonts_dir, font_file)
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, size)
                    print(f"🎨 Using uploaded font: {font_file} (size {size})")
                    return font
                except (IOError, OSError) as e:
                    print(f"Could not load uploaded font {font_file}: {e}")
                    continue
    
    system = platform.system()
    
    # SECOND PRIORITY: System fonts (macOS)
    if system == "Darwin":  # macOS
        # These are common macOS system fonts. Consider adding more comic-like ones
        # if available on macOS by default, or relying on uploads.
        font_mappings = {
            "arial": "/System/Library/Fonts/Helvetica.ttc",
            "arial_bold": "/System/Library/Fonts/Helvetica Bold.ttf" if os.path.exists("/System/Library/Fonts/Helvetica Bold.ttf") else "/System/Library/Fonts/Helvetica.ttc",
            "arial_black": "/System/Library/Fonts/Arial Black.ttf" if os.path.exists("/System/Library/Fonts/Arial Black.ttf") else "/System/Library/Fonts/Helvetica.ttc",
            "times": "/System/Library/Fonts/Times.ttc",
            "comic_speech": "/System/Library/Fonts/Arial.ttf" if os.path.exists("/Library/Fonts/Arial.ttf") else "/System/Library/Fonts/Helvetica.ttc", # More readable
            "comic_bold": "/System/Library/Fonts/Impact.ttf" if os.path.exists("/System/Library/Fonts/Impact.ttf") else "/System/Library/Fonts/Helvetica.ttc", # More impact
            "impact": "/System/Library/Fonts/Impact.ttf" if os.path.exists("/System/Library/Fonts/Impact.ttf") else "/System/Library/Fonts/Helvetica.ttc",
            "thought": "/System/Library/Fonts/Apple Chancery.ttf" if os.path.exists("/System/Library/Fonts/Apple Chancery.ttf") else "/System/Library/Fonts/Helvetica.ttc", # More whimsical
            "narration": "/System/Library/Fonts/Times.ttc"
        }
        
        # Try the mapped font
        mapped_font = font_mappings.get(font_name)
        if mapped_font and os.path.exists(mapped_font):
            try:
                if mapped_font.endswith(".ttc"):
                    for i in range(5):
                        try:
                            font = ImageFont.truetype(mapped_font, size, index=i)
                            print(f"✅ Using system font: {os.path.basename(mapped_font)} (index {i}, size {size})")
                            return font
                        except (IOError, OSError):
                            continue
                else:
                    font = ImageFont.truetype(mapped_font, size)
                    print(f"✅ Using system font: {os.path.basename(mapped_font)} (size {size})")
                    return font
            except (IOError, OSError):
                pass
        
        # THIRD PRIORITY: Common macOS backup fonts
        backup_fonts = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Times.ttc", 
            "/System/Library/Fonts/Courier.ttc",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Monaco.ttf"
        ]
        
        for backup_font in backup_fonts:
            if os.path.exists(backup_font):
                try:
                    if backup_font.endswith(".ttc"):
                        for i in range(3):
                            try:
                                font = ImageFont.truetype(backup_font, size, index=i)
                                print(f"✅ Using backup font: {os.path.basename(backup_font)} (size {size})")
                                return font
                            except (IOError, OSError):
                                continue
                    else:
                        font = ImageFont.truetype(backup_font, size)
                        print(f"✅ Using backup font: {os.path.basename(backup_font)} (size {size})")
                        return font
                except (IOError, OSError):
                    continue
    
    else:  # Windows/Linux - simplified fallback
        common_fonts = ["arial.ttf", "times.ttf", "helvetica.ttf", "courier.ttf"]
        font_dirs = []
        
        if system == "Windows":
            font_dirs = [os.environ.get("WINDIR", "C:\\Windows") + "\\Fonts"]
        else:  # Linux
            font_dirs = ["/usr/share/fonts/truetype", "/usr/share/fonts", os.path.expanduser("~/.fonts")]
        
        for font_dir in font_dirs:
            for font_file in common_fonts:
                font_path = os.path.join(font_dir, font_file)
                if os.path.exists(font_path):
                    try:
                        font = ImageFont.truetype(font_path, size)
                        print(f"✅ Using system font: {font_file} (size {size})")
                        return font
                    except (IOError, OSError):
                        continue

    # FINAL FALLBACK: Pillow default
    print(f"⚠️ All fonts failed, using Pillow default for '{font_name}' (size {size})")
    return ImageFont.load_default()

# --- Load Fonts using the improved function ---
# Consider making these dynamic later based on total panel size or user preference
# Increased sizes are good, ensure they work well with your chosen sheet size.
SPEECH_FONT_SIZE = 36 # Readable speech bubbles
THOUGHT_FONT_SIZE = 32 # Slightly smaller for thoughts
SFX_FONT_SIZE = 48 # Bigger for sound effects
NARRATION_FONT_SIZE = 30 # Clean narration text
SCREAM_FONT_SIZE = 42 # Bigger for emphasis
WHISPER_FONT_SIZE = 28 # Smaller for whispers
EXCITED_FONT_SIZE = 40 # Medium excited text

try:
    SPEECH_FONT = get_system_font("comic_speech", SPEECH_FONT_SIZE)
    THOUGHT_FONT = get_system_font("thought", THOUGHT_FONT_SIZE)
    SFX_FONT = get_system_font("impact", SFX_FONT_SIZE)
    NARRATION_FONT = get_system_font("narration", NARRATION_FONT_SIZE)
    SCREAM_FONT = get_system_font("comic_bold", SCREAM_FONT_SIZE)
    WHISPER_FONT = get_system_font("thought", WHISPER_FONT_SIZE) # Using thought font for whisper
    EXCITED_FONT = get_system_font("comic_bold", EXCITED_FONT_SIZE)
except Exception as e:
    print(f"CRITICAL: Font loading error: {e}. All fonts defaulting.")
    # If all else fails, ensure *some* font is loaded
    SPEECH_FONT = ImageFont.load_default()
    THOUGHT_FONT = ImageFont.load_default()
    SFX_FONT = ImageFont.load_default()
    NARRATION_FONT = ImageFont.load_default()
    SCREAM_FONT = ImageFont.load_default()
    WHISPER_FONT = ImageFont.load_default()
    EXCITED_FONT = ImageFont.load_default()





def wrap_text_pil(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """
    Advanced text wrapping using PIL's textlength method for accurate measurements.
    Handles very long words by breaking them if necessary.
    """
    if not text or not text.strip():
        return []

    lines = []
    current_line_words = []

    words = text.split(' ') # Split by space
    
    for word in words:
        # Check if adding the next word exceeds max_width
        test_line = ' '.join(current_line_words + [word])
        if draw.textlength(test_line, font=font) <= max_width:
            current_line_words.append(word)
        else:
            # Current word doesn't fit
            if current_line_words:
                # If there's content in the current line, add it
                lines.append(' '.join(current_line_words))
                current_line_words = [word] # Start new line with the current word
            else:
                # This means a single word is longer than max_width.
                # We need to break this word.
                broken_word_lines = []
                temp_word_part = ""
                for char in word:
                    if draw.textlength(temp_word_part + char, font=font) <= max_width:
                        temp_word_part += char
                    else:
                        broken_word_lines.append(temp_word_part)
                        temp_word_part = char
                if temp_word_part:
                    broken_word_lines.append(temp_word_part)
                lines.extend(broken_word_lines)
                current_line_words = [] # Reset for next words
    
    if current_line_words:
        lines.append(' '.join(current_line_words))
        
    return lines

def calculate_dynamic_font_size(draw: ImageDraw.Draw, text: str, max_width: int, max_height: int, base_font_obj: ImageFont.FreeTypeFont, min_font_size: int = 28) -> ImageFont.FreeTypeFont:
    """ Calculate optimal font size that fits within given dimensions, starting from a base font object and shrinking if necessary. """
    current_size = base_font_obj.size # Start from the size of the passed font object
    # Extract font family name from font object
    try:
        font_family_name = base_font_obj.getname()[0]
    except AttributeError:
        font_family_name = "arial" # Fallback if getname() fails

    optimal_font = base_font_obj
    
    # Try increasing size slightly first if there's ample space (optional, but can improve look)
    # This might make text too large, so commenting out for now for safer default behavior.
    # for size in range(current_size, current_size + 10, 2):
    #     temp_font = get_system_font(font_family_name, size)
    #     wrapped_text = wrap_text_pil(draw, text, temp_font, max_width)
    #     text_height = len(wrapped_text) * draw.textlength("A", font=temp_font) # Approximated line height
    #     if text_height <= max_height:
    #         optimal_font = temp_font
    #     else:
    #         break

    # Decrease font size if text is too large
    for size in range(current_size, min_font_size - 1, -2):
        temp_font = get_system_font(font_family_name, size)
        wrapped_text = wrap_text_pil(draw, text, temp_font, max_width)
        
        # Calculate actual height needed for wrapped text
        total_text_height = 0
        if wrapped_text:
            # Measure height of each line and sum them up, plus a small line spacing
            line_height = draw.textbbox((0, 0), "TEST", font=temp_font)[3] - draw.textbbox((0, 0), "TEST", font=temp_font)[1]
            total_text_height = len(wrapped_text) * line_height + (len(wrapped_text) - 1) * 2 # 2px line spacing

        if total_text_height <= max_height:
            optimal_font = temp_font
            break
        optimal_font = temp_font # Keep shrinking even if it doesn't fit, to get smallest possible

    return optimal_font

def draw_text_with_outline(draw: ImageDraw.Draw, xy: Tuple[int, int], text: str, 
                           font: ImageFont.FreeTypeFont, text_color: str, 
                           outline_color: str, outline_width: int):
    """
    Draws text with an outline.
    """
    x, y = xy
    # Draw outline
    if outline_width > 0:
        for offset_x in range(-outline_width, outline_width + 1):
            for offset_y in range(-outline_width, outline_width + 1):
                if offset_x * offset_x + offset_y * offset_y <= outline_width * outline_width: # Circle for smoother outline
                    draw.text((x + offset_x, y + offset_y), text, font=font, fill=outline_color)
    # Draw main text
    draw.text(xy, text, font=font, fill=text_color)
def add_dialogues_and_sfx_to_panel(
    panel_image: Image.Image,
    dialogues: List[Dialogue],
    panel_width: int,
    panel_height: int,
    character_names: List[str] = None
) -> Image.Image:
    """
    Adds dialogues, thought bubbles, narration, and SFX to a single comic panel image.
    Uses the new improved comic text rendering system with smart positioning.
    """
    from .comic_text_utils import ComicTextRenderer, TextBubble
    
    if not dialogues:
        return panel_image
    
    print(f"🎯 Processing panel with FRAME-SPECIFIC dimensions {panel_width}x{panel_height} and {len(dialogues)} dialogues")
    
    renderer = ComicTextRenderer()
    result = panel_image.copy()
    
    # Scale font sizes based on panel size - but keep them readable
    size_factor = min(panel_width / 800, panel_height / 600, 1.0)  # Scale down for smaller panels
    # Don't let size_factor go too small - keep text readable
    size_factor = max(size_factor, 0.6)  # Minimum 60% of original size for readability
    print(f"📏 Frame-specific size factor: {size_factor:.2f} for {panel_width}x{panel_height} panel")
    
    # ALWAYS use simple positioning to prevent overlaps - more reliable than smart positioning
    positioned_dialogues = dialogues
    try:
        from .simple_positioning import simple_position_dialogues
        positioned_dialogues, analysis = simple_position_dialogues(
            panel_image, dialogues, character_names
        )
        print(f"📍 Simple positioning: Prevented overlaps for {len(positioned_dialogues)} bubbles")
    except Exception as e:
        print(f"❌ Simple positioning failed: {e}")
        # Fallback to manual collision avoidance
        positioned_dialogues = []
        used_positions = []
        
        for i, dialogue in enumerate(dialogues):
            # Calculate safe position manually with frame-relative spacing
            safe_margin = max(20, int(panel_width * 0.05))  # 5% of panel width as margin
            
            # Try different positions until we find one without collision
            candidate_positions = [
                (safe_margin, safe_margin),                    # Top-left
                (panel_width - 400 * size_factor, safe_margin),         # Top-right  
                (safe_margin, panel_height - 120 * size_factor),         # Bottom-left
                (panel_width - 400 * size_factor, panel_height - 120 * size_factor), # Bottom-right
                (panel_width//2 - 200 * size_factor, safe_margin),      # Top-center
                (panel_width//2 - 200 * size_factor, panel_height - 120 * size_factor), # Bottom-center
                (safe_margin, panel_height//2 - 60 * size_factor),       # Mid-left
                (panel_width - 400 * size_factor, panel_height//2 - 60 * size_factor), # Mid-right
                (panel_width//2 - 200 * size_factor, panel_height//2 - 60 * size_factor), # Center
            ]
            
            # Add offset for each subsequent dialogue to avoid overlaps - use more spacing
            for j, (base_x, base_y) in enumerate(candidate_positions):
                final_x = base_x + (i * 80 * size_factor)  # More spacing between bubbles
                final_y = base_y + (i * 50 * size_factor)
                
                # Keep within bounds
                final_x = max(safe_margin, min(final_x, panel_width - 400 * size_factor))
                final_y = max(safe_margin, min(final_y, panel_height - 120 * size_factor))
                
                # Check if this position conflicts with already placed bubbles
                bubble_w = int(min(250 * size_factor, panel_width * 0.35))  # Narrower width - max 35%
                bubble_h = int(min(150 * size_factor, panel_height * 0.35))  # Taller height - max 35%
                bubble_rect = (final_x, final_y, bubble_w, bubble_h)
                has_conflict = False
                
                for used_rect in used_positions:
                    if not (bubble_rect[0] + bubble_rect[2] < used_rect[0] or 
                           used_rect[0] + used_rect[2] < bubble_rect[0] or
                           bubble_rect[1] + bubble_rect[3] < used_rect[1] or 
                           used_rect[1] + used_rect[3] < bubble_rect[1]):
                        has_conflict = True
                        break
            
                if not has_conflict:
                    # Found a good position
                    used_positions.append(bubble_rect)
                    
                    # Update dialogue position
                    if hasattr(dialogue, '__dict__'):
                        new_dialogue = type(dialogue)(**dialogue.__dict__)
                        new_dialogue.position = "center"
                        if hasattr(new_dialogue, 'x_coord'):
                            new_dialogue.x_coord = int(final_x)
                            new_dialogue.y_coord = int(final_y)
                    else:
                        new_dialogue = dialogue
                    
                    positioned_dialogues.append(new_dialogue)
                    break
            else:
                # If no position found, just add with large offset
                positioned_dialogues.append(dialogue)
        
        print(f"🔧 Manual collision avoidance: {len(positioned_dialogues)} bubbles positioned")
    
    # Convert dialogues to TextBubbles and render them with FORCED positioning
    rendered_positions = []  # Track what we've actually rendered to prevent overlaps
    
    for i, dialogue in enumerate(positioned_dialogues):
        if not dialogue.text or not dialogue.text.strip():
            continue

        # Map dialogue type to bubble type (handle scream -> speech with shouting emotion)
        bubble_type = dialogue.type
        bubble_emotion = dialogue.emotion
        
        # Handle "scream" type by converting to speech with shouting emotion
        if dialogue.type == "scream":
            bubble_type = "speech"
            bubble_emotion = "shouting"
        
        # Use a more distributed default spread pattern
        default_positions = [
            (int(panel_width * 0.1), int(panel_height * 0.1)),      # Top-left
            (int(panel_width * 0.6), int(panel_height * 0.1)),      # Top-right
            (int(panel_width * 0.1), int(panel_height * 0.6)),      # Bottom-left
            (int(panel_width * 0.6), int(panel_height * 0.6)),      # Bottom-right
            (int(panel_width * 0.35), int(panel_height * 0.1)),     # Top-center
            (int(panel_width * 0.35), int(panel_height * 0.6)),     # Bottom-center
        ]
        
        if i < len(default_positions):
            forced_x, forced_y = default_positions[i]
        else:
            forced_x = int(50 * size_factor + ((i % 3) * panel_width * 0.3))  # Distribute across width
            forced_y = int(50 * size_factor + ((i // 3) * panel_height * 0.4))  # Distribute across height
        
        # Override with coordinates from positioning system if available and valid
        if hasattr(dialogue, 'x_coord') and hasattr(dialogue, 'y_coord'):
            if dialogue.x_coord is not None and dialogue.y_coord is not None:
                # Scale coordinates to current panel size if they seem to be from a different scale
                pos_x, pos_y = dialogue.x_coord, dialogue.y_coord
                
                # If coordinates are outside current panel, assume they're from a different scale and adjust
                if pos_x >= panel_width or pos_y >= panel_height:
                    # Assume coordinates were calculated for 800x600 and scale down
                    scale_x = panel_width / 800
                    scale_y = panel_height / 600
                    pos_x = int(pos_x * scale_x)
                    pos_y = int(pos_y * scale_y)
                    print(f"📏 Scaled coordinates from ({dialogue.x_coord}, {dialogue.y_coord}) to ({pos_x}, {pos_y}) for {panel_width}x{panel_height} panel")
                
                # Ensure coordinates are within panel bounds
                forced_x = max(20, min(pos_x, panel_width - 150))
                forced_y = max(20, min(pos_y, panel_height - 80))
                print(f"📍 Using positioned coordinates for bubble {i}: ({forced_x}, {forced_y})")
            else:
                print(f"⚠️ No coordinates found for bubble {i}, using default: ({forced_x}, {forced_y})")
        else:
            print(f"⚠️ No coordinates found for bubble {i}, using default: ({forced_x}, {forced_y})")
        
        # Final collision check against already rendered bubbles with frame-relative bubble size
        bubble_w = int(min(250 * size_factor, panel_width * 0.35))  # Narrower width - max 35%
        bubble_h = int(min(150 * size_factor, panel_height * 0.35))  # Taller height - max 35%
        bubble_rect = (forced_x, forced_y, bubble_w, bubble_h)
        print(f"💬 Frame-specific bubble {i} size: {bubble_w}x{bubble_h} for {panel_width}x{panel_height} panel")
        
        collision_attempts = 0
        while (any(not (bubble_rect[0] + bubble_rect[2] + 20 < rendered[0] or 
                       rendered[0] + rendered[2] + 20 < bubble_rect[0] or
                       bubble_rect[1] + bubble_rect[3] + 20 < rendered[1] or 
                       rendered[1] + rendered[3] + 20 < bubble_rect[1]) 
                  for rendered in rendered_positions) and collision_attempts < 10):
            # Move bubble to avoid collision with more spacing
            forced_x += int(80 * size_factor)
            forced_y += int(50 * size_factor)
            # Keep within panel bounds
            forced_x = max(20, min(forced_x, panel_width - bubble_w - 20))
            forced_y = max(20, min(forced_y, panel_height - bubble_h - 20))
            bubble_rect = (forced_x, forced_y, bubble_w, bubble_h)
            collision_attempts += 1
            print(f"🔄 Adjusted bubble {i} position to avoid collision: ({forced_x}, {forced_y})")
        
        # Track this bubble's position
        rendered_positions.append(bubble_rect)
        
        print(f"🎯 FORCING bubble at exact position: ({forced_x}, {forced_y}) - '{dialogue.speaker}: {dialogue.text[:30]}...'")
        
        # Create TextBubble with FORCED coordinates and frame-scaled style
        bubble = TextBubble(
            text=dialogue.text,
            position=(forced_x, forced_y),  # FORCE the positioned coordinates
            bubble_type=bubble_type,
            emotion=bubble_emotion,
            speaker_position=dialogue.position if hasattr(dialogue, 'position') else "center"
        )
        
        # Adjust bubble style for panel size
        if bubble.style is None:
            bubble.style = renderer.default_styles.get(bubble_type, renderer.default_styles["speech"])
        
        # Scale font size based on panel dimensions - keep it readable
        original_font_size = bubble.style.font_size
        scaled_font_size = max(24, int(original_font_size * size_factor))  # Minimum 24px for readability
        bubble.style.font_size = scaled_font_size
        
        # Scale padding but keep it reasonable
        bubble.style.padding = max(15, int(bubble.style.padding * size_factor))
        
        # Add speaker name reference
        if dialogue.speaker:
            bubble.speaker_name = dialogue.speaker
            if bubble_type in ["speech", "thought"]:
                bubble.text = f"{dialogue.speaker}: {dialogue.text}"
        
        # Render the bubble directly at specified coordinates
        try:
            result = renderer.render_text_bubble_at_position(result, bubble, forced_x, forced_y, panel_width, panel_height)
            
            # Get actual bubble size for tracking
            actual_bubble_size = renderer.calculate_bubble_size(bubble.text, bubble.style, panel_width // 2)
            print(f"📐 Bubble size: {actual_bubble_size[0]}x{actual_bubble_size[1]} at final position ({forced_x}, {forced_y})")
            print(f"✅ Successfully rendered bubble at ({forced_x}, {forced_y})")
        except AttributeError:
            # Fallback to original method if new method doesn't exist
            result = renderer.render_text_bubble(result, bubble, panel_width, panel_height)
            print(f"✅ Rendered bubble {i} using fallback method")
        except Exception as e:
            print(f"❌ Error rendering text bubble {i}: {e}")
            # Continue with next bubble instead of failing completely
    
    return result


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
    
    return best_match

def create_comic_sheet(panels_with_images: List[Tuple[Image.Image, List[Dialogue]]], character_names: List[str] = None) -> Tuple[Image.Image, List[dict]]:
    """
    Creates a multi-panel comic sheet.
    Layout for 6 panels with dynamic layout structure.
    """
    num_panels = len(panels_with_images)
    if num_panels == 0:
        return Image.new('RGB', (800, 600), color='gray'), [] # Return empty gray image and empty locations

    panel_locations = []

    if num_panels == 6:
        gutter = 30
        outer_margin = 40

        # NARRATIVE-FOCUSED 6-PANEL LAYOUT WITH SDXL DIMENSIONS
        # Each panel tailored for storytelling beats using valid SDXL sizes

        panel1_w, panel1_h = 768, 1344     # Strong vertical intro (scene setup / entry)
        panel2_w, panel2_h = 1344, 768 
            # Establishing shot or zoom (world / space)
        panel3_w, panel3_h = 1344, 768      # Super wide reveal or climax (turning point)
        panel4_w, panel4_h = 1536, 640      # Aftermath (character response / world state)
        panel5_w, panel5_h = 1216, 832     # Emotional close-up / reflection
        panel6_w, panel6_h = 1216, 832    # Closing beat / ambiguity / full stop

        # Calculate sheet size based on the narrative layout:
        # Layout structure:
        # [ Panel 1 (wide) ]    [ Panel 2 ]
        #                       [ Panel 3 ]
        # [ Panel 4 (wide)              ]
        # [ Panel 5 ][ Panel 6 ]
        
        # Calculate positions for narrative layout
        top_row_height = max(panel1_h, panel2_h + panel3_h + gutter)
        
        # Fixed width calculation to ensure all panels fit
        extra_right_spacing = 80  # Additional space for moving panels 2&3 right (match positioning)
        right_column_width = max(panel2_w, panel3_w)  # Width of right column (panels 2&3)
        wide_panel_width = panel4_w  # Width of wide panel 4
        bottom_row_width = panel5_w + panel6_w + gutter  # Width of bottom row (panels 5&6)
        
        # OPTIMIZED sheet size calculation for better visibility
        # Make layout more compact - limit maximum width for better viewing
        max_sheet_width = 2400  # Increased width to accommodate wider panel 1 and extra spacing
        
        content_width = max(
            panel1_w + right_column_width + gutter + extra_right_spacing,  # Top row: Panel 1 + spacing + (Panel 2/3)
            wide_panel_width,  # Middle row: Panel 4
            bottom_row_width   # Bottom row: Panel 5 + Panel 6
        )
        
        # If content is too wide, scale it down proportionally
        if content_width > max_sheet_width:
            scale_factor = max_sheet_width / content_width
            # Reduce panel sizes proportionally but keep minimum readable size
            scale_factor = max(scale_factor, 0.7)  # Don't scale smaller than 70%
            print(f"🔧 Scaling layout by {scale_factor:.2f} to fit within {max_sheet_width}px width")
        else:
            scale_factor = 1.0
        
        sheet_width = min(content_width + 2*outer_margin, max_sheet_width + 2*outer_margin)
        
        # Sheet height calculation - OPTIMIZED for better viewing
        sheet_height = outer_margin + max(panel1_h, panel2_h + panel3_h + gutter) + panel4_h + max(panel5_h, panel6_h) + 3*gutter + outer_margin
        
        print(f"🔧 Layout calculation:")
        print(f"   Top row height: {top_row_height}")
        print(f"   Content width: {content_width}")
        print(f"   Bottom row width: {bottom_row_width}")
        print(f"   Sheet dimensions: {sheet_width}x{sheet_height}")
        print(f"   Individual panel sizes:")
        print(f"     Panel 1: {panel1_w}x{panel1_h}")  
        print(f"     Panel 2: {panel2_w}x{panel2_h}")
        print(f"     Panel 3: {panel3_w}x{panel3_h}")
        print(f"     Panel 4: {panel4_w}x{panel4_h}")
        print(f"     Panel 5: {panel5_w}x{panel5_h}")
        print(f"     Panel 6: {panel6_w}x{panel6_h}")
        
        # Create comic sheet with calculated dimensions
        comic_sheet = Image.new('RGB', (sheet_width, sheet_height), color='white')
        draw = ImageDraw.Draw(comic_sheet)

        print(f"📐 Comic sheet dimensions: {sheet_width}x{sheet_height}")
        print(f"📖 Narrative layout: Setup(1) → Tension(2) → Reveal(3) → Action(4) → Fallout(5) → Resolution(6)")
        
        # Apply scaling if needed for better viewing
        if scale_factor < 1.0:
            panel1_w = int(panel1_w * scale_factor)
            panel1_h = int(panel1_h * scale_factor)
            panel2_w = int(panel2_w * scale_factor)
            panel2_h = int(panel2_h * scale_factor)
            panel3_w = int(panel3_w * scale_factor)
            panel3_h = int(panel3_h * scale_factor)
            panel4_w = int(panel4_w * scale_factor)
            panel4_h = int(panel4_h * scale_factor)
            panel5_w = int(panel5_w * scale_factor)
            panel5_h = int(panel5_h * scale_factor)
            panel6_w = int(panel6_w * scale_factor)
            panel6_h = int(panel6_h * scale_factor)
            print(f"🔧 Applied scaling - new panel sizes:")
            print(f"   Panel 1: {panel1_w}×{panel1_h}, Panel 2: {panel2_w}×{panel2_h}")
        
        # Calculate exact positions for each panel - OPTIMIZED positioning
        panel1_x = outer_margin
        panel1_y = outer_margin
        
        # Add extra spacing to move panels 2 & 3 further right
        extra_right_spacing = 80  # Additional space to push panels 2&3 right
        panel2_x = outer_margin + panel1_w + gutter + extra_right_spacing
        panel2_y = outer_margin
        
        panel3_x = outer_margin + panel1_w + gutter + extra_right_spacing
        panel3_y = outer_margin + panel2_h + gutter
        
        # DEBUG: Verify panel 2 & 3 positions 
        print(f"🔍 CRITICAL DEBUG - Panel 2 & 3 positioning:")
        print(f"   Panel 1: {panel1_w}×{panel1_h} at ({panel1_x}, {panel1_y})")
        print(f"   Panel 2: {panel2_w}×{panel2_h} at ({panel2_x}, {panel2_y}) - ends at ({panel2_x + panel2_w}, {panel2_y + panel2_h})")
        print(f"   Panel 3: {panel3_w}×{panel3_h} at ({panel3_x}, {panel3_y}) - ends at ({panel3_x + panel3_w}, {panel3_y + panel3_h})")
        print(f"   Sheet will be: {sheet_width}×{sheet_height}")
        print(f"   Panel 2 fits horizontally: {panel2_x + panel2_w <= sheet_width}")
        print(f"   Panel 3 fits horizontally: {panel3_x + panel3_w <= sheet_width}")
        
        panel4_x = outer_margin
        panel4_y = outer_margin + max(panel1_h, panel2_h + panel3_h + gutter) + gutter
        
        panel5_x = outer_margin
        panel5_y = panel4_y + panel4_h + gutter
        
        panel6_x = outer_margin + panel5_w + gutter
        panel6_y = panel4_y + panel4_h + gutter
        
        print(f"🎯 Panel positions:")
        print(f"   Panel 1: ({panel1_x}, {panel1_y}) size {panel1_w}x{panel1_h} -> ends at ({panel1_x + panel1_w}, {panel1_y + panel1_h})")
        print(f"   Panel 2: ({panel2_x}, {panel2_y}) size {panel2_w}x{panel2_h} -> ends at ({panel2_x + panel2_w}, {panel2_y + panel2_h})")
        print(f"   Panel 3: ({panel3_x}, {panel3_y}) size {panel3_w}x{panel3_h} -> ends at ({panel3_x + panel3_w}, {panel3_y + panel3_h})")
        print(f"   Panel 4: ({panel4_x}, {panel4_y}) size {panel4_w}x{panel4_h} -> ends at ({panel4_x + panel4_w}, {panel4_y + panel4_h})")
        print(f"   Panel 5: ({panel5_x}, {panel5_y}) size {panel5_w}x{panel5_h} -> ends at ({panel5_x + panel5_w}, {panel5_y + panel5_h})")
        print(f"   Panel 6: ({panel6_x}, {panel6_y}) size {panel6_w}x{panel6_h} -> ends at ({panel6_x + panel6_w}, {panel6_y + panel6_h})")
        print(f"   Sheet size: {sheet_width}x{sheet_height}")
        
        # Check if any panels extend beyond sheet bounds
        panels_info = [
            (1, panel1_x, panel1_y, panel1_w, panel1_h),
            (2, panel2_x, panel2_y, panel2_w, panel2_h),
            (3, panel3_x, panel3_y, panel3_w, panel3_h),
            (4, panel4_x, panel4_y, panel4_w, panel4_h),
            (5, panel5_x, panel5_y, panel5_w, panel5_h),
            (6, panel6_x, panel6_y, panel6_w, panel6_h)
        ]
        
        for panel_num, x, y, w, h in panels_info:
            if x + w > sheet_width or y + h > sheet_height:
                print(f"⚠️ WARNING: Panel {panel_num} extends beyond sheet bounds!")
                print(f"   Panel {panel_num} ends at ({x + w}, {y + h}) but sheet is {sheet_width}x{sheet_height}")
            else:
                print(f"✅ Panel {panel_num} fits within sheet bounds")
        
        # Layout configuration using calculated positions
        configs = [
            # Panel 1: Wide Top-Left Panel - Initial Scene Setting
            {"x": panel1_x, "y": panel1_y, "width": panel1_w, "height": panel1_h},
            # Panel 2: Top Right Portrait - Character Focus/Inciting Incident  
            {"x": panel2_x, "y": panel2_y, "width": panel2_w, "height": panel2_h},
            # Panel 3: Bottom Right Portrait - Reaction/Echo
            {"x": panel3_x, "y": panel3_y, "width": panel3_w, "height": panel3_h},
            # Panel 4: Wide Middle Panel - Peak action
            {"x": panel4_x, "y": panel4_y, "width": panel4_w, "height": panel4_h},
            # Panel 5: Bottom Left - Emotional fallout
            {"x": panel5_x, "y": panel5_y, "width": panel5_w, "height": panel5_h},
            # Panel 6: Bottom Right - Resolution/humor
            {"x": panel6_x, "y": panel6_y, "width": panel6_w, "height": panel6_h}
        ]

        # Process each panel with the correct target dimensions
        print(f"🎬 Processing {len(panels_with_images)} panels, have {len(configs)} configurations")
        print(f"🔍 DEBUGGING: panels_with_images count = {len(panels_with_images)}")
        print(f"🔍 DEBUGGING: configs count = {len(configs)}")
        
        if len(panels_with_images) != 6:
            print(f"❌ CRITICAL ERROR: Expected 6 panels but got {len(panels_with_images)}!")
        
        if len(configs) != 6:
            print(f"❌ CRITICAL ERROR: Expected 6 configs but got {len(configs)}!")
        
        for idx, (panel_img, dialogues) in enumerate(panels_with_images):
            print(f"🎯 Processing panel {idx+1}/{len(panels_with_images)}...")
            
            if idx < len(configs):
                config = configs[idx]
                x, y = config["x"], config["y"]
                panel_w, panel_h = config["width"], config["height"]

                print(f"   Panel {idx+1} at position ({x}, {y}) with dimensions {panel_w}x{panel_h}")
                print(f"   Panel {idx+1} will end at ({x + panel_w}, {y + panel_h})")
                
                # Check if position is within sheet bounds
                if x + panel_w > sheet_width or y + panel_h > sheet_height:
                    print(f"⚠️ WARNING: Panel {idx+1} extends beyond sheet bounds!")
                    print(f"   Panel ends at ({x + panel_w}, {y + panel_h}) but sheet is {sheet_width}x{sheet_height}")
                    print(f"   X overflow: {max(0, (x + panel_w) - sheet_width)} pixels")
                    print(f"   Y overflow: {max(0, (y + panel_h) - sheet_height)} pixels")
                else:
                    print(f"✅ Panel {idx+1} fits within sheet bounds")

                # Process panel with dialogues using ACTUAL panel dimensions
                processed_img = add_dialogues_and_sfx_to_panel(
                    panel_img, dialogues, panel_w, panel_h, character_names
                )
                
                # Resize the processed panel to fit the layout
                resized_panel = processed_img.resize((panel_w, panel_h), Image.Resampling.LANCZOS)
                
                # CRITICAL DEBUG: Special attention to panels 2 & 3
                if idx + 1 in [2, 3]:
                    print(f"🚨 CRITICAL: About to paste panel {idx+1} at ({x}, {y})")
                    print(f"   Panel {idx+1} size after resize: {resized_panel.size}")
                    print(f"   Comic sheet size: {comic_sheet.size}")
                    print(f"   Paste coordinates: ({x}, {y})")
                    print(f"   Panel will occupy area: ({x}, {y}) to ({x + panel_w}, {y + panel_h})")
                
                comic_sheet.paste(resized_panel, (x, y))
                
                if idx + 1 in [2, 3]:
                    print(f"✅ CRITICAL: Panel {idx+1} successfully pasted!")

                # Draw panel border
                border_coords = (x - 2, y - 2, x + panel_w + 2, y + panel_h + 2)
                draw.rectangle(border_coords, outline="black", width=3)
                
                if idx + 1 in [2, 3]:
                    print(f"✅ CRITICAL: Panel {idx+1} border drawn at {border_coords}")

                panel_locations.append({
                    "panel": idx + 1,
                    "x": x,
                    "y": y,
                    "width": panel_w,
                    "height": panel_h
                })
                
                print(f"✅ Panel {idx+1} successfully placed at ({x}, {y}) - border at {border_coords}")
            else:
                print(f"❌ ERROR: Panel {idx+1} has no layout configuration! Only {len(configs)} configs available.")
                print(f"❌ This panel will NOT be included in the final comic!")
        
        print(f"📊 FINAL SUMMARY:")
        print(f"   Generated panels: {len(panels_with_images)}")
        print(f"   Placed panels: {len(panel_locations)}")
        print(f"   Missing panels: {len(panels_with_images) - len(panel_locations)}")

    else:
        # Fallback for other panel counts using simple grid
        cols = 2 if num_panels <= 4 else 3
        rows = math.ceil(num_panels / cols)

        gutter = 20  # Increased from 15
        outer_margin = 35  # Increased from 25
        sheet_target_width = 2400  # Increased from 1600
        calculated_panel_width = (sheet_target_width - (cols + 1) * gutter - 2 * outer_margin) // cols
        calculated_panel_height = int(calculated_panel_width * 0.75)  # 4:3 aspect ratio

        sheet_width = cols * calculated_panel_width + (cols + 1) * gutter + 2 * outer_margin
        sheet_height = rows * calculated_panel_height + (rows + 1) * gutter + 2 * outer_margin

        comic_sheet = Image.new('RGB', (sheet_width, sheet_height), 'white')
        draw = ImageDraw.Draw(comic_sheet)

        # Map dimensions to allowed SDXL dimensions for Stable Diffusion compatibility
        calculated_panel_width, calculated_panel_height = map_to_allowed_sdxl_dimensions(calculated_panel_width, calculated_panel_height)

        # Process each panel with correct dimensions
        for idx, (panel_img, dialogues) in enumerate(panels_with_images):
            row = idx // cols
            col = idx % cols
            x = outer_margin + col * (calculated_panel_width + gutter) + gutter
            y = outer_margin + row * (calculated_panel_height + gutter) + gutter

            # Process panel with dialogues using ACTUAL panel dimensions
            print(f"🎯 Processing panel {idx+1} with dimensions {calculated_panel_width}x{calculated_panel_height}")
            processed_img = add_dialogues_and_sfx_to_panel(
                panel_img, dialogues, calculated_panel_width, calculated_panel_height, character_names
            )

            resized_img = processed_img.resize((calculated_panel_width, calculated_panel_height), Image.Resampling.LANCZOS)
            comic_sheet.paste(resized_img, (x, y))

            # Add border
            border_coords = (x-2, y-2, x + calculated_panel_width + 2, y + calculated_panel_height + 2)
            draw.rectangle(border_coords, outline="black", width=3)

            panel_locations.append({
                "panel": idx + 1,
                "x": x,
                "y": y,
                "width": calculated_panel_width,
                "height": calculated_panel_height
            })

    return comic_sheet, panel_locations


# Keep create_simple_comic_grid for pure fallback, but create_comic_sheet should be primary
def create_simple_comic_grid(images):
    """Create a simple comic grid layout as fallback when more complex sheet creation fails"""
    try:
        num_images = len(images)
        
        if num_images == 8: # Handle 8 panels for simple grid fallback
            panel_size = (600, 450) # Increased from (400, 300)
            cols = 4
            rows = 2
            grid_width = panel_size[0] * cols + (cols + 1) * 15
            grid_height = panel_size[1] * rows + (rows + 1) * 15
            comic_grid = Image.new('RGB', (grid_width, grid_height), 'white')
            
            positions = []
            for i in range(num_images):
                col = i % cols
                row = i // cols
                x = col * (panel_size[0] + 15) + 15
                y = row * (panel_size[1] + 15) + 15
                positions.append((x, y))

        elif num_images == 5:
            # Special 5-panel layout: 2 on top, 3 on bottom
            panel_size = (525, 420)  # Increased from (350, 280)
            grid_width = panel_size[0] * 3 + 60  # 3 panels wide with spacing
            grid_height = panel_size[1] * 2 + 45  # 2 panels high with spacing
            comic_grid = Image.new('RGB', (grid_width, grid_height), 'white')

            # Top row: 2 panels centered
            positions = [
                (panel_size[0] // 2 + 15, 15),  # Top left (centered)
                (panel_size[0] * 1.5 + 45, 15),  # Top right (centered)
                (15, panel_size[1] + 30),  # Bottom left
                (panel_size[0] + 30, panel_size[1] + 30),  # Bottom center
                (panel_size[0] * 2 + 45, panel_size[1] + 30)   # Bottom right
            ]
        elif num_images == 6:
            # 3x2 grid
            panel_size = (450, 375)  # Increased from (300, 250)
            grid_width = panel_size[0] * 3 + 60
            grid_height = panel_size[1] * 2 + 45
            comic_grid = Image.new('RGB', (grid_width, grid_height), 'white')

            positions = []
            for i in range(6):
                col = i % 3
                row = i // 3
                x = col * (panel_size[0] + 15) + 15
                y = row * (panel_size[1] + 15) + 15
                positions.append((x, y))
        else:
            # Default grid for other numbers
            panel_size = (600, 450)  # Increased from (400, 300)
            cols = 2 if num_images <= 4 else 3
            rows = math.ceil(num_images / cols) # Use ceil to ensure all panels fit

            grid_width = panel_size[0] * cols + (cols + 1) * 15
            grid_height = panel_size[1] * rows + (rows + 1) * 15
            comic_grid = Image.new('RGB', (grid_width, grid_height), 'white')

            positions = []
            for i in range(num_images):
                col = i % cols
                row = i // cols
                x = col * (panel_size[0] + 15) + 15
                y = row * (panel_size[1] + 15) + 15
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

def extract_character_details(frame_description: str, character_name: str) -> str:
    """
    Extracts and standardizes rich visual details about a character from a frame description.
    Focuses on unique and consistent features.
    """
    description_lower = frame_description.lower()
    details = []
    
    # 1. Core Identity & Appearance
    details.append(f"a person named {character_name}") # Always include the name tag for LoRA if available
    
    # Gender (inference, if not explicit, skip)
    if "man" in description_lower or "male" in description_lower or "he " in description_lower:
        details.append("male")
    elif "woman" in description_lower or "female" in description_lower or "she " in description_lower:
        details.append("female")
    
    # Age/Build (more specific keywords)
    age_keywords = {
        "child": ["child", "kid", "youngster", "boy", "girl"],
        "teenager": ["teenager", "teen", "adolescent"],
        "young adult": ["young woman", "young man", "youth", "young adult"],
        "middle-aged": ["middle-aged"],
        "elderly": ["old man", "old woman", "elderly", "senior"]
    }
    for age_group, kws in age_keywords.items():
        if any(kw in description_lower for kw in kws):
            details.append(age_group)
            break
            
    build_keywords = ["slim", "athletic", "muscular", "stocky", "petite", "curvy"]
    for build in build_keywords:
        if build in description_lower:
            details.append(build)
            break

    # Hair Details (color, style, length) - Prioritize specific combinations
    hair_descriptors = [
        ("long black hair", "long black hair"), ("short black hair", "short black hair"),
        ("curly black hair", "curly black hair"), ("straight black hair", "straight black hair"),
        ("wavy black hair", "wavy black hair"), ("spiky black hair", "spiky black hair"),
        ("long blonde hair", "long blonde hair"), ("short blonde hair", "short blonde hair"),
        ("curly blonde hair", "curly blonde hair"), ("straight blonde hair", "straight blonde hair"),
        ("long brown hair", "long brown hair"), ("short brown hair", "short brown hair"),
        ("red hair", "red hair"), ("ginger hair", "ginger hair"), ("white hair", "white hair"),
        ("gray hair", "gray hair"), ("blue hair", "blue hair"), ("green hair", "green hair"),
        ("pink hair", "pink hair"), ("purple hair", "purple hair"),
        ("bald", "bald"), ("receding hairline", "receding hairline")
    ]
    for pattern, desc in hair_descriptors:
        if pattern in description_lower:
            details.append(desc)
            break
    
    # Eyes (color, shape)
    eye_colors = ["blue eyes", "brown eyes", "green eyes", "hazel eyes", "grey eyes"]
    for color in eye_colors:
        if color in description_lower:
            details.append(color)
            break
    if "large eyes" in description_lower: details.append("large eyes")
    if "small eyes" in description_lower: details.append("small eyes")

    # Facial Features
    facial_features = ["beard", "mustache", "glasses", "freckles", "scar", "dimples"]
    for feature in facial_features:
        if feature in description_lower:
            details.append(feature)
    if "clean-shaven" in description_lower: details.append("clean-shaven")
    if "glowing eyes" in description_lower: details.append("glowing eyes")


    # Clothing (more specific items and patterns) - extract up to 3 key items
    clothing_keywords = {
        "shirt": ["shirt", "t-shirt", "button-up"],
        "jacket": ["jacket", "coat", "hoodie", "blazer"],
        "pants": ["pants", "jeans", "trousers", "leggings"],
        "dress": ["dress", "gown"],
        "skirt": ["skirt"],
        "armor": ["armor", "suit of armor"],
        "uniform": ["uniform", "suit"],
        "cape": ["cape", "cloak"],
        "hat": ["hat", "cap", "beanie"],
        "boots": ["boots", "shoes", "sneakers"],
        "gloves": ["gloves"],
        "scarf": ["scarf"],
        "jewelry": ["necklace", "ring", "earrings", "jewelry"]
    }
    
    extracted_clothing = []
    clothing_count = 0
    for item_type, kws in clothing_keywords.items():
        if clothing_count >= 3: break # Limit number of clothing items
        for kw in kws:
            if kw in description_lower:
                # Try to get color if available for this specific item
                color_found = False
                for color in ["red", "blue", "green", "black", "white", "yellow", "purple", "orange", "grey", "brown", "gold", "silver"]:
                    if f"{color} {kw}" in description_lower:
                        extracted_clothing.append(f"{color} {kw}")
                        color_found = True
                        break
                if not color_found:
                    extracted_clothing.append(kw)
                clothing_count += 1
                break # Move to next item_type

    if extracted_clothing:
        details.extend(extracted_clothing)

    # Distinguishing marks/props always carried
    distinguishing_marks = ["tattoo", "piercing", "specific weapon", "unique gadget", "scar"]
    for mark in distinguishing_marks:
        if mark in description_lower:
            details.append(mark)

    # Final combined description for LoRA
    if len(details) > 1: # Beyond just the name
        # Remove duplicates while preserving order
        unique_details = []
        [unique_details.append(item) for item in details if item not in unique_details]
        character_desc = ", ".join(unique_details)
    else:
        character_desc = f"a person named {character_name}, distinctive and consistent appearance"
    
    # Ensure the character's name is always at the very start for LoRA trigger
    if not character_desc.startswith(f"{character_name}: "):
        character_desc = f"{character_name}: {character_desc}"

    return character_desc