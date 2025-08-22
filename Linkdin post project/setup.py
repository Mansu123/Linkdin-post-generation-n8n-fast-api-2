#!/usr/bin/env python3
"""
LinkedIn Post Automation Setup Script
This script creates the complete project structure and files
"""

import os
import subprocess
import sys
from pathlib import Path

def create_directory_structure():
    """Create the project directory structure"""
    directories = [
        "linkedin-automation",
        "linkedin-automation/backend",
        "linkedin-automation/backend/services",
        "linkedin-automation/backend/models",
        "linkedin-automation/backend/config",
        "linkedin-automation/frontend",
        "linkedin-automation/tests",
        "linkedin-automation/tests/backend",
        "linkedin-automation/tests/frontend"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_init_files():
    """Create __init__.py files for Python packages"""
    init_files = [
        "linkedin-automation/backend/__init__.py",
        "linkedin-automation/backend/services/__init__.py",
        "linkedin-automation/backend/models/__init__.py",
        "linkedin-automation/backend/config/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"✅ Created: {init_file}")

def create_env_file():
    """Create .env template file"""
    env_content = """# LinkedIn Post Automation - Environment Variables
# Replace with your actual API keys and tokens

# Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key_here

# LinkedIn API Credentials
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token_here
LINKEDIN_PERSON_ID=your_linkedin_person_id_here

# Application Settings
DEBUG=False
LOG_LEVEL=INFO

# Database (if needed in future)
DATABASE_URL=sqlite:///./linkedin_automation.db
"""
    
    with open("linkedin-automation/.env", "w") as f:
        f.write(env_content)
    print("✅ Created .env template file")

def create_requirements_files():
    """Create requirements.txt for both backend and frontend"""
    backend_requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
aiohttp==3.9.1
google-generativeai==0.3.2
langchain==0.0.350
langchain-google-genai==0.0.8
torch==2.1.1
requests==2.31.0
python-multipart==0.0.6
"""

    frontend_requirements = """streamlit==1.28.1
requests==2.31.0
python-dotenv==1.0.0
pandas==2.1.4
plotly==5.17.0
"""

    with open("linkedin-automation/backend/requirements.txt", "w") as f:
        f.write(backend_requirements)
    
    with open("linkedin-automation/frontend/requirements.txt", "w") as f:
        f.write(frontend_requirements)
    
    with open("linkedin-automation/requirements.txt", "w") as f:
        f.write(backend_requirements + frontend_requirements)
    
    print("✅ Created requirements.txt files")

def create_readme():
    """Create comprehensive README.md"""
    readme_content = """# LinkedIn Post Automation System

An AI-powered system for creating and publishing LinkedIn posts using Gemini AI and LinkedIn API.

## Features

- 🤖 AI-powered content generation using Google's Gemini AI
- 📱 Professional LinkedIn post creation and publishing
- 🎨 Multiple post tones and lengths
- 📊 Modern web interface with Streamlit
- 🚀 FastAPI backend with async support
- 🐳 Docker containerization
- 🔒 Secure API key management

## Architecture

```
├── backend/                 # FastAPI backend
│   ├── services/           # Business logic services
│   ├── models/             # Pydantic data models
│   ├── config/             # Configuration management
│   └── main.py             # FastAPI application
├── frontend/               # Streamlit frontend
│   └── app.py             # Web interface
├── docker-compose.yml     # Docker configuration
└── requirements.txt       # Python dependencies
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd linkedin-automation
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env .env.local
```

Edit `.env.local` with your credentials:
```
GEMINI_API_KEY=your_gemini_api_key
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
LINKEDIN_PERSON_ID=your_linkedin_person_id
```

### 3. Installation Options

#### Option A: Docker (Recommended)

```bash
docker-compose up -d
```

#### Option B: Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

### 4. Access the Application

- **Frontend:** http://localhost:8501
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Getting LinkedIn Credentials

### LinkedIn Access Token

1. Go to [LinkedIn Developer Portal](https://developer.linkedin.com/)
2. Create a new app
3. Request access to LinkedIn Marketing Developer Platform
4. Generate access token with required scopes:
   - `r_liteprofile`
   - `r_emailaddress`
   - `w_member_social`

### LinkedIn Person ID

Use this API call to get your person ID:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
https://api.linkedin.com/v2/people/(id~)
```

## API Endpoints

### Main Endpoints

- `GET /` - Health check
- `GET /user/info` - Get LinkedIn user information
- `POST /generate-content` - Generate post content with AI
- `POST /post/create` - Create and publish LinkedIn post
- `POST /post/schedule` - Schedule post for later

### Example API Usage

```python
import requests

# Generate content
response = requests.post("http://localhost:8000/generate-content", json={
    "topic": "AI in healthcare",
    "tone": "professional",
    "length": "medium",
    "include_hashtags": True
})

content = response.json()["generated_content"]

# Publish post
response = requests.post("http://localhost:8000/post/create", json={
    "content": content
})
```

## Development

### Backend Development

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
streamlit run app.py --server.port 8501
```

### Running Tests

```bash
pytest tests/
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini AI API key | Yes |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn API access token | Yes |
| `LINKEDIN_PERSON_ID` | Your LinkedIn person ID | Yes |
| `DEBUG` | Enable debug mode | No |
| `LOG_LEVEL` | Logging level | No |

### Customization

- **Post Templates:** Modify prompts in `services/gemini_service.py`
- **UI Themes:** Customize Streamlit interface in `frontend/app.py`
- **API Models:** Update schemas in `models/schemas.py`

## Deployment

### Production Deployment

1. **Environment Setup:**
   ```bash
   cp .env.example .env.production
   # Edit with production values
   ```

2. **Docker Production:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Manual Deployment:**
   - Deploy backend to cloud service (AWS, GCP, Azure)
   - Deploy frontend to Streamlit Cloud or similar
   - Configure environment variables

### Security Considerations

- Never commit API keys to version control
- Use environment variables for all sensitive data
- Implement rate limiting in production
- Use HTTPS in production
- Regularly rotate API keys

## Troubleshooting

### Common Issues

1. **LinkedIn API Errors:**
   - Check token validity and scopes
   - Verify person ID format
   - Ensure app has proper permissions

2. **Gemini AI Errors:**
   - Verify API key is correct
   - Check quota and billing
   - Ensure proper model access

3. **Connection Issues:**
   - Check backend is running on port 8000
   - Verify frontend can reach backend
   - Check firewall settings

### Debugging

Enable debug mode:
```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
```

Check logs:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create GitHub issue
- Check existing documentation
- Review API documentation at `/docs`
"""

    with open("linkedin-automation/README.md", "w") as f:
        f.write(readme_content)
    print("✅ Created README.md")

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.env.local
.env.production
.venv
env/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Docker
.docker/

# Streamlit
.streamlit/

# Cache
.cache/
.pytest_cache/

# Coverage
.coverage
htmlcov/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json
"""

    with open("linkedin-automation/.gitignore", "w") as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore")

def create_test_files():
    """Create basic test files"""
    backend_test = """import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "LinkedIn Post Automation API" in response.json()["message"]

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
"""

    frontend_test = """import pytest
import sys
from pathlib import Path

# Add frontend to path
sys.path.append(str(Path(__file__).parent.parent / "frontend"))

def test_app_import():
    try:
        import app
        assert hasattr(app, 'main')
    except ImportError:
        pytest.fail("Cannot import frontend app")
"""

    with open("linkedin-automation/tests/backend/test_main.py", "w") as f:
        f.write(backend_test)
    
    with open("linkedin-automation/tests/frontend/test_app.py", "w") as f:
        f.write(frontend_test)
    
    with open("linkedin-automation/tests/__init__.py", "w") as f:
        f.write("")
    
    print("✅ Created test files")

def main():
    """Main setup function"""
    print("🚀 Setting up LinkedIn Post Automation project...")
    
    try:
        create_directory_structure()
        create_init_files()
        create_env_file()
        create_requirements_files()
        create_readme()
        create_gitignore()
        create_test_files()
        
        print("\n" + "="*50)
        print("✅ Project setup completed successfully!")
        print("="*50)
        print("\nNext steps:")
        print("1. cd linkedin-automation")
        print("2. Edit .env file with your API keys")
        print("3. Run: docker-compose up -d")
        print("4. Open http://localhost:8501")
        print("\nFor local development:")
        print("1. cd backend && pip install -r requirements.txt")
        print("2. python main.py (in one terminal)")
        print("3. cd frontend && streamlit run app.py (in another terminal)")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()