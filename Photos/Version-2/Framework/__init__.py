"""
HSTL Photo Framework

A comprehensive Python framework for managing the complete HSTL Photo Metadata Project workflow.
Orchestrates 8 steps of photo metadata processing from Google Spreadsheet preparation 
through final watermarked JPEG creation.
"""

__version__ = "0.1.2"
__author__ = "HSTL Photo Metadata Project"
__description__ = "Framework for orchestrating HSTL photo metadata processing workflow"

# Core imports moved to avoid circular dependencies
# Import these modules directly when needed

# Framework constants
FRAMEWORK_VERSION = __version__
SUPPORTED_STEPS = list(range(1, 9))  # Steps 1-8