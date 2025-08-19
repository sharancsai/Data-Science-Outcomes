"""
Memory Manager Module

Handles persistent memory for student interactions, learning progress,
and conversation history to enable personalized learning experiences.
"""

import json
import sqlite3
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from ..configs.config import get_config

logger = logging.getLogger(__name__)

Base = declarative_base()

class StudentMemory(Base):
    """Database model for student memory/interaction history."""
    __tablename__ = "student_memory"
    
    id = Column(Integer, primary_key=True)
    student_id = Column(String(50), nullable=False)
    session_id = Column(String(50), nullable=True)
    input_text = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    context = Column(Text, nullable=True)  # JSON string for additional context

class LearningProgress(Base):
    """Database model for tracking student learning progress."""
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True)
    student_id = Column(String(50), nullable=False)
    topic = Column(String(100), nullable=False)
    progress_score = Column(Integer, default=0)
    completed_labs = Column(Text, nullable=True)  # JSON string
    last_activity = Column(DateTime, nullable=False)

class MemoryManager:
    """
    Manages persistent memory for student interactions and learning progress.
    
    This class handles storing and retrieving conversation history, learning
    progress, and contextual information to enable personalized learning experiences.
    """
    
    def __init__(self):
        self.config = get_config()
        self.engine = create_engine(self.config.database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
        
        logger.info("Memory Manager initialized")
    
    async def save_interaction(self, student_id: str, input_text: str, response: str, 
                             timestamp: datetime, session_id: str = None, context: Dict = None) -> bool:
        """
        Save a student interaction to memory.
        
        Args:
            student_id: Unique identifier for the student
            input_text: Student's input/question
            response: Agent's response
            timestamp: When the interaction occurred
            session_id: Optional session identifier
            context: Additional context information
            
        Returns:
            Boolean indicating success
        """
        try:
            session = self.SessionLocal()
            
            # Create memory record
            memory_record = StudentMemory(
                student_id=student_id,
                session_id=session_id,
                input_text=input_text,
                response=response,
                timestamp=timestamp,
                context=json.dumps(context) if context else None
            )
            
            session.add(memory_record)
            session.commit()
            
            # Clean up old memories if we exceed max size
            await self._cleanup_old_memories(student_id, session)
            
            session.close()
            
            logger.debug(f"Saved interaction for student {student_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving interaction: {str(e)}")
            return False
    
    async def get_student_memory(self, student_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve recent memory for a student.
        
        Args:
            student_id: Student identifier
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of memory dictionaries
        """
        try:
            session = self.SessionLocal()
            
            # Get recent memories for the student
            memories = session.query(StudentMemory)\
                .filter(StudentMemory.student_id == student_id)\
                .order_by(StudentMemory.timestamp.desc())\
                .limit(limit)\
                .all()
            
            # Convert to dictionaries
            memory_list = []
            for memory in reversed(memories):  # Reverse to get chronological order
                memory_dict = {
                    "id": memory.id,
                    "input": memory.input_text,
                    "response": memory.response,
                    "timestamp": memory.timestamp.isoformat(),
                    "session_id": memory.session_id,
                    "context": json.loads(memory.context) if memory.context else None
                }
                memory_list.append(memory_dict)
            
            session.close()
            
            logger.debug(f"Retrieved {len(memory_list)} memories for student {student_id}")
            return memory_list
            
        except Exception as e:
            logger.error(f"Error retrieving student memory: {str(e)}")
            return []
    
    async def update_learning_progress(self, student_id: str, topic: str, 
                                     progress_score: int, completed_labs: List[str] = None) -> bool:
        """
        Update student's learning progress for a specific topic.
        
        Args:
            student_id: Student identifier
            topic: Learning topic (e.g., "EC2", "S3", "VPC")
            progress_score: Score from 0-100
            completed_labs: List of completed lab names
            
        Returns:
            Boolean indicating success
        """
        try:
            session = self.SessionLocal()
            
            # Check if progress record exists
            progress = session.query(LearningProgress)\
                .filter(LearningProgress.student_id == student_id,
                       LearningProgress.topic == topic)\
                .first()
            
            if progress:
                # Update existing record
                progress.progress_score = progress_score
                progress.completed_labs = json.dumps(completed_labs or [])
                progress.last_activity = datetime.utcnow()
            else:
                # Create new record
                progress = LearningProgress(
                    student_id=student_id,
                    topic=topic,
                    progress_score=progress_score,
                    completed_labs=json.dumps(completed_labs or []),
                    last_activity=datetime.utcnow()
                )
                session.add(progress)
            
            session.commit()
            session.close()
            
            logger.debug(f"Updated learning progress for student {student_id}, topic {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating learning progress: {str(e)}")
            return False
    
    async def get_learning_progress(self, student_id: str) -> Dict[str, Any]:
        """
        Get comprehensive learning progress for a student.
        
        Args:
            student_id: Student identifier
            
        Returns:
            Dictionary containing progress information
        """
        try:
            session = self.SessionLocal()
            
            # Get all progress records for the student
            progress_records = session.query(LearningProgress)\
                .filter(LearningProgress.student_id == student_id)\
                .all()
            
            # Compile progress information
            progress_data = {
                "student_id": student_id,
                "topics": {},
                "overall_score": 0,
                "total_labs_completed": 0,
                "last_activity": None
            }
            
            total_score = 0
            topic_count = 0
            latest_activity = None
            
            for record in progress_records:
                topic_data = {
                    "score": record.progress_score,
                    "completed_labs": json.loads(record.completed_labs or "[]"),
                    "last_activity": record.last_activity.isoformat()
                }
                progress_data["topics"][record.topic] = topic_data
                
                total_score += record.progress_score
                topic_count += 1
                progress_data["total_labs_completed"] += len(json.loads(record.completed_labs or "[]"))
                
                if latest_activity is None or record.last_activity > latest_activity:
                    latest_activity = record.last_activity
            
            # Calculate overall score
            if topic_count > 0:
                progress_data["overall_score"] = total_score / topic_count
            
            if latest_activity:
                progress_data["last_activity"] = latest_activity.isoformat()
            
            session.close()
            
            return progress_data
            
        except Exception as e:
            logger.error(f"Error retrieving learning progress: {str(e)}")
            return {"student_id": student_id, "error": str(e)}
    
    async def _cleanup_old_memories(self, student_id: str, session):
        """Clean up old memories if exceeding maximum size."""
        try:
            total_memories = session.query(StudentMemory)\
                .filter(StudentMemory.student_id == student_id)\
                .count()
            
            if total_memories > self.config.max_memory_size:
                # Delete oldest memories
                excess_count = total_memories - self.config.max_memory_size
                old_memories = session.query(StudentMemory)\
                    .filter(StudentMemory.student_id == student_id)\
                    .order_by(StudentMemory.timestamp.asc())\
                    .limit(excess_count)\
                    .all()
                
                for memory in old_memories:
                    session.delete(memory)
                
                logger.debug(f"Cleaned up {excess_count} old memories for student {student_id}")
                
        except Exception as e:
            logger.error(f"Error cleaning up memories: {str(e)}")
    
    def get_total_interactions(self) -> int:
        """Get total number of interactions across all students."""
        try:
            session = self.SessionLocal()
            total = session.query(StudentMemory).count()
            session.close()
            return total
        except Exception as e:
            logger.error(f"Error getting total interactions: {str(e)}")
            return 0
    
    async def get_student_stats(self, student_id: str) -> Dict[str, Any]:
        """Get statistics for a specific student."""
        try:
            session = self.SessionLocal()
            
            # Count total interactions
            total_interactions = session.query(StudentMemory)\
                .filter(StudentMemory.student_id == student_id)\
                .count()
            
            # Get latest interaction
            latest_interaction = session.query(StudentMemory)\
                .filter(StudentMemory.student_id == student_id)\
                .order_by(StudentMemory.timestamp.desc())\
                .first()
            
            stats = {
                "student_id": student_id,
                "total_interactions": total_interactions,
                "last_interaction": latest_interaction.timestamp.isoformat() if latest_interaction else None,
                "learning_progress": await self.get_learning_progress(student_id)
            }
            
            session.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting student stats: {str(e)}")
            return {"student_id": student_id, "error": str(e)}