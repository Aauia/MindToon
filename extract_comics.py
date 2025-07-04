import psycopg2
import base64
import os
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="mydb",
    user="dbuser",
    password="dbpassword"
)

# Create comics directory
os.makedirs("saved_comics", exist_ok=True)

# Query to get comics with their images
cursor = conn.cursor()
cursor.execute("""
    SELECT id, title, concept, image_base64, created_at, user_id 
    FROM comicspage 
    ORDER BY created_at DESC 
    LIMIT 10
""")

comics = cursor.fetchall()

print(f"📚 Found {len(comics)} comics to extract...")

for comic in comics:
    comic_id, title, concept, image_base64, created_at, user_id = comic
    
    if image_base64:
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            
            # Create safe filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:50]
            filename = f"saved_comics/comic_{comic_id}_{safe_title}.png"
            
            # Save image file
            with open(filename, 'wb') as f:
                f.write(image_data)
            
            print(f"✅ Extracted: {filename}")
            print(f"   Title: {title}")
            print(f"   Concept: {concept[:100]}...")
            print(f"   Created: {created_at}")
            print(f"   User ID: {user_id}")
            print()
            
        except Exception as e:
            print(f"❌ Error extracting comic {comic_id}: {e}")
    else:
        print(f"⚠️ Comic {comic_id} has no image data")

cursor.close()
conn.close()

print(f"🎨 Comics extracted to 'saved_comics' folder!")
print("You can now open these PNG files to view your comics visually.") 