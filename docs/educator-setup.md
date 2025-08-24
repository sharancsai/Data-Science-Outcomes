# Setup Guide for Educators

This guide helps educators set up the AWS Learning Agent for their students with no prior agentic agent experience.

## 🎯 Overview

The AWS Learning Agent is designed to help students learn Amazon Web Services through interactive conversations, guided labs, and personalized feedback. As an educator, you can deploy this system for your classroom in multiple ways.

## 🚀 Quick Setup Options

### Option 1: Google Colab (Easiest - 5 minutes)

**Best for**: Individual students, immediate access, no technical setup

1. **Share the Colab link** with students:
   ```
   https://colab.research.google.com/github/sharancsai/Data-Science-Outcomes/blob/main/notebooks/AWS_Learning_Agent_Colab.ipynb
   ```

2. **Student instructions**:
   - Click the link
   - Run all cells in order
   - Start chatting with the agent

**Pros**: Zero setup, immediate access, free
**Cons**: Limited to individual use, requires Google account

### Option 2: GitHub Codespaces (Recommended - 10 minutes)

**Best for**: Classroom deployment, consistent environments, advanced students

1. **Create a classroom setup**:
   - Fork the repository to your GitHub organization
   - Enable Codespaces for your organization
   - Share the repository link with students

2. **Student instructions**:
   - Go to the repository
   - Click "Code" → "Codespaces" → "Create codespace"
   - Wait for automatic setup
   - Follow the quick start instructions

**Pros**: Consistent environment, version control, collaborative
**Cons**: Requires GitHub account, limited free hours

### Option 3: Docker Deployment (Advanced - 30 minutes)

**Best for**: On-premises deployment, full control, large classrooms

1. **Prerequisites**:
   - Docker and Docker Compose installed
   - 8GB RAM minimum per instance
   - Network access for students

2. **Setup steps**:
   ```bash
   # Clone repository
   git clone https://github.com/sharancsai/Data-Science-Outcomes.git
   cd Data-Science-Outcomes
   
   # Start services
   docker-compose -f docker/docker-compose.yml up -d
   
   # Access at:
   # API: http://localhost:8000
   # UI: http://localhost:8501
   ```

**Pros**: Full control, on-premises, scalable
**Cons**: Technical setup required, infrastructure needed

## 🎓 Classroom Integration

### Curriculum Integration

The AWS Learning Agent can be integrated into your AWS curriculum as:

1. **Interactive Tutor**: Students ask questions during lectures
2. **Lab Assistant**: Provides step-by-step guidance for AWS labs
3. **Study Companion**: Helps with homework and review sessions
4. **Assessment Tool**: Track student progress and understanding

### Suggested Learning Path

```
Week 1: Cloud Computing Fundamentals
   └── Agent Introduction + Basic Q&A

Week 2: Amazon EC2
   └── EC2 Basics Lab with Agent Guidance

Week 3: Amazon S3  
   └── S3 Fundamentals Lab with Agent Support

Week 4: Amazon VPC
   └── VPC Configuration Lab with Agent Help

Week 5: Integration Project
   └── Multi-service project with Agent mentoring
```

### Student Management

#### Progress Tracking
- Use the `/progress/{student_id}` endpoint to monitor learning
- Generate reports on student engagement and understanding
- Identify students who need additional help

#### Feedback Collection
- Collect student feedback through the built-in system
- Use feedback to improve teaching methods
- Adapt curriculum based on common questions

## ⚙️ Configuration for Educators

### Model Selection

**For Classroom Use (Recommended)**:
```bash
MODEL_TYPE=huggingface
MODEL_NAME=microsoft/DialoGPT-medium
```
- Free to use
- Good performance
- No local hardware requirements

**For Advanced/Local Deployment**:
```bash
MODEL_TYPE=ollama
MODEL_NAME=llama3.2
```
- Better responses
- Requires powerful hardware
- More control over data

### Environment Variables

Create a `.env` file with your configuration:

```bash
# Model Configuration
MODEL_TYPE=huggingface
MODEL_NAME=microsoft/DialoGPT-medium

# Database (SQLite for simple deployment)
DATABASE_URL=sqlite:///./classroom_aws_agent.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/classroom.log

# Features
FEEDBACK_ENABLED=true
MAX_MEMORY_SIZE=1000
```

### Multi-Student Setup

For multiple students, consider:

1. **Shared Instance**: Single deployment, students use different IDs
2. **Individual Instances**: Each student gets their own environment
3. **Classroom Server**: Central server with student authentication

## 📊 Monitoring and Analytics

### Student Progress Dashboard

Access student analytics via API:

```bash
# Get overall statistics
curl http://localhost:8000/agent/stats

# Get student-specific progress
curl http://localhost:8000/progress/{student_id}

# Get feedback summary
curl http://localhost:8000/feedback/summary?days=30
```

### Common Metrics to Track

- **Engagement**: Number of questions asked
- **Progress**: Lab completion rates
- **Understanding**: Topic knowledge scores
- **Satisfaction**: Student feedback ratings

## 🛠️ Troubleshooting

### Common Issues

**"Agent not responding"**
- Check internet connection for cloud models
- Verify API server is running
- Check logs for error messages

**"Slow responses"**
- Reduce model complexity in configuration
- Check system resources (RAM, CPU)
- Consider using a more powerful deployment option

**"Students can't access"**
- Verify port forwarding for local deployments
- Check firewall settings
- Ensure proper URL sharing

### Getting Help

1. **Documentation**: Check the [docs](.) folder for detailed guides
2. **Issues**: Report problems on [GitHub Issues](https://github.com/sharancsai/Data-Science-Outcomes/issues)
3. **Community**: Join discussions on [GitHub Discussions](https://github.com/sharancsai/Data-Science-Outcomes/discussions)

## 📋 Pre-Class Checklist

Before introducing the agent to students:

- [ ] Test the setup yourself with sample questions
- [ ] Verify all endpoints are accessible
- [ ] Prepare sample questions for demonstration
- [ ] Brief students on appropriate usage
- [ ] Set up progress tracking for your class
- [ ] Test feedback collection mechanism

## 🎯 Best Practices

### For Student Success

1. **Start Simple**: Begin with basic AWS concepts
2. **Encourage Questions**: Create a safe environment for inquiry
3. **Monitor Progress**: Regular check-ins on student advancement
4. **Gather Feedback**: Continuously improve based on student input
5. **Combine Methods**: Use agent alongside traditional teaching

### For System Management

1. **Regular Updates**: Keep the system updated
2. **Backup Data**: Save student progress and feedback
3. **Monitor Resources**: Watch system performance
4. **Security**: Protect student data and privacy
5. **Documentation**: Keep setup notes for future reference

---

**Need help?** Contact us through GitHub Issues or check the troubleshooting section in the main documentation.