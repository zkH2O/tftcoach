"""
Vision Module - Screen capture, OCR, and coordinate management for TFT
"""

# Vector classes for coordinates
from .vec2 import Vec2
from .vec4 import Vec4, GameWindow

# Screen coordinates
from . import screen_coords

# OCR engine
from . import ocr_engine

# Game state reading functions
from . import arena_functions

__all__ = [
    'Vec2',
    'Vec4',
    'GameWindow',
    'screen_coords',
    'ocr_engine',
    'arena_functions',
]
