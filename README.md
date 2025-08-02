# 📄 PDF Redactor & AI Auditor

An intelligent PDF redaction and ticket auditing tool that automatically removes sensitive information and uses OpenAI to perform comprehensive ticket audits.

## 🚀 Features

### 🔒 **Smart Redaction**
- IP addresses → `[REDACTED IP]`
- MAC addresses → `[REDACTED MAC]`
- Phone numbers → `[REDACTED PHONE]`
- Email addresses → `[REDACTED EMAIL]`
- Employee IDs → `[REDACTED EMPLOYEE ID]`
- IMEI numbers → `IMEI#[REDACTED]`
- Account numbers → `Account [REDACTED]`
- URLs → `[REDACTED URL]`
- Names → "John Smith" becomes "John S."

### 🤖 **AI-Powered Auditing**
- **General Audit**: Issue resolution quality, response time, communication
- **Security Audit**: Incident classification, containment, compliance
- **Performance Audit**: SLA adherence, efficiency metrics, customer satisfaction

### 🎯 **Multiple Interfaces**
- **Web GUI**: User-friendly Streamlit interface
- **Command Line**: Batch processing and automation
- **Shell Script**: Quick GUI launcher

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Redactor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Get your OpenAI API Key**
   - Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Create a new API key
   - Add it to your `.env` file

## 🎮 Usage

### Web Interface
```bash
streamlit run gui.py
```

### Command Line

**Basic redaction only:**
```bash
python main.py document.pdf
```

**Redaction + AI audit:**
```bash
python main.py document.pdf --audit
```

**Specific audit type:**
```bash
python main.py document.pdf --audit --audit-type security
```

**Custom model:**
```bash
python main.py document.pdf --audit --model gpt-3.5-turbo
```

### Shell Script (GUI)
```bash
./run_redactor.sh
```

## 📁 Output Files

- **Redacted text**: `reports/redacted_output.txt`
- **Audit reports**: `reports/[audit_type]_audit_[timestamp].txt`

## 🛡️ Security

- Sensitive data is redacted before sending to OpenAI
- API keys stored in environment variables
- `.env` file excluded from version control
- All audit reports saved locally

## 🔧 Configuration

Edit `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
DEFAULT_MODEL=gpt-4
DEFAULT_AUDIT_TYPE=general
```

## 📊 Audit Types

| Type | Focus Areas |
|------|-------------|
| **General** | Issue resolution, response time, communication, process adherence |
| **Security** | Incident classification, containment, compliance, documentation |
| **Performance** | SLA metrics, efficiency, customer satisfaction, technical accuracy |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This tool is designed to redact common sensitive information patterns. Always review redacted content before sharing. The AI audit is for assistance only and should not replace human oversight for critical decisions.
