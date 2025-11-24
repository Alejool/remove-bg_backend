"""
Image Enhancement Module
Advanced quality improvements using OpenCV
"""

import cv2
import numpy as np
from PIL import Image
from typing import Literal, Optional, Tuple

EnhanceMethod = Literal['clahe', 'histogram', 'manual']
DenoiseMethod = Literal['gaussian', 'bilateral', 'nlmeans']


def pil_to_cv2(image: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV format."""
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def cv2_to_pil(image: np.ndarray) -> Image.Image:
    """Convert OpenCV image to PIL format."""
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def denoise_image(
    image: Image.Image,
    method: DenoiseMethod = 'bilateral',
    strength: int = 5
) -> Image.Image:
    """
    Remove noise from image.
    
    Args:
        image: PIL Image
        method: Denoising method
            - 'gaussian': Fast, simple blur
            - 'bilateral': Preserves edges while denoising
            - 'nlmeans': Best quality, slower (Non-local means)
        strength: Denoising strength (1-10)
    
    Returns:
        Denoised PIL Image
    """
    try:
        cv_img = pil_to_cv2(image)
        strength = max(1, min(10, strength))
        
        if method == 'gaussian':
            # Simple Gaussian blur
            kernel_size = strength * 2 + 1
            result = cv2.GaussianBlur(cv_img, (kernel_size, kernel_size), 0)
            
        elif method == 'bilateral':
            # Bilateral filter - preserves edges
            d = strength * 2
            sigma_color = strength * 15
            sigma_space = strength * 15
            result = cv2.bilateralFilter(cv_img, d, sigma_color, sigma_space)
            
        elif method == 'nlmeans':
            # Non-local means - best quality
            h = strength * 3
            result = cv2.fastNlMeansDenoisingColored(cv_img, None, h, h, 7, 21)
            
        else:
            raise ValueError(f"Unknown denoise method: {method}")
        
        return cv2_to_pil(result)
        
    except Exception as e:
        raise Exception(f"Denoising failed: {str(e)}")


def sharpen_image(
    image: Image.Image,
    amount: float = 1.0,
    radius: float = 1.0,
    threshold: int = 0
) -> Image.Image:
    """
    Sharpen image using unsharp mask.
    
    Args:
        image: PIL Image
        amount: Sharpening strength (0.0-3.0, default 1.0)
        radius: Blur radius for mask (0.5-3.0, default 1.0)
        threshold: Minimum brightness change to sharpen (0-255, default 0)
    
    Returns:
        Sharpened PIL Image
    """
    try:
        cv_img = pil_to_cv2(image)
        
        # Create Gaussian blur
        kernel_size = int(radius * 4) | 1  # Ensure odd number
        blurred = cv2.GaussianBlur(cv_img, (kernel_size, kernel_size), radius)
        
        # Unsharp mask = original + amount * (original - blurred)
        sharpened = cv2.addWeighted(cv_img, 1.0 + amount, blurred, -amount, 0)
        
        # Apply threshold if specified
        if threshold > 0:
            diff = cv2.absdiff(cv_img, blurred)
            mask = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)[1]
            sharpened = np.where(mask > 0, sharpened, cv_img)
        
        # Clip values to valid range
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
        
        return cv2_to_pil(sharpened)
        
    except Exception as e:
        raise Exception(f"Sharpening failed: {str(e)}")


def enhance_contrast(
    image: Image.Image,
    method: EnhanceMethod = 'clahe',
    clip_limit: float = 2.0,
    tile_size: int = 8
) -> Image.Image:
    """
    Enhance image contrast.
    
    Args:
        image: PIL Image
        method: Enhancement method
            - 'clahe': Contrast Limited Adaptive Histogram Equalization (best)
            - 'histogram': Global histogram equalization
            - 'manual': Use adjust_brightness_contrast instead
        clip_limit: CLAHE clip limit (1.0-4.0, default 2.0)
        tile_size: CLAHE tile size (4-16, default 8)
    
    Returns:
        Contrast-enhanced PIL Image
    """
    try:
        cv_img = pil_to_cv2(image)
        
        if method == 'clahe':
            # CLAHE - best for most images
            lab = cv2.cvtColor(cv_img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            clahe = cv2.createCLAHE(
                clipLimit=clip_limit,
                tileGridSize=(tile_size, tile_size)
            )
            l = clahe.apply(l)
            
            enhanced = cv2.merge([l, a, b])
            result = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
        elif method == 'histogram':
            # Global histogram equalization
            ycrcb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2YCrCb)
            y, cr, cb = cv2.split(ycrcb)
            
            y = cv2.equalizeHist(y)
            
            enhanced = cv2.merge([y, cr, cb])
            result = cv2.cvtColor(enhanced, cv2.COLOR_YCrCb2BGR)
            
        else:
            raise ValueError(f"Unknown contrast method: {method}")
        
        return cv2_to_pil(result)
        
    except Exception as e:
        raise Exception(f"Contrast enhancement failed: {str(e)}")


def adjust_brightness_contrast(
    image: Image.Image,
    brightness: int = 0,
    contrast: int = 0
) -> Image.Image:
    """
    Manually adjust brightness and contrast.
    
    Args:
        image: PIL Image
        brightness: Brightness adjustment (-100 to 100)
        contrast: Contrast adjustment (-100 to 100)
    
    Returns:
        Adjusted PIL Image
    """
    try:
        cv_img = pil_to_cv2(image)
        
        # Normalize inputs
        brightness = max(-100, min(100, brightness))
        contrast = max(-100, min(100, contrast))
        
        # Convert to float for calculations
        img_float = cv_img.astype(np.float32)
        
        # Apply brightness (additive)
        if brightness != 0:
            img_float = img_float + (brightness * 2.55)
        
        # Apply contrast (multiplicative)
        if contrast != 0:
            factor = (259 * (contrast + 255)) / (255 * (259 - contrast))
            img_float = 128 + factor * (img_float - 128)
        
        # Clip and convert back
        result = np.clip(img_float, 0, 255).astype(np.uint8)
        
        return cv2_to_pil(result)
        
    except Exception as e:
        raise Exception(f"Brightness/contrast adjustment failed: {str(e)}")


def adjust_color(
    image: Image.Image,
    saturation: int = 0,
    hue: int = 0,
    temperature: int = 0
) -> Image.Image:
    """
    Adjust color properties.
    
    Args:
        image: PIL Image
        saturation: Saturation adjustment (-100 to 100)
        hue: Hue shift (-180 to 180 degrees)
        temperature: Color temperature (-100 to 100, negative=cooler, positive=warmer)
    
    Returns:
        Color-adjusted PIL Image
    """
    try:
        cv_img = pil_to_cv2(image)
        
        # Convert to HSV for saturation and hue adjustments
        hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)
        
        # Adjust saturation
        if saturation != 0:
            sat_factor = 1.0 + (saturation / 100.0)
            s = np.clip(s * sat_factor, 0, 255)
        
        # Adjust hue
        if hue != 0:
            h = (h + hue) % 180
        
        # Merge back
        hsv = cv2.merge([h, s, v]).astype(np.uint8)
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Adjust temperature (blue-orange balance)
        if temperature != 0:
            temp_factor = temperature / 100.0
            if temp_factor > 0:
                # Warmer (more orange/red)
                result[:, :, 2] = np.clip(result[:, :, 2] * (1 + temp_factor * 0.3), 0, 255)  # Red
                result[:, :, 0] = np.clip(result[:, :, 0] * (1 - temp_factor * 0.3), 0, 255)  # Blue
            else:
                # Cooler (more blue)
                result[:, :, 0] = np.clip(result[:, :, 0] * (1 - temp_factor * 0.3), 0, 255)  # Blue
                result[:, :, 2] = np.clip(result[:, :, 2] * (1 + temp_factor * 0.3), 0, 255)  # Red
        
        return cv2_to_pil(result)
        
    except Exception as e:
        raise Exception(f"Color adjustment failed: {str(e)}")


def enhance_edges(
    image: Image.Image,
    strength: float = 1.0
) -> Image.Image:
    """
    Enhance edges in the image.
    
    Args:
        image: PIL Image
        strength: Edge enhancement strength (0.0-2.0)
    
    Returns:
        Edge-enhanced PIL Image
    """
    try:
        cv_img = pil_to_cv2(image)
        
        # Detect edges using Laplacian
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian = np.uint8(np.absolute(laplacian))
        
        # Convert back to 3 channels
        edges = cv2.cvtColor(laplacian, cv2.COLOR_GRAY2BGR)
        
        # Blend with original
        result = cv2.addWeighted(cv_img, 1.0, edges, strength, 0)
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        return cv2_to_pil(result)
        
    except Exception as e:
        raise Exception(f"Edge enhancement failed: {str(e)}")


def auto_enhance(
    image: Image.Image,
    denoise: bool = True,
    sharpen: bool = True,
    contrast: bool = True
) -> Image.Image:
    """
    Automatically enhance image with optimal settings.
    
    Args:
        image: PIL Image
        denoise: Apply denoising
        sharpen: Apply sharpening
        contrast: Apply contrast enhancement
    
    Returns:
        Auto-enhanced PIL Image
    """
    try:
        result = image.copy()
        
        # Step 1: Denoise (if needed)
        if denoise:
            result = denoise_image(result, method='bilateral', strength=3)
        
        # Step 2: Enhance contrast
        if contrast:
            result = enhance_contrast(result, method='clahe', clip_limit=2.0)
        
        # Step 3: Sharpen
        if sharpen:
            result = sharpen_image(result, amount=0.8, radius=1.0)
        
        return result
        
    except Exception as e:
        raise Exception(f"Auto enhancement failed: {str(e)}")


# CLI test
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 3:
        print("Usage: python enhancer.py input.jpg output.jpg [operation]")
        print("Operations: denoise, sharpen, contrast, auto")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    operation = sys.argv[3] if len(sys.argv) > 3 else 'auto'
    
    img = Image.open(input_path)
    
    if operation == 'denoise':
        result = denoise_image(img, method='bilateral', strength=5)
    elif operation == 'sharpen':
        result = sharpen_image(img, amount=1.5)
    elif operation == 'contrast':
        result = enhance_contrast(img, method='clahe')
    elif operation == 'auto':
        result = auto_enhance(img)
    else:
        print(f"Unknown operation: {operation}")
        sys.exit(1)
    
    result.save(output_path)
    print(f"✅ Enhanced image saved to {output_path}")
