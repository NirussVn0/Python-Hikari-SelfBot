#!/usr/bin/env python3
"""
Main entry point for utils module execution.

This allows running: python -m src.utils validators <token>
"""

import sys
import asyncio
from .validators import main as validator_main

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.utils <submodule> [args...]")
        print("Available submodules:")
        print("  validators <token> - Validate Discord token")
        sys.exit(1)
    
    submodule = sys.argv[1]
    
    if submodule == "validators":
        # Remove the submodule name from argv so validators.main() gets the right args
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        asyncio.run(validator_main())
    else:
        print(f"Unknown submodule: {submodule}")
        sys.exit(1)
