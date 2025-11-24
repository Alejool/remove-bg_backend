"""
Image Resizer Processor
Handles smart image resizing with multiple modes and aspect ratio preservation
"""

from PIL import Image
from typing import Tuple, Literal


ResizeMode = Literal['contain', 'cover', 'fill']


def resize_image(
    image: Image.Image,
    width: int,
    height: int = None,
    mode: ResizeMode = 'contain'
) -> Image.Image:
    """
    Resize image with smart mode handling
    
    Args:
        image: PIL Image object
        width: Target width
        height: Target height (if None, maintains aspect ratio)
        mode: Resize mode ('contain', 'cover', 'fill')
        
    Returns:
        Resized PIL Image object
    """
    try:
        original_width, original_height = image.size
        
        # If no height specified, maintain aspect ratio
        if height is None:
            aspect_ratio = original_height / original_width
            height = int(width * aspect_ratio)
        
        if mode == 'contain':
            # Fit inside dimensions, maintain aspect ratio
            image.thumbnail((width, height), Image.Resampling.LANCZOS)
            return image
        
        elif mode == 'cover':
            # Cover dimensions, crop if needed
            aspect_ratio = width / height
            original_aspect = original_width / original_height
            
            if original_aspect > aspect_ratio:
                # Image is wider, scale by height
                new_height = height
                new_width = int(original_width * (height / original_height))
            else:
                # Image is taller, scale by width
                new_width = width
                new_height = int(original_height * (width / original_width))
            
            # Resize
            resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Crop to exact dimensions
            left = (new_width - width) // 2
            top = (new_height - height) // 2
            right = left + width
            bottom = top + height
            
            return resized.crop((left, top, right, bottom))
        
        elif mode == 'fill':
            # Stretch to exact dimensions (may distort)
            return image.resize((width, height), Image.Resampling.LANCZOS)
        
        else:
            raise ValueError(f"Invalid resize mode: {mode}")
    
    except Exception as e:
        raise Exception(f"Image resizing failed: {str(e)}")


def resize_to_width(image: Image.Image, width: int) -> Image.Image:
    """
    Resize image to specific width, maintaining aspect ratio
    
    Args:
        image: PIL Image object
        width: Target width
        
    Returns:
        Resized PIL Image object
    """
    original_width, original_height = image.size
    aspect_ratio = original_height / original_width
    height = int(width * aspect_ratio)
    
    return image.resize((width, height), Image.Resampling.LANCZOS)


def create_thumbnail(image: Image.Image, size: int = 200) -> Image.Image:
    """
    Create a square thumbnail
    
    Args:
        image: PIL Image object
        size: Thumbnail size (width and height)
        
    Returns:
        Thumbnail PIL Image object
    """
    return resize_image(image, size, size, mode='cover')


def get_dimensions(image: Image.Image) -> Tuple[int, int]:
    """
    Get image dimensions
    
    Args:
        image: PIL Image object
        
    Returns:
        Tuple of (width, height)
    """
    return image.size