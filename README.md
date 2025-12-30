# MaiKnit Recruitment Agent

An intelligent AI-powered recruitment assistant that analyzes resumes, evaluates candidate skills, generates interview questions, and provides actionable improvement suggestions using advanced NLP and LLM technology.

## 🚀 Features

- **Resume Analysis**: Intelligent parsing and evaluation of resume content against job requirements
- **Skill Assessment**: Deterministic scoring system that evaluates skills based on frequency and relevance
- **Interview Questions Generation**: AI-powered generation of tailored interview questions based on resume content
- **Q&A Assistant**: Interactive question-answering system for recruitment inquiries
- **Resume Improvement Suggestions**: Actionable recommendations to enhance resume quality and impact
- **Multi-Role Support**: Pre-configured roles including Software Engineer, Data Scientist, Product Manager, and more
- **Real-time Processing**: Fast, responsive feedback powered by Groq API

## 📋 Requirements

- Python 3.8+
- Groq API Key (free tier available at [groq.com](https://groq.com))
- Modern web browser for Streamlit UI

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Maithili2004/Recruitment_agent.git
cd Recruitment_agent
```

### 2. Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Local Development
```bash
streamlit run app.py
```
The application will open at `http://localhost:8501`

### Configuration
1. Get your free Groq API Key from [console.groq.com](https://console.groq.com)
2. Paste the API key in the sidebar when the app starts
3. Select your recruitment role (Software Engineer, Data Scientist, etc.)
4. Upload a resume PDF/TXT file
5. Interact with the analysis and receive insights

## 📁 Project Structure

```
├── app.py                 # Main Streamlit application
├── agents.py              # Core agent logic and LLM integration
├── ui.py                  # User interface components
├── requirements.txt       # Python dependencies
├── test_groq_api.py       # Model validation script
├── Dockerfile             # Docker container configuration
├── deploy.yml             # GitHub Actions CI/CD pipeline
└── README.md              # This file
```

## 🧠 How It Works

### Resume Analysis Pipeline
1. **Text Extraction**: Parse uploaded resume documents
2. **Skill Extraction**: Identify and extract skills mentioned in resume
3. **Scoring System**: 
   - 5+ mentions = Score 8/10 (Strong)
   - 3-4 mentions = Score 6/10 (Moderate)
   - 2 mentions = Score 4/10 (Basic)
   - 1 mention = Score 2/10 (Minimal)
   - 0 mentions = Score 1/10 (Absent)
4. **Interview Questions**: Generate role-specific interview questions
5. **Improvements**: Provide actionable suggestions for resume enhancement

### Technology Stack
- **LLM**: Groq API with `llama-3.1-8b-instant` model
- **Framework**: Streamlit 1.31.0
- **Vector Store**: FAISS 1.13.1
- **Embeddings**: Custom SimpleEmbeddings (hash-based, lightweight)
- **Language**: Python 3.8+

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -t maiknit-recruitment-agent .
```

### Run Container
```bash
docker run -p 8501:8501 maiknit-recruitment-agent
```

## 🚀 AWS Deployment with GitHub Actions

The repository includes automated CI/CD pipeline that:
1. Builds Docker image on every push to `main` branch
2. Pushes to Amazon ECR (Elastic Container Registry)
3. Deploys container to self-hosted runner
4. Configures Nginx reverse proxy
5. Automatically restarts service on updates

**Prerequisites:**
- AWS account with ECR repository
- GitHub Secrets configured: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `ECR_REPOSITORY`
- Self-hosted GitHub Actions runner


**ECR Repository URL:**
```
158311565058.dkr.ecr.eu-north-1.amazonaws.com/streamlit-apps
```

## 📊 Scoring System Details

The deterministic scoring system evaluates skills based on:
- **Frequency Analysis**: How many times skill is mentioned
- **Context Matching**: Relevance to selected job role
- **Threshold-based Classification**:
  - Strengths: Score ≥ 7/10
  - Areas for Development: Score ≤ 4/10
  - Moderate Skills: Score 5-6/10

## 🔐 Environment Variables

Create a `.env` file (optional for local development):
```
GROQ_API_KEY=your_groq_api_key_here
```

For production, use GitHub Secrets or AWS Secrets Manager.

## 📝 API Keys

### Getting Groq API Key
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up (free tier available)
3. Generate API key
4. Add to application via Streamlit sidebar

## ⚙️ Configuration

### Supported Roles
- Software Engineer
- Data Scientist
- Product Manager
- DevOps Engineer
- Machine Learning Engineer
- Full Stack Developer

Add custom roles by modifying `roles` dictionary in `agents.py`

## 🧪 Testing

### Validate Groq API Models
```bash
python test_groq_api.py
```
This script tests available Groq models and reports which ones are functional.

## 🐛 Troubleshooting

### "Groq API Error"
- Verify API key is correct and has quota remaining
- Check internet connectivity
- Ensure model `llama-3.1-8b-instant` is available in your Groq account

### "No resume uploaded"
- Ensure file is PDF or TXT format
- Maximum file size recommended: 10MB
- File should contain readable text

### "Interview questions not generating"
- Check Groq API key validity
- Verify resume has sufficient content
- Review browser console for error messages

## 📊 Performance

- Resume parsing: < 2 seconds
- Skill analysis: < 1 second
- Interview question generation: 3-5 seconds (depends on Groq API)
- Q&A response: 2-4 seconds

## 🔄 Model Information

**Current Model**: `llama-3.1-8b-instant`
- Fast inference with 8 billion parameters
- Low latency suitable for interactive applications
- Free tier available on Groq platform
- Good balance of speed and quality

## 📄 License

This project is open source. Feel free to fork, modify, and distribute.

## 👤 Author

Maithili (Maithili2004)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📞 Support

For issues, questions, or feedback:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section above

## 🔮 Future Enhancements

- Multi-document analysis (cover letters, portfolios)
- Batch resume processing
- Custom scoring weights per role
- Resume formatting suggestions
- LinkedIn profile integration
- Export analysis as PDF report
- Support for additional document formats

---

**Powered by MaiKnit** | Made with ❤️ using Streamlit and Groq API