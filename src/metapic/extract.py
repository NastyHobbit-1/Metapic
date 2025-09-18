#!/usr/bin/env python3
"""
MetaPic Metadata Extraction - exiftool Integration

This module provides the core metadata extraction functionality using exiftool.
It handles batch processing of images and returns structured metadata that
can be further processed by AI-specific parsers.

Key Features:
- Batch processing for efficiency
- Error handling and validation
- JSON output format for easy parsing
- Support for all major image formats

Dependencies:
- exiftool: External tool for metadata extraction
- subprocess: For running exiftool commands

Author: MetaPic Enhanced Team
Version: 2.0
"""

from __future__ import annotations
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Iterable

# exiftool command name (should be in PATH)
EXIFTOOL = "exiftool"

def exiftool_batch(paths: Iterable[Path]) -> Dict[str, Dict[str, Any]]:
    """
    Extract metadata from multiple images using exiftool.
    
    This function runs exiftool in batch mode to extract metadata from
    multiple images efficiently. It requests specific tags that are
    commonly used in AI image metadata.
    
    Args:
        paths: Iterable of Path objects pointing to image files
        
    Returns:
        Dictionary mapping file paths to their metadata dictionaries.
        Each metadata dictionary contains all EXIF tags and values.
        
    Raises:
        RuntimeError: If exiftool command fails or returns invalid JSON
        
    Examples:
        >>> from pathlib import Path
        >>> paths = [Path("image1.png"), Path("image2.jpg")]
        >>> metadata = exiftool_batch(paths)
        >>> print(metadata["image1.png"]["ImageWidth"])
        512
        
    Note:
        Requires exiftool to be installed and available in PATH.
        The function requests these specific tags:
        - FileSize#: Numeric file size in bytes
        - ImageWidth: Image width in pixels
        - ImageHeight: Image height in pixels
        - MIMEType: MIME type of the file
    """
    paths = [str(Path(p)) for p in paths]
    if not paths:
        return {}

    # Request numeric size and a few common tags up-front
    cmd = [
        EXIFTOOL, "-json",
        "-FileSize#", "-ImageWidth", "-ImageHeight", "-MIMEType",
    ] + paths

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"exiftool failed: {proc.stderr[:200]}")

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid exiftool JSON: {e}")

    result: Dict[str, Dict[str, Any]] = {}
    for item in data:
        src = item.get("SourceFile")
        if src:
            result[src] = item
    return result
