"""
Image Transformation Module
Resize, crop, rotate, flip operations using Pillow
"""

from PIL import Image, ImageOps
from typing import Literal, Optional, Tuple
import math

ResizeMode = Literal['fit', 'fill', 'stretch', 'cover']
RotateMode = Literal['90', '180', '270', 'custom']


def resize_image(
    image: Image.Image,
    width: Optional[int] = None,
    height: Optional[int] = None,
    mode: ResizeMode = 'fit',
    resample: Image.Resampling = Image.Resampling.LANCZOS
) -> Image.Image:
    """
    Resize image with various modes.
    
    Args:
        image: PIL Image
        width: Target width (None to auto-calculate)
        height: Target height (None to auto-calculate)
        mode: Resize mode
            - 'fit': Fit inside dimensions, maintain aspect ratio (default)
            - 'fill': Fill dimensions, crop if needed
            - 'stretch': Stretch to exact dimensions
            - 'cover': Cover dimensions, maintain aspect ratio
        resample: Resampling filter (LANCZOS is highest quality)
    
    Returns:
        Resized PIL Image
    """
    try:
        if width is None and height is None:
            return image.copy()
        
        orig_width, orig_height = image.size
        aspect_ratio = orig_width / orig_height
        
        # Calculate target dimensions
        if width is None:
            width = int(height * aspect_ratio)
        elif height is None:
            height = int(width / aspect_ratio)
        
        if mode == 'fit':
            # Fit inside dimensions, maintain aspect ratio
            image.thumbnail((width, height), resample)
            return image
            
        elif mode == 'fill':
            # Fill dimensions, crop excess
            return ImageOps.fit(image, (width, height), method=resample)
            
        elif mode == 'stretch':
            # Stretch to exact dimensions (may distort)
            return image.resize((width, height), resample)
            
        elif mode == 'cover':
            # Cover dimensions, maintain aspect ratio (may exceed)
            target_ratio = width / height
            
            if aspect_ratio > target_ratio:
                # Image is wider
                new_height = height
                new_width = int(height * aspect_ratio)
            else:
                # Image is taller
                new_width = width
                new_height = int(width / aspect_ratio)
            
            return image.resize((new_width, new_height), resample)
            
        else:
            raise ValueError(f"Unknown resize mode: {mode}")
            
    except Exception as e:
        raise Exception(f"Resize failed: {str(e)}")


def crop_image(
    image: Image.Image,
    x: int,
    y: int,
    width: int,
    height: int
) -> Image.Image:
    """
    Crop image to specified rectangle.
    
    Args:
        image: PIL Image
        x: Left coordinate
        y: Top coordinate
        width: Crop width
        height: Crop height
    
    Returns:
        Cropped PIL Image
    """
    try:
        img_width, img_height = image.size
        
        # Validate coordinates
        x = max(0, min(x, img_width))
        y = max(0, min(y, img_height))
        width = max(1, min(width, img_width - x))
        height = max(1, min(height, img_height - y))
        
        # Crop (left, top, right, bottom)
        return image.crop((x, y, x + width, y + height))
        
    except Exception as e:
        raise Exception(f"Crop failed: {str(e)}")


def auto_crop(
    image: Image.Image,
    background_color: Optional[Tuple[int, int, int]] = None,
    border: int = 0
) -> Image.Image:
    """
    Automatically crop image to content (remove uniform background).
    
    Args:
        image: PIL Image
        background_color: Background color to remove (None = auto-detect from corners)
        border: Pixels to add around content
    
    Returns:
        Auto-cropped PIL Image
    """
    try:
        # Convert to RGB if needed
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')
        
        # Auto-detect background color from corners if not specified
        if background_color is None:
            corners = [
                image.getpixel((0, 0)),
                image.getpixel((image.width - 1, 0)),
                image.getpixel((0, image.height - 1)),
                image.getpixel((image.width - 1, image.height - 1))
            ]
            # Use most common corner color
            background_color = max(set(corners), key=corners.count)
        
        # Get bounding box of non-background pixels
        bbox = image.getbbox()
        
        if bbox:
            # Add border
            x1, y1, x2, y2 = bbox
            x1 = max(0, x1 - border)
            y1 = max(0, y1 - border)
            x2 = min(image.width, x2 + border)
            y2 = min(image.height, y2 + border)
            
            return image.crop((x1, y1, x2, y2))
        else:
            # No content found, return original
            return image
            
    except Exception as e:
        raise Exception(f"Auto-crop failed: {str(e)}")


def rotate_image(
    image: Image.Image,
    angle: float,
    expand: bool = True,
    fill_color: Optional[Tuple[int, int, int, int]] = None,
    resample: Image.Resampling = Image.Resampling.BICUBIC
) -> Image.Image:
    """
    Rotate image by specified angle.
    
    Args:
        image: PIL Image
        angle: Rotation angle in degrees (positive = counter-clockwise)
        expand: Expand canvas to fit rotated image
        fill_color: Fill color for empty areas (None = transparent for RGBA, white for RGB)
        resample: Resampling filter
    
    Returns:
        Rotated PIL Image
    """
    try:
        # Normalize angle to 0-360
        angle = angle % 360
        
        # Handle simple 90-degree rotations more efficiently
        if angle == 90:
            return image.transpose(Image.Transpose.ROTATE_90)
        elif angle == 180:
            return image.transpose(Image.Transpose.ROTATE_180)
        elif angle == 270:
            return image.transpose(Image.Transpose.ROTATE_270)
        
        # Default fill color
        if fill_color is None:
            if image.mode == 'RGBA':
                fill_color = (0, 0, 0, 0)  # Transparent
            else:
                fill_color = (255, 255, 255)  # White
        
        # Rotate with specified parameters
        return image.rotate(
            -angle,  # PIL rotates clockwise, we want counter-clockwise
            resample=resample,
            expand=expand,
            fillcolor=fill_color
        )
        
    except Exception as e:
        raise Exception(f"Rotation failed: {str(e)}")


def flip_image(
    image: Image.Image,
    horizontal: bool = False,
    vertical: bool = False
) -> Image.Image:
    """
    Flip image horizontally and/or vertically.
    
    Args:
        image: PIL Image
        horizontal: Flip horizontally (mirror)
        vertical: Flip vertically
    
    Returns:
        Flipped PIL Image
    """
    try:
        result = image.copy()
        
        if horizontal:
            result = result.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        
        if vertical:
            result = result.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        
        return result
        
    except Exception as e:
        raise Exception(f"Flip failed: {str(e)}")


def add_padding(
    image: Image.Image,
    padding: int,
    color: Optional[Tuple[int, int, int, int]] = None
) -> Image.Image:
    """
    Add padding around image.
    
    Args:
        image: PIL Image
        padding: Padding size in pixels
        color: Padding color (None = transparent for RGBA, white for RGB)
    
    Returns:
        Padded PIL Image
    """
    try:
        if padding <= 0:
            return image.copy()
        
        # Default color
        if color is None:
            if image.mode == 'RGBA':
                color = (0, 0, 0, 0)
            else:
                color = (255, 255, 255)
        
        # Create new image with padding
        new_width = image.width + (padding * 2)
        new_height = image.height + (padding * 2)
        
        padded = Image.new(image.mode, (new_width, new_height), color)
        padded.paste(image, (padding, padding))
        
        return padded
        
    except Exception as e:
        raise Exception(f"Padding failed: {str(e)}")


def resize_to_width(image: Image.Image, width: int) -> Image.Image:
    """
    Resize image to specific width, maintaining aspect ratio.
    
    Args:
        image: PIL Image
        width: Target width
    
    Returns:
        Resized PIL Image
    """
    return resize_image(image, width=width, mode='fit')


def resize_to_height(image: Image.Image, height: int) -> Image.Image:
    """
    Resize image to specific height, maintaining aspect ratio.
    
    Args:
        image: PIL Image
        height: Target height
    
    Returns:
        Resized PIL Image
    """
    return resize_image(image, height=height, mode='fit')


def scale_image(image: Image.Image, scale: float) -> Image.Image:
    """
    Scale image by percentage.
    
    Args:
        image: PIL Image
        scale: Scale factor (0.5 = 50%, 2.0 = 200%)
    
    Returns:
        Scaled PIL Image
    """
    try:
        if scale <= 0:
            raise ValueError("Scale must be positive")
        
        new_width = int(image.width * scale)
        new_height = int(image.height * scale)
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
    except Exception as e:
        raise Exception(f"Scaling failed: {str(e)}")


# CLI test
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 3:

        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    operation = sys.argv[3] if len(sys.argv) > 3 else 'resize'
    
    img = Image.open(input_path)
    
    if operation == 'resize':
        width = int(sys.argv[4]) if len(sys.argv) > 4 else 800
        height = int(sys.argv[5]) if len(sys.argv) > 5 else None
        mode = sys.argv[6] if len(sys.argv) > 6 else 'fit'
        result = resize_image(img, width, height, mode)
        
    elif operation == 'crop':
        x = int(sys.argv[4])
        y = int(sys.argv[5])
        width = int(sys.argv[6])
        height = int(sys.argv[7])
        result = crop_image(img, x, y, width, height)
        
    elif operation == 'rotate':
        angle = float(sys.argv[4])
        result = rotate_image(img, angle)
        
    elif operation == 'flip':
        h = 'h' in sys.argv[4:] if len(sys.argv) > 4 else False
        v = 'v' in sys.argv[4:] if len(sys.argv) > 4 else False
        result = flip_image(img, h, v)
        
    elif operation == 'scale':
        scale = float(sys.argv[4])
        result = scale_image(img, scale)
        
    else:

        sys.exit(1)
    
    result.save(output_path)

