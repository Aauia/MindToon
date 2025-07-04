import os
from supabase import create_client, Client
from typing import Optional, Dict, List
import io
import uuid
from PIL import Image
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.url:
            raise ValueError("SUPABASE_URL must be set in environment variables")
        
        # Use service role key for backend operations to bypass RLS
        if self.service_key:
            logger.info("🔑 Using Supabase service role key for backend operations")
            self.client: Client = create_client(self.url, self.service_key)
        elif self.key:
            logger.warning("⚠️ Using anonymous key - this may cause RLS issues")
            self.client: Client = create_client(self.url, self.key)
        else:
            raise ValueError("Either SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY must be set")
        self.bucket_name = "comics"
        
        # Initialize storage bucket if needed
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the comics bucket exists"""
        try:
            print(f"🔍 DEBUG: Checking for bucket '{self.bucket_name}'...")
            print(f"🔍 DEBUG: Using Supabase URL: {self.url}")
            print(f"🔍 DEBUG: Using API key: {self.key[:20]}...{self.key[-10:] if self.key else 'None'}")
            
            # Try to get bucket info
            buckets = self.client.storage.list_buckets()
            print(f"🔍 DEBUG: Raw buckets response: {buckets}")
            
            if hasattr(buckets, '__iter__') and not isinstance(buckets, str):
                bucket_names = [bucket.name for bucket in buckets]
                print(f"🔍 DEBUG: Found bucket names: {bucket_names}")
                print(f"🔍 DEBUG: Looking for bucket: '{self.bucket_name}'")
                print(f"🔍 DEBUG: Bucket exists check: {self.bucket_name in bucket_names}")
                
                if self.bucket_name not in bucket_names:
                    logger.warning(f"❌ Bucket '{self.bucket_name}' not found in {bucket_names}")
                    logger.warning(f"Available buckets: {bucket_names}")
                else:
                    logger.info(f"✅ Storage bucket '{self.bucket_name}' is available")
                    print(f"✅ DEBUG: Bucket '{self.bucket_name}' confirmed present!")
            else:
                print(f"🔍 DEBUG: Unexpected buckets response format: {type(buckets)}")
                print(f"🔍 DEBUG: Response content: {buckets}")
                
        except Exception as e:
            logger.error(f"❌ Error checking storage bucket: {e}")
            print(f"🔍 DEBUG: Exception details: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"🔍 DEBUG: Full traceback:\n{traceback.format_exc()}")
    
    def upload_comic_image(self, user_id: int, image: Image.Image) -> str:
        """Upload a comic image to Supabase Storage and return the public URL"""
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_path = f"users/{user_id}/comics/{file_id}.png"
            
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG', optimize=True, quality=85)
            img_byte_arr.seek(0)
            
            # Upload to Supabase Storage
            response = self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=img_byte_arr.getvalue(),
                file_options={
                    "content-type": "image/png",
                    "cache-control": "3600"
                }
            )
            
            if hasattr(response, 'status_code') and response.status_code != 200:
                raise Exception(f"Failed to upload image: {response}")
            
            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
            
            logger.info(f"✅ Successfully uploaded comic image for user {user_id}: {file_path}")
            return public_url
            
        except Exception as e:
            logger.error(f"Error uploading comic image for user {user_id}: {e}")
            raise
    
    def delete_comic_image(self, image_url: str) -> bool:
        """Delete a comic image from Supabase Storage"""
        try:
            logger.info(f"🗑️ Attempting to delete image: {image_url}")
            
            # Extract file path from URL
            if self.bucket_name not in image_url:
                logger.error(f"❌ Invalid image URL format (bucket '{self.bucket_name}' not found): {image_url}")
                return False
            
            # Parse the file path from the URL
            try:
                file_path = image_url.split(f"{self.bucket_name}/")[-1]
                # Remove query parameters (like ?t=timestamp) from the file path
                file_path = file_path.split('?')[0]
                logger.info(f"   📂 Extracted file path: {file_path}")
            except Exception as path_error:
                logger.error(f"❌ Failed to extract file path from URL {image_url}: {path_error}")
                return False
            
            # Attempt to delete from storage
            logger.info(f"   🗑️ Sending delete request to Supabase Storage...")
            response = self.client.storage.from_(self.bucket_name).remove([file_path])
            
            logger.info(f"   📋 Supabase response: {response}")
            
            # Check response - Supabase storage delete can return different response formats
            if hasattr(response, 'status_code'):
                success = response.status_code == 200
                logger.info(f"   📊 Response status code: {response.status_code}")
            elif isinstance(response, list):
                # Supabase returns an empty list [] for successful deletions
                success = True
                logger.info(f"   📊 Response list (successful deletion): {len(response)} items")
            elif response is None:
                # Sometimes deletion succeeds but returns None
                success = True
                logger.info(f"   📊 Response is None (may indicate success)")
            else:
                success = False
                logger.warning(f"   📊 Unexpected response format: {type(response)}")
            
            if success:
                logger.info(f"✅ Successfully deleted comic image: {file_path}")
            else:
                logger.error(f"❌ Failed to delete comic image: {file_path}")
                logger.error(f"   Response details: {response}")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Exception during comic image deletion for {image_url}: {e}")
            
            # Try to get more details about the error
            try:
                import traceback
                logger.error(f"   Full traceback: {traceback.format_exc()}")
            except:
                pass
            
            return False
    
    def get_user_comics_storage_usage(self, user_id: int) -> Dict:
        """Get storage usage statistics for a user"""
        try:
            # List all files for the user
            files = self.client.storage.from_(self.bucket_name).list(f"users/{user_id}/comics/")
            
            total_files = len(files)
            total_size = sum(file.get('metadata', {}).get('size', 0) for file in files)
            
            return {
                "user_id": user_id,
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting storage usage for user {user_id}: {e}")
            return {"user_id": user_id, "total_files": 0, "total_size_bytes": 0, "total_size_mb": 0}
    
    def list_user_comics(self, user_id: int) -> List[Dict]:
        """List all comic images for a user"""
        try:
            files = self.client.storage.from_(self.bucket_name).list(f"users/{user_id}/comics/")
            
            comics = []
            for file in files:
                if file.get('name', '').endswith('.png'):
                    file_path = f"users/{user_id}/comics/{file['name']}"
                    public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
                    
                    comics.append({
                        "filename": file['name'],
                        "path": file_path,
                        "url": public_url,
                        "size": file.get('metadata', {}).get('size', 0),
                        "created_at": file.get('created_at'),
                        "updated_at": file.get('updated_at')
                    })
            
            return comics
            
        except Exception as e:
            logger.error(f"Error listing comics for user {user_id}: {e}")
            return []
    
    def save_comic_to_database(self, comic_data: Dict) -> Dict:
        """Save comic metadata to Supabase database"""
        try:
            result = self.client.table('comics').insert(comic_data).execute()
            
            if result.data:
                logger.info(f"✅ Comic saved to Supabase database with ID: {result.data[0].get('id')}")
                return {"success": True, "data": result.data[0]}
            else:
                logger.error(f"❌ Failed to save comic to database: {result}")
                return {"success": False, "error": "No data returned"}
                
        except Exception as e:
            logger.error(f"❌ Error saving comic to database: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user_comics_from_database(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get user's comics from Supabase database"""
        try:
            result = self.client.table('comics').select('*').eq('user_id', user_id).order('created_at', desc=True).range(offset, offset + limit - 1).execute()
            
            if result.data:
                logger.info(f"✅ Retrieved {len(result.data)} comics for user {user_id}")
                return result.data
            else:
                logger.info(f"📭 No comics found for user {user_id}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting user comics: {e}")
            return []
    
    def save_scenario_to_database(self, scenario_data: Dict) -> Dict:
        """Save detailed scenario metadata to Supabase database"""
        try:
            result = self.client.table('detailedscenario').insert(scenario_data).execute()
            
            if result.data:
                logger.info(f"✅ Scenario saved to Supabase database with ID: {result.data[0].get('id')}")
                return {"success": True, "data": result.data[0]}
            else:
                logger.error(f"❌ Failed to save scenario to database: {result}")
                return {"success": False, "error": "No data returned"}
                
        except Exception as e:
            logger.error(f"❌ Error saving scenario to database: {e}")
            return {"success": False, "error": str(e)}
    
    def get_scenario_by_comic_id(self, comic_id: int) -> Optional[Dict]:
        """Get detailed scenario for a specific comic"""
        try:
            result = self.client.table('detailedscenario').select('*').eq('comic_id', comic_id).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"✅ Retrieved scenario for comic {comic_id}")
                return result.data[0]
            else:
                logger.info(f"📭 No scenario found for comic {comic_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error retrieving scenario for comic {comic_id}: {e}")
            return None
    
    def get_user_scenarios_from_database(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get user's scenarios from Supabase database"""
        try:
            result = self.client.table('detailedscenario').select('*').eq('user_id', user_id).order('created_at', desc=True).range(offset, offset + limit - 1).execute()
            
            if result.data:
                logger.info(f"✅ Retrieved {len(result.data)} scenarios for user {user_id}")
                return result.data
            else:
                logger.info(f"📭 No scenarios found for user {user_id}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error retrieving scenarios for user {user_id}: {e}")
            return []
    
    def update_scenario_in_database(self, scenario_id: int, updates: Dict) -> Dict:
        """Update scenario in Supabase database"""
        try:
            result = self.client.table('detailedscenario').update(updates).eq('id', scenario_id).execute()
            
            if result.data:
                logger.info(f"✅ Scenario {scenario_id} updated successfully")
                return {"success": True, "data": result.data[0]}
            else:
                logger.error(f"❌ Failed to update scenario {scenario_id}")
                return {"success": False, "error": "No data returned"}
                
        except Exception as e:
            logger.error(f"❌ Error updating scenario {scenario_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_scenario_from_database(self, scenario_id: int) -> Dict:
        """Delete scenario from Supabase database"""
        try:
            result = self.client.table('detailedscenario').delete().eq('id', scenario_id).execute()
            
            if result.data:
                logger.info(f"✅ Scenario {scenario_id} deleted successfully")
                return {"success": True}
            else:
                logger.error(f"❌ Failed to delete scenario {scenario_id}")
                return {"success": False, "error": "No data returned"}
                
        except Exception as e:
            logger.error(f"❌ Error deleting scenario {scenario_id}: {e}")
            return {"success": False, "error": str(e)}

    def test_connection(self) -> Dict:
        """Test the Supabase connection and return status"""
        try:
            # Test basic connection
            buckets = self.client.storage.list_buckets()
            
            # Check if comics bucket exists
            bucket_exists = any(bucket.name == self.bucket_name for bucket in buckets)
            
            # Test database access
            try:
                test_query = self.client.table('comics').select('count').execute()
                db_connected = True
            except Exception as db_error:
                logger.warning(f"Database test failed: {db_error}")
                db_connected = False
            
            return {
                "connected": True,
                "bucket_exists": bucket_exists,
                "database_connected": db_connected,
                "total_buckets": len(buckets),
                "using_service_key": bool(self.service_key),
                "message": "✅ Supabase connection successful"
            }
            
        except Exception as e:
            return {
                "connected": False,
                "bucket_exists": False,
                "database_connected": False,
                "total_buckets": 0,
                "using_service_key": bool(self.service_key),
                "error": str(e),
                "message": f"❌ Supabase connection failed: {e}"
            }

# Global instance
try:
    supabase_client = SupabaseClient()
    logger.info("✅ Supabase client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Supabase client: {e}")
    # Create a dummy client to prevent import errors
    supabase_client = None 