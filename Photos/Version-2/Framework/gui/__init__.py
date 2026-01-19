"""GUI Package for HSTL Photo Framework"""

import sys
from pathlib import Path

# Ensure framework root is in path for imports
_framework_dir = Path(__file__).parent.parent
if str(_framework_dir) not in sys.path:
    sys.path.insert(0, str(_framework_dir))

# Import version from central source
from __init__ import __version__, __commit_date__

from .main_window import MainWindow
from .hstl_gui import main

__all__ = ["MainWindow", "main", "__version__", "__commit_date__"]
