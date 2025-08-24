"""
AWS Knowledge Base Module

Provides AWS learning content, lab guidance, and educational resources
for the agentic learning assistant.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

from ..configs.config import get_config

logger = logging.getLogger(__name__)

class AWSKnowledgeBase:
    """
    AWS Knowledge Base containing learning content, lab instructions,
    and educational resources for AWS services.
    """
    
    def __init__(self):
        self.config = get_config()
        self.knowledge_data = {}
        self.lab_guides = {}
        self.aws_services = {}
        
        # Load knowledge base content
        self._load_knowledge_base()
        logger.info("AWS Knowledge Base initialized")
    
    def _load_knowledge_base(self):
        """Load AWS knowledge base content from data files."""
        try:
            # Create default knowledge base if files don't exist
            knowledge_base_path = Path(self.config.knowledge_base_path)
            
            if not knowledge_base_path.exists():
                self._create_default_knowledge_base()
            
            # Load AWS services information
            self.aws_services = self._get_default_aws_services()
            
            # Load lab guides
            self.lab_guides = self._get_default_lab_guides()
            
            # Load general knowledge data
            self.knowledge_data = self._get_default_knowledge_data()
            
            logger.info("Knowledge base loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
            # Use minimal default data
            self._load_minimal_defaults()
    
    def search(self, query: str) -> str:
        """
        Search the knowledge base for AWS-related information.
        
        Args:
            query: Search query string
            
        Returns:
            Relevant information from the knowledge base
        """
        try:
            query_lower = query.lower()
            results = []
            
            # Search AWS services
            for service, info in self.aws_services.items():
                if (query_lower in service.lower() or 
                    any(query_lower in desc.lower() for desc in info.get("description", "").split()) or
                    any(query_lower in keyword.lower() for keyword in info.get("keywords", []))):
                    
                    result = f"**{service}**: {info.get('description', 'No description available')}"
                    if info.get("use_cases"):
                        result += f"\n\nCommon use cases:\n" + "\n".join(f"• {uc}" for uc in info["use_cases"][:3])
                    results.append(result)
            
            # Search knowledge data
            for topic, content in self.knowledge_data.items():
                if query_lower in topic.lower() or query_lower in content.get("content", "").lower():
                    results.append(f"**{topic}**: {content.get('content', '')}")
            
            if results:
                return "\n\n".join(results[:3])  # Return top 3 results
            else:
                return f"I couldn't find specific information about '{query}' in my knowledge base. However, I can help you with general AWS concepts, services like EC2, S3, VPC, Lambda, and more. Please ask me about a specific AWS service or concept!"
                
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return "I encountered an error while searching. Please try rephrasing your question."
    
    def get_lab_guidance(self, lab_name: str) -> str:
        """
        Get step-by-step guidance for AWS lab exercises.
        
        Args:
            lab_name: Name of the lab
            
        Returns:
            Lab guidance and instructions
        """
        try:
            # Normalize lab name
            lab_name_lower = lab_name.lower()
            
            # Find matching lab
            for lab_key, lab_content in self.lab_guides.items():
                if lab_name_lower in lab_key.lower() or any(lab_name_lower in keyword.lower() for keyword in lab_content.get("keywords", [])):
                    
                    guidance = f"## {lab_content['title']}\n\n"
                    guidance += f"**Objective**: {lab_content.get('objective', 'Learn AWS concepts hands-on')}\n\n"
                    guidance += f"**Duration**: {lab_content.get('duration', '30-45 minutes')}\n\n"
                    
                    if lab_content.get("prerequisites"):
                        guidance += "**Prerequisites**:\n"
                        guidance += "\n".join(f"• {prereq}" for prereq in lab_content["prerequisites"])
                        guidance += "\n\n"
                    
                    guidance += "**Step-by-Step Instructions**:\n"
                    for i, step in enumerate(lab_content.get("steps", []), 1):
                        guidance += f"{i}. {step}\n"
                    
                    if lab_content.get("verification"):
                        guidance += f"\n**Verification**: {lab_content['verification']}\n"
                    
                    if lab_content.get("cleanup"):
                        guidance += f"\n**Cleanup**: {lab_content['cleanup']}\n"
                    
                    return guidance
            
            # If no specific lab found, provide general guidance
            return f"I don't have specific guidance for '{lab_name}' lab, but I can help you with these AWS labs:\n\n" + \
                   "\n".join(f"• {lab['title']}" for lab in self.lab_guides.values()) + \
                   "\n\nPlease specify which lab you'd like help with, or ask about specific AWS services!"
                   
        except Exception as e:
            logger.error(f"Error getting lab guidance: {str(e)}")
            return "I encountered an error while retrieving lab guidance. Please try again."
    
    def get_all_topics(self) -> List[str]:
        """Get all available knowledge base topics."""
        topics = list(self.aws_services.keys()) + list(self.knowledge_data.keys()) + list(self.lab_guides.keys())
        return topics
    
    def _create_default_knowledge_base(self):
        """Create default knowledge base directories and files."""
        try:
            knowledge_base_path = Path(self.config.knowledge_base_path)
            aws_content_path = Path(self.config.aws_content_path)
            
            knowledge_base_path.mkdir(parents=True, exist_ok=True)
            aws_content_path.mkdir(parents=True, exist_ok=True)
            
            # Create default files with basic AWS content
            services_file = knowledge_base_path / "aws_services.json"
            if not services_file.exists():
                with open(services_file, 'w') as f:
                    json.dump(self._get_default_aws_services(), f, indent=2)
            
            labs_file = aws_content_path / "lab_guides.json"
            if not labs_file.exists():
                with open(labs_file, 'w') as f:
                    json.dump(self._get_default_lab_guides(), f, indent=2)
            
            logger.info("Default knowledge base created")
            
        except Exception as e:
            logger.error(f"Error creating default knowledge base: {str(e)}")
    
    def _get_default_aws_services(self) -> Dict[str, Any]:
        """Get default AWS services information."""
        return {
            "Amazon EC2": {
                "description": "Amazon Elastic Compute Cloud (EC2) provides scalable virtual servers in the cloud. It allows you to launch and manage virtual machines with various configurations.",
                "keywords": ["compute", "virtual machine", "server", "instance"],
                "use_cases": [
                    "Web application hosting",
                    "Batch processing",
                    "High-performance computing",
                    "Development and testing environments"
                ],
                "key_concepts": ["AMI", "Instance Types", "Security Groups", "Key Pairs", "EBS Volumes"]
            },
            "Amazon S3": {
                "description": "Amazon Simple Storage Service (S3) is object storage built to store and retrieve any amount of data from anywhere on the Internet. It's designed for 99.999999999% durability.",
                "keywords": ["storage", "bucket", "object", "file"],
                "use_cases": [
                    "Static website hosting",
                    "Data backup and archiving",
                    "Content distribution",
                    "Data lakes and analytics"
                ],
                "key_concepts": ["Buckets", "Objects", "Storage Classes", "Access Control", "Versioning"]
            },
            "Amazon VPC": {
                "description": "Amazon Virtual Private Cloud (VPC) lets you provision a logically isolated section of the AWS Cloud where you can launch AWS resources in a virtual network that you define.",
                "keywords": ["network", "subnet", "vpc", "routing"],
                "use_cases": [
                    "Secure cloud networks",
                    "Multi-tier applications",
                    "Hybrid cloud connectivity",
                    "Isolated development environments"
                ],
                "key_concepts": ["Subnets", "Route Tables", "Internet Gateway", "NAT Gateway", "Security Groups"]
            },
            "AWS Lambda": {
                "description": "AWS Lambda is a serverless compute service that runs your code in response to events and automatically manages the underlying compute resources.",
                "keywords": ["serverless", "function", "event", "compute"],
                "use_cases": [
                    "API backends",
                    "Data processing",
                    "Automated workflows",
                    "Real-time file processing"
                ],
                "key_concepts": ["Functions", "Triggers", "Runtime", "Layers", "Environment Variables"]
            },
            "Amazon RDS": {
                "description": "Amazon Relational Database Service (RDS) makes it easy to set up, operate, and scale a relational database in the cloud.",
                "keywords": ["database", "mysql", "postgresql", "oracle", "sql"],
                "use_cases": [
                    "Web applications",
                    "E-commerce platforms",
                    "Data warehousing",
                    "Content management systems"
                ],
                "key_concepts": ["DB Instances", "Multi-AZ", "Read Replicas", "Snapshots", "Parameter Groups"]
            }
        }
    
    def _get_default_lab_guides(self) -> Dict[str, Any]:
        """Get default lab guides."""
        return {
            "ec2_basic": {
                "title": "Getting Started with Amazon EC2",
                "objective": "Learn to launch, configure, and manage EC2 instances",
                "duration": "45 minutes",
                "difficulty": "Beginner",
                "prerequisites": [
                    "AWS account with appropriate permissions",
                    "Basic understanding of cloud computing concepts"
                ],
                "keywords": ["ec2", "instance", "launch", "virtual machine"],
                "steps": [
                    "Log into the AWS Management Console and navigate to EC2",
                    "Click 'Launch Instance' to start the instance creation wizard",
                    "Choose an Amazon Machine Image (AMI) - select Amazon Linux 2",
                    "Select an instance type (t2.micro for free tier)",
                    "Configure instance details (use defaults for now)",
                    "Add storage (8GB gp2 root volume is sufficient)",
                    "Add tags (Name: MyFirstInstance)",
                    "Configure security group (allow SSH access from your IP)",
                    "Review and launch the instance",
                    "Create or select a key pair for SSH access",
                    "Wait for the instance to reach 'running' state",
                    "Connect to your instance using SSH"
                ],
                "verification": "Successfully SSH into the instance and run 'uptime' command",
                "cleanup": "Terminate the instance to avoid charges"
            },
            "s3_basics": {
                "title": "Introduction to Amazon S3",
                "objective": "Learn to create buckets, upload objects, and configure basic settings",
                "duration": "30 minutes",
                "difficulty": "Beginner",
                "prerequisites": [
                    "AWS account with S3 permissions"
                ],
                "keywords": ["s3", "bucket", "storage", "upload"],
                "steps": [
                    "Navigate to Amazon S3 in the AWS Console",
                    "Click 'Create bucket'",
                    "Choose a globally unique bucket name",
                    "Select an AWS Region",
                    "Configure bucket settings (keep defaults for now)",
                    "Create the bucket",
                    "Upload a test file to the bucket",
                    "Set object permissions and properties",
                    "Access the object via the S3 URL",
                    "Enable versioning on the bucket",
                    "Upload a new version of the same file",
                    "Explore different storage classes"
                ],
                "verification": "Access uploaded files via S3 URL and verify versioning works",
                "cleanup": "Delete all objects and then delete the bucket"
            },
            "vpc_setup": {
                "title": "Creating a Virtual Private Cloud",
                "objective": "Build a basic VPC with public and private subnets",
                "duration": "60 minutes",
                "difficulty": "Intermediate",
                "prerequisites": [
                    "Understanding of networking concepts",
                    "Completed EC2 basics lab"
                ],
                "keywords": ["vpc", "subnet", "networking", "routing"],
                "steps": [
                    "Go to VPC service in AWS Console",
                    "Create a new VPC with CIDR block 10.0.0.0/16",
                    "Create a public subnet (10.0.1.0/24)",
                    "Create a private subnet (10.0.2.0/24)",
                    "Create an Internet Gateway and attach to VPC",
                    "Create a custom route table for public subnet",
                    "Add route to Internet Gateway in public route table",
                    "Associate public subnet with public route table",
                    "Launch EC2 instance in public subnet",
                    "Configure security groups for web access",
                    "Test connectivity to instance",
                    "Create NAT Gateway in public subnet",
                    "Configure private route table with NAT Gateway route"
                ],
                "verification": "Successfully access EC2 instance in public subnet and verify internet connectivity",
                "cleanup": "Terminate instances, delete NAT Gateway, Internet Gateway, and VPC"
            }
        }
    
    def _get_default_knowledge_data(self) -> Dict[str, Any]:
        """Get default general knowledge data."""
        return {
            "AWS Basics": {
                "content": "Amazon Web Services (AWS) is a comprehensive cloud computing platform that offers over 200 services including compute, storage, networking, databases, analytics, and more. AWS follows a pay-as-you-go pricing model and provides global infrastructure with multiple regions and availability zones."
            },
            "Cloud Computing Fundamentals": {
                "content": "Cloud computing is the delivery of computing services over the internet. The main service models are IaaS (Infrastructure as a Service), PaaS (Platform as a Service), and SaaS (Software as a Service). Benefits include cost savings, scalability, reliability, and global reach."
            },
            "AWS Free Tier": {
                "content": "AWS Free Tier provides free access to AWS services with usage limits. It includes 12 months free for services like EC2 (750 hours/month), S3 (5GB storage), and RDS (750 hours/month). Some services like Lambda and DynamoDB offer always-free tiers."
            },
            "Security Best Practices": {
                "content": "AWS security best practices include using IAM roles instead of access keys, enabling MFA, following the principle of least privilege, encrypting data at rest and in transit, regularly rotating credentials, and monitoring with CloudTrail."
            }
        }
    
    def _load_minimal_defaults(self):
        """Load minimal default data if file loading fails."""
        self.aws_services = {
            "Amazon EC2": {
                "description": "Virtual servers in the cloud",
                "keywords": ["compute", "server"],
                "use_cases": ["Web hosting", "Applications"]
            },
            "Amazon S3": {
                "description": "Object storage service",
                "keywords": ["storage", "files"],
                "use_cases": ["File storage", "Backups"]
            }
        }
        
        self.lab_guides = {
            "basic_ec2": {
                "title": "Basic EC2 Lab",
                "steps": ["Launch EC2 instance", "Connect via SSH", "Install software"],
                "duration": "30 minutes"
            }
        }
        
        self.knowledge_data = {
            "AWS Basics": {
                "content": "AWS is Amazon's cloud computing platform offering various services."
            }
        }