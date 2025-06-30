import os
from supabase import create_client, Client
from typing import Optional
import io
import uuid
from PIL import Image

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.client: Client = create_client(self.url, self.key)
        self.bucket_name = "comics"
    
    def upload_comic_image(self, user_id: int, image: Image.Image) -> str:
        """Upload a comic image to Supabase Storage and return the public URL"""
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_path = f"users/{user_id}/comics/{file_id}.png"
            
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Upload to Supabase Storage
            response = self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=img_byte_arr.getvalue(),
                file_options={"content-type": "image/png"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to upload image: {response}")
            
            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
            return public_url
            
        except Exception as e:
            print(f"Error uploading comic image: {e}")
            raise
    
    def delete_comic_image(self, image_url: str) -> bool:
        """Delete a comic image from Supabase Storage"""
        try:
            # Extract file path from URL
            file_path = image_url.split(f"{self.bucket_name}/")[-1]
            
            response = self.client.storage.from_(self.bucket_name).remove([file_path])
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error deleting comic image: {e}")
            return False

# Global instance
supabase_client = SupabaseClient() 