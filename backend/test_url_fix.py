#!/usr/bin/env python3
"""
Test script to verify the URL loading fix
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.ai.image2image import (
    ImageToImageRequest,
    process_image_to_image
)

async def test_url_image():
    """Test image-to-image with URL"""
    print("🧪 Testing URL Image-to-Image")
    print("=" * 40)
    
    # Test with the same URL that was failing
    request = ImageToImageRequest(
        source_image="https://upload.wikimedia.org/wikipedia/commons/0/05/People.png",
        prompt="Turn it into cyber bank",
        genre="action",
        art_style="comic book",
        strength=0.35,
        cfg_scale=7,
        steps=20,
        seed=0,
        width=0,  # This should now be handled correctly
        height=0,  # This should now be handled correctly
        is_url=True
    )
    
    print(f"🔄 Processing request...")
    print(f"   URL: {request.source_image}")
    print(f"   Prompt: {request.prompt}")
    print(f"   Genre: {request.genre}")
    print(f"   Art Style: {request.art_style}")
    print(f"   Width: {request.width}, Height: {request.height}")
    
    try:
        result = await process_image_to_image(request)
        
        if result.success:
            print("✅ Success!")
            print(f"   Output dimensions: {result.width}x{result.height}")
            print(f"   Seed used: {result.seed}")
            
            # Save the result
            if result.image_base64:
                import base64
                from PIL import Image
                from io import BytesIO
                
                image_data = base64.b64decode(result.image_base64)
                image = Image.open(BytesIO(image_data))
                image.save("test_url_result.png")
                print("   💾 Saved as: test_url_result.png")
        else:
            print(f"❌ Failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    # Check if STABILITY_API_KEY is set
    if not os.getenv("STABILITY_API_KEY"):
        print("❌ STABILITY_API_KEY environment variable not set!")
        print("Please set your Stability AI API key before running this test.")
        sys.exit(1)
    
    # Run the test
    asyncio.run(test_url_image()) 