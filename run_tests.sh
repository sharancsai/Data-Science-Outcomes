#!/bin/bash

# AWS Learning Agent - Test Runner Script
# This script runs the complete test suite for the AWS Learning Agent

set -e  # Exit on any error

echo "🧪 AWS Learning Agent - Test Suite Runner"
echo "=========================================="

# Check if we're in the correct directory
if [[ ! -f "requirements.txt" || ! -d "agent" ]]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python and pip
if ! command_exists python3; then
    echo "❌ Error: Python 3 is required but not installed"
    exit 1
fi

if ! command_exists pip; then
    echo "❌ Error: pip is required but not installed"
    exit 1
fi

# Install test dependencies if needed
echo "📦 Installing test dependencies..."
pip install pytest pytest-asyncio pytest-cov black flake8 > /dev/null 2>&1
echo "✅ Test dependencies installed"

# Create logs directory if it doesn't exist
mkdir -p logs

# Run linting checks
echo ""
echo "🔍 Running code quality checks..."

echo "  → Running Black formatter check..."
if command_exists black; then
    if black --check . --exclude="/(\.git|\.venv|venv|__pycache__|\.pytest_cache)/" > /dev/null 2>&1; then
        echo "    ✅ Code formatting is good"
    else
        echo "    ⚠️  Code formatting issues found. Run 'black .' to fix"
    fi
else
    echo "    ⏭️  Black not available, skipping formatting check"
fi

echo "  → Running Flake8 linter..."
if command_exists flake8; then
    if flake8 . --exclude=.git,__pycache__,.pytest_cache,venv,.venv --max-line-length=100 --ignore=E203,W503 > /dev/null 2>&1; then
        echo "    ✅ Linting passed"
    else
        echo "    ⚠️  Linting issues found:"
        flake8 . --exclude=.git,__pycache__,.pytest_cache,venv,.venv --max-line-length=100 --ignore=E203,W503 | head -10
    fi
else
    echo "    ⏭️  Flake8 not available, skipping linting check"
fi

# Run unit tests
echo ""
echo "🧪 Running unit tests..."

# Create a temporary test environment
export PYTHONPATH="$(pwd):$PYTHONPATH"
export TESTING=1

# Run tests with coverage
pytest tests/ -v --tb=short --cov=agent --cov=configs --cov-report=term-missing --cov-report=html:htmlcov

TEST_EXIT_CODE=$?

# Test results summary
echo ""
echo "📊 Test Results Summary"
echo "======================="

if [[ $TEST_EXIT_CODE -eq 0 ]]; then
    echo "✅ All tests passed successfully!"
else
    echo "❌ Some tests failed (exit code: $TEST_EXIT_CODE)"
fi

# Check test coverage
if [[ -f "htmlcov/index.html" ]]; then
    echo "📈 Test coverage report generated: htmlcov/index.html"
fi

# Additional checks for production readiness
echo ""
echo "🔧 Additional Production Readiness Checks"
echo "========================================="

# Check for required files
required_files=("README.md" "requirements.txt" "docker/Dockerfile" ".env.example")
missing_files=()

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file exists"
    else
        echo "❌ Missing required file: $file"
        missing_files+=("$file")
    fi
done

# Check for required directories
required_dirs=("agent" "configs" "docs" "tests" "docker")
missing_dirs=()

for dir in "${required_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        echo "✅ Directory $dir exists"
    else
        echo "❌ Missing required directory: $dir"
        missing_dirs+=("$dir")
    fi
done

# Configuration validation
echo ""
echo "⚙️  Configuration Validation"
echo "============================="

if python -c "from configs.config import get_config; config = get_config(); print('✅ Configuration loads successfully')" 2>/dev/null; then
    echo "✅ Configuration is valid"
else
    echo "❌ Configuration validation failed"
fi

# Import validation
echo ""
echo "📥 Import Validation"
echo "==================="

python_imports=(
    "agent"
    "configs.config"
    "agent.core_agent"
    "agent.memory_manager"
    "agent.feedback_collector"
    "agent.knowledge_base"
)

for module in "${python_imports[@]}"; do
    if python -c "import $module" 2>/dev/null; then
        echo "✅ Can import $module"
    else
        echo "❌ Cannot import $module"
    fi
done

# Performance quick check
echo ""
echo "⚡ Performance Quick Check"
echo "========================="

echo "Testing agent initialization time..."
start_time=$(date +%s%N)
python -c "
from agent import AWSLearningAgent
from unittest.mock import Mock, patch

# Mock the model initialization to avoid loading actual models
with patch.object(AWSLearningAgent, '_initialize_model', return_value=Mock()):
    agent = AWSLearningAgent()
print('Agent initialization completed')
" 2>/dev/null

end_time=$(date +%s%N)
duration_ms=$(( (end_time - start_time) / 1000000 ))

if [[ $duration_ms -lt 5000 ]]; then
    echo "✅ Agent initialization: ${duration_ms}ms (Good)"
elif [[ $duration_ms -lt 10000 ]]; then
    echo "⚠️  Agent initialization: ${duration_ms}ms (Acceptable)"
else
    echo "❌ Agent initialization: ${duration_ms}ms (Slow - consider optimization)"
fi

# Final summary
echo ""
echo "🎯 Final Summary"
echo "==============="

total_issues=0

if [[ $TEST_EXIT_CODE -ne 0 ]]; then
    echo "❌ Test failures detected"
    ((total_issues++))
fi

if [[ ${#missing_files[@]} -gt 0 ]]; then
    echo "❌ Missing required files: ${missing_files[*]}"
    ((total_issues++))
fi

if [[ ${#missing_dirs[@]} -gt 0 ]]; then
    echo "❌ Missing required directories: ${missing_dirs[*]}"
    ((total_issues++))
fi

if [[ $total_issues -eq 0 ]]; then
    echo ""
    echo "🎉 All checks passed! The AWS Learning Agent is ready for deployment."
    echo ""
    echo "Next steps:"
    echo "  • Review the test coverage report in htmlcov/index.html"
    echo "  • Run 'python api_server.py' to start the API server"
    echo "  • Run 'streamlit run streamlit_app.py' to start the web UI"
    echo "  • Check the deployment documentation in docs/deployment.md"
    exit 0
else
    echo ""
    echo "⚠️  Found $total_issues issue(s) that should be addressed before deployment."
    echo ""
    echo "Please fix the issues above and run the tests again."
    exit 1
fi