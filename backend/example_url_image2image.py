#!/usr/bin/env python3
"""
Example script demonstrating image-to-image with URL loading
"""

import asyncio
import base64
import os
import sys
from PIL import Image, ImageDraw
from io import BytesIO

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.ai.image2image import (
    ImageToImageRequest,
    ImageToImageVariationRequest,
    ImageLoadRequest,
    process_image_to_image,
    generate_image_variations,
    load_image_from_url_endpoint,
    get_available_genres,
    get_available_art_styles
)

def save_base64_image(base64_string, filename):
    """Save base64 image to file"""
    image_data = base64.b64decode(base64_string)
    image = Image.open(BytesIO(image_data))
    image.save(filename)
    print(f"💾 Saved: {filename}")

async def example_url_loading():
    """Example of loading images from URLs"""
    print("🌐 Example 1: Loading Images from URLs")
    print("-" * 50)
    
    # Sample image URLs (these are public domain/CC0 images)
    sample_urls = [
        "https://picsum.photos/512/512",  # Random image
        "https://via.placeholder.com/512x512/FF0000/FFFFFF?text=Red+Square",  # Red square
        "https://via.placeholder.com/512x512/00FF00/FFFFFF?text=Green+Circle",  # Green circle
    ]
    
    for i, url in enumerate(sample_urls, 1):
        print(f"\n🔄 Loading image {i} from URL: {url}")
        
        # Load image from URL
        load_request = ImageLoadRequest(image_url=url, format="PNG")
        load_result = await load_image_from_url_endpoint(load_request)
        
        if load_result.success:
            print(f"✅ Successfully loaded image {i}")
            print(f"   📏 Size: {load_result.original_size[0]}x{load_result.original_size[1]} pixels")
            
            # Save the loaded image
            save_base64_image(load_result.image_base64, f"loaded_image_{i}.png")
            
            # Transform the loaded image
            print(f"🔄 Transforming image {i}...")
            transform_request = ImageToImageRequest(
                source_image=url,
                prompt=f"Transform this into a {['action', 'romance', 'fantasy'][i-1]} scene",
                genre=["action", "romance", "fantasy"][i-1],
                art_style=["comic book", "watercolor", "storybook"][i-1],
                strength=0.4,
                cfg_scale=7.0,
                steps=20,
                is_url=True
            )
            
            transform_result = await process_image_to_image(transform_request)
            
            if transform_result.success:
                print(f"✅ Transformation successful!")
                save_base64_image(transform_result.image_base64, f"transformed_image_{i}.png")
            else:
                print(f"❌ Transformation failed: {transform_result.error_message}")
        else:
            print(f"❌ Failed to load image {i}: {load_result.error_message}")

async def example_internet_images():
    """Example with real internet images"""
    print("\n🌐 Example 2: Real Internet Images")
    print("-" * 50)
    
    # Some interesting image URLs (public domain/CC0)
    internet_images = [
        {
            "url": "https://picsum.photos/800/600",
            "prompt": "Transform this into a cyberpunk cityscape with neon lights",
            "genre": "sci-fi",
            "art_style": "anime"
        },
        {
            "url": "https://via.placeholder.com/800x600/4A90E2/FFFFFF?text=Blue+Sky",
            "prompt": "Transform this into a magical fantasy landscape with floating islands",
            "genre": "fantasy",
            "art_style": "storybook"
        },
        {
            "url": "https://via.placeholder.com/800x600/FF6B6B/FFFFFF?text=Sunset",
            "prompt": "Transform this into a romantic sunset scene with warm lighting",
            "genre": "romance",
            "art_style": "watercolor"
        }
    ]
    
    for i, image_info in enumerate(internet_images, 1):
        print(f"\n🔄 Processing internet image {i}...")
        print(f"   URL: {image_info['url']}")
        print(f"   Prompt: {image_info['prompt']}")
        print(f"   Genre: {image_info['genre']}")
        print(f"   Art Style: {image_info['art_style']}")
        
        # Transform directly from URL
        request = ImageToImageRequest(
            source_image=image_info['url'],
            prompt=image_info['prompt'],
            genre=image_info['genre'],
            art_style=image_info['art_style'],
            strength=0.35,
            cfg_scale=7.0,
            steps=20,
            is_url=True
        )
        
        result = await process_image_to_image(request)
        
        if result.success:
            print(f"✅ Internet image {i} transformation successful!")
            save_base64_image(result.image_base64, f"internet_transformed_{i}.png")
        else:
            print(f"❌ Internet image {i} transformation failed: {result.error_message}")

async def example_url_variations():
    """Example of generating variations from URL images"""
    print("\n🔄 Example 3: URL Image Variations")
    print("-" * 50)
    
    # Use a simple placeholder image
    url = "https://via.placeholder.com/512x512/9B59B6/FFFFFF?text=Purple+Magic"
    
    print(f"🔄 Generating variations from URL: {url}")
    
    request = ImageToImageVariationRequest(
        source_image=url,
        genre="fantasy",
        art_style="watercolor",
        num_variations=3,
        strength=0.3,
        cfg_scale=7.0,
        steps=20,
        is_url=True
    )
    
    result = await generate_image_variations(request)
    
    if result.success:
        print(f"✅ Generated {len(result.variations)} variations!")
        for i, variation in enumerate(result.variations, 1):
            save_base64_image(variation, f"url_variation_{i}.png")
    else:
        print(f"❌ URL variations failed: {result.error_message}")

async def example_error_handling():
    """Example of error handling with invalid URLs"""
    print("\n⚠️ Example 4: Error Handling")
    print("-" * 50)
    
    # Test invalid URLs
    invalid_urls = [
        "https://invalid-url-that-does-not-exist.com/image.png",
        "https://httpbin.org/status/404",  # 404 error
        "not-a-url-at-all",
        "https://example.com/nonexistent-image.jpg"
    ]
    
    for i, url in enumerate(invalid_urls, 1):
        print(f"\n🔄 Testing invalid URL {i}: {url}")
        
        request = ImageToImageRequest(
            source_image=url,
            prompt="Transform this image",
            genre="action",
            art_style="comic book",
            strength=0.35,
            is_url=True
        )
        
        result = await process_image_to_image(request)
        
        if result.success:
            print(f"✅ Unexpected success for invalid URL {i}")
        else:
            print(f"❌ Correctly failed for invalid URL {i}: {result.error_message}")

async def main():
    """Run all URL examples"""
    print("🚀 Image-to-Image with URL Loading Examples")
    print("=" * 60)
    
    # Check available options
    print("📋 Available Genres:", get_available_genres())
    print("📋 Available Art Styles:", get_available_art_styles())
    print()
    
    # Run examples
    await example_url_loading()
    await example_internet_images()
    await example_url_variations()
    await example_error_handling()
    
    print("\n" + "=" * 60)
    print("✅ All URL examples completed!")
    print("📁 Check the generated PNG files to see the results.")
    print("\n💡 Tips:")
    print("   - You can use any public image URL")
    print("   - Supported formats: PNG, JPG, JPEG, GIF, etc.")
    print("   - Images are automatically converted to PNG format")
    print("   - Invalid URLs will return appropriate error messages")

if __name__ == "__main__":
    # Check if STABILITY_API_KEY is set
    if not os.getenv("STABILITY_API_KEY"):
        print("❌ STABILITY_API_KEY environment variable not set!")
        print("Please set your Stability AI API key before running this example.")
        sys.exit(1)
    
    # Run the examples
    asyncio.run(main()) 