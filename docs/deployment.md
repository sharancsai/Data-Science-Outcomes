# Deployment Instructions

This guide covers all deployment options for the AWS Learning Agent, from simple cloud deployments to enterprise-scale installations.

## 🌟 Deployment Overview

Choose the deployment option that best fits your needs:

| Deployment Type | Best For | Setup Time | Technical Level | Cost |
|----------------|----------|------------|-----------------|------|
| Google Colab | Individual learners | 2 minutes | Beginner | Free |
| GitHub Codespaces | Small classes | 5 minutes | Intermediate | Free tier available |
| Docker Local | On-premises | 15 minutes | Advanced | Infrastructure costs |
| Cloud VM | Large deployments | 30 minutes | Expert | Cloud hosting costs |

## 🚀 Quick Deployments

### Google Colab Deployment

**Prerequisites**: Google account

**Steps**:
1. Access the notebook: [AWS Learning Agent Colab](https://colab.research.google.com/github/sharancsai/Data-Science-Outcomes/blob/main/notebooks/AWS_Learning_Agent_Colab.ipynb)
2. Run all cells in order
3. Follow the interactive setup

**Features**:
- ✅ Zero setup required
- ✅ Free to use
- ✅ Immediate access
- ❌ Limited to individual use
- ❌ No persistent storage

### GitHub Codespaces Deployment

**Prerequisites**: GitHub account

**Steps**:
1. Go to the [repository](https://github.com/sharancsai/Data-Science-Outcomes)
2. Click "Code" → "Codespaces" → "Create codespace on main"
3. Wait for automatic environment setup
4. Start the services:
   ```bash
   # Start API server
   python api_server.py &
   
   # Start Streamlit UI
   streamlit run streamlit_app.py
   ```

**Features**:
- ✅ Pre-configured environment
- ✅ Version control integration
- ✅ Collaborative features
- ✅ Free tier available (60 hours/month)
- ❌ Requires GitHub account

## 🐳 Docker Deployments

### Single Container Deployment

**Prerequisites**: Docker installed

**Quick Start**:
```bash
# Clone repository
git clone https://github.com/sharancsai/Data-Science-Outcomes.git
cd Data-Science-Outcomes

# Build and run
docker build -f docker/Dockerfile -t aws-learning-agent .
docker run -p 8000:8000 aws-learning-agent
```

**Access**: http://localhost:8000

### Multi-Service Deployment (Recommended)

**Prerequisites**: Docker and Docker Compose

**Setup**:
```bash
# Clone repository
git clone https://github.com/sharancsai/Data-Science-Outcomes.git
cd Data-Science-Outcomes

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Check status
docker-compose -f docker/docker-compose.yml ps
```

**Services**:
- API Server: http://localhost:8000
- Streamlit UI: http://localhost:8501
- Ollama (optional): http://localhost:11434

**Configuration**:
Create a `docker/.env` file:
```bash
MODEL_TYPE=huggingface
MODEL_NAME=microsoft/DialoGPT-medium
DATABASE_URL=sqlite:///./aws_agent.db
ENVIRONMENT=production
```

### Docker with Ollama (Local Models)

**Prerequisites**: Docker, 16GB RAM, preferably GPU

**Setup**:
```bash
# Start with Ollama support
docker-compose -f docker/docker-compose.yml up -d

# Install a model (in the ollama container)
docker exec -it ollama ollama pull llama3.2

# Update configuration
MODEL_TYPE=ollama
MODEL_NAME=llama3.2
OLLAMA_BASE_URL=http://ollama:11434
```

## ☁️ Cloud Deployments

### AWS EC2 Deployment

**Prerequisites**: AWS account, EC2 access

**Instance Requirements**:
- Instance Type: t3.large or larger (for HuggingFace models)
- Instance Type: g4dn.xlarge or larger (for Ollama with GPU)
- Storage: 20GB EBS volume
- Security Group: Ports 8000, 8501 open

**Setup Script**:
```bash
#!/bin/bash
# EC2 User Data Script

# Update system
sudo yum update -y
sudo yum install -y docker git

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and setup
cd /home/ec2-user
git clone https://github.com/sharancsai/Data-Science-Outcomes.git
cd Data-Science-Outcomes

# Configure for cloud deployment
cat > docker/.env << EOF
MODEL_TYPE=huggingface
MODEL_NAME=microsoft/DialoGPT-medium
DATABASE_URL=sqlite:///./aws_agent.db
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
EOF

# Start services
docker-compose -f docker/docker-compose.yml up -d

echo "Deployment complete!"
echo "API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo "UI: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501"
```

### Google Cloud Platform (GCP) Deployment

**Prerequisites**: GCP account, Cloud Run access

**Using Cloud Run**:
```bash
# Build and push container
gcloud builds submit --tag gcr.io/PROJECT_ID/aws-learning-agent

# Deploy to Cloud Run
gcloud run deploy aws-learning-agent \
  --image gcr.io/PROJECT_ID/aws-learning-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000
```

### Azure Container Instances

**Prerequisites**: Azure account, Container Instances access

**Deployment**:
```bash
# Create resource group
az group create --name aws-learning-agent --location eastus

# Create container instance
az container create \
  --resource-group aws-learning-agent \
  --name aws-learning-agent \
  --image your-registry/aws-learning-agent:latest \
  --dns-name-label aws-learning-agent \
  --ports 8000 8501
```

## 🔧 Advanced Configurations

### Environment Variables

Create a comprehensive `.env` file:

```bash
# Model Configuration
MODEL_TYPE=huggingface                    # or ollama
MODEL_NAME=microsoft/DialoGPT-medium      # or llama3.2
OLLAMA_BASE_URL=http://localhost:11434
HUGGINGFACE_API_KEY=your_key_here         # if using HF API

# Database Configuration  
DATABASE_URL=sqlite:///./aws_agent.db     # or PostgreSQL URL
# DATABASE_URL=postgresql://user:pass@localhost:5432/awsagent

# Agent Configuration
AGENT_NAME=AWS Learning Assistant
MAX_MEMORY_SIZE=1000
FEEDBACK_ENABLED=true

# AWS Content Paths
AWS_CONTENT_PATH=./data/aws_content
KNOWLEDGE_BASE_PATH=./data/knowledge_base

# Server Configuration
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
LOG_FILE=./logs/agent.log

# Security (for production)
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,localhost
```

### Database Configurations

#### SQLite (Default)
```bash
DATABASE_URL=sqlite:///./aws_agent.db
```

#### PostgreSQL
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Configure
DATABASE_URL=postgresql://username:password@localhost:5432/aws_learning_agent
```

#### MySQL
```bash
# Install MySQL driver
pip install pymysql

# Configure
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/aws_learning_agent
```

### Load Balancer Configuration

For high-traffic deployments, use a load balancer:

**Nginx Configuration** (`nginx.conf`):
```nginx
upstream aws_learning_agent {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://aws_learning_agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /streamlit {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 🛡️ Security Considerations

### Production Security Checklist

- [ ] Use HTTPS/TLS encryption
- [ ] Implement authentication and authorization
- [ ] Set up proper firewall rules
- [ ] Use environment variables for secrets
- [ ] Enable logging and monitoring
- [ ] Regular security updates
- [ ] Input validation and sanitization
- [ ] Rate limiting implementation

### Authentication Setup

**Basic HTTP Authentication**:
```python
# In api_server.py, add:
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, status

security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    # Implement your authentication logic here
    if credentials.username != "admin" or credentials.password != "secret":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return credentials.username
```

## 📊 Monitoring and Logging

### Application Logging

Configure logging in your deployment:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### Health Monitoring

Set up health checks:

```bash
# Simple health check script
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ $response -eq 200 ]; then
    echo "Service is healthy"
    exit 0
else
    echo "Service is unhealthy"
    exit 1
fi
```

### Performance Monitoring

Monitor key metrics:
- Response time
- Memory usage
- CPU utilization
- Database connection pool
- Active user sessions

## 🔄 Updates and Maintenance

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up --build -d

# Check health
curl http://localhost:8000/health
```

### Database Migrations

```bash
# Backup database before updates
cp aws_agent.db aws_agent.db.backup

# Run any migration scripts
python scripts/migrate_database.py

# Verify data integrity
python scripts/verify_data.py
```

### Scaling Considerations

For growing usage:

1. **Horizontal Scaling**: Add more application instances
2. **Database Scaling**: Move to managed database service
3. **Caching**: Implement Redis for session storage
4. **CDN**: Use CloudFront/CloudFlare for static assets
5. **Auto-scaling**: Use container orchestration (Kubernetes)

## 🆘 Troubleshooting

### Common Issues

**Port conflicts**:
```bash
# Check what's using the port
netstat -tulpn | grep :8000
# Kill the process if needed
sudo kill -9 PID
```

**Memory issues**:
```bash
# Check memory usage
free -h
# Monitor container memory
docker stats
```

**Model loading failures**:
```bash
# Check model cache
ls ~/.cache/huggingface/
# Clear cache if corrupted
rm -rf ~/.cache/huggingface/
```

**Database connection issues**:
```bash
# Check database file permissions
ls -la aws_agent.db
# Reset database if corrupted
rm aws_agent.db
python -c "from configs.config import setup_directories; setup_directories()"
```

### Deployment Verification

After deployment, verify:

```bash
# Health check
curl http://localhost:8000/health

# API functionality
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"student_id": "test", "message": "Hello"}'

# UI accessibility
curl http://localhost:8501

# Database connectivity
curl http://localhost:8000/agent/stats
```

---

**Need help?** Check the troubleshooting section or create an issue on GitHub for deployment-specific problems.