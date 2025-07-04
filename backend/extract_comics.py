#!/usr/bin/env python3
"""
Extract saved comics from database and save as PNG files
"""
import os
import sys
import base64
from pathlib import Path

# Add the src directory to Python path
sys.path.append('/app')
sys.path.append('/app/src')
sys.path.append('src')  # For local development

try:
    # Try Docker/container imports first (when running from /app)
    from api.db import get_session
    from api.chat.models import ComicsPage
except ImportError:
    # Fallback to src imports for local development
    from src.api.db import get_session
    from src.api.chat.models import ComicsPage
from sqlmodel import select

def extract_comics():
    """Extract comics from database and save as PNG files"""
    
    # Create output directory
    output_dir = Path("/app/extracted_comics")
    output_dir.mkdir(exist_ok=True)
    
    # Get database session
    session = next(get_session())
    
    # Query recent comics
    comics = session.exec(
        select(ComicsPage)
        .order_by(ComicsPage.created_at.desc())
        .limit(10)
    ).all()
    
    print(f"📚 Found {len(comics)} comics to extract...")
    
    extracted_count = 0
    for comic in comics:
        if comic.image_base64:
            try:
                # Decode base64 image
                image_data = base64.b64decode(comic.image_base64)
                
                # Create safe filename
                safe_title = "".join(c for c in comic.title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:50]
                filename = f"comic_{comic.id}_{safe_title}.png"
                filepath = output_dir / filename
                
                # Save image file
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                print(f"✅ Extracted: {filename}")
                print(f"   Title: {comic.title}")
                print(f"   Concept: {comic.concept[:100]}...")
                print(f"   Created: {comic.created_at}")
                print(f"   User ID: {comic.user_id}")
                print()
                
                extracted_count += 1
                
            except Exception as e:
                print(f"❌ Error extracting comic {comic.id}: {e}")
        else:
            print(f"⚠️ Comic {comic.id} has no image data")
    
    session.close()
    
    print(f"🎨 Successfully extracted {extracted_count} comics!")
    print(f"📁 Files saved to: {output_dir}")
    print("🔍 To view them, copy the files from the container to your local machine:")
    print(f"   docker cp mindtoon-1-backend-1:/app/extracted_comics ./saved_comics")

if __name__ == "__main__":
    extract_comics() 