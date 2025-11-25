from PIL import Image, ImageFilter, ImageEnhance
import io
import numpy as np
from typing import Literal, Optional
from .super_resolution import apply_super_resolution
from .alpha_refinement import refine_alpha_channel

BackgroundRemovalEngine = Literal['rembg', 'carvekit', 'backgroundremover', 'auto']


def _remove_bg_rembg(
    image: Image.Image,
    model: str = 'u2net'
) -> Image.Image:
    """Remove background using rembg library with selectable models.

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


def _remove_bg_carvekit(image: Image.Image) -> Image.Image:
    """Remove background using CarveKit - excellent for illustrations and flat designs.
    Uses FBA Matting for high-quality edge preservation.
    """
    try:
        from carvekit.api.high import HiInterface
        interface = HiInterface(
            object_type="object",
            batch_size_seg=5,
            batch_size_matting=1,
            device='cpu',
            seg_mask_size=640,
            matting_mask_size=2048,
            trimap_prob_threshold=231,
            trimap_dilation=30,
            trimap_erosion_iters=5,
            fp16=False,
        )
        images_without_background = interface([image])
        result = images_without_background[0]
        if result.mode != 'RGBA':
            result = result.convert('RGBA')
        return result
    except Exception as e:
        raise Exception(f"CarveKit removal failed: {str(e)}")


def _remove_bg_backgroundremover(image: Image.Image) -> Image.Image:
    """Remove background using backgroundremover - excellent for sharp edges.
    Uses alpha matting for professional results.
    """
    try:
        from backgroundremover.bg import remove as bg_remove
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)
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


def _is_illustration(image: Image.Image) -> bool:
    """Detect if image is likely an illustration/flat design.

    Heuristics:
    - Low color variance (flat colors)
    - High saturation
    - Limited color palette
    """
    try:
        rgb = image.convert("RGB")
        arr = np.asarray(rgb)
        variance = arr.var()
        pixels = arr.reshape(-1, 3)
        unique_colors = len(np.unique(pixels, axis=0))
        total_pixels = len(pixels)
        color_ratio = unique_colors / total_pixels
        is_flat = variance < 400
        is_limited_palette = color_ratio < 0.1
        return is_flat or is_limited_palette
    except Exception:
        return False


def _refine_illustration_edges(image: Image.Image) -> Image.Image:
    """Refine edges for illustration-style images.
    Makes edges sharper and cleaner.
    """
    try:
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        r, g, b, alpha = image.split()
        alpha = alpha.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
        alpha = alpha.point(lambda p: 255 if p > 20 else 0)
        alpha = alpha.filter(ImageFilter.GaussianBlur(radius=0.5))
        result = Image.merge('RGBA', (r, g, b, alpha))
        return result
    except Exception:
        return image



def remove_background(
    image: Image.Image,
    engine: BackgroundRemovalEngine = 'auto',
    model: Optional[str] = None,
    upscale: bool = False,
    upscale_factor: int = 2,
    refine_alpha: bool = True,
    alpha_algorithm: str = 'cf',
) -> Image.Image:
    """Remove background from image using the best available engine.

    Args:
        image: PIL Image object
        engine: Background removal engine to use:
            - 'auto': Automatically select best engine (default)
            - 'rembg': Use rembg library
            - 'carvekit': Use CarveKit (best for illustrations)
            - 'backgroundremover': Use backgroundremover (sharp edges)
        model: Model name for rembg engine (ignored for other engines).
        upscale: Whether to apply super‑resolution after background removal.
        upscale_factor: Upscaling factor (2 or 4). Real‑ESRGAN defaults to 4×.
        refine_alpha: Whether to use PyMatting for alpha refinement.
        alpha_algorithm: PyMatting algorithm ('cf', 'knn', 'lbdm', 'lkm', 'rw').

    Returns:
        PIL Image with transparent background (RGBA).
    """
    try:
        if engine == 'auto':
            is_illust = _is_illustration(image)
            if is_illust:
                try:
                    result = _remove_bg_carvekit(image)
                except Exception:
                    try:
                        result = _remove_bg_rembg(image, model='u2netp')
                    except Exception:
                        result = _remove_bg_rembg(image, model='u2net')
                if refine_alpha:
                    result = refine_alpha_channel(result, algorithm=alpha_algorithm)
                else:
                    result = _refine_illustration_edges(result)
            else:
                try:
                    result = _remove_bg_backgroundremover(image)
                except Exception:
                    result = _remove_bg_rembg(image, model='u2net')
            if upscale:
                result = apply_super_resolution(result, factor=upscale_factor)
            return result
        if engine == 'carvekit':
            result = _remove_bg_carvekit(image)
            if _is_illustration(image):
                if refine_alpha:
                    result = refine_alpha_channel(result, algorithm=alpha_algorithm)
                else:
                    result = _refine_illustration_edges(result)
            if upscale:
                result = apply_super_resolution(result, factor=upscale_factor)
            return result
        if engine == 'backgroundremover':
            result = _remove_bg_backgroundremover(image)
            if upscale:
                result = apply_super_resolution(result, factor=upscale_factor)
            return result
        if engine == 'rembg':
            model_name = model or 'u2net'
            result = _remove_bg_rembg(image, model=model_name)
            if _is_illustration(image):
                if refine_alpha:
                    result = refine_alpha_channel(result, algorithm=alpha_algorithm)
                else:
                    result = _refine_illustration_edges(result)
            if upscale:
                result = apply_super_resolution(result, factor=upscale_factor)
            return result
        raise ValueError(f"Unknown engine: {engine}")
    except Exception:
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
    return image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info)

if __name__ == "__main__":
    import sys
    from pathlib import Path
    if len(sys.argv) < 3:
        sys.exit(1)
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    engine = sys.argv[3] if len(sys.argv) > 3 else 'auto'
    img = Image.open(input_path)
    result = remove_background(img, engine=engine)
    result.save(output_path, "PNG")
