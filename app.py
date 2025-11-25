"""
Image Manager - FastAPI Backend
Professional image processing API with background removal, optimization, and format conversion
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from PIL import Image
import time
from pathlib import Path
from typing import List, Optional
import io

# Import local modules
import config
from processors import (
    remove_background,
    optimize_image,
    save_optimized,
    resize_to_width,
    get_file_size_reduction,
)
from utils import (
    format_file_size,
    sanitize_filename,
    generate_placeholder_blur,
    get_image_info,
    allowed_file,
    calculate_processing_time,
)

# Initialize FastAPI app
app = FastAPI(
    title="Image Manager API",
    description="Professional image processing with AI background removal",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving processed images
app.mount("/outputs", StaticFiles(directory=str(config.OUTPUT_DIR)), name="outputs")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Image Manager API",
        "version": "1.0.0"
    }


@app.post("/api/process")
async def process_image(
    file: UploadFile = File(...),
    remove_bg: bool = Form(False),
    bg_engine: str = Form("auto"),
    bg_model: str = Form("u2net"),
    formats: str = Form("webp"),
    sizes: str = Form("800"),
    quality: int = Form(95),
    optimize: bool = Form(True),
    generate_placeholder: bool = Form(True),
):
    """
    Process an image with various transformations
    
    Parameters:
    - file: Image file to process
    - remove_bg: Remove background (AI-powered)
    - bg_engine: Background removal engine (auto, rembg, carvekit, backgroundremover)
    - bg_model: Model for rembg engine (u2net, u2netp, u2net_human_seg, isnet-anime, birefnet-dis)
    - formats: Comma-separated output formats (webp,avif,png,jpeg)
    - sizes: Comma-separated width sizes (400,800,1200)
    - quality: Quality level 0-100 (default 95 for high quality)
    - optimize: Enable optimization
    - generate_placeholder: Generate blur placeholder
    """
    start_time = time.time()
    
    try:
        # Validate file
        if not allowed_file(file.filename, config.ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(config.ALLOWED_EXTENSIONS)}"
            )
        
        # Read uploaded file
        contents = await file.read()
        
        # Check file size
        if len(contents) > config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {format_file_size(config.MAX_FILE_SIZE)}"
            )
        
        # Open image
        original_image = Image.open(io.BytesIO(contents))
        original_info = get_image_info(original_image)
        original_size = len(contents)
        
        # Process image
        processed_image = original_image.copy()
        
        # Remove background if requested
        if remove_bg:
            processed_image = remove_background(
                processed_image,
                engine=bg_engine,
                model=bg_model if bg_engine == 'rembg' else None
            )
        
        # Parse formats and sizes
        output_formats = [f.strip() for f in formats.split(',') if f.strip()]
        output_sizes = [int(s.strip()) for s in sizes.split(',') if s.strip()]
        
        # Validate formats
        for fmt in output_formats:
            if fmt not in config.OUTPUT_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid format: {fmt}. Allowed: {', '.join(config.OUTPUT_FORMATS)}"
                )
        
        # Generate processed variants
        processed_files = []
        
        for fmt in output_formats:
            for size in output_sizes:
                # Resize image
                resized = resize_to_width(processed_image, size)
                
                # Optimize if requested
                if optimize:
                    resized = optimize_image(
                        resized,
                        format=fmt,
                        quality=quality,
                        remove_exif=config.REMOVE_EXIF,
                        enhance=True
                    )
                
                # Generate filename
                safe_filename = sanitize_filename(file.filename)
                stem = Path(safe_filename).stem
                output_filename = f"{stem}_{size}.{fmt}"
                output_path = config.OUTPUT_DIR / output_filename
                
                # Save optimized image
                file_size = save_optimized(
                    resized,
                    output_path,
                    format=fmt,
                    quality=quality,
                    remove_exif=config.REMOVE_EXIF
                )
                
                # Calculate reduction
                reduction = get_file_size_reduction(original_size, file_size)
                
                processed_files.append({
                    "format": fmt,
                    "size": str(size),
                    "url": f"/outputs/{output_filename}",
                    "filename": output_filename,
                    "filesize": format_file_size(file_size),
                    "filesize_bytes": file_size,
                    "reduction": f"{reduction:.1f}%"
                })
        
        # Generate placeholder if requested
        placeholder = None
        if generate_placeholder:
            placeholder = generate_placeholder_blur(
                processed_image,
                size=config.PLACEHOLDER_SIZE
            )
        
        # Calculate processing time
        end_time = time.time()
        processing_time = calculate_processing_time(start_time, end_time)
        
        # Return response
        return JSONResponse({
            "success": True,
            "original": {
                "filename": file.filename,
                "size": format_file_size(original_size),
                "size_bytes": original_size,
                "dimensions": original_info['dimensions'],
                "width": original_info['width'],
                "height": original_info['height'],
            },
            "processed": processed_files,
            "placeholder": placeholder,
            "processing_time": processing_time,
            "options": {
                "background_removed": remove_bg,
                "optimized": optimize,
                "quality": quality,
                "formats": output_formats,
                "sizes": output_sizes,
            }
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD
    )
