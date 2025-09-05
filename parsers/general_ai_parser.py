from utils.parser_plugin_interface import ParserPluginInterface
import re
import json
from typing import Dict, Any

class GeneralAIParser(ParserPluginInterface):
    """General AI parser for various AI generation tools with comprehensive detection"""

    @staticmethod
    def detect(metadata: Dict[str, Any]) -> bool:
        # Check for common AI generation indicators
        ai_indicators = [
            'prompt', 'Prompt', 'parameters', 'Parameters',
            'seed', 'Seed', 'steps', 'Steps',
            'cfg', 'CFG', 'sampler', 'Sampler',
            'model', 'Model', 'negative', 'Negative'
        ]
        
        # Check in various metadata fields
        check_fields = [
            'parameters', 'Parameters', 'comment', 'Comment',
            'description', 'Description', 'software', 'Software',
            'user_comment', 'UserComment', 'artist', 'Artist',
            'copyright', 'Copyright', 'title', 'Title'
        ]
        
        for field in check_fields:
            if field in metadata:
                value = str(metadata[field]).lower()
                # Check if it contains AI-related keywords
                if any(indicator.lower() in value for indicator in ai_indicators):
                    return True
                
                # Check for typical AI parameter patterns
                if re.search(r'\b(?:seed|steps|cfg|sampler)[:=]\s*\w+', value, re.IGNORECASE):
                    return True
        
        return False

    @staticmethod
    def parse(metadata: Dict[str, Any]) -> Dict[str, Any]:
        result = {'source': 'AI Generated'}
        
        # Fields to search for parameters
        search_fields = [
            'parameters', 'Parameters', 'comment', 'Comment',
            'description', 'Description', 'user_comment', 'UserComment',
            'artist', 'Artist', 'copyright', 'Copyright'
        ]
        
        all_text = ""
        for field in search_fields:
            if field in metadata:
                value = str(metadata[field])
                all_text += value + "\n"
        
        if not all_text.strip():
            return result
        
        # Try to detect specific AI tools first
        text_lower = all_text.lower()
        
        if 'stable diffusion' in text_lower or 'automatic1111' in text_lower:
            result['source'] = 'Stable Diffusion'
        elif 'midjourney' in text_lower:
            result['source'] = 'Midjourney'
        elif 'dall-e' in text_lower or 'dalle' in text_lower:
            result['source'] = 'DALL-E'
        elif 'leonardo' in text_lower:
            result['source'] = 'Leonardo AI'
        elif 'civitai' in text_lower:
            result['source'] = 'CivitAI'
        elif 'runway' in text_lower:
            result['source'] = 'Runway ML'
        elif 'artbreeder' in text_lower:
            result['source'] = 'Artbreeder'
        elif 'dreamstudio' in text_lower:
            result['source'] = 'DreamStudio'
        elif 'firefly' in text_lower:
            result['source'] = 'Adobe Firefly'
        
        # Extract common parameters with enhanced patterns
        param_patterns = {
            # Basic generation parameters
            'seed': [
                r'seed[:=]?\s*([0-9-]+)',
                r'random\s*seed[:=]?\s*([0-9-]+)',
            ],
            'steps': [
                r'steps[:=]?\s*([0-9]+)',
                r'sampling\s*steps[:=]?\s*([0-9]+)',
                r'iterations[:=]?\s*([0-9]+)',
            ],
            'cfg_scale': [
                r'cfg\s*scale[:=]?\s*([0-9.]+)',
                r'guidance\s*scale[:=]?\s*([0-9.]+)',
                r'cfg[:=]?\s*([0-9.]+)',
            ],
            'sampler': [
                r'sampler[:=]?\s*([^,\n;]+)',
                r'sampling\s*method[:=]?\s*([^,\n;]+)',
                r'algorithm[:=]?\s*([^,\n;]+)',
            ],
            'scheduler': [
                r'scheduler[:=]?\s*([^,\n;]+)',
                r'schedule\s*type[:=]?\s*([^,\n;]+)',
            ],
            'model_name': [
                r'model[:=]?\s*([^,\n;]+)',
                r'checkpoint[:=]?\s*([^,\n;]+)',
                r'base\s*model[:=]?\s*([^,\n;]+)',
            ],
            'model_hash': [
                r'model\s*hash[:=]?\s*([a-fA-F0-9]+)',
                r'hash[:=]?\s*([a-fA-F0-9]{8,})',
            ],
            'width': [
                r'width[:=]?\s*([0-9]+)',
                r'w[:=]?\s*([0-9]+)',
                r'size[:=]?\s*([0-9]+)x[0-9]+',
            ],
            'height': [
                r'height[:=]?\s*([0-9]+)',
                r'h[:=]?\s*([0-9]+)',
                r'size[:=]?\s*[0-9]+x([0-9]+)',
            ],
            'denoising_strength': [
                r'denoising\s*strength[:=]?\s*([0-9.]+)',
                r'noise\s*strength[:=]?\s*([0-9.]+)',
                r'strength[:=]?\s*([0-9.]+)',
            ],
            'clip_skip': [
                r'clip\s*skip[:=]?\s*([0-9]+)',
            ],
            'eta': [
                r'eta[:=]?\s*([0-9.]+)',
            ],
            'batch_size': [
                r'batch\s*size[:=]?\s*([0-9]+)',
                r'batch[:=]?\s*([0-9]+)',
            ],
        }
        
        # Extract parameters using patterns
        for field, patterns in param_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    try:
                        if field in ['seed', 'steps', 'width', 'height', 'clip_skip', 'batch_size']:
                            result[field] = int(value)
                        elif field in ['cfg_scale', 'denoising_strength', 'eta']:
                            result[field] = float(value)
                        else:
                            result[field] = value.strip('"\'')
                    except (ValueError, TypeError):
                        result[field] = value.strip('"\'')
                    break  # Use first matching pattern
        
        # Extract size as combined field
        size_match = re.search(r'size[:=]?\s*([0-9]+x[0-9]+)', all_text, re.IGNORECASE)
        if size_match:
            result['size'] = size_match.group(1)
            if 'width' not in result or 'height' not in result:
                try:
                    w, h = size_match.group(1).split('x')
                    if 'width' not in result:
                        result['width'] = int(w)
                    if 'height' not in result:
                        result['height'] = int(h)
                except:
                    pass
        
        # Extract prompts with various formats
        prompt_patterns = [
            # Standard format
            (r'prompt[:=]?\s*["\']?([^"\n]+)["\']?', 'positive_prompt'),
            (r'positive\s*prompt[:=]?\s*["\']?([^"\n]+)["\']?', 'positive_prompt'),
            # Negative prompts
            (r'negative\s*prompt[:=]?\s*["\']?([^"\n]+)["\']?', 'negative_prompt'),
            (r'avoid[:=]?\s*["\']?([^"\n]+)["\']?', 'negative_prompt'),
            # Description field might contain prompt
            (r'description[:=]?\s*["\']?([^"\n]+)["\']?', 'description'),
        ]
        
        for pattern, field in prompt_patterns:
            if field not in result:
                match = re.search(pattern, all_text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    # Clean up common artifacts
                    value = re.sub(r'^[:\-=]+\s*', '', value)
                    value = value.strip('"\'')
                    if value and len(value) > 3:  # Avoid very short matches
                        result[field] = value
        
        # If no explicit prompts found, try to extract from first lines
        if 'positive_prompt' not in result and 'description' not in result:
            lines = all_text.strip().split('\n')
            if lines:
                first_line = lines[0].strip()
                # Check if first line looks like a prompt (not a parameter)
                if first_line and not re.search(r'[:=]', first_line) and len(first_line) > 10:
                    result['positive_prompt'] = first_line
        
        # Extract version information
        version_patterns = [
            r'version[:=]?\s*([^,\n;]+)',
            r'v[:=]?\s*([0-9.]+)',
            r'build[:=]?\s*([^,\n;]+)',
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                result['version'] = match.group(1).strip()
                break
        
        # Extract additional technical parameters
        tech_patterns = {
            'upscaler': r'upscaler[:=]?\s*([^,\n;]+)',
            'face_restoration': r'face\s*restoration[:=]?\s*([^,\n;]+)',
            'controlnet': r'controlnet[:=]?\s*([^,\n;]+)',
            'lora': r'lora[:=]?\s*([^,\n;]+)',
            'vae': r'vae[:=]?\s*([^,\n;]+)',
            'hypernetwork': r'hypernetwork[:=]?\s*([^,\n;]+)',
        }
        
        for field, pattern in tech_patterns.items():
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                result[field] = match.group(1).strip().strip('"\'')
        
        # Try to parse any JSON-like structures
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        json_matches = re.findall(json_pattern, all_text)
        for json_text in json_matches:
            try:
                data = json.loads(json_text)
                if isinstance(data, dict):
                    # Merge any additional fields
                    for key, value in data.items():
                        if key not in result and isinstance(value, (str, int, float)):
                            result[key] = value
            except:
                continue
        
        return result
