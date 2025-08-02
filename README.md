# � AI-Powered PDF Redactor & Network Team Compliance Auditor

An intelligent PDF redaction and compliance auditing system with **smart business term preservation** and **Claude 3.5 Sonnet AI auditing**. Built for Network Team compliance standards with personal team lead feedback.

## ✨ Key Features

### 🧠 **Intelligent Redaction System**
- **Smart Pattern Recognition**: Distinguishes between business terms and personal names
- **Business Term Preservation**: Keeps "Security Device Management", "Client Hold", etc. intact
- **Hostname Protection**: Preserves technical identifiers like "PRNFSPA-TowerFW01"
- **Comprehensive PII Removal**: IP addresses, emails, phone numbers, personal names
- **Context-Aware Logic**: Uses AI-level intelligence to avoid false positives

### 🎯 **Superior AI Auditing**
- **Claude 3.5 Sonnet Integration**: Advanced reasoning for Network Team compliance
- **Personal Team Lead Feedback**: Coaching-style notes from your manager
- **Procedure References**: Links failed assessments to specific documentation
- **15-Point Compliance Check**: Comprehensive Network Team standard validation
- **Professional Formatting**: Clean, readable audit reports with emojis and structure

### 🔒 **Privacy & Security**
- **Local Processing**: Sensitive data redacted before AI analysis
- **No Data Retention**: AI providers don't store your ticket information
- **Environment-Based Config**: Secure API key management
- **Audit Trail**: Complete logs of all redaction statistics

## � What Makes This Special

**Before**: Generic redaction that broke business terms
- "Security Device Management" → "Security D. Management" ❌

**After**: Intelligent context-aware redaction
- "Security Device Management" → "Security Device Management" ✅
- "John Smith worked on this" → "John S. worked on this" ✅

**AI Auditing Evolution**:
- Personal feedback that sounds like your team lead wrote it
- Specific procedure references when standards aren't met
- Actionable coaching instead of formal compliance language

## 📦 Quick Start

1. **Clone & Setup**
   ```bash
   git clone <your-repo-url>
   cd Redactor
   pip install -r requirements.txt
   ```

2. **Configure API Keys**
   ```bash
   cp .env.example .env
   # Add your Anthropic API key for Claude 3.5 Sonnet (recommended)
   # Or OpenAI API key for GPT models
   ```

3. **Launch the Web App**
   ```bash
   streamlit run gui.py
   ```

## 🎮 Usage Options

### 🌐 **Web Interface (Recommended)**
```bash
streamlit run gui.py
```
- Drag & drop PDF upload
- Real-time redaction preview
- Claude 3.5 Sonnet auditing
- Personal team lead feedback
- Download redacted content & audit reports

### 💻 **Command Line Interface**
```bash
# Basic redaction
python main.py document.pdf

# With AI audit
python main.py document.pdf --audit

# Specific audit type with Claude
python claude_auditor.py extracted_text.txt
```

### 🚀 **Shell Script (macOS/Linux)**
```bash
./run_redactor.sh  # Launches GUI automatically
```

## 🎯 **Audit Features**

### 📋 **15-Point Network Team Compliance Check**
1. **Incident Number** - Proper format validation
2. **CI/Location/Service Fields** - Required field completion
3. **First Access Verification** - Security compliance check
4. **Ownership Acknowledgment** - Engineer accountability
5. **Event Dates** - Follow-up scheduling
6. **Pending Codes** - Proper state management
7. **Status Updates** - Current status documentation
8. **Client Communications** - Professional messaging
9. **Troubleshooting Documentation** - Technical evidence
10. **Update Frequency** - Priority-based cadence
11. **Procedures/Templates** - Standard compliance
12. **Activity/Change Tasks** - Proper task linking
13. **Time Tracking** - Accurate billing documentation
14. **Close Notes** - Resolution evidence
15. **Overall Performance** - Comprehensive rating

### 💬 **Personal Team Lead Feedback**
- **What I Really Liked**: Positive reinforcement
- **Areas for Growth**: Coaching suggestions
- **My Overall Take**: Direct manager assessment
- **Procedure References**: Links to specific documentation

## 🔧 **API Configuration**

### Claude 3.5 Sonnet (Recommended)
```bash
# .env file
ANTHROPIC_API_KEY=your_claude_api_key
```
- Superior compliance reasoning
- Better context understanding
- More professional audit output

### OpenAI (Alternative)
```bash
# .env file  
OPENAI_API_KEY=your_openai_api_key
DEFAULT_MODEL=gpt-4
```

## 📈 **Intelligence Features**

### 🧠 **Smart Redaction Examples**
```
✅ PRESERVED: "Security Device Management" 
✅ PRESERVED: "PRNFSPA-TowerFW01"
✅ PRESERVED: "Client Hold"
✅ PRESERVED: "Network Services"
❌ REDACTED: "John Smith" → "John S."
❌ REDACTED: "555-123-4567" → "[REDACTED PHONE]"
```

### 📚 **Audit Learning System**
When engineers don't meet standards, they get:
- **Exact procedure quotes** from your documentation
- **Section references** for easy lookup  
- **Personal coaching** from team lead perspective
- **Actionable next steps** for improvement

## 📁 **Output & Reports**

- **Redacted Content**: Clean text ready for forms/sharing
- **Redaction Statistics**: Detailed metrics of what was removed
- **Audit Reports**: Professional compliance assessments
- **Procedure References**: Learning opportunities for engineers
- **Timestamped Files**: Complete audit trail

## 🌐 **Deployment Options**

### Local Development
```bash
streamlit run gui.py  # http://localhost:8502
```

### Streamlit Cloud (Recommended)
- Connect your GitHub repository
- Automatic deployment on code changes
- Free hosting for team access
- Built-in SSL and domain

### Enterprise Deployment
- Docker containerization ready
- Environment variable configuration
- Scalable for multiple teams
- Audit logging capabilities

## 🛡️ **Security & Privacy**

- **Privacy First**: All PII removed before AI processing
- **Local Processing**: Redaction happens on your machine
- **Secure APIs**: Encrypted communication with AI providers
- **No Data Storage**: AI providers don't retain your data
- **Audit Trails**: Complete logging of all operations
- **Environment Isolation**: Secure credential management

## 🎓 **For Network Team Managers**

This tool transforms compliance auditing from:
- ❌ Time-consuming manual reviews
- ❌ Inconsistent feedback quality  
- ❌ Generic compliance language
- ❌ No learning opportunities

To:
- ✅ Automated 15-point assessments
- ✅ Personal coaching feedback
- ✅ Procedure-linked learning
- ✅ Consistent quality standards

## 🔄 **Continuous Improvement**

The system learns and adapts:
- **Business term recognition** improves over time
- **Audit criteria** can be customized per team
- **Feedback language** remains coaching-focused
- **Procedure integration** keeps training current

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Test thoroughly with real Network Team data
4. Submit pull request with clear description
5. Include test cases for new redaction patterns

## 📋 **System Requirements**

- Python 3.8+
- 2GB RAM minimum (4GB recommended)
- Internet connection for AI API calls
- Modern web browser for GUI
- PDF processing libraries (auto-installed)

## ⚡ **Performance**

- **PDF Processing**: ~1-2 seconds per page
- **Smart Redaction**: ~500ms per document
- **AI Auditing**: ~10-15 seconds per ticket
- **Batch Processing**: Supports multiple files
- **Memory Efficient**: Processes large PDFs in chunks

## 🆘 **Support & Troubleshooting**

### Common Issues
- **API Key Errors**: Check `.env` file configuration
- **Import Errors**: Run `pip install -r requirements.txt`
- **PDF Issues**: Ensure PDF is text-based, not scanned
- **Performance**: Close other applications for large files

### Getting Help
- Check the issue tracker for known problems
- Include error logs and system details
- Test with sample documents first
- Verify API key permissions

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏆 **Acknowledgments**

- **Anthropic** for Claude 3.5 Sonnet's superior reasoning
- **Streamlit** for the excellent web framework
- **Network Team** for compliance standards and feedback
- **Open Source Community** for PDF processing libraries

## ⚠️ **Important Notes**

- **Review Output**: Always verify redacted content before sharing
- **AI Assistance**: Audit feedback assists human judgment, doesn't replace it
- **Compliance**: Tool helps meet standards but doesn't guarantee compliance
- **Data Handling**: Follow your organization's data governance policies
- **Updates**: Keep dependencies current for security patches
