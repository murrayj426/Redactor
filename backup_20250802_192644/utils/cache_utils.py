"""
Cache utilities for file loading and AI responses
"""
import os
import hashlib
import json
import time
from typing import Dict, Any, Optional
from functools import wraps

class FileCache:
    """Simple file-based cache for procedures and other static content"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_file_hash(self, filepath: str) -> str:
        """Get MD5 hash of file for cache invalidation"""
        if not os.path.exists(filepath):
            return ""
        
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """Get cache file path for key"""
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def get(self, key: str, source_file: str = None) -> Optional[str]:
        """Get cached content if still valid"""
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Check if source file has changed
            if source_file and os.path.exists(source_file):
                current_hash = self._get_file_hash(source_file)
                if cache_data.get('source_hash') != current_hash:
                    return None
            
            # Check expiry (24 hours default)
            if time.time() - cache_data.get('timestamp', 0) > 86400:
                return None
            
            return cache_data.get('content')
        
        except (json.JSONDecodeError, KeyError):
            return None
    
    def set(self, key: str, content: str, source_file: str = None):
        """Cache content with metadata"""
        cache_path = self._get_cache_path(key)
        
        cache_data = {
            'content': content,
            'timestamp': time.time(),
            'source_hash': self._get_file_hash(source_file) if source_file else None
        }
        
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)

# Global cache instance
_file_cache = FileCache()

def cached_file_load(cache_key: str = None):
    """Decorator to cache file loading operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and args
            key = cache_key or f"{func.__name__}_{hash(str(args))}"
            
            # Try to get from cache first
            cached_result = _file_cache.get(key)
            if cached_result is not None:
                return cached_result
            
            # Load file and cache result
            result = func(*args, **kwargs)
            if result:
                _file_cache.set(key, result)
            
            return result
        return wrapper
    return decorator

@cached_file_load("network_procedures")
def load_network_procedures() -> str:
    """Load network team procedures with caching"""
    try:
        with open('incident_handling_procedures.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        # Try alternative locations
        for alt_path in ['incident_handling_procedures_full.txt', 'docs/procedures.txt']:
            try:
                with open(alt_path, 'r') as f:
                    return f.read()
            except FileNotFoundError:
                continue
        return "Network Team procedures file not found."

class ResponseCache:
    """Cache AI responses to avoid duplicate API calls"""
    
    def __init__(self, max_age_hours: int = 24):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_age = max_age_hours * 3600
    
    def _generate_key(self, text: str, audit_type: str, model: str) -> str:
        """Generate cache key from request parameters"""
        content = f"{text[:500]}_{audit_type}_{model}"  # Use first 500 chars
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, text: str, audit_type: str, model: str) -> Optional[str]:
        """Get cached response if available and not expired"""
        key = self._generate_key(text, audit_type, model)
        
        if key in self.cache:
            cache_entry = self.cache[key]
            if time.time() - cache_entry['timestamp'] < self.max_age:
                return cache_entry['response']
            else:
                # Clean expired entry
                del self.cache[key]
        
        return None
    
    def set(self, text: str, audit_type: str, model: str, response: str):
        """Cache response"""
        key = self._generate_key(text, audit_type, model)
        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
    
    def clear_expired(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items() 
            if current_time - entry['timestamp'] > self.max_age
        ]
        
        for key in expired_keys:
            del self.cache[key]

# Global response cache
_response_cache = ResponseCache()

def cached_ai_response(func):
    """Decorator to cache AI API responses"""
    @wraps(func)
    def wrapper(self, text: str, audit_type: str = "general", model: str = "gpt-4o-mini"):
        # Check cache first
        cached_response = _response_cache.get(text, audit_type, model)
        if cached_response:
            return cached_response
        
        # Make API call
        response = func(self, text, audit_type, model)
        
        # Cache successful responses
        if response and not any(error in response.lower() for error in ['error', 'failed', 'rate limit']):
            _response_cache.set(text, audit_type, model, response)
        
        return response
    
    return wrapper
