#!/usr/bin/env python3
"""
ComfyUI Parser Plugin
Parser for ComfyUI workflow metadata
"""

from __future__ import annotations
import json
import os
from typing import Dict, Any, Optional

def detect(metadata: Dict[str, Any]) -> bool:
    """Detect if metadata is from ComfyUI"""
    # Check for ComfyUI-specific fields
    return any(key in metadata for key in [
        'workflow', 'ComfyUI', 'comfyui', 'workflow_data'
    ])

def parse(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Parse ComfyUI metadata"""
    result = {}
    
    # Extract workflow data
    workflow_data = _extract_workflow_data(metadata)
    result.update(workflow_data)
    
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

def _extract_workflow_data(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Extract workflow data"""
    result = {}
    
    # Look for workflow in various possible locations
    workflow_keys = ['workflow', 'ComfyUI', 'comfyui', 'workflow_data']
    
    for key in workflow_keys:
        if key in metadata:
            workflow = metadata[key]
            if isinstance(workflow, str):
                try:
                    workflow_data = json.loads(workflow)
                    result['workflow_data'] = workflow_data
                    break
                except json.JSONDecodeError:
                    continue
            elif isinstance(workflow, dict):
                result['workflow_data'] = workflow
                break
    
    return result

def _extract_generation_parameters(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Extract generation parameters from ComfyUI metadata"""
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
    
    # Base model
    if 'base_model' in metadata:
        result['base_model'] = metadata['base_model']
    
    # Method/Pipeline
    if 'method' in metadata:
        result['method'] = metadata['method']
    elif 'pipeline' in metadata:
        result['method'] = metadata['pipeline']
    
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

def _extract_from_workflow_nodes(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract parameters from workflow nodes"""
    result = {}
    
    if not isinstance(workflow_data, dict) or 'nodes' not in workflow_data:
        return result
    
    nodes = workflow_data['nodes']
    
    for node in nodes:
        if not isinstance(node, dict):
            continue
        
        node_type = node.get('type', '')
        node_data = node.get('data', {})
        
        # KSampler node
        if 'KSampler' in node_type:
            if 'steps' in node_data:
                result['steps'] = int(node_data['steps'])
            if 'cfg' in node_data:
                result['cfg'] = float(node_data['cfg'])
            if 'seed' in node_data:
                result['seed'] = int(node_data['seed'])
            if 'sampler_name' in node_data:
                result['sampler'] = node_data['sampler_name']
            if 'scheduler' in node_data:
                result['scheduler'] = node_data['scheduler']
        
        # CheckpointLoaderSimple node
        elif 'CheckpointLoaderSimple' in node_type:
            if 'ckpt_name' in node_data:
                result['model'] = node_data['ckpt_name']
        
        # CLIPTextEncode nodes
        elif 'CLIPTextEncode' in node_type:
            if 'text' in node_data:
                text = node_data['text']
                # Try to determine if it's positive or negative prompt
                if 'negative' in node_type.lower() or 'neg' in node_type.lower():
                    result['negative_prompt'] = text
                else:
                    result['prompt'] = text
    
    return result
