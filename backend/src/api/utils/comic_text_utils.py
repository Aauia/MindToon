from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Dict, Optional, Literal
import math
from dataclasses import dataclass
from .font_utils import get_system_font, wrap_text_pil, draw_text_with_outline

"""
comic_text_utils.py

This module now supports a single wide, bottom-anchored speech bubble per panel.
All dialogue lines are combined into one bubble, placed at the bottom center.
"""

@dataclass
class ComicTextStyle:
    """Defines styling for comic text elements"""
    font_size: int = 16  # Smaller text size (was 36)
    text_color: str = "black"  # Clean black text
    outline_color: str = "black"  # Changed from white to black
    outline_width: int = 3  # Thicker outline by default
    bubble_color: str = "white"  # Clean white bubbles
    bubble_outline: str = "black"  # Clean black outline
    bubble_outline_width: int = 0  # No border (was 4)
    padding: int = 25  # Much more generous padding for better readability
    corner_radius: int = 0  # No rounded corners (was 15)
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
                font_size=14,  # Readable speech text
                bubble_color="white",
                bubble_outline="black",
                corner_radius=0,  # No rounded corners
                padding=25,  # Generous padding
                outline_width=3,
                line_spacing=12,
                outline_color="black"  # Black outline
            ),
            "thought": ComicTextStyle(
                font_size=20,  # Slightly smaller thought text
                bubble_color="white",
                bubble_outline="black",
                corner_radius=0,  # No rounded corners
                padding=25,  # Generous padding
                outline_width=2,
                line_spacing=12,
                outline_color="black"  # Black outline
            ),
            "narration": ComicTextStyle(
                font_size=20,  # Clean narration text
                bubble_color="#f8f8f8",  # Slightly off-white for narration
                bubble_outline="black",
                corner_radius=0,  # No rounded corners
                padding=25,  # Generous padding
                outline_width=2,
                line_spacing=12,
                outline_color="black"  # Black outline
            ),
            "sound_effect": ComicTextStyle(
                font_size=40,  # Bigger and bolder for sound effects
                text_color="black",
                outline_color="black",  # Black outline
                outline_width=6,  # Thicker outline for impact
                bubble_color="transparent",  # No bubble for SFX
                bubble_outline="transparent",
                padding=15,  # Less padding for SFX
                line_spacing=8
            ),
            "scream": ComicTextStyle(
                font_size=30,  # Bigger scream text
                text_color="black",
                outline_color="black",  # Black outline
                outline_width=4,  # Thicker outline for emphasis
                bubble_color="white",
                bubble_outline="black",
                corner_radius=0,  # No rounded corners
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
                test_font = get_system_font("default", test_size)
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
        """Calculate the required bubble size for given text - favor wide, compact bubbles"""
        try:
            font = get_system_font("default", style.font_size)
            # Create temporary draw object to measure text
            temp_img = Image.new('RGB', (1, 1))
            draw = ImageDraw.Draw(temp_img)
            # Use the full max_width for wrapping
            constrained_width = max_width
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
            # Always use the full width available, don't constrain to minimum
            bubble_width = max_width
            # Calculate height based on actual text needs
            bubble_height = text_height + 2 * style.padding
            # Ensure minimum height for readability
            bubble_height = max(bubble_height, style.font_size + 2 * style.padding)
            return bubble_width, bubble_height
        except Exception as e:
            print(f"Error calculating bubble size: {e}")
            return max_width, 120
    
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
            # Removed speech tail
        elif bubble_type == "narration":
            # Draw rectangular narration box
            self._draw_narration_box(draw, coords, style)
        else:
            # Regular speech bubble without tail
            self._draw_speech_bubble(draw, coords, style, speaker_pos)
            # Removed speech tail
    
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
            
            # Removed speech tail
    
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
        
        # Always use the bubble size that was already calculated and set by the caller
        bubble_width, bubble_height = bubble._calculated_size
        
        # USE EXACTLY the forced coordinates (no bounds checking)
        x = forced_x
        y = forced_y
        
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
        """Render wrapped text inside bubble with bounds checking to prevent overflow"""
        x1, y1, x2, y2 = coords
        try:
            bubble_width = x2 - x1
            bubble_height = y2 - y1
            print(f"🔍 DEBUG: Rendering text in bubble {bubble_width}x{bubble_height}")
            print(f"🔍 DEBUG: Text to render: '{text[:50]}...'")
            
            # Use the style's font size directly
            font = get_system_font("default", style.font_size)
            print(f"🔍 DEBUG: Using font size: {style.font_size}")
            
            # Calculate available text area with padding
            max_text_width = bubble_width - 2 * style.padding
            max_text_height = bubble_height - 2 * style.padding
            print(f"🔍 DEBUG: Available text area: {max_text_width}x{max_text_height}")
            
            # Wrap text to fit the available width
            all_lines = []
            for raw_line in text.splitlines():
                wrapped = wrap_text_pil(draw, raw_line, font, max_text_width)
                if wrapped:
                    all_lines.extend(wrapped)
            
            print(f"🔍 DEBUG: Total lines to render: {len(all_lines)}")
            if not all_lines:
                print("❌ No lines to render!")
                return
            
            # Calculate line height and spacing
            line_height = draw.textbbox((0, 0), "Ay", font=font)[3] - draw.textbbox((0, 0), "Ay", font=font)[1]
            line_spacing = getattr(style, 'line_spacing', 12)
            total_text_height = len(all_lines) * line_height + (len(all_lines) - 1) * line_spacing
            
            # Check if text fits in available height
            if total_text_height > max_text_height:
                # Truncate lines to fit (NOTE: This will cut off text if it doesn't fit. Consider reducing font size further for future improvements.)
                available_lines = max(1, (max_text_height - line_spacing) // (line_height + line_spacing))
                all_lines = all_lines[:available_lines]
                total_text_height = len(all_lines) * line_height + (len(all_lines) - 1) * line_spacing
                print(f"🔍 DEBUG: Truncated to {len(all_lines)} lines")
            
            # Center text vertically in available space
            start_y = y1 + style.padding + (max_text_height - total_text_height) // 2
            start_y = max(y1 + style.padding, start_y)  # Don't start below top padding
            
            print(f"🔍 DEBUG: Line height: {line_height}, Total text height: {total_text_height}")
            print(f"🔍 DEBUG: Start Y: {start_y}")
            
            # Draw each line centered horizontally
            for i, line in enumerate(all_lines):
                line_bbox = draw.textbbox((0, 0), line, font=font)
                line_width = line_bbox[2] - line_bbox[0]
                line_x = x1 + style.padding + (max_text_width - line_width) // 2
                line_y = start_y + i * (line_height + line_spacing)
                
                # Ensure line doesn't go outside bubble bounds
                line_x = max(x1 + style.padding, min(line_x, x2 - style.padding - line_width))
                line_y = max(y1 + style.padding, min(line_y, y2 - style.padding - line_height))
                
                print(f"🔍 DEBUG: Drawing line {i}: '{line}' at ({line_x}, {line_y})")
                
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
            
            print(f"✅ Successfully rendered {len(all_lines)} lines in {bubble_width}x{bubble_height} bubble")
            
        except Exception as e:
            print(f"❌ Error rendering text in bubble: {e}")
            import traceback
            traceback.print_exc()
    
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