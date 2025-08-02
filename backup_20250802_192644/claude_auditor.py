"""
Claude 3.5 Sonnet-powered Network Team Audit System
Specialized for superior compliance reasoning and procedural analysis
"""

import os
import re
from datetime import datetime
from dotenv import load_dotenv
import anthropic

# Import base auditor and optimization utilities
from base_auditor import BaseAuditor
from utils.error_handling import smart_error_handler, monitor_performance
from utils.ai_utils import optimize_prompt_for_model

# Load environment variables
load_dotenv()

class ClaudeAuditor(BaseAuditor):
    def __init__(self):
        super().__init__()
        self.client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
    
    @smart_error_handler(retry_count=3, delay=2.0)
    @monitor_performance
    def audit_ticket(self, redacted_text, model="claude-3-5-sonnet-20241022"):
        """Conduct audit using Claude 3.5 Sonnet's superior reasoning capabilities"""
        
        # Apply rate limiting
        self.rate_limiter.wait_if_needed(model, 50)  # Claude's rate limit
        
        # Optimize prompt for token limits
        prompt = self.create_audit_prompt(redacted_text)
        optimization = optimize_prompt_for_model(prompt, model)
        
        if optimization['truncated']:
            print(f"⚠️ Prompt truncated for Claude: {optimization['reason']}")
            prompt = optimization['optimized_prompt']
        
        response = self.client.messages.create(
            model=model,
            max_tokens=4000,
            temperature=0.1,  # Low temperature for consistent compliance analysis
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return response.content[0].text

# Test function for command line usage
def main():
    if len(sys.argv) != 2:
        print("Usage: python claude_auditor.py <path_to_text_file>")
        return
    
    auditor = ClaudeAuditor()
    
    with open(sys.argv[1], 'r') as f:
        ticket_text = f.read()
    
    result = auditor.audit_ticket(ticket_text)
    print(result)

if __name__ == "__main__":
    import sys
    main()
