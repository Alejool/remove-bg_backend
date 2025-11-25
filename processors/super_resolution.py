import torch
from pathlib import Path
from PIL import Image

# Lazy load model to avoid heavy import at startup
_model = None

def _load_model(device: str = 'cpu'):
    global _model
    if _model is None:
        try:
            from realesrgan import RealESRGAN
        except ImportError as e:
            raise ImportError('Real-ESRGAN package not installed. Install with `pip install realesrgan`')
        _model = RealESRGAN(device)
        # Load pretrained weights (will download if not present)
        _model.load_weights('RealESRGAN_x4.pth')
    return _model

def apply_super_resolution(image: Image.Image, factor: int = 2, device: str = 'cpu') -> Image.Image:
    """Upscale image using Real-ESRGAN.

    Args:
        image: PIL Image (RGBA or RGB).
        factor: Upscaling factor (2 or 4). Real-ESRGAN supports 4x; for 2x we use half the size after 4x.
        device: 'cpu' or 'cuda'.
    Returns:
        Upscaled PIL Image.
    """
    # Ensure image is RGB for the model
    if image.mode != 'RGB':
        rgb_image = image.convert('RGB')
    else:
        rgb_image = image

    model = _load_model(device)
    # Real-ESRGAN default is 4x; if factor is 2, we upscale 4x then downscale 0.5
    upscaled = model.predict(rgb_image)
    if factor == 2:
        width, height = upscaled.size
        upscaled = upscaled.resize((width // 2, height // 2), Image.LANCZOS)
    # Preserve alpha channel if present
    if image.mode == 'RGBA':
        r, g, b, a = image.split()
        upscaled = Image.merge('RGBA', (upscaled.split()[0], upscaled.split()[1], upscaled.split()[2], a.resize(upscaled.size, Image.LANCZOS)))
    return upscaled
