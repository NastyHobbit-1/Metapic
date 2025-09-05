# metadata_extractor.py
import os
from typing import Dict, Any, List
from .raw_metadata_loader import extract_metadata as raw_extract
import os
from typing import Dict, Any, List
from .raw_metadata_loader import extract_metadata as raw_extract

# Import parsers
try:
    from parsers.automatic1111_parser import Automatic1111Parser
    from parsers.comfyui_parser import ComfyUIParser
    from parsers.novelai_parser import NovelAIParser
    from parsers.general_ai_parser import GeneralAIParser
except ImportError:
    Automatic1111Parser = None
    ComfyUIParser = None
    NovelAIParser = None
    GeneralAIParser = None

def get_default_plugins():
    """Get list of available parsers"""
    plugins = []
    if Automatic1111Parser:
        plugins.append(Automatic1111Parser)
    if ComfyUIParser:
        plugins.append(ComfyUIParser)
    if NovelAIParser:
        plugins.append(NovelAIParser)
    if GeneralAIParser:
        plugins.append(GeneralAIParser)
    return plugins

def extract_metadata(image_path: str, plugins: List = None) -> Dict[str, Any]:
    """Extract metadata from image using available plugins"""
    raw = raw_extract(image_path)
    
    if plugins is None:
        plugins = get_default_plugins()
    
    if plugins:
        
        best_result = None
        best_field_count = 0
        
        # Try each parser and find the one that extracts the most fields
        for plugin in plugins:
            try:
                if plugin.detect(raw):
                    parsed = plugin.parse(raw)
                    if parsed:
                        # Count non-internal fields (exclude those starting with _)
                        field_count = len([k for k in parsed.keys() if not k.startswith('_')])
                        
                        # If this parser extracts more fields, use it
                        if field_count > best_field_count:
                            best_result = parsed
                            best_field_count = field_count
                            
            except Exception as e:
                print(f"Error in plugin {plugin.__name__}: {e}")
        
        if best_result:
            # Add raw metadata for debugging/comparison
            best_result['_raw_metadata'] = raw
            return best_result
    
    # If no plugins provided, try default parsers directly
    default_plugins = get_default_plugins()
    if default_plugins:
        for plugin in default_plugins:
            try:
                if plugin.detect(raw):
                    parsed = plugin.parse(raw)
                    if parsed:
                        parsed['_raw_metadata'] = raw
                        return parsed
            except Exception as e:
                print(f"Error in plugin {plugin.__name__}: {e}")

    # Fallback: return raw or minimally structured
    return {
        "source": "Unknown",
        "extra": str(raw),
        "_raw_metadata": raw
    }


# Import enhanced metadata writer
from .enhanced_metadata_writer import save_metadata
