"""
Configuration loader for topics and sources.

Loads topics.yaml and provides access to topic configurations.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class ConfigLoader:
    """
    Loads and provides access to topic configurations.
    
    Usage:
        config = ConfigLoader()
        topics = config.get_topics()
        for topic_id, topic_config in topics.items():
            print(topic_config['name'])
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config loader.
        
        Args:
            config_path: Path to topics.yaml. If None, uses default location.
        """
        if config_path is None:
            # Default: config/topics.yaml relative to project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / 'config' / 'topics.yaml'
        
        self.config_path = Path(config_path)
        self._config = None
    
    def _load(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if self._config is None:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Config file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        
        return self._config
    
    def get_topics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all topic configurations.
        
        Returns:
            Dict mapping topic_id to topic config
        """
        config = self._load()
        return config.get('topics', {})
    
    def get_topic(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific topic.
        
        Args:
            topic_id: Topic identifier (e.g., 'tech', 'ai', 'design')
        
        Returns:
            Topic configuration dict or None if not found
        """
        topics = self.get_topics()
        return topics.get(topic_id)
    
    def get_topic_ids(self) -> List[str]:
        """Get list of all topic IDs"""
        return list(self.get_topics().keys())
    
    def get_settings(self) -> Dict[str, Any]:
        """Get global settings"""
        config = self._load()
        return config.get('settings', {})
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        settings = self.get_settings()
        return settings.get(key, default)


# Singleton instance for convenience
_config_loader: Optional[ConfigLoader] = None


def get_config() -> ConfigLoader:
    """Get the global config loader instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader
