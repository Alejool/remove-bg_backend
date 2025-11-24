"""
Utility Helper Functions
"""

from PIL import Image, ImageFilter
import base64
import io
import re
from pathlib import Path
from datetime import datetime


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "2.4 MB", "124 KB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove unsafe characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = Path(filename).name
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\s\-\.]', '', filename)
    filename = re.sub(r'[\s]+', '_', filename)
    
    return filename


def generate_unique_filename(original_filename: str, suffix: str = "") -> str:
    """
    Generate unique filename with timestamp
    
    Args:
        original_filename: Original filename
        suffix: Optional suffix to add before extension
        
    Returns:
        Unique filename
    """
    path = Path(original_filename)
    stem = path.stem
    ext = path.suffix
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if suffix:
        return f"{stem}_{suffix}_{timestamp}{ext}"
    else:
        return f"{stem}_{timestamp}{ext}"


def generate_placeholder_blur(image: Image.Image, size: int = 40) -> str:
    """
    Generate a tiny blurred placeholder image as base64
    
    Args:
        image: PIL Image object
        size: Size of the placeholder (default 40px for better visibility)
        
    Returns:
        Base64 encoded data URI
    """
    try:
        # Create thumbnail
        img = image.copy()
        
        # Convert to RGB if needed (for JPEG encoding)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background for transparency
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
                img = background
            else:
                img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Create thumbnail with better quality
        img.thumbnail((size, size), Image.Resampling.LANCZOS)
        
        # Apply stronger blur for better placeholder effect
        img = img.filter(ImageFilter.GaussianBlur(radius=4))
        
        # Convert to base64 with JPEG for smaller size
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=60, optimize=True)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/jpeg;base64,{img_str}"
    
    except Exception as e:
        print(f"Error generating placeholder: {str(e)}")
        return ""


def get_image_info(image: Image.Image) -> dict:
    """
    Get image information
    
    Args:
        image: PIL Image object
        
    Returns:
        Dictionary with image info
    """
    width, height = image.size
    
    return {
        'width': width,
        'height': height,
        'dimensions': f"{width}x{height}",
        'mode': image.mode,
        'format': image.format or 'Unknown',
    }


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """
    Check if file extension is allowed
    
    Args:
        filename: Filename to check
        allowed_extensions: Set of allowed extensions
        
    Returns:
        Boolean indicating if file is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def calculate_processing_time(start_time: float, end_time: float) -> str:
    """
    Calculate and format processing time
    
    Args:
        start_time: Start timestamp
        end_time: End timestamp
        
    Returns:
        Formatted time string (e.g., "3.2s")
    """
    duration = end_time - start_time
    
    if duration < 1:
        return f"{duration * 1000:.0f}ms"
    else:
        return f"{duration:.1f}s"
