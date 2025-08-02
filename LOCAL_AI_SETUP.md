# Local AI Setup Instructions

## Option 1: Ollama (Recommended for No Rate Limits)

### Install Ollama:
```bash
# macOS
brew install ollama

# Or download from: https://ollama.ai
```

### Install a suitable model:
```bash
# Install Llama 3.1 8B (good for auditing)
ollama pull llama3.1:8b

# Or install Code Llama for technical analysis
ollama pull codellama:13b
```

### Benefits:
- ✅ No rate limits
- ✅ No API costs
- ✅ Complete privacy (runs locally)
- ✅ Works offline

### Drawbacks:
- ❌ Requires powerful hardware (8GB+ RAM)
- ❌ Slower than OpenAI
- ❌ May need fine-tuning for best results

## Option 2: Azure OpenAI
- Higher rate limits than OpenAI directly
- Better for enterprise use
- Requires Azure subscription

## Option 3: Anthropic Claude
- Alternative to OpenAI
- Different rate limit structure
- May be more suitable for long documents

Would you like me to implement any of these alternatives?
