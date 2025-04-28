#!/usr/bin/env python3
"""
Standalone launcher for the Coyote Manager application.
This script provides an easy way to launch the manager without relying on package installation.
"""

import os
import sys
from pathlib import Path

# Add the 'src' directory to the Python path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

# Import main function. Since src is now on path, we can import directly
from src import main

if __name__ == "__main__":
    main.main()