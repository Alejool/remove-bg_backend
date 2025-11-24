"""
Processors package for image processing operations
"""

from .background_remover import remove_background, has_transparency
from .optimizer import optimize_image, save_optimized, get_file_size_reduction
from .resizer import resize_image, resize_to_width, create_thumbnail, get_dimensions

__all__ = [
    'remove_background',
    'has_transparency',
    'optimize_image',
    'save_optimized',
    'get_file_size_reduction',
    'resize_image',
    'resize_to_width',
    'create_thumbnail',
    'get_dimensions',
]