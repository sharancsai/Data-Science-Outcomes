"""
Test configuration and fixtures for the AWS Learning Agent test suite.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import sqlite3
import os

# Import our modules
from agent.core_agent import AWSLearningAgent
from agent.memory_manager import MemoryManager
from agent.feedback_collector import FeedbackCollector
from agent.knowledge_base import AWSKnowledgeBase
from configs.config import AgentConfig

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def test_config(temp_dir):
    """Create a test configuration."""
    config = AgentConfig(
        model_type="test",
        model_name="test-model",
        database_url=f"sqlite:///{temp_dir}/test.db",
        aws_content_path=f"{temp_dir}/aws_content",
        knowledge_base_path=f"{temp_dir}/knowledge_base",
        log_file=f"{temp_dir}/test.log",
        max_memory_size=10  # Small for testing
    )
    
    # Create necessary directories
    Path(config.aws_content_path).mkdir(parents=True, exist_ok=True)
    Path(config.knowledge_base_path).mkdir(parents=True, exist_ok=True)
    Path(config.log_file).parent.mkdir(parents=True, exist_ok=True)
    
    return config

@pytest.fixture
def mock_llm():
    """Create a mock language model."""
    mock = Mock()
    mock.invoke = Mock(return_value="This is a test response from the mock LLM")
    mock.ainvoke = AsyncMock(return_value="This is a test async response from the mock LLM")
    return mock

@pytest.fixture
def memory_manager(test_config):
    """Create a MemoryManager instance for testing."""
    # Patch the global config
    import configs.config
    original_config = configs.config.config
    configs.config.config = test_config
    
    try:
        manager = MemoryManager()
        yield manager
    finally:
        # Restore original config
        configs.config.config = original_config

@pytest.fixture
def feedback_collector(test_config):
    """Create a FeedbackCollector instance for testing."""
    import configs.config
    original_config = configs.config.config
    configs.config.config = test_config
    
    try:
        collector = FeedbackCollector()
        yield collector
    finally:
        configs.config.config = original_config

@pytest.fixture
def knowledge_base(test_config):
    """Create a KnowledgeBase instance for testing."""
    import configs.config
    original_config = configs.config.config
    configs.config.config = test_config
    
    try:
        kb = AWSKnowledgeBase()
        yield kb
    finally:
        configs.config.config = original_config

@pytest.fixture
def mock_agent(test_config, mock_llm):
    """Create a mock AWS Learning Agent for testing."""
    import configs.config
    original_config = configs.config.config
    configs.config.config = test_config
    
    try:
        # Create agent with mocked components
        agent = AWSLearningAgent()
        agent.llm = mock_llm
        agent.agent = Mock()
        agent.agent.ainvoke = AsyncMock(return_value={"output": "Mock agent response"})
        yield agent
    finally:
        configs.config.config = original_config

@pytest.fixture
def sample_student_data():
    """Sample student data for testing."""
    return {
        "student_id": "test_student_123",
        "session_id": "test_session_456",
        "input_text": "What is Amazon EC2?",
        "response": "Amazon EC2 is a web service that provides secure, resizable compute capacity in the cloud.",
        "rating": 4,
        "comments": "Very helpful explanation!",
        "feedback_type": "general"
    }

@pytest.fixture
def sample_aws_services():
    """Sample AWS services data for testing knowledge base."""
    return {
        "Amazon EC2": {
            "description": "Virtual servers in the cloud",
            "keywords": ["compute", "server", "instance"],
            "use_cases": ["Web hosting", "Application development"]
        },
        "Amazon S3": {
            "description": "Object storage service", 
            "keywords": ["storage", "bucket", "object"],
            "use_cases": ["Data backup", "Static website hosting"]
        }
    }

@pytest.mark.asyncio
async def pytest_configure(config):
    """Configure pytest for async tests."""
    pass

class MockDatabase:
    """Mock database for testing without actual SQLite."""
    
    def __init__(self):
        self.data = {}
        self.tables = set()
    
    def execute(self, query, params=None):
        # Simple mock implementation
        if "CREATE TABLE" in query:
            # Extract table name and add to tables set
            pass
        elif "INSERT INTO" in query:
            # Mock insert operation
            pass
        elif "SELECT" in query:
            # Mock select operation
            return []
        return Mock()
    
    def commit(self):
        pass
    
    def close(self):
        pass

@pytest.fixture
def mock_database():
    """Create a mock database for testing."""
    return MockDatabase()

# Utility functions for tests

def create_test_database(db_path):
    """Create a test SQLite database with sample data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE student_memory (
            id INTEGER PRIMARY KEY,
            student_id TEXT NOT NULL,
            session_id TEXT,
            input_text TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            context TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE student_feedback (
            id INTEGER PRIMARY KEY,
            student_id TEXT NOT NULL,
            session_id TEXT,
            rating INTEGER NOT NULL,
            comments TEXT,
            feedback_type TEXT DEFAULT 'general',
            timestamp DATETIME NOT NULL,
            context TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    
    return db_path

def assert_aws_response_quality(response):
    """Assert that a response meets AWS learning quality standards."""
    assert len(response) > 10, "Response should be substantial"
    assert any(keyword in response.lower() for keyword in ['aws', 'amazon', 'cloud']), \
        "Response should be AWS-related"
    assert not any(inappropriate in response.lower() for inappropriate in ['error', 'failed', 'broken']), \
        "Response should not contain error messages"

def assert_valid_student_id(student_id):
    """Assert that student ID is in valid format."""
    assert isinstance(student_id, str), "Student ID should be string"
    assert len(student_id) > 0, "Student ID should not be empty"
    assert len(student_id) < 100, "Student ID should be reasonable length"