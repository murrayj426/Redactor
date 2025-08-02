# 📁 Project Structure

## 🚀 Production Files (Main Application)
```
├── gui.py                              # Primary Streamlit web interface
├── main.py                             # Command-line entry point  
├── pdf_parser.py                       # Smart redaction engine
├── claude_auditor.py                   # Claude 3.5 Sonnet AI auditing
├── openai_auditor.py                   # OpenAI GPT auditing
├── requirements.txt                    # Python dependencies
├── run_redactor.sh                     # Shell launcher script
└── .env.example                        # Environment template
```

## 📚 Documentation & Configuration
```
├── README.md                           # Comprehensive project documentation
├── incident_handling_procedures.txt    # Network Team procedures (core)
├── incident_handling_procedures_full.txt # Complete procedures (reference)
├── LOCAL_AI_SETUP.md                   # Local AI setup instructions
└── .streamlit/config.toml              # Streamlit configuration
```

## 📊 Reports & Output
```
└── reports/                            # Generated audit reports and redacted content
    ├── claude_*_audit_*.txt           # Claude audit reports
    ├── network_team_*.txt             # Network team audit reports
    └── redacted_output.txt            # Redacted content output
```

## 🔧 Development Files (Moved to /development/)
```
└── development/
    ├── test_*.py                      # All test files for validation
    ├── chat_auditor.py                # Early chat-based auditor
    ├── cli_auditor.py                 # Command line auditor variant
    ├── docx_processor.py              # Word document processor
    ├── interactive_*.py               # Interactive interface variants
    ├── simple_chat.py                 # Simple chat interface
    ├── step_by_step_*.py              # Step-by-step variants
    └── cleanup_analysis.md            # This cleanup analysis
```

## 🎯 Core Dependencies
- **Streamlit**: Web interface framework
- **Anthropic**: Claude 3.5 Sonnet API  
- **OpenAI**: GPT model API
- **pdfplumber**: PDF text extraction
- **python-dotenv**: Environment management
- **regex**: Advanced pattern matching

## 🚀 Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Launch web interface
streamlit run gui.py
```
