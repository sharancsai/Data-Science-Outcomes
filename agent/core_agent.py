"""
Core AWS Learning Agent Implementation

This module contains the main agentic agent implementation using LangChain
for AWS learner lab integration with support for both Ollama and Hugging Face models.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

from ..configs.config import get_config
from .memory_manager import MemoryManager
from .feedback_collector import FeedbackCollector
from .knowledge_base import AWSKnowledgeBase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSLearningAgent:
    """
    Main agentic agent for AWS learning assistance.
    
    This agent provides guided AWS lab experiences, adapts to student interactions,
    and maintains memory of learning sessions for continuous improvement.
    """
    
    def __init__(self):
        self.config = get_config()
        self.memory_manager = MemoryManager()
        self.feedback_collector = FeedbackCollector()
        self.knowledge_base = AWSKnowledgeBase()
        
        # Initialize the language model
        self.llm = self._initialize_model()
        
        # Initialize memory
        self.conversation_memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Initialize tools
        self.tools = self._create_tools()
        
        # Initialize agent
        self.agent = self._create_agent()
        
        logger.info(f"AWS Learning Agent initialized with {self.config.model_type} model")
    
    def _initialize_model(self):
        """Initialize the language model based on configuration."""
        if self.config.model_type.lower() == "ollama":
            return ChatOllama(
                model=self.config.model_name,
                base_url=self.config.ollama_base_url,
                temperature=0.7
            )
        elif self.config.model_type.lower() == "huggingface":
            # Use HuggingFace pipeline for free deployment
            hf_pipeline = HuggingFacePipeline.from_model_id(
                model_id=self.config.huggingface_model_name,
                task="text-generation",
                model_kwargs={
                    "temperature": 0.7,
                    "max_length": 512,
                    "do_sample": True
                }
            )
            return ChatHuggingFace(llm=hf_pipeline)
        else:
            raise ValueError(f"Unsupported model type: {self.config.model_type}")
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent to use."""
        tools = [
            Tool(
                name="aws_knowledge_search",
                description="Search AWS knowledge base for information about AWS services, best practices, and tutorials",
                func=self.knowledge_base.search
            ),
            Tool(
                name="get_lab_guidance",
                description="Get step-by-step guidance for AWS lab exercises",
                func=self.knowledge_base.get_lab_guidance
            ),
            Tool(
                name="check_progress",
                description="Check student's progress on current AWS lab",
                func=self._check_progress
            ),
            Tool(
                name="provide_feedback",
                description="Provide personalized feedback based on student's performance",
                func=self._provide_feedback
            ),
            Tool(
                name="simulate_aws_scenario",
                description="Simulate AWS scenarios for practice without real AWS resources",
                func=self._simulate_scenario
            )
        ]
        return tools
    
    def _create_agent(self) -> AgentExecutor:
        """Create the main agent with tools and memory."""
        
        # Define the agent prompt template
        prompt_template = PromptTemplate.from_template("""
You are an AWS Learning Assistant, an expert AI tutor helping students learn Amazon Web Services (AWS).
Your goal is to provide guided, interactive learning experiences for AWS concepts and practical labs.

You have access to the following tools:
{tools}

Your capabilities include:
- Providing step-by-step AWS lab guidance
- Explaining AWS concepts in simple terms
- Simulating AWS scenarios for practice
- Tracking student progress and providing feedback
- Adapting your teaching style based on student interactions

Guidelines:
1. Always be encouraging and patient with students
2. Break complex AWS concepts into digestible steps
3. Provide practical examples and use cases
4. Ask clarifying questions to understand student needs
5. Use the available tools to enhance learning experiences
6. Remember previous interactions to provide personalized assistance

Previous conversation:
{chat_history}

Student question: {input}

Thought: {agent_scratchpad}
""")
        
        # Create the agent
        react_agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt_template
        )
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=react_agent,
            tools=self.tools,
            memory=self.conversation_memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
        
        return agent_executor
    
    async def process_student_input(self, student_id: str, input_text: str) -> Dict[str, Any]:
        """
        Process student input and provide response with learning assistance.
        
        Args:
            student_id: Unique identifier for the student
            input_text: Student's question or input
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Load student's memory context
            student_memory = await self.memory_manager.get_student_memory(student_id)
            
            # Add context to the agent's memory if available
            if student_memory:
                for memory in student_memory[-5:]:  # Last 5 interactions
                    self.conversation_memory.chat_memory.add_user_message(memory['input'])
                    self.conversation_memory.chat_memory.add_ai_message(memory['response'])
            
            # Process the input through the agent
            response = await self.agent.ainvoke({
                "input": input_text,
                "chat_history": self.conversation_memory.chat_memory.messages
            })
            
            # Extract the agent's response
            agent_response = response["output"]
            
            # Save to memory
            await self.memory_manager.save_interaction(
                student_id=student_id,
                input_text=input_text,
                response=agent_response,
                timestamp=datetime.utcnow()
            )
            
            # Prepare response metadata
            response_data = {
                "response": agent_response,
                "student_id": student_id,
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": self.config.model_type,
                "tools_used": response.get("intermediate_steps", [])
            }
            
            logger.info(f"Processed input for student {student_id}")
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing student input: {str(e)}")
            return {
                "response": "I apologize, but I encountered an issue processing your request. Please try again.",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _check_progress(self, student_id: str) -> str:
        """Check and return student's learning progress."""
        try:
            # This would typically integrate with a learning management system
            # For now, we'll return a simulated progress report
            return f"Student {student_id} has completed 3/10 AWS labs with an average score of 85%"
        except Exception as e:
            return f"Unable to check progress: {str(e)}"
    
    def _provide_feedback(self, context: str) -> str:
        """Provide personalized feedback based on context."""
        try:
            # This would analyze student performance and provide tailored feedback
            return "Great work! Consider reviewing VPC concepts before moving to the next lab."
        except Exception as e:
            return f"Unable to provide feedback: {str(e)}"
    
    def _simulate_scenario(self, scenario: str) -> str:
        """Simulate AWS scenarios for practice."""
        try:
            scenarios = {
                "ec2_launch": "Simulating EC2 instance launch: \n1. Choose AMI\n2. Select instance type\n3. Configure security groups\n4. Launch instance",
                "s3_setup": "Simulating S3 bucket setup:\n1. Create bucket\n2. Configure permissions\n3. Upload test file\n4. Verify access",
                "vpc_config": "Simulating VPC configuration:\n1. Create VPC\n2. Add subnets\n3. Configure route tables\n4. Set up internet gateway"
            }
            
            return scenarios.get(scenario.lower(), f"Scenario '{scenario}' not available. Available scenarios: ec2_launch, s3_setup, vpc_config")
        except Exception as e:
            return f"Unable to simulate scenario: {str(e)}"
    
    async def collect_feedback(self, student_id: str, session_id: str, rating: int, comments: str) -> bool:
        """Collect student feedback for continuous improvement."""
        try:
            await self.feedback_collector.save_feedback(
                student_id=student_id,
                session_id=session_id,
                rating=rating,
                comments=comments,
                timestamp=datetime.utcnow()
            )
            logger.info(f"Feedback collected from student {student_id}")
            return True
        except Exception as e:
            logger.error(f"Error collecting feedback: {str(e)}")
            return False
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent statistics and performance metrics."""
        return {
            "model_type": self.config.model_type,
            "model_name": self.config.model_name,
            "total_interactions": self.memory_manager.get_total_interactions(),
            "feedback_enabled": self.config.feedback_enabled,
            "knowledge_base_size": len(self.knowledge_base.get_all_topics())
        }