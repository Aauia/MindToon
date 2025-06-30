#!/usr/bin/env python3
"""
Database reset script for MindToon
This script will drop all existing tables and recreate them with the current schema.
WARNING: This will delete all existing data!
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from api.db import engine, recreate_tables
from api.auth.models import User
from api.chat.models import ComicsPage
from api.auth.utils import get_password_hash
from sqlmodel import Session

def reset_database():
    """Reset the database and create initial data"""
    print("Starting database reset...")
    
    try:
        # Drop and recreate all tables
        recreate_tables()
        
        # Create initial admin user
        print("Creating initial admin user...")
        with Session(engine) as session:
            admin_user = User(
                username="admin",
                email="adminof@mindtoon.com",
                full_name="Admin User",
                hashed_password=get_password_hash("ad123")
            )
            session.add(admin_user)
            session.commit()
            print("Admin user created successfully")
        
        print("Database reset completed successfully!")
        print("Admin credentials: username='admin', password='ad123'")
        
    except Exception as e:
        print(f"Error during database reset: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Confirm with user
    response = input("This will DELETE ALL DATA in the database. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Database reset cancelled.")
        sys.exit(0)
    
    reset_database() 