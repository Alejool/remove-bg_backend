"""
Image Optimizer Processor
Handles image optimization, compression, and format conversion
"""

from PIL import Image, ImageFilter, ImageEnhance
from pathlib import Path
import io
import sys
import traceback




# Register AVIF support
try:
    import pillow_heif
    from pillow_heif import register_heif_opener, register_avif_opener
    
    register_heif_opener()
    register_avif_opener()
    

    
    if ".avif" not in Image.registered_extensions():
        from pillow_heif import HeifImagePlugin
        Image.register_extension("AVIF", ".avif")
        Image.register_save("AVIF", HeifImagePlugin.HeifImageFile._save)

except Exception as e:
    pass



def _diagnose_avif_support():
    """Diagnostic helper for AVIF support"""
    try:
        ext_map = Image.registered_extensions()
        formats = set(ext_map.values())
        supported_by_name = 'AVIF' in formats or 'avif' in formats

        return supported_by_name
    except Exception:

        traceback.print_exc()
        return False


def optimize_image(
    image: Image.Image,
    format: str = 'webp',
    quality: int = 95,
    remove_exif: bool = True,
    enhance: bool = True
) -> Image.Image:
    """
    Optimize image with gentle enhancements for better quality
    """
    try:
        img = image.copy()

        # Handle format-specific mode conversions
        if format.lower() in ('jpeg', 'jpg'):
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

        elif format.lower() == 'avif':
            if img.mode == 'RGBA':
                pass
            elif img.mode in ('LA', 'P'):
                img = img.convert('RGBA')
            else:
                img = img.convert('RGB')

        elif format.lower() in ('webp', 'png'):
            if img.mode not in ('RGBA', 'RGB'):
                img = img.convert('RGBA')

        # Apply GENTLE enhancements only for lossy formats
        if enhance and format.lower() not in ('png',):
            # GENTLE sharpening
            img = img.filter(ImageFilter.SHARPEN)
            
            # GENTLE contrast (reduced from 1.15 to 1.08)
            img = ImageEnhance.Contrast(img).enhance(1.08)
            
            # GENTLE color (reduced from 1.1 to 1.05)
            img = ImageEnhance.Color(img).enhance(1.05)

        return img

    except Exception as e:
        raise Exception(f"Image optimization failed: {str(e)}")


def save_optimized(
    image: Image.Image,
    output_path: Path,
    format: str = 'webp',
    quality: int = 95,
    remove_exif: bool = True
) -> int:
    """
    Save optimized image with high quality settings
    """
    try:
        save_kwargs = {}
        fmt = format.lower()

        if fmt == 'webp':
            save_kwargs = {
                'format': 'WEBP',
                'quality': max(90, quality),
                'method': 6,
                'lossless': quality >= 100,
            }

        elif fmt == 'avif':
            save_kwargs = {
                'format': 'AVIF',
                'quality': max(85, quality),
                'speed': 2,
            }

        elif fmt == 'png':
            save_kwargs = {
                'format': 'PNG',
                'optimize': True,
                'compress_level': 9,
            }

        elif fmt in ('jpeg', 'jpg'):
            save_kwargs = {
                'format': 'JPEG',
                'quality': max(90, quality),
                'optimize': True,
                'progressive': True,
                'subsampling': 0,
            }

        if remove_exif and fmt != 'png':
            save_kwargs['exif'] = b''

        if fmt == 'avif':
            save_kwargs.pop('exif', None)
            supported = _diagnose_avif_support()
            if not supported:
                raise Exception("AVIF save support not registered in Pillow.")

        # Save image
        buffer = io.BytesIO()
        image.save(buffer, **save_kwargs)
        buffer.seek(0)
        with open(output_path, 'wb') as f:
            f.write(buffer.read())

        return output_path.stat().st_size

    except Exception as e:
        raise Exception(f"Failed to save optimized image: {str(e)}")


def get_file_size_reduction(original_size: int, new_size: int) -> float:
    """Calculate percentage reduction in file size"""
    if original_size == 0:
        return 0.0
    reduction = ((original_size - new_size) / original_size) * 100
    return max(0.0, reduction)
