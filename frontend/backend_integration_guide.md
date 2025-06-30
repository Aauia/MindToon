# Backend Integration Guide

## Issue Analysis

Your logs show that:
1. ✅ **Backend successfully generates comics** with 1065760-byte images
2. ❌ **Individual panel generation fails** with 403 content moderation errors
3. ✅ **iOS app receives complete comic data** but may have display issues

## Content Moderation Fix

### 1. Add Prompt Sanitization to Your Backend

In your `generate_complete_comic` function, add this before calling Stability AI:

```python
from prompt_sanitizer import PromptSanitizer

def generate_complete_comic(concept, genre, art_style):
    sanitizer = PromptSanitizer()
    
    # Sanitize the main concept
    sanitized_concept = sanitizer.sanitize_prompt(concept)
    
    # Generate panels with sanitized prompts
    panels = generate_panels(sanitized_concept, genre, art_style)
    
    # Sanitize each panel's image prompt before sending to Stability AI
    for panel in panels:
        if 'image_prompt' in panel:
            panel['image_prompt'] = sanitizer.sanitize_prompt(panel['image_prompt'])
    
    # Continue with your existing logic...
```

### 2. Alternative: Use Different Image Generation

Consider switching to:
- **DALL-E 3** (less strict content moderation)
- **Midjourney API** (when available)
- **Local Stable Diffusion** (no content moderation)

### 3. Prompt Enhancement

Add these safe terms to all image prompts:
```python
safe_terms = "comic book art style, family-friendly, cartoon illustration, clean art, professional artwork"
enhanced_prompt = f"{original_prompt}, {safe_terms}"
```

## iOS App Improvements

### ✅ Already Fixed:
1. **Download functionality** - saves to photo library
2. **Share functionality** - uses UIActivityViewController  
3. **Photo permissions** - added to Info.plist

### Next Steps:
1. Test the complete comic display with working backend
2. Verify download functionality works
3. Test share functionality

## Testing Your Backend

Run this test to verify sanitization:

```python
from prompt_sanitizer import PromptSanitizer

sanitizer = PromptSanitizer()

# Test your current failing prompt
test_prompt = "Maia (16-year-old girl, long dark hair, tied in a ponytail, leather armor with the symbol of the kingdom, determined expression)"

sanitized = sanitizer.sanitize_prompt(test_prompt)
print(f"Sanitized: {sanitized}")
```

## Expected Results

After implementing sanitization:
- ✅ No more 403 content moderation errors
- ✅ All panels generate successfully
- ✅ Complete comic sheet displays properly
- ✅ Download/share functionality works

## Debug Your Current Issue

Add this logging to your backend:

```python
print(f"🔍 Prompt before Stability AI: {prompt}")
print(f"🔍 Prompt length: {len(prompt)} characters")

# Check for flagged words
flagged_words = ['violence', 'weapon', 'fight', 'battle', 'sword']
found_words = [word for word in flagged_words if word.lower() in prompt.lower()]
if found_words:
    print(f"⚠️ Potentially flagged words found: {found_words}")
``` 