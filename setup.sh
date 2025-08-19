#!/bin/bash

# AWS Learning Agent - Quick Setup Script
# This script helps educators and developers set up the AWS Learning Agent quickly

set -e

echo "🚀 AWS Learning Agent - Quick Setup"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check system requirements
echo "🔍 Checking system requirements..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python $PYTHON_VERSION found"
else
    print_error "Python 3.11+ is required but not found"
    exit 1
fi

# Check pip
if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
    print_status "pip found"
else
    print_error "pip is required but not found"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "requirements.txt" || ! -d "agent" ]]; then
    print_error "Please run this script from the AWS Learning Agent project root"
    exit 1
fi

# Ask user for setup type
echo ""
echo "📋 Setup Options"
echo "=================="
echo "1. Quick Setup (Recommended for beginners)"
echo "2. Development Setup (For developers)"
echo "3. Production Setup (For deployment)"
echo ""

while true; do
    read -p "Choose setup type (1-3): " setup_type
    case $setup_type in
        1) 
            echo "🎯 Quick Setup selected"
            break;;
        2) 
            echo "🛠️  Development Setup selected"
            break;;
        3) 
            echo "🏭 Production Setup selected"
            break;;
        *) 
            print_warning "Please choose 1, 2, or 3";;
    esac
done

# Create virtual environment (optional but recommended)
echo ""
read -p "Create virtual environment? (y/n) [recommended]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
    
    print_info "Activating virtual environment..."
    source venv/bin/activate
    print_status "Virtual environment activated"
fi

# Install dependencies
echo ""
print_info "Installing dependencies..."

if [[ $setup_type == "2" ]]; then
    # Development dependencies
    pip install -r requirements.txt
    pip install pytest pytest-asyncio pytest-cov black flake8 jupyter
    print_status "Development dependencies installed"
else
    # Basic dependencies
    pip install -r requirements.txt
    print_status "Dependencies installed"
fi

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p data/aws_content data/knowledge_base data/feedback data/memory logs
print_status "Directories created"

# Set up configuration
echo ""
print_info "Setting up configuration..."

if [[ ! -f ".env" ]]; then
    cp .env.example .env
    print_status "Environment configuration created (.env)"
    
    echo ""
    echo "📝 Configuration Setup"
    echo "======================="
    
    # Ask for model preference
    echo "Choose AI model type:"
    echo "1. Hugging Face (Free, cloud-based, recommended for beginners)"
    echo "2. Ollama (Local, requires powerful hardware)"
    
    while true; do
        read -p "Choose model type (1-2): " model_choice
        case $model_choice in
            1)
                sed -i 's/MODEL_TYPE=.*/MODEL_TYPE=huggingface/' .env
                sed -i 's/MODEL_NAME=.*/MODEL_NAME=microsoft\/DialoGPT-medium/' .env
                print_status "Configured for Hugging Face model"
                break;;
            2)
                sed -i 's/MODEL_TYPE=.*/MODEL_TYPE=ollama/' .env
                sed -i 's/MODEL_NAME=.*/MODEL_NAME=llama3.2/' .env
                print_status "Configured for Ollama model"
                print_warning "Make sure Ollama is installed and running"
                break;;
            *)
                print_warning "Please choose 1 or 2";;
        esac
    done
else
    print_info "Configuration file already exists"
fi

# Initialize the database and knowledge base
print_info "Initializing database and knowledge base..."
python -c "
from configs.config import setup_directories
setup_directories()
print('✅ Database and knowledge base initialized')
"
print_status "Database initialized"

# Setup-specific additional steps
if [[ $setup_type == "2" ]]; then
    # Development setup
    print_info "Setting up development environment..."
    
    # Pre-commit hooks (if git repo)
    if [[ -d ".git" ]]; then
        pip install pre-commit
        echo "
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100, --ignore=E203,W503]
" > .pre-commit-config.yaml
        pre-commit install
        print_status "Git pre-commit hooks installed"
    fi
    
elif [[ $setup_type == "3" ]]; then
    # Production setup
    print_info "Configuring for production..."
    
    # Update environment for production
    sed -i 's/ENVIRONMENT=.*/ENVIRONMENT=production/' .env
    sed -i 's/LOG_LEVEL=.*/LOG_LEVEL=INFO/' .env
    
    print_status "Production configuration applied"
    print_warning "Remember to configure proper secrets and database for production"
fi

# Test the installation
echo ""
print_info "Testing installation..."

if python -c "
import sys
sys.path.append('.')
from agent import AWSLearningAgent
from configs.config import get_config
from unittest.mock import Mock, patch

# Test configuration loading
config = get_config()
print('✅ Configuration loads successfully')

# Test agent initialization (with mocked model to avoid loading issues)
with patch.object(AWSLearningAgent, '_initialize_model', return_value=Mock()):
    agent = AWSLearningAgent()
    print('✅ Agent initializes successfully')

print('✅ All components load successfully')
" 2>/dev/null; then
    print_status "Installation test passed"
else
    print_error "Installation test failed"
    print_info "Check the error messages above"
    exit 1
fi

# Docker setup (if requested)
echo ""
read -p "Set up Docker containers? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        print_info "Building Docker containers..."
        docker-compose -f docker/docker-compose.yml build --no-cache
        print_status "Docker containers built successfully"
        
        print_info "You can now run: docker-compose -f docker/docker-compose.yml up"
    else
        print_warning "Docker and/or Docker Compose not found. Skipping Docker setup."
        print_info "Install Docker to use containerized deployment"
    fi
fi

# Final instructions
echo ""
echo "🎉 Setup Complete!"
echo "=================="

print_status "AWS Learning Agent is ready to use!"

echo ""
echo "📚 Next Steps:"
echo "=============="

if [[ $setup_type == "1" ]]; then
    echo "Quick Start:"
    echo "1. Start the API server:"
    echo "   python api_server.py"
    echo ""
    echo "2. In another terminal, start the web UI:"
    echo "   streamlit run streamlit_app.py"
    echo ""
    echo "3. Open your browser and go to:"
    echo "   • API: http://localhost:8000"
    echo "   • UI: http://localhost:8501"
    echo ""
    echo "4. Try the Google Colab notebook for an easy start:"
    echo "   • Open: notebooks/AWS_Learning_Agent_Colab.ipynb in Google Colab"

elif [[ $setup_type == "2" ]]; then
    echo "Development:"
    echo "1. Run tests:"
    echo "   ./run_tests.sh"
    echo ""
    echo "2. Start development servers:"
    echo "   python api_server.py    # API server"
    echo "   streamlit run streamlit_app.py  # Web UI"
    echo ""
    echo "3. Code formatting:"
    echo "   black .                 # Format code"
    echo "   flake8 .               # Check linting"
    echo ""
    echo "4. Check documentation in docs/ folder"

else
    echo "Production Deployment:"
    echo "1. Review and update .env configuration"
    echo "2. Set up proper database (PostgreSQL recommended)"
    echo "3. Configure HTTPS/TLS certificates"
    echo "4. Use Docker for deployment:"
    echo "   docker-compose -f docker/docker-compose.yml up -d"
    echo ""
    echo "5. Check docs/deployment.md for detailed instructions"
fi

echo ""
echo "📖 Documentation:"
echo "• Educator Setup Guide: docs/educator-setup.md"
echo "• Student Guide: docs/student-guide.md"
echo "• Deployment Guide: docs/deployment.md"
echo ""

echo "🆘 Need Help?"
echo "• Check the documentation in the docs/ folder"
echo "• Report issues: https://github.com/sharancsai/Data-Science-Outcomes/issues"

echo ""
print_status "Happy Learning! ☁️✨"