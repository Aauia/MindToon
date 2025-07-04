from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import List, Tuple, Optional, Dict, Literal
import math
import random
from dataclasses import dataclass
from .image_utils import get_system_font

@dataclass
class LetteringEffect:
    """Defines special lettering effects for comic text"""
    name: str
    outline_width: int = 2
    shadow_offset: Tuple[int, int] = (2, 2)
    shadow_color: str = "gray"
    gradient_colors: Optional[List[str]] = None
    texture: Optional[str] = None  # "rough", "smooth", "digital", "hand_drawn"
    animation_type: Optional[str] = None  # "shake", "wobble", "glow"

class ComicTypography:
    """Advanced typography and lettering effects for comics"""
    
    def __init__(self):
        # Predefined lettering effects
        self.effects = {
            "classic": LetteringEffect(
                name="classic",
                outline_width=2,
                shadow_offset=(1, 1),
                shadow_color="#333333"
            ),
            "bold_impact": LetteringEffect(
                name="bold_impact", 
                outline_width=4,
                shadow_offset=(3, 3),
                shadow_color="black",
                gradient_colors=["#ff0000", "#darkred"]
            ),
            "whisper": LetteringEffect(
                name="whisper",
                outline_width=1,
                shadow_offset=(0, 0),
                gradient_colors=["#cccccc", "#999999"]
            ),
            "shout": LetteringEffect(
                name="shout",
                outline_width=5,
                shadow_offset=(4, 4),
                shadow_color="black",
                gradient_colors=["#ff4500", "#red"],
                animation_type="shake"
            ),
            "thought": LetteringEffect(
                name="thought",
                outline_width=1,
                shadow_offset=(1, 1),
                shadow_color="#87ceeb",
                gradient_colors=["#4682b4", "#87ceeb"],
                texture="soft"
            ),
            "sound_effect": LetteringEffect(
                name="sound_effect",
                outline_width=6,
                shadow_offset=(5, 5),
                shadow_color="yellow",
                gradient_colors=["#ff6347", "#ffa500"],
                texture="rough"
            ),
            "magical": LetteringEffect(
                name="magical",
                outline_width=3,
                shadow_offset=(2, 2), 
                shadow_color="purple",
                gradient_colors=["#9370db", "#dda0dd"],
                animation_type="glow"
            ),
            "retro": LetteringEffect(
                name="retro",
                outline_width=3,
                shadow_offset=(4, 4),
                shadow_color="#8b4513",
                gradient_colors=["#ffd700", "#ffb347"],
                texture="vintage"
            )
        }
    
    def create_text_with_effect(self, text: str, font_size: int, effect_name: str, 
                               font_family: str = "arial_bold") -> Image.Image:
        """Create text with special lettering effects"""
        effect = self.effects.get(effect_name, self.effects["classic"])
        
        # Calculate text dimensions
        font = get_system_font(font_family, font_size)
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        text_bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Create image with padding for effects
        padding = max(effect.outline_width * 2, max(effect.shadow_offset)) + 10
        img_width = text_width + padding * 2
        img_height = text_height + padding * 2
        
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        text_x = padding
        text_y = padding - text_bbox[1]  # Adjust for baseline
        
        # Apply effects based on effect type
        if effect.name == "sound_effect":
            return self._create_sound_effect_text(text, font, img, text_x, text_y, effect)
        elif effect.animation_type == "shake":
            return self._create_shake_text(text, font, img, text_x, text_y, effect)
        elif effect.animation_type == "glow":
            return self._create_glow_text(text, font, img, text_x, text_y, effect)
        else:
            return self._create_standard_text(text, font, img, text_x, text_y, effect)
    
    def _create_standard_text(self, text: str, font: ImageFont.FreeTypeFont, 
                             img: Image.Image, x: int, y: int, effect: LetteringEffect) -> Image.Image:
        """Create text with standard effects"""
        draw = ImageDraw.Draw(img)
        
        # Draw shadow first
        if effect.shadow_offset != (0, 0):
            shadow_x = x + effect.shadow_offset[0]
            shadow_y = y + effect.shadow_offset[1]
            self._draw_text_outline(draw, shadow_x, shadow_y, text, font, effect.shadow_color, 1)
        
        # Draw outline
        if effect.outline_width > 0:
            outline_color = "black"
            if effect.gradient_colors:
                outline_color = effect.gradient_colors[-1]  # Use darker color for outline
            self._draw_text_outline(draw, x, y, text, font, outline_color, effect.outline_width)
        
        # Draw main text
        text_color = "black"
        if effect.gradient_colors:
            text_color = effect.gradient_colors[0]
        
        draw.text((x, y), text, font=font, fill=text_color)
        
        return img
    
    def _create_sound_effect_text(self, text: str, font: ImageFont.FreeTypeFont,
                                 img: Image.Image, x: int, y: int, effect: LetteringEffect) -> Image.Image:
        """Create dramatic sound effect text"""
        draw = ImageDraw.Draw(img)
        
        # Multiple outline layers for depth
        outline_colors = ["black", "#333333", "#666666"]
        for i, color in enumerate(outline_colors):
            outline_width = effect.outline_width - i
            if outline_width > 0:
                self._draw_text_outline(draw, x, y, text, font, color, outline_width)
        
        # Main text with gradient effect
        if effect.gradient_colors and len(effect.gradient_colors) >= 2:
            self._draw_gradient_text(draw, x, y, text, font, effect.gradient_colors)
        else:
            draw.text((x, y), text, font=font, fill="red")
        
        return img
    
    def _create_shake_text(self, text: str, font: ImageFont.FreeTypeFont,
                          img: Image.Image, x: int, y: int, effect: LetteringEffect) -> Image.Image:
        """Create text with shake effect"""
        draw = ImageDraw.Draw(img)
        
        # Create multiple offset versions for shake effect
        shake_offsets = [(0, 0), (1, -1), (-1, 1), (1, 0), (0, 1)]
        
        for i, (offset_x, offset_y) in enumerate(shake_offsets):
            alpha = 255 - i * 40  # Decreasing opacity
            if alpha > 0:
                # Create temporary image for this layer
                temp_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
                temp_draw = ImageDraw.Draw(temp_img)
                
                shake_x = x + offset_x
                shake_y = y + offset_y
                
                # Draw outline
                self._draw_text_outline(temp_draw, shake_x, shake_y, text, font, "black", effect.outline_width)
                
                # Draw text
                text_color = effect.gradient_colors[0] if effect.gradient_colors else "red"
                temp_draw.text((shake_x, shake_y), text, font=font, fill=text_color)
                
                # Apply alpha and composite
                temp_img.putalpha(alpha)
                img = Image.alpha_composite(img, temp_img)
        
        return img
    
    def _create_glow_text(self, text: str, font: ImageFont.FreeTypeFont,
                         img: Image.Image, x: int, y: int, effect: LetteringEffect) -> Image.Image:
        """Create text with glow effect"""
        # Create glow layers
        glow_layers = [
            {"offset": 8, "color": effect.gradient_colors[1] if effect.gradient_colors else "purple", "alpha": 50},
            {"offset": 5, "color": effect.gradient_colors[0] if effect.gradient_colors else "magenta", "alpha": 100},
            {"offset": 2, "color": "white", "alpha": 150}
        ]
        
        for layer in glow_layers:
            glow_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_img)
            
            # Draw glow outline
            self._draw_text_outline(glow_draw, x, y, text, font, layer["color"], layer["offset"])
            
            # Apply blur for glow effect
            glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=layer["offset"]//2))
            glow_img.putalpha(layer["alpha"])
            
            img = Image.alpha_composite(img, glow_img)
        
        # Draw main text on top
        draw = ImageDraw.Draw(img)
        self._draw_text_outline(draw, x, y, text, font, "black", effect.outline_width)
        draw.text((x, y), text, font=font, fill="white")
        
        return img
    
    def _draw_text_outline(self, draw: ImageDraw.Draw, x: int, y: int, text: str,
                          font: ImageFont.FreeTypeFont, color: str, width: int):
        """Draw text outline"""
        for offset_x in range(-width, width + 1):
            for offset_y in range(-width, width + 1):
                if offset_x * offset_x + offset_y * offset_y <= width * width:
                    draw.text((x + offset_x, y + offset_y), text, font=font, fill=color)
    
    def _draw_gradient_text(self, draw: ImageDraw.Draw, x: int, y: int, text: str,
                           font: ImageFont.FreeTypeFont, colors: List[str]):
        """Draw text with gradient effect (simplified version)"""
        # For now, just use the first color - could be enhanced with actual gradient
        draw.text((x, y), text, font=font, fill=colors[0])
    
    def create_comic_title(self, title: str, style: str = "classic") -> Image.Image:
        """Create a stylized comic title"""
        return self.create_text_with_effect(title, 72, style, "arial_black")
    
    def create_sound_effect(self, sound: str, intensity: str = "medium") -> Image.Image:
        """Create a sound effect with appropriate styling"""
        effect_map = {
            "low": "whisper",
            "medium": "sound_effect", 
            "high": "shout",
            "extreme": "bold_impact"
        }
        
        effect_name = effect_map.get(intensity, "sound_effect")
        font_size = {
            "low": 36,
            "medium": 54,
            "high": 72,
            "extreme": 96
        }.get(intensity, 54)
        
        return self.create_text_with_effect(sound, font_size, effect_name, "arial_black")
    
    def create_dialogue_text(self, text: str, emotion: str = "normal") -> Image.Image:
        """Create dialogue text with emotion-appropriate styling"""
        emotion_effects = {
            "normal": "classic",
            "angry": "bold_impact", 
            "whisper": "whisper",
            "shout": "shout",
            "thought": "thought",
            "excited": "magical",
            "sad": "whisper"
        }
        
        effect = emotion_effects.get(emotion, "classic")
        return self.create_text_with_effect(text, 32, effect)


class ComicLettering:
    """Comic lettering and balloon management"""
    
    def __init__(self):
        self.typography = ComicTypography()
    
    def create_speech_balloon(self, text: str, balloon_type: str = "speech", 
                             emotion: str = "normal", size: Tuple[int, int] = (200, 100)) -> Image.Image:
        """Create a complete speech balloon with text"""
        width, height = size
        
        # Create balloon background
        balloon = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(balloon)
        
        # Balloon styling based on type
        if balloon_type == "thought":
            # Cloud-like thought bubble
            self._draw_thought_balloon(draw, width, height)
        elif balloon_type == "scream":
            # Jagged scream balloon
            self._draw_scream_balloon(draw, width, height)
        else:
            # Standard speech balloon
            self._draw_speech_balloon(draw, width, height)
        
        # Add text
        text_img = self.typography.create_dialogue_text(text, emotion)
        
        # Center text in balloon
        text_x = (width - text_img.width) // 2
        text_y = (height - text_img.height) // 2
        
        balloon.paste(text_img, (text_x, text_y), text_img)
        
        return balloon
    
    def _draw_speech_balloon(self, draw: ImageDraw.Draw, width: int, height: int):
        """Draw standard speech balloon"""
        # Main balloon
        draw.rounded_rectangle((10, 10, width-10, height-20), radius=20, fill="white", outline="black", width=3)
        
        # Tail
        tail_points = [(20, height-20), (15, height-5), (35, height-15)]
        draw.polygon(tail_points, fill="white", outline="black")
    
    def _draw_thought_balloon(self, draw: ImageDraw.Draw, width: int, height: int):
        """Draw thought balloon with cloud effect"""
        # Main cloud
        draw.rounded_rectangle((10, 10, width-10, height-20), radius=30, fill="white", outline="black", width=2)
        
        # Small thought circles
        for i, size in enumerate([12, 8, 5]):
            x = 20 + i * 10
            y = height - 15 + i * 5
            draw.ellipse((x-size, y-size, x+size, y+size), fill="white", outline="black", width=2)
    
    def _draw_scream_balloon(self, draw: ImageDraw.Draw, width: int, height: int):
        """Draw jagged scream balloon"""
        # Create jagged edge points
        points = []
        segments = 16
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            # Random jagged radius
            radius = 80 + random.randint(-15, 15)
            x = width//2 + radius * math.cos(angle)
            y = height//2 + radius * math.sin(angle) * 0.7  # Slightly flattened
            points.append((x, y))
        
        draw.polygon(points, fill="white", outline="black", width=3)


# Convenience functions
def create_comic_text(text: str, style: str = "classic", font_size: int = 32) -> Image.Image:
    """Quick function to create comic text with effects"""
    typography = ComicTypography()
    return typography.create_text_with_effect(text, font_size, style)

def create_sound_effect_text(sound: str, intensity: str = "medium") -> Image.Image:
    """Quick function to create sound effect text"""
    typography = ComicTypography()
    return typography.create_sound_effect(sound, intensity)

def create_speech_balloon(text: str, balloon_type: str = "speech", emotion: str = "normal") -> Image.Image:
    """Quick function to create speech balloon"""
    lettering = ComicLettering()
    return lettering.create_speech_balloon(text, balloon_type, emotion) 