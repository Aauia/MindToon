#!/usr/bin/env python3
"""
Test script for image-to-image functionality
"""

import asyncio
import base64
import os
from PIL import Image
from io import BytesIO
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.ai.image2image import (
    ImageToImageRequest,
    process_image_to_image,
    get_available_genres,
    get_available_art_styles,
    get_genre_details,
    get_art_style_details
)

def create_test_image(width=512, height=512, color=(255, 100, 100)):
    """Create a simple test image"""
    image = Image.new('RGB', (width, height), color)
    
    # Add some simple shapes for testing
    from PIL import ImageDraw
    draw = ImageDraw.Draw(image)
    
    # Draw a simple circle
    draw.ellipse([50, 50, 200, 200], fill=(100, 255, 100), outline=(0, 0, 0), width=3)
    
    # Draw a rectangle
    draw.rectangle([250, 250, 400, 400], fill=(100, 100, 255), outline=(0, 0, 0), width=3)
    
    return image

def image_to_base64(image):
    """Convert PIL image to base64 string"""
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

async def test_image_to_image():
    """Test the image-to-image functionality"""
    print("🧪 Testing Image-to-Image Functionality")
    print("=" * 50)
    
    # Test 1: Check available genres and art styles
    print("\n1. Testing available genres and art styles:")
    genres = get_available_genres()
    art_styles = get_available_art_styles()
    print(f"   Available genres: {genres}")
    print(f"   Available art styles: {art_styles}")
    
    # Test 2: Get genre and art style details
    print("\n2. Testing genre and art style details:")
    genre_details = get_genre_details("action")
    art_style_details = get_art_style_details("comic book")
    print(f"   Action genre details: {genre_details['mood']}")
    print(f"   Comic book art style: {art_style_details[:100]}...")
    
    # Test 3: Create test image
    print("\n3. Creating test image...")
    test_image = create_test_image(512, 512)
    image_base64 = image_to_base64(test_image)
    print(f"   Test image created: {test_image.size[0]}x{test_image.size[1]} pixels")
    
    # Test 4: Test image-to-image generation
    print("\n4. Testing image-to-image generation...")
    request = ImageToImageRequest(
        source_image=image_base64,
        prompt="Transform this into a superhero comic panel with dramatic lighting",
        genre="action",
        art_style="comic book",
        strength=0.35,
        cfg_scale=7.0,
        steps=20
    )
    
    try:
        result = await process_image_to_image(request)
        if result.success:
            print("   ✅ Image-to-image generation successful!")
            print(f"   📏 Output dimensions: {result.width}x{result.height}")
            print(f"   🌱 Seed used: {result.seed}")
            print(f"   🎭 Genre: {result.genre}")
            print(f"   🎨 Art style: {result.art_style}")
            
            # Save the result image
            if result.image_base64:
                output_image_data = base64.b64decode(result.image_base64)
                output_image = Image.open(BytesIO(output_image_data))
                output_image.save("test_output_image.png")
                print("   💾 Output image saved as 'test_output_image.png'")
        else:
            print(f"   ❌ Image-to-image generation failed: {result.error_message}")
            
    except Exception as e:
        print(f"   ❌ Test failed with exception: {str(e)}")
    
    # Test 5: Test with different genre and art style
    print("\n5. Testing with different genre and art style...")
    request2 = ImageToImageRequest(
        source_image=image_base64,
        prompt="Transform this into a romantic scene with soft lighting",
        genre="romance",
        art_style="watercolor",
        strength=0.4,
        cfg_scale=7.0,
        steps=20
    )
    
    try:
        result2 = await process_image_to_image(request2)
        if result2.success:
            print("   ✅ Second image-to-image generation successful!")
            print(f"   🎭 Genre: {result2.genre}")
            print(f"   🎨 Art style: {result2.art_style}")
            
            # Save the second result image
            if result2.image_base64:
                output_image_data2 = base64.b64decode(result2.image_base64)
                output_image2 = Image.open(BytesIO(output_image_data2))
                output_image2.save("test_output_image2.png")
                print("   💾 Second output image saved as 'test_output_image2.png'")
        else:
            print(f"   ❌ Second generation failed: {result2.error_message}")
            
    except Exception as e:
        print(f"   ❌ Second test failed with exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🧪 Image-to-Image Testing Complete!")

if __name__ == "__main__":
    # Check if STABILITY_API_KEY is set
    if not os.getenv("STABILITY_API_KEY"):
        print("❌ STABILITY_API_KEY environment variable not set!")
        print("Please set your Stability AI API key before running this test.")
        sys.exit(1)
    
    # Run the test
    asyncio.run(test_image_to_image()) 