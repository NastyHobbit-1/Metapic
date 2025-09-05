from utils.parser_plugin_interface import ParserPluginInterface
import json
import re
from typing import Dict, Any

class ComfyUIParser(ParserPluginInterface):
    """ComfyUI parser with comprehensive workflow and metadata extraction"""

    @staticmethod
    def detect(metadata: Dict[str, Any]) -> bool:
        # Check for ComfyUI workflow in various fields
        workflow_fields = ['workflow', 'prompt', 'ComfyUI', 'comfyui']
        
        for field in workflow_fields:
            if field in metadata:
                value = metadata[field]
                if isinstance(value, (str, dict)):
                    if isinstance(value, str):
                        try:
                            parsed = json.loads(value)
                            if isinstance(parsed, dict) and any(key in parsed for key in ['nodes', 'workflow', 'extra_data']):
                                return True
                        except:
                            pass
                    elif isinstance(value, dict):
                        if any(key in value for key in ['nodes', 'workflow', 'extra_data']):
                            return True
        
        # Check for ComfyUI-style parameters string
        params = metadata.get('parameters') or metadata.get('Parameters') or ""
        if isinstance(params, str) and ('comfyui' in params.lower() or 'workflow' in params.lower()):
            return True
            
        return False

    @staticmethod
    def parse(metadata: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        
        # Try to find workflow data
        workflow_data = None
        for field in ['workflow', 'prompt', 'ComfyUI', 'comfyui']:
            if field in metadata:
                value = metadata[field]
                if isinstance(value, str):
                    try:
                        workflow_data = json.loads(value)
                        break
                    except:
                        continue
                elif isinstance(value, dict):
                    workflow_data = value
                    break
        
        if workflow_data:
            # Extract nodes information
            nodes = workflow_data.get('nodes', {})
            if isinstance(nodes, dict):
                # Look for common node types and extract their parameters
                for node_id, node_data in nodes.items():
                    if isinstance(node_data, dict):
                        class_type = node_data.get('class_type', '')
                        inputs = node_data.get('inputs', {})
                        
                        # Checkpoint/model loader
                        if 'CheckpointLoader' in class_type or 'ModelLoader' in class_type:
                            if 'ckpt_name' in inputs:
                                result['model_name'] = inputs['ckpt_name']
                        
                        # KSampler nodes
                        elif 'KSampler' in class_type or 'sampler' in class_type.lower():
                            if 'seed' in inputs:
                                result['seed'] = inputs['seed']
                            if 'steps' in inputs:
                                result['steps'] = inputs['steps']
                            if 'cfg' in inputs:
                                result['cfg_scale'] = inputs['cfg']
                            if 'sampler_name' in inputs:
                                result['sampler'] = inputs['sampler_name']
                            if 'scheduler' in inputs:
                                result['scheduler'] = inputs['scheduler']
                            if 'denoise' in inputs:
                                result['denoising_strength'] = inputs['denoise']
                        
                        # Text encode nodes (prompts)
                        elif 'CLIPTextEncode' in class_type or 'TextEncode' in class_type:
                            if 'text' in inputs:
                                text = inputs['text']
                                # Try to determine if this is positive or negative
                                # This is a heuristic - ComfyUI doesn't inherently label positive/negative
                                if not result.get('positive_prompt'):
                                    result['positive_prompt'] = text
                                elif text != result.get('positive_prompt'):
                                    result['negative_prompt'] = text
                        
                        # Image size nodes
                        elif 'EmptyLatentImage' in class_type or 'LatentUpscale' in class_type:
                            if 'width' in inputs:
                                result['width'] = inputs['width']
                            if 'height' in inputs:
                                result['height'] = inputs['height']
                        
                        # VAE nodes
                        elif 'VAE' in class_type:
                            if 'vae_name' in inputs:
                                result['vae'] = inputs['vae_name']
                        
                        # ControlNet nodes
                        elif 'ControlNet' in class_type:
                            if 'control_net_name' in inputs:
                                result['controlnet'] = inputs['control_net_name']
                            if 'strength' in inputs:
                                result['controlnet_strength'] = inputs['strength']
                        
                        # LoRA nodes
                        elif 'LoRA' in class_type:
                            if 'lora_name' in inputs:
                                loras = result.get('loras', [])
                                lora_info = {'name': inputs['lora_name']}
                                if 'strength_model' in inputs:
                                    lora_info['strength_model'] = inputs['strength_model']
                                if 'strength_clip' in inputs:
                                    lora_info['strength_clip'] = inputs['strength_clip']
                                loras.append(lora_info)
                                result['loras'] = loras
            
            # Extract extra data
            extra_data = workflow_data.get('extra_data', {})
            if isinstance(extra_data, dict):
                if 'ds' in extra_data:
                    result['extra_data'] = extra_data['ds']
        
        # Also try to parse parameters string if present
        params = metadata.get('parameters') or metadata.get('Parameters') or ""
        if isinstance(params, str) and params:
            # Look for key-value pairs
            param_patterns = {
                'model': r'Model[:=]?\s*([^,\n]+)',
                'seed': r'Seed[:=]?\s*([0-9-]+)',
                'steps': r'Steps[:=]?\s*([0-9]+)',
                'cfg': r'CFG[:=]?\s*([0-9.]+)',
                'sampler': r'Sampler[:=]?\s*([^,\n]+)',
                'scheduler': r'Scheduler[:=]?\s*([^,\n]+)',
                'size': r'Size[:=]?\s*([0-9]+x[0-9]+)',
                'width': r'Width[:=]?\s*([0-9]+)',
                'height': r'Height[:=]?\s*([0-9]+)',
            }
            
            for field, pattern in param_patterns.items():
                if field not in result:  # Don't override workflow data
                    match = re.search(pattern, params, re.IGNORECASE)
                    if match:
                        value = match.group(1).strip()
                        if field in ['seed', 'steps']:
                            try:
                                result[field] = int(value)
                            except:
                                result[field] = value
                        elif field == 'cfg':
                            try:
                                result['cfg_scale'] = float(value)
                            except:
                                result['cfg_scale'] = value
                        elif field == 'size':
                            result[field] = value
                            try:
                                w, h = value.split('x')
                                if 'width' not in result:
                                    result['width'] = int(w)
                                if 'height' not in result:
                                    result['height'] = int(h)
                            except:
                                pass
                        elif field in ['width', 'height']:
                            try:
                                result[field] = int(value)
                            except:
                                result[field] = value
                        else:
                            result[field] = value
        
        # Set source
        result['source'] = 'ComfyUI'
        
        return result
