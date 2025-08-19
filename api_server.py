"""
FastAPI Web Interface for AWS Learning Agent

Provides REST API endpoints for the agentic learning agent to enable
web-based interactions and integration with various platforms.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import logging

from agent import AWSLearningAgent
from configs.config import get_config, setup_directories

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize configuration and create directories
config = get_config()
setup_directories()

# Initialize the agent
agent = AWSLearningAgent()

# FastAPI app
app = FastAPI(
    title="AWS Learning Agent API",
    description="Agentic agent API for AWS learner lab integration",
    version="1.0.0"
)

# CORS middleware for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class StudentQuery(BaseModel):
    student_id: str = Field(..., description="Unique student identifier")
    message: str = Field(..., description="Student's question or input")
    session_id: Optional[str] = Field(None, description="Optional session identifier")

class AgentResponse(BaseModel):
    response: str = Field(..., description="Agent's response")
    student_id: str = Field(..., description="Student identifier")
    timestamp: str = Field(..., description="Response timestamp")
    session_id: Optional[str] = Field(None, description="Session identifier")
    model_used: str = Field(..., description="Model used for response")

class FeedbackRequest(BaseModel):
    student_id: str = Field(..., description="Student identifier")
    session_id: str = Field(..., description="Session identifier")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    comments: Optional[str] = Field(None, description="Optional feedback comments")
    feedback_type: str = Field(default="general", description="Type of feedback")

class LabGuidanceRequest(BaseModel):
    lab_name: str = Field(..., description="Name of the AWS lab")
    student_id: Optional[str] = Field(None, description="Optional student identifier")

class ProgressRequest(BaseModel):
    student_id: str = Field(..., description="Student identifier")
    topic: str = Field(..., description="AWS topic/service")
    progress_score: int = Field(..., ge=0, le=100, description="Progress score 0-100")
    completed_labs: Optional[List[str]] = Field(None, description="List of completed labs")

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AWS Learning Agent API",
        "version": "1.0.0",
        "status": "active",
        "agent_model": config.model_type,
        "endpoints": {
            "/chat": "Student chat interaction",
            "/feedback": "Submit student feedback", 
            "/lab-guidance": "Get lab guidance",
            "/progress": "Update/get learning progress",
            "/health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        stats = agent.get_agent_stats()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "agent_stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/chat", response_model=AgentResponse)
async def chat_with_agent(query: StudentQuery):
    """
    Chat with the AWS learning agent.
    
    This endpoint processes student questions and returns personalized responses
    with AWS learning guidance and assistance.
    """
    try:
        # Generate session ID if not provided
        session_id = query.session_id or str(uuid.uuid4())
        
        # Process the query through the agent
        response_data = await agent.process_student_input(
            student_id=query.student_id,
            input_text=query.message
        )
        
        # Return structured response
        return AgentResponse(
            response=response_data["response"],
            student_id=query.student_id,
            timestamp=response_data["timestamp"],
            session_id=session_id,
            model_used=response_data["model_used"]
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit student feedback for agent improvement.
    
    Collects student feedback to help improve the agent's performance
    and learning effectiveness.
    """
    try:
        success = await agent.collect_feedback(
            student_id=feedback.student_id,
            session_id=feedback.session_id,
            rating=feedback.rating,
            comments=feedback.comments
        )
        
        if success:
            return {
                "message": "Feedback submitted successfully",
                "student_id": feedback.student_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save feedback")
            
    except Exception as e:
        logger.error(f"Error in feedback endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Feedback submission failed: {str(e)}")

@app.post("/lab-guidance")
async def get_lab_guidance(request: LabGuidanceRequest):
    """
    Get step-by-step guidance for AWS labs.
    
    Provides detailed lab instructions and guidance for specific AWS
    learning exercises and practical labs.
    """
    try:
        guidance = agent.knowledge_base.get_lab_guidance(request.lab_name)
        
        return {
            "lab_name": request.lab_name,
            "guidance": guidance,
            "student_id": request.student_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in lab guidance endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lab guidance retrieval failed: {str(e)}")

@app.post("/progress")
async def update_progress(request: ProgressRequest):
    """
    Update student learning progress.
    
    Updates and tracks student progress for specific AWS topics
    and learning modules.
    """
    try:
        success = await agent.memory_manager.update_learning_progress(
            student_id=request.student_id,
            topic=request.topic,
            progress_score=request.progress_score,
            completed_labs=request.completed_labs
        )
        
        if success:
            return {
                "message": "Progress updated successfully",
                "student_id": request.student_id,
                "topic": request.topic,
                "score": request.progress_score,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update progress")
            
    except Exception as e:
        logger.error(f"Error in progress endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Progress update failed: {str(e)}")

@app.get("/progress/{student_id}")
async def get_progress(student_id: str):
    """
    Get student learning progress.
    
    Retrieves comprehensive learning progress information for a student.
    """
    try:
        progress = await agent.memory_manager.get_learning_progress(student_id)
        
        return {
            "student_id": student_id,
            "progress": progress,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting progress for student {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Progress retrieval failed: {str(e)}")

@app.get("/student/{student_id}/history")
async def get_student_history(student_id: str, limit: int = 20):
    """
    Get student interaction history.
    
    Retrieves recent interaction history for a specific student.
    """
    try:
        history = await agent.memory_manager.get_student_memory(student_id, limit=limit)
        
        return {
            "student_id": student_id,
            "history": history,
            "count": len(history),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting history for student {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")

@app.get("/knowledge/topics")
async def get_knowledge_topics():
    """
    Get available AWS knowledge topics.
    
    Returns a list of all available AWS topics and services
    in the knowledge base.
    """
    try:
        topics = agent.knowledge_base.get_all_topics()
        
        return {
            "topics": topics,
            "count": len(topics),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting knowledge topics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Topics retrieval failed: {str(e)}")

@app.get("/feedback/summary")
async def get_feedback_summary(days: int = 30):
    """
    Get feedback summary and insights.
    
    Provides analysis of student feedback for the specified time period.
    """
    try:
        summary = await agent.feedback_collector.get_feedback_summary(days=days)
        
        return {
            "summary": summary,
            "period_days": days,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting feedback summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Feedback summary failed: {str(e)}")

@app.get("/agent/stats")
async def get_agent_statistics():
    """
    Get agent performance statistics.
    
    Returns comprehensive statistics about agent performance,
    interactions, and system health.
    """
    try:
        stats = agent.get_agent_stats()
        feedback_insights = await agent.feedback_collector.generate_feedback_insights()
        
        return {
            "agent_stats": stats,
            "feedback_insights": feedback_insights,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting agent statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")

# Background task for periodic cleanup and analysis
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("AWS Learning Agent API starting up...")
    logger.info(f"Using {config.model_type} model: {config.model_name}")
    logger.info(f"Database: {config.database_url}")
    logger.info("API ready for requests")

@app.on_event("shutdown") 
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("AWS Learning Agent API shutting down...")

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "api_server:app",
        host=config.host,
        port=config.port,
        reload=True if config.environment == "development" else False,
        log_level=config.log_level.lower()
    )