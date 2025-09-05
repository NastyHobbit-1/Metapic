from utils.parser_plugin_interface import ParserPluginInterface
from utils.common_imports import *
from utils.extraction_utils import extractor
from utils.logger import logger, PerformanceTimer
from utils.error_handler import handle_errors, ErrorCategory, ErrorSeverity

class Automatic1111Parser(ParserPluginInterface):
    """Automatic1111 parser with comprehensive metadata extraction"""

    @staticmethod
    def detect(metadata: Dict[str, Any]) -> bool:
        params = metadata.get('parameters') or metadata.get('Parameters') or ""
        return isinstance(params, str) and ('Negative prompt:' in params or 
                                           'Steps:' in params or 
                                           'Seed:' in params or
                                           'CFG scale:' in params)

    @staticmethod
    @handle_errors(ErrorCategory.PARSING, "Parsing Automatic1111 metadata")
    def parse(metadata: Dict[str, Any]) -> Dict[str, Any]:
        params = metadata.get('parameters') or metadata.get('Parameters') or ""
        
        with PerformanceTimer("automatic1111_parse"):
            result = {}
            
            # Use extraction utilities for prompt splitting
            prompt_data = extractor.extract_prompt_sections(params)
            result['positive_prompt'] = prompt_data['positive_prompt']
            result['negative_prompt'] = prompt_data['negative_prompt']
            
            logger.debug(f"Extracted prompts: positive={len(result['positive_prompt'])} chars, "
                        f"negative={len(result['negative_prompt'])} chars")

            # Use extraction utilities for technical parameters
            tech_params = extractor.extract_technical_parameters(params)
            result.update(tech_params)
            
            # Use extraction utilities for hi-res parameters
            hires_params = extractor.extract_hires_parameters(params)
            result.update(hires_params)
            
            # Use extraction utilities for model information
            model_info = extractor.extract_model_information(params)
            result.update(model_info)
            
            # Use extraction utilities for dimensions
            dimensions = extractor.extract_size_dimensions(params)
            result.update(dimensions)
            
            # Use extraction utilities for ControlNet information
            controlnet_info = extractor.extract_controlnet_information(params)
            result.update(controlnet_info)
            
            # Use extraction utilities for LoRA information
            if result.get('positive_prompt'):
                loras = extractor.extract_lora_information(result['positive_prompt'])
                if loras:
                    result['loras'] = loras
                    result['lora_names'] = [lora['name'] for lora in loras]
            
            # Validate and clean the extracted data
            result = extractor.validate_extracted_data(result)
            
            # Set source identifier
            result['source'] = 'Automatic1111'
            
            logger.debug(f"Automatic1111 parser extracted {len(result)} fields")
            return result
