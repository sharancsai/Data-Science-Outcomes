# AWS Learning Agent - Knowledge Base

This directory contains the structured knowledge base for the AWS Learning Agent.

## Knowledge Base Structure

```
knowledge_base/
├── services/         # AWS service definitions and information
├── concepts/         # Cloud computing and AWS concepts
├── labs/            # Laboratory exercise definitions
├── glossary/        # AWS terminology and definitions
└── faqs/           # Frequently asked questions
```

## Data Formats

### Service Information (JSON)
```json
{
  "service_name": {
    "description": "Service description",
    "keywords": ["keyword1", "keyword2"],
    "use_cases": ["use case 1", "use case 2"],
    "key_concepts": ["concept1", "concept2"],
    "pricing_model": "pricing information",
    "related_services": ["service1", "service2"]
  }
}
```

### Lab Definitions (JSON)
```json
{
  "lab_id": {
    "title": "Lab title",
    "objective": "What students will learn",
    "duration": "Expected time",
    "difficulty": "beginner|intermediate|advanced",
    "prerequisites": ["requirement1", "requirement2"],
    "steps": ["step 1", "step 2", "..."],
    "verification": "How to verify completion",
    "cleanup": "Cleanup instructions"
  }
}
```

### Concept Definitions (JSON)
```json
{
  "concept_name": {
    "definition": "Clear definition",
    "explanation": "Detailed explanation",
    "examples": ["example1", "example2"],
    "related_concepts": ["concept1", "concept2"],
    "aws_services": ["relevant services"]
  }
}
```

## Adding New Content

1. **Services**: Add new AWS services to `services/aws_services.json`
2. **Labs**: Create lab definitions in `labs/lab_guides.json`
3. **Concepts**: Add explanations to `concepts/aws_concepts.json`
4. **Glossary**: Update `glossary/aws_glossary.json`
5. **FAQs**: Add common questions to `faqs/common_questions.json`

## Content Quality Guidelines

- **Accuracy**: Ensure all information is current and correct
- **Clarity**: Use clear, beginner-friendly language
- **Completeness**: Include all essential information
- **Consistency**: Follow established formats and terminology
- **Examples**: Provide practical, real-world examples
- **Updates**: Keep content current with AWS changes

## Validation

Before adding content:
1. Verify technical accuracy
2. Test any procedures or examples
3. Check for consistency with existing content
4. Ensure proper JSON formatting
5. Review for clarity and completeness