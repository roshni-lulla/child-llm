"""Scenario configuration models."""

from datetime import date, time
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ChildProfile(BaseModel):
    """Child personality and characteristics."""
    name: str = Field(..., description="Child's name")
    birthdate: date = Field(..., description="Birth date")
    sex: str = Field(..., description="Sex assigned at birth")
    personality: Dict[str, float] = Field(
        default_factory=lambda: {"openness": 0.5, "conscientiousness": 0.5, 
                               "extraversion": 0.5, "agreeableness": 0.5, "neuroticism": 0.5},
        description="Big Five personality traits (0-1 scale)"
    )
    temperament_tags: List[str] = Field(
        default_factory=list,
        description="Temperament characteristics"
    )
    special_needs: List[str] = Field(
        default_factory=list,
        description="Any special needs or conditions"
    )


class Caregiver(BaseModel):
    """Primary caregiver information."""
    name: str = Field(..., description="Caregiver's name")
    relation: str = Field(..., description="Relationship to child")
    age: Optional[int] = Field(None, description="Caregiver's age")
    personality: Optional[Dict[str, float]] = Field(None, description="Personality traits")


class Environment(BaseModel):
    """Environmental context."""
    home_type: str = Field("apartment", description="Type of home")
    city: str = Field("Unknown", description="City/location")
    timezone: str = Field("UTC", description="Timezone")
    socioeconomic_status: str = Field("middle", description="SES level")
    cultural_background: str = Field("US", description="Cultural context")
    siblings: List[str] = Field(default_factory=list, description="Sibling names")


class ScenarioMilestone(BaseModel):
    """Developmental milestone."""
    milestone_date: date = Field(..., description="When milestone occurs")
    event: str = Field(..., description="Milestone description")
    category: str = Field("developmental", description="Milestone category")
    impact_level: str = Field("medium", description="Impact on consciousness")


class ScheduledEvent(BaseModel):
    """Scheduled event or activity."""
    event_date: date = Field(..., description="Event date")
    event_time: Optional[time] = Field(None, description="Event time")
    event: str = Field(..., description="Event description")
    category: str = Field("routine", description="Event category")
    participants: List[str] = Field(default_factory=list, description="Who's involved")


class Timeline(BaseModel):
    """Timeline configuration."""
    weekly_plan_file: Optional[str] = Field(None, description="Master timeline file")
    vocabulary_bands: Dict[int, int] = Field(
        default_factory=lambda: {1: 2000, 2: 3000, 3: 5000, 4: 5000, 5: 7000},
        description="Vocabulary limits by year"
    )
    milestones: List[ScenarioMilestone] = Field(default_factory=list, description="Custom milestones")
    scheduled_events: List[ScheduledEvent] = Field(default_factory=list, description="Scheduled events")
    personality_events: List[Dict[str, Any]] = Field(default_factory=list, description="Personality-driven events")


class Scenario(BaseModel):
    """Complete scenario configuration."""
    monologue_id: str = Field(..., description="Unique monologue identifier")
    seed: int = Field(12345, description="Random seed for reproducibility")
    language: str = Field("en-US", description="Primary language")
    culture: str = Field("US", description="Cultural context")
    child_profile: ChildProfile = Field(..., description="Child characteristics")
    caregivers: List[Caregiver] = Field(..., description="Primary caregivers")
    environment: Environment = Field(..., description="Environmental context")
    timeline: Timeline = Field(..., description="Timeline configuration")
    style: Dict[str, str] = Field(
        default_factory=lambda: {
            "sentence_length": "short",
            "tone": "observational", 
            "narrative_continuity": "high"
        },
        description="Writing style preferences"
    ) 