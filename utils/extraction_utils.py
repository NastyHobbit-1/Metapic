"""
Metadata Extraction Utilities for MetaPicPick
Consolidates common regex patterns and extraction logic used across parsers.
"""

from .common_imports import *
from .logger import logger, PerformanceTimer


class MetadataExtractor:
    """Utility class for extracting metadata fields using standardized patterns"""
    
    def __init__(self):
        """Initialize the metadata extractor"""
        logger.debug("Initializing MetadataExtractor")
        self.extraction_cache = {}
    
    @staticmethod
    def extract_field(text: str, field_config: Tuple[str, type, Any]) -> Any:
        """
        Extract a single field from text using regex pattern
        
        Args:
            text: Text to search in
            field_config: Tuple of (pattern, type_converter, default_value)
            
        Returns:
            Extracted and converted value or default value
        """
        pattern, type_conv, default = field_config
        
        try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                raw_value = match.group(1).strip()
                if raw_value:
                    try:
                        return type_conv(raw_value)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Failed to convert '{raw_value}' to {type_conv.__name__}: {e}")
                        return raw_value
            return default
        except Exception as e:
            logger.error(f"Error extracting field with pattern '{pattern}'", e)
            return default
    
    def extract_multiple_fields(self, text: str, field_configs: Dict[str, Tuple[str, type, Any]]) -> Dict[str, Any]:
        """
        Extract multiple fields from text using regex patterns
        
        Args:
            text: Text to search in
            field_configs: Dictionary mapping field names to (pattern, type_converter, default_value)
            
        Returns:
            Dictionary of extracted field values
        """
        with PerformanceTimer("extract_multiple_fields", f"{len(field_configs)} fields"):
            result = {}
            
            for field_name, field_config in field_configs.items():
                result[field_name] = self.extract_field(text, field_config)
            
            logger.debug(f"Extracted {len([k for k, v in result.items() if v is not None])} non-null fields")
            return result
    
    def extract_size_dimensions(self, text: str) -> Dict[str, Any]:
        """
        Extract image dimensions with various formats
        
        Args:
            text: Text to search in
            
        Returns:
            Dictionary with width, height, and size fields
        """
        result = {}
        
        # Pattern variations for size extraction
        size_patterns = [
            r'Size[:=]?\s*([0-9]+)x([0-9]+)',  # Size: 512x512
            r'Resolution[:=]?\s*([0-9]+)x([0-9]+)',  # Resolution: 512x512
            r'Dimensions[:=]?\s*([0-9]+)x([0-9]+)',  # Dimensions: 512x512
            r'([0-9]+)\s*x\s*([0-9]+)\s*pixels',  # 512 x 512 pixels
            r'Width[:=]?\s*([0-9]+).*?Height[:=]?\s*([0-9]+)',  # Width: 512, Height: 512
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    width = int(match.group(1))
                    height = int(match.group(2))
                    result['width'] = width
                    result['height'] = height
                    result['size'] = f"{width}x{height}"
                    logger.debug(f"Extracted dimensions: {width}x{height}")
                    break
                except (ValueError, IndexError) as e:
                    logger.warning(f"Failed to parse dimensions from match: {match.groups()}", e)
                    continue
        
        return result
    
    def extract_prompt_sections(self, text: str) -> Dict[str, str]:
        """
        Extract positive and negative prompts from text
        
        Args:
            text: Text containing prompts
            
        Returns:
            Dictionary with 'positive_prompt' and 'negative_prompt' keys
        """
        result = {'positive_prompt': '', 'negative_prompt': ''}
        
        # Common negative prompt markers
        negative_markers = [
            'Negative prompt:',
            'Negative:',
            'Neg prompt:',
            'Neg:',
            'Negative Prompt:',
        ]
        
        for marker in negative_markers:
            if marker in text:
                parts = text.split(marker, 1)
                result['positive_prompt'] = parts[0].strip()
                
                if len(parts) > 1:
                    negative_part = parts[1].strip()
                    # Split on newline to separate negative prompt from parameters
                    negative_lines = negative_part.split('\n')
                    result['negative_prompt'] = negative_lines[0].strip()
                
                logger.debug(f"Split prompts using marker: {marker}")
                return result
        
        # If no negative prompt marker found, treat entire text as positive
        result['positive_prompt'] = text.strip()
        logger.debug("No negative prompt marker found, treating entire text as positive")
        return result
    
    def extract_lora_information(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract LoRA information from prompts
        
        Args:
            text: Text containing LoRA references
            
        Returns:
            List of dictionaries with LoRA information
        """
        loras = []
        
        # Pattern for LoRA syntax: <lora:name:weight>
        lora_pattern = r'<lora:([^:>]+)(?::([0-9.]+))?>'
        
        matches = re.findall(lora_pattern, text, re.IGNORECASE)
        for match in matches:
            lora_info = {
                'name': match[0].strip(),
                'weight': float(match[1]) if match[1] else 1.0
            }
            loras.append(lora_info)
        
        if loras:
            logger.debug(f"Extracted {len(loras)} LoRA references")
        
        return loras
    
    def extract_controlnet_information(self, text: str) -> Dict[str, Any]:
        """
        Extract ControlNet information from metadata
        
        Args:
            text: Text containing ControlNet information
            
        Returns:
            Dictionary with ControlNet details
        """
        result = {}
        
        # ControlNet patterns
        controlnet_patterns = {
            'model': r'ControlNet\s*(?:Model)?[:=]?\s*([^,\n]+)',
            'weight': r'ControlNet\s*Weight[:=]?\s*([0-9.]+)',
            'guidance_start': r'ControlNet\s*Guidance\s*Start[:=]?\s*([0-9.]+)',
            'guidance_end': r'ControlNet\s*Guidance\s*End[:=]?\s*([0-9.]+)',
            'preprocessor': r'ControlNet\s*Preprocessor[:=]?\s*([^,\n]+)',
        }
        
        for field, pattern in controlnet_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if field in ['weight', 'guidance_start', 'guidance_end']:
                    try:
                        result[field] = float(value)
                    except ValueError:
                        result[field] = value
                else:
                    result[field] = value
        
        if result:
            logger.debug(f"Extracted ControlNet information: {list(result.keys())}")
        
        return result
    
    def extract_technical_parameters(self, text: str) -> Dict[str, Any]:
        """
        Extract common technical parameters with standardized patterns
        
        Args:
            text: Text containing technical parameters
            
        Returns:
            Dictionary of extracted parameters
        """
        # Standard parameter extraction configurations
        tech_configs = {
            'seed': (r'Seed[:=]?\s*([0-9-]+)', int, None),
            'steps': (r'Steps[:=]?\s*([0-9]+)', int, None),
            'cfg_scale': (r'CFG\s*[Ss]cale[:=]?\s*([0-9.]+)', float, None),
            'sampler': (r'Sampler[:=]?\s*([^,\n]+)', str, None),
            'scheduler': (r'Schedule(?:r|r\s+type)?[:=]?\s*([^,\n]+)', str, None),
            'model_hash': (r'Model\s*[Hh]ash[:=]?\s*([a-fA-F0-9]+)', str, None),
            'clip_skip': (r'Clip\s*[Ss]kip[:=]?\s*([0-9]+)', int, None),
            'ensd': (r'ENSD[:=]?\s*([0-9-]+)', int, None),
            'eta': (r'Eta[:=]?\s*([0-9.]+)', float, None),
            'denoising_strength': (r'Denoising\s*[Ss]trength[:=]?\s*([0-9.]+)', float, None),
            'subseed': (r'(?:Variation\s*seed|Subseed)[:=]?\s*([0-9-]+)', int, None),
            'subseed_strength': (r'(?:Variation\s*seed\s*strength|Subseed\s*strength)[:=]?\s*([0-9.]+)', float, None),
        }
        
        return self.extract_multiple_fields(text, tech_configs)
    
    def extract_hires_parameters(self, text: str) -> Dict[str, Any]:
        """
        Extract hi-res fix parameters
        
        Args:
            text: Text containing hi-res parameters
            
        Returns:
            Dictionary of hi-res parameters
        """
        hires_configs = {
            'hires_upscale': (r'Hires\s*[Uu]pscale[:=]?\s*([0-9.]+)', float, None),
            'hires_steps': (r'Hires\s*[Ss]teps[:=]?\s*([0-9]+)', int, None),
            'hires_upscaler': (r'Hires\s*[Uu]pscaler[:=]?\s*([^,\n]+)', str, None),
            'hires_resize_width': (r'Hires\s*[Rr]esize[:=]?\s*([0-9]+)x[0-9]+', int, None),
            'hires_resize_height': (r'Hires\s*[Rr]esize[:=]?\s*[0-9]+x([0-9]+)', int, None),
        }
        
        return self.extract_multiple_fields(text, hires_configs)
    
    def extract_model_information(self, text: str) -> Dict[str, Any]:
        """
        Extract model-related information
        
        Args:
            text: Text containing model information
            
        Returns:
            Dictionary of model information
        """
        model_configs = {
            'model_name': (r'Model[:=]\s*([^,\n]+?)(?:,|\n|$)', str, None),
            'model_hash': (r'Model\s*[Hh]ash[:=]?\s*([a-fA-F0-9]+)', str, None),
            'vae': (r'VAE[:=]\s*([^,\n]+?)(?:,|\n|$)', str, None),
            'vae_hash': (r'VAE\s*[Hh]ash[:=]?\s*([a-fA-F0-9]+)', str, None),
            'version': (r'Version[:=]?\s*([^,\n]+)', str, None),
        }
        
        return self.extract_multiple_fields(text, model_configs)
    
    def extract_quality_tags(self, prompt: str) -> Dict[str, List[str]]:
        """
        Extract quality-related tags from prompts
        
        Args:
            prompt: Prompt text
            
        Returns:
            Dictionary with 'positive_quality' and 'negative_quality' lists
        """
        result = {'positive_quality': [], 'negative_quality': []}
        
        # Quality indicators
        positive_quality = [
            'masterpiece', 'best quality', 'high quality', 'ultra detailed',
            'extremely detailed', 'highly detailed', 'perfect', 'beautiful',
            'stunning', 'amazing', 'incredible', 'fantastic', 'excellent'
        ]
        
        negative_quality = [
            'worst quality', 'low quality', 'normal quality', 'bad quality',
            'poor quality', 'blurry', 'ugly', 'deformed', 'disfigured',
            'bad anatomy', 'bad proportions', 'gross proportions'
        ]
        
        prompt_lower = prompt.lower()
        
        for tag in positive_quality:
            if tag in prompt_lower:
                result['positive_quality'].append(tag)
        
        for tag in negative_quality:
            if tag in prompt_lower:
                result['negative_quality'].append(tag)
        
        return result
    
    def extract_artist_style_tags(self, prompt: str) -> List[str]:
        """
        Extract artist and style-related tags
        
        Args:
            prompt: Prompt text
            
        Returns:
            List of artist/style tags
        """
        style_patterns = [
            r'(?:by|artist:|style\s+of)\s+([^,\n]+)',
            r'([^,\n]*(?:art|painting|style|artwork)[^,\n]*)',
        ]
        
        styles = []
        for pattern in style_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                clean_match = match.strip()
                if len(clean_match) > 3 and clean_match not in styles:
                    styles.append(clean_match)
        
        return styles
    
    def clean_and_normalize_value(self, value: Any, field_type: type = str) -> Any:
        """
        Clean and normalize extracted values
        
        Args:
            value: Raw extracted value
            field_type: Expected type
            
        Returns:
            Cleaned and normalized value
        """
        if value is None:
            return None
        
        # Convert to string first for cleaning
        str_value = str(value).strip()
        
        if not str_value:
            return None
        
        # Remove common unwanted characters
        str_value = re.sub(r'["""''`]', '', str_value)  # Remove quotes
        str_value = re.sub(r'\s+', ' ', str_value)  # Normalize whitespace
        
        # Type conversion
        try:
            if field_type == int:
                # Handle negative numbers and remove non-numeric suffixes
                match = re.search(r'^(-?[0-9]+)', str_value)
                if match:
                    return int(match.group(1))
            elif field_type == float:
                # Handle decimal numbers
                match = re.search(r'^(-?[0-9]*\.?[0-9]+)', str_value)
                if match:
                    return float(match.group(1))
            elif field_type == bool:
                return str_value.lower() in ('true', '1', 'yes', 'on', 'enabled')
            else:
                return str_value
        except (ValueError, AttributeError):
            logger.warning(f"Failed to convert '{str_value}' to {field_type.__name__}")
            return str_value
        
        return str_value
    
    def validate_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean extracted metadata
        
        Args:
            data: Dictionary of extracted data
            
        Returns:
            Validated and cleaned data
        """
        validated = {}
        
        for key, value in data.items():
            if value is not None:
                # Remove empty strings and whitespace-only values
                if isinstance(value, str) and not value.strip():
                    continue
                
                # Validate numeric ranges
                if key == 'steps' and isinstance(value, int):
                    if 1 <= value <= 1000:
                        validated[key] = value
                elif key == 'cfg_scale' and isinstance(value, (int, float)):
                    if 0.1 <= value <= 30.0:
                        validated[key] = float(value)
                elif key in ['width', 'height'] and isinstance(value, int):
                    if 64 <= value <= 8192:
                        validated[key] = value
                else:
                    validated[key] = value
        
        return validated


# Global extractor instance
extractor = MetadataExtractor()

# Convenience functions
def extract_field(text: str, pattern: str, type_conv: type = str, default: Any = None) -> Any:
    """Convenience function for single field extraction"""
    return extractor.extract_field(text, (pattern, type_conv, default))

def extract_prompts(text: str) -> Dict[str, str]:
    """Convenience function for prompt extraction"""
    return extractor.extract_prompt_sections(text)

def extract_dimensions(text: str) -> Dict[str, Any]:
    """Convenience function for dimension extraction"""
    return extractor.extract_size_dimensions(text)
