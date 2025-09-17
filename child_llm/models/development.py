"""Developmental psychology models for automated generation."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum


class DevelopmentalStage(str, Enum):
    """Piagetian developmental stages."""
    SENSORIMOTOR = "sensorimotor"
    PREOPERATIONAL = "preoperational"
    CONCRETE_OPERATIONAL = "concrete_operational"
    FORMAL_OPERATIONAL = "formal_operational"


class VocabularyBand(BaseModel):
    """Vocabulary constraints by developmental stage."""
    year: int = Field(..., description="Year of development")
    max_tokens: int = Field(..., description="Maximum vocabulary size")
    developmental_stage: DevelopmentalStage = Field(..., description="Piagetian stage")
    cognitive_focus: str = Field(..., description="Primary cognitive development")
    language_characteristics: List[str] = Field(..., description="Language features")
    forbidden_patterns: List[str] = Field(..., description="Patterns to avoid")
    core_vocabulary: List[str] = Field(default_factory=list, description="Core vocabulary words for this stage")


class Milestone(BaseModel):
    """Developmental milestone."""
    week_index: int = Field(..., description="Week number")
    year: int = Field(..., description="Year of development")
    developmental_theme: str = Field(..., description="Primary developmental focus")
    vocabulary_period: str = Field(..., description="Vocabulary constraint")  # Changed from language_band
    milestones: List[str] = Field(default_factory=list, description="Specific milestones")
    dominant_emotions: List[str] = Field(default_factory=list, description="Typical emotions")
    routine_tags: List[str] = Field(default_factory=list, description="Daily routines")
    new_social_actors: List[str] = Field(default_factory=list, description="New people")
    vocabulary_focus: List[str] = Field(default_factory=list, description="Key vocabulary")
    cognitive_focus: str = Field(..., description="Cognitive development focus")
    environment_notes: List[str] = Field(default_factory=list, description="Environmental factors")
    health_state: str = Field("healthy", description="Health status")


class WeeklyTimeline(BaseModel):
    """Complete weekly timeline."""
    weekly_timeline: List[Milestone] = Field(..., description="260 weeks of development")


class DevelopmentalContext(BaseModel):
    """Context for a specific developmental period."""
    year: int = Field(..., description="Year of development")
    month: int = Field(..., description="Month (1-12)")
    week: int = Field(..., description="Week of the year")
    vocabulary_band: VocabularyBand = Field(..., description="Vocabulary constraints")
    cognitive_abilities: List[str] = Field(..., description="Available cognitive abilities")
    social_context: Dict[str, str] = Field(..., description="Social environment")
    typical_activities: List[str] = Field(..., description="Common activities")
    emotional_range: List[str] = Field(..., description="Typical emotions")
    language_patterns: List[str] = Field(..., description="Language patterns to use")
    forbidden_patterns: List[str] = Field(..., description="Patterns to avoid") 