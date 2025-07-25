from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple
import platform
import os

def get_system_font(font_name: str, size: int, fallback_font_name: str = "arial", fallback_size: int = 20):
    """Get system font - simplified to use only default font"""
    # Use only the default system font - no complex mappings
    return ImageFont.load_default()

def wrap_text_pil(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """Wrap text using PIL's textlength method"""
    if not text or not text.strip():
        return []

    lines = []
    current_line_words = []
    words = text.split(' ')
    
    for word in words:
        test_line = ' '.join(current_line_words + [word])
        if draw.textlength(test_line, font=font) <= max_width:
            current_line_words.append(word)
        else:
            if current_line_words:
                lines.append(' '.join(current_line_words))
                current_line_words = [word]
            else:
                # Break long word
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
                current_line_words = []
    
    if current_line_words:
        lines.append(' '.join(current_line_words))
        
    return lines

def draw_text_with_outline(draw: ImageDraw.Draw, xy: Tuple[int, int], text: str, 
                           font: ImageFont.FreeTypeFont, text_color: str, 
                           outline_color: str, outline_width: int):
    """Draw text - simplified to use only 1 layer, no outline"""
    # Draw only the main text - no outline, no layering
    draw.text(xy, text, font=font, fill=text_color) 