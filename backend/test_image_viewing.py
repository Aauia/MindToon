#!/usr/bin/env python3
"""
Test script to demonstrate image viewing functionality
"""

import asyncio
import os
import sys
import requests

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.ai.image2image import (
    ImageToImageRequest,
    process_image_to_image
)

async def test_image_viewing():
    """Test image-to-image with viewing functionality"""
    print("🖼️ Testing Image Viewing Functionality")
    print("=" * 50)
    
    # Test with URL image
    request = ImageToImageRequest(
        source_image="https://upload.wikimedia.org/wikipedia/commons/0/05/People.png",
        prompt="Turn it into cyber bank",
        genre="action",
        art_style="comic book",
        strength=0.35,
        cfg_scale=7,
        steps=20,
        seed=0,
        width=0,
        height=0,
        is_url=True,
        save_image=True  # This will save the image
    )
    
    print(f"🔄 Processing request...")
    print(f"   URL: {request.source_image}")
    print(f"   Prompt: {request.prompt}")
    print(f"   Save image: {request.save_image}")
    
    try:
        result = await process_image_to_image(request)
        
        if result.success:
            print("✅ Success!")
            print(f"   📏 Output dimensions: {result.width}x{result.height}")
            print(f"   🌱 Seed used: {result.seed}")
            
            if result.image_url:
                print(f"   🌐 View image at: http://localhost:8000{result.image_url}")
                print(f"   📁 Saved to: {result.image_path}")
                
                # Test if we can access the image
                try:
                    response = requests.get(f"http://localhost:8000{result.image_url}")
                    if response.status_code == 200:
                        print("   ✅ Image is accessible via URL!")
                    else:
                        print(f"   ⚠️ Image URL returned status: {response.status_code}")
                except Exception as e:
                    print(f"   ⚠️ Could not test image URL: {str(e)}")
            else:
                print("   ⚠️ No image URL generated")
                
        else:
            print(f"❌ Failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

async def test_variations_with_viewing():
    """Test variations with image viewing"""
    print("\n🔄 Testing Variations with Image Viewing")
    print("-" * 50)
    
    from api.ai.image2image import ImageToImageVariationRequest, generate_image_variations
    
    request = ImageToImageVariationRequest(
        source_image="https://via.placeholder.com/512x512/FF0000/FFFFFF?text=Test",
        genre="fantasy",
        art_style="watercolor",
        num_variations=2,
        strength=0.3,
        cfg_scale=7.0,
        steps=20,
        is_url=True,
        save_images=True
    )
    
    print(f"🔄 Generating {request.num_variations} variations...")
    
    try:
        result = await generate_image_variations(request)
        
        if result.success:
            print(f"✅ Generated {len(result.variations)} variations!")
            
            for i, (image_url, image_path) in enumerate(zip(result.image_urls, result.image_paths)):
                if image_url:
                    print(f"   Variation {i+1}:")
                    print(f"     🌐 URL: http://localhost:8000{image_url}")
                    print(f"     📁 Path: {image_path}")
                else:
                    print(f"   Variation {i+1}: No image saved")
        else:
            print(f"❌ Variations failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

async def test_list_images():
    """Test listing all saved images"""
    print("\n📋 Testing Image Listing")
    print("-" * 50)
    
    try:
        response = requests.get("http://localhost:8000/api/ai/images")
        if response.status_code == 200:
            data = response.json()
            images = data.get("images", [])
            
            if images:
                print(f"📁 Found {len(images)} saved images:")
                for img in images:
                    print(f"   📄 {img['filename']}")
                    print(f"      🌐 URL: http://localhost:8000{img['url']}")
                    print(f"      📏 Size: {img['size_bytes']} bytes")
            else:
                print("📁 No saved images found")
        else:
            print(f"❌ Failed to list images: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

async def main():
    """Run all image viewing tests"""
    print("🚀 Image Viewing Functionality Test")
    print("=" * 60)
    
    # Run tests
    await test_image_viewing()
    await test_variations_with_viewing()
    await test_list_images()
    
    print("\n" + "=" * 60)
    print("✅ Image viewing tests completed!")
    print("\n💡 How to view images:")
    print("   1. Generated images are automatically saved")
    print("   2. Access via: http://localhost:8000/api/ai/images/{filename}")
    print("   3. List all images: http://localhost:8000/api/ai/images")
    print("   4. Images are saved in the 'generated_images' directory")

if __name__ == "__main__":
    # Check if STABILITY_API_KEY is set
    if not os.getenv("STABILITY_API_KEY"):
        print("❌ STABILITY_API_KEY environment variable not set!")
        print("Please set your Stability AI API key before running this test.")
        sys.exit(1)
    
    # Run the tests
    asyncio.run(main()) 