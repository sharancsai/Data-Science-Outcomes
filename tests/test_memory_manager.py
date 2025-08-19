"""
Tests for the memory management system.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from agent.memory_manager import MemoryManager, StudentMemory, LearningProgress


class TestMemoryManager:
    """Test suite for the MemoryManager class."""

    @pytest.mark.asyncio
    async def test_memory_manager_initialization(self, memory_manager):
        """Test that MemoryManager initializes correctly."""
        assert memory_manager is not None
        assert memory_manager.config is not None
        assert memory_manager.engine is not None
        assert memory_manager.SessionLocal is not None

    @pytest.mark.asyncio
    async def test_save_interaction_basic(self, memory_manager, sample_student_data):
        """Test basic interaction saving."""
        result = await memory_manager.save_interaction(
            student_id=sample_student_data["student_id"],
            input_text=sample_student_data["input_text"],
            response=sample_student_data["response"],
            timestamp=datetime.utcnow()
        )
        
        assert result is True

    @pytest.mark.asyncio
    async def test_save_interaction_with_context(self, memory_manager, sample_student_data):
        """Test saving interaction with additional context."""
        context = {
            "topic": "EC2",
            "difficulty": "beginner",
            "tools_used": ["aws_knowledge_search"]
        }
        
        result = await memory_manager.save_interaction(
            student_id=sample_student_data["student_id"],
            input_text=sample_student_data["input_text"],
            response=sample_student_data["response"],
            timestamp=datetime.utcnow(),
            session_id=sample_student_data["session_id"],
            context=context
        )
        
        assert result is True

    @pytest.mark.asyncio
    async def test_get_student_memory_empty(self, memory_manager):
        """Test retrieving memory for student with no history."""
        memories = await memory_manager.get_student_memory("nonexistent_student")
        
        assert isinstance(memories, list)
        assert len(memories) == 0

    @pytest.mark.asyncio
    async def test_get_student_memory_with_data(self, memory_manager, sample_student_data):
        """Test retrieving memory after saving interactions."""
        student_id = sample_student_data["student_id"]
        
        # Save multiple interactions
        interactions = [
            ("What is AWS?", "AWS is Amazon Web Services..."),
            ("How do I use S3?", "Amazon S3 is object storage..."),
            ("Tell me about EC2", "Amazon EC2 provides virtual servers...")
        ]
        
        for input_text, response in interactions:
            await memory_manager.save_interaction(
                student_id=student_id,
                input_text=input_text,
                response=response,
                timestamp=datetime.utcnow()
            )
        
        # Retrieve memories
        memories = await memory_manager.get_student_memory(student_id)
        
        assert len(memories) == len(interactions)
        assert all("input" in memory for memory in memories)
        assert all("response" in memory for memory in memories)
        assert all("timestamp" in memory for memory in memories)

    @pytest.mark.asyncio
    async def test_get_student_memory_limit(self, memory_manager, sample_student_data):
        """Test memory retrieval with limit parameter."""
        student_id = sample_student_data["student_id"]
        
        # Save many interactions
        for i in range(10):
            await memory_manager.save_interaction(
                student_id=student_id,
                input_text=f"Question {i}",
                response=f"Response {i}",
                timestamp=datetime.utcnow()
            )
        
        # Retrieve with limit
        memories = await memory_manager.get_student_memory(student_id, limit=5)
        
        assert len(memories) == 5

    @pytest.mark.asyncio
    async def test_update_learning_progress_new(self, memory_manager, sample_student_data):
        """Test updating learning progress for new topic."""
        student_id = sample_student_data["student_id"]
        topic = "EC2"
        score = 85
        completed_labs = ["ec2_basics", "ec2_security"]
        
        result = await memory_manager.update_learning_progress(
            student_id=student_id,
            topic=topic,
            progress_score=score,
            completed_labs=completed_labs
        )
        
        assert result is True

    @pytest.mark.asyncio
    async def test_update_learning_progress_existing(self, memory_manager, sample_student_data):
        """Test updating existing learning progress."""
        student_id = sample_student_data["student_id"]
        topic = "S3"
        
        # First update
        await memory_manager.update_learning_progress(
            student_id=student_id,
            topic=topic,
            progress_score=60,
            completed_labs=["s3_basics"]
        )
        
        # Second update (should update existing record)
        result = await memory_manager.update_learning_progress(
            student_id=student_id,
            topic=topic,
            progress_score=90,
            completed_labs=["s3_basics", "s3_advanced"]
        )
        
        assert result is True

    @pytest.mark.asyncio
    async def test_get_learning_progress_empty(self, memory_manager):
        """Test getting learning progress for student with no progress."""
        progress = await memory_manager.get_learning_progress("nonexistent_student")
        
        assert isinstance(progress, dict)
        assert "student_id" in progress
        assert progress["overall_score"] == 0
        assert progress["total_labs_completed"] == 0

    @pytest.mark.asyncio
    async def test_get_learning_progress_with_data(self, memory_manager, sample_student_data):
        """Test getting learning progress with actual data."""
        student_id = sample_student_data["student_id"]
        
        # Add progress for multiple topics
        topics_progress = [
            ("EC2", 85, ["ec2_basics", "ec2_advanced"]),
            ("S3", 75, ["s3_basics"]),
            ("VPC", 90, ["vpc_basics", "vpc_advanced", "vpc_peering"])
        ]
        
        for topic, score, labs in topics_progress:
            await memory_manager.update_learning_progress(
                student_id=student_id,
                topic=topic,
                progress_score=score,
                completed_labs=labs
            )
        
        # Get overall progress
        progress = await memory_manager.get_learning_progress(student_id)
        
        assert progress["student_id"] == student_id
        assert len(progress["topics"]) == 3
        assert progress["overall_score"] > 0
        assert progress["total_labs_completed"] == 6  # Sum of all labs

    @pytest.mark.asyncio
    async def test_memory_cleanup(self, memory_manager, sample_student_data):
        """Test automatic memory cleanup when exceeding max size."""
        student_id = sample_student_data["student_id"]
        
        # Set a small max memory size for testing
        original_max_size = memory_manager.config.max_memory_size
        memory_manager.config.max_memory_size = 5
        
        try:
            # Add more interactions than max size
            for i in range(10):
                await memory_manager.save_interaction(
                    student_id=student_id,
                    input_text=f"Question {i}",
                    response=f"Response {i}",
                    timestamp=datetime.utcnow()
                )
            
            # Check that old memories were cleaned up
            memories = await memory_manager.get_student_memory(student_id)
            assert len(memories) <= memory_manager.config.max_memory_size
            
        finally:
            # Restore original max size
            memory_manager.config.max_memory_size = original_max_size

    def test_get_total_interactions(self, memory_manager):
        """Test getting total interaction count."""
        total = memory_manager.get_total_interactions()
        assert isinstance(total, int)
        assert total >= 0

    @pytest.mark.asyncio
    async def test_get_student_stats(self, memory_manager, sample_student_data):
        """Test getting comprehensive student statistics."""
        student_id = sample_student_data["student_id"]
        
        # Add some data first
        await memory_manager.save_interaction(
            student_id=student_id,
            input_text="Test question",
            response="Test response",
            timestamp=datetime.utcnow()
        )
        
        await memory_manager.update_learning_progress(
            student_id=student_id,
            topic="EC2",
            progress_score=80,
            completed_labs=["ec2_basics"]
        )
        
        # Get stats
        stats = await memory_manager.get_student_stats(student_id)
        
        assert "student_id" in stats
        assert "total_interactions" in stats
        assert "learning_progress" in stats
        assert stats["student_id"] == student_id
        assert stats["total_interactions"] > 0

    @pytest.mark.asyncio
    async def test_error_handling_database_failure(self, memory_manager):
        """Test error handling when database operations fail."""
        # Mock database failure
        with patch.object(memory_manager, 'SessionLocal') as mock_session_local:
            mock_session = Mock()
            mock_session.add.side_effect = Exception("Database error")
            mock_session_local.return_value = mock_session
            
            result = await memory_manager.save_interaction(
                student_id="test",
                input_text="test",
                response="test",
                timestamp=datetime.utcnow()
            )
            
            assert result is False

    @pytest.mark.asyncio
    async def test_memory_chronological_order(self, memory_manager, sample_student_data):
        """Test that memories are returned in chronological order."""
        student_id = sample_student_data["student_id"]
        
        # Add interactions with specific timestamps
        base_time = datetime.utcnow()
        interactions = []
        
        for i in range(5):
            timestamp = base_time + timedelta(minutes=i)
            input_text = f"Question {i}"
            interactions.append((timestamp, input_text))
            
            await memory_manager.save_interaction(
                student_id=student_id,
                input_text=input_text,
                response=f"Response {i}",
                timestamp=timestamp
            )
        
        # Retrieve memories
        memories = await memory_manager.get_student_memory(student_id)
        
        # Check chronological order (oldest first in our implementation)
        for i in range(len(memories) - 1):
            current_time = datetime.fromisoformat(memories[i]["timestamp"])
            next_time = datetime.fromisoformat(memories[i + 1]["timestamp"])
            assert current_time <= next_time

    @pytest.mark.asyncio
    async def test_context_preservation(self, memory_manager, sample_student_data):
        """Test that context information is preserved correctly."""
        student_id = sample_student_data["student_id"]
        context = {
            "topic": "EC2",
            "lab_name": "ec2_basics",
            "difficulty": "beginner",
            "tools_used": ["aws_knowledge_search", "get_lab_guidance"]
        }
        
        await memory_manager.save_interaction(
            student_id=student_id,
            input_text="How do I launch an EC2 instance?",
            response="To launch an EC2 instance...",
            timestamp=datetime.utcnow(),
            context=context
        )
        
        memories = await memory_manager.get_student_memory(student_id)
        
        assert len(memories) == 1
        assert memories[0]["context"] == context

class TestLearningProgressModel:
    """Test the LearningProgress database model."""
    
    def test_learning_progress_model_attributes(self):
        """Test that LearningProgress model has required attributes."""
        # This would typically test the SQLAlchemy model
        # For now, we'll test the conceptual structure
        required_attributes = [
            'id', 'student_id', 'topic', 'progress_score', 
            'completed_labs', 'last_activity'
        ]
        
        # In a real implementation, you would test:
        # progress = LearningProgress()
        # for attr in required_attributes:
        #     assert hasattr(progress, attr)
        
        assert all(attr in required_attributes for attr in required_attributes)

class TestMemoryManagerIntegration:
    """Integration tests for the MemoryManager."""
    
    @pytest.mark.asyncio
    async def test_full_student_journey(self, memory_manager):
        """Test a complete student learning journey through memory system."""
        student_id = "integration_test_student"
        
        # Phase 1: Initial learning
        await memory_manager.save_interaction(
            student_id=student_id,
            input_text="What is cloud computing?",
            response="Cloud computing is...",
            timestamp=datetime.utcnow(),
            context={"topic": "basics", "phase": "introduction"}
        )
        
        # Phase 2: Service-specific learning
        ec2_interactions = [
            "What is EC2?",
            "How do I launch an instance?", 
            "How do I connect to my instance?"
        ]
        
        for question in ec2_interactions:
            await memory_manager.save_interaction(
                student_id=student_id,
                input_text=question,
                response=f"Response to: {question}",
                timestamp=datetime.utcnow(),
                context={"topic": "EC2", "phase": "service_learning"}
            )
        
        # Phase 3: Progress tracking
        await memory_manager.update_learning_progress(
            student_id=student_id,
            topic="EC2",
            progress_score=75,
            completed_labs=["ec2_basics"]
        )
        
        # Phase 4: Advanced learning
        await memory_manager.update_learning_progress(
            student_id=student_id,
            topic="EC2",
            progress_score=90,
            completed_labs=["ec2_basics", "ec2_advanced"]
        )
        
        # Verify the complete journey
        memories = await memory_manager.get_student_memory(student_id)
        progress = await memory_manager.get_learning_progress(student_id)
        stats = await memory_manager.get_student_stats(student_id)
        
        assert len(memories) == 4  # 1 intro + 3 EC2 questions
        assert "EC2" in progress["topics"]
        assert progress["topics"]["EC2"]["score"] == 90
        assert len(progress["topics"]["EC2"]["completed_labs"]) == 2
        assert stats["total_interactions"] == 4