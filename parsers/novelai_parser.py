from utils.parser_plugin_interface import ParserPluginInterface
import json
import base64
import re
from typing import Dict, Any

class NovelAIParser(ParserPluginInterface):
    """NovelAI parser with comprehensive metadata extraction including base64 encoded data"""

    @staticmethod
    def detect(metadata: Dict[str, Any]) -> bool:
        # Check for NovelAI specific fields
        novelai_indicators = [
            'Comment', 'comment',  # NovelAI often uses PNG comment field
            'Software', 'software',
            'Title', 'title'
        ]
        
        for field in novelai_indicators:
            if field in metadata:
                value = str(metadata[field]).lower()
                if 'novelai' in value or 'nai' in value:
                    return True
        
        # Check parameters string
        params = metadata.get('parameters') or metadata.get('Parameters') or ""
        if isinstance(params, str):
            if 'novelai' in params.lower() or 'nai diffusion' in params.lower():
                return True
        
        # Check for NovelAI-style base64 encoded data in comment
        comment = metadata.get('Comment') or metadata.get('comment') or ""
        if isinstance(comment, str) and comment:
            try:
                # Try to decode as base64 and parse as JSON
                decoded = base64.b64decode(comment)
                data = json.loads(decoded.decode('utf-8'))
                if isinstance(data, dict) and ('steps' in data or 'scale' in data or 'sampler' in data):
                    return True
            except:
                pass
        
        return False

    @staticmethod
    def parse(metadata: Dict[str, Any]) -> Dict[str, Any]:
        result = {'source': 'NovelAI'}
        
        # First, try to parse base64 encoded JSON from comment
        comment = metadata.get('Comment') or metadata.get('comment') or ""
        if isinstance(comment, str) and comment:
            try:
                decoded = base64.b64decode(comment)
                data = json.loads(decoded.decode('utf-8'))
                if isinstance(data, dict):
                    # Map NovelAI fields to standard names
                    field_mappings = {
                        'steps': 'steps',
                        'scale': 'cfg_scale',
                        'sampler': 'sampler',
                        'seed': 'seed',
                        'strength': 'denoising_strength',
                        'noise': 'noise_schedule',
                        'sm': 'sm',
                        'sm_dyn': 'sm_dyn',
                        'width': 'width',
                        'height': 'height',
                        'uc': 'negative_prompt',
                        'request_type': 'request_type',
                        'signed_hash': 'signed_hash'
                    }
                    
                    for nai_field, std_field in field_mappings.items():
                        if nai_field in data:
                            result[std_field] = data[nai_field]
                    
                    # Handle prompt - might be in root or nested
                    if 'input' in data:
                        result['positive_prompt'] = data['input']
                    elif 'prompt' in data:
                        result['positive_prompt'] = data['prompt']
                    
                    # Handle model information
                    if 'model' in data:
                        result['model_name'] = data['model']
                    
                    # Handle qualifiers (tags/boorus settings)
                    if 'qualifiers' in data:
                        result['qualifiers'] = data['qualifiers']
                    
                    # Handle advanced parameters
                    if 'parameters' in data:
                        params = data['parameters']
                        if isinstance(params, dict):
                            # Copy any additional parameters
                            for key, value in params.items():
                                if key not in result:
                                    result[key] = value
            except:
                # If base64 decoding fails, treat as regular text
                pass
        
        # Also try to parse regular parameters string format
        params = metadata.get('parameters') or metadata.get('Parameters') or ""
        if isinstance(params, str) and params:
            # Look for typical AI generation parameters
            param_patterns = {
                'steps': r'Steps[:=]?\s*([0-9]+)',
                'cfg_scale': r'(?:CFG scale|Scale)[:=]?\s*([0-9.]+)',
                'sampler': r'Sampler[:=]?\s*([^,\n]+)',
                'seed': r'Seed[:=]?\s*([0-9-]+)',
                'model_name': r'Model[:=]?\s*([^,\n]+)',
                'width': r'(?:Width|Size)[:=]?\s*([0-9]+)',
                'height': r'Height[:=]?\s*([0-9]+)',
                'denoising_strength': r'(?:Strength|Denoising strength)[:=]?\s*([0-9.]+)',
            }
            
            for field, pattern in param_patterns.items():
                if field not in result:  # Don't override decoded data
                    match = re.search(pattern, params, re.IGNORECASE)
                    if match:
                        value = match.group(1).strip()
                        try:
                            if field in ['steps', 'seed', 'width', 'height']:
                                result[field] = int(value)
                            elif field in ['cfg_scale', 'denoising_strength']:
                                result[field] = float(value)
                            else:
                                result[field] = value
                        except (ValueError, TypeError):
                            result[field] = value
            
            # Extract prompts if not already found
            if 'positive_prompt' not in result:
                # Look for prompt patterns
                if 'Positive prompt:' in params:
                    parts = params.split('Positive prompt:')
                    if len(parts) > 1:
                        prompt_part = parts[1].split('\n')[0].strip()
                        result['positive_prompt'] = prompt_part
                elif 'Prompt:' in params:
                    parts = params.split('Prompt:')
                    if len(parts) > 1:
                        prompt_part = parts[1].split('\n')[0].strip()
                        result['positive_prompt'] = prompt_part
                else:
                    # First line might be the prompt
                    first_line = params.split('\n')[0].strip()
                    if first_line and not ':' in first_line:
                        result['positive_prompt'] = first_line
            
            if 'negative_prompt' not in result:
                if 'Negative prompt:' in params:
                    parts = params.split('Negative prompt:')
                    if len(parts) > 1:
                        neg_part = parts[1].split('\n')[0].strip()
                        result['negative_prompt'] = neg_part
        
        # Check other metadata fields for additional info
        software = metadata.get('Software') or metadata.get('software') or ""
        if isinstance(software, str) and software:
            result['software'] = software
            if 'novelai' in software.lower():
                result['source'] = 'NovelAI'
        
        title = metadata.get('Title') or metadata.get('title') or ""
        if isinstance(title, str) and title:
            result['title'] = title
        
        # Extract size from standard EXIF if not found
        if 'width' not in result and 'Image Width' in metadata:
            try:
                result['width'] = int(metadata['Image Width'])
            except:
                pass
        
        if 'height' not in result and 'Image Height' in metadata:
            try:
                result['height'] = int(metadata['Image Height'])
            except:
                pass
        
        return result
