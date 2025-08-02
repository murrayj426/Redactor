"""
Enhanced error handling and logging utilities
"""
import logging
import traceback
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps
from dataclasses import dataclass
from enum import Enum

class ErrorType(Enum):
    """Error categories for better handling"""
    RATE_LIMIT = "rate_limit"
    TOKEN_LIMIT = "token_limit" 
    API_ERROR = "api_error"
    FILE_ERROR = "file_error"
    VALIDATION_ERROR = "validation_error"
    NETWORK_ERROR = "network_error"

@dataclass
class ErrorContext:
    """Context information for errors"""
    error_type: ErrorType
    message: str
    details: Dict[str, Any]
    timestamp: float
    function_name: str
    suggested_action: Optional[str] = None

class SmartErrorHandler:
    """Intelligent error handler with recovery suggestions"""
    
    def __init__(self):
        self.error_history: Dict[str, list] = {}
        self.recovery_strategies = {
            ErrorType.RATE_LIMIT: self._handle_rate_limit,
            ErrorType.TOKEN_LIMIT: self._handle_token_limit,
            ErrorType.API_ERROR: self._handle_api_error,
            ErrorType.FILE_ERROR: self._handle_file_error,
            ErrorType.NETWORK_ERROR: self._handle_network_error
        }
    
    def classify_error(self, error: Exception) -> ErrorType:
        """Classify error type from exception"""
        error_str = str(error).lower()
        
        if any(term in error_str for term in ['rate limit', 'too many requests', '429']):
            return ErrorType.RATE_LIMIT
        elif any(term in error_str for term in ['token', 'context length', 'too large']):
            return ErrorType.TOKEN_LIMIT
        elif any(term in error_str for term in ['api', '400', '401', '403', '500']):
            return ErrorType.API_ERROR
        elif any(term in error_str for term in ['file not found', 'permission denied']):
            return ErrorType.FILE_ERROR
        elif any(term in error_str for term in ['connection', 'timeout', 'network']):
            return ErrorType.NETWORK_ERROR
        else:
            return ErrorType.VALIDATION_ERROR
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorContext:
        """Handle error with intelligent recovery suggestions"""
        context = context or {}
        error_type = self.classify_error(error)
        
        error_context = ErrorContext(
            error_type=error_type,
            message=str(error),
            details=context,
            timestamp=time.time(),
            function_name=context.get('function_name', 'unknown')
        )
        
        # Apply recovery strategy
        if error_type in self.recovery_strategies:
            error_context.suggested_action = self.recovery_strategies[error_type](error, context)
        
        # Track error history
        function_name = error_context.function_name
        if function_name not in self.error_history:
            self.error_history[function_name] = []
        
        self.error_history[function_name].append(error_context)
        
        return error_context
    
    def _handle_rate_limit(self, error: Exception, context: Dict[str, Any]) -> str:
        """Suggest rate limit recovery"""
        model = context.get('model', 'unknown')
        if model == 'gpt-4':
            return "Switch to gpt-4o-mini for higher rate limits"
        elif 'gpt' in model:
            return "Wait 60 seconds and retry, or switch to gpt-3.5-turbo"
        else:
            return "Wait 60 seconds before retrying"
    
    def _handle_token_limit(self, error: Exception, context: Dict[str, Any]) -> str:
        """Suggest token limit recovery"""
        return "Reduce input text size or switch to a model with larger context window"
    
    def _handle_api_error(self, error: Exception, context: Dict[str, Any]) -> str:
        """Suggest API error recovery"""
        if '401' in str(error):
            return "Check API key configuration"
        elif '403' in str(error):
            return "Verify API permissions and quota"
        else:
            return "Check API service status and retry"
    
    def _handle_file_error(self, error: Exception, context: Dict[str, Any]) -> str:
        """Suggest file error recovery"""
        if 'not found' in str(error).lower():
            return "Check file path and ensure file exists"
        else:
            return "Verify file permissions and disk space"
    
    def _handle_network_error(self, error: Exception, context: Dict[str, Any]) -> str:
        """Suggest network error recovery"""
        return "Check internet connection and retry"

# Global error handler instance
_error_handler = SmartErrorHandler()

def smart_error_handler(func: Callable = None, *, retry_count: int = 2, delay: float = 1.0):
    """Decorator for intelligent error handling with retries"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(retry_count + 1):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    
                    # Handle the error
                    context = {
                        'function_name': f.__name__,
                        'attempt': attempt + 1,
                        'max_attempts': retry_count + 1,
                        'args': str(args)[:100],  # Limit args length
                        'kwargs': {k: str(v)[:50] for k, v in kwargs.items()}
                    }
                    
                    error_context = _error_handler.handle_error(e, context)
                    
                    # Log the error
                    logging.error(f"Error in {f.__name__}: {error_context.message}")
                    logging.error(f"Suggested action: {error_context.suggested_action}")
                    
                    # Don't retry on certain error types
                    if error_context.error_type in [ErrorType.VALIDATION_ERROR, ErrorType.FILE_ERROR]:
                        break
                    
                    # Wait before retry (exponential backoff)
                    if attempt < retry_count:
                        wait_time = delay * (2 ** attempt)
                        logging.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
            
            # All retries failed
            raise last_error
        
        return wrapper
    
    if func is None:
        return decorator
    else:
        return decorator(func)

def setup_logging(level: str = "INFO", log_file: str = None):
    """Setup enhanced logging configuration"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Setup file handler if specified
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True
    )

class PerformanceMonitor:
    """Monitor function performance and identify bottlenecks"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
    
    def record_execution(self, function_name: str, duration: float, success: bool = True):
        """Record function execution metrics"""
        if function_name not in self.metrics:
            self.metrics[function_name] = []
        
        self.metrics[function_name].append({
            'duration': duration,
            'success': success,
            'timestamp': time.time()
        })
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all monitored functions"""
        summary = {}
        
        for func_name, executions in self.metrics.items():
            durations = [e['duration'] for e in executions if e['success']]
            failures = [e for e in executions if not e['success']]
            
            if durations:
                summary[func_name] = {
                    'total_calls': len(executions),
                    'successful_calls': len(durations),
                    'failed_calls': len(failures),
                    'avg_duration': sum(durations) / len(durations),
                    'max_duration': max(durations),
                    'min_duration': min(durations),
                    'success_rate': len(durations) / len(executions) * 100
                }
        
        return summary

# Global performance monitor
_performance_monitor = PerformanceMonitor()

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            raise
        finally:
            duration = time.time() - start_time
            _performance_monitor.record_execution(func.__name__, duration, success)
    
    return wrapper

def get_performance_report() -> Dict[str, Any]:
    """Get current performance report"""
    return _performance_monitor.get_performance_summary()
