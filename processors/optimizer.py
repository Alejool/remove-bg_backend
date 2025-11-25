from PIL import Image, ImageFilter, ImageEnhance
from pathlib import Path
import io
import sys
import traceback


# Register AVIF support
try:
    import pillow_heif
    from pillow_heif import register_heif_opener, register_avif_opener
    from PIL import ImageResampling # Asegurar importación para las nuevas versiones de PIL
    
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
        supported_by_name = 'AVIF' in formats or '.avif' in ext_map

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
    Optimize image with gentle enhancements for better quality.
    Lógica ajustada para priorizar la calidad y el realce controlado.
    """
    try:
        img = image.copy()
        fmt = format.lower()

        # Handle format-specific mode conversions
        if fmt in ('jpeg', 'jpg'):
            # Convertir a RGB (manejar transparencia mezclando con fondo blanco)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                # Asegurar la conversión a RGBA antes de la mezcla para extraer la máscara alfa correctamente
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                    
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

        elif fmt == 'avif':
            # Si tiene transparencia o es LA/P, convertir a RGBA
            if img.mode in ('LA', 'P'):
                img = img.convert('RGBA')
            elif img.mode != 'RGBA' and img.mode != 'RGB':
                img = img.convert('RGB') # AVIF soporta RGB o RGBA

        elif fmt in ('webp', 'png'):
            # Formatos que soportan transparencia: asegurar RGBA si la tiene o RGB si no la tiene
            if img.mode not in ('RGBA', 'RGB'):
                img = img.convert('RGBA')
            elif img.mode == 'P':
                 img = img.convert('RGBA')


        # Apply GENTLE enhancements only for lossy formats
        # No se aplica realce a PNG (lossless)
        if enhance and fmt not in ('png',):
            
            # --- MEJORA DE CALIDAD: UNARP MASK (mejor que SHARPEN) ---
            # UnsharpMask permite más control para evitar artefactos
            # Radio 1.5, Porcentaje 150, Umbral 3 es un buen realce "gentle" de alta calidad
            img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=150, threshold=3))
            
            # --- MEJORA DE CONTRASTE Y COLOR ---
            
            # GENTLE contrast (1.10 es un valor seguro para realce sutil)
            img = ImageEnhance.Contrast(img).enhance(1.10)
            
            # GENTLE color (1.08 es un valor seguro para realce sutil)
            img = ImageEnhance.Color(img).enhance(1.08)

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
    Save optimized image with high quality settings.
    Lógica ajustada para maximizar la calidad en el guardado.
    """
    try:
        save_kwargs = {}
        fmt = format.lower()
        
        # Asegurar que el modo es correcto antes de guardar
        if fmt in ('jpeg', 'jpg') and image.mode != 'RGB':
            image = image.convert('RGB')

        if fmt == 'webp':
            save_kwargs = {
                'format': 'WEBP',
                'quality': max(95, quality), # Subir el mínimo a 95
                'method': 6, # Mayor calidad, más lento
                'lossless': quality >= 100,
            }

        elif fmt == 'avif':
            save_kwargs = {
                'format': 'AVIF',
                'quality': max(90, quality), # Subir el mínimo a 90
                'speed': 1, # Priorizar calidad (más lento)
            }

        elif fmt == 'png':
            save_kwargs = {
                'format': 'PNG',
                'optimize': True,
                'compress_level': 9, # Compresión máxima
            }

        elif fmt in ('jpeg', 'jpg'):
            save_kwargs = {
                'format': 'JPEG',
                'quality': max(95, quality), # Mínimo 95 de calidad
                'optimize': True,
                'progressive': True,
                'subsampling': 0, # MÁXIMA calidad de color (4:4:4)
            }

        if remove_exif and fmt != 'png':
            # Manejo de EXIF
            if image.info and 'exif' in image.info:
                save_kwargs['exif'] = b''
            else:
                 save_kwargs.pop('exif', None)


        if fmt == 'avif':
            save_kwargs.pop('exif', None)
            supported = _diagnose_avif_support()
            if not supported:
                # Fallback a WebP si AVIF no es soportado
                print("AVIF save support not registered in Pillow, falling back to WEBP.")
                return save_optimized(image, output_path, 'webp', quality, remove_exif)

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