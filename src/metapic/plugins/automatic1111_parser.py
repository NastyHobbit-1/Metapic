#!/usr/bin/env python3
"""
Automatic1111 Parser Plugin
Enhanced parser for Automatic1111 (Stable Diffusion WebUI) metadata
"""

from __future__ import annotations
import re
from typing import Dict, Any, Optional

def detect(metadata: Dict[str, Any]) -> bool:
    """Detect if metadata is from Automatic1111"""
    params = metadata.get('parameters') or metadata.get('Parameters') or ""
    return isinstance(params, str) and (
        'Negative prompt:' in params or 
        'Steps:' in params or 
        'Seed:' in params or
        'CFG scale:' in params
    )

def parse(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Automatic1111 metadata"""
    params = metadata.get('parameters') or metadata.get('Parameters') or ""
    
    result = {}
    
    # Extract prompt sections
    prompt_data = _extract_prompt_sections(params)
    result.update(prompt_data)
    
    # Extract technical parameters
    tech_params = _extract_technical_parameters(params)
    result.update(tech_params)
    
    # Extract model information
    model_info = _extract_model_information(params)
    result.update(model_info)
    
    # Extract dimensions
    dimensions = _extract_size_dimensions(params)
    result.update(dimensions)
    
    # Extract ControlNet information
    controlnet_info = _extract_controlnet_info(params)
    result.update(controlnet_info)
    
    # Extract LoRA information
    lora_info = _extract_lora_info(params)
    result.update(lora_info)
    
    # Extract VAE information
    vae_info = _extract_vae_info(params)
    result.update(vae_info)
    
    # Extract other parameters
    other_params = _extract_other_parameters(params)
    result.update(other_params)
    
    return {k: v for k, v in result.items() if v is not None and v != ""}

def _extract_prompt_sections(params: str) -> Dict[str, Any]:
    """Extract positive and negative prompts"""
    result = {}
    
    if 'Negative prompt:' in params:
        parts = params.split('Negative prompt:', 1)
        if len(parts) == 2:
            result['prompt'] = parts[0].strip().strip('\n, ')
            negative_part = parts[1].split('\n')[0].strip().strip(', ')
            result['negative_prompt'] = negative_part
    else:
        # No negative prompt, everything is positive
        result['prompt'] = params.strip()
    
    return result

def _extract_technical_parameters(params: str) -> Dict[str, Any]:
    """Extract technical generation parameters"""
    result = {}
    
    # Steps
    steps_match = re.search(r'Steps:\s*(\d+)', params, re.I)
    if steps_match:
        result['steps'] = int(steps_match.group(1))
    
    # CFG Scale
    cfg_match = re.search(r'CFG\s*scale:\s*([\d.]+)', params, re.I)
    if cfg_match:
        result['cfg'] = float(cfg_match.group(1))
    
    # Seed
    seed_match = re.search(r'Seed:\s*(\d+)', params, re.I)
    if seed_match:
        result['seed'] = int(seed_match.group(1))
    
    # Sampler
    sampler_match = re.search(r'Sampler:\s*([^,\n]+)', params, re.I)
    if sampler_match:
        result['sampler'] = sampler_match.group(1).strip()
    
    # Scheduler
    scheduler_match = re.search(r'Scheduler:\s*([^,\n]+)', params, re.I)
    if scheduler_match:
        result['scheduler'] = scheduler_match.group(1).strip()
    
    return result

def _extract_model_information(params: str) -> Dict[str, Any]:
    """Extract model information"""
    result = {}
    
    # Model name
    model_match = re.search(r'Model:\s*([^,\n]+)', params, re.I)
    if model_match:
        result['model'] = model_match.group(1).strip()
    
    # Base model
    base_model_match = re.search(r'Base\s*model:\s*([^,\n]+)', params, re.I)
    if base_model_match:
        result['base_model'] = base_model_match.group(1).strip()
    
    # Method/Pipeline
    method_match = re.search(r'Method:\s*([^,\n]+)', params, re.I)
    if method_match:
        result['method'] = method_match.group(1).strip()
    
    return result

def _extract_size_dimensions(params: str) -> Dict[str, Any]:
    """Extract image dimensions"""
    result = {}
    
    # Size
    size_match = re.search(r'Size:\s*(\d+)\s*x\s*(\d+)', params, re.I)
    if size_match:
        result['width'] = int(size_match.group(1))
        result['height'] = int(size_match.group(2))
    
    return result

def _extract_controlnet_info(params: str) -> Dict[str, Any]:
    """Extract ControlNet information"""
    result = {}
    
    # ControlNet enabled
    if 'ControlNet' in params:
        result['controlnet_enabled'] = True
        
        # ControlNet model
        cn_model_match = re.search(r'ControlNet\s*model:\s*([^,\n]+)', params, re.I)
        if cn_model_match:
            result['controlnet_model'] = cn_model_match.group(1).strip()
        
        # ControlNet weight
        cn_weight_match = re.search(r'ControlNet\s*weight:\s*([\d.]+)', params, re.I)
        if cn_weight_match:
            result['controlnet_weight'] = float(cn_weight_match.group(1))
    
    return result

def _extract_lora_info(params: str) -> Dict[str, Any]:
    """Extract LoRA information"""
    result = {}
    
    # LoRA models
    lora_matches = re.findall(r'LoRA:\s*([^,\n]+)', params, re.I)
    if lora_matches:
        result['lora_models'] = [lora.strip() for lora in lora_matches]
    
    return result

def _extract_vae_info(params: str) -> Dict[str, Any]:
    """Extract VAE information"""
    result = {}
    
    # VAE
    vae_match = re.search(r'VAE:\s*([^,\n]+)', params, re.I)
    if vae_match:
        result['vae'] = vae_match.group(1).strip()
    
    return result

def _extract_other_parameters(params: str) -> Dict[str, Any]:
    """Extract other miscellaneous parameters"""
    result = {}
    
    # Clip skip
    clip_skip_match = re.search(r'Clip\s*skip:\s*(\d+)', params, re.I)
    if clip_skip_match:
        result['clip_skip'] = int(clip_skip_match.group(1))
    
    # ENSD
    ensd_match = re.search(r'ENSD:\s*([^,\n]+)', params, re.I)
    if ensd_match:
        result['ensd'] = ensd_match.group(1).strip()
    
    # Version
    version_match = re.search(r'Version:\s*([^,\n]+)', params, re.I)
    if version_match:
        result['version'] = version_match.group(1).strip()
    
    return result
