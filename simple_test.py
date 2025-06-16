#!/usr/bin/env python3
"""Simple test to isolate import issues."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Testing individual imports...")

# Test 1: Core exceptions only
try:
    print("1. Testing core.exceptions...")
    import core.exceptions
    print("   ✅ Success")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Core types only  
try:
    print("2. Testing core.types...")
    import core.types
    print("   ✅ Success")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Core interfaces only
try:
    print("3. Testing core.interfaces...")
    import core.interfaces
    print("   ✅ Success")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()

print("Basic imports completed!")
