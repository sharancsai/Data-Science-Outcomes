# AWS Learning Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

An intelligent agentic assistant for AWS learner lab integration, designed to provide guided learning experiences, real-time interaction, and adaptive feedback for students learning Amazon Web Services.

## 🚀 Features

- **🤖 Intelligent Agent**: LangChain-powered AI assistant with AWS expertise
- **🔄 Multiple Model Support**: Both Ollama (local) and Hugging Face (cloud) integration
- **🧠 Memory System**: Persistent learning from student interactions
- **📊 Progress Tracking**: Comprehensive learning progress analytics
- **💬 Real-time Interaction**: Interactive chat interface with lab guidance
- **🐳 Easy Deployment**: Docker, Codespaces, and Colab ready
- **🎯 Adaptive Learning**: Feedback-driven continuous improvement

## 🏗️ Architecture

```
├── agent/                     # Core agentic agent implementation
│   ├── core_agent.py         # Main agent with LangChain
│   ├── memory_manager.py     # Persistent memory system
│   ├── feedback_collector.py # Student feedback analysis
│   └── knowledge_base.py     # AWS learning content
├── notebooks/                # Google Colab ready notebooks
├── configs/                  # Configuration management
├── docs/                     # Comprehensive documentation
├── data/                     # AWS learning content & knowledge base
├── tests/                    # Testing framework
├── docker/                   # Container configurations
├── api_server.py             # FastAPI REST API
└── streamlit_app.py          # Web UI interface
```

## 🚀 Quick Start

### Option 1: Google Colab (Recommended for beginners)

1. Open the notebook in Google Colab:
   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sharancsai/Data-Science-Outcomes/blob/main/notebooks/AWS_Learning_Agent_Colab.ipynb)

2. Run all cells to set up the environment
3. Start chatting with the AWS Learning Agent!

### Option 2: GitHub Codespaces

1. Click "Code" → "Codespaces" → "Create codespace on main"
2. Wait for the environment to set up automatically
3. Run: `python api_server.py` to start the API
4. Run: `streamlit run streamlit_app.py` to start the UI
5. Access the interfaces through forwarded ports

### Option 3: Docker (Local deployment)

```bash
# Clone the repository
git clone https://github.com/sharancsai/Data-Science-Outcomes.git
cd Data-Science-Outcomes

# Start with Docker Compose
docker-compose -f docker/docker-compose.yml up --build

# Access the interfaces
# API: http://localhost:8000
# UI: http://localhost:8501
```

### Option 4: Local development

```bash
# Clone and setup
git clone https://github.com/sharancsai/Data-Science-Outcomes.git
cd Data-Science-Outcomes

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Start the API server
python api_server.py

# Start the web UI (in another terminal)
streamlit run streamlit_app.py
```

## 🎓 For Educators

### Setting up for your students:

1. **Classroom Deployment**: Use the Docker setup for consistent environments
2. **Individual Access**: Share the Colab notebook link for immediate access
3. **Development Learning**: Use Codespaces for advanced students

### Configuration Options:

```bash
# For local models (requires powerful hardware)
MODEL_TYPE=ollama
MODEL_NAME=llama3.2

# For cloud deployment (free tier)
MODEL_TYPE=huggingface
MODEL_NAME=microsoft/DialoGPT-medium
```

## 🧪 Example Usage

### Chat Interface

```python
from agent import AWSLearningAgent

# Initialize the agent
agent = AWSLearningAgent()

# Start learning
response = agent.process_student_input(
    student_id="student123",
    input_text="How do I launch an EC2 instance?"
)

print(response["response"])
```

### API Usage

```bash
# Chat with the agent
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"student_id": "student123", "message": "What is Amazon S3?"}'

# Get lab guidance
curl -X POST "http://localhost:8000/lab-guidance" \
     -H "Content-Type: application/json" \
     -d '{"lab_name": "ec2_basic"}'
```

## 📚 Available AWS Labs

- **EC2 Basics**: Launch and manage virtual servers
- **S3 Fundamentals**: Object storage and bucket management
- **VPC Setup**: Virtual private cloud configuration
- **Lambda Introduction**: Serverless computing basics
- **RDS Basics**: Managed database setup

## 🛠️ Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
python -m pytest tests/ -v
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📖 Documentation

- [Setup Guide for Educators](docs/educator-setup.md)
- [Student Interaction Guide](docs/student-guide.md)
- [Deployment Instructions](docs/deployment.md)
- [API Reference](docs/api-reference.md)
- [Configuration Guide](docs/configuration.md)

## 🔧 Technical Requirements

### Minimum Requirements
- Python 3.11+
- 4GB RAM
- 2GB disk space
- Internet connection for cloud models

### Recommended for Local Models
- Python 3.11+
- 16GB RAM
- GPU with 8GB VRAM (for Ollama)
- 10GB disk space

## 🤝 Support

- **Issues**: Report bugs via [GitHub Issues](https://github.com/sharancsai/Data-Science-Outcomes/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/sharancsai/Data-Science-Outcomes/discussions)
- **Documentation**: Check the [docs](docs/) folder

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) for agent framework
- Uses [Hugging Face](https://huggingface.co/) for free cloud models
- Powered by [Ollama](https://ollama.ai/) for local deployment
- UI built with [Streamlit](https://streamlit.io/)
- API powered by [FastAPI](https://fastapi.tiangolo.com/)

## 🌟 Star the Project!

If this project helped you learn AWS, please give it a star ⭐ to help others discover it!

---

**Made with ❤️ for AWS learners worldwide**