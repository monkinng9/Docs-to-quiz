from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class QuizConfig(BaseModel):
    """Configuration for quiz generation with customizable question counts."""
    
    multiple_choice_count: Optional[int] = Field(
        None, 
        description="Number of multiple choice questions",
        ge=0
    )
    true_false_count: Optional[int] = Field(
        None, 
        description="Number of true/false questions",
        ge=0
    )
    short_answer_count: Optional[int] = Field(
        None, 
        description="Number of short answer questions",
        ge=0
    )
    scenario_count: Optional[int] = Field(
        None, 
        description="Number of scenario-based questions",
        ge=0
    )

    def get_config_text(self) -> str:
        """Generate a formatted string representation of the quiz configuration."""
        config_parts = []
        fields = {
            'multiple_choice_count': 'Multiple Choice Questions',
            'true_false_count': 'True/False Questions',
            'short_answer_count': 'Short Answer Questions',
            'scenario_count': 'Scenario Questions'
        }
        
        for field, label in fields.items():
            value = getattr(self, field)
            if value is not None:
                config_parts.append(f"- {label}: Exactly {value}")
        
        if not config_parts:
            return (
                "Determine appropriate number of questions for each type based on the content complexity "
                "and importance of different topics. Aim for a comprehensive assessment that can be "
                "completed in 30-45 minutes."
            )
        
        return "\n".join(config_parts)


class ExtractedInfo(BaseModel):
    """Structure for storing extracted information from documents."""
    
    main_concepts: List[str] = Field(
        description="List of key concepts from the document"
    )
    supporting_details: Dict[str, List[str]] = Field(
        description="Mapping of concepts to their supporting details"
    )
    technical_terms: Dict[str, str] = Field(
        description="Mapping of technical terms to their definitions"
    )
    relationships: List[str] = Field(
        description="List of relationships between concepts"
    )
    facts: List[str] = Field(
        description="List of important facts from the document"
    )
