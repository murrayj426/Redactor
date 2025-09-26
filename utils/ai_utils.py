"""
AI utilities for token management and rate limiting
"""
import time
import tiktoken
from typing import Dict, Any, Optional, Deque, Tuple
from collections import deque
import os

class TokenManager:
    """Manage AI API tokens and rate limiting"""
    
    def __init__(self):
        self.encoders = {}
        self.rate_limits = {
            'gpt-4': {'rpm': 10, 'tpm': 10000},
            'gpt-4o-mini': {'rpm': 500, 'tpm': 200000},
            'gpt-3.5-turbo': {'rpm': 3500, 'tpm': 90000},
            'claude-3-5-sonnet-20241022': {'rpm': 50, 'tpm': 40000}
        }
        self.request_history = []
    
    def get_encoder(self, model: str):
        """Get or create token encoder for model"""
        if model not in self.encoders:
            # Use gpt-4 encoder as fallback for Claude
            encoder_model = model if 'gpt' in model else 'gpt-4'
            try:
                self.encoders[model] = tiktoken.encoding_for_model(encoder_model)
            except KeyError:
                self.encoders[model] = tiktoken.get_encoding('cl100k_base')
        return self.encoders[model]
    
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text for specific model"""
        encoder = self.get_encoder(model)
        return len(encoder.encode(text))
    
    def check_token_limit(self, text: str, model: str, max_tokens: int = None) -> Dict[str, Any]:
        """Check if text exceeds token limits"""
        token_count = self.count_tokens(text, model)
        limit = max_tokens or self.rate_limits.get(model, {}).get('tpm', 8000)
        
        return {
            'token_count': token_count,
            'limit': limit,
            'within_limit': token_count <= limit,
            'percentage': (token_count / limit) * 100 if limit > 0 else 100
        }
    
    def truncate_text(self, text: str, model: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit"""
        encoder = self.get_encoder(model)
        tokens = encoder.encode(text)
        
        if len(tokens) <= max_tokens:
            return text
        
        # Truncate from middle to preserve start and end context
        start_tokens = tokens[:max_tokens//2]
        end_tokens = tokens[-(max_tokens//2):]
        
        truncated_text = encoder.decode(start_tokens) + "\n\n[...TRUNCATED...]\n\n" + encoder.decode(end_tokens)
        return truncated_text
    
    def suggest_cheaper_model(self, current_model: str) -> Optional[str]:
        """Suggest a cheaper model if rate limited"""
        model_hierarchy = [
            'gpt-4',
            'gpt-4o-mini', 
            'gpt-3.5-turbo'
        ]
        
        try:
            current_index = model_hierarchy.index(current_model)
            if current_index < len(model_hierarchy) - 1:
                return model_hierarchy[current_index + 1]
        except ValueError:
            pass
        
        return 'gpt-4o-mini'  # Default fallback

class RateLimiter:
    """Token + request aware rate limiter (sliding 60s window)."""

    def __init__(self):
        # model -> deque[(timestamp, tokens)]
        self.history: Dict[str, Deque[Tuple[float, int]]] = {}
        self.token_manager = TokenManager()

    def _limits_for(self, model: str) -> Tuple[int, int]:
        rl = self.token_manager.rate_limits.get(model, {})
        # Environment overrides allow tuning without code change
        rpm = int(os.getenv(f"{model.upper().replace('-','_')}_RPM", rl.get('rpm', 10)))
        tpm = int(os.getenv(f"{model.upper().replace('-','_')}_TPM", rl.get('tpm', 8000)))
        return rpm, tpm

    def consume(self, model: str, request_tokens: int, response_tokens_reserved: int = 0):
        """Block until sending this request fits within RPM & TPM budgets.

        request_tokens: tokens in prompt
        response_tokens_reserved: conservative expected output tokens (buffer)
        """
        if model not in self.history:
            self.history[model] = deque()
        window = self.history[model]
        rpm_limit, tpm_limit = self._limits_for(model)

        now = time.time()
        cutoff = now - 60
        while window and window[0][0] < cutoff:
            window.popleft()

        total_needed = request_tokens + response_tokens_reserved
        if total_needed > tpm_limit:
            print(f"⚠️ Request size {total_needed} tokens exceeds TPM limit {tpm_limit} for {model}. Consider further compression.")

        def usage():
            return len(window), sum(t for _, t in window)

        # Wait loop until both RPM & TPM satisfied
        while True:
            req_count, tok_sum = usage()
            over_rpm = req_count >= rpm_limit
            over_tpm = (tok_sum + total_needed) > tpm_limit
            if not over_rpm and not over_tpm:
                break
            oldest_ts, _ = window[0]
            sleep_for = max(0.01, 60 - (time.time() - oldest_ts))
            time.sleep(min(sleep_for, 5))
            now = time.time()
            cutoff = now - 60
            while window and window[0][0] < cutoff:
                window.popleft()

        window.append((time.time(), total_needed))

    def estimate_budget(self, model: str) -> Dict[str, Any]:
        rpm_limit, tpm_limit = self._limits_for(model)
        if model not in self.history:
            return {'rpm_used': 0, 'tpm_used': 0, 'rpm_limit': rpm_limit, 'tpm_limit': tpm_limit, 'tpm_remaining_est': tpm_limit}
        window = self.history[model]
        cutoff = time.time() - 60
        while window and window[0][0] < cutoff:
            window.popleft()
        tok_sum = sum(t for _, t in window)
        return {
            'rpm_used': len(window),
            'tpm_used': tok_sum,
            'rpm_limit': rpm_limit,
            'tpm_limit': tpm_limit,
            'tpm_remaining_est': max(tpm_limit - tok_sum, 0)
        }

def optimize_prompt_for_model(prompt: str, model: str) -> Dict[str, Any]:
    """Optimize prompt based on model capabilities"""
    token_manager = TokenManager()
    
    # Check token limits
    token_info = token_manager.check_token_limit(prompt, model)
    
    optimization_result = {
        'original_tokens': token_info['token_count'],
        'optimized_prompt': prompt,
        'model_suggestion': model,
        'truncated': False
    }
    
    # If over limit, try to optimize
    if not token_info['within_limit']:
        if model == 'gpt-4':
            # Suggest cheaper model
            cheaper_model = token_manager.suggest_cheaper_model(model)
            optimization_result['model_suggestion'] = cheaper_model
            optimization_result['reason'] = 'Token limit exceeded, suggested cheaper model'
        else:
            # Truncate text
            max_tokens = int(token_info['limit'] * 0.8)  # Leave buffer
            optimized_prompt = token_manager.truncate_text(prompt, model, max_tokens)
            optimization_result['optimized_prompt'] = optimized_prompt
            optimization_result['truncated'] = True
            optimization_result['reason'] = 'Text truncated to fit token limit'
    
    return optimization_result
