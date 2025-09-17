"""Deterministic planner for hour-level consciousness generation."""

import hashlib
import json
from datetime import date, datetime, time
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..models.scenario import Scenario
from ..models.development import DevelopmentalContext
from ..models.consciousness import HourChunk


class HourPlanner:
    """Plans hour-level context for consciousness generation."""
    
    def __init__(self):
        self.sleep_patterns = {
            "newborn": {"sleep_hours": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]},
            "infant": {"sleep_hours": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]},
            "toddler": {"sleep_hours": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]},
            "preschool": {"sleep_hours": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]},
            "school_age": {"sleep_hours": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]}
        }
    
    def plan_day(self, scenario: Scenario, target_date: date, timeline_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan 24 hours for a specific day."""
        # Calculate child's age
        age_days = (target_date - scenario.child_profile.birthdate).days
        age_years = age_days // 365
        
        # Get weekly context
        week_index = self._get_week_index(target_date, scenario.child_profile.birthdate)
        weekly_context = self._get_weekly_context(week_index, timeline_data)
        
        # Plan each hour
        hour_plans = []
        for hour in range(24):
            hour_plan = self._plan_hour(
                hour=hour,
                age_years=age_years,
                weekly_context=weekly_context,
                scenario=scenario,
                target_date=target_date
            )
            hour_plans.append(hour_plan)
        
        return hour_plans
    
    def _get_week_index(self, target_date: date, birthdate: date) -> int:
        """Calculate week index from birth."""
        days_since_birth = (target_date - birthdate).days
        return (days_since_birth // 7) + 1
    
    def _get_weekly_context(self, week_index: int, timeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get weekly developmental context."""
        weekly_timeline = timeline_data.get("weekly_timeline", [])
        
        # Find the week entry
        week_entry = None
        for entry in weekly_timeline:
            if entry.get("week_index") == week_index:
                week_entry = entry
                break
        
        if not week_entry:
            # Default developmental context
            default_context = {
                "developmental_stage": "sensorimotor",
                "cognitive_focus": "sensory_integration",
                "vocabulary_period": "1.1",  # Use vocabulary period instead of hardcoded band
                "language_characteristics": ["cooing", "babbling"],
                "forbidden_patterns": ["complex sentences", "abstract concepts"],
                "typical_activities": ["sleeping", "feeding", "sensory exploration"],
                "emotional_range": ["calm", "discomfort", "curiosity"]
            }
            return default_context
        
        return week_entry
    
    def _plan_hour(self, hour: int, age_years: int, weekly_context: Dict[str, Any], 
                   scenario: Scenario, target_date: date) -> Dict[str, Any]:
        """Plan a specific hour."""
        # Determine sleep state
        sleep_state = self._determine_sleep_state(hour, age_years)
        
        # Get developmental context
        developmental_context = self._get_developmental_context(weekly_context)
        
        # Get environmental context
        environmental_context = self._get_environmental_context(hour, target_date, scenario)
        
        # Get social context
        social_context = self._get_social_context(hour, scenario)
        
        # Get emotional context
        emotional_context = self._get_emotional_context(hour, weekly_context, scenario)
        
        # Calculate week index for this date
        week_index = self._get_week_index(target_date, scenario.child_profile.birthdate)
        
        # Create hour plan
        hour_plan = {
            "hour": hour,
            "year": age_years,  # Add year field
            "week": week_index,  # Add week field
            "sleep_state": sleep_state,
            "developmental_context": developmental_context,
            "environmental_context": environmental_context,
            "social_context": social_context,
            "emotional_context": emotional_context,
            "language_constraints": self._get_language_constraints(age_years),
            "cognitive_abilities": self._get_cognitive_abilities(age_years),
            "typical_activities": self._get_typical_activities(hour, age_years),
            "forbidden_patterns": self._get_forbidden_patterns(age_years)
        }
        
        # Add content hash for idempotency
        hour_plan["content_hash"] = self._compute_content_hash(hour_plan)
        
        return hour_plan
    
    def _determine_sleep_state(self, hour: int, age_years: int) -> str:
        """Determine sleep state for the hour."""
        if age_years == 0:  # Newborn
            if hour in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]:
                return "asleep"
        elif age_years == 1:  # Infant
            if hour in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]:
                return "asleep"
        elif age_years == 2:  # Toddler
            if hour in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]:
                return "asleep"
        elif age_years == 3:  # Preschool
            if hour in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]:
                return "asleep"
        elif age_years == 4:  # School age
            if hour in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]:
                return "asleep"
        
        return "awake"
    
    def _get_developmental_context(self, weekly_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get developmental context for the hour."""
        return {
            "developmental_theme": weekly_context.get("developmental_theme", "sensory_integration"),
            "cognitive_focus": weekly_context.get("cognitive_focus", "pattern_recognition"),
            "vocabulary_period": weekly_context.get("vocabulary_period", "1.1"),  # Use vocabulary_period field
            "milestones": weekly_context.get("milestones", []),
            "vocabulary_focus": weekly_context.get("vocabulary_focus", []),
            "dominant_emotions": weekly_context.get("dominant_emotions", ["curiosity"]),  # Add missing field
            "routine_tags": weekly_context.get("routine_tags", ["daily routine"]),
            "forbidden_patterns": weekly_context.get("forbidden_patterns", ["complex_sentences", "abstract_concepts"])
        }
    
    def _get_environmental_context(self, hour: int, target_date: date, scenario: Scenario) -> Dict[str, Any]:
        """Get environmental context for the hour."""
        # Simple environmental patterns
        if 6 <= hour <= 8:
            time_of_day = "morning"
        elif 12 <= hour <= 14:
            time_of_day = "afternoon"
        elif 18 <= hour <= 20:
            time_of_day = "evening"
        elif 22 <= hour or hour <= 6:
            time_of_day = "night"
        else:
            time_of_day = "day"
        
        return {
            "time_of_day": time_of_day,
            "season": self._get_season(target_date),
            "weather": "typical",  # Could be randomized
            "location": scenario.environment.home_type,
            "temperature": "comfortable"
        }
    
    def _get_social_context(self, hour: int, scenario: Scenario) -> Dict[str, Any]:
        """Get social context for the hour."""
        caregivers_present = []
        
        # Simple caregiver presence logic
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            caregivers_present = [c.name for c in scenario.caregivers]
        elif 9 <= hour <= 17:
            # Some caregivers might be at work
            caregivers_present = [scenario.caregivers[0].name]  # Primary caregiver
        else:
            caregivers_present = [scenario.caregivers[0].name]  # Primary caregiver
        
        return {
            "caregivers_present": caregivers_present,
            "social_interaction_level": "high" if caregivers_present else "low",
            "other_children": []  # Could be expanded
        }
    
    def _get_emotional_context(self, hour: int, weekly_context: Dict[str, Any], scenario: Scenario) -> Dict[str, Any]:
        """Get emotional context for the hour."""
        base_emotions = weekly_context.get("dominant_emotions", ["curiosity"])
        
        # Add personality-driven emotions
        personality = scenario.child_profile.personality
        temperament = scenario.child_profile.temperament_tags
        
        additional_emotions = []
        if "sensitive_to_noise" in temperament and hour in [8, 18]:  # Busy hours
            additional_emotions.append("overwhelmed")
        
        if personality.get("extraversion", 0.5) > 0.7:
            additional_emotions.append("excited")
        
        return {
            "dominant_emotions": base_emotions + additional_emotions,
            "arousal_level": "medium",
            "emotional_stability": "stable"
        }
    
    def _get_language_constraints(self, age_years: int) -> Dict[str, Any]:
        """Get language constraints for the age."""
        constraints = {
            0: {"max_sentence_length": 3, "forbidden_patterns": ["future_tense", "complex_sentences"]},
            1: {"max_sentence_length": 4, "forbidden_patterns": ["future_tense", "complex_sentences"]},
            2: {"max_sentence_length": 5, "forbidden_patterns": ["complex_sentences"]},
            3: {"max_sentence_length": 6, "forbidden_patterns": ["abstract_concepts"]},
            4: {"max_sentence_length": 7, "forbidden_patterns": []},
            5: {"max_sentence_length": 8, "forbidden_patterns": []}
        }
        
        return constraints.get(age_years, constraints[0])
    
    def _get_cognitive_abilities(self, age_years: int) -> List[str]:
        """Get available cognitive abilities for the age."""
        abilities = {
            0: ["sensory_perception", "basic_attention", "simple_memory"],
            1: ["object_permanence", "basic_causality", "simple_imitation"],
            2: ["symbolic_play", "basic_language", "simple_reasoning"],
            3: ["self_awareness", "basic_empathy", "simple_planning"],
            4: ["world_modeling", "hypothesis_testing", "basic_abstraction"],
            5: ["abstract_thinking", "metacognition", "complex_reasoning"]
        }
        
        return abilities.get(age_years, abilities[0])
    
    def _get_typical_activities(self, hour: int, age_years: int) -> List[str]:
        """Get typical activities for the hour and age."""
        if age_years == 0:
            return ["feeding", "sleeping", "crying", "looking"]
        elif age_years == 1:
            return ["playing", "exploring", "babbling", "crawling"]
        elif age_years == 2:
            return ["walking", "talking", "playing", "exploring"]
        elif age_years == 3:
            return ["pretend_play", "talking", "learning", "socializing"]
        elif age_years == 4:
            return ["learning", "playing", "reading", "creating"]
        else:
            return ["learning", "playing", "thinking", "creating"]
    
    def _get_forbidden_patterns(self, age_years: int) -> List[str]:
        """Get forbidden language patterns for the age."""
        patterns = {
            0: ["future_tense", "complex_sentences", "abstract_concepts"],
            1: ["future_tense", "complex_sentences", "abstract_concepts"],
            2: ["complex_sentences", "abstract_concepts"],
            3: ["abstract_concepts"],
            4: [],
            5: []
        }
        
        return patterns.get(age_years, patterns[0])
    
    def _get_season(self, target_date: date) -> str:
        """Get season for the date."""
        month = target_date.month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
    
    def _compute_content_hash(self, hour_plan: Dict[str, Any]) -> str:
        """Compute content hash for idempotency."""
        # Create a deterministic string representation
        content_str = json.dumps(hour_plan, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16] 