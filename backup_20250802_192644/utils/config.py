"""
Configuration management for the redactor application
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

@dataclass
class RedactionConfig:
    """Configuration for redaction settings"""
    max_pages: Optional[int] = None
    batch_size: int = 50
    preserve_business_terms: bool = True
    enable_statistics: bool = True
    patterns: Dict[str, str] = field(default_factory=lambda: {
        'ip_addresses': r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        'mac_addresses': r"(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}",
        'phone_numbers': r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",
        'email_addresses': r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        'employee_ids': r"EVE\d{8}",
        'imei_numbers': r"IMEI[#\s]*\d+",
        'account_numbers': r"Account\s+\d{8,}(-\d+)?",
        'urls': r"https?://\S+"
    })

@dataclass 
class AIConfig:
    """Configuration for AI providers"""
    openai_api_key: str = field(default_factory=lambda: os.getenv('OPENAI_API_KEY', ''))
    anthropic_api_key: str = field(default_factory=lambda: os.getenv('ANTHROPIC_API_KEY', ''))
    default_model: str = field(default_factory=lambda: os.getenv('DEFAULT_MODEL', 'gpt-4o-mini'))
    max_retries: int = 3
    timeout: int = 60
    enable_caching: bool = True
    rate_limiting: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        'gpt-4': {'rpm': 10, 'tpm': 10000},
        'gpt-4o-mini': {'rpm': 500, 'tpm': 200000},
        'gpt-3.5-turbo': {'rpm': 3500, 'tpm': 90000},
        'claude-3-5-sonnet-20241022': {'rpm': 50, 'tpm': 40000}
    })

@dataclass
class AppConfig:
    """Main application configuration"""
    debug: bool = field(default_factory=lambda: os.getenv('DEBUG', 'False').lower() == 'true')
    reports_dir: str = 'reports'
    cache_dir: str = 'cache'
    procedures_file: str = 'incident_handling_procedures.txt'
    max_file_size_mb: int = 50
    enable_performance_monitoring: bool = True
    redaction: RedactionConfig = field(default_factory=RedactionConfig)
    ai: AIConfig = field(default_factory=AIConfig)

# Global configuration instance
config = AppConfig()

def get_config() -> AppConfig:
    """Get application configuration"""
    return config

def validate_config() -> Dict[str, Any]:
    """Validate configuration and return status"""
    issues = []
    warnings = []
    
    # Check API keys
    if not config.ai.openai_api_key:
        warnings.append("OpenAI API key not configured")
    
    if not config.ai.anthropic_api_key:
        warnings.append("Anthropic API key not configured") 
    
    # Check file paths
    if not os.path.exists(config.procedures_file):
        issues.append(f"Procedures file not found: {config.procedures_file}")
    
    if not os.path.exists(config.reports_dir):
        os.makedirs(config.reports_dir)
        warnings.append(f"Created reports directory: {config.reports_dir}")
    
    if config.ai.enable_caching and not os.path.exists(config.cache_dir):
        os.makedirs(config.cache_dir)
        warnings.append(f"Created cache directory: {config.cache_dir}")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings
    }

def update_config(**kwargs):
    """Update configuration values"""
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        elif hasattr(config.ai, key):
            setattr(config.ai, key, value)
        elif hasattr(config.redaction, key):
            setattr(config.redaction, key, value)
