# Image-to-Image Generation with Stable Diffusion

This module provides image-to-image generation capabilities using Stable Diffusion XL, with support for genre and art style customization similar to the comic generation system.

## Features

- **Image-to-Image Transformation**: Transform existing images using Stable Diffusion XL
- **Genre & Art Style Support**: Apply different genres (action, romance, horror, etc.) and art styles (comic book, manga, watercolor, etc.)
- **Multiple Generation Options**: Single image generation or multiple variations
- **Flexible Parameters**: Control strength, CFG scale, steps, and dimensions
- **File Upload Support**: Upload images directly via API endpoints
- **URL Loading Support**: Load images directly from internet URLs
- **Multiple Image Formats**: Support for PNG, JPG, JPEG, GIF, and more
- **Health Monitoring**: Built-in health checks and status monitoring

## API Endpoints

### 1. Image-to-Image Generation
```
POST /api/ai/image-to-image
```

**Request Body:**
```json
{
  "source_image": "base64_encoded_image_string_or_url",
  "prompt": "Transform this into a superhero scene",
  "genre": "action",
  "art_style": "comic book",
  "strength": 0.35,
  "cfg_scale": 7.0,
  "steps": 20,
  "seed": 12345,
  "width": 1024,
  "height": 1024,
  "is_url": false
}
```

**Response:**
```json
{
  "success": true,
  "image_base64": "generated_image_base64_string",
  "error_message": null,
  "prompt_used": "Transform this into a superhero scene",
  "genre": "action",
  "art_style": "comic book",
  "strength": 0.35,
  "cfg_scale": 7.0,
  "steps": 20,
  "seed": 12345,
  "width": 1024,
  "height": 1024
}
```

### 2. Image Upload & Generation
```
POST /api/ai/image-to-image/upload
```

**Form Data:**
- `file`: Image file (PNG, JPG, etc.)
- `prompt`: Text prompt (optional)
- `genre`: Genre selection (default: "action")
- `art_style`: Art style selection (default: "comic book")
- `strength`: Transformation strength 0.0-1.0 (default: 0.35)
- `cfg_scale`: CFG scale 1.0-20.0 (default: 7.0)
- `steps`: Generation steps 10-50 (default: 20)
- `seed`: Random seed (optional)
- `width`: Output width (optional)
- `height`: Output height (optional)

### 3. URL Image Loading
```
POST /api/ai/image-to-image/load-url
```

**Request Body:**
```json
{
  "image_url": "https://example.com/image.png",
  "format": "PNG"
}
```

**Response:**
```json
{
  "success": true,
  "image_base64": "base64_encoded_image",
  "original_size": [800, 600],
  "format": "PNG"
}
```

### 4. Image Variations
```
POST /api/ai/image-to-image/variations
```

**Request Body:**
```json
{
  "source_image": "base64_encoded_image_string_or_url",
  "genre": "action",
  "art_style": "comic book",
  "num_variations": 3,
  "strength": 0.35,
  "cfg_scale": 7.0,
  "steps": 20,
  "seed": 12345,
  "is_url": false
}
```

**Response:**
```json
{
  "success": true,
  "variations": ["base64_image_1", "base64_image_2", "base64_image_3"],
  "error_message": null,
  "genre": "action",
  "art_style": "comic book",
  "strength": 0.35,
  "cfg_scale": 7.0,
  "steps": 20,
  "seed": 12345
}
```

### 5. Available Genres
```
GET /api/ai/genres
```

**Response:**
```json
[
  "action", "adventure", "comedy", "drama", "fantasy",
  "horror", "mystery", "romance", "sci-fi", "slice-of-life"
]
```

### 6. Available Art Styles
```
GET /api/ai/art-styles
```

**Response:**
```json
[
  "anime", "cartoon", "comic book", "manga", "minimalist",
  "noir", "pixel art", "pop art", "realistic", "sketch",
  "storybook", "vintage", "watercolor"
]
```

### 7. Genre Details
```
GET /api/ai/genres/{genre}
```

**Response:**
```json
{
  "genre": "action",
  "details": {
    "mood": "intense, dynamic, powerful, explosive",
    "palette": "bold reds and oranges, high contrast, dramatic colors",
    "lighting": "dynamic lighting, explosion glows, dramatic spotlights",
    "font_style": "bold angular, impact",
    "atmosphere": "intense, fast-paced, dramatic",
    "visual_cues": "motion blur, impact lines, detailed explosions, epic scale"
  }
}
```

### 8. Art Style Details
```
GET /api/ai/art-styles/{art_style}
```

**Response:**
```json
{
  "art_style": "comic book",
  "description": "Classic American comic book art style. Characterized by strong, impactful linework, dynamic action poses, and a vibrant, high-contrast color palette often with distinct black inks..."
}
```

### 9. Health Check
```
GET /api/ai/image-to-image/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "image-to-image",
  "available_genres": 10,
  "available_art_styles": 13,
  "features": {
    "url_loading": true,
    "base64_support": true,
    "file_upload": true,
    "variations": true
  }
}
```

## Usage Examples

### Python Example
```python
import asyncio
import base64
from api.ai.image2image import ImageToImageRequest, process_image_to_image

async def transform_image():
    # Method 1: Load image from file and convert to base64
    with open("input_image.png", "rb") as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Create request with base64 image
    request = ImageToImageRequest(
        source_image=image_base64,
        prompt="Transform this into a cyberpunk scene",
        genre="sci-fi",
        art_style="anime",
        strength=0.4,
        cfg_scale=7.0,
        steps=25,
        is_url=False
    )
    
    # Generate image
    result = await process_image_to_image(request)
    
    if result.success:
        # Save the generated image
        output_data = base64.b64decode(result.image_base64)
        with open("output_image.png", "wb") as f:
            f.write(output_data)
        print("Image generated successfully!")
    else:
        print(f"Generation failed: {result.error_message}")

# Method 2: Use URL directly
async def transform_url_image():
    # Create request with URL
    request = ImageToImageRequest(
        source_image="https://example.com/image.png",
        prompt="Transform this into a fantasy scene",
        genre="fantasy",
        art_style="watercolor",
        strength=0.35,
        is_url=True
    )
    
    # Generate image
    result = await process_image_to_image(request)
    
    if result.success:
        # Save the generated image
        output_data = base64.b64decode(result.image_base64)
        with open("url_output_image.png", "wb") as f:
            f.write(output_data)
        print("URL image generated successfully!")
    else:
        print(f"Generation failed: {result.error_message}")

# Run the functions
asyncio.run(transform_image())
asyncio.run(transform_url_image())
```

### cURL Example
```bash
# Upload image and generate
curl -X POST "http://localhost:8000/api/ai/image-to-image/upload" \
  -F "file=@input_image.png" \
  -F "prompt=Transform this into a fantasy scene" \
  -F "genre=fantasy" \
  -F "art_style=watercolor" \
  -F "strength=0.35"

# Generate with base64 image
curl -X POST "http://localhost:8000/api/ai/image-to-image" \
  -H "Content-Type: application/json" \
  -d '{
    "source_image": "base64_encoded_image",
    "prompt": "Transform this into a horror scene",
    "genre": "horror",
    "art_style": "noir",
    "strength": 0.5,
    "is_url": false
  }'

# Generate with URL image
curl -X POST "http://localhost:8000/api/ai/image-to-image" \
  -H "Content-Type: application/json" \
  -d '{
    "source_image": "https://example.com/image.png",
    "prompt": "Transform this into a sci-fi scene",
    "genre": "sci-fi",
    "art_style": "anime",
    "strength": 0.4,
    "is_url": true
  }'

# Load image from URL
curl -X POST "http://localhost:8000/api/ai/image-to-image/load-url" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.png",
    "format": "PNG"
  }'
```

## Parameters

### Strength (0.0 - 1.0)
- **0.0**: Minimal transformation, keeps original image mostly intact
- **0.35**: Balanced transformation (recommended default)
- **0.7**: Strong transformation
- **1.0**: Maximum transformation, may completely change the image

### CFG Scale (1.0 - 20.0)
- **1.0**: Minimal prompt influence
- **7.0**: Balanced prompt influence (recommended default)
- **15.0**: Strong prompt influence
- **20.0**: Maximum prompt influence

### Steps (10 - 50)
- **10**: Fast generation, lower quality
- **20**: Balanced speed/quality (recommended default)
- **30**: Higher quality, slower generation
- **50**: Maximum quality, slowest generation

## Supported Genres

1. **Action**: Intense, dynamic, powerful scenes
2. **Adventure**: Exploratory, thrilling, discovery-driven
3. **Comedy**: Lighthearted, playful, energetic
4. **Drama**: Emotional, realistic, character-focused
5. **Fantasy**: Magical, mystical, enchanting
6. **Horror**: Tense, eerie, dark, foreboding
7. **Mystery**: Suspenseful, intriguing, noir
8. **Romance**: Tender, dreamy, warm, intimate
9. **Sci-fi**: Futuristic, technological, vast
10. **Slice-of-life**: Calm, heartwarming, reflective

## Supported Art Styles

1. **Anime**: Modern Japanese anime style
2. **Cartoon**: Vibrant, expressive cartoon illustration
3. **Comic Book**: Classic American comic book art
4. **Manga**: Authentic Japanese manga style
5. **Minimalist**: Clean and sleek minimalist art
6. **Noir**: Gritty, high-contrast film noir style
7. **Pixel Art**: Distinctive pixel art style
8. **Pop Art**: Bold and graphic Pop Art style
9. **Realistic**: Photorealistic digital painting
10. **Sketch**: Expressive pencil sketch style
11. **Storybook**: Whimsical and warm storybook style
12. **Vintage**: Nostalgic vintage illustration style
13. **Watercolor**: Evocative watercolor painting style

## Environment Variables

Required:
- `STABILITY_API_KEY`: Your Stability AI API key

## Testing

Run the test scripts to verify functionality:

```bash
# Basic functionality test
python test_image2image.py

# URL loading test
python example_url_image2image.py
```

These will:
1. Test available genres and art styles
2. Create test images
3. Generate image-to-image transformations
4. Test URL loading functionality
5. Save output images for inspection

## Error Handling

The API provides detailed error messages for common issues:
- Invalid API key
- Invalid image format
- Network timeouts
- Invalid URLs or failed downloads
- Parameter validation errors
- Generation failures

## Performance Notes

- Image generation typically takes 10-30 seconds
- Larger images and higher step counts increase generation time
- Multiple variations are generated concurrently for better performance
- The API automatically maps dimensions to Stable Diffusion XL's allowed sizes

## Integration with Comic Generation

This image-to-image system uses the same genre and art style mappings as the comic generation system, ensuring consistency across the entire application. The same validation and enhancement functions are shared between both systems. 