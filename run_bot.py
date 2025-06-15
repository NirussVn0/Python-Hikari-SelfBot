#!/usr/bin/env python3

import sys
import asyncio
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from discord_selfbot.main import run

if __name__ == "__main__":
    print("🐍 Starting Discord Self-Bot Python Implementation...")
    print("⚠️  WARNING: Self-bots violate Discord's Terms of Service")
    print("⚠️  This is for educational purposes only!")
    print("=" * 60)
    
    try:
        run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
