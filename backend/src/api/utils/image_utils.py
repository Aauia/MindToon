
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
from .comic_text_utils import ComicTextRenderer, TextBubble
from .font_utils import get_system_font, wrap_text_pil, draw_text_with_outline

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

def add_dialogues_and_sfx_to_panel(
    panel_image: Image.Image,
    dialogues: List[Dialogue],
    panel_width: int,
    panel_height: int,
    character_names: List[str] = None
) -> Image.Image:
    """
    Adds a single wide speech bubble at the bottom center of the panel, combining all dialogue lines.
    The bubble is horizontally wide, vertically compact, and avoids overlapping character faces.
    """
 
    if not dialogues:
        return panel_image

    # Combine all dialogue lines, preserving speaker names
    combined_lines = []
    for dialogue in dialogues:
        if hasattr(dialogue, 'speaker') and dialogue.speaker:
            combined_lines.append(f"{dialogue.speaker}: {dialogue.text}")
        else:
            combined_lines.append(dialogue.text)
    combined_text = "\n".join(combined_lines)

    renderer = ComicTextRenderer()
    result = panel_image.copy()

    # Use a wide, compact bubble style
    bubble_style = renderer.default_styles["speech"]
    # Make font size dynamic and readable
    bubble_style.font_size = max(18, int(panel_height * 0.06))  # Dynamic, readable font size
    bubble_style.padding = max(5, int(panel_height * 0.03))
    bubble_style.corner_radius = 0

    # Calculate bubble size for the combined text
    max_bubble_width = int(panel_width * 0.80)  # Reduced from 85% to 60% for narrower bubbles
    max_bubble_height = int(panel_height * 0.15)  # Increased from 15% to 35% for more text
    bubble_width, bubble_height = renderer.calculate_bubble_size(combined_text, bubble_style, max_bubble_width)
    bubble_width = min(bubble_width, max_bubble_width)
    bubble_height = min(bubble_height, max_bubble_height)
    
    print(f"🔍 DEBUG: Panel size: {panel_width}x{panel_height}")
    print(f"🔍 DEBUG: Max bubble size: {max_bubble_width}x{max_bubble_height}")
    print(f"🔍 DEBUG: Calculated bubble size: {bubble_width}x{bubble_height}")
    print(f"🔍 DEBUG: Combined text: '{combined_text[:50]}...'")

    # Bottom edge positioning with margin to stay within panel bounds
    bubble_x = (panel_width - bubble_width) // 2  # Horizontally centered
    bubble_y = max(0, panel_height - bubble_height - 10)  # 10px margin from bottom, but don't go below 0
    
    # ALTERNATIVE POSITIONING OPTIONS (uncomment to use):
    # bubble_x = 20  # Left-aligned, 20px from left edge
    # bubble_x = panel_width - bubble_width - 20  # Right-aligned, 20px from right edge
    # bubble_y = (panel_height - bubble_height) // 2  # Vertically centered
    # bubble_y = 20  # Top-aligned, 20px from top
    # bubble_y = panel_height - bubble_height - 50  # Higher from bottom (50px margin)

    print(f"🔍 DEBUG: Bubble position: ({bubble_x}, {bubble_y})")

    # Create a TextBubble for the combined text
    bubble = TextBubble(
        text=combined_text,
        position=(bubble_x, bubble_y),
        bubble_type="speech",
        emotion="normal",
        speaker_position="bottom",
        style=bubble_style
    )
    
    # Set the calculated size on the bubble so renderer doesn't recalculate it
    bubble._calculated_size = (bubble_width, bubble_height)

    # Render the single bubble at the specified position and size
    result = renderer.render_text_bubble_at_position(result, bubble, bubble_x, bubble_y, panel_width, panel_height)
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
    Layout for 6 panels, specifically Variant 15: "Dominant Panel with Visual Inset".
    """
    num_panels = len(panels_with_images)
    if num_panels == 0:
        return Image.new('RGB', (800, 600), color='gray'), []

    panel_locations = []

    if num_panels == 6:
        gutter = 30
        outer_margin = 40

        # --- VARIANT 15: Dominant Panel with Visual Inset ---
        # Overall sheet dimensions targeting a square SDXL resolution
        sheet_target_width = 1024 # SDXL square width
        sheet_target_height = 1024 # SDXL square height

        # Calculate available content space
        content_width_area = sheet_target_width - (2 * outer_margin)
        content_height_area = sheet_target_height - (2 * outer_margin)

        # Panel 1 (Dominant Left Panel)
        # It takes up about 60% of the width and about 70% of the height
        panel1_w = int(content_width_area * 0.6) - (gutter // 2) # Account for gutter
        panel1_h = int(content_height_area * 0.7) - (gutter // 2) # Account for gutter

        # Remaining width for right column panels (2, 3, 4)
        right_col_w = content_width_area - panel1_w - gutter

        # Remaining height for bottom row panels (5, 6)
        bottom_row_h = content_height_area - panel1_h - gutter

        # Panels 2, 3, 4 (Stacked on Right of Panel 1)
        panel2_w = right_col_w
        panel3_w = right_col_w
        panel4_w = right_col_w
        
        # 3 panels vertically, 2 gutters between them
        panel2_h = (panel1_h - (2 * gutter)) // 3
        panel3_h = panel2_h
        panel4_h = panel2_h

        # Panels 5, 6 (Bottom Row)
        # These span the full content width below Panel 1 and the right stack
        panel5_w = (content_width_area - gutter) // 2
        panel6_w = panel5_w
        
        panel5_h = bottom_row_h
        panel6_h = bottom_row_h
        
        # Final sheet dimensions
        sheet_width = sheet_target_width
        sheet_height = sheet_target_height
        
        # Create comic sheet with calculated dimensions
        comic_sheet = Image.new('RGB', (sheet_width, sheet_height), color='white')
        draw = ImageDraw.Draw(comic_sheet)

        print(f"\n--- Variant 15: Dominant Panel with Visual Inset ---")
        print(f"📐 Comic sheet dimensions: {sheet_width}x{sheet_height} (Targeted SDXL)")
        print(f"   Calculated content area: {content_width_area}x{content_height_area}")
        print(f"   Individual panel sizes:")
        print(f"     Panel 1 (Dominant): {panel1_w}x{panel1_h}")  
        print(f"     Panels 2,3,4 (Right Stack): {panel2_w}x{panel2_h}")
        print(f"     Panels 5,6 (Bottom Row): {panel5_w}x{panel5_h}")
        
        # Calculate exact positions for each panel
        # Panel 1
        panel1_x = outer_margin
        panel1_y = outer_margin
        
        # Panels 2, 3, 4 (Right Column)
        panel2_x = outer_margin + panel1_w + gutter
        panel2_y = outer_margin
        
        panel3_x = panel2_x
        panel3_y = outer_margin + panel2_h + gutter
        
        panel4_x = panel2_x
        panel4_y = outer_margin + (2 * panel2_h) + (2 * gutter)
        
        # Panels 5, 6 (Bottom Row)
        panel5_x = outer_margin
        panel5_y = outer_margin + panel1_h + gutter # Below Panel 1
        
        panel6_x = outer_margin + panel5_w + gutter
        panel6_y = panel5_y # Same y as Panel 5
        
        print(f"🎯 Panel positions:")
        print(f"   Panel 1: ({panel1_x}, {panel1_y}) size {panel1_w}x{panel1_h} -> ends at ({panel1_x + panel1_w}, {panel1_y + panel1_h})")
        print(f"   Panel 2: ({panel2_x}, {panel2_y}) size {panel2_w}x{panel2_h} -> ends at ({panel2_x + panel2_w}, {panel2_y + panel2_h})")
        print(f"   Panel 3: ({panel3_x}, {panel3_y}) size {panel3_w}x{panel3_h} -> ends at ({panel3_x + panel3_w}, {panel3_y + panel3_h})")
        print(f"   Panel 4: ({panel4_x}, {panel4_y}) size {panel4_w}x{panel4_h} -> ends at ({panel4_x + panel4_w}, {panel4_y + panel4_h})")
        print(f"   Panel 5: ({panel5_x}, {panel5_y}) size {panel5_w}x{panel5_h} -> ends at ({panel5_x + panel5_w}, {panel5_y + panel5_h})")
        print(f"   Panel 6: ({panel6_x}, {panel6_y}) size {panel6_w}x{panel6_h} -> ends at ({panel6_x + panel6_w}, {panel6_y + panel6_h})")
        
        # Validate panel fitting within sheet (debug prints)
        panels_info = [
            (1, panel1_x, panel1_y, panel1_w, panel1_h),
            (2, panel2_x, panel2_y, panel2_w, panel2_h),
            (3, panel3_x, panel3_y, panel3_w, panel3_h),
            (4, panel4_x, panel4_y, panel4_w, panel4_h),
            (5, panel5_x, panel5_y, panel5_w, panel5_h),
            (6, panel6_x, panel6_y, panel6_w, panel6_h)
        ]
        for panel_num, x, y, w, h in panels_info:
            if x < outer_margin - 5 or y < outer_margin - 5 or \
               x + w > sheet_width - (outer_margin - 5) or \
               y + h > sheet_height - (outer_margin - 5):
                print(f"⚠️ WARNING: Panel {panel_num} seems to extend or be too close to outer bounds!")
                print(f"   Panel {panel_num} bounds: ({x}, {y}) to ({x+w}, {y+h}). Sheet: {sheet_width}x{sheet_height}")
            else:
                print(f"✅ Panel {panel_num} fits well within sheet bounds.")


        # Layout configuration using calculated positions and dimensions
        configs = [
            {"x": panel1_x, "y": panel1_y, "width": panel1_w, "height": panel1_h}, # Panel 1
            {"x": panel2_x, "y": panel2_y, "width": panel2_w, "height": panel2_h}, # Panel 2
            {"x": panel3_x, "y": panel3_y, "width": panel3_w, "height": panel3_h}, # Panel 3
            {"x": panel4_x, "y": panel4_y, "width": panel4_w, "height": panel4_h}, # Panel 4
            {"x": panel5_x, "y": panel5_y, "width": panel5_w, "height": panel5_h}, # Panel 5
            {"x": panel6_x, "y": panel6_y, "width": panel6_w, "height": panel6_h}  # Panel 6
        ]

        if len(panels_with_images) != 6 or len(configs) != 6:
            print(f"❌ CRITICAL ERROR: Panel count mismatch. Expected 6, got {len(panels_with_images)} images and {len(configs)} configs.")
            return Image.new('RGB', (sheet_width, sheet_height), color='red'), []
        
        for idx, (panel_img, dialogues) in enumerate(panels_with_images):
            config = configs[idx]
            x, y = config["x"], config["y"]
            panel_w, panel_h = config["width"], config["height"]

            print(f"🎨 Placing Panel {idx+1}: Target {panel_w}x{panel_h} at ({x}, {y})")

            # First resize the panel image to target size
            resized_panel = panel_img.resize((panel_w, panel_h), Image.Resampling.LANCZOS)
            
            # Then add bubbles to the resized panel
            processed_img = add_dialogues_and_sfx_to_panel(
                resized_panel, dialogues, panel_w, panel_h, character_names
            )
            
            comic_sheet.paste(processed_img, (x, y))
            
            # Draw panel border
            border_coords = (x - 2, y - 2, x + panel_w + 2, y + panel_h + 2)
            draw.rectangle(border_coords, outline="black", width=3)
            
            panel_locations.append({
                "panel": idx + 1,
                "x": x,
                "y": y,
                "width": panel_w,
                "height": panel_h
            })
            print(f"✅ Panel {idx+1} successfully placed.")

    else: # Fallback for other panel counts (from original code)
        cols = 2 if num_panels <= 4 else 3
        rows = math.ceil(num_panels / cols)

        gutter = 30
        outer_margin = 40
        sheet_target_width = 2400 
        calculated_panel_width = (sheet_target_width - (cols + 1) * gutter - 2 * outer_margin) // cols
        calculated_panel_height = int(calculated_panel_width * 0.75) 

        sheet_width = cols * calculated_panel_width + (cols + 1) * gutter + 2 * outer_margin
        sheet_height = rows * calculated_panel_height + (rows + 1) * gutter + 2 * outer_margin

        comic_sheet = Image.new('RGB', (sheet_width, sheet_height), 'white')
        draw = ImageDraw.Draw(comic_sheet)

        for idx, (panel_img, dialogues) in enumerate(panels_with_images):
            row = idx // cols
            col = idx % cols
            x = outer_margin + col * (calculated_panel_width + gutter) + gutter
            y = outer_margin + row * (calculated_panel_height + gutter) + gutter

            processed_img = add_dialogues_and_sfx_to_panel(
                panel_img, dialogues, calculated_panel_width, calculated_panel_height, character_names
            )

            resized_img = processed_img.resize((calculated_panel_width, calculated_panel_height), Image.Resampling.LANCZOS)
            comic_sheet.paste(resized_img, (x, y))

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