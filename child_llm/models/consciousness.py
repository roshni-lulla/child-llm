"""Consciousness component models for the monologue."""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ConsciousnessEntry(BaseModel):
    """Enhanced consciousness components per minute based on developmental psychology."""
    # Core sensory-motor components (Piaget's sensorimotor stage)
    sensory_perception: str = Field(..., description="External stimuli: sights, sounds, touches, smells")
    interoception: str = Field(..., description="Internal bodily states: hunger, comfort, temperature, pain")
    attention_focus: str = Field(..., description="What captures attention: faces, objects, sounds, movement")
    intention_motive: str = Field(..., description="Action tendencies: reach, grasp, vocalize, seek comfort")
    
    # Social and environmental components (Vygotsky, Bowlby)
    social_interaction: str = Field(..., description="Social context: caregiver presence, eye contact, touch")
    vocalization: str = Field(..., description="Vocal expressions: crying, cooing, babbling, silence")
    motor_behavior: str = Field(..., description="Physical actions: reaching, grasping, kicking, turning")
    emotional_expression: str = Field(..., description="Emotional displays: smiling, frowning, alertness, distress")
    
    # Environmental learning (cause-effect, object permanence)
    environmental_learning: str = Field(..., description="Learning experiences: cause-effect, object permanence, patterns")
    
    # Meta-cognitive awareness (age-appropriate)
    reflective_awareness: str = Field(..., description="Awareness of experience: varies by developmental stage")


class MinuteEntry(BaseModel):
    """One minute of consciousness with labels."""
    minute: int = Field(..., description="Minute of the hour (0-59)")
    consciousness_components: ConsciousnessEntry = Field(..., description="Five consciousness components")
    labels: Dict[str, str] = Field(
        default_factory=lambda: {
            "arousal_level": "medium",
            "dominant_emotion": "neutral",
            "cognitive_load": "minimal",
            "social_context": "alone",
            "language_complexity": "simple"
        },
        description="Categorical labels for analysis"
    )


class HourChunk(BaseModel):
    """One hour of consciousness (60 minutes)."""
    hour: int = Field(..., description="Hour of the day (0-23)")
    state_summary: Dict[str, Any] = Field(
        default_factory=lambda: {
            "sleep_state": "awake",
            "dominant_emotions": ["neutral"],  # Changed to list
            "vocabulary_period": "1.1",  # Use vocabulary period instead of hardcoded band
            "context_tags": [],  # Already a list
            "developmental_focus": "sensory_integration"
        },
        description="Summary of the hour's state"
    )
    entries: List[MinuteEntry] = Field(..., description="60 minute entries")


class DayFile(BaseModel):
    """Complete day of consciousness."""
    monologue_id: str = Field(..., description="Monologue identifier")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    provenance: Dict[str, str] = Field(
        default_factory=lambda: {
            "model": "gpt-4o-mini",
            "prompt_version": "consciousness.v1",
            "temperature": "0.6",
            "seed": "12345"
        },
        description="Generation metadata"
    )
    hour_chunks: List[HourChunk] = Field(..., description="24 hour chunks") 