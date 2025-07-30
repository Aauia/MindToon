#!/usr/bin/env python3
"""
Simple test to verify the migration script works
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from migrate_existing_comics_to_analytics import migrate_existing_comics_to_analytics

async def test_migration():
    """Test the migration script"""
    print("🧪 Testing migration script...")
    
    try:
        await migrate_existing_comics_to_analytics()
        print("✅ Migration test completed successfully!")
    except Exception as e:
        print(f"❌ Migration test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_migration()) 