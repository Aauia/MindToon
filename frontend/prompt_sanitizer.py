import re
from typing import List, Dict

class PromptSanitizer:
    """
    Sanitizes prompts to avoid Stability AI content moderation issues
    """
    
    def __init__(self):
        # Words that often trigger content moderation
        self.flagged_words = [
            'violence', 'violent', 'blood', 'gore', 'death', 'kill', 'murder',
            'weapon', 'gun', 'knife', 'sword', 'fight', 'battle', 'war',
            'nude', 'naked', 'sexy', 'erotic', 'explicit', 'adult',
            'drug', 'alcohol', 'smoking', 'cigarette', 'beer', 'wine',
            'hate', 'racism', 'discrimination', 'offensive',
            'disturbing', 'scary', 'horror', 'nightmare',
            'political', 'religion', 'religious'
        ]
        
        # Safe replacements for problematic terms
        self.safe_replacements = {
            'violence': 'action',
            'violent': 'dynamic',
            'blood': 'red liquid',
            'death': 'ending',
            'kill': 'defeat',
            'murder': 'conflict',
            'weapon': 'tool',
            'gun': 'device',
            'knife': 'blade',
            'sword': 'blade',
            'fight': 'confrontation',
            'battle': 'encounter',
            'war': 'conflict',
            'scary': 'mysterious',
            'horror': 'suspense',
            'nightmare': 'dream'
        }
    
    def sanitize_prompt(self, prompt: str) -> str:
        """
        Sanitize a single prompt to make it safer for Stability AI
        """
        sanitized = prompt.lower()
        
        # Replace flagged words with safe alternatives
        for word, replacement in self.safe_replacements.items():
            sanitized = re.sub(r'\b' + word + r'\b', replacement, sanitized, flags=re.IGNORECASE)
        
        # Remove remaining flagged words that don't have replacements
        for word in self.flagged_words:
            if word not in self.safe_replacements:
                sanitized = re.sub(r'\b' + word + r'\b', '', sanitized, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        sanitized = ' '.join(sanitized.split())
        
        # Ensure family-friendly, artistic focus
        if not any(safe_word in sanitized for safe_word in ['comic', 'art', 'illustration', 'cartoon']):
            sanitized = f"comic book art style, {sanitized}"
        
        # Add positive artistic terms
        sanitized = f"{sanitized}, professional illustration, clean art style"
        
        return sanitized.strip()
    
    def sanitize_comic_panels(self, panels_data: List[Dict]) -> List[Dict]:
        """
        Sanitize all prompts in comic panels data
        """
        sanitized_panels = []
        
        for panel in panels_data:
            sanitized_panel = panel.copy()
            
            # Sanitize image prompt
            if 'image_prompt' in panel:
                sanitized_panel['image_prompt'] = self.sanitize_prompt(panel['image_prompt'])
            
            # Sanitize dialogue (less strict)
            if 'dialogue' in panel:
                sanitized_panel['dialogue'] = self.sanitize_dialogue(panel['dialogue'])
            
            sanitized_panels.append(sanitized_panel)
        
        return sanitized_panels
    
    def sanitize_dialogue(self, dialogue: str) -> str:
        """
        Light sanitization for dialogue text
        """
        # Just remove extreme content, keep the dialogue natural
        sanitized = dialogue
        extreme_words = ['kill', 'murder', 'death', 'blood', 'violence']
        
        for word in extreme_words:
            sanitized = re.sub(r'\b' + word + r'\b', '***', sanitized, flags=re.IGNORECASE)
        
        return sanitized

# Usage example for your backend:
def sanitize_comic_generation_request(concept: str, panels_data: List[Dict]) -> tuple:
    """
    Sanitize both the concept and panels data for comic generation
    """
    sanitizer = PromptSanitizer()
    
    # Sanitize the main concept
    sanitized_concept = sanitizer.sanitize_prompt(concept)
    
    # Sanitize all panel prompts
    sanitized_panels = sanitizer.sanitize_comic_panels(panels_data)
    
    return sanitized_concept, sanitized_panels

# Example usage:
if __name__ == "__main__":
    sanitizer = PromptSanitizer()
    
    # Test prompt
    test_prompt = "Maia draws her sword and prepares for a violent battle"
    sanitized = sanitizer.sanitize_prompt(test_prompt)
    
    print(f"Original: {test_prompt}")
    print(f"Sanitized: {sanitized}") 