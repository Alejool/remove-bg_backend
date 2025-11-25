from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from PIL import Image
import time
from pathlib import Path
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

app = FastAPI(
    title="Image Manager API",
    description="Professional image processing with AI background removal",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=str(config.OUTPUT_DIR)), name="outputs")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

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
    upscale: bool = Form(False),
    upscale_factor: int = Form(2),
    refine_alpha: bool = Form(True),
    alpha_algorithm: str = Form("cf"),
):
    """Process an image with optional background removal and super‑resolution.

    Parameters:
    - file: Image file to process
    - remove_bg: Whether to remove background
    - bg_engine: Engine for background removal
    - bg_model: Model name for rembg (if used)
    - formats: Output formats (comma‑separated)
    - sizes: Output widths (comma‑separated)
    - quality: Output quality (0‑100)
    - optimize: Optimize output images
    - generate_placeholder: Generate blur placeholder
    - upscale: Apply super‑resolution after processing
    - upscale_factor: Factor (2 or 4)
    - refine_alpha: Use PyMatting for alpha refinement
    - alpha_algorithm: PyMatting algorithm (cf/knn/lbdm/lkm/rw)
    """
    start_time = time.time()
    try:
        if not allowed_file(file.filename, config.ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(config.ALLOWED_EXTENSIONS)}",
            )
        contents = await file.read()
        if len(contents) > config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {format_file_size(config.MAX_FILE_SIZE)}",
            )
        original_image = Image.open(io.BytesIO(contents))
        original_info = get_image_info(original_image)
        original_size = len(contents)
        processed_image = original_image.copy()
        if remove_bg:
            processed_image = remove_background(
                processed_image,
                engine=bg_engine,
                model=bg_model if bg_engine == "rembg" else None,
                upscale=upscale,
                upscale_factor=upscale_factor,
                refine_alpha=refine_alpha,
                alpha_algorithm=alpha_algorithm,
            )
        output_formats = [f.strip() for f in formats.split(',') if f.strip()]
        output_sizes = [int(s.strip()) for s in sizes.split(',') if s.strip()]
        for fmt in output_formats:
            if fmt not in config.OUTPUT_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid format: {fmt}. Allowed: {', '.join(config.OUTPUT_FORMATS)}",
                )
        processed_files = []
        for fmt in output_formats:
            for size in output_sizes:
                resized = resize_to_width(processed_image, size)
                if optimize:
                    resized = optimize_image(
                        resized,
                        format=fmt,
                        quality=quality,
                        remove_exif=config.REMOVE_EXIF,
                        enhance=True,
                    )
                safe_filename = sanitize_filename(file.filename)
                stem = Path(safe_filename).stem
                output_filename = f"{stem}_{size}.{fmt}"
                output_path = config.OUTPUT_DIR / output_filename
                file_size = save_optimized(
                    resized,
                    output_path,
                    format=fmt,
                    quality=quality,
                    remove_exif=config.REMOVE_EXIF,
                )
                reduction = get_file_size_reduction(original_size, file_size)
                processed_files.append({
                    "format": fmt,
                    "size": str(size),
                    "url": f"/outputs/{output_filename}",
                    "filename": output_filename,
                    "filesize": format_file_size(file_size),
                    "filesize_bytes": file_size,
                    "reduction": f"{reduction:.1f}%",
                })
        placeholder = None
        if generate_placeholder:
            placeholder = generate_placeholder_blur(
                processed_image,
                size=config.PLACEHOLDER_SIZE,
            )
        end_time = time.time()
        processing_time = calculate_processing_time(start_time, end_time)
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
                "upscale": upscale,
                "upscale_factor": upscale_factor,
                "refine_alpha": refine_alpha,
                "alpha_algorithm": alpha_algorithm,
            },
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
        reload=config.RELOAD,
    )
