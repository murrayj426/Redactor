import openai
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Import base auditor and optimization utilities
from base_auditor import BaseAuditor
from utils.error_handling import smart_error_handler, monitor_performance
from utils.ai_utils import optimize_prompt_for_model

# Load environment variables
load_dotenv()

class TicketAuditor(BaseAuditor):
    def __init__(self):
        super().__init__()
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    @smart_error_handler(retry_count=3, delay=2.0)
    @monitor_performance
    def audit_ticket(self, redacted_text, model="gpt-4o-mini"):
        """Send redacted text to OpenAI for auditing using Network Team standards"""
        
        # Apply rate limiting
        model_rates = {'gpt-4': 10, 'gpt-4o-mini': 500, 'gpt-3.5-turbo': 3500}
        rpm_limit = model_rates.get(model, 10)
        self.rate_limiter.wait_if_needed(model, rpm_limit)
        
        # Optimize prompt for token limits
        prompt = self.create_audit_prompt(redacted_text)
        optimization = optimize_prompt_for_model(prompt, model)
        
        if optimization['truncated']:
            print(f"⚠️ Prompt truncated for {model}: {optimization['reason']}")
            prompt = optimization['optimized_prompt']
        elif optimization['model_suggestion'] != model:
            print(f"💡 Suggesting {optimization['model_suggestion']} instead of {model} for better performance")
            model = optimization['model_suggestion']
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a Network Team incident auditor. Provide concise, structured audit responses."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        # Log API response for debugging
        print("OpenAI API Full Response:", response)
        print("DEBUG: audit_ticket method called with prompt:", prompt)

        # Extract and process the text attribute from the response
        audit_results = []
        if response.choices:
            for choice in response.choices:
                if hasattr(choice.message, 'content'):
                    audit_results.append(choice.message.content)
                else:
                    print(f"⚠️ Skipping choice without 'content' attribute: {choice}")

        if audit_results:
            return "\n\n".join(audit_results)
        else:
            raise ValueError("Unexpected response structure: No valid content found")
    
    def get_available_models(self):
        """Get list of available OpenAI models"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data if 'gpt' in model.id]
        except:
            return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
