import os
import subprocess
import tempfile
from typing import Dict, Any
from PIL import Image
import piexif

def extract_png_text_chunks(image_path: str) -> Dict[str, str]:
    try:
        img = Image.open(image_path)
        meta = img.info
        text_chunks = {}
        for k, v in meta.items():
            text_chunks[k.lower()] = v
        return text_chunks
    except Exception:
        return {}

def extract_exif_ai_metadata(image_path: str) -> Dict[str, str]:
    try:
        exif_dict = piexif.load(image_path)
    except Exception:
        return {}

    ai_metadata = {}
    for ifd_name in ("0th", "Exif", "GPS", "1st"):
        if ifd_name not in exif_dict:
            continue
        for tag, value in exif_dict[ifd_name].items():
            tag_name = piexif.TAGS[ifd_name].get(tag, {}).get("name", f"UnknownTag{tag}")
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8', errors='ignore').strip('\x00')
                except Exception:
                    value = value.decode('latin1', errors='ignore').strip('\x00')
            if tag_name in ('UserComment', 'ImageDescription', 'XPComment'):
                ai_metadata[tag_name] = value
    return ai_metadata

def extract_tiff_metadata(image_path: str) -> Dict[str, Any]:
    try:
        img = Image.open(image_path)
        tags = img.tag_v2
        metadata = {str(tag): str(tags[tag]) for tag in tags}
        return metadata
    except Exception:
        return {}

def extract_webp_metadata_with_webpmux(image_path: str, webpmux_path: str = None) -> Dict[str, bytes]:
    metadata = {}
    
    # Find webpmux binary if path not provided
    if webpmux_path is None:
        webpmux_paths = [
            "webpmux.exe",
            "webpmux",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "webpmux.exe")
        ]
        
        webpmux_path = None
        for path in webpmux_paths:
            if os.path.isfile(path) or __import__('shutil').which(path):
                webpmux_path = path
                break
        
        if webpmux_path is None:
            print("webpmux binary not found, skipping WebP metadata extraction.")
            return metadata
    elif not os.path.isfile(webpmux_path):
        print(f"webpmux binary not found at {webpmux_path}, skipping WebP metadata extraction.")
        return metadata
    temp_dir = tempfile.mkdtemp()
    try:
        for chunk in ['exif', 'iccp', 'xmp']:
            out_path = os.path.join(temp_dir, f"{chunk}.bin")
            result = subprocess.run([webpmux_path, '-get', chunk, image_path, '-o', out_path], capture_output=True)
            if result.returncode == 0 and os.path.getsize(out_path) > 0:
                with open(out_path, 'rb') as f:
                    metadata[chunk] = f.read()
    except Exception:
        pass
    finally:
        import shutil
        shutil.rmtree(temp_dir)
    return metadata

def extract_metadata(image_path: str, webpmux_path: str = None) -> Dict[str, Any]:
    ext = os.path.splitext(image_path)[1].lower()
    if ext == '.png':
        return extract_png_text_chunks(image_path)
    elif ext in ['.jpg', '.jpeg']:
        return extract_exif_ai_metadata(image_path)
    elif ext == '.tiff' or ext == '.tif':
        return extract_tiff_metadata(image_path)
    elif ext == '.webp':
        return extract_webp_metadata_with_webpmux(image_path, webpmux_path)
    else:
        return {}

