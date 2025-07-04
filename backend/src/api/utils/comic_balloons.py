from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional, Dict, Literal
import math
from dataclasses import dataclass
from .image_utils import get_system_font, wrap_text_pil
from .comic_text_utils import ComicTextStyle, TextBubble, ComicTextRenderer

@dataclass
class BalloonStyle:
    """Defines the visual style of a speech balloon"""
    shape: Literal["oval", "rectangle", "cloud", "jagged", "whisper"] = "oval"
    fill_color: str = "white"
    border_color: str = "black"
    border_width: int = 3
    corner_radius: int = 20
    tail_style: Literal["triangle", "cloud_circles", "none", "whisper_dashes"] = "triangle"
    tail_size: int = 20
    padding: int = 15
    shadow: bool = False
    shadow_offset: Tuple[int, int] = (2, 2)
    shadow_color: str = "#888888"

class ComicBalloonRenderer:
    """Specialized renderer for comic speech balloons and bubbles"""
    
    def __init__(self):
        self.balloon_styles = {
            "speech": BalloonStyle(
                shape="oval",
                fill_color="white",
                border_color="black",
                tail_style="triangle"
            ),
            "thought": BalloonStyle(
                shape="cloud",
                fill_color="#f8f8ff",
                border_color="#4682b4",
                border_width=2,
                tail_style="cloud_circles",
                corner_radius=30
            ),
            "whisper": BalloonStyle(
                shape="whisper",
                fill_color="#f5f5f5",
                border_color="gray",
                border_width=1,
                tail_style="whisper_dashes",
                corner_radius=15
            ),
            "shout": BalloonStyle(
                shape="jagged",
                fill_color="white",
                border_color="red",
                border_width=4,
                tail_style="triangle",
                tail_size=25
            ),
            "narration": BalloonStyle(
                shape="rectangle",
                fill_color="#fffacd",
                border_color="#daa520",
                border_width=2,
                corner_radius=10,
                tail_style="none"
            ),
            "sound_effect": BalloonStyle(
                shape="jagged",
                fill_color="transparent",
                border_color="transparent",
                tail_style="none"
            )
        }
    
    def create_balloon(self, text: str, balloon_type: str = "speech", 
                      size: Optional[Tuple[int, int]] = None,
                      speaker_position: str = "bottom",
                      text_style: Optional[ComicTextStyle] = None) -> Image.Image:
        """Create a complete speech balloon with text"""
        
        # Get balloon style
        style = self.balloon_styles.get(balloon_type, self.balloon_styles["speech"])
        
        # Calculate required size if not provided
        if size is None:
            size = self._calculate_balloon_size(text, style, text_style)
        
        width, height = size
        
        # Create balloon image with transparency
        balloon_img = Image.new('RGBA', (width + 40, height + 40), (0, 0, 0, 0))  # Extra space for tail
        draw = ImageDraw.Draw(balloon_img)
        
        # Balloon coordinates (leaving space for tail)
        balloon_x = 20
        balloon_y = 20
        balloon_coords = (balloon_x, balloon_y, balloon_x + width, balloon_y + height)
        
        # Draw shadow if enabled
        if style.shadow:
            shadow_coords = (
                balloon_coords[0] + style.shadow_offset[0],
                balloon_coords[1] + style.shadow_offset[1],
                balloon_coords[2] + style.shadow_offset[0],
                balloon_coords[3] + style.shadow_offset[1]
            )
            self._draw_balloon_shape(draw, shadow_coords, style.shape, style.shadow_color, "transparent", 1, style.corner_radius)
        
        # Draw main balloon shape
        if style.fill_color != "transparent":
            self._draw_balloon_shape(draw, balloon_coords, style.shape, style.fill_color, style.border_color, style.border_width, style.corner_radius)
        
        # Draw tail
        if style.tail_style != "none":
            self._draw_balloon_tail(draw, balloon_coords, speaker_position, style)
        
        # Add text
        if text and style.fill_color != "transparent":
            self._add_text_to_balloon(balloon_img, text, balloon_coords, text_style or ComicTextStyle())
        
        return balloon_img
    
    def _calculate_balloon_size(self, text: str, style: BalloonStyle, text_style: Optional[ComicTextStyle]) -> Tuple[int, int]:
        """Calculate optimal balloon size for given text"""
        if not text_style:
            text_style = ComicTextStyle()
        
        try:
            font = get_system_font(text_style.font_family, text_style.font_size)
            
            # Create temporary draw to measure text
            temp_img = Image.new('RGB', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # Estimate max width (will be refined)
            max_width = 300
            wrapped_lines = wrap_text_pil(temp_draw, text, font, max_width - 2 * style.padding)
            
            if not wrapped_lines:
                return 150, 80
            
            # Calculate actual text dimensions
            line_height = temp_draw.textbbox((0, 0), "Ay", font=font)[3] - temp_draw.textbbox((0, 0), "Ay", font=font)[1]
            text_height = len(wrapped_lines) * line_height + (len(wrapped_lines) - 1) * 8
            
            max_line_width = 0
            for line in wrapped_lines:
                line_bbox = temp_draw.textbbox((0, 0), line, font=font)
                line_width = line_bbox[2] - line_bbox[0]
                max_line_width = max(max_line_width, line_width)
            
            # Add padding
            balloon_width = max_line_width + 2 * style.padding
            balloon_height = text_height + 2 * style.padding
            
            # Ensure minimum size
            balloon_width = max(balloon_width, 100)
            balloon_height = max(balloon_height, 60)
            
            return int(balloon_width), int(balloon_height)
            
        except Exception as e:
            print(f"Error calculating balloon size: {e}")
            return 200, 100
    
    def _draw_balloon_shape(self, draw: ImageDraw.Draw, coords: Tuple[int, int, int, int], 
                           shape: str, fill_color: str, border_color: str, border_width: int, corner_radius: int):
        """Draw the balloon shape"""
        x1, y1, x2, y2 = coords
        
        if shape == "oval":
            # Oval/ellipse balloon
            draw.ellipse(coords, fill=fill_color, outline=border_color, width=border_width)
        
        elif shape == "rectangle":
            # Rectangular balloon with rounded corners
            draw.rounded_rectangle(coords, radius=corner_radius, fill=fill_color, outline=border_color, width=border_width)
        
        elif shape == "cloud":
            # Cloud-like thought bubble
            self._draw_cloud_shape(draw, coords, fill_color, border_color, border_width)
        
        elif shape == "jagged":
            # Jagged balloon for shouts/sound effects
            self._draw_jagged_shape(draw, coords, fill_color, border_color, border_width)
        
        elif shape == "whisper":
            # Dashed outline for whispers
            self._draw_whisper_shape(draw, coords, fill_color, border_color, border_width, corner_radius)
    
    def _draw_cloud_shape(self, draw: ImageDraw.Draw, coords: Tuple[int, int, int, int], 
                         fill_color: str, border_color: str, border_width: int):
        """Draw a cloud-like shape for thought bubbles"""
        x1, y1, x2, y2 = coords
        width = x2 - x1
        height = y2 - y1
        
        # Main ellipse
        draw.ellipse(coords, fill=fill_color, outline=border_color, width=border_width)
        
        # Add smaller cloud bumps
        bump_size = min(width, height) // 6
        positions = [
            (x1 + width * 0.2, y1),
            (x1 + width * 0.8, y1),
            (x1, y1 + height * 0.3),
            (x2, y1 + height * 0.3),
            (x1, y1 + height * 0.7),
            (x2, y1 + height * 0.7),
            (x1 + width * 0.3, y2),
            (x1 + width * 0.7, y2)
        ]
        
        for px, py in positions:
            bump_coords = (px - bump_size, py - bump_size, px + bump_size, py + bump_size)
            draw.ellipse(bump_coords, fill=fill_color, outline=border_color, width=border_width)
    
    def _draw_jagged_shape(self, draw: ImageDraw.Draw, coords: Tuple[int, int, int, int], 
                          fill_color: str, border_color: str, border_width: int):
        """Draw a jagged shape for shouts/explosions"""
        x1, y1, x2, y2 = coords
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Create jagged points
        points = []
        num_points = 16
        base_radius = min(x2 - x1, y2 - y1) / 2
        
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            # Alternate between inner and outer radius for jagged effect
            radius = base_radius * (0.7 if i % 2 == 0 else 1.0)
            
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle) * 0.8  # Slightly flatten
            points.append((x, y))
        
        draw.polygon(points, fill=fill_color, outline=border_color, width=border_width)
    
    def _draw_whisper_shape(self, draw: ImageDraw.Draw, coords: Tuple[int, int, int, int], 
                           fill_color: str, border_color: str, border_width: int, corner_radius: int):
        """Draw a whisper balloon with dashed outline"""
        # Main shape
        draw.rounded_rectangle(coords, radius=corner_radius, fill=fill_color)
        
        # Draw dashed outline manually
        x1, y1, x2, y2 = coords
        dash_length = 8
        gap_length = 4
        
        # Top edge
        x = x1
        while x < x2:
            draw.line([(x, y1), (min(x + dash_length, x2), y1)], fill=border_color, width=border_width)
            x += dash_length + gap_length
        
        # Right edge
        y = y1
        while y < y2:
            draw.line([(x2, y), (x2, min(y + dash_length, y2))], fill=border_color, width=border_width)
            y += dash_length + gap_length
        
        # Bottom edge
        x = x2
        while x > x1:
            draw.line([(max(x - dash_length, x1), y2), (x, y2)], fill=border_color, width=border_width)
            x -= dash_length + gap_length
        
        # Left edge
        y = y2
        while y > y1:
            draw.line([(x1, max(y - dash_length, y1)), (x1, y)], fill=border_color, width=border_width)
            y -= dash_length + gap_length
    
    def _draw_balloon_tail(self, draw: ImageDraw.Draw, balloon_coords: Tuple[int, int, int, int], 
                          speaker_position: str, style: BalloonStyle):
        """Draw the balloon tail pointing to speaker"""
        x1, y1, x2, y2 = balloon_coords
        
        if style.tail_style == "triangle":
            self._draw_triangle_tail(draw, balloon_coords, speaker_position, style)
        elif style.tail_style == "cloud_circles":
            self._draw_cloud_tail(draw, balloon_coords, speaker_position, style)
        elif style.tail_style == "whisper_dashes":
            self._draw_whisper_tail(draw, balloon_coords, speaker_position, style)
    
    def _draw_triangle_tail(self, draw: ImageDraw.Draw, coords: Tuple[int, int, int, int], 
                           speaker_position: str, style: BalloonStyle):
        """Draw triangular tail"""
        x1, y1, x2, y2 = coords
        tail_size = style.tail_size
        
        if speaker_position == "bottom":
            # Tail pointing down
            tail_base_x = x1 + (x2 - x1) // 2
            tail_points = [
                (tail_base_x - tail_size//2, y2),
                (tail_base_x + tail_size//2, y2),
                (tail_base_x, y2 + tail_size)
            ]
        elif speaker_position == "left":
            # Tail pointing left
            tail_base_y = y1 + (y2 - y1) // 2
            tail_points = [
                (x1, tail_base_y - tail_size//2),
                (x1, tail_base_y + tail_size//2),
                (x1 - tail_size, tail_base_y)
            ]
        elif speaker_position == "right":
            # Tail pointing right
            tail_base_y = y1 + (y2 - y1) // 2
            tail_points = [
                (x2, tail_base_y - tail_size//2),
                (x2, tail_base_y + tail_size//2),
                (x2 + tail_size, tail_base_y)
            ]
        else:  # top
            # Tail pointing up
            tail_base_x = x1 + (x2 - x1) // 2
            tail_points = [
                (tail_base_x - tail_size//2, y1),
                (tail_base_x + tail_size//2, y1),
                (tail_base_x, y1 - tail_size)
            ]
        
        draw.polygon(tail_points, fill=style.fill_color, outline=style.border_color)
    
    def _draw_cloud_tail(self, draw: ImageDraw.Draw, coords: Tuple[int, int, int, int], 
                        speaker_position: str, style: BalloonStyle):
        """Draw cloud circles for thought bubble tail"""
        x1, y1, x2, y2 = coords
        
        # Starting position based on speaker location
        if speaker_position == "bottom":
            start_x = x1 + (x2 - x1) // 2
            start_y = y2
            direction = (0, 1)
        elif speaker_position == "left":
            start_x = x1
            start_y = y1 + (y2 - y1) // 2
            direction = (-1, 0)
        elif speaker_position == "right":
            start_x = x2
            start_y = y1 + (y2 - y1) // 2
            direction = (1, 0)
        else:  # top
            start_x = x1 + (x2 - x1) // 2
            start_y = y1
            direction = (0, -1)
        
        # Draw decreasing circles
        circle_sizes = [12, 8, 5]
        for i, size in enumerate(circle_sizes):
            offset = 15 + i * 10
            cx = start_x + direction[0] * offset
            cy = start_y + direction[1] * offset
            
            circle_coords = (cx - size, cy - size, cx + size, cy + size)
            draw.ellipse(circle_coords, fill=style.fill_color, outline=style.border_color, width=2)
    
    def _draw_whisper_tail(self, draw: ImageDraw.Draw, coords: Tuple[int, int, int, int], 
                          speaker_position: str, style: BalloonStyle):
        """Draw dashed line for whisper tail"""
        x1, y1, x2, y2 = coords
        
        # Calculate start and end points
        if speaker_position == "bottom":
            start_pos = (x1 + (x2 - x1) // 2, y2)
            end_pos = (start_pos[0], start_pos[1] + 20)
        elif speaker_position == "left":
            start_pos = (x1, y1 + (y2 - y1) // 2)
            end_pos = (start_pos[0] - 20, start_pos[1])
        elif speaker_position == "right":
            start_pos = (x2, y1 + (y2 - y1) // 2)
            end_pos = (start_pos[0] + 20, start_pos[1])
        else:  # top
            start_pos = (x1 + (x2 - x1) // 2, y1)
            end_pos = (start_pos[0], start_pos[1] - 20)
        
        # Draw dashed line
        dash_length = 4
        total_length = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
        num_dashes = int(total_length // (dash_length * 2))
        
        for i in range(num_dashes):
            progress1 = (i * 2 * dash_length) / total_length
            progress2 = ((i * 2 + 1) * dash_length) / total_length
            
            if progress2 > 1:
                break
                
            x_start = start_pos[0] + progress1 * (end_pos[0] - start_pos[0])
            y_start = start_pos[1] + progress1 * (end_pos[1] - start_pos[1])
            x_end = start_pos[0] + progress2 * (end_pos[0] - start_pos[0])
            y_end = start_pos[1] + progress2 * (end_pos[1] - start_pos[1])
            
            draw.line([(x_start, y_start), (x_end, y_end)], fill=style.border_color, width=2)
    
    def _add_text_to_balloon(self, balloon_img: Image.Image, text: str, 
                            balloon_coords: Tuple[int, int, int, int], text_style: ComicTextStyle):
        """Add text to the balloon"""
        try:
            font = get_system_font(text_style.font_family, text_style.font_size)
            
            # Create text overlay
            overlay = Image.new('RGBA', balloon_img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            x1, y1, x2, y2 = balloon_coords
            max_width = (x2 - x1) - 2 * text_style.padding
            
            # Wrap text
            wrapped_lines = wrap_text_pil(draw, text, font, max_width)
            
            if wrapped_lines:
                # Calculate text positioning
                line_height = draw.textbbox((0, 0), "Ay", font=font)[3] - draw.textbbox((0, 0), "Ay", font=font)[1]
                total_text_height = len(wrapped_lines) * line_height + (len(wrapped_lines) - 1) * 8
                
                start_y = y1 + text_style.padding + (y2 - y1 - 2 * text_style.padding - total_text_height) // 2
                
                # Draw each line
                for i, line in enumerate(wrapped_lines):
                    line_bbox = draw.textbbox((0, 0), line, font=font)
                    line_width = line_bbox[2] - line_bbox[0]
                    
                    line_x = x1 + text_style.padding + (max_width - line_width) // 2
                    line_y = start_y + i * (line_height + 8)
                    
                    # Draw text with outline
                    for offset_x in range(-text_style.outline_width, text_style.outline_width + 1):
                        for offset_y in range(-text_style.outline_width, text_style.outline_width + 1):
                            if offset_x * offset_x + offset_y * offset_y <= text_style.outline_width * text_style.outline_width:
                                draw.text((line_x + offset_x, line_y + offset_y), line, font=font, fill=text_style.outline_color)
                    
                    draw.text((line_x, line_y), line, font=font, fill=text_style.text_color)
            
            # Composite text onto balloon
            balloon_img = Image.alpha_composite(balloon_img, overlay)
            
        except Exception as e:
            print(f"Error adding text to balloon: {e}")


# Convenience functions
def create_speech_balloon(text: str, balloon_type: str = "speech", 
                         speaker_position: str = "bottom") -> Image.Image:
    """Quick function to create a speech balloon"""
    renderer = ComicBalloonRenderer()
    return renderer.create_balloon(text, balloon_type, speaker_position=speaker_position)

def create_thought_bubble(text: str) -> Image.Image:
    """Quick function to create a thought bubble"""
    renderer = ComicBalloonRenderer()
    return renderer.create_balloon(text, "thought", speaker_position="bottom")

def create_sound_effect_balloon(text: str) -> Image.Image:
    """Quick function to create a sound effect balloon"""
    renderer = ComicBalloonRenderer()
    return renderer.create_balloon(text, "sound_effect") 