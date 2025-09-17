#!/usr/bin/env python3
"""
Single-pass consciousness monologue generator using longer context models.
This approach generates the entire day in one API call to avoid JSON parsing issues.
"""

import json
import asyncio
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List
from openai import OpenAI

from child_llm.models.scenario import Scenario
from child_llm.models.consciousness import DayFile
from child_llm.pipeline.planner import HourPlanner


class SinglePassGenerator:
    """Generates complete day monologues in a single API call."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.temperature = 0.6
        self.planner = HourPlanner()
        self.client = OpenAI(api_key=api_key)
    
    async def generate_day(self, scenario: Scenario, target_date: date, timeline_context: Dict[str, Any]) -> DayFile:
        """Generate a complete day in a single API call."""
        
        # Calculate age
        birth_date = scenario.child_profile.birthdate
        age_days = (target_date - birth_date).days
        age_weeks = age_days // 7
        age_years = age_weeks // 52
        
        print(f"🎯 Generating complete day: {target_date}")
        print(f"👶 Age: {age_weeks} weeks (Year {age_years + 1}, Week {age_weeks % 52 + 1})")
        
        # Create comprehensive prompt for entire day
        prompt = self._create_day_prompt(scenario, target_date, timeline_context, age_weeks, age_years)
        
        try:
            print("🎬 Generating complete day in single API call...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=8000,  # Reduced for better reliability
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            day_data = json.loads(content)
            
            print("✅ Complete day generated successfully!")
            return self._create_day_file(day_data, scenario, target_date, age_weeks, age_years, timeline_context)
            
        except Exception as e:
            print(f"❌ Error generating day: {e}")
            print("🔄 Falling back to chunked generation...")
            return await self._fallback_to_chunked(scenario, target_date, timeline_context)
    
    def _create_day_prompt(self, scenario: Scenario, target_date: date, timeline_context: Dict[str, Any], age_weeks: int, age_years: int) -> str:
        """Create a comprehensive prompt for the entire day."""
        
        return f"""You are an expert developmental psychologist generating a complete day of consciousness data for a {age_weeks}-week-old child.

CHILD PROFILE:
- Name: {scenario.child_profile.name}
- Age: {age_weeks} weeks ({age_years} years old)
- Birth Date: {scenario.child_profile.birthdate}
- Target Date: {target_date}
- Developmental Stage: {timeline_context.get('developmental_theme', 'sensory_integration')}
- Vocabulary Period: {timeline_context.get('vocabulary_period', '1.1')}

DEVELOPMENTAL CONTEXT:
- Dominant Emotions: {timeline_context.get('dominant_emotions', ['curiosity', 'joy', 'discomfort'])}
- Routine Tags: {timeline_context.get('routine_tags', ['daily routine', 'playtime', 'feeding'])}
- Vocabulary Focus: {timeline_context.get('vocabulary_focus', ['mama', 'dada', 'milk'])}
- Cognitive Focus: {timeline_context.get('cognitive_focus', 'pattern_recognition')}

TASK:
Generate a complete 24-hour consciousness monologue with minute-by-minute entries for each hour (0-23).

For each hour, provide:
1. EXTERNAL REALITY: What's happening in the environment
2. INTERNAL MONOLOGUE: The child's consciousness experience

CONSCIOUSNESS COMPONENTS (age-appropriate):
- sensory_perception: What the child sees, hears, feels
- interoception: Internal bodily sensations
- attention_focus: What the child is focusing on
- intention_motive: Basic needs and motivations
- social_interaction: Interaction with caregivers
- vocalization: Sounds and communication attempts
- motor_behavior: Physical movements and actions
- emotional_expression: Emotional states and expressions
- environmental_learning: What the child is learning
- reflective_awareness: Level of self-awareness

TIME-BASED REALISM:
- Hours 0-6: Deep sleep, minimal consciousness
- Hours 6-12: Morning routine, feeding, gentle wake-up
- Hours 12-18: Active play, exploration, learning
- Hours 18-24: Wind-down routine, preparation for sleep

OUTPUT FORMAT:
Return valid JSON with this exact structure:
{{
  "external_reality": {{
    "0": {{
      "hour": 0,
      "external_reality": [
        {{
          "minute": 0,
          "environment": "description",
          "caregiver_actions": "description",
          "objects_present": "description",
          "sensory_stimuli": "description",
          "routine_activity": "description",
          "external_events": "description"
        }}
        // ... for minutes 1-59
      ]
    }}
    // ... for hours 1-23
  }},
  "internal_monologue": {{
    "0": {{
      "hour": 0,
      "entries": [
        {{
          "minute": 0,
          "consciousness_components": {{
            "sensory_perception": "description",
            "interoception": "description",
            "attention_focus": "description",
            "intention_motive": "description",
            "social_interaction": "description",
            "vocalization": "description",
            "motor_behavior": "description",
            "emotional_expression": "description",
            "environmental_learning": "description",
            "reflective_awareness": "description"
          }},
          "labels": {{
            "arousal_level": "low/medium/high",
            "dominant_emotion": "emotion",
            "cognitive_load": "low/medium/high",
            "social_context": "alone/with_caregivers"
          }}
        }}
        // ... for minutes 1-59
      ]
    }}
    // ... for hours 1-23
  }}
}}

IMPORTANT:
- Generate exactly 60 minutes per hour (0-59)
- Use age-appropriate language and concepts
- Ensure temporal consistency across the day
- Make each minute unique and realistic
- Return ONLY valid JSON, no other text
"""
    
    def _create_day_file(self, day_data: Dict[str, Any], scenario: Scenario, target_date: date, age_weeks: int, age_years: int, timeline_context: Dict[str, Any]) -> DayFile:
        """Create a DayFile from the generated data."""
        
        return DayFile(
            monologue_id=scenario.child_profile.name,
            date=target_date.strftime("%Y-%m-%d"),
            generation_method="single_pass",
            age_weeks=age_weeks,
            age_year=age_years + 1,
            age_week=(age_weeks % 52) + 1,
            provenance={
                "generator": "SinglePassGenerator",
                "model": self.model,
                "temperature": self.temperature,
                "timeline_context": timeline_context,
                "generation_timestamp": datetime.now().isoformat()
            },
            external_reality=day_data.get("external_reality", {}),
            internal_monologue=day_data.get("internal_monologue", {}),
            summary={
                "total_hours": 24,
                "total_minutes": 1440,
                "generation_success": True,
                "fallback_used": False
            }
        )
    
    async def _fallback_to_chunked(self, scenario: Scenario, target_date: date, timeline_context: Dict[str, Any]) -> DayFile:
        """Fallback to chunked generation if single-pass fails."""
        from chunked_two_pass_generator import ChunkedTwoPassGenerator
        
        chunked_generator = ChunkedTwoPassGenerator(self.api_key, self.model)
        return await chunked_generator.generate_day_chunked(scenario, target_date, timeline_context)


async def main():
    """Test the single-pass generator."""
    import os
    from child_llm.models.scenario import Scenario
    
    # Load scenario
    with open("my_monologue/scenarios/my_child.json", "r") as f:
        scenario_data = json.load(f)
    scenario = Scenario(**scenario_data)
    
    # Load timeline context
    with open("my_monologue/timeline/master_timeline.json", "r") as f:
        timeline_data = json.load(f)
    
    # Get week context
    target_date = date(2025, 1, 1)
    week_index = 1  # Week 1
    timeline_context = timeline_data["weekly_timeline"][week_index - 1]  # 0-indexed
    
    # Generate day
    generator = SinglePassGenerator(os.getenv("OPENAI_API_KEY", "your-key*here"))
    day_file = await generator.generate_day(scenario, target_date, timeline_context)
    
    # Save result
    output_dir = Path("my_monologue/output/year_2025/month_01")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"day_{target_date.strftime('%Y-%m-%d')}_single.json"
    with open(output_file, "w") as f:
        json.dump(day_file.dict(), f, indent=2)
    
    print(f"✅ Day saved: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
