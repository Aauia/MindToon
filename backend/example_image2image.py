#!/usr/bin/env python3
"""
Example script demonstrating image-to-image functionality
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
    process_image_to_image,
    generate_image_variations,
    get_available_genres,
    get_available_art_styles
)

def create_sample_image():
    """Create a sample image for testing"""
    # Create a simple image with shapes
    img = Image.new('RGB', (512, 512), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Draw some shapes
    draw.rectangle([50, 50, 200, 200], fill='red', outline='black', width=3)
    draw.ellipse([250, 250, 400, 400], fill='green', outline='black', width=3)
    draw.polygon([(300, 100), (350, 150), (250, 150)], fill='yellow', outline='black', width=3)
    
    # Add some text
    draw.text((50, 450), "Sample Image", fill='black')
    
    return img

def image_to_base64(image):
    """Convert PIL image to base64 string"""
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def save_base64_image(base64_string, filename):
    """Save base64 image to file"""
    image_data = base64.b64decode(base64_string)
    image = Image.open(BytesIO(image_data))
    image.save(filename)
    print(f"💾 Saved: {filename}")

async def example_basic_transformation():
    """Example of basic image-to-image transformation"""
    print("🎨 Example 1: Basic Image-to-Image Transformation")
    print("-" * 50)
    
    # Create sample image
    sample_image = create_sample_image()
    image_base64 = image_to_base64(sample_image)
    
    # Save original
    sample_image.save("original_sample.png")
    print("📸 Created sample image: original_sample.png")
    
    # Transform to action comic style
    request = ImageToImageRequest(
        source_image=image_base64,
        prompt="Transform this into a dynamic superhero comic panel with dramatic action poses",
        genre="action",
        art_style="comic book",
        strength=0.4,
        cfg_scale=7.0,
        steps=20
    )
    
    print("🔄 Generating action comic transformation...")
    result = await process_image_to_image(request)
    
    if result.success:
        print("✅ Transformation successful!")
        save_base64_image(result.image_base64, "action_comic_result.png")
    else:
        print(f"❌ Transformation failed: {result.error_message}")

async def example_genre_variations():
    """Example of generating variations with different genres"""
    print("\n🎭 Example 2: Genre Variations")
    print("-" * 50)
    
    # Create sample image
    sample_image = create_sample_image()
    image_base64 = image_to_base64(sample_image)
    
    # Test different genres
    genres_to_test = [
        ("romance", "watercolor", "Transform into a romantic scene with soft, dreamy lighting"),
        ("horror", "noir", "Transform into a dark, eerie horror scene"),
        ("sci-fi", "anime", "Transform into a futuristic sci-fi scene with neon lighting"),
        ("fantasy", "storybook", "Transform into a magical fantasy scene with enchanted elements")
    ]
    
    for i, (genre, art_style, prompt) in enumerate(genres_to_test, 1):
        print(f"\n🔄 Generating {genre} style ({art_style})...")
        
        request = ImageToImageRequest(
            source_image=image_base64,
            prompt=prompt,
            genre=genre,
            art_style=art_style,
            strength=0.35,
            cfg_scale=7.0,
            steps=20
        )
        
        result = await process_image_to_image(request)
        
        if result.success:
            print(f"✅ {genre.capitalize()} transformation successful!")
            save_base64_image(result.image_base64, f"{genre}_result.png")
        else:
            print(f"❌ {genre.capitalize()} transformation failed: {result.error_message}")

async def example_multiple_variations():
    """Example of generating multiple variations"""
    print("\n🔄 Example 3: Multiple Variations")
    print("-" * 50)
    
    # Create sample image
    sample_image = create_sample_image()
    image_base64 = image_to_base64(sample_image)
    
    # Generate multiple variations
    request = ImageToImageVariationRequest(
        source_image=image_base64,
        genre="adventure",
        art_style="cartoon",
        num_variations=3,
        strength=0.3,
        cfg_scale=7.0,
        steps=20
    )
    
    print("🔄 Generating 3 adventure cartoon variations...")
    result = await generate_image_variations(request)
    
    if result.success:
        print(f"✅ Generated {len(result.variations)} variations!")
        for i, variation in enumerate(result.variations, 1):
            save_base64_image(variation, f"variation_{i}.png")
    else:
        print(f"❌ Variations failed: {result.error_message}")

async def example_parameter_exploration():
    """Example of exploring different parameters"""
    print("\n⚙️ Example 4: Parameter Exploration")
    print("-" * 50)
    
    # Create sample image
    sample_image = create_sample_image()
    image_base64 = image_to_base64(sample_image)
    
    # Test different strength values
    strengths = [0.2, 0.4, 0.6]
    
    for strength in strengths:
        print(f"\n🔄 Testing strength: {strength}")
        
        request = ImageToImageRequest(
            source_image=image_base64,
            prompt="Transform this into a fantasy scene",
            genre="fantasy",
            art_style="watercolor",
            strength=strength,
            cfg_scale=7.0,
            steps=20
        )
        
        result = await process_image_to_image(request)
        
        if result.success:
            print(f"✅ Strength {strength} successful!")
            save_base64_image(result.image_base64, f"strength_{strength}.png")
        else:
            print(f"❌ Strength {strength} failed: {result.error_message}")

async def main():
    """Run all examples"""
    print("🚀 Image-to-Image Examples")
    print("=" * 60)
    
    # Check available options
    print("📋 Available Genres:", get_available_genres())
    print("📋 Available Art Styles:", get_available_art_styles())
    print()
    
    # Run examples
    await example_basic_transformation()
    await example_genre_variations()
    await example_multiple_variations()
    await example_parameter_exploration()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("📁 Check the generated PNG files to see the results.")

if __name__ == "__main__":
    # Check if STABILITY_API_KEY is set
    if not os.getenv("STABILITY_API_KEY"):
        print("❌ STABILITY_API_KEY environment variable not set!")
        print("Please set your Stability AI API key before running this example.")
        sys.exit(1)
    
    # Run the examples
    asyncio.run(main()) 