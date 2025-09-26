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
from utils.ai_utils import optimize_prompt_for_model, TokenManager

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
        token_manager = TokenManager()
        prompt = self.create_audit_prompt(redacted_text)
        prompt_tokens = token_manager.count_tokens(prompt, model)
        reserved_output = 220 * 13 + 300  # heuristic expected output size
        self.rate_limiter.consume(model, prompt_tokens, reserved_output)
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
        
        # Log the entire response and its attributes for debugging
        print("Claude API Full Response:", response)
        print("Response Attributes:", dir(response))
        
        # Ensure response logging is visible
        print("DEBUG: audit_ticket method called with prompt:", prompt)
        print("DEBUG: Claude API response:", response)
        
        # Log the type of the content objects for debugging
        print("DEBUG: Type of response.content[0]:", type(response.content[0]))
        print("DEBUG: Attributes of response.content[0]:", dir(response.content[0]))

        # Extract and process the text attribute from the response
        audit_results = []
        if response.content:
            for block in response.content:
                if isinstance(block, anthropic.types.text_block.TextBlock) and hasattr(block, 'text'):
                    audit_results.append(block.text)
                else:
                    print(f"⚠️ Skipping non-TextBlock or missing 'text' attribute in block: {block}")

        if audit_results:
            full_text = "\n\n".join(audit_results)
            parsed = self.parse_json_summary(full_text)
            if parsed:
                print(f"Parsed JSON summary: {parsed}")
            return full_text
        else:
            raise ValueError("Unexpected response structure: No valid text blocks found")

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
