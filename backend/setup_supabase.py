#!/usr/bin/env python3
"""
Supabase Setup Script for MindToon
This script helps you configure and test your Supabase connection.
"""

import os
import sys
import subprocess
from pathlib import Path

def create_env_file():
    """Create a .env file with Supabase configuration"""
    env_content = """# Supabase Configuration
# Replace with your actual Supabase project values
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Database Configuration (Use Supabase PostgreSQL)
# Replace with your actual Supabase database URL
DATABASE_URL=postgresql://postgres:your_password@db.your-project-ref.supabase.co:5432/postgres

# API Configuration
API_KEY=your_openai_api_key_here
MY_PROJECT=MindToon
BASE_URL=http://localhost:8000

# Development
DEBUG=True
"""
    
    env_path = Path(".env")
    if env_path.exists():
        print("❌ .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return False
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file")
    print("📝 Please edit .env with your actual Supabase credentials")
    return True

def check_supabase_connection():
    """Test the Supabase connection"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        try:
            # Try Docker/container imports first (when running from /app)
            from api.supabase.client import supabase_client
        except ImportError:
            # Fallback to src imports for local development
            # Add src to path for local development
            if 'src' not in sys.path:
                sys.path.append('src')
            from src.api.supabase.client import supabase_client
        
        # Test basic connection
        print("🔍 Testing Supabase connection...")
        
        # Check environment variables
        required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'DATABASE_URL']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var) or os.getenv(var).startswith('your_'):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing or incomplete environment variables: {', '.join(missing_vars)}")
            print("Please update your .env file with actual Supabase credentials")
            return False
        
        print("✅ Environment variables configured")
        
        # Test Supabase client initialization
        if supabase_client.client:
            print("✅ Supabase client initialized successfully")
        else:
            print("❌ Failed to initialize Supabase client")
            return False
        
        print("🎉 Supabase connection test passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you've installed all requirements: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def setup_database():
    """Initialize the database tables"""
    try:
        print("🔧 Setting up database tables...")
        
        # Run the database reset script
        result = subprocess.run([
            sys.executable, "src/main.py", "--reset-db"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database tables created successfully")
            return True
        else:
            print(f"❌ Database setup failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*50)
    print("🎯 NEXT STEPS")
    print("="*50)
    print("1. Create a Supabase project at https://supabase.com")
    print("2. Get your credentials from Settings → API")
    print("3. Update the .env file with your actual credentials")
    print("4. Create a 'comics' storage bucket in Supabase")
    print("5. Run this script again to test the connection")
    print("\n📖 For detailed instructions, see: supabase_setup_guide.md")

def main():
    """Main setup function"""
    print("🚀 MindToon Supabase Setup")
    print("="*30)
    
    # Check if we're in the backend directory
    if not Path("src").exists():
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Menu options
    print("\nWhat would you like to do?")
    print("1. Create .env file template")
    print("2. Test Supabase connection")
    print("3. Setup database tables")
    print("4. Full setup (1-3)")
    print("5. Show next steps")
    
    try:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            create_env_file()
        elif choice == "2":
            check_supabase_connection()
        elif choice == "3":
            setup_database()
        elif choice == "4":
            print("🔄 Running full setup...")
            if create_env_file():
                print("\n⏳ Please update .env with your Supabase credentials, then run option 2 to test")
            print_next_steps()
        elif choice == "5":
            print_next_steps()
        else:
            print("❌ Invalid choice. Please select 1-5.")
    
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"❌ Setup error: {e}")

if __name__ == "__main__":
    main() 