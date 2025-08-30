#!/usr/bin/env python3
"""
Startup script for BizLinkMZ API
This script handles initialization and error handling
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def main():
    """Main startup function"""
    try:
        print("🚀 Starting BizLinkMZ API...")
        
        # Check environment
        print("📋 Environment check...")
        required_vars = ["DATABASE_URL"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Missing environment variables: {missing_vars}")
            print("💡 Please check your Railway configuration")
        else:
            print("✅ Environment variables OK")
        
        # Import and start app
        print("📦 Importing application...")
        from app.main import app
        
        print("✅ Application imported successfully")
        print("🎯 Ready to start server")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Check if all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
