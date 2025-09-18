#!/usr/bin/env python3
"""
MetaPic Data Models - Pydantic v2 Models for Type-Safe Metadata

This module defines the core data models used throughout MetaPic Enhanced.
All models use Pydantic v2 for automatic validation, serialization, and
type safety. The ImageMeta model is the central data structure that
represents AI-generated image metadata.

Key Features:
- Type-safe field definitions with validation
- Automatic serialization/deserialization
- Rich metadata support for all AI platforms
- Computed properties for common operations

Author: MetaPic Enhanced Team
Version: 2.0
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from pathlib import Path

class ImageMeta(BaseModel):
    """
    Comprehensive metadata model for AI-generated images.
    
    This model represents all metadata that can be extracted from AI-generated
    images, including technical parameters, prompts, model information, and
    raw data. It supports all major AI platforms (A1111, ComfyUI, NovelAI, etc.)
    and provides type-safe access to all fields.
    
    Attributes:
        path: File path to the image
        width: Image width in pixels
        height: Image height in pixels
        format: Image format (PNG, JPEG, WebP, etc.)
        size_bytes: File size in bytes
        
        # AI Generation Parameters
        model: Primary AI model name
        base_model: Base model (e.g., Stable Diffusion 1.5)
        sampler: Sampling method (Euler a, DPM++, etc.)
        scheduler: Scheduler algorithm
        steps: Number of generation steps
        cfg: CFG scale value
        seed: Random seed used for generation
        prompt: Positive prompt text
        negative_prompt: Negative prompt text
        method: Generation method/pipeline
        
        # Raw Data Storage
        metadata_raw: Raw EXIF/metadata from exiftool
        parsed_raw: Parsed metadata from AI-specific parsers
        
    Examples:
        >>> meta = ImageMeta(
        ...     path="image.png",
        ...     model="stable-diffusion-v1-5",
        ...     steps=20,
        ...     cfg=7.5,
        ...     seed=12345
        ... )
        >>> print(meta.title_hint())
        stable-diffusion-v1-5-s20-cfg7.5-seed12345
    """
    path: str
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    size_bytes: Optional[int] = None

    # Core AI fields
    model: Optional[str] = None
    base_model: Optional[str] = None
    sampler: Optional[str] = None
    scheduler: Optional[str] = None
    steps: Optional[int] = None
    cfg: Optional[float] = Field(default=None, alias="cfg_scale")
    seed: Optional[int] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    method: Optional[str] = None  # e.g., "StableDiffusion", "SDXL", "Flux"

    # Raw blobs
    metadata_raw: Dict[str, Any] = Field(default_factory=dict)
    parsed_raw: Dict[str, Any] = Field(default_factory=dict)

    def title_hint(self) -> str:
        """
        Generate a descriptive title hint from metadata.
        
        This method creates a human-readable title by combining key metadata
        fields like model, steps, CFG scale, and seed. It's used for file
        naming and display purposes.
        
        Returns:
            A descriptive title string combining relevant metadata fields.
            
        Examples:
            >>> meta = ImageMeta(path="test.png", model="sd-v1-5", steps=20, cfg=7.5, seed=123)
            >>> meta.title_hint()
            "sd-v1-5-s20-cfg7.5-seed123"
            
            >>> meta = ImageMeta(path="test.png", model=None, steps=None)
            >>> meta.title_hint()
            "test"  # Falls back to filename stem
        """
        parts = []
        base = self.model or self.base_model or self.method
        if base:
            parts.append(str(base))
        if self.steps is not None:
            parts.append(f"s{self.steps}")
        if self.cfg is not None:
            # trim trailing .0 to keep names clean
            cfg_str = f"{self.cfg}".rstrip("0").rstrip(".")
            parts.append(f"cfg{cfg_str}")
        if self.seed is not None:
            parts.append(f"seed{self.seed}")

        if not parts:
            # fallback to file stem if we have no parsed fields
            try:
                parts.append(Path(self.path).stem)
            except Exception:
                parts.append("image")

        return "-".join(parts)
