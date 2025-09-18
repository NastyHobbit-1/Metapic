#!/usr/bin/env python3
"""
General AI Parser Plugin
Fallback parser for generic AI metadata formats
"""

from __future__ import annotations
import re
from typing import Dict, Any, Optional

def detect(metadata: Dict[str, Any]) -> bool:
    """Detect if metadata contains general AI parameters"""
    # This is a fallback parser, so it should always return True
    # but only parse if it finds relevant AI parameters
    
    # Check for common AI parameter patterns
    ai_indicators = [
        'prompt', 'negative_prompt', 'steps', 'cfg', 'seed', 'sampler',
        'model', 'width', 'height', 'generation', 'ai', 'stable diffusion'
    ]
    
    metadata_str = str(metadata).lower()
    return any(indicator in metadata_str for indicator in ai_indicators)

def parse(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Parse general AI metadata"""
    result = {}
    
    # Extract basic parameters
    basic_params = _extract_basic_parameters(metadata)
    result.update(basic_params)
    
    # Extract prompt information
    prompt_info = _extract_prompt_info(metadata)
    result.update(prompt_info)
    
    # Extract model information
    model_info = _extract_model_info(metadata)
    result.update(model_info)
    
    # Extract dimensions
    dimensions = _extract_dimensions(metadata)
    result.update(dimensions)
    
    # Extract technical parameters
    tech_params = _extract_technical_parameters(metadata)
    result.update(tech_params)
    
    return {k: v for k, v in result.items() if v is not None and v != ""}

def _extract_basic_parameters(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Extract basic AI parameters"""
    result = {}
    
    # Steps
    if 'steps' in metadata:
        try:
            result['steps'] = int(metadata['steps'])
        except (ValueError, TypeError):
            pass
    
    # CFG Scale
    if 'cfg' in metadata:
        try:
            result['cfg'] = float(metadata['cfg'])
        except (ValueError, TypeError):
            pass
    elif 'cfg_scale' in metadata:
        try:
            result['cfg'] = float(metadata['cfg_scale'])
        except (ValueError, TypeError):
            pass
    
    # Seed
    if 'seed' in metadata:
        try:
            result['seed'] = int(metadata['seed'])
        except (ValueError, TypeError):
            pass
    
    return result

def _extract_prompt_info(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Extract prompt information"""
    result = {}
    
    # Positive prompt
    prompt_keys = ['prompt', 'positive_prompt', 'text', 'description']
    for key in prompt_keys:
        if key in metadata and metadata[key]:
            result['prompt'] = str(metadata[key])
            break
    
    # Negative prompt
    negative_keys = ['negative_prompt', 'negative', 'unwanted']
    for key in negative_keys:
        if key in metadata and metadata[key]:
            result['negative_prompt'] = str(metadata[key])
            break
    
    return result

def _extract_model_info(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Extract model information"""
    result = {}
    
    # Model name
    model_keys = ['model', 'model_name', 'checkpoint', 'ckpt']
    for key in model_keys:
        if key in metadata and metadata[key]:
            result['model'] = str(metadata[key])
            break
    
    # Base model
    base_model_keys = ['base_model', 'base', 'foundation_model']
    for key in base_model_keys:
        if key in metadata and metadata[key]:
            result['base_model'] = str(metadata[key])
            break
    
    # Method/Pipeline
    method_keys = ['method', 'pipeline', 'engine', 'generator']
    for key in method_keys:
        if key in metadata and metadata[key]:
            result['method'] = str(metadata[key])
            break
    
    return result

def _extract_dimensions(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Extract image dimensions"""
    result = {}
    
    # Width
    width_keys = ['width', 'w', 'image_width']
    for key in width_keys:
        if key in metadata and metadata[key]:
            try:
                result['width'] = int(metadata[key])
                break
            except (ValueError, TypeError):
                continue
    
    # Height
    height_keys = ['height', 'h', 'image_height']
    for key in height_keys:
        if key in metadata and metadata[key]:
            try:
                result['height'] = int(metadata[key])
                break
            except (ValueError, TypeError):
                continue
    
    # Size string (e.g., "512x512")
    size_keys = ['size', 'dimensions', 'resolution']
    for key in size_keys:
        if key in metadata and metadata[key]:
            size_str = str(metadata[key])
            size_match = re.search(r'(\d+)\s*[x×]\s*(\d+)', size_str)
            if size_match:
                result['width'] = int(size_match.group(1))
                result['height'] = int(size_match.group(2))
                break
    
    return result

def _extract_technical_parameters(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Extract technical parameters"""
    result = {}
    
    # Sampler
    sampler_keys = ['sampler', 'sampling_method', 'scheduler']
    for key in sampler_keys:
        if key in metadata and metadata[key]:
            result['sampler'] = str(metadata[key])
            break
    
    # Scheduler
    scheduler_keys = ['scheduler', 'scheduling']
    for key in scheduler_keys:
        if key in metadata and metadata[key]:
            result['scheduler'] = str(metadata[key])
            break
    
    # Format
    format_keys = ['format', 'file_format', 'image_format']
    for key in format_keys:
        if key in metadata and metadata[key]:
            result['format'] = str(metadata[key])
            break
    
    return result

def _extract_from_text(text: str) -> Dict[str, Any]:
    """Extract parameters from text using regex patterns"""
    result = {}
    
    if not text:
        return result
    
    # Steps pattern
    steps_match = re.search(r'steps?\s*[:=]\s*(\d+)', text, re.I)
    if steps_match:
        result['steps'] = int(steps_match.group(1))
    
    # CFG pattern
    cfg_match = re.search(r'cfg\s*(?:scale)?\s*[:=]\s*([\d.]+)', text, re.I)
    if cfg_match:
        result['cfg'] = float(cfg_match.group(1))
    
    # Seed pattern
    seed_match = re.search(r'seed\s*[:=]\s*(\d+)', text, re.I)
    if seed_match:
        result['seed'] = int(seed_match.group(1))
    
    # Sampler pattern
    sampler_match = re.search(r'sampler\s*[:=]\s*([^,\n]+)', text, re.I)
    if sampler_match:
        result['sampler'] = sampler_match.group(1).strip()
    
    # Model pattern
    model_match = re.search(r'model\s*[:=]\s*([^,\n]+)', text, re.I)
    if model_match:
        result['model'] = model_match.group(1).strip()
    
    return result
