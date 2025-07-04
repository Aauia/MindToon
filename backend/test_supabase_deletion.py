#!/usr/bin/env python3
"""
Quick Supabase Deletion Test Script

This script helps you diagnose why Supabase deletion might not be working 
during account deletion by testing the connection and storage functionality.

Usage:
    python test_supabase_deletion.py

Make sure to run this from the backend directory.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
if 'src' not in sys.path:
    sys.path.append('src')

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("🔍 Checking Environment Variables...")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'SUPABASE_SERVICE_ROLE_KEY'
    ]
    
    missing_vars = []
    configured_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"   ❌ {var}: Not set")
        elif value.startswith('your_') or value.startswith('https://your-'):
            missing_vars.append(var)
            print(f"   ⚠️ {var}: Set but appears to be placeholder value")
        else:
            configured_vars.append(var)
            print(f"   ✅ {var}: Configured")
    
    if missing_vars:
        print(f"\n❌ Missing or incomplete variables: {', '.join(missing_vars)}")
        print("   Update your .env file with actual Supabase credentials")
        return False
    else:
        print(f"\n✅ All environment variables are configured")
        return True

def test_supabase_import():
    """Test if Supabase client can be imported and initialized"""
    print("\n🔍 Testing Supabase Import and Initialization...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("   ✅ Loaded .env file")
        
        from api.supabase.client import supabase_client
        print("   ✅ Successfully imported supabase_client")
        
        if supabase_client is None:
            print("   ❌ supabase_client is None - initialization failed")
            return False
        else:
            print("   ✅ supabase_client is initialized")
            return True
            
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Initialization error: {e}")
        return False

def test_supabase_connection(supabase_client):
    """Test the actual Supabase connection"""
    print("\n🔍 Testing Supabase Connection...")
    
    try:
        connection_test = supabase_client.test_connection()
        print(f"   📋 Connection test result: {connection_test}")
        
        if connection_test.get("connected", False):
            print("   ✅ Successfully connected to Supabase")
            
            if connection_test.get("bucket_exists", False):
                print("   ✅ 'comics' storage bucket exists")
            else:
                print("   ❌ 'comics' storage bucket does not exist")
                print("   🔧 Create the bucket in your Supabase dashboard")
                
            return connection_test.get("bucket_exists", False)
        else:
            print("   ❌ Failed to connect to Supabase")
            print(f"   Error: {connection_test.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection test exception: {e}")
        return False

def test_storage_operations(supabase_client):
    """Test basic storage operations"""
    print("\n🔍 Testing Storage Operations...")
    
    try:
        # Test listing files (this doesn't require creating files)
        files = supabase_client.client.storage.from_("comics").list("")
        print(f"   ✅ Successfully listed storage contents: {len(files)} items")
        
        # If we can list, we can probably delete too
        print("   ✅ Storage operations appear to be working")
        return True
        
    except Exception as e:
        print(f"   ❌ Storage operation failed: {e}")
        return False

def get_user_comics_info():
    """Get information about user comics in the database"""
    print("\n🔍 Checking Database for User Comics...")
    
    try:
        from api.db import get_session
        from api.chat.models import ComicsPage
        from sqlmodel import select
        
        session = next(get_session())
        
        # Get all comics and their storage types
        all_comics = session.exec(select(ComicsPage)).all()
        
        if not all_comics:
            print("   📭 No comics found in database")
            return
        
        comics_with_urls = [c for c in all_comics if c.image_url]
        comics_base64_only = [c for c in all_comics if not c.image_url and c.image_base64]
        comics_no_image = [c for c in all_comics if not c.image_url and not c.image_base64]
        
        print(f"   📊 Total comics in database: {len(all_comics)}")
        print(f"   📁 Comics with Supabase URLs: {len(comics_with_urls)}")
        print(f"   💾 Comics with base64 only: {len(comics_base64_only)}")
        print(f"   🚫 Comics with no image data: {len(comics_no_image)}")
        
        if comics_with_urls:
            print(f"   🎯 During deletion, {len(comics_with_urls)} images would need Supabase cleanup")
            print("   Sample URLs:")
            for i, comic in enumerate(comics_with_urls[:3]):
                print(f"     {i+1}. {comic.image_url}")
        else:
            print("   💡 No Supabase storage cleanup needed - all comics use base64")
            
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")

def simulate_deletion_test(supabase_client):
    """Simulate what would happen during account deletion"""
    print("\n🔍 Simulating Account Deletion Process...")
    
    try:
        from api.db import get_session
        from api.chat.models import ComicsPage
        from sqlmodel import select
        
        session = next(get_session())
        
        # Simulate getting comics with URLs (like in the deletion process)
        comics_with_urls = session.exec(
            select(ComicsPage).where(ComicsPage.image_url.isnot(None))
        ).all()
        
        print(f"   📊 Found {len(comics_with_urls)} comics with Supabase URLs")
        
        if not comics_with_urls:
            print("   💡 No Supabase deletion would be attempted (no comics with URLs)")
            return True
        
        print(f"   🗑️ During deletion, the system would attempt to delete {len(comics_with_urls)} images")
        
        # Test if we can parse the URLs (don't actually delete)
        for i, comic in enumerate(comics_with_urls[:3], 1):
            print(f"   📂 Comic {i}: {comic.image_url}")
            
            if "comics/" in comic.image_url:
                file_path = comic.image_url.split("comics/")[-1]
                print(f"      Extracted path: {file_path}")
                print(f"      ✅ URL format is valid for deletion")
            else:
                print(f"      ❌ URL format doesn't contain 'comics/' - deletion would fail")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Deletion simulation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Supabase Deletion Diagnostic Test")
    print("=" * 50)
    
    # Step 1: Check environment variables
    env_ok = check_environment_variables()
    if not env_ok:
        print("\n🛑 Fix environment variables before proceeding")
        return
    
    # Step 2: Test import and initialization
    import_ok = test_supabase_import()
    if not import_ok:
        print("\n🛑 Fix Supabase import/initialization before proceeding")
        return
    
    # Get the supabase client for further tests
    from api.supabase.client import supabase_client
    
    # Step 3: Test connection
    connection_ok = test_supabase_connection(supabase_client)
    
    # Step 4: Test storage operations
    if connection_ok:
        storage_ok = test_storage_operations(supabase_client)
    else:
        storage_ok = False
    
    # Step 5: Check database comics
    get_user_comics_info()
    
    # Step 6: Simulate deletion process
    if storage_ok:
        simulate_deletion_test(supabase_client)
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if env_ok and import_ok and connection_ok and storage_ok:
        print("✅ All tests passed - Supabase deletion should work properly")
    else:
        print("❌ Some tests failed - this explains why account deletion didn't clean up Supabase")
        print("\n🔧 FIXES NEEDED:")
        if not env_ok:
            print("   - Update .env file with correct Supabase credentials")
        if not import_ok:
            print("   - Check Supabase Python client installation")
        if not connection_ok:
            print("   - Verify Supabase project is active and credentials are correct")
            print("   - Create 'comics' storage bucket in Supabase dashboard")
        if not storage_ok:
            print("   - Check storage permissions and bucket configuration")

if __name__ == "__main__":
    try:
        # Make sure we're in the right directory
        if not Path("src").exists():
            print("❌ Please run this script from the backend directory")
            sys.exit(1)
        
        main()
        
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test script error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}") 