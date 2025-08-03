# Streamlit Cloud API Key Configuration Guide

## Problem
Your Streamlit Cloud app shows "API key not configured" warnings because API keys aren't being loaded from environment variables in the cloud environment.

## Solution: Configure Streamlit Secrets

### Step 1: Access Your Streamlit Cloud Dashboard
1. Go to https://share.streamlit.io/
2. Find your "Redactor" app
3. Click on your app to open its details
4. Click the **"Settings"** button (gear icon) 
5. Navigate to the **"Secrets"** tab

### Step 2: Add Your API Keys
Copy and paste this template into the Secrets section, replacing with your actual API keys:

```toml
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"
ANTHROPIC_API_KEY = "sk-ant-your-actual-anthropic-api-key-here"
DEFAULT_MODEL = "gpt-4o-mini"
```

### Step 3: Save and Redeploy
1. Click **"Save"** in the Secrets section
2. Your app will automatically redeploy
3. Wait for the deployment to complete (usually 1-2 minutes)

### Step 4: Verify Configuration
After redeployment, your app should show:
- ✅ "OpenAI API Key loaded from environment/secrets"
- ✅ "Claude API Key loaded from environment/secrets" 
- No more warning messages in the System Status sidebar

## Getting Your API Keys

### OpenAI API Key
1. Go to https://platform.openai.com/account/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with "sk-")
4. Add it to Streamlit secrets as `OPENAI_API_KEY`

### Anthropic Claude API Key
1. Go to https://console.anthropic.com/
2. Navigate to "API Keys" section
3. Click "Create Key"
4. Copy the key (starts with "sk-ant-")
5. Add it to Streamlit secrets as `ANTHROPIC_API_KEY`

## Important Notes

- **Never commit API keys to your Git repository**
- The `.env` file is only for local development
- Streamlit Cloud uses the Secrets section for secure configuration
- Changes to secrets trigger an automatic redeployment
- You can override keys in the UI if needed for testing

## Troubleshooting

If you still see warnings after configuration:
1. Double-check that your keys are correctly formatted
2. Ensure there are no extra spaces or quotes in the secrets
3. Wait for the full redeployment to complete
4. Refresh your browser and check the System Status sidebar

Your app should now work perfectly with both OpenAI and Claude APIs!
