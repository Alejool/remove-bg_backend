"""
Professional Background Removal System
Supports multiple engines for optimal quality across different image types
"""

from PIL import Image, ImageFilter, ImageEnhance
import io
import numpy as np
from typing import Literal, Optional

# ============================================================================
# MULTI-ENGINE BACKGROUND REMOVAL SYSTEM
# ============================================================================

BackgroundRemovalEngine = Literal['rembg', 'carvekit', 'backgroundremover', 'auto']


# ----------------------------------------------------------------------------
# ENGINE 1: REMBG (Multiple Models)
# ----------------------------------------------------------------------------
def _remove_bg_rembg(
    image: Image.Image,
    model: str = 'u2net'
) -> Image.Image:
    """
    Remove background using rembg library with selectable models.
    
    Available models:
    - u2net: General purpose (default)
    - u2netp: Lightweight, good for illustrations
    - u2net_human_seg: Optimized for people
    - isnet-anime: Specialized for anime characters
    - birefnet-dis: Dichotomous image segmentation
    """
    try:
        from rembg import remove
        
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)
        
        output = remove(
            buf.read(),
            model_name=model,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10
        )
        
        result = Image.open(io.BytesIO(output)).convert("RGBA")
        return result
        
    except Exception as e:
        raise Exception(f"Rembg removal failed: {str(e)}")


# ----------------------------------------------------------------------------
# ENGINE 2: CARVEKIT (Best for Illustrations)
# ----------------------------------------------------------------------------
def _remove_bg_carvekit(image: Image.Image) -> Image.Image:
    """
    Remove background using CarveKit - excellent for illustrations and flat designs.
    Uses FBA Matting for high-quality edge preservation.
    """
    try:
        from carvekit.api.high import HiInterface
        
        # Initialize CarveKit with best settings for illustrations
        interface = HiInterface(
            object_type="object",  # Can be "object" or "hairs-like"
            batch_size_seg=5,
            batch_size_matting=1,
            device='cpu',  # Change to 'cuda' if GPU available
            seg_mask_size=640,
            matting_mask_size=2048,
            trimap_prob_threshold=231,
            trimap_dilation=30,
            trimap_erosion_iters=5,
            fp16=False,
        )
        
        # Process image
        images_without_background = interface([image])
        result = images_without_background[0]
        
        # Ensure RGBA
        if result.mode != 'RGBA':
            result = result.convert('RGBA')
            
        return result
        
    except Exception as e:
        raise Exception(f"CarveKit removal failed: {str(e)}")


# ----------------------------------------------------------------------------
# ENGINE 3: BACKGROUNDREMOVER (Sharp Edges)
# ----------------------------------------------------------------------------
def _remove_bg_backgroundremover(image: Image.Image) -> Image.Image:
    """
    Remove background using backgroundremover - excellent for sharp edges.
    Uses alpha matting for professional results.
    """
    try:
        from backgroundremover.bg import remove as bg_remove
        
        # Convert to bytes
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)
        
        # Remove background with alpha matting
        output = bg_remove(
            buf.read(),
            model_name="u2net",
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_structure_size=10,
            alpha_matting_base_size=1000
        )
        
        result = Image.open(io.BytesIO(output)).convert("RGBA")
        return result
        
    except Exception as e:
        raise Exception(f"BackgroundRemover removal failed: {str(e)}")


# ----------------------------------------------------------------------------
# ILLUSTRATION DETECTION
# ----------------------------------------------------------------------------
def _is_illustration(image: Image.Image) -> bool:
    """
    Detect if image is likely an illustration/flat design.
    
    Heuristics:
    - Low color variance (flat colors)
    - High saturation
    - Limited color palette
    """
    try:
        # Convert to RGB and get array
        rgb = image.convert("RGB")
        arr = np.asarray(rgb)
        
        # Calculate variance (low = flat colors)
        variance = arr.var()
        
        # Calculate unique colors ratio
        pixels = arr.reshape(-1, 3)
        unique_colors = len(np.unique(pixels, axis=0))
        total_pixels = len(pixels)
        color_ratio = unique_colors / total_pixels
        
        # Illustration indicators:
        # - Low variance (< 400)
        # - Low color ratio (< 0.1 = limited palette)
        is_flat = variance < 400
        is_limited_palette = color_ratio < 0.1
        
        return is_flat or is_limited_palette
        
    except Exception:
        return False


# ----------------------------------------------------------------------------
# POST-PROCESSING FOR ILLUSTRATIONS
# ----------------------------------------------------------------------------
def _refine_illustration_edges(image: Image.Image) -> Image.Image:
    """
    Refine edges for illustration-style images.
    Makes edges sharper and cleaner.
    """
    try:
        # Extract alpha channel
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        r, g, b, alpha = image.split()
        
        # Sharpen alpha for crisper edges
        alpha = alpha.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
        
        # Hard threshold to remove semi-transparent artifacts
        alpha = alpha.point(lambda p: 255 if p > 20 else 0)
        
        # Slight blur to smooth jagged edges
        alpha = alpha.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Recombine
        result = Image.merge('RGBA', (r, g, b, alpha))
        
        return result
        
    except Exception as e:
        print(f"Edge refinement failed: {str(e)}")
        return image


# ============================================================================
# PUBLIC API
# ============================================================================

def remove_background(
    image: Image.Image,
    engine: BackgroundRemovalEngine = 'auto',
    model: Optional[str] = None
) -> Image.Image:
    """
    Remove background from image using the best available engine.
    
    Args:
        image: PIL Image object
        engine: Background removal engine to use:
            - 'auto': Automatically select best engine (default)
            - 'rembg': Use rembg library
            - 'carvekit': Use CarveKit (best for illustrations)
            - 'backgroundremover': Use backgroundremover (sharp edges)
        model: Model name for rembg engine (ignored for other engines):
            - 'u2net': General purpose (default)
            - 'u2netp': Lightweight, good for illustrations
            - 'u2net_human_seg': Optimized for people
            - 'isnet-anime': For anime characters
            - 'birefnet-dis': Dichotomous segmentation
    
    Returns:
        PIL Image with transparent background (RGBA)
    """
    try:
        # Auto-select best engine
        if engine == 'auto':
            is_illust = _is_illustration(image)
            
            # Try CarveKit for illustrations (best quality)
            if is_illust:
                try:
                    print("🎨 Detected illustration - using CarveKit")
                    result = _remove_bg_carvekit(image)
                    return _refine_illustration_edges(result)
                except Exception as e:
                    print(f"CarveKit failed, falling back to rembg: {e}")
                    try:
                        result = _remove_bg_rembg(image, model='u2netp')
                        return _refine_illustration_edges(result)
                    except Exception:
                        result = _remove_bg_rembg(image, model='u2net')
                        return _refine_illustration_edges(result)
            
            # For photos, try backgroundremover first (sharp edges)
            else:
                try:
                    print("📷 Detected photo - using BackgroundRemover")
                    return _remove_bg_backgroundremover(image)
                except Exception as e:
                    print(f"BackgroundRemover failed, falling back to rembg: {e}")
                    return _remove_bg_rembg(image, model='u2net')
        
        # Use specific engine
        elif engine == 'carvekit':
            result = _remove_bg_carvekit(image)
            if _is_illustration(image):
                return _refine_illustration_edges(result)
            return result
            
        elif engine == 'backgroundremover':
            return _remove_bg_backgroundremover(image)
            
        elif engine == 'rembg':
            model_name = model or 'u2net'
            result = _remove_bg_rembg(image, model=model_name)
            if _is_illustration(image):
                return _refine_illustration_edges(result)
            return result
            
        else:
            raise ValueError(f"Unknown engine: {engine}")
            
    except Exception as e:
        # Ultimate fallback: basic rembg
        print(f"All engines failed, using basic rembg: {e}")
        try:
            from rembg import remove
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            buf.seek(0)
            output = remove(buf.read())
            return Image.open(io.BytesIO(output)).convert("RGBA")
        except Exception as final_error:
            raise Exception(f"All background removal methods failed: {final_error}")


def has_transparency(image: Image.Image) -> bool:
    """Check if image has transparency."""
    return image.mode in ('RGBA', 'LA') or (
        image.mode == 'P' and 'transparency' in image.info
    )


# ============================================================================
# CLI TEST
# ============================================================================
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 3:
        print("Usage: python background_remover.py input.png output.png [engine]")
        print("Engines: auto (default), rembg, carvekit, backgroundremover")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    engine = sys.argv[3] if len(sys.argv) > 3 else 'auto'
    
    print(f"Loading image: {input_path}")
    img = Image.open(input_path)
    
    print(f"Removing background using engine: {engine}")
    result = remove_background(img, engine=engine)
    
    print(f"Saving result: {output_path}")
    result.save(output_path, "PNG")
    
    print("✅ Done!")
