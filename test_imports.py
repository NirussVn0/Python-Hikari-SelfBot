#!/usr/bin/env python3
"""Test script to check import issues."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Testing imports step by step...")

try:
    print("1. Importing core.exceptions...")
    from core.exceptions import ValidationError
    print("   ✅ core.exceptions imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import core.exceptions: {e}")
    sys.exit(1)

try:
    print("2. Importing core.interfaces...")
    from core.interfaces import ITokenValidator
    print("   ✅ core.interfaces imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import core.interfaces: {e}")
    sys.exit(1)

try:
    print("3. Importing core.types...")
    from core.types import TokenInfo
    print("   ✅ core.types imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import core.types: {e}")
    sys.exit(1)

try:
    print("4. Importing config.logging...")
    from config.logging import StructuredLogger
    print("   ✅ config.logging imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import config.logging: {e}")
    sys.exit(1)

try:
    print("5. Importing utils.validators...")
    from utils.validators import TokenValidator
    print("   ✅ utils.validators imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import utils.validators: {e}")
    sys.exit(1)

print("\n🎉 All imports successful!")

# Test token validation
if len(sys.argv) > 1:
    token = sys.argv[1]
    print(f"\nTesting token validation with: {token[:10]}...")
    
    import asyncio
    
    async def test_validation():
        validator = TokenValidator()
        result = await validator.validate_format(token)
        print(f"Format validation result: {result}")
        return result
    
    try:
        result = asyncio.run(test_validation())
        print(f"✅ Token validation completed: {result}")
    except Exception as e:
        print(f"❌ Token validation failed: {e}")
else:
    print("\nTo test token validation, run: python test_imports.py <token>")
