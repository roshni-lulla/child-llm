"""Automated timeline generator based on developmental psychology."""

import json
from datetime import date, timedelta
from typing import List, Dict, Any
from pathlib import Path

from ..models.development import WeeklyTimeline, Milestone, DevelopmentalStage


class TimelineGenerator:
    """Generates developmental timeline based on psychology research."""
    
    def __init__(self):
        # Updated to use realistic developmental stages with vocabulary integration
        # Different numbers of vocabulary periods per year based on learning acceleration
        self.developmental_stages = {
            1: {
                "stage": DevelopmentalStage.SENSORIMOTOR,
                "theme": "sensory_integration",
                "vocabulary_periods": ["1.1", "1.2"],  # 2 periods: 0-6 months, 6-12 months
                "cognitive_focus": "pattern_recognition",
                "typical_emotions": ["curiosity", "joy", "discomfort"],
                "routines": ["daily routine", "playtime", "feeding"],
                "milestones": [
                    (4, "first smile"),
                    (12, "first laugh"),
                    (52, "first birthday")
                ]
            },
            2: {
                "stage": DevelopmentalStage.SENSORIMOTOR,
                "theme": "object_schema",
                "vocabulary_periods": ["2.1", "2.2"],  # 2 periods: 12-18 months, 18-24 months
                "cognitive_focus": "goal-directed action",
                "typical_emotions": ["excitement", "pride", "frustration"],
                "routines": ["daily routine", "playtime", "exploration"],
                "milestones": [
                    (75, "first steps"),
                    (104, "first words")
                ]
            },
            3: {
                "stage": DevelopmentalStage.PREOPERATIONAL,
                "theme": "awareness",
                "vocabulary_periods": ["3.1", "3.2", "3.3"],  # 3 periods: 24-30, 30-36, 36-42 months
                "cognitive_focus": "self-awareness",
                "typical_emotions": ["curiosity", "nervous", "excitement"],
                "routines": ["daily routine", "playtime", "preschool"],
                "milestones": [
                    (130, "learns to use toilet"),
                    (156, "first day of preschool")
                ]
            },
            4: {
                "stage": DevelopmentalStage.PREOPERATIONAL,
                "theme": "world_model",
                "vocabulary_periods": ["4.1", "4.2", "4.3", "4.4"],  # 4 periods: 42-45, 45-48, 48-51, 51-54 months
                "cognitive_focus": "outcome simulation",
                "typical_emotions": ["pride", "joy", "curiosity"],
                "routines": ["daily routine", "playtime", "learning"],
                "milestones": [
                    (200, "learns to ride a bike")
                ]
            },
            5: {
                "stage": DevelopmentalStage.PREOPERATIONAL,
                "theme": "abstract_reasoning",
                "vocabulary_periods": ["5.1", "5.2", "5.3"],  # 3 periods: 54-56, 56-58, 58-60 months
                "cognitive_focus": "nested reflection",
                "typical_emotions": ["curiosity", "pride", "wonder"],
                "routines": ["daily routine", "playtime", "school"],
                "milestones": [
                    (260, "fifth birthday")
                ]
            }
        }
    
    def get_vocabulary_band_for_week(self, year: int, week: int) -> str:
        """Get appropriate vocabulary period for a specific week."""
        year_data = self.developmental_stages[year]
        vocab_periods = year_data["vocabulary_periods"]
        num_periods = len(vocab_periods)
        
        # Calculate weeks per period for this year
        weeks_per_period = 52 // num_periods
        
        # Determine which period based on week number within the year
        period_index = min((week - 1) // weeks_per_period, num_periods - 1)
        
        return vocab_periods[period_index]
    
    def generate_timeline(self, scenario: Dict[str, Any]) -> WeeklyTimeline:
        """Generate complete 5-year timeline based on scenario."""
        timeline = []
        week_index = 1
        
        for year in range(1, 6):
            year_data = self.developmental_stages[year]
            
            for week in range(1, 53):  # 52 weeks per year
                # Get vocabulary period for this week
                vocab_period = self.get_vocabulary_band_for_week(year, week)
                
                # Add seasonal variations
                seasonal_context = self._get_seasonal_context(week)
                
                # Add personality-driven variations
                personality_context = self._get_personality_context(scenario, year, week)
                
                # Create milestone entry
                milestone = Milestone(
                    week_index=week_index,
                    year=year,
                    developmental_theme=year_data["theme"],
                    vocabulary_period=vocab_period,  # Use vocabulary period instead of language_band
                    milestones=self._get_week_milestones(year, week),
                    dominant_emotions=year_data["typical_emotions"] + personality_context.get("emotions", []),
                    routine_tags=year_data["routines"] + seasonal_context.get("routines", []),
                    new_social_actors=personality_context.get("social_actors", []),
                    vocabulary_focus=self._get_vocabulary_focus(year, week),
                    cognitive_focus=year_data["cognitive_focus"],
                    environment_notes=seasonal_context.get("environment", []),
                    health_state=self._get_health_state(week, scenario)
                )
                
                timeline.append(milestone)
                week_index += 1
        
        return WeeklyTimeline(weekly_timeline=timeline)
    
    def _get_seasonal_context(self, week: int) -> Dict[str, List[str]]:
        """Add seasonal variations to timeline."""
        # Simple seasonal mapping
        season_week = (week - 1) % 13  # 13 weeks per season
        
        if season_week < 4:  # Early season
            return {
                "routines": ["adjusting to seasons"],
                "environment": ["seasonal changes"]
            }
        elif season_week > 9:  # Late season
            return {
                "routines": ["seasonal activities"],
                "environment": ["seasonal weather"]
            }
        
        return {}
    
    def _get_personality_context(self, scenario: Dict[str, Any], year: int, week: int) -> Dict[str, List[str]]:
        """Add personality-driven variations."""
        personality = scenario.get("child_profile", {}).get("personality", {})
        temperament = scenario.get("child_profile", {}).get("temperament_tags", [])
        
        context = {"emotions": [], "social_actors": []}
        
        # Add temperament-based variations
        if "sensitive_to_noise" in temperament and week % 4 == 0:
            context["emotions"].append("overwhelmed")
        
        if "curious" in temperament and week % 3 == 0:
            context["emotions"].append("excited")
        
        # Add personality-based social interactions
        if personality.get("extraversion", 0.5) > 0.7 and year >= 3:
            context["social_actors"].append("new_friend")
        
        return context
    
    def _get_week_milestones(self, year: int, week: int) -> List[str]:
        """Get milestones for specific week."""
        year_data = self.developmental_stages[year]
        milestones = []
        
        for milestone_week, milestone_desc in year_data["milestones"]:
            if week == milestone_week:
                milestones.append(milestone_desc)
        
        return milestones
    
    def _get_vocabulary_focus(self, year: int, week: int) -> List[str]:
        """Get vocabulary focus for the week."""
        # Simple vocabulary progression
        base_vocab = {
            1: ["mama", "dada", "milk", "warm", "cold"],
            2: ["ball", "dog", "cat", "up", "down"],
            3: ["I", "you", "want", "go", "play"],
            4: ["why", "how", "when", "because", "maybe"],
            5: ["think", "feel", "remember", "imagine", "wonder"]
        }
        
        return base_vocab.get(year, [])
    
    def _get_health_state(self, week: int, scenario: Dict[str, Any]) -> str:
        """Determine health state for the week."""
        # Add occasional mild illnesses
        if week % 10 == 0:  # Every 10 weeks
            return "mild cold"
        return "healthy"
    
    def save_timeline(self, timeline: WeeklyTimeline, output_path: Path):
        """Save timeline to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(timeline.model_dump(mode='json'), f, indent=2)
        
        print(f"Timeline saved to {output_path}")
    
    def generate_from_scenario(self, scenario_path: Path, output_path: Path):
        """Generate timeline from scenario file."""
        with open(scenario_path, 'r') as f:
            scenario = json.load(f)
        
        timeline = self.generate_timeline(scenario)
        self.save_timeline(timeline, output_path) 