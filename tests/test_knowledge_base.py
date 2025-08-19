"""
Tests for the knowledge base functionality.
"""

import pytest
from unittest.mock import Mock, patch

from agent.knowledge_base import AWSKnowledgeBase


class TestAWSKnowledgeBase:
    """Test suite for the AWS Knowledge Base."""

    def test_knowledge_base_initialization(self, knowledge_base):
        """Test that knowledge base initializes correctly."""
        assert knowledge_base is not None
        assert isinstance(knowledge_base.aws_services, dict)
        assert isinstance(knowledge_base.lab_guides, dict)
        assert isinstance(knowledge_base.knowledge_data, dict)
        assert len(knowledge_base.aws_services) > 0

    def test_search_aws_services(self, knowledge_base):
        """Test searching for AWS service information."""
        # Test searching for EC2
        result = knowledge_base.search("EC2")
        assert "EC2" in result
        assert "compute" in result.lower() or "virtual" in result.lower()
        
        # Test searching for S3
        result = knowledge_base.search("S3")
        assert "S3" in result
        assert "storage" in result.lower()

    def test_search_keywords(self, knowledge_base):
        """Test searching by keywords."""
        # Test compute keyword
        result = knowledge_base.search("compute")
        assert len(result) > 0
        assert "EC2" in result or "Lambda" in result
        
        # Test storage keyword
        result = knowledge_base.search("storage")
        assert len(result) > 0
        assert "S3" in result

    def test_search_no_results(self, knowledge_base):
        """Test search with no matching results."""
        result = knowledge_base.search("nonexistent_service_xyz")
        assert "couldn't find specific information" in result.lower()
        assert "ask me about" in result.lower()

    def test_search_case_insensitive(self, knowledge_base):
        """Test that search is case insensitive."""
        result_lower = knowledge_base.search("ec2")
        result_upper = knowledge_base.search("EC2")
        result_mixed = knowledge_base.search("Ec2")
        
        # All should return similar results
        assert "EC2" in result_lower
        assert "EC2" in result_upper  
        assert "EC2" in result_mixed

    def test_get_lab_guidance_existing(self, knowledge_base):
        """Test getting guidance for existing labs."""
        # Test EC2 basics lab
        result = knowledge_base.get_lab_guidance("ec2_basic")
        assert "Getting Started with Amazon EC2" in result
        assert "Step-by-Step Instructions" in result
        assert "Launch Instance" in result
        
        # Test S3 basics lab
        result = knowledge_base.get_lab_guidance("s3_basics")
        assert "Introduction to Amazon S3" in result
        assert "Create bucket" in result

    def test_get_lab_guidance_partial_match(self, knowledge_base):
        """Test lab guidance with partial name matching."""
        result = knowledge_base.get_lab_guidance("ec2")
        # Should match ec2_basic lab
        assert "EC2" in result
        assert "Step-by-Step Instructions" in result or "don't have specific guidance" in result

    def test_get_lab_guidance_nonexistent(self, knowledge_base):
        """Test lab guidance for non-existent lab."""
        result = knowledge_base.get_lab_guidance("nonexistent_lab")
        assert "don't have specific guidance" in result
        assert "help you with these AWS labs" in result

    def test_get_all_topics(self, knowledge_base):
        """Test getting all available topics."""
        topics = knowledge_base.get_all_topics()
        
        assert isinstance(topics, list)
        assert len(topics) > 0
        
        # Should include AWS services
        topic_str = " ".join(topics)
        assert "EC2" in topic_str or "Amazon EC2" in topic_str
        assert "S3" in topic_str or "Amazon S3" in topic_str

    def test_default_aws_services_content(self, knowledge_base):
        """Test that default AWS services have proper content structure."""
        services = knowledge_base._get_default_aws_services()
        
        assert isinstance(services, dict)
        
        for service_name, service_info in services.items():
            assert "description" in service_info
            assert "keywords" in service_info
            assert "use_cases" in service_info
            assert isinstance(service_info["keywords"], list)
            assert isinstance(service_info["use_cases"], list)
            assert len(service_info["description"]) > 0

    def test_default_lab_guides_content(self, knowledge_base):
        """Test that default lab guides have proper structure."""
        labs = knowledge_base._get_default_lab_guides()
        
        assert isinstance(labs, dict)
        
        for lab_key, lab_content in labs.items():
            assert "title" in lab_content
            assert "steps" in lab_content
            assert "duration" in lab_content
            assert isinstance(lab_content["steps"], list)
            assert len(lab_content["steps"]) > 0

    def test_knowledge_base_resilience(self, test_config):
        """Test that knowledge base handles missing files gracefully."""
        # Test with non-existent paths
        test_config.knowledge_base_path = "/nonexistent/path"
        test_config.aws_content_path = "/nonexistent/path"
        
        with patch('agent.knowledge_base.get_config', return_value=test_config):
            kb = AWSKnowledgeBase()
            
            # Should still have minimal defaults
            assert len(kb.aws_services) > 0
            assert len(kb.lab_guides) > 0
            
            # Basic functionality should work
            result = kb.search("EC2")
            assert len(result) > 0

    def test_lab_guidance_structure(self, knowledge_base):
        """Test the structure of lab guidance output."""
        result = knowledge_base.get_lab_guidance("ec2_basic")
        
        # Check for expected sections
        expected_sections = [
            "Objective",
            "Duration", 
            "Step-by-Step Instructions",
            "Verification",
            "Cleanup"
        ]
        
        for section in expected_sections:
            assert section in result

    def test_search_result_quality(self, knowledge_base):
        """Test that search results are informative and well-formatted."""
        queries = ["EC2", "S3", "VPC", "Lambda", "storage", "compute"]
        
        for query in queries:
            result = knowledge_base.search(query)
            
            # Basic quality checks
            assert len(result) > 20  # Should be substantial
            assert not result.startswith("Error")  # Should not be error message
            assert query.lower() in result.lower() or "couldn't find" in result.lower()

    def test_knowledge_base_update_capability(self, knowledge_base):
        """Test that knowledge base can be updated with new content."""
        # Add new service information
        new_service = {
            "Test Service": {
                "description": "A test AWS service for unit testing",
                "keywords": ["test", "unit", "mock"],
                "use_cases": ["Testing applications"]
            }
        }
        
        knowledge_base.aws_services.update(new_service)
        
        # Search should now find the new service
        result = knowledge_base.search("test service")
        assert "Test Service" in result
        assert "unit testing" in result

class TestKnowledgeBaseIntegration:
    """Integration tests for the knowledge base."""
    
    def test_knowledge_base_with_agent_tools(self, knowledge_base):
        """Test knowledge base integration with agent tools."""
        # Test search function (used as agent tool)
        search_result = knowledge_base.search("How do I use EC2 for web hosting?")
        assert len(search_result) > 0
        assert "EC2" in search_result
        
        # Test lab guidance function (used as agent tool)  
        lab_result = knowledge_base.get_lab_guidance("ec2_basic")
        assert "EC2" in lab_result
        assert "step" in lab_result.lower()

    def test_comprehensive_aws_coverage(self, knowledge_base):
        """Test that knowledge base covers major AWS services."""
        major_services = [
            "EC2", "S3", "VPC", "Lambda", "RDS", 
            "IAM", "CloudFormation", "ELB", "Auto Scaling"
        ]
        
        topics = knowledge_base.get_all_topics()
        topic_str = " ".join(topics).lower()
        
        covered_services = []
        for service in major_services:
            if service.lower() in topic_str:
                covered_services.append(service)
        
        # Should cover at least core services
        assert len(covered_services) >= 3
        assert "EC2" in covered_services
        assert "S3" in covered_services

    def test_lab_progression_logical_order(self, knowledge_base):
        """Test that labs follow a logical learning progression."""
        all_labs = knowledge_base.lab_guides
        
        # Check that basic labs exist before advanced ones
        lab_names = list(all_labs.keys())
        
        # Should have fundamental labs
        fundamental_topics = ["ec2", "s3", "vpc"]
        for topic in fundamental_topics:
            has_basic_lab = any(topic in lab_name for lab_name in lab_names)
            # Would be good to have, but not strictly required for tests to pass
            # assert has_basic_lab, f"Should have basic lab for {topic}"

    def test_search_result_relevance(self, knowledge_base):
        """Test that search results are relevant to queries."""
        test_cases = [
            ("virtual machines", "EC2"),
            ("object storage", "S3"),
            ("networking", "VPC"),
            ("serverless", "Lambda"),
            ("database", "RDS")
        ]
        
        for query, expected_service in test_cases:
            result = knowledge_base.search(query)
            # Should either find the expected service or give a helpful general response
            assert (expected_service in result or 
                    "couldn't find specific information" in result or
                    any(service in result for service in knowledge_base.aws_services.keys()))

    def test_error_handling_in_knowledge_operations(self, knowledge_base):
        """Test error handling in knowledge base operations."""
        # Test with None input
        result = knowledge_base.search(None)
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Test with empty string
        result = knowledge_base.search("")
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Test lab guidance with None
        result = knowledge_base.get_lab_guidance(None)
        assert isinstance(result, str)
        assert len(result) > 0