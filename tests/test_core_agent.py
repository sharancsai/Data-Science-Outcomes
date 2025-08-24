"""
Tests for the core AWS Learning Agent functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from agent.core_agent import AWSLearningAgent


class TestAWSLearningAgent:
    """Test suite for the core AWS Learning Agent."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, test_config, mock_llm):
        """Test that the agent initializes correctly."""
        with patch('agent.core_agent.get_config', return_value=test_config):
            with patch.object(AWSLearningAgent, '_initialize_model', return_value=mock_llm):
                agent = AWSLearningAgent()
                
                assert agent is not None
                assert agent.config == test_config
                assert agent.llm == mock_llm
                assert agent.memory_manager is not None
                assert agent.feedback_collector is not None
                assert agent.knowledge_base is not None

    @pytest.mark.asyncio
    async def test_process_student_input_basic(self, mock_agent, sample_student_data):
        """Test basic student input processing."""
        student_id = sample_student_data["student_id"]
        input_text = sample_student_data["input_text"]
        
        response = await mock_agent.process_student_input(student_id, input_text)
        
        assert isinstance(response, dict)
        assert "response" in response
        assert "student_id" in response
        assert "timestamp" in response
        assert response["student_id"] == student_id
        assert len(response["response"]) > 0

    @pytest.mark.asyncio
    async def test_process_student_input_with_memory(self, mock_agent, sample_student_data):
        """Test that student input processing uses memory correctly."""
        student_id = sample_student_data["student_id"]
        
        # Mock memory manager to return previous interactions
        mock_agent.memory_manager.get_student_memory = AsyncMock(return_value=[
            {
                "input": "Previous question about S3",
                "response": "Previous response about S3", 
                "timestamp": datetime.utcnow().isoformat()
            }
        ])
        
        mock_agent.memory_manager.save_interaction = AsyncMock(return_value=True)
        
        response = await mock_agent.process_student_input(student_id, "Follow up question")
        
        # Verify memory was accessed and saved
        mock_agent.memory_manager.get_student_memory.assert_called_once_with(student_id)
        mock_agent.memory_manager.save_interaction.assert_called_once()
        
        assert response["student_id"] == student_id

    @pytest.mark.asyncio
    async def test_process_student_input_error_handling(self, mock_agent):
        """Test error handling in student input processing."""
        # Make the agent throw an exception
        mock_agent.agent.ainvoke = AsyncMock(side_effect=Exception("Test error"))
        
        response = await mock_agent.process_student_input("test_student", "test input")
        
        assert "response" in response
        assert "error" in response["response"].lower()
        assert "timestamp" in response

    @pytest.mark.asyncio
    async def test_collect_feedback(self, mock_agent, sample_student_data):
        """Test feedback collection functionality."""
        mock_agent.feedback_collector.save_feedback = AsyncMock(return_value=True)
        
        result = await mock_agent.collect_feedback(
            student_id=sample_student_data["student_id"],
            session_id=sample_student_data["session_id"],
            rating=sample_student_data["rating"],
            comments=sample_student_data["comments"]
        )
        
        assert result is True
        mock_agent.feedback_collector.save_feedback.assert_called_once()

    def test_get_agent_stats(self, mock_agent):
        """Test agent statistics retrieval."""
        # Mock memory manager stats
        mock_agent.memory_manager.get_total_interactions = Mock(return_value=42)
        mock_agent.knowledge_base.get_all_topics = Mock(return_value=["EC2", "S3", "VPC"])
        
        stats = mock_agent.get_agent_stats()
        
        assert isinstance(stats, dict)
        assert "model_type" in stats
        assert "total_interactions" in stats
        assert "knowledge_base_size" in stats
        assert stats["total_interactions"] == 42
        assert stats["knowledge_base_size"] == 3

    def test_initialize_model_ollama(self, test_config):
        """Test Ollama model initialization."""
        test_config.model_type = "ollama"
        test_config.model_name = "llama3.2"
        test_config.ollama_base_url = "http://localhost:11434"
        
        with patch('agent.core_agent.get_config', return_value=test_config):
            with patch('agent.core_agent.ChatOllama') as mock_ollama:
                agent = AWSLearningAgent()
                agent._initialize_model()
                
                mock_ollama.assert_called_once_with(
                    model=test_config.model_name,
                    base_url=test_config.ollama_base_url,
                    temperature=0.7
                )

    def test_initialize_model_huggingface(self, test_config):
        """Test Hugging Face model initialization."""
        test_config.model_type = "huggingface"
        test_config.huggingface_model_name = "microsoft/DialoGPT-medium"
        
        with patch('agent.core_agent.get_config', return_value=test_config):
            with patch('agent.core_agent.HuggingFacePipeline') as mock_pipeline:
                with patch('agent.core_agent.ChatHuggingFace') as mock_chat:
                    agent = AWSLearningAgent()
                    agent._initialize_model()
                    
                    mock_pipeline.from_model_id.assert_called_once()
                    mock_chat.assert_called_once()

    def test_initialize_model_invalid_type(self, test_config):
        """Test initialization with invalid model type."""
        test_config.model_type = "invalid_model_type"
        
        with patch('agent.core_agent.get_config', return_value=test_config):
            agent = AWSLearningAgent()
            
            with pytest.raises(ValueError, match="Unsupported model type"):
                agent._initialize_model()

    def test_create_tools(self, mock_agent):
        """Test that agent tools are created correctly."""
        tools = mock_agent._create_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "aws_knowledge_search",
            "get_lab_guidance", 
            "check_progress",
            "provide_feedback",
            "simulate_aws_scenario"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    def test_check_progress_tool(self, mock_agent):
        """Test the check_progress tool function."""
        student_id = "test_student"
        progress_info = mock_agent._check_progress(student_id)
        
        assert isinstance(progress_info, str)
        assert student_id in progress_info
        assert "labs" in progress_info.lower() or "progress" in progress_info.lower()

    def test_provide_feedback_tool(self, mock_agent):
        """Test the provide_feedback tool function."""
        context = "Student struggling with VPC concepts"
        feedback = mock_agent._provide_feedback(context)
        
        assert isinstance(feedback, str)
        assert len(feedback) > 0

    def test_simulate_scenario_tool(self, mock_agent):
        """Test the simulate_scenario tool function."""
        # Test known scenario
        ec2_result = mock_agent._simulate_scenario("ec2_launch")
        assert "EC2" in ec2_result
        assert "launch" in ec2_result.lower()
        
        # Test unknown scenario
        unknown_result = mock_agent._simulate_scenario("unknown_scenario")
        assert "not available" in unknown_result.lower()
        assert "Available scenarios" in unknown_result

    @pytest.mark.asyncio
    async def test_agent_conversation_flow(self, mock_agent, sample_student_data):
        """Test a complete conversation flow with the agent."""
        student_id = sample_student_data["student_id"]
        
        # Mock the memory and feedback systems
        mock_agent.memory_manager.get_student_memory = AsyncMock(return_value=[])
        mock_agent.memory_manager.save_interaction = AsyncMock(return_value=True)
        
        # Simulate a series of interactions
        questions = [
            "What is AWS?",
            "How do I create an S3 bucket?",
            "What are the steps for launching an EC2 instance?"
        ]
        
        responses = []
        for question in questions:
            response = await mock_agent.process_student_input(student_id, question)
            responses.append(response)
            
            # Verify each response
            assert "response" in response
            assert response["student_id"] == student_id
            assert "timestamp" in response
        
        # Verify all interactions were saved
        assert mock_agent.memory_manager.save_interaction.call_count == len(questions)

    def test_agent_with_different_configurations(self, test_config):
        """Test agent behavior with different configurations."""
        configurations = [
            {"model_type": "ollama", "model_name": "llama3.2"},
            {"model_type": "huggingface", "model_name": "microsoft/DialoGPT-medium"},
        ]
        
        for config_updates in configurations:
            # Update test config
            for key, value in config_updates.items():
                setattr(test_config, key, value)
            
            with patch('agent.core_agent.get_config', return_value=test_config):
                with patch.object(AWSLearningAgent, '_initialize_model'):
                    agent = AWSLearningAgent()
                    
                    assert agent.config.model_type == config_updates["model_type"]
                    assert agent.config.model_name == config_updates["model_name"]

class TestAWSLearningAgentIntegration:
    """Integration tests for the AWS Learning Agent."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_learning_session(self, mock_agent, sample_student_data):
        """Test a complete learning session from start to finish."""
        student_id = sample_student_data["student_id"]
        session_id = sample_student_data["session_id"]
        
        # Mock all dependencies
        mock_agent.memory_manager.get_student_memory = AsyncMock(return_value=[])
        mock_agent.memory_manager.save_interaction = AsyncMock(return_value=True)
        mock_agent.feedback_collector.save_feedback = AsyncMock(return_value=True)
        
        # Step 1: Initial question
        response1 = await mock_agent.process_student_input(
            student_id, "I'm new to AWS. Where should I start?"
        )
        assert "response" in response1
        
        # Step 2: Follow-up question
        response2 = await mock_agent.process_student_input(
            student_id, "Tell me more about EC2"
        )
        assert "response" in response2
        
        # Step 3: Collect feedback
        feedback_result = await mock_agent.collect_feedback(
            student_id=student_id,
            session_id=session_id,
            rating=4,
            comments="Very helpful!"
        )
        assert feedback_result is True
        
        # Verify all systems were engaged
        assert mock_agent.memory_manager.save_interaction.call_count == 2
        mock_agent.feedback_collector.save_feedback.assert_called_once()

    @pytest.mark.asyncio 
    async def test_agent_resilience_to_failures(self, mock_agent):
        """Test that the agent handles various failure scenarios gracefully."""
        student_id = "resilience_test_student"
        
        # Test memory failure
        mock_agent.memory_manager.get_student_memory = AsyncMock(
            side_effect=Exception("Memory system failure")
        )
        mock_agent.memory_manager.save_interaction = AsyncMock(return_value=False)
        
        # Agent should still respond despite memory issues
        response = await mock_agent.process_student_input(student_id, "Test question")
        assert "response" in response
        assert response["student_id"] == student_id
        
        # Test feedback system failure
        mock_agent.feedback_collector.save_feedback = AsyncMock(return_value=False)
        
        feedback_result = await mock_agent.collect_feedback(
            student_id=student_id,
            session_id="test_session",
            rating=3,
            comments="Test feedback"
        )
        # Should return False but not crash
        assert feedback_result is False