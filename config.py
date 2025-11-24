import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Upload and output directories
UPLOAD_DIR = BASE_DIR / "upload"
OUTPUT_DIR = BASE_DIR / "outputs"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# File upload settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

# Output format settings
OUTPUT_FORMATS = ['webp', 'avif', 'png', 'jpeg']
DEFAULT_QUALITY = 95  # Increased from 85 for better quality
DEFAULT_SIZES = [400, 800, 1200]

# Processing settings
REMOVE_EXIF = True
ENABLE_OPTIMIZATION = True
GENERATE_PLACEHOLDER = True
PLACEHOLDER_SIZE = 40  # Size for blur placeholder (increased for better visibility)

# Image processing settings
RESIZE_MODES = {
    'contain': 'contain',  # Fit inside dimensions, maintain aspect ratio
    'cover': 'cover',      # Cover dimensions, crop if needed
    'fill': 'fill'         # Stretch to exact dimensions
}

DEFAULT_RESIZE_MODE = 'contain'

# Server settings
HOST = "0.0.0.0"
PORT = 8000
RELOAD = True

# CORS settings
CORS_ORIGINS = [
    "http://localhost:4321",
    "http://localhost:3000",
    "http://127.0.0.1:4321",
    "http://127.0.0.1:3000",
]
