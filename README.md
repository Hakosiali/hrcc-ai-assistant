# HRCC AI Assistant

**AI-powered legal and HR compliance assistant specializing in Algerian labor law and HR compliance.**

🌐 **[Try it Live on Streamlit Cloud](https://hrcc-ai-assistant.streamlit.app)**  
🔗 **GitHub:** [Hakosiali/hrcc-ai-assistant](https://github.com/Hakosiali/hrcc-ai-assistant)

## ✨ Features

- 🤖 **AI Chat Assistant** - Ask questions about HR and Algerian labor law
- 📄 **Report Generation** - Create CNAS audit reports, HR compliance summaries, training sheets
- 📊 **Analytics Dashboard** - Track usage and interactions
- 📥 **PDF Export** - Download generated reports as PDF
- 🌍 **Multilingual Support** - French, Arabic, English
- ⚡ **Fast & Free** - Runs on Streamlit Cloud with no server costs
- 🔒 **Secure** - No authentication required (but can be added)

## 🚀 Quick Start

### Option 1: Use the Web App (Easiest!)

Visit: **[HRCC AI Assistant Live](https://hrcc-ai-assistant.streamlit.app)**

No installation needed! Just start asking questions.

### Option 2: Run Locally

**Requirements:** Python 3.8+

```bash
# Clone the repository
git clone https://github.com/Hakosiali/hrcc-ai-assistant.git
cd hrcc-ai-assistant

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`

## 📤 Deploy to Streamlit Cloud

Already deployed! But if you want to deploy your own fork:

1. **Fork this repository** on GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click **"New app"**
4. Select your fork:
   - Repository: `YOUR_USERNAME/hrcc-ai-assistant`
   - Branch: `main`
   - Main file: `app.py`
5. Click **"Deploy"** ✅

Your app will be live in ~2 minutes!

## 📋 Usage Guide

### 💬 Chat Tab
- Ask questions about Algerian labor law
- Supports French, Arabic, English
- Select different knowledge bases (default, knowledge, simple)
- Chat history displays last 5 conversations

### 📄 Reports Tab
- **CNAS Audit Report** - Compliance audit report
- **HR Compliance Summary** - HR policy compliance
- **Training Sheet** - Training documentation
- Generate PDF for download
- Optional: Email reports (requires email configuration)

### 📊 Analytics Tab
- View usage statistics
- Monitor queries and reports
- Download audit logs

## ⚙️ Configuration

### Environment Variables (Optional)

Create `.env` in project root:
```env
HUGGINGFACE_TOKEN=your_token_here
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
```

### For Streamlit Cloud

In app settings, add Secrets:
```toml
HUGGINGFACE_TOKEN = "your_token"
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASS = "your_password"
```

See [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example) for template.

## 📁 Project Structure

```
hrcc-ai-assistant/
├── app.py                 # Main Streamlit app
├── requirements.txt       # Python dependencies
├── .streamlit/
│   ├── config.toml       # Streamlit configuration
│   └── secrets.toml.example  # Secrets template
├── storage/              # Knowledge base storage (optional)
├── src/
│   └── report_generator.py  # Report generation logic
└── README.md            # This file
```

## 📚 Knowledge Base

The app can work with different knowledge bases:
- **default** - General HR knowledge
- **knowledge** - Algerian labor law documents
- **simple** - Simplified content
- **client1/client2** - Client-specific knowledge

To add your own knowledge base:
1. Create a `storage/your_client/` directory
2. Use `src/index.py` to build the index
3. Select it from the sidebar

## 🔒 Security

- ✅ No authentication required (easy access)
- ✅ No data saved by default
- ✅ Runs client-side (chat not stored on server)
- ⚠️ For production: Add authentication using `streamlit-authenticator`

## 🐛 Troubleshooting

**Issue: "Storage directory not found"**
- App runs in demo mode
- Add knowledge base to `storage/` folder to enable full functionality

**Issue: Models not loading**
- First load may take 2-3 minutes
- Check Streamlit Cloud logs
- May require more RAM - upgrade plan if needed

**Issue: Slow responses**
- Models are running on CPU
- Upgrade Streamlit plan for better performance
- Or use lighter models

## 📦 Dependencies

- **streamlit** - Web UI framework
- **llama-index** - LLM indexing & querying
- **transformers** - ML models
- **fpdf2** - PDF generation
- **pandas** - Data processing

See [requirements.txt](requirements.txt) for full list.

## 📄 License

MIT License - feel free to use, modify, and distribute!

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📞 Support

- 📧 Email: [Create an issue](https://github.com/Hakosiali/hrcc-ai-assistant/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Hakosiali/hrcc-ai-assistant/discussions)
- 🐛 Report bugs: [GitHub Issues](https://github.com/Hakosiali/hrcc-ai-assistant/issues)

- Credentials stored in YAML config (not in code)
- Email validation
- Response content validation
- Role-based access control
- Audit logging

## Production Ready

✅ Security fixes applied
✅ No hardcoded credentials  
✅ Proper error handling
✅ Clean architecture