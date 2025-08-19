"""
Feedback Collector Module

Handles collection, storage, and analysis of student feedback
to improve the learning experience and agent responses.
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from ..configs.config import get_config

logger = logging.getLogger(__name__)

Base = declarative_base()

class StudentFeedback(Base):
    """Database model for student feedback."""
    __tablename__ = "student_feedback"
    
    id = Column(Integer, primary_key=True)
    student_id = Column(String(50), nullable=False)
    session_id = Column(String(50), nullable=True)
    rating = Column(Integer, nullable=False)  # 1-5 scale
    comments = Column(Text, nullable=True)
    feedback_type = Column(String(50), default="general")  # general, lab, explanation, etc.
    timestamp = Column(DateTime, nullable=False)
    context = Column(Text, nullable=True)  # JSON string for additional context

class FeedbackAnalysis(Base):
    """Database model for feedback analysis results."""
    __tablename__ = "feedback_analysis"
    
    id = Column(Integer, primary_key=True)
    analysis_date = Column(DateTime, nullable=False)
    avg_rating = Column(Float, nullable=False)
    total_feedback_count = Column(Integer, nullable=False)
    improvement_suggestions = Column(Text, nullable=True)  # JSON string
    sentiment_analysis = Column(Text, nullable=True)  # JSON string

class FeedbackCollector:
    """
    Collects and analyzes student feedback for continuous improvement.
    
    This class handles feedback storage, analysis, and generation of
    insights to improve the learning agent's performance.
    """
    
    def __init__(self):
        self.config = get_config()
        self.engine = create_engine(self.config.database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
        
        logger.info("Feedback Collector initialized")
    
    async def save_feedback(self, student_id: str, session_id: str, rating: int, 
                          comments: str = None, feedback_type: str = "general", 
                          context: Dict = None) -> bool:
        """
        Save student feedback to the database.
        
        Args:
            student_id: Unique identifier for the student
            session_id: Session identifier
            rating: Rating from 1-5
            comments: Optional feedback comments
            feedback_type: Type of feedback (general, lab, explanation, etc.)
            context: Additional context information
            
        Returns:
            Boolean indicating success
        """
        try:
            if not (1 <= rating <= 5):
                raise ValueError("Rating must be between 1 and 5")
            
            session = self.SessionLocal()
            
            # Create feedback record
            feedback_record = StudentFeedback(
                student_id=student_id,
                session_id=session_id,
                rating=rating,
                comments=comments,
                feedback_type=feedback_type,
                timestamp=datetime.utcnow(),
                context=json.dumps(context) if context else None
            )
            
            session.add(feedback_record)
            session.commit()
            session.close()
            
            logger.info(f"Feedback saved from student {student_id} with rating {rating}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
            return False
    
    async def get_feedback_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get feedback summary for the specified time period.
        
        Args:
            days: Number of days to look back for feedback
            
        Returns:
            Dictionary containing feedback summary
        """
        try:
            session = self.SessionLocal()
            
            # Calculate date threshold
            from datetime import timedelta
            date_threshold = datetime.utcnow() - timedelta(days=days)
            
            # Get feedback within the time period
            feedback_records = session.query(StudentFeedback)\
                .filter(StudentFeedback.timestamp >= date_threshold)\
                .all()
            
            if not feedback_records:
                return {
                    "period_days": days,
                    "total_feedback": 0,
                    "average_rating": 0,
                    "rating_distribution": {},
                    "feedback_types": {},
                    "recent_comments": []
                }
            
            # Calculate statistics
            total_feedback = len(feedback_records)
            ratings = [record.rating for record in feedback_records]
            average_rating = sum(ratings) / len(ratings)
            
            # Rating distribution
            rating_distribution = {}
            for rating in range(1, 6):
                rating_distribution[str(rating)] = ratings.count(rating)
            
            # Feedback types distribution
            feedback_types = {}
            for record in feedback_records:
                feedback_type = record.feedback_type
                feedback_types[feedback_type] = feedback_types.get(feedback_type, 0) + 1
            
            # Recent comments (last 10)
            recent_comments = []
            for record in sorted(feedback_records, key=lambda x: x.timestamp, reverse=True)[:10]:
                if record.comments:
                    recent_comments.append({
                        "student_id": record.student_id,
                        "rating": record.rating,
                        "comments": record.comments,
                        "timestamp": record.timestamp.isoformat(),
                        "feedback_type": record.feedback_type
                    })
            
            summary = {
                "period_days": days,
                "total_feedback": total_feedback,
                "average_rating": round(average_rating, 2),
                "rating_distribution": rating_distribution,
                "feedback_types": feedback_types,
                "recent_comments": recent_comments,
                "improvement_areas": await self._identify_improvement_areas(feedback_records)
            }
            
            session.close()
            return summary
            
        except Exception as e:
            logger.error(f"Error getting feedback summary: {str(e)}")
            return {"error": str(e)}
    
    async def get_student_feedback_history(self, student_id: str) -> List[Dict[str, Any]]:
        """
        Get feedback history for a specific student.
        
        Args:
            student_id: Student identifier
            
        Returns:
            List of feedback records
        """
        try:
            session = self.SessionLocal()
            
            feedback_records = session.query(StudentFeedback)\
                .filter(StudentFeedback.student_id == student_id)\
                .order_by(StudentFeedback.timestamp.desc())\
                .all()
            
            feedback_history = []
            for record in feedback_records:
                feedback_dict = {
                    "id": record.id,
                    "session_id": record.session_id,
                    "rating": record.rating,
                    "comments": record.comments,
                    "feedback_type": record.feedback_type,
                    "timestamp": record.timestamp.isoformat(),
                    "context": json.loads(record.context) if record.context else None
                }
                feedback_history.append(feedback_dict)
            
            session.close()
            return feedback_history
            
        except Exception as e:
            logger.error(f"Error getting student feedback history: {str(e)}")
            return []
    
    async def _identify_improvement_areas(self, feedback_records: List[StudentFeedback]) -> List[str]:
        """
        Analyze feedback to identify areas for improvement.
        
        Args:
            feedback_records: List of feedback records
            
        Returns:
            List of improvement suggestions
        """
        improvement_areas = []
        
        # Analyze low ratings
        low_ratings = [record for record in feedback_records if record.rating <= 2]
        if len(low_ratings) > len(feedback_records) * 0.2:  # More than 20% low ratings
            improvement_areas.append("High number of low ratings - review overall agent performance")
        
        # Analyze comments for common themes
        comments = [record.comments.lower() for record in feedback_records if record.comments]
        
        # Simple keyword analysis (in production, use more sophisticated NLP)
        common_issues = {
            "slow": "Response time optimization needed",
            "unclear": "Improve explanation clarity",
            "wrong": "Review accuracy of responses",
            "confusing": "Simplify complex explanations",
            "difficult": "Adjust difficulty level",
            "boring": "Make interactions more engaging"
        }
        
        for keyword, suggestion in common_issues.items():
            if any(keyword in comment for comment in comments):
                if suggestion not in improvement_areas:
                    improvement_areas.append(suggestion)
        
        return improvement_areas
    
    async def generate_feedback_insights(self) -> Dict[str, Any]:
        """
        Generate insights from all collected feedback.
        
        Returns:
            Dictionary containing feedback insights and recommendations
        """
        try:
            session = self.SessionLocal()
            
            # Get all feedback
            all_feedback = session.query(StudentFeedback).all()
            
            if not all_feedback:
                return {
                    "total_feedback": 0,
                    "insights": ["No feedback data available"],
                    "recommendations": ["Encourage students to provide feedback"]
                }
            
            insights = []
            recommendations = []
            
            # Overall statistics
            total_feedback = len(all_feedback)
            avg_rating = sum(record.rating for record in all_feedback) / total_feedback
            
            insights.append(f"Total feedback collected: {total_feedback}")
            insights.append(f"Average rating: {avg_rating:.2f}/5.0")
            
            # Trend analysis (compare recent vs older feedback)
            from datetime import timedelta
            recent_threshold = datetime.utcnow() - timedelta(days=7)
            recent_feedback = [record for record in all_feedback if record.timestamp >= recent_threshold]
            
            if recent_feedback:
                recent_avg = sum(record.rating for record in recent_feedback) / len(recent_feedback)
                insights.append(f"Recent 7-day average: {recent_avg:.2f}/5.0")
                
                if recent_avg > avg_rating:
                    insights.append("Positive trend: Recent ratings are improving")
                elif recent_avg < avg_rating:
                    insights.append("Negative trend: Recent ratings are declining")
                    recommendations.append("Investigate recent changes that may have impacted user experience")
            
            # Feedback type analysis
            type_analysis = {}
            for record in all_feedback:
                feedback_type = record.feedback_type
                if feedback_type not in type_analysis:
                    type_analysis[feedback_type] = []
                type_analysis[feedback_type].append(record.rating)
            
            for feedback_type, ratings in type_analysis.items():
                avg_type_rating = sum(ratings) / len(ratings)
                insights.append(f"{feedback_type.title()} feedback average: {avg_type_rating:.2f}/5.0")
                
                if avg_type_rating < 3.0:
                    recommendations.append(f"Focus on improving {feedback_type} interactions")
            
            # Save analysis to database
            analysis_record = FeedbackAnalysis(
                analysis_date=datetime.utcnow(),
                avg_rating=avg_rating,
                total_feedback_count=total_feedback,
                improvement_suggestions=json.dumps(recommendations),
                sentiment_analysis=json.dumps(insights)
            )
            
            session.add(analysis_record)
            session.commit()
            session.close()
            
            return {
                "total_feedback": total_feedback,
                "average_rating": avg_rating,
                "insights": insights,
                "recommendations": recommendations,
                "analysis_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating feedback insights: {str(e)}")
            return {"error": str(e)}
    
    async def export_feedback_data(self, format: str = "json") -> str:
        """
        Export feedback data for analysis.
        
        Args:
            format: Export format (json, csv)
            
        Returns:
            Exported data as string
        """
        try:
            session = self.SessionLocal()
            
            feedback_records = session.query(StudentFeedback).all()
            
            if format.lower() == "json":
                data = []
                for record in feedback_records:
                    data.append({
                        "id": record.id,
                        "student_id": record.student_id,
                        "session_id": record.session_id,
                        "rating": record.rating,
                        "comments": record.comments,
                        "feedback_type": record.feedback_type,
                        "timestamp": record.timestamp.isoformat(),
                        "context": json.loads(record.context) if record.context else None
                    })
                return json.dumps(data, indent=2)
            
            elif format.lower() == "csv":
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow(["ID", "Student ID", "Session ID", "Rating", "Comments", "Type", "Timestamp"])
                
                # Write data
                for record in feedback_records:
                    writer.writerow([
                        record.id,
                        record.student_id,
                        record.session_id,
                        record.rating,
                        record.comments,
                        record.feedback_type,
                        record.timestamp.isoformat()
                    ])
                
                session.close()
                return output.getvalue()
            
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting feedback data: {str(e)}")
            return f"Error: {str(e)}"