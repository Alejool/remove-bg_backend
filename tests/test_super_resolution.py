import io
from fastapi.testclient import TestClient
from pathlib import Path
from PIL import Image

from backend.app import app

client = TestClient(app)

def create_test_image(color=(255, 0, 0), size=(100, 100), format="PNG"):
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    return buf


def test_process_image_with_upscale():
    # Create a simple red square image
    img_bytes = create_test_image()
    files = {"file": ("test.png", img_bytes, "image/png")}
    data = {
        "remove_bg": "false",
        "bg_engine": "auto",
        "bg_model": "u2net",
        "formats": "webp",
        "sizes": "100",
        "quality": "95",
        "optimize": "true",
        "generate_placeholder": "true",
        "upscale": "true",
        "upscale_factor": "2",
    }
    response = client.post("/api/process", files=files, data=data)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["success"] is True
    # Verify options reflect upscale parameters
    assert json_resp["options"]["upscale"] is True
    assert json_resp["options"]["upscale_factor"] == 2
    # Ensure at least one processed file is returned
    assert len(json_resp["processed"]) > 0
