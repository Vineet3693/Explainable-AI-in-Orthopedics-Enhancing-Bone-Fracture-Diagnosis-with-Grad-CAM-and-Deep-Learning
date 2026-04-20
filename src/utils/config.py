"""
Configuration Management Utility

PURPOSE:
    Centralized configuration loading and management for the entire project.
    Supports YAML configs with environment variable overrides.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to main config file (default: configs/config.yaml)
        """
        if config_path is None:
            config_path = 'configs/config.yaml'
        
        self.config_path = config_path
        self.config = self.load_config(config_path)
    
    def load_config(self, path: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        try:
            with open(path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded config from {path}")
            return config or {}
        except FileNotFoundError:
            logger.warning(f"Config file not found: {path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with dot notation support
        
        Args:
            key: Config key (supports dot notation: 'model.architecture')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        # Check for environment variable override
        env_key = key.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, path: Optional[str] = None):
        """Save configuration to file"""
        if path is None:
            path = self.config_path
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
        
        logger.info(f"Saved config to {path}")


# Global config instance
_config = None

def get_config(config_path: Optional[str] = None) -> Config:
    """Get global config instance"""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config


__all__ = ['Config', 'get_config']
