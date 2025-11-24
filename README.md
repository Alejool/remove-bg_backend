# 🖼️ Image Manager - Professional Image Processor

A complete full-stack application for processing, optimizing, and transforming images with a modern web interface and REST API.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![Astro](https://img.shields.io/badge/Astro-4.x-orange.svg)
![React](https://img.shields.io/badge/React-18-blue.svg)
![Tailwind](https://img.shields.io/badge/Tailwind-3.x-cyan.svg)

## ✨ Features

### 🎨 Image Processing Capabilities

- **AI-Powered Background Removal** - Remove backgrounds with precision using rembg and u2net model
- **Smart Resizing** - Intelligent resizing with multiple modes (contain, cover, fill)
- **Format Conversion** - Convert to WebP, AVIF, PNG, and JPEG
- **Image Optimization** - Reduce file sizes by up to 80% without quality loss
- **Batch Processing** - Generate multiple size variants in one operation
- **Blur Placeholders** - Create tiny blurred placeholders for progressive loading
- **EXIF Removal** - Strip metadata for privacy and smaller file sizes
- **Quality Enhancement** - Apply sharpening and contrast adjustments

### 🚀 Technology Stack

**Backend:**
- Python 3.11+
- FastAPI - Modern, fast web framework
- Pillow (PIL) - Image processing library
- rembg - AI background removal
- Uvicorn - ASGI server

**Frontend:**
- Astro 4.x - Modern web framework
- React 18 - UI components
- TypeScript - Type safety
- Tailwind CSS 3 - Utility-first styling
- Lucide Icons - Beautiful icons
- Axios - HTTP client

---

## 📦 Installation

### Prerequisites

Ensure you have the following installed:

```bash
# Python 3.11 or higher
python --version

# Node.js 18 or higher
node --version

# pip (Python package manager)
pip --version

# npm or pnpm
npm --version
```

### 1️⃣ Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Note:** The first time you run background removal, rembg will automatically download the u2net model (~176MB). This is a one-time download.

### 2️⃣ Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Or with pnpm
pnpm install
```

---

## 🚀 Running the Application

### Start Backend Server

```bash
cd backend
python app.py
```

The API will be available at: **http://localhost:8000**

API Documentation (Swagger): **http://localhost:8000/docs**

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The application will be available at: **http://localhost:4321**

---

## 📡 API Documentation

### Endpoints

#### `GET /api/health`

Health check endpoint to verify server status.

**Response:**
```json
{
  "status": "healthy",
  "service": "Image Manager API",
  "version": "1.0.0"
}
```

#### `POST /api/process`

Process an image with specified transformations.

**Parameters (multipart/form-data):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file` | File | Required | Image file to process |
| `remove_bg` | Boolean | `false` | Remove background using AI |
| `formats` | String | `"webp"` | Comma-separated output formats (webp,avif,png,jpeg) |
| `sizes` | String | `"800"` | Comma-separated width sizes in pixels (400,800,1200) |
| `quality` | Integer | `85` | Quality level (1-100) |
| `optimize` | Boolean | `true` | Enable image optimization |
| `generate_placeholder` | Boolean | `true` | Generate blur placeholder |

**Example Request (cURL):**

```bash
curl -X POST "http://localhost:8000/api/process" \
  -F "file=@image.jpg" \
  -F "remove_bg=true" \
  -F "formats=webp,png" \
  -F "sizes=400,800,1200" \
  -F "quality=85" \
  -F "optimize=true" \
  -F "generate_placeholder=true"
```

**Example Response:**

```json
{
  "success": true,
  "original": {
    "filename": "image.jpg",
    "size": "2.4 MB",
    "size_bytes": 2516582,
    "dimensions": "3000x2000",
    "width": 3000,
    "height": 2000
  },
  "processed": [
    {
      "format": "webp",
      "size": "400",
      "url": "/outputs/image_400.webp",
      "filename": "image_400.webp",
      "filesize": "24.3 KB",
      "filesize_bytes": 24883,
      "reduction": "99.0%"
    },
    {
      "format": "webp",
      "size": "800",
      "url": "/outputs/image_800.webp",
      "filename": "image_800.webp",
      "filesize": "68.5 KB",
      "filesize_bytes": 70144,
      "reduction": "97.2%"
    }
  ],
  "placeholder": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "processing_time": "3.2s",
  "options": {
    "background_removed": true,
    "optimized": true,
    "quality": 85,
    "formats": ["webp", "png"],
    "sizes": [400, 800, 1200]
  }
}
```

---

## 🎯 Use Cases

### 1. E-commerce Product Images

- Remove backgrounds from product photos
- Generate multiple sizes for thumbnails, listings, and detail views
- Optimize for fast page loads
- Create WebP/AVIF versions for modern browsers

### 2. Blog & Portfolio

- Optimize images for web without manual work
- Generate responsive image sets automatically
- Reduce bandwidth and improve SEO
- Create blur placeholders for better UX

### 3. Web Development

- Prepare assets before deployment
- Automate image optimization pipeline
- Generate multiple formats for browser compatibility
- Batch process entire image libraries

---

## ⚙️ Configuration

### Backend Configuration

Edit `backend/config.py`:

```python
# File upload settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

# Output format settings
OUTPUT_FORMATS = ['webp', 'avif', 'png', 'jpeg']
DEFAULT_QUALITY = 85
DEFAULT_SIZES = [400, 800, 1200]

# Processing settings
REMOVE_EXIF = True
ENABLE_OPTIMIZATION = True
GENERATE_PLACEHOLDER = True
PLACEHOLDER_SIZE = 20

# Server settings
HOST = "0.0.0.0"
PORT = 8000

# CORS settings
CORS_ORIGINS = [
    "http://localhost:4321",
    "http://localhost:3000",
]
```

### Frontend Configuration

Create `frontend/.env`:

```env
PUBLIC_API_URL=http://localhost:8000
```

---

## 📁 Project Structure

```
image-manager/
├── backend/
│   ├── app.py                      # FastAPI application
│   ├── config.py                   # Configuration settings
│   ├── requirements.txt            # Python dependencies
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── background_remover.py   # AI background removal
│   │   ├── optimizer.py            # Image optimization
│   │   └── resizer.py              # Smart resizing
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py              # Utility functions
│   ├── upload/                     # Temporary uploads
│   └── outputs/                    # Processed images
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ImageUploader.tsx   # Drag & drop upload
│   │   │   ├── ProcessingOptions.tsx  # Options panel
│   │   │   ├── ResultsGallery.tsx  # Results display
│   │   │   └── ImageProcessor.tsx  # Main app component
│   │   ├── layouts/
│   │   │   └── Layout.astro        # Base layout
│   │   ├── pages/
│   │   │   └── index.astro         # Home page
│   │   ├── styles/
│   │   │   └── global.css          # Global styles
│   │   └── env.d.ts                # TypeScript definitions
│   ├── public/
│   ├── astro.config.mjs            # Astro configuration
│   ├── tailwind.config.mjs         # Tailwind configuration
│   ├── tsconfig.json               # TypeScript configuration
│   └── package.json                # Node dependencies
│
├── .gitignore
└── README.md
```

---

## 🐛 Troubleshooting

### Backend Issues

**Error: "rembg model not found"**

The model downloads automatically on first use. If you encounter issues:

```bash
# For GPU support
pip install rembg[gpu]

# For CPU only
pip install rembg[cpu]
```

**Error: "AVIF support not available"**

Install AVIF plugin:

```bash
pip install pillow-avif-plugin
```

**Port already in use:**

Change the port in `config.py` or run with custom port:

```bash
uvicorn app:app --port 8001
```

### Frontend Issues

**Build errors:**

Clear cache and reinstall:

```bash
rm -rf node_modules .astro
npm install
```

**API connection refused:**

1. Verify backend is running on port 8000
2. Check CORS settings in `backend/config.py`
3. Verify `PUBLIC_API_URL` in frontend `.env`

**TypeScript errors:**

Ensure all dependencies are installed:

```bash
npm install -D @types/react @types/react-dom --legacy-peer-deps
```

---

## 🎨 UI Features

The frontend features a modern, premium design with:

- **Glassmorphism** - Frosted glass effect cards
- **Gradient Animations** - Smooth color transitions
- **Drag & Drop** - Intuitive file upload
- **Real-time Preview** - See images before processing
- **Interactive Controls** - Sliders, toggles, and buttons
- **Responsive Design** - Works on mobile, tablet, and desktop
- **Dark Mode** - Beautiful dark theme by default
- **Micro-animations** - Smooth transitions and hover effects

---

## 🔧 Development

### Adding New Image Processors

Create a new processor in `backend/processors/`:

```python
# backend/processors/custom_filter.py
from PIL import Image

def apply_custom_filter(image: Image.Image, **kwargs) -> Image.Image:
    """Apply custom filter to image"""
    # Your processing logic here
    return image
```

Import and use in `app.py`:

```python
from processors.custom_filter import apply_custom_filter

# Use in processing pipeline
processed_image = apply_custom_filter(image, param=value)
```

### Adding New Frontend Components

Create component in `frontend/src/components/`:

```tsx
// frontend/src/components/NewFeature.tsx
import React from 'react';

export default function NewFeature() {
  return (
    <div className="glass p-6">
      {/* Your component */}
    </div>
  );
}
```

---

## 📊 Performance

- **Background Removal**: ~2-5 seconds (depends on image size)
- **Format Conversion**: ~0.5-1 second per variant
- **Optimization**: ~0.3-0.8 seconds per image
- **File Size Reduction**: 50-80% average (with quality 85)

**Optimization Tips:**
- Use WebP/AVIF for best compression
- Quality 80-90 is optimal for most use cases
- Limit size variants to what you actually need
- Consider disabling background removal for batch operations

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - Free to use for personal and commercial projects.

---

## 🙏 Acknowledgments

- [rembg](https://github.com/danielgatis/rembg) - AI background removal
- [Pillow](https://python-pillow.org/) - Python imaging library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Astro](https://astro.build/) - Web framework for content-focused sites
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Lucide](https://lucide.dev/) - Beautiful icon library

---

## 📞 Support

For questions, issues, or feature requests:

- Open an issue on GitHub
- Check existing documentation
- Review the API docs at `/docs`

---

**Built with ❤️ using Python, FastAPI, Astro, React, and Tailwind CSS**

**Enjoy processing images! 🎉**
