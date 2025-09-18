#!/usr/bin/env python3
"""
NovelAI Parser Plugin
Parser for NovelAI-specific metadata
"""

from __future__ import annotations
import json
from typing import Dict, Any, Optional

def detect(metadata: Dict[str, Any]) -> bool:
    """Detect if metadata is from NovelAI"""
    # Check for NovelAI-specific fields
    return any(key in metadata for key in [
        'NovelAI', 'novelai', 'nai', 'quality', 'style'
    ])

def parse(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Parse NovelAI metadata"""
    result = {}
    
    # Extract NovelAI-specific parameters
    novelai_params = _extract_novelai_parameters(metadata)
    result.update(novelai_params)
    
    # Extract generation parameters
    gen_params = _extract_generation_parameters(metadata)
    result.update(gen_params)
    
    # Extract model information
    model_info = _extract_model_info(metadata)
    result.update(model_info)
    
    # Extract prompt information
    prompt_info = _extract_prompt_info(metadata)
    result.update(prompt_info)
    
    return {k: v for k, v in result.items() if v is not None and v != ""}

def _extract_novelai_parameters(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Extract NovelAI-specific parameters"""
    result = {}
    
    # Quality tags
    if 'quality' in metadata:
        result['quality'] = metadata['quality']
    
    # Style tags
    if 'style' in metadata:
        result['style'] = metadata['style']
    
    # Artist tags
    if 'artist' in metadata:
        result['artist'] = metadata['artist']
    
    # Subscription tier
    if 'tier' in metadata:
        result['tier'] = metadata['tier']
    elif 'subscription' in metadata:
        result['tier'] = metadata['subscription']
    
    # NovelAI version
    if 'version' in metadata:
        result['version'] = metadata['version']
    elif 'nai_version' in metadata:
        result['version'] = metadata['nai_version']
    
    return result

def _extract_generation_parameters(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Extract generation parameters"""
    result = {}
    
    # Steps
    if 'steps' in metadata:
        result['steps'] = int(metadata['steps'])
    
    # CFG Scale
    if 'cfg' in metadata:
        result['cfg'] = float(metadata['cfg'])
    elif 'cfg_scale' in metadata:
        result['cfg'] = float(metadata['cfg_scale'])
    
    # Seed
    if 'seed' in metadata:
        result['seed'] = int(metadata['seed'])
    
    # Sampler
    if 'sampler' in metadata:
        result['sampler'] = metadata['sampler']
    
    # Scheduler
    if 'scheduler' in metadata:
        result['scheduler'] = metadata['scheduler']
    
    return result

def _extract_model_info(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Extract model information"""
    result = {}
    
    # Model name
    if 'model' in metadata:
        result['model'] = metadata['model']
    elif 'nai_model' in metadata:
        result['model'] = metadata['nai_model']
    
    # Base model
    if 'base_model' in metadata:
        result['base_model'] = metadata['base_model']
    
    # Method/Pipeline
    if 'method' in metadata:
        result['method'] = metadata['method']
    elif 'pipeline' in metadata:
        result['method'] = metadata['pipeline']
    else:
        result['method'] = 'NovelAI'
    
    return result

def _extract_prompt_info(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Extract prompt information"""
    result = {}
    
    # Positive prompt
    if 'prompt' in metadata:
        result['prompt'] = metadata['prompt']
    elif 'positive_prompt' in metadata:
        result['prompt'] = metadata['positive_prompt']
    
    # Negative prompt
    if 'negative_prompt' in metadata:
        result['negative_prompt'] = metadata['negative_prompt']
    
    return result

def _extract_quality_tags(prompt: str) -> Dict[str, Any]:
    """Extract quality tags from NovelAI prompt"""
    result = {}
    
    if not prompt:
        return result
    
    # Common NovelAI quality tags
    quality_tags = [
        'masterpiece', 'best quality', 'high quality', 'ultra detailed',
        'detailed', '1girl', '1boy', '2girls', '2boys', 'multiple girls',
        'solo', 'portrait', 'full body', 'close-up', 'wide shot'
    ]
    
    found_quality = []
    prompt_lower = prompt.lower()
    
    for tag in quality_tags:
        if tag in prompt_lower:
            found_quality.append(tag)
    
    if found_quality:
        result['quality_tags'] = found_quality
    
    return result

def _extract_style_tags(prompt: str) -> Dict[str, Any]:
    """Extract style tags from NovelAI prompt"""
    result = {}
    
    if not prompt:
        return result
    
    # Common NovelAI style tags
    style_tags = [
        'anime', 'manga', 'realistic', 'photorealistic', 'oil painting',
        'watercolor', 'sketch', 'digital art', 'concept art', 'fantasy art',
        'sci-fi', 'cyberpunk', 'steampunk', 'vintage', 'retro'
    ]
    
    found_styles = []
    prompt_lower = prompt.lower()
    
    for tag in style_tags:
        if tag in prompt_lower:
            found_styles.append(tag)
    
    if found_styles:
        result['style_tags'] = found_styles
    
    return result
