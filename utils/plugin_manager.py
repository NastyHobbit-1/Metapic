# Enhanced plugin manager with logging and error handling

from .common_imports import *
from .logger import logger, PerformanceTimer
from .error_handler import handle_errors, ErrorCategory, ErrorSeverity
from config.settings import get_config
import importlib
import pkgutil
import parsers  # Make sure 'parsers' is a Python package (has __init__.py)

class PluginManager:
    """Enhanced plugin manager with comprehensive error handling and logging"""
    
    def __init__(self, plugins_package: str = "parsers"):
        self.plugins = []
        self.plugins_package = plugins_package
        self.plugin_errors = []
        self.timeout = get_config('parser_timeout', 30)
        
        logger.info(f"Initializing PluginManager for package: {plugins_package}")
        
        with PerformanceTimer("plugin_manager_initialization"):
            self.load_plugins()
            
        logger.info(f"PluginManager initialized with {len(self.plugins)} plugins")

    @handle_errors(ErrorCategory.PARSING, "Loading parser plugins")
    def load_plugins(self):
        """Load all parser plugins from the parsers directory with enhanced error handling"""
        try:
            logger.info(f"Loading plugins from package: {self.plugins_package}")
            
            # Import the parsers package
            parsers_module = importlib.import_module(self.plugins_package)
            logger.debug(f"Successfully imported {self.plugins_package} package")
            
            # Iterate through all modules in the parsers package
            for finder, name, ispkg in pkgutil.iter_modules(parsers_module.__path__):
                module_name = f'{self.plugins_package}.{name}'
                
                try:
                    with PerformanceTimer(f"load_plugin_{name}"):
                        logger.debug(f"Loading plugin module: {module_name}")
                        module = importlib.import_module(module_name)
                        
                        # Look for classes that end with 'Parser'
                        plugin_count = 0
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            
                            if (isinstance(attr, type) and 
                                attr_name.endswith('Parser') and 
                                hasattr(attr, 'detect') and 
                                hasattr(attr, 'parse')):
                                
                                # Validate plugin interface
                                if self._validate_plugin(attr, attr_name):
                                    self.plugins.append(attr)
                                    plugin_count += 1
                                    logger.info(f"Successfully loaded parser plugin: {attr_name}")
                        
                        if plugin_count == 0:
                            logger.warning(f"No valid parser classes found in module: {module_name}")
                            
                except ImportError as e:
                    error_msg = f"Failed to import parser plugin {module_name}"
                    logger.error(error_msg, e)
                    self.plugin_errors.append((module_name, str(e)))
                    
                except Exception as e:
                    error_msg = f"Error processing parser plugin {module_name}"
                    logger.error(error_msg, e)
                    self.plugin_errors.append((module_name, str(e)))
                    
        except Exception as e:
            error_msg = f"Critical error loading plugins from {self.plugins_package}"
            logger.error(error_msg, e)
            raise

    def _validate_plugin(self, plugin_class, plugin_name: str) -> bool:
        """Validate that a plugin has the required interface"""
        try:
            # Check required methods
            required_methods = ['detect', 'parse']
            for method_name in required_methods:
                if not hasattr(plugin_class, method_name):
                    logger.warning(f"Plugin {plugin_name} missing required method: {method_name}")
                    return False
                
                method = getattr(plugin_class, method_name)
                if not callable(method):
                    logger.warning(f"Plugin {plugin_name} method {method_name} is not callable")
                    return False
            
            logger.debug(f"Plugin {plugin_name} passed validation")
            return True
            
        except Exception as e:
            logger.error(f"Error validating plugin {plugin_name}", e)
            return False
    
    @handle_errors(ErrorCategory.PARSING, "Parsing metadata with plugins")
    def parse_metadata(self, raw_metadata):
        """Try each plugin to parse the metadata with enhanced error handling"""
        
        with PerformanceTimer("parse_metadata_all_plugins"):
            logger.debug(f"Attempting to parse metadata with {len(self.plugins)} plugins")
            
            for plugin in self.plugins:
                try:
                    plugin_name = plugin.__name__
                    logger.debug(f"Trying plugin: {plugin_name}")
                    
                    with PerformanceTimer(f"plugin_detect_{plugin_name}"):
                        if plugin.detect(raw_metadata):
                            logger.info(f"Plugin {plugin_name} detected compatible metadata")
                            
                            with PerformanceTimer(f"plugin_parse_{plugin_name}"):
                                parsed = plugin.parse(raw_metadata)
                                
                            if parsed:
                                logger.info(f"Successfully parsed metadata with {plugin_name}")
                                return parsed
                            else:
                                logger.warning(f"Plugin {plugin_name} returned empty result")
                        else:
                            logger.debug(f"Plugin {plugin_name} did not detect compatible metadata")
                            
                except Exception as e:
                    error_msg = f"Error in parser {plugin.__name__}"
                    logger.error(error_msg, e)
                    self.plugin_errors.append((plugin.__name__, str(e)))
            
            logger.warning("No plugins could successfully parse the metadata")
            # fallback if no parser succeeds
            return raw_metadata
    
    def get_plugin_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded plugins"""
        return {
            'total_plugins': len(self.plugins),
            'plugin_names': [plugin.__name__ for plugin in self.plugins],
            'plugin_errors': self.plugin_errors,
            'error_count': len(self.plugin_errors)
        }
    
    def get_plugin_by_name(self, name: str):
        """Get a specific plugin by name"""
        for plugin in self.plugins:
            if plugin.__name__ == name:
                return plugin
        return None
    
    def reload_plugins(self):
        """Reload all plugins (useful for development)"""
        logger.info("Reloading all plugins...")
        
        # Clear current plugins and errors
        self.plugins.clear()
        self.plugin_errors.clear()
        
        # Reload plugins
        with PerformanceTimer("plugin_reload"):
            self.load_plugins()
            
        logger.info(f"Plugin reload complete: {len(self.plugins)} plugins loaded")
