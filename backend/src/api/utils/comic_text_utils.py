from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Dict, Optional, Literal
import math
from dataclasses import dataclass
from .image_utils import get_system_font, wrap_text_pil, draw_text_with_outline

@dataclass
class ComicTextStyle:
    """Defines styling for comic text elements"""
    font_size: int = 36  # Readable text size
    font_family: str = "arial_bold"
    text_color: str = "black"  # Clean black text
    outline_color: str = "white"
    outline_width: int = 3  # Thicker outline by default
    bubble_color: str = "white"  # Clean white bubbles
    bubble_outline: str = "black"  # Clean black outline
    bubble_outline_width: int = 4  # Thicker bubble outline
    padding: int = 25  # Much more generous padding for better readability
    corner_radius: int = 15  # Nice rounded corners
    line_spacing: int = 12  # Extra space between lines

@dataclass 
class TextBubble:
    """Represents a text bubble in a comic panel"""
    text: str
    position: Tuple[int, int]  # x, y coordinates
    bubble_type: Literal["speech", "thought", "narration", "sound_effect", "scream"]
    emotion: Literal["normal", "shouting", "whispering", "thoughtful", "angry", "excited", "sad"]
    speaker_position: Literal["left", "right", "center", "top", "bottom", "above", "below"] = "center"
    style: Optional[ComicTextStyle] = None
    speaker_name: Optional[str] = None  # For smart positioning

class ComicTextRenderer:
    """Handles rendering of text elements in comic panels"""
    
    def __init__(self):
        self.default_styles = {
            "speech": ComicTextStyle(
                font_size=36,  # Readable speech text
                font_family="arial_bold",
                bubble_color="white",
                bubble_outline="black",
                corner_radius=15,
                padding=25,  # Generous padding
                outline_width=3,
                line_spacing=12
            ),
            "thought": ComicTextStyle(
                font_size=32,  # Slightly smaller thought text
                font_family="arial",
                bubble_color="white",
                bubble_outline="black",
                corner_radius=25,  # More rounded for thoughts
                padding=25,  # Generous padding
                outline_width=2,
                line_spacing=12
            ),
            "narration": ComicTextStyle(
                font_size=30,  # Clean narration text
                font_family="times",  # More elegant font for narration
                bubble_color="#f8f8f8",  # Slightly off-white for narration
                bubble_outline="black",
                corner_radius=5,  # Sharp corners for narration boxes
                padding=25,  # Generous padding
                outline_width=2,
                line_spacing=12
            ),
            "sound_effect": ComicTextStyle(
                font_size=52,  # Bigger and bolder for sound effects
                font_family="arial_black",
                text_color="black",
                outline_color="white",
                outline_width=6,  # Thicker outline for impact
                bubble_color="transparent",  # No bubble for SFX
                bubble_outline="transparent",
                padding=15,  # Less padding for SFX
                line_spacing=8
            ),
            "scream": ComicTextStyle(
                font_size=44,  # Bigger scream text
                font_family="arial_black", 
                text_color="black",
                outline_color="white",
                outline_width=4,  # Thicker outline for emphasis
                bubble_color="white",
                bubble_outline="black",
                corner_radius=8,  # Jagged-ish corners for screaming
                padding=25,  # Generous padding
                line_spacing=10
            )
        }
    
    def get_style_for_emotion(self, base_style: ComicTextStyle, emotion: str) -> ComicTextStyle:
        """Modify style based on emotion"""
        style = ComicTextStyle(**base_style.__dict__)
        
        emotion_modifications = {
            "shouting": {
                "font_size": int(style.font_size * 1.2),  # Slightly larger for shouting
                "text_color": "black",  # BLACK text for all emotions
                "outline_width": style.outline_width + 1,  # Slightly thicker outline
                "outline_color": "white",
                "bubble_color": "white",
                "bubble_outline": "black"
            },
            "whispering": {
                "font_size": int(style.font_size * 0.9),  # Slightly smaller
                "text_color": "black",  # BLACK text for all emotions
                "bubble_color": "white",
                "bubble_outline": "black",
                "outline_width": 2
            },
            "thoughtful": {
                "text_color": "black",  # BLACK text for all emotions
                "bubble_color": "white",
                "bubble_outline": "black"
            },
            "angry": {
                "text_color": "black",  # BLACK text for all emotions
                "bubble_color": "white",
                "bubble_outline": "black"
            },
            "excited": {
                "text_color": "black",  # BLACK text for all emotions
                "bubble_color": "white",
                "bubble_outline": "black"
            },
            "sad": {
                "text_color": "black",  # BLACK text for all emotions
                "bubble_color": "white",
                "bubble_outline": "black"
            }
        }
        
        if emotion in emotion_modifications:
            for key, value in emotion_modifications[emotion].items():
                setattr(style, key, value)
        
        return style
    
    def calculate_optimal_font_size(self, text: str, style: ComicTextStyle, 
                                   bubble_width: int, bubble_height: int) -> int:
        """Calculate optimal font size that fits within the given bubble dimensions"""
        if not text.strip():
            return style.font_size
        
        # Start with the base font size and work down if needed
        max_font_size = min(style.font_size, 72)  # Cap at reasonable maximum
        min_font_size = max(16, style.font_size // 3)  # Minimum readable size
        
        available_width = bubble_width - 2 * style.padding
        available_height = bubble_height - 2 * style.padding
        
        # Binary search for optimal font size
        best_size = min_font_size
        
        for test_size in range(max_font_size, min_font_size - 1, -2):
            try:
                test_font = get_system_font(style.font_family, test_size)
                temp_img = Image.new('RGB', (1, 1))
                draw = ImageDraw.Draw(temp_img)
                
                # Test if text fits at this size
                wrapped_lines = wrap_text_pil(draw, text, test_font, available_width)
                if not wrapped_lines:
                    continue
                
                # Calculate total height needed
                line_height = draw.textbbox((0, 0), "Ay", font=test_font)[3] - draw.textbbox((0, 0), "Ay", font=test_font)[1]
                total_height = len(wrapped_lines) * line_height + (len(wrapped_lines) - 1) * 8
                
                # If it fits, this is our size
                if total_height <= available_height:
                    best_size = test_size
                    break
                    
            except Exception:
                continue
        
        print(f"📏 Optimal font size for bubble {bubble_width}x{bubble_height}: {best_size}px")
        return best_size

    def calculate_bubble_size(self, text: str, style: ComicTextStyle, max_width: int) -> Tuple[int, int]:
        """Calculate the required bubble size for given text - favor narrower, taller bubbles"""
        try:
            font = get_system_font(style.font_family, style.font_size)
            
            # Create temporary draw object to measure text
            temp_img = Image.new('RGB', (1, 1))
            draw = ImageDraw.Draw(temp_img)
            
            # Use a narrower max width to force more text wrapping (taller bubbles)
            constrained_width = int(max_width * 0.6)  # Use only 60% of available width
            
            # Wrap text and calculate dimensions
            wrapped_lines = wrap_text_pil(draw, text, font, constrained_width - 2 * style.padding)
            
            if not wrapped_lines:
                return style.padding * 2, style.padding * 2
            
            # Calculate text dimensions
            line_height = draw.textbbox((0, 0), "Ay", font=font)[3] - draw.textbbox((0, 0), "Ay", font=font)[1]
            text_height = len(wrapped_lines) * line_height + (len(wrapped_lines) - 1) * 8
            
            max_line_width = 0
            for line in wrapped_lines:
                line_bbox = draw.textbbox((0, 0), line, font=font)
                line_width = line_bbox[2] - line_bbox[0]
                max_line_width = max(max_line_width, line_width)
            
            # Add padding and set adaptive minimum sizes - favor narrower, taller dimensions
            min_bubble_width = max(120, constrained_width * 0.4)  # Narrower minimum
            min_bubble_height = max(80, style.font_size + 40)     # Taller minimum
            
            bubble_width = max(max_line_width + 2 * style.padding, min_bubble_width)
            bubble_height = max(text_height + 2 * style.padding, min_bubble_height)
            
            # Ensure bubble doesn't exceed reasonable limits - keep it narrow
            bubble_width = min(bubble_width, constrained_width * 0.8)  # Max 80% of constrained width
            
            return bubble_width, bubble_height
            
        except Exception as e:
            print(f"Error calculating bubble size: {e}")
            # Adaptive fallback size - narrower and taller
            fallback_width = max(120, max_width * 0.25)
            return fallback_width, 120
    
    def draw_bubble_shape(self, draw: ImageDraw.Draw, coords: Tuple[int, int, int, int], 
                         bubble_type: str, style: ComicTextStyle, speaker_pos: str = "center"):
        """Draw the bubble shape based on type with proper styling"""
        x1, y1, x2, y2 = coords
        
        if bubble_type == "thought":
            # Draw thought bubble with cloud-like edges
            self._draw_cloud_bubble(draw, coords, style)
        elif bubble_type == "sound_effect":
            # Sound effects get no bubble (transparent)
            return  # Skip drawing bubble for SFX
        elif bubble_type == "scream":
            # Draw jagged bubble for screaming
            self._draw_jagged_bubble(draw, coords, style)
            self._draw_speech_tail(draw, coords, speaker_pos, style)
        elif bubble_type == "narration":
            # Draw rectangular narration box
            self._draw_narration_box(draw, coords, style)
        else:
            # Regular speech bubble with tail
            self._draw_speech_bubble(draw, coords, style, speaker_pos)
            self._draw_speech_tail(draw, coords, speaker_pos, style)
    
    def _draw_speech_bubble(self, draw: ImageDraw.Draw, coords: Tuple[int, int, int, int], 
                           style: ComicTextStyle, speaker_pos: str):
        """Draw a standard speech bubble"""
        x1, y1, x2, y2 = coords
        
        if style.bubble_color != "transparent":
            # Draw rounded rectangle
            draw.rounded_rectangle(
                coords, 
                radius=style.corner_radius,
                fill=style.bubble_color,
                outline=style.bubble_outline,
                width=style.bubble_outline_width
            )
            
            # Add tail pointing to speaker
            self._draw_speech_tail(draw, coords, speaker_pos, style)
    
    def _draw_cloud_bubble(self, draw: ImageDraw.Draw, coords: Tuple[int, int, int, int], 
                          style: ComicTextStyle):
        """Draw a cloud-like thought bubble"""
        x1, y1, x2, y2 = coords
        
        if style.bubble_color != "transparent":
            # Main bubble
            draw.rounded_rectangle(
                coords,
                radius=style.corner_radius,
                fill=style.bubble_color,
                outline=style.bubble_outline,
                width=style.bubble_outline_width
            )
            
            # Add small cloud circles for thought bubble effect
            circle_size = 8
            for i in range(3):
                cx = x1 + 20 + i * 15
                cy = y2 + 10 + i * 8
                draw.ellipse(
                    (cx - circle_size, cy - circle_size, cx + circle_size, cy + circle_size),
                    fill=style.bubble_color,
                    outline=style.bubble_outline,
                    width=2
                )
                circle_size = max(3, circle_size - 2)
    
    def _draw_jagged_bubble(self, draw: ImageDraw.Draw, coords: Tuple[int, int, int, int], 
                           style: ComicTextStyle):
        """Draw a jagged bubble for screaming with spiky edges"""
        x1, y1, x2, y2 = coords
        
        # Create jagged points around the perimeter
        points = []
        spike_size = 8
        step = 25
        
        # Top edge with spikes pointing up
        x = x1
        while x < x2:
            points.extend([(x, y1), (x + step//2, y1 - spike_size), (min(x + step, x2), y1)])
            x += step
        
        # Right edge with spikes pointing right
        y = y1  
        while y < y2:
            points.extend([(x2, y), (x2 + spike_size, y + step//2), (x2, min(y + step, y2))])
            y += step
        
        # Bottom edge with spikes pointing down
        x = x2
        while x > x1:
            points.extend([(x, y2), (x - step//2, y2 + spike_size), (max(x - step, x1), y2)])
            x -= step
        
        # Left edge with spikes pointing left
        y = y2
        while y > y1:
            points.extend([(x1, y), (x1 - spike_size, y - step//2), (x1, max(y - step, y1))])
            y -= step
        
        # Draw the jagged polygon
        if len(points) > 6:
            draw.polygon(points, fill=style.bubble_color, outline=style.bubble_outline, width=style.bubble_outline_width)
        else:
            # Fallback to regular rectangle
            draw.rectangle(coords, fill=style.bubble_color, outline=style.bubble_outline, width=style.bubble_outline_width)

    def _draw_narration_box(self, draw: ImageDraw.Draw, coords: Tuple[int, int, int, int], 
                           style: ComicTextStyle):
        """Draw rectangular narration box"""
        draw.rectangle(
            coords,
            fill=style.bubble_color,
            outline=style.bubble_outline,
            width=style.bubble_outline_width
        )
    
    def _draw_speech_tail(self, draw: ImageDraw.Draw, coords: Tuple[int, int, int, int], 
                         speaker_pos: str, style: ComicTextStyle):
        """Draw bubble tail pointing to speaker"""
        x1, y1, x2, y2 = coords
        tail_size = 20
        
        if speaker_pos == "left":
            # Tail pointing left
            tail_points = [
                (x1, y2 - 30),
                (x1 - tail_size, y2),
                (x1, y2 - 15)
            ]
        elif speaker_pos == "right":
            # Tail pointing right  
            tail_points = [
                (x2, y2 - 30),
                (x2 + tail_size, y2),
                (x2, y2 - 15)
            ]
        elif speaker_pos == "bottom":
            # Tail pointing down
            tail_points = [
                (x1 + (x2-x1)//2 - 15, y2),
                (x1 + (x2-x1)//2, y2 + tail_size),
                (x1 + (x2-x1)//2 + 15, y2)
            ]
        else:
            return  # No tail for center or top positions
        
        draw.polygon(tail_points, fill=style.bubble_color, outline=style.bubble_outline)
    
    def render_text_bubble(self, panel: Image.Image, bubble: TextBubble, 
                          panel_width: int, panel_height: int) -> Image.Image:
        """Render a single text bubble on the panel"""
        if not bubble.style:
            bubble.style = self.default_styles.get(bubble.bubble_type, self.default_styles["speech"])
        
        # Apply emotion modifications
        style = self.get_style_for_emotion(bubble.style, bubble.emotion)
        
        # Calculate optimal position if not specified
        if bubble.position == (0, 0):
            bubble.position = self._find_optimal_position(panel, bubble, panel_width, panel_height, style)
        
        # Calculate bubble dimensions for readable text
        max_bubble_width = min(int(panel_width * 0.8), 600)  # Good balance for readable text
        bubble_width, bubble_height = self.calculate_bubble_size(bubble.text, style, max_bubble_width)
        
        # Ensure bubble fits in panel
        x, y = bubble.position
        x = max(10, min(x, panel_width - bubble_width - 10))
        y = max(10, min(y, panel_height - bubble_height - 10))
        
        # Create overlay for bubble
        overlay = Image.new('RGBA', panel.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        bubble_coords = (x, y, x + bubble_width, y + bubble_height)
        
        # Draw bubble shape
        self.draw_bubble_shape(draw, bubble_coords, bubble.bubble_type, style, bubble.speaker_position)
        
        # Draw text
        self._render_text_in_bubble(draw, bubble.text, bubble_coords, style)
        
        # Composite with panel
        if panel.mode != 'RGBA':
            panel = panel.convert('RGBA')
        
        result = Image.alpha_composite(panel, overlay)
        return result.convert('RGB')
    
    def render_text_bubble_at_position(self, panel: Image.Image, bubble: TextBubble, 
                                     forced_x: int, forced_y: int, panel_width: int, panel_height: int) -> Image.Image:
        """Render a text bubble at EXACTLY the specified coordinates (no automatic positioning)"""
        if not bubble.text.strip():
            return panel
        
        print(f"🎯 FORCING bubble at exact position: ({forced_x}, {forced_y}) - '{bubble.text[:30]}...'")
        
        # Get style
        if not bubble.style:
            bubble.style = self.default_styles.get(bubble.bubble_type, self.default_styles["speech"])
        
        # Apply emotion modifications
        style = self.get_style_for_emotion(bubble.style, bubble.emotion)
        
        # Calculate bubble size for normal text
        max_bubble_width = min(int(panel_width * 0.7), 500)  # Good max width for readable text
        bubble_width, bubble_height = self.calculate_bubble_size(bubble.text, style, max_bubble_width)
        
        # USE EXACTLY the forced coordinates (minimal bounds checking)
        x = max(5, min(forced_x, panel_width - bubble_width - 5))
        y = max(5, min(forced_y, panel_height - bubble_height - 5))
        
        print(f"📐 Bubble size: {bubble_width}x{bubble_height} at final position ({x}, {y})")
        
        # Create overlay for bubble
        overlay = Image.new('RGBA', panel.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        bubble_coords = (x, y, x + bubble_width, y + bubble_height)
        
        # Draw bubble shape
        self.draw_bubble_shape(draw, bubble_coords, bubble.bubble_type, style, bubble.speaker_position)
        
        # Draw text
        self._render_text_in_bubble(draw, bubble.text, bubble_coords, style)
        
        # Composite with panel
        if panel.mode != 'RGBA':
            panel = panel.convert('RGBA')
        
        result = Image.alpha_composite(panel, overlay)
        print(f"✅ Successfully rendered bubble at ({x}, {y})")
        return result.convert('RGB')
    
    def _render_text_in_bubble(self, draw: ImageDraw.Draw, text: str, 
                              coords: Tuple[int, int, int, int], style: ComicTextStyle):
        """Render wrapped text inside bubble with optimal font sizing"""
        x1, y1, x2, y2 = coords
        
        try:
            # Calculate optimal font size for this bubble
            bubble_width = x2 - x1
            bubble_height = y2 - y1
            optimal_font_size = self.calculate_optimal_font_size(text, style, bubble_width, bubble_height)
            
            # Use optimal font size
            font = get_system_font(style.font_family, optimal_font_size)
            
            # Wrap text with optimal font
            max_width = (x2 - x1) - 2 * style.padding
            wrapped_lines = wrap_text_pil(draw, text, font, max_width)
            
            if not wrapped_lines:
                return
            
            # Calculate line height and starting position with proper spacing
            line_height = draw.textbbox((0, 0), "Ay", font=font)[3] - draw.textbbox((0, 0), "Ay", font=font)[1]
            line_spacing = getattr(style, 'line_spacing', 12)  # Use style's line spacing or default
            total_text_height = len(wrapped_lines) * line_height + (len(wrapped_lines) - 1) * line_spacing
            
            start_y = y1 + style.padding + (y2 - y1 - 2 * style.padding - total_text_height) // 2
            
            # Draw each line centered with proper spacing
            for i, line in enumerate(wrapped_lines):
                line_bbox = draw.textbbox((0, 0), line, font=font)
                line_width = line_bbox[2] - line_bbox[0]
                
                line_x = x1 + style.padding + (max_width - line_width) // 2
                line_y = start_y + i * (line_height + line_spacing)
                
                # Draw text with outline
                draw_text_with_outline(
                    draw, 
                    (line_x, line_y), 
                    line, 
                    font, 
                    style.text_color, 
                    style.outline_color, 
                    style.outline_width
                )
                
            print(f"✅ Rendered text with adaptive font size {optimal_font_size}px in {bubble_width}x{bubble_height} bubble")
        
        except Exception as e:
            print(f"❌ Error rendering adaptive text in bubble: {e}")
    
    def _find_optimal_position(self, panel: Image.Image, bubble: TextBubble, 
                              panel_width: int, panel_height: int, style: ComicTextStyle) -> Tuple[int, int]:
        """Find optimal position for bubble with smart positioning when available"""
        
        # Try to use smart positioning if available
        try:
            from .smart_positioning import SmartTextPositioner
            positioner = SmartTextPositioner()
            analysis = positioner.analyze_image(panel)
            
            # Calculate bubble size for smart positioning
            max_bubble_width = min(int(panel_width * 0.9), 1000)
            bubble_width, bubble_height = self.calculate_bubble_size(bubble.text, style, max_bubble_width)
            
            # Create simple character mapping (could be enhanced)
            speaker_name = getattr(bubble, 'speaker_name', bubble.text.split(':')[0] if ':' in bubble.text else '')
            char_mapping = {speaker_name: 0} if speaker_name and analysis['characters'] else {}
            
            x, y, speaker_pos = positioner.get_optimal_position(
                speaker_name,
                bubble.bubble_type,
                analysis,
                char_mapping,
                (bubble_width, bubble_height)
            )
            
            # Update speaker position based on smart analysis
            bubble.speaker_position = speaker_pos
            return (x, y)
            
        except Exception as e:
            print(f"Smart positioning failed, trying simple positioning: {e}")
            # Try simple positioning as fallback
            try:
                from .simple_positioning import SimpleTextPositioner
                simple_positioner = SimpleTextPositioner()
                simple_positioner.reset_placement_tracking()
                
                # Calculate bubble size for simple positioning
                max_bubble_width = min(int(panel_width * 0.9), 1000)
                bubble_width, bubble_height = self.calculate_bubble_size(bubble.text, style, max_bubble_width)
                
                x, y, speaker_pos = simple_positioner.get_optimal_position(
                    bubble.bubble_type,
                    (bubble_width, bubble_height),
                    panel_width,
                    panel_height
                )
                
                bubble.speaker_position = speaker_pos
                return (x, y)
                
            except Exception as e2:
                print(f"Simple positioning also failed, using standard fallback: {e2}")
                # Fallback to original positioning logic
                pass
        
        # Enhanced positioning strategy with more variety for multiple bubbles (FALLBACK)
        position_preferences = {
            "top": (panel_width // 6, panel_height // 8),
            "center": (panel_width // 4, panel_height // 2),
            "bottom": (panel_width // 5, panel_height * 3 // 4),
            "left": (panel_width // 10, panel_height // 3),
            "right": (panel_width * 3 // 4, panel_height // 4)
        }
        
        # Additional positions for multiple bubbles
        if bubble.bubble_type == "thought":
            # Thoughts often go in upper areas
            return (panel_width // 3, panel_height // 6)
        elif bubble.bubble_type == "narration":
            # Narration boxes often go at top or bottom
            return (panel_width // 8, panel_height // 12)
        elif bubble.bubble_type == "sound_effect":
            # Sound effects can be more central or dramatic
            return (panel_width // 2, panel_height // 3)
        
        return position_preferences.get(bubble.speaker_position, position_preferences["center"])


# Convenience functions for easy integration with existing code
def create_text_bubble(text: str, bubble_type: str = "speech", emotion: str = "normal", 
                      position: Tuple[int, int] = (0, 0), speaker_position: str = "center") -> TextBubble:
    """Create a text bubble with specified parameters"""
    return TextBubble(
        text=text,
        position=position,
        bubble_type=bubble_type,
        emotion=emotion,
        speaker_position=speaker_position
    )

def render_comic_text(panel: Image.Image, bubbles: List[TextBubble], 
                     panel_width: int, panel_height: int) -> Image.Image:
    """Render multiple text bubbles on a comic panel"""
    renderer = ComicTextRenderer()
    result = panel.copy()
    
    for bubble in bubbles:
        result = renderer.render_text_bubble(result, bubble, panel_width, panel_height)
    
    return result 