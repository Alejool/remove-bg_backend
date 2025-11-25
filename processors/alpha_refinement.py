"""
Alpha refinement using PyMatting algorithms.
Adapted from ailia-models rembg implementation.
"""
import numpy as np
import cv2
from PIL import Image
from scipy.ndimage import binary_erosion
from pymatting.alpha.estimate_alpha_cf import estimate_alpha_cf
from pymatting.alpha.estimate_alpha_knn import estimate_alpha_knn
from pymatting.alpha.estimate_alpha_lbdm import estimate_alpha_lbdm
from pymatting.alpha.estimate_alpha_lkm import estimate_alpha_lkm
from pymatting.alpha.estimate_alpha_rw import estimate_alpha_rw


def norm_pred(d: np.ndarray) -> np.ndarray:
    """Normalize prediction values to 0-1 range."""
    ma = np.max(d)
    mi = np.min(d)
    if ma == mi:
        return np.zeros_like(d)
    return (d - mi) / (ma - mi)


def estimate_alpha(
    image: Image.Image,
    mask: Image.Image,
    algorithm: str = 'cf',
    foreground_threshold: int = 240,
    background_threshold: int = 10,
    erode_structure_size: int = 10
) -> Image.Image:
    """
    Refine alpha mask using PyMatting algorithms.
    
    Args:
        image: Original RGB/RGBA PIL Image
        mask: Initial alpha mask PIL Image (grayscale)
        algorithm: Algorithm to use ('cf', 'knn', 'lbdm', 'lkm', 'rw')
        foreground_threshold: Threshold for certain foreground (0-255)
        background_threshold: Threshold for certain background (0-255)
        erode_structure_size: Size of erosion structure
        
    Returns:
        Refined alpha mask as PIL Image (grayscale)
    """
    # Convert PIL to numpy
    img_np = np.array(image.convert('RGB'))
    mask_np = np.array(mask.convert('L'))
    
    # Guess likely foreground/background
    is_foreground = mask_np > foreground_threshold
    is_background = mask_np < background_threshold
    
    # Erode foreground/background to create clear separation
    structure = None
    if erode_structure_size > 0:
        structure = np.ones(
            (erode_structure_size, erode_structure_size), dtype=np.uint8
        )
    
    is_foreground = binary_erosion(is_foreground, structure=structure)
    is_background = binary_erosion(is_background, structure=structure, border_value=1)
    
    # Build trimap
    # 0   = background
    # 128 = unknown
    # 255 = foreground
    trimap = np.full(mask_np.shape, dtype=np.uint8, fill_value=128)
    trimap[is_foreground] = 255
    trimap[is_background] = 0
    
    # Check if trimap contains foreground values
    if not (255 in trimap):
        # No foreground detected, return original mask
        return mask
    
    # Normalize for pymatting (expects 0-1 range)
    img_normalized = img_np / 255.0
    trimap_normalized = trimap / 255.0
    
    # Select algorithm
    algorithm_map = {
        'cf': estimate_alpha_cf,
        'knn': estimate_alpha_knn,
        'lbdm': estimate_alpha_lbdm,
        'lkm': estimate_alpha_lkm,
        'rw': estimate_alpha_rw,
    }
    
    if algorithm not in algorithm_map:
        raise ValueError(
            f"Unknown algorithm '{algorithm}'. "
            f"Choose from: {list(algorithm_map.keys())}"
        )
    
    estimate_func = algorithm_map[algorithm]
    
    try:
        # Estimate alpha using selected algorithm
        alpha = estimate_func(img_normalized, trimap_normalized)
        alpha = np.clip(alpha * 255, 0, 255).astype(np.uint8)
        
        # Convert back to PIL
        return Image.fromarray(alpha, mode='L')
    except Exception as e:
        # If refinement fails, return original mask
        print(f"Alpha refinement failed: {e}. Using original mask.")
        return mask


def refine_alpha_channel(
    image: Image.Image,
    algorithm: str = 'cf',
    **kwargs
) -> Image.Image:
    """
    Refine the alpha channel of an RGBA image.
    
    Args:
        image: RGBA PIL Image
        algorithm: PyMatting algorithm to use
        **kwargs: Additional arguments for estimate_alpha
        
    Returns:
        RGBA PIL Image with refined alpha channel
    """
    if image.mode != 'RGBA':
        raise ValueError("Image must be in RGBA mode")
    
    # Split channels
    r, g, b, a = image.split()
    
    # Create RGB version for refinement
    rgb = Image.merge('RGB', (r, g, b))
    
    # Refine alpha
    refined_alpha = estimate_alpha(rgb, a, algorithm=algorithm, **kwargs)
    
    # Merge back
    return Image.merge('RGBA', (r, g, b, refined_alpha))
