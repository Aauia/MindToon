from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple
from api.ai.schemas import Dialogue # Make sure to import the updated Dialogue schema
import platform
import os

# Define fonts - Mac-compatible system fonts
def get_system_font(font_name: str, size: int, fallback_size: int = 20):
    """Get system font with Mac compatibility"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        font_paths = {
            "arial": "/Library/Fonts/Arial.ttf",
            "arial_bold": "/Library/Fonts/Arial Bold.ttf",
            "helvetica": "/System/Library/Fonts/Helvetica.ttc",
            "times": "/Library/Fonts/Times New Roman.ttf"
        }
    elif system == "Windows":
        font_paths = {
            "arial": "arial.ttf",
            "arial_bold": "arialbd.ttf",
            "helvetica": "arial.ttf",
            "times": "times.ttf"
        }
    else:  # Linux
        font_paths = {
            "arial": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "arial_bold": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "helvetica": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "times": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
        }
    
    try:
        if font_name in font_paths and os.path.exists(font_paths[font_name]):
            return ImageFont.truetype(font_paths[font_name], size)
        else:
            # Try default system font
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size) if system == "Darwin" else ImageFont.load_default()
    except (IOError, OSError):
        print(f"Could not load font {font_name}, using default.")
        return ImageFont.load_default()

# Load fonts with Mac compatibility
try:
    SPEECH_FONT = get_system_font("helvetica", 24)
    THOUGHT_FONT = get_system_font("helvetica", 24)
    SFX_FONT = get_system_font("arial_bold", 48)
    NARRATION_FONT = get_system_font("times", 20)
    SCREAM_FONT = get_system_font("arial_bold", 48)
except Exception as e:
    print(f"Font loading error: {e}, falling back to default.")
    SPEECH_FONT = ImageFont.load_default()
    THOUGHT_FONT = ImageFont.load_default()
    SFX_FONT = ImageFont.load_default()
    NARRATION_FONT = ImageFont.load_default()
    SCREAM_FONT = ImageFont.load_default()


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """Wrap text to fit within a specified width"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                lines.append(word)
    
    if current_line:
        lines.append(current_line)
    
    return lines


def draw_speech_bubble(draw: ImageDraw.Draw, text: str, position: Tuple[int, int], font: ImageFont.FreeTypeFont, max_width: int = 180, fill_color: str = "white", text_color: str = "black", border_color: str = "black"):
    """Draw a speech bubble with proper text wrapping"""
    # Wrap text to fit bubble
    lines = wrap_text(text, font, max_width)
    
    # Calculate total text dimensions
    line_height = font.getbbox("Ay")[3] - font.getbbox("Ay")[1] + 4
    total_height = len(lines) * line_height
    max_line_width = max([font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines])
    
    padding = 15
    bubble_coords = (
        position[0] - padding,
        position[1] - padding,
        position[0] + max_line_width + padding,
        position[1] + total_height + padding
    )
    
    # Draw rounded rectangle for speech bubble
    draw.rounded_rectangle(bubble_coords, radius=15, fill=fill_color, outline=border_color, width=2)

    # Draw a "tail" for the speech bubble
    tail_base_x = (bubble_coords[0] + bubble_coords[2]) / 2
    tail_base_y = bubble_coords[3]
    tail_point_x = tail_base_x
    tail_point_y = tail_base_y + 15
    draw.polygon([(tail_base_x - 8, tail_base_y), (tail_base_x + 8, tail_base_y), (tail_point_x, tail_point_y)], fill=fill_color, outline=border_color)

    # Draw text lines
    for i, line in enumerate(lines):
        line_y = position[1] + (i * line_height)
        draw.text((position[0], line_y), line, fill=text_color, font=font)


def draw_thought_bubble(draw: ImageDraw.Draw, text: str, position: Tuple[int, int], font: ImageFont.FreeTypeFont, max_width: int = 180, fill_color: str = "white", text_color: str = "black", border_color: str = "black"):
    """Draw a thought bubble with proper text wrapping"""
    lines = wrap_text(text, font, max_width)
    
    line_height = font.getbbox("Ay")[3] - font.getbbox("Ay")[1] + 4
    total_height = len(lines) * line_height
    max_line_width = max([font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines])
    
    padding = 15
    bubble_coords = (
        position[0] - padding,
        position[1] - padding,
        position[0] + max_line_width + padding,
        position[1] + total_height + padding
    )
    
    # Draw ellipse for thought bubble
    draw.ellipse(bubble_coords, fill=fill_color, outline=border_color, width=2)

    # Draw thought "bubbles" leading to the character
    small_bubble_1 = (bubble_coords[0] + 30, bubble_coords[3] + 5, bubble_coords[0] + 45, bubble_coords[3] + 20)
    small_bubble_2 = (bubble_coords[0] + 45, bubble_coords[3] + 15, bubble_coords[0] + 55, bubble_coords[3] + 25)
    draw.ellipse(small_bubble_1, fill=fill_color, outline=border_color, width=1)
    draw.ellipse(small_bubble_2, fill=fill_color, outline=border_color, width=1)

    # Draw text lines
    for i, line in enumerate(lines):
        line_y = position[1] + (i * line_height)
        draw.text((position[0], line_y), line, fill=text_color, font=font)

def draw_scream_text(draw: ImageDraw.Draw, text: str, position: Tuple[int, int], font: ImageFont.FreeTypeFont, text_color: str = "red", border_color: str = "black"):
    # For "AAAAAH!", often large, bold, and sometimes with jagged outline or shadow
    # This will just draw bold text, for jagged outline, you'd need to draw multiple shifted texts or use a path effect.
    draw.text(position, text, fill=text_color, font=font, stroke_width=2, stroke_fill=border_color)


def add_dialogue_to_image(image: Image.Image, dialogues: List[Dialogue]) -> Image.Image:
    """Add professional-looking dialogue to comic panels with better positioning"""
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # Improved positioning system - avoid overlap
    dialogue_areas = []  # Track used areas to avoid overlap
    
    for i, d in enumerate(dialogues):
        # Clean up speaker names and text
        speaker_text = ""
        if d.speaker and d.type == "speech":
            speaker_text = f"{d.speaker}: " if len(d.speaker) <= 8 else f"{d.speaker[:8]}: "
        
        full_text = f"{speaker_text}{d.text}"
        
        # Position dialogue based on type with better spacing
        if d.type == "speech":
            # Smarter positioning for speech bubbles
            if i % 2 == 0:
                # Left side
                text_position_x = 20
                text_position_y = height - 120 - (i * 60)
            else:
                # Right side
                text_position_x = width - 220
                text_position_y = height - 120 - ((i-1) * 60)
            
            # Ensure position is within bounds
            text_position_y = max(50, text_position_y)
            
            draw_speech_bubble(draw, full_text, (text_position_x, text_position_y), SPEECH_FONT, max_width=160)
            
        elif d.type == "thought":
            # Center thoughts in upper area
            text_position_x = width // 4
            text_position_y = 30 + (i * 80)
            text_position_y = min(text_position_y, height - 100)
            
            draw_thought_bubble(draw, full_text, (text_position_x, text_position_y), THOUGHT_FONT, max_width=160)
            
        elif d.type == "narration":
            # Narration at top of panel with better styling
            narration_box_height = 30
            narration_box_y = 5
            
            # Semi-transparent background with better contrast
            draw.rectangle((0, narration_box_y, width, narration_box_y + narration_box_height), 
                         fill=(0, 0, 0, 160))
            draw.text((10, narration_box_y + 8), d.text, fill="white", font=NARRATION_FONT)
            
        elif d.type == "sound_effect":
            # Dynamic sound effects with better positioning
            lines = wrap_text(d.text, SFX_FONT, width - 40)
            total_height = len(lines) * 40
            
            start_y = (height - total_height) // 2
            
            for j, line in enumerate(lines):
                line_bbox = SFX_FONT.getbbox(line)
                line_width = line_bbox[2] - line_bbox[0]
                sfx_position_x = (width - line_width) // 2
                sfx_position_y = start_y + (j * 40)
                
                # Add shadow effect
                draw.text((sfx_position_x + 2, sfx_position_y + 2), line, fill="black", font=SFX_FONT)
                draw.text((sfx_position_x, sfx_position_y), line, fill="red", font=SFX_FONT, 
                         stroke_width=2, stroke_fill="white")
            
        elif d.type == "scream":
            # Dramatic screams with better positioning
            lines = wrap_text(full_text, SCREAM_FONT, width - 40)
            total_height = len(lines) * 45
            
            start_y = height // 4
            
            for j, line in enumerate(lines):
                line_bbox = SCREAM_FONT.getbbox(line)
                line_width = line_bbox[2] - line_bbox[0]
                scream_position_x = (width - line_width) // 2
                scream_position_y = start_y + (j * 45)
                
                # Jagged effect with multiple colors
                draw.text((scream_position_x + 3, scream_position_y + 3), line, fill="black", font=SCREAM_FONT)
                draw.text((scream_position_x, scream_position_y), line, fill="red", font=SCREAM_FONT, 
                         stroke_width=3, stroke_fill="yellow")

    return image

def create_comic_sheet(frames: List[Tuple[Image.Image, List[Dialogue]]]) -> Image.Image:
    """Create a professional comic sheet layout with varied panel sizes"""
    num_panels = len(frames)
    
    # Different layouts based on number of panels
    if num_panels == 3:
        # 3-panel layout: Large top panel, two smaller bottom panels
        panel_configs = [
            {"size": (800, 300), "pos": (0, 0)},      # Top wide panel
            {"size": (390, 350), "pos": (0, 320)},    # Bottom left
            {"size": (390, 350), "pos": (410, 320)}   # Bottom right
        ]
        sheet_size = (820, 690)
    elif num_panels == 4:
        # 2x2 grid with slightly varied sizes
        panel_configs = [
            {"size": (400, 320), "pos": (0, 0)},      # Top left
            {"size": (400, 320), "pos": (420, 0)},    # Top right
            {"size": (400, 320), "pos": (0, 340)},    # Bottom left
            {"size": (400, 320), "pos": (420, 340)}   # Bottom right
        ]
        sheet_size = (840, 680)
    else:
        # Fallback to simple layout
        panel_size = (400, 300)
        cols = 2
        rows = (num_panels + 1) // 2
        panel_configs = []
        for i in range(num_panels):
            col = i % cols
            row = i // cols
            panel_configs.append({
                "size": panel_size,
                "pos": (col * 420, row * 320)
            })
        sheet_size = (840, rows * 320 + 20)
    
    # Create comic sheet with white background
    comic_sheet = Image.new('RGB', sheet_size, "white")
    
    # Add panels with improved styling
    for idx, (frame, config) in enumerate(zip(frames, panel_configs)):
        img, dialogs = frame
        
        # Resize image to panel size
        img = img.resize(config["size"], Image.Resampling.LANCZOS)
        
        # Apply dialogue AFTER resizing
        img_with_dialogue = add_dialogue_to_image(img.copy(), dialogs)
        
        # Calculate position with margin
        x = config["pos"][0] + 10
        y = config["pos"][1] + 10
        
        # Add professional panel border
        draw = ImageDraw.Draw(comic_sheet)
        border_coords = (x-3, y-3, x + config["size"][0] + 3, y + config["size"][1] + 3)
        draw.rectangle(border_coords, outline="black", width=3)
        
        # Paste the panel
        comic_sheet.paste(img_with_dialogue, (x, y))

    return comic_sheet