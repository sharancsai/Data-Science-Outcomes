"""
Streamlit Web Interface for AWS Learning Agent

Interactive web application for students to interact with the AWS learning agent.
Provides a user-friendly interface for learning AWS concepts and getting lab guidance.
"""

import streamlit as st
import requests
import json
import uuid
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="AWS Learning Assistant",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if "student_id" not in st.session_state:
    st.session_state.student_id = str(uuid.uuid4())[:8]
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False

def call_api(endpoint, method="GET", data=None):
    """Make API calls to the backend."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

def display_chat_message(message, is_user=True):
    """Display a chat message with appropriate styling."""
    if is_user:
        with st.chat_message("user"):
            st.write(message)
    else:
        with st.chat_message("assistant"):
            st.write(message)

def main():
    """Main application function."""
    
    # Header
    st.title("☁️ AWS Learning Assistant")
    st.markdown("Your AI-powered guide to learning Amazon Web Services")
    
    # Sidebar
    with st.sidebar:
        st.header("Student Info")
        st.info(f"Student ID: {st.session_state.student_id}")
        st.info(f"Session: {st.session_state.session_id[:8]}...")
        
        st.header("Quick Actions")
        
        # Lab guidance section
        if st.button("📚 Get Lab Guidance"):
            st.session_state.show_lab_guidance = True
        
        # Progress tracking
        if st.button("📊 View Progress"):
            st.session_state.show_progress = True
        
        # Knowledge base
        if st.button("🔍 Browse Topics"):
            st.session_state.show_topics = True
        
        # Feedback section
        st.header("Feedback")
        if not st.session_state.feedback_submitted:
            with st.form("feedback_form"):
                rating = st.slider("Rate your experience", 1, 5, 3)
                comments = st.text_area("Comments (optional)")
                feedback_type = st.selectbox("Feedback type", 
                    ["general", "lab", "explanation", "difficulty"])
                
                if st.form_submit_button("Submit Feedback"):
                    feedback_data = {
                        "student_id": st.session_state.student_id,
                        "session_id": st.session_state.session_id,
                        "rating": rating,
                        "comments": comments,
                        "feedback_type": feedback_type
                    }
                    
                    response = call_api("/feedback", "POST", feedback_data)
                    if "error" not in response:
                        st.success("Thank you for your feedback!")
                        st.session_state.feedback_submitted = True
                    else:
                        st.error(f"Error submitting feedback: {response['error']}")
        else:
            st.success("Feedback submitted! ✅")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat interface
        st.header("💬 Chat with AWS Learning Assistant")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                display_chat_message(message["content"], message["is_user"])
        
        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area("Ask me anything about AWS...", height=100,
                placeholder="e.g., How do I launch an EC2 instance? What is S3 used for?")
            
            col_send, col_clear = st.columns([1, 1])
            with col_send:
                send_button = st.form_submit_button("Send 📤", use_container_width=True)
            with col_clear:
                clear_button = st.form_submit_button("Clear Chat 🗑️", use_container_width=True)
        
        if send_button and user_input:
            # Add user message to history
            st.session_state.chat_history.append({
                "content": user_input,
                "is_user": True,
                "timestamp": datetime.now()
            })
            
            # Show loading spinner
            with st.spinner("AWS Learning Assistant is thinking..."):
                # Call the API
                chat_data = {
                    "student_id": st.session_state.student_id,
                    "message": user_input,
                    "session_id": st.session_state.session_id
                }
                
                response = call_api("/chat", "POST", chat_data)
                
                if "error" not in response:
                    # Add assistant response to history
                    st.session_state.chat_history.append({
                        "content": response["response"],
                        "is_user": False,
                        "timestamp": datetime.now()
                    })
                else:
                    st.error(f"Error: {response['error']}")
                    st.session_state.chat_history.append({
                        "content": f"I apologize, but I encountered an error: {response['error']}. Please try again.",
                        "is_user": False,
                        "timestamp": datetime.now()
                    })
            
            # Refresh the page to show new messages
            st.rerun()
        
        if clear_button:
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        # Quick help and suggestions
        st.header("💡 Quick Help")
        
        with st.expander("Sample Questions"):
            st.markdown("""
            **Getting Started:**
            - What is AWS and why should I learn it?
            - How do I get started with AWS?
            - What are the core AWS services?
            
            **EC2 Questions:**
            - How do I launch an EC2 instance?
            - What are the different EC2 instance types?
            - How do I connect to my EC2 instance?
            
            **Storage Questions:**
            - What is Amazon S3 and how do I use it?
            - How do I create an S3 bucket?
            - What are the different S3 storage classes?
            
            **Networking:**
            - What is a VPC and why do I need one?
            - How do I set up a VPC with subnets?
            - What are security groups?
            
            **Lab Help:**
            - Give me guidance for the EC2 lab
            - Show me the S3 basics lab steps
            - Help me with VPC configuration
            """)
        
        with st.expander("AWS Service Quick Reference"):
            st.markdown("""
            **Compute:**
            - **EC2**: Virtual servers in the cloud
            - **Lambda**: Serverless computing
            
            **Storage:**
            - **S3**: Object storage service
            - **EBS**: Block storage for EC2
            
            **Database:**
            - **RDS**: Managed relational databases
            - **DynamoDB**: NoSQL database
            
            **Networking:**
            - **VPC**: Virtual private cloud
            - **CloudFront**: Content delivery network
            
            **Security:**
            - **IAM**: Identity and access management
            - **KMS**: Key management service
            """)
        
        # System status
        st.header("🚀 System Status")
        status_response = call_api("/health")
        if "error" not in status_response:
            st.success("✅ Agent is online and ready")
            if "agent_stats" in status_response:
                stats = status_response["agent_stats"]
                st.info(f"Model: {stats.get('model_type', 'Unknown')}")
                st.info(f"Total interactions: {stats.get('total_interactions', 0)}")
        else:
            st.error("❌ Agent is currently unavailable")
            st.error(f"Error: {status_response['error']}")
    
    # Handle sidebar actions
    if hasattr(st.session_state, 'show_lab_guidance') and st.session_state.show_lab_guidance:
        show_lab_guidance_modal()
        st.session_state.show_lab_guidance = False
    
    if hasattr(st.session_state, 'show_progress') and st.session_state.show_progress:
        show_progress_modal()
        st.session_state.show_progress = False
    
    if hasattr(st.session_state, 'show_topics') and st.session_state.show_topics:
        show_topics_modal()
        st.session_state.show_topics = False

def show_lab_guidance_modal():
    """Show lab guidance in a modal."""
    with st.expander("📚 Lab Guidance", expanded=True):
        lab_name = st.selectbox("Select a lab:", [
            "ec2_basic", "s3_basics", "vpc_setup", "lambda_intro", "rds_setup"
        ])
        
        if st.button("Get Lab Guidance"):
            with st.spinner("Loading lab guidance..."):
                response = call_api("/lab-guidance", "POST", {"lab_name": lab_name})
                if "error" not in response:
                    st.markdown(response["guidance"])
                else:
                    st.error(f"Error loading lab guidance: {response['error']}")

def show_progress_modal():
    """Show progress tracking in a modal."""
    with st.expander("📊 Learning Progress", expanded=True):
        response = call_api(f"/progress/{st.session_state.student_id}")
        if "error" not in response:
            progress = response.get("progress", {})
            
            if progress.get("topics"):
                st.subheader("Progress by Topic")
                for topic, data in progress["topics"].items():
                    st.write(f"**{topic}**: {data['score']}%")
                    st.progress(data['score'] / 100)
                
                st.info(f"Overall Score: {progress.get('overall_score', 0):.1f}%")
                st.info(f"Total Labs Completed: {progress.get('total_labs_completed', 0)}")
            else:
                st.info("No progress data available yet. Start learning to track your progress!")
        else:
            st.error(f"Error loading progress: {response['error']}")

def show_topics_modal():
    """Show available topics in a modal."""
    with st.expander("🔍 Available AWS Topics", expanded=True):
        response = call_api("/knowledge/topics")
        if "error" not in response:
            topics = response.get("topics", [])
            st.write("Click on any topic to learn more about it:")
            
            cols = st.columns(3)
            for i, topic in enumerate(topics):
                with cols[i % 3]:
                    if st.button(topic, key=f"topic_{i}"):
                        # Add topic question to chat
                        question = f"Tell me about {topic}"
                        st.session_state.chat_history.append({
                            "content": question,
                            "is_user": True,
                            "timestamp": datetime.now()
                        })
                        st.rerun()
        else:
            st.error(f"Error loading topics: {response['error']}")

if __name__ == "__main__":
    main()