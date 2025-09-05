"""
Configuration Management for MetaPicPick
Centralizes application settings with validation and persistence.
"""

from utils.common_imports import *
from utils.logger import logger
from pathlib import Path


@dataclass
class AppConfig:
    """Application configuration with default values"""
    
    # GUI Settings
    auto_refresh_interval: int = 5000  # milliseconds
    default_window_width: int = 1400
    default_window_height: int = 900
    default_font_size: int = 10
    theme: str = "light"  # light, dark
    
    # Statistics Settings
    max_tags_display: int = 1000
    backup_statistics: bool = True
    statistics_cache_enabled: bool = True
    cache_timeout: int = 300  # seconds
    
    # Export Settings
    default_export_format: str = "json"  # json, csv
    export_include_raw: bool = True
    
    # Logging Settings
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_to_file: bool = True
    log_to_console: bool = True
    max_log_size_mb: int = 10
    log_backup_count: int = 5
    
    # Parser Settings
    parser_timeout: int = 30  # seconds
    enable_parser_caching: bool = True
    max_cache_entries: int = 1000
    
    # Performance Settings
    parallel_processing: bool = True
    max_worker_threads: int = 4
    chunk_size: int = 100  # for batch operations
    
    # Validation Settings
    validate_metadata: bool = True
    strict_validation: bool = False
    auto_fix_common_issues: bool = True
    
    # UI Behavior
    remember_window_state: bool = True
    remember_tab_selection: bool = True
    show_tooltips: bool = True
    confirm_destructive_actions: bool = True
    
    # Advanced Settings
    debug_mode: bool = False
    enable_profiling: bool = False
    custom_parser_paths: List[str] = None
    
    def __post_init__(self):
        """Initialize lists if None"""
        if self.custom_parser_paths is None:
            self.custom_parser_paths = []

    @classmethod
    def load_from_file(cls, filepath: str) -> 'AppConfig':
        """
        Load configuration from JSON file
        
        Args:
            filepath: Path to configuration file
            
        Returns:
            AppConfig instance with loaded settings
        """
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Create instance with loaded data
                config = cls()
                for key, value in data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
                    else:
                        logger.warning(f"Unknown configuration key: {key}")
                
                logger.info(f"Configuration loaded from {filepath}")
                return config
            else:
                logger.info(f"Configuration file not found: {filepath}, using defaults")
                return cls()
                
        except Exception as e:
            logger.error(f"Failed to load configuration from {filepath}", e)
            logger.info("Using default configuration")
            return cls()
    
    def save_to_file(self, filepath: str) -> bool:
        """
        Save configuration to JSON file
        
        Args:
            filepath: Path to save configuration file
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Convert to dictionary
            data = asdict(self)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {filepath}", e)
            return False
    
    def validate(self) -> List[str]:
        """
        Validate configuration values
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Validate numeric ranges
        if self.auto_refresh_interval < 1000 or self.auto_refresh_interval > 60000:
            errors.append("auto_refresh_interval must be between 1000 and 60000 ms")
        
        if self.default_window_width < 800 or self.default_window_width > 3840:
            errors.append("default_window_width must be between 800 and 3840")
        
        if self.default_window_height < 600 or self.default_window_height > 2160:
            errors.append("default_window_height must be between 600 and 2160")
        
        if self.max_tags_display < 10 or self.max_tags_display > 10000:
            errors.append("max_tags_display must be between 10 and 10000")
        
        if self.cache_timeout < 60 or self.cache_timeout > 3600:
            errors.append("cache_timeout must be between 60 and 3600 seconds")
        
        if self.max_worker_threads < 1 or self.max_worker_threads > 16:
            errors.append("max_worker_threads must be between 1 and 16")
        
        # Validate string values
        if self.theme not in ['light', 'dark']:
            errors.append("theme must be 'light' or 'dark'")
        
        if self.default_export_format not in ['json', 'csv']:
            errors.append("default_export_format must be 'json' or 'csv'")
        
        if self.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            errors.append("log_level must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL")
        
        return errors
    
    def apply_fixes(self) -> List[str]:
        """
        Apply automatic fixes for common configuration issues
        
        Returns:
            List of fixes applied
        """
        fixes = []
        
        # Fix out-of-range values
        if self.auto_refresh_interval < 1000:
            self.auto_refresh_interval = 1000
            fixes.append("Fixed auto_refresh_interval minimum value")
        elif self.auto_refresh_interval > 60000:
            self.auto_refresh_interval = 60000
            fixes.append("Fixed auto_refresh_interval maximum value")
        
        if self.max_tags_display < 10:
            self.max_tags_display = 10
            fixes.append("Fixed max_tags_display minimum value")
        elif self.max_tags_display > 10000:
            self.max_tags_display = 1000
            fixes.append("Fixed max_tags_display maximum value")
        
        # Fix invalid string values
        if self.theme not in ['light', 'dark']:
            self.theme = 'light'
            fixes.append("Fixed invalid theme, set to 'light'")
        
        if self.default_export_format not in ['json', 'csv']:
            self.default_export_format = 'json'
            fixes.append("Fixed invalid export format, set to 'json'")
        
        if self.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            self.log_level = 'INFO'
            fixes.append("Fixed invalid log level, set to 'INFO'")
        
        return fixes
    
    def get_display_settings(self) -> Dict[str, Any]:
        """Get settings related to display and UI"""
        return {
            'window_width': self.default_window_width,
            'window_height': self.default_window_height,
            'font_size': self.default_font_size,
            'theme': self.theme,
            'show_tooltips': self.show_tooltips,
            'remember_window_state': self.remember_window_state,
            'remember_tab_selection': self.remember_tab_selection
        }
    
    def get_performance_settings(self) -> Dict[str, Any]:
        """Get settings related to performance"""
        return {
            'parallel_processing': self.parallel_processing,
            'max_worker_threads': self.max_worker_threads,
            'chunk_size': self.chunk_size,
            'cache_enabled': self.statistics_cache_enabled,
            'cache_timeout': self.cache_timeout,
            'parser_caching': self.enable_parser_caching,
            'max_cache_entries': self.max_cache_entries
        }
    
    def get_logging_settings(self) -> Dict[str, Any]:
        """Get settings related to logging"""
        return {
            'log_level': self.log_level,
            'log_to_file': self.log_to_file,
            'log_to_console': self.log_to_console,
            'max_log_size_mb': self.max_log_size_mb,
            'log_backup_count': self.log_backup_count
        }


class ConfigManager:
    """Configuration manager with persistence and validation"""
    
    def __init__(self, config_dir: str = None):
        """
        Initialize configuration manager
        
        Args:
            config_dir: Directory to store configuration files
        """
        if config_dir is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".metapicpick")
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.backup_dir = self.config_dir / "backups"
        
        # Create directories
        self.config_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self.config = AppConfig.load_from_file(str(self.config_file))
        
        # Validate and fix configuration
        self._validate_and_fix()
        
        logger.info("Configuration manager initialized")
    
    def _validate_and_fix(self):
        """Validate configuration and apply fixes if needed"""
        errors = self.config.validate()
        if errors:
            logger.warning(f"Configuration validation errors: {errors}")
            
            if self.config.auto_fix_common_issues:
                fixes = self.config.apply_fixes()
                if fixes:
                    logger.info(f"Applied automatic fixes: {fixes}")
                    self.save()
        
        # Re-validate after fixes
        remaining_errors = self.config.validate()
        if remaining_errors:
            logger.error(f"Configuration still has errors after fixes: {remaining_errors}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value by key
        
        Args:
            key: Configuration key
            value: Value to set
            
        Returns:
            True if set successfully, False otherwise
        """
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            logger.debug(f"Configuration updated: {key} = {value}")
            return True
        else:
            logger.warning(f"Unknown configuration key: {key}")
            return False
    
    def save(self) -> bool:
        """
        Save current configuration to file
        
        Returns:
            True if saved successfully, False otherwise
        """
        return self.config.save_to_file(str(self.config_file))
    
    def backup(self) -> bool:
        """
        Create a backup of current configuration
        
        Returns:
            True if backup created successfully, False otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"config_backup_{timestamp}.json"
            
            success = self.config.save_to_file(str(backup_file))
            if success:
                logger.info(f"Configuration backed up to {backup_file}")
                
                # Clean up old backups (keep last 10)
                self._cleanup_old_backups()
                
            return success
            
        except Exception as e:
            logger.error("Failed to create configuration backup", e)
            return False
    
    def _cleanup_old_backups(self, keep_count: int = 10):
        """Remove old backup files, keeping only the most recent ones"""
        try:
            backup_files = list(self.backup_dir.glob("config_backup_*.json"))
            if len(backup_files) > keep_count:
                # Sort by modification time (newest first)
                backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                # Remove old files
                for old_file in backup_files[keep_count:]:
                    old_file.unlink()
                    logger.debug(f"Removed old backup: {old_file}")
        
        except Exception as e:
            logger.warning("Failed to cleanup old backups", e)
    
    def restore_from_backup(self, backup_file: str = None) -> bool:
        """
        Restore configuration from backup file
        
        Args:
            backup_file: Specific backup file to restore from (optional)
            
        Returns:
            True if restored successfully, False otherwise
        """
        try:
            if backup_file is None:
                # Find the most recent backup
                backup_files = list(self.backup_dir.glob("config_backup_*.json"))
                if not backup_files:
                    logger.error("No backup files found")
                    return False
                
                backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                backup_file = str(backup_files[0])
            
            # Load configuration from backup
            restored_config = AppConfig.load_from_file(backup_file)
            
            # Create backup of current config before restoring
            self.backup()
            
            # Replace current configuration
            self.config = restored_config
            self.save()
            
            logger.info(f"Configuration restored from {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore configuration from {backup_file}", e)
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values
        
        Returns:
            True if reset successfully, False otherwise
        """
        try:
            # Create backup before reset
            self.backup()
            
            # Create new default configuration
            self.config = AppConfig()
            self.save()
            
            logger.info("Configuration reset to defaults")
            return True
            
        except Exception as e:
            logger.error("Failed to reset configuration to defaults", e)
            return False
    
    def export_config(self, export_path: str) -> bool:
        """
        Export configuration to external file
        
        Args:
            export_path: Path to export the configuration
            
        Returns:
            True if exported successfully, False otherwise
        """
        return self.config.save_to_file(export_path)
    
    def import_config(self, import_path: str) -> bool:
        """
        Import configuration from external file
        
        Args:
            import_path: Path to import the configuration from
            
        Returns:
            True if imported successfully, False otherwise
        """
        try:
            # Create backup before import
            self.backup()
            
            # Load imported configuration
            imported_config = AppConfig.load_from_file(import_path)
            
            # Validate imported configuration
            errors = imported_config.validate()
            if errors:
                logger.warning(f"Imported configuration has validation errors: {errors}")
                
                if imported_config.auto_fix_common_issues:
                    fixes = imported_config.apply_fixes()
                    logger.info(f"Applied fixes to imported configuration: {fixes}")
            
            # Replace current configuration
            self.config = imported_config
            self.save()
            
            logger.info(f"Configuration imported from {import_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import configuration from {import_path}", e)
            return False


# Global configuration manager instance
config_manager = ConfigManager()

# Convenience functions for easy access
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return config_manager.get(key, default)

def set_config(key: str, value: Any) -> bool:
    """Set configuration value"""
    return config_manager.set(key, value)

def save_config() -> bool:
    """Save configuration"""
    return config_manager.save()

def get_display_settings() -> Dict[str, Any]:
    """Get display-related settings"""
    return config_manager.config.get_display_settings()

def get_performance_settings() -> Dict[str, Any]:
    """Get performance-related settings"""
    return config_manager.config.get_performance_settings()

def get_logging_settings() -> Dict[str, Any]:
    """Get logging-related settings"""
    return config_manager.config.get_logging_settings()
