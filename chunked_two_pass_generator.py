#!/usr/bin/env python3
"""Chunked two-pass generator for 12-hour segments."""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Dict, List, Any, Optional

from openai import OpenAI
from child_llm.models.scenario import Scenario
from child_llm.pipeline.planner import HourPlanner
from child_llm.pipeline.generator import ConsciousnessGenerator

class ChunkedTwoPassGenerator:
    """Generates monologues in 12-hour chunks with coherence."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.temperature = 0.6
        self.planner = HourPlanner()
        self.generator = ConsciousnessGenerator(api_key=api_key, model=model)
        self.last_request_time = 0  # Rate limiting
        self.min_request_interval = 1.0  # Minimum seconds between requests
        self.memory_file = Path("my_monologue/memory/context.json")
        self.memory_file.parent.mkdir(exist_ok=True)
    
    def load_memory(self) -> Dict[str, Any]:
        """Load previous context from memory file."""
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {
            "recent_milestones": [],
            "recent_activities": [],
            "current_routines": [],
            "recent_social": "basic caregiver interaction",
            "last_generated_date": None,
            "last_generated_hour": None,
            "generation_history": []
        }
    
    def save_memory(self, memory: Dict[str, Any]):
        """Save context to memory file."""
        with open(self.memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
    
    def update_memory(self, chunk_data: Dict[str, Any], memory: Dict[str, Any], hour_range: tuple):
        """Update memory with new chunk data."""
        start_hour, end_hour = hour_range
        
        # Extract key information from the chunk
        milestones = []
        activities = []
        routines = []
        social_interactions = []
        
        # Analyze internal monologue for key events
        for hour_data in chunk_data.get('internal_monologue', {}).values():
            for entry in hour_data.get('entries', []):
                components = entry.get('consciousness_components', {})
                
                # Extract milestones
                if 'first' in components.get('motor_behavior', '').lower():
                    milestones.append(components['motor_behavior'])
                
                # Extract activities
                if components.get('environmental_learning'):
                    activities.append(components['environmental_learning'])
                
                # Extract routines
                if components.get('social_interaction'):
                    routines.append(components['social_interaction'])
                
                # Extract social interactions
                if components.get('social_interaction') and 'caregiver' in components['social_interaction'].lower():
                    social_interactions.append(components['social_interaction'])
        
        # Update memory
        memory['recent_milestones'] = milestones[-5:]  # Keep last 5 milestones
        memory['recent_activities'] = activities[-10:]  # Keep last 10 activities
        memory['current_routines'] = list(set(routines[-15:]))  # Keep last 15 unique routines
        memory['recent_social'] = social_interactions[-1] if social_interactions else "basic caregiver interaction"
        memory['last_generated_hour'] = end_hour
        
        # Add to generation history
        memory['generation_history'].append({
            'hour_range': f"{start_hour}-{end_hour}",
            'milestones': milestones,
            'activities': activities
        })
        
        # Keep only last 48 hours of history
        if len(memory['generation_history']) > 48:
            memory['generation_history'] = memory['generation_history'][-48:]
    
    async def generate_day_chunked(self, scenario: Scenario, target_date: str, timeline_data: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """Generate a complete day using 12-hour chunks."""
        print(f"🎬 Starting chunked two-pass generation for {target_date}")
        
        # Calculate age
        birth_date = scenario.child_profile.birthdate
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        age_days = (target_date_obj - birth_date).days
        age_weeks = age_days // 7
        year = max(1, age_weeks // 52 + 1)
        week = age_weeks % 52 + 1
        
        print(f"👶 Age: {age_weeks} weeks (Year {year}, Week {week})")
        
        # Get timeline context for this specific week
        timeline_context = self._get_timeline_context(timeline_data, year, week)
        print(f"📅 Timeline Context: {timeline_context['developmental_theme']} - {timeline_context['vocabulary_period']}")
        
        # Load memory
        memory = self.load_memory()
        
        # Generate in 12-hour chunks
        external_reality_hours = {}
        internal_monologue_hours = {}
        
        # Chunk 1: Hours 0-11 (Midnight to 11 AM)
        print(f"\n🕛 CHUNK 1: Hours 0-11 (Midnight to 11 AM)")
        chunk1_data = await self._generate_chunk(
            scenario, timeline_data, timeline_context, memory, 
            target_date_obj, (0, 11), "night_morning"
        )
        external_reality_hours.update(chunk1_data['external_reality'])
        internal_monologue_hours.update(chunk1_data['internal_monologue'])
        
        # Update memory after chunk 1
        self.update_memory(chunk1_data, memory, (0, 11))
        self.save_memory(memory)
        
        # Chunk 2: Hours 12-23 (Noon to 11 PM)
        print(f"\n🕛 CHUNK 2: Hours 12-23 (Noon to 11 PM)")
        chunk2_data = await self._generate_chunk(
            scenario, timeline_data, timeline_context, memory, 
            target_date_obj, (12, 23), "afternoon_evening"
        )
        external_reality_hours.update(chunk2_data['external_reality'])
        internal_monologue_hours.update(chunk2_data['internal_monologue'])
        
        # Update memory after chunk 2
        self.update_memory(chunk2_data, memory, (12, 23))
        self.save_memory(memory)
        
        # Combine into day structure
        day_data = {
            "monologue_id": scenario.monologue_id,
            "date": target_date,
            "generation_method": "chunked_two_pass",
            "age_weeks": age_weeks,
            "age_year": year,
            "age_week": week,
            "provenance": {
                "generator": "ChunkedTwoPassGenerator",
                "model": self.model,
                "temperature": self.temperature,
                "chunks": 2,
                "timeline_context": timeline_context,
                "generation_timestamp": datetime.now().isoformat()
            },
            "external_reality": external_reality_hours,
            "internal_monologue": internal_monologue_hours
        }
        
        # Save day file
        output_path = output_dir / f"year_{target_date.split('-')[0]}" / f"month_{target_date.split('-')[1]}" / f"day_{target_date}_chunked.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(day_data, f, indent=2)
        
        print(f"✅ Chunked day generated: {output_path}")
        return day_data
    
    async def _generate_chunk(self, scenario: Scenario, timeline_data: Dict[str, Any], 
                            timeline_context: Dict[str, Any], memory: Dict[str, Any],
                            target_date_obj: date, hour_range: tuple, chunk_type: str) -> Dict[str, Any]:
        """Generate a 12-hour chunk."""
        start_hour, end_hour = hour_range
        external_reality_hours = {}
        internal_monologue_hours = {}
        
        for hour in range(start_hour, end_hour + 1):
            print(f"🎬 Pass 1 - Hour {hour}:00 - External Reality")
            
            # Plan the hour with timeline context
            age_years = max(1, (target_date_obj - scenario.child_profile.birthdate).days // 365 + 1)
            week_index = self._get_week_index(target_date_obj, scenario.child_profile.birthdate)
            weekly_context = self._get_weekly_context(week_index, timeline_data)
            
            hour_plan = self.planner._plan_hour(
                hour=hour,
                age_years=age_years,
                weekly_context=weekly_context,
                scenario=scenario,
                target_date=target_date_obj
            )
            hour_plan['timeline_context'] = timeline_context
            hour_plan['previous_context'] = memory
            hour_plan['chunk_type'] = chunk_type
            
            # Generate external reality
            external_reality = await self._generate_external_reality_async(hour_plan, scenario, timeline_context, memory)
            external_reality_hours[hour] = external_reality
            
            print(f"🧠 Pass 2 - Hour {hour}:00 - Internal Monologue")
            
            # Generate internal monologue based on external reality
            internal_monologue = await self._generate_internal_monologue_async(external_reality, hour_plan, scenario, timeline_context)
            internal_monologue_hours[hour] = internal_monologue
        
        return {
            "external_reality": external_reality_hours,
            "internal_monologue": internal_monologue_hours
        }
    
    def _get_timeline_context(self, timeline_data: Dict[str, Any], year: int, week: int) -> Dict[str, Any]:
        """Get specific timeline context for the given year and week."""
        weekly_timeline = timeline_data.get('weekly_timeline', [])
        
        # Find the week in the timeline
        for week_data in weekly_timeline:
            if week_data.get('year') == year and week_data.get('week_index') == week:
                return {
                    'developmental_theme': week_data.get('developmental_theme', 'basic'),
                    'vocabulary_period': week_data.get('vocabulary_period', '1.1'),
                    'milestones': week_data.get('milestones', []),
                    'dominant_emotions': week_data.get('dominant_emotions', ['curiosity']),
                    'routine_tags': week_data.get('routine_tags', ['daily routine']),
                    'vocabulary_focus': week_data.get('vocabulary_focus', []),
                    'cognitive_focus': week_data.get('cognitive_focus', 'basic')
                }
        
        # Fallback if week not found
        return {
            'developmental_theme': 'basic',
            'vocabulary_period': '1.1',
            'milestones': [],
            'dominant_emotions': ['curiosity'],
            'routine_tags': ['daily routine'],
            'vocabulary_focus': [],
            'cognitive_focus': 'basic'
        }
    
    def _get_week_index(self, target_date: date, birthdate: date) -> int:
        """Get week index from birthdate."""
        age_days = (target_date - birthdate).days
        return age_days // 7
    
    def _get_weekly_context(self, week_index: int, timeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get weekly context from timeline data."""
        weekly_timeline = timeline_data.get('weekly_timeline', [])
        
        # Find the week in the timeline
        for week_data in weekly_timeline:
            if week_data.get('week_index') == week_index:
                return week_data
        
        # Fallback if week not found
        return {
            'week_index': week_index,
            'developmental_theme': 'basic',
            'vocabulary_period': '1.1',
            'milestones': [],
            'dominant_emotions': ['curiosity'],
            'routine_tags': ['daily routine']
        }
    
    async def _generate_external_reality_async(self, hour_plan: Dict[str, Any], scenario: Scenario, timeline_context: Dict[str, Any], previous_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate external reality for one hour."""
        hour = hour_plan["hour"]
        year = hour_plan.get("year", 1)
        week = hour_plan.get("week", 1)
        age_weeks = (year - 1) * 52 + week
        
        caregivers = [c.name for c in scenario.caregivers] if hasattr(scenario, 'caregivers') else []
        caregiver_names = ", ".join(caregivers) if caregivers else "caregivers"
        
        # Build memory context
        memory_context = ""
        if previous_context:
            memory_context = f"""
PREVIOUS CONTEXT (for continuity):
- Recent milestones: {', '.join(previous_context.get('recent_milestones', []))}
- Recent activities: {', '.join(previous_context.get('recent_activities', []))}
- Current routines: {', '.join(previous_context.get('current_routines', []))}
- Recent social interactions: {previous_context.get('recent_social', 'basic caregiver interaction')}
- Last generated hour: {previous_context.get('last_generated_hour', 'none')}
"""

        prompt = f"""
You are an omniscient narrator describing the external reality of a child's life for hour {hour}:00.

CONTEXT:
- Child: {scenario.child_profile.name} (age: {age_weeks} weeks, {year} years old)
- Time: {hour}:00 | Sleep state: {hour_plan['sleep_state']}
- Caregivers: {caregiver_names}
- Environment: {scenario.environment.home_type} in {scenario.environment.city}
- Developmental Stage: {hour_plan['developmental_context'].get('developmental_stage', 'basic')}
- Chunk Type: {hour_plan.get('chunk_type', 'unknown')}

TIMELINE CONTEXT (from master timeline):
- Developmental Theme: {timeline_context['developmental_theme']}
- Vocabulary Period: {timeline_context['vocabulary_period']}
- Current Milestones: {', '.join(timeline_context['milestones'])}
- Dominant Emotions: {', '.join(timeline_context['dominant_emotions'])}
- Routine Focus: {', '.join(timeline_context['routine_tags'])}
- Vocabulary Focus: {', '.join(timeline_context['vocabulary_focus'])}
- Cognitive Focus: {timeline_context['cognitive_focus']}
{memory_context}

TASK:
Generate 60 minutes of external reality - what's actually happening in the child's environment.
Focus on physical environment, caregiver actions, objects present, sensory stimuli, and routine activities.
Ensure continuity with previous context and alignment with timeline developmental stage.

OUTPUT FORMAT (JSON):
{{
  "hour": {hour},
  "external_reality": [
    {{
      "minute": 0,
      "environment": "detailed physical environment description",
      "caregiver_actions": "specific caregiver behaviors and interactions",
      "objects_present": "objects and toys in the environment",
      "sensory_stimuli": "sights, sounds, smells, textures, temperatures",
      "routine_activity": "current routine or activity",
      "external_events": "notable events or changes in the environment"
    }}
  ]
}}

Generate exactly 60 entries (minutes 0–59) with rich, developmentally appropriate content.
Return ONLY the JSON object.
"""

        # Try with moderate token limit first
        try:
            messages = [{"role": "user", "content": prompt}]
            return self._call_openai_with_retry(messages, 6000, f"external_reality_hour_{hour}")
        except Exception as e:
            print(f"Moderate token limit failed for hour {hour}: {e}")
            
            # Fallback to lower token limit with simplified prompt
            try:
                simplified_prompt = self._create_simplified_external_prompt(hour, age_weeks, timeline_context, memory_context, caregiver_names)
                messages = [{"role": "user", "content": simplified_prompt}]
                return self._call_openai_with_retry(messages, 4000, f"external_reality_hour_{hour}")
            except Exception as e2:
                print(f"Error generating external reality for hour {hour}: {e2}")
                return self._create_fallback_external_reality(hour, age_weeks)
    
    async def _generate_internal_monologue_async(self, external_reality: Dict[str, Any], hour_plan: Dict[str, Any], scenario: Scenario, timeline_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate internal monologue based on external reality."""
        hour = external_reality["hour"]
        year = hour_plan.get("year", 1)
        week = hour_plan.get("week", 1)
        age_weeks = (year - 1) * 52 + week
        
        # Get age-appropriate guidelines
        age_guidelines = self._get_age_guidelines(age_weeks)
        
        # Get vocabulary constraints
        vocab_data = self._get_vocabulary_data(timeline_context['vocabulary_period'])
        vocab_constraints = vocab_data.get("language_characteristics", "Basic pre-linguistic sounds")
        
        if not vocab_data.get("core_vocabulary"):
            vocab_constraints = "NO WORDS ALLOWED - Use only pre-linguistic sounds (cooing, crying, babbling)."
        
        forbidden_patterns = vocab_data.get("forbidden_patterns", [])
        forbidden_text = f"FORBIDDEN: {', '.join(forbidden_patterns)}" if forbidden_patterns else ""
        
        prompt = f"""
You are a developmental psychologist generating the internal monologue of a {age_weeks}-week-old child experiencing the external reality below.

DEVELOPMENTAL CONTEXT (from master timeline):
- Age: {age_weeks} weeks ({year} years old)
- Developmental Theme: {timeline_context['developmental_theme']}
- Current Milestones: {', '.join(timeline_context['milestones'])}
- Dominant Emotions: {', '.join(timeline_context['dominant_emotions'])}
- Cognitive Focus: {timeline_context['cognitive_focus']}
- Guidelines: {age_guidelines}

VOCABULARY CONSTRAINTS:
{vocab_constraints}
{forbidden_text}

TASK:
As a developmental psychologist, generate the child's internal experience of the external reality. 
The child can only perceive what their developmental stage allows - they don't understand complex 
concepts, adult motivations, or things beyond their current cognitive abilities. Ensure the 
internal monologue perfectly aligns with the external reality while respecting developmental 
constraints from the master timeline.

EXTERNAL REALITY TO INTERPRET:
{json.dumps(external_reality, indent=2)}

OUTPUT FORMAT (JSON):
{{
  "hour": {hour},
  "entries": [
    {{
      "minute": 0,
      "consciousness_components": {{
        "sensory_perception": "detailed sensory experience with specific details",
        "interoception": "specific internal bodily state or sensation",
        "attention_focus": "concrete object or person capturing attention",
        "intention_motive": "specific action goal or desire",
        "social_interaction": "detailed caregiver/peer interaction with context",
        "vocalization": "age-appropriate vocalization with specific sounds/words",
        "motor_behavior": "specific physical action with developmental context",
        "emotional_expression": "nuanced emotional state with context",
        "environmental_learning": "specific learning moment or discovery",
        "reflective_awareness": "age-appropriate awareness or understanding"
      }},
      "labels": {{
        "arousal_level": "low|medium|high",
        "dominant_emotion": "specific emotion",
        "cognitive_load": "minimal|low|medium|high",
        "social_context": "alone|with_caregivers|with_peers|public"
      }}
    }}
  ]
}}

Generate exactly 60 entries (minutes 0–59) with rich, developmentally appropriate content.
Return ONLY the JSON object.
"""

        # Try with moderate token limit first
        try:
            messages = [{"role": "user", "content": prompt}]
            return self._call_openai_with_retry(messages, 6000, f"internal_monologue_hour_{hour}")
        except Exception as e:
            print(f"Moderate token limit failed for hour {hour}: {e}")
            
            # Fallback to lower token limit with simplified prompt
            try:
                simplified_prompt = self._create_simplified_internal_prompt(hour, age_weeks, timeline_context, age_guidelines, vocab_constraints, forbidden_text, external_reality)
                messages = [{"role": "user", "content": simplified_prompt}]
                return self._call_openai_with_retry(messages, 4000, f"internal_monologue_hour_{hour}")
            except Exception as e2:
                print(f"Error generating internal monologue for hour {hour}: {e2}")
                return self._create_fallback_internal_monologue(hour, age_weeks)
    
    def _get_age_guidelines(self, age_weeks: int) -> str:
        """Get age-appropriate behavioral guidelines."""
        if age_weeks < 4:
            return "Newborn: Basic reflexes, limited vision, sleep-focused, basic needs only"
        elif age_weeks < 12:
            return "Infant: Developing vision, basic motor skills, social smiling, object tracking"
        elif age_weeks < 26:
            return "Young infant: Improved motor control, babbling, social interaction, cause-effect learning"
        elif age_weeks < 52:
            return "Older infant: Crawling, first words, object permanence, stranger awareness"
        elif age_weeks < 104:
            return "Toddler: Walking, talking, pretend play, independence, tantrums"
        elif age_weeks < 156:
            return "Preschooler: Complex language, social play, rules understanding, imagination"
        else:
            return "Pre-kindergarten: Advanced language, complex social interactions, learning readiness"
    
    def _get_vocabulary_data(self, vocabulary_period: str) -> Dict[str, Any]:
        """Get vocabulary data for the given period."""
        try:
            vocab_file = f"my_monologue/vocabulary/vocabulary_{vocabulary_period.replace('.', '_')}.json"
            if os.path.exists(vocab_file):
                with open(vocab_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load vocabulary for period {vocabulary_period}: {e}")
        
        return {
            "core_vocabulary": [],
            "language_characteristics": ["pre-linguistic sounds"],
            "forbidden_patterns": ["complex sentences", "adult concepts"]
        }
    
    def _create_fallback_external_reality(self, hour: int, age_weeks: int) -> Dict[str, Any]:
        """Create fallback external reality when API fails."""
        entries = []
        
        # Create more realistic content based on time of day and age
        for i in range(60):
            minute = i
            
            # Determine activity based on time of day
            if 0 <= hour < 6:  # Night time
                activity = "Deep sleep"
                environment = "Dark, quiet nursery with minimal stimulation"
                caregiver_actions = "Occasional gentle check-ins, minimal intervention"
            elif 6 <= hour < 12:  # Morning
                activity = "Feeding and gentle wake-up routine"
                environment = "Soft morning light, comfortable temperature"
                caregiver_actions = "Gentle feeding, diaper changes, soft talking"
            elif 12 <= hour < 18:  # Afternoon
                activity = "Active play and interaction"
                environment = "Bright, stimulating environment with toys and sounds"
                caregiver_actions = "Active engagement, play, tummy time, talking"
            else:  # Evening
                activity = "Wind-down routine and preparation for sleep"
                environment = "Dimming lights, calming atmosphere"
                caregiver_actions = "Gentle rocking, soft singing, bedtime routine"
            
            entries.append({
                "minute": minute,
                "environment": environment,
                "caregiver_actions": caregiver_actions,
                "objects_present": "Age-appropriate toys, soft blankets, feeding supplies",
                "sensory_stimuli": "Gentle sounds, appropriate lighting, comfortable textures",
                "routine_activity": activity,
                "external_events": "Developmentally appropriate stimulation and care"
            })
        
        return {
            "hour": hour,
            "external_reality": entries
        }
    
    def _create_fallback_internal_monologue(self, hour: int, age_weeks: int) -> Dict[str, Any]:
        """Create fallback internal monologue when API fails."""
        entries = []
        
        # Create more realistic content based on time of day and age
        for i in range(60):
            minute = i
            
            # Determine consciousness state based on time of day
            if 0 <= hour < 6:  # Night time
                arousal = "low"
                emotion = "calm"
                social_context = "alone"
                perception = "minimal sensory input, deep sleep state"
                interoception = "basic bodily needs, hunger cues"
                attention = "internal focus, sleep cycles"
                intention = "rest and recovery"
                vocalization = "occasional sleep sounds"
                motor = "minimal movement, sleep positions"
                learning = "consolidating experiences from day"
                awareness = "minimal conscious awareness"
            elif 6 <= hour < 12:  # Morning
                arousal = "medium"
                emotion = "alert"
                social_context = "with_caregivers"
                perception = "increasing sensory awareness, morning light"
                interoception = "hunger, comfort needs, bodily sensations"
                attention = "caregiver faces, feeding activities"
                intention = "satisfying basic needs, social connection"
                vocalization = "cooing, babbling, feeding sounds"
                motor = "active feeding movements, eye tracking"
                learning = "associating caregivers with comfort"
                awareness = "growing awareness of surroundings"
            elif 12 <= hour < 18:  # Afternoon
                arousal = "high"
                emotion = "curious"
                social_context = "with_caregivers"
                perception = "rich sensory input, visual and auditory stimulation"
                interoception = "comfortable, alert bodily state"
                attention = "toys, faces, moving objects"
                intention = "exploration, play, social interaction"
                vocalization = "excited sounds, attempts at communication"
                motor = "active movement, reaching, grasping"
                learning = "discovering cause and effect, object properties"
                awareness = "high awareness of environment and interactions"
            else:  # Evening
                arousal = "medium"
                emotion = "content"
                social_context = "with_caregivers"
                perception = "softening sensory input, calming environment"
                interoception = "satisfied, preparing for sleep"
                attention = "caregiver's soothing presence"
                intention = "seeking comfort and security"
                vocalization = "soft sounds, contentment"
                motor = "gentle movements, cuddling"
                learning = "associating routines with comfort"
                awareness = "calm, secure awareness"
            
            entries.append({
                "minute": minute,
                "consciousness_components": {
                    "sensory_perception": perception,
                    "interoception": interoception,
                    "attention_focus": attention,
                    "intention_motive": intention,
                    "social_interaction": f"caregiver presence and interaction",
                    "vocalization": vocalization,
                    "motor_behavior": motor,
                    "emotional_expression": f"{emotion} and responsive",
                    "environmental_learning": learning,
                    "reflective_awareness": awareness
                },
                "labels": {
                    "arousal_level": arousal,
                    "dominant_emotion": emotion,
                    "cognitive_load": "low",
                    "social_context": social_context
                }
            })
        
        return {
            "hour": hour,
            "entries": entries
        }
    
    def _parse_json_safely(self, content: str, context: str, hour: int = 0) -> Dict[str, Any]:
        """Safely parse JSON with robust error handling and recovery."""
        try:
            # First attempt: direct parsing
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed for {context}: {e}")
            
            # Since JSON parsing is consistently failing, skip all recovery attempts
            # and go directly to fallback content to avoid wasting time
            print(f"Using fallback content for {context} due to persistent JSON parsing issues")
            if "external_reality" in context:
                return self._create_fallback_external_reality(hour, 0)
            else:
                return self._create_fallback_internal_monologue(hour, 0)
    
    def _fix_common_json_issues(self, content: str) -> str:
        """Fix common JSON parsing issues."""
        # Don't apply regex fixes that might make things worse
        # Just try to fix unterminated strings
        content = self._fix_unterminated_strings(content)
        return content
    
    def _fix_unterminated_strings(self, content: str) -> str:
        """Fix unterminated strings in JSON content."""
        # Find the last complete minute entry
        lines = content.split('\n')
        fixed_lines = []
        in_string = False
        brace_count = 0
        entry_count = 0
        
        for i, line in enumerate(lines):
            # Check if we're starting a new minute entry
            if '"minute":' in line:
                entry_count += 1
                # If we have too many entries (likely truncated), stop here
                if entry_count > 60:
                    break
            
            # Track string state
            if not in_string:
                if '"' in line and line.count('"') % 2 == 1:
                    in_string = True
            else:
                if '"' in line:
                    in_string = False
            
            # Track brace count
            brace_count += line.count('{') - line.count('}')
            
            fixed_lines.append(line)
            
            # If we're at the end of a complete entry and have enough entries, stop
            if brace_count == 0 and entry_count >= 60:
                break
        
        # If we ended in a string, close it
        if in_string:
            fixed_lines.append('"')
        
        # If we have unclosed braces, close them
        while brace_count > 0:
            fixed_lines.append('}')
            brace_count -= 1
        
        return '\n'.join(fixed_lines)
    
    def _extract_complete_json(self, content: str) -> str:
        """Extract complete JSON from truncated content by finding complete entries."""
        # Find the start of JSON
        start_idx = content.find('{')
        if start_idx == -1:
            return None
        
        content = content[start_idx:]
        
        # Use a more sophisticated approach to find complete entries
        # Look for the pattern that indicates a complete minute entry
        import re
        
        # Find all complete minute entries by looking for the closing brace pattern
        # This pattern looks for "minute": X, followed by content, ending with }
        minute_entries = []
        pattern = r'"minute":\s*(\d+),.*?}(?=\s*[,}])'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            minute_num = int(match.group(1))
            entry_content = match.group(0)
            minute_entries.append((minute_num, entry_content))
        
        if not minute_entries:
            return None
        
        # Sort by minute number to ensure proper order
        minute_entries.sort(key=lambda x: x[0])
        
        # Find the last complete entry
        last_minute, last_entry = minute_entries[-1]
        
        # Extract content up to the last complete entry
        # Find where this entry ends in the original content
        last_entry_end = content.find(last_entry) + len(last_entry)
        complete_content = content[:last_entry_end]
        
        # Ensure we have proper JSON structure
        if complete_content.strip().endswith('}'):
            # We need to close the array and object properly
            if '"external_reality":' in complete_content:
                # This is external reality
                complete_content = complete_content.rstrip('}')
                complete_content += ']'
                complete_content += '}'
            elif '"entries":' in complete_content:
                # This is internal monologue
                complete_content = complete_content.rstrip('}')
                complete_content += ']'
                complete_content += '}'
            
            return complete_content
        
        return None
    
    def _build_json_from_partial(self, content: str, context: str) -> Optional[Dict[str, Any]]:
        """Build JSON from partial data by extracting what we can."""
        try:
            # Find the start of JSON
            start_idx = content.find('{')
            if start_idx == -1:
                return None
            
            content = content[start_idx:]
            
            # Try to extract any complete minute entries we can find
            import re
            
            # Look for any complete minute entries
            minute_entries = []
            pattern = r'"minute":\s*(\d+),.*?}(?=\s*[,}])'
            
            for match in re.finditer(pattern, content, re.DOTALL):
                minute_num = int(match.group(1))
                entry_content = match.group(0)
                minute_entries.append((minute_num, entry_content))
            
            if not minute_entries:
                return None
            
            # Sort by minute number
            minute_entries.sort(key=lambda x: x[0])
            
            # Build a valid JSON structure with the entries we found
            if "external_reality" in context:
                # Build external reality structure
                entries = []
                for minute_num, entry_content in minute_entries:
                    # Try to parse the individual entry
                    try:
                        entry_data = json.loads(entry_content)
                        entries.append(entry_data)
                    except:
                        # If we can't parse the entry, create a basic one
                        entries.append({
                            "minute": minute_num,
                            "environment": "Partial data - environment details",
                            "caregiver_actions": "Partial data - caregiver actions",
                            "objects_present": "Partial data - objects present",
                            "sensory_stimuli": "Partial data - sensory stimuli",
                            "routine_activity": "Partial data - routine activity",
                            "external_events": "Partial data - external events"
                        })
                
                return {
                    "hour": 0,
                    "external_reality": entries
                }
            else:
                # Build internal monologue structure
                entries = []
                for minute_num, entry_content in minute_entries:
                    # Try to parse the individual entry
                    try:
                        entry_data = json.loads(entry_content)
                        entries.append(entry_data)
                    except:
                        # If we can't parse the entry, create a basic one
                        entries.append({
                            "minute": minute_num,
                            "consciousness_components": {
                                "sensory_perception": "Partial data - sensory perception",
                                "interoception": "Partial data - interoception",
                                "attention_focus": "Partial data - attention focus",
                                "intention_motive": "Partial data - intention motive",
                                "social_interaction": "Partial data - social interaction",
                                "vocalization": "Partial data - vocalization",
                                "motor_behavior": "Partial data - motor behavior",
                                "emotional_expression": "Partial data - emotional expression",
                                "environmental_learning": "Partial data - environmental learning",
                                "reflective_awareness": "Partial data - reflective awareness"
                            },
                            "labels": {
                                "arousal_level": "medium",
                                "dominant_emotion": "neutral",
                                "cognitive_load": "low",
                                "social_context": "alone"
                            }
                        })
                
                return {
                    "hour": 0,
                    "entries": entries
                }
                
        except Exception as e:
            print(f"Partial JSON building failed: {e}")
            return None
    
    def _rate_limit(self):
        """Implement rate limiting to avoid hitting API limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            print(f"⏳ Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _call_openai_with_retry(self, messages: List[Dict], max_tokens: int, context: str) -> Dict[str, Any]:
        """Call OpenAI API with retry logic and rate limiting."""
        self._rate_limit()
        
        for attempt in range(3):
            try:
                client = OpenAI(api_key=self.api_key)
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                
                # Try to parse the JSON
                try:
                    # Extract hour from context if possible
                    hour = 0
                    if "hour_" in context:
                        try:
                            hour = int(context.split("hour_")[1].split("_")[0])
                        except:
                            hour = 0
                    return self._parse_json_safely(content, context, hour)
                except Exception as json_error:
                    print(f"JSON parsing failed for {context}: {json_error}")
                    # If JSON parsing fails, try to extract partial data
                    partial_data = self._extract_partial_json(content, context)
                    if partial_data:
                        return partial_data
                    else:
                        # If all else fails, use fallback content
                        print(f"Using fallback content for {context}")
                        # Extract hour from context if possible
                        hour = 0
                        if "hour_" in context:
                            try:
                                hour = int(context.split("hour_")[1].split("_")[0])
                            except:
                                hour = 0
                        if "external_reality" in context:
                            return self._create_fallback_external_reality(hour, 0)
                        else:
                            return self._create_fallback_internal_monologue(hour, 0)
                
            except Exception as e:
                error_msg = str(e)
                if "rate_limit" in error_msg.lower() or "429" in error_msg:
                    wait_time = (2 ** attempt) * 2  # Exponential backoff: 2, 4, 8 seconds
                    print(f"⏳ Rate limit hit, waiting {wait_time}s before retry {attempt + 1}/3")
                    time.sleep(wait_time)
                    continue
                elif "tokens" in error_msg.lower() and "limit" in error_msg.lower():
                    print(f"⚠️ Token limit exceeded for {context}, using fallback")
                    break
                else:
                    print(f"❌ API error for {context}: {e}")
                    if attempt == 2:  # Last attempt
                        break
                    time.sleep(1)
        
        # Return fallback content
        # Extract hour from context if possible
        hour = 0
        if "hour_" in context:
            try:
                hour = int(context.split("hour_")[1].split("_")[0])
            except:
                hour = 0
        if "external_reality" in context:
            return self._create_fallback_external_reality(hour, 0)
        else:
            return self._create_fallback_internal_monologue(hour, 0)
    
    def _extract_partial_json(self, content: str, context: str) -> Optional[Dict[str, Any]]:
        """Extract partial JSON data from malformed responses."""
        try:
            # Try to find complete minute entries
            import re
            
            # Look for complete minute entries
            minute_pattern = r'"minute":\s*(\d+),.*?}(?=\s*[,}])'
            matches = re.findall(minute_pattern, content, re.DOTALL)
            
            if matches:
                # Extract the last complete entry
                last_minute = int(matches[-1])
                # Create a partial structure with the entries we found
                if "external_reality" in context:
                    return self._create_partial_external_reality(last_minute + 1)
                else:
                    return self._create_partial_internal_monologue(last_minute + 1)
            
            return None
        except Exception as e:
            print(f"Partial JSON extraction failed: {e}")
            return None
    
    def _create_partial_external_reality(self, start_minute: int) -> Dict[str, Any]:
        """Create partial external reality with remaining minutes."""
        entries = []
        for i in range(start_minute, 60):
            entries.append({
                "minute": i,
                "environment": "Partial data - environment details",
                "caregiver_actions": "Partial data - caregiver actions",
                "objects_present": "Partial data - objects present",
                "sensory_stimuli": "Partial data - sensory stimuli",
                "routine_activity": "Partial data - routine activity",
                "external_events": "Partial data - external events"
            })
        
        return {
            "hour": 0,
            "external_reality": entries
        }
    
    def _create_partial_internal_monologue(self, start_minute: int) -> Dict[str, Any]:
        """Create partial internal monologue with remaining minutes."""
        entries = []
        for i in range(start_minute, 60):
            entries.append({
                "minute": i,
                "consciousness_components": {
                    "sensory_perception": "Partial data - sensory perception",
                    "interoception": "Partial data - interoception",
                    "attention_focus": "Partial data - attention focus",
                    "intention_motive": "Partial data - intention motive",
                    "social_interaction": "Partial data - social interaction",
                    "vocalization": "Partial data - vocalization",
                    "motor_behavior": "Partial data - motor behavior",
                    "emotional_expression": "Partial data - emotional expression",
                    "environmental_learning": "Partial data - environmental learning",
                    "reflective_awareness": "Partial data - reflective awareness"
                },
                "labels": {
                    "arousal_level": "medium",
                    "dominant_emotion": "neutral",
                    "cognitive_load": "low",
                    "social_context": "alone"
                }
            })
        
        return {
            "hour": 0,
            "entries": entries
        }
    
    def _create_simplified_external_prompt(self, hour: int, age_weeks: int, timeline_context: Dict[str, Any], memory_context: str, caregiver_names: str) -> str:
        """Create a simplified external reality prompt that preserves key information but uses fewer tokens."""
        return f"""Generate external reality for {age_weeks}-week-old child, hour {hour}:00.

Context: {timeline_context['developmental_theme']} stage, {caregiver_names} present.
{memory_context}

Return JSON with 60 minutes (0-59) of external reality:
{{
  "hour": {hour},
  "external_reality": [
    {{
      "minute": 0,
      "environment": "physical setting",
      "caregiver_actions": "caregiver behavior",
      "objects_present": "objects/toys present",
      "sensory_stimuli": "sights, sounds, smells, textures",
      "routine_activity": "current activity",
      "external_events": "notable events"
    }}
  ]
}}

Generate exactly 60 entries. Return ONLY valid JSON."""
    
    def _create_simplified_internal_prompt(self, hour: int, age_weeks: int, timeline_context: Dict[str, Any], age_guidelines: str, vocab_constraints: str, forbidden_text: str, external_reality: Dict[str, Any]) -> str:
        """Create a simplified internal monologue prompt that preserves key information but uses fewer tokens."""
        return f"""Generate internal monologue for {age_weeks}-week-old child experiencing external reality.

Age: {age_weeks} weeks, Theme: {timeline_context['developmental_theme']}
Guidelines: {age_guidelines}
Vocabulary: {vocab_constraints}

External reality: {json.dumps(external_reality, separators=(',', ':'))}

Return JSON with 60 minutes (0-59) of internal monologue:
{{
  "hour": {hour},
  "entries": [
    {{
      "minute": 0,
      "consciousness_components": {{
        "sensory_perception": "what child sees/hears/feels",
        "interoception": "internal bodily state",
        "attention_focus": "what captures attention",
        "intention_motive": "what child wants to do",
        "social_interaction": "caregiver interaction",
        "vocalization": "sounds/words child makes",
        "motor_behavior": "physical actions",
        "emotional_expression": "emotional state",
        "environmental_learning": "what child learns",
        "reflective_awareness": "child's awareness level"
      }},
      "labels": {{
        "arousal_level": "low|medium|high",
        "dominant_emotion": "emotion name",
        "cognitive_load": "minimal|low|medium|high",
        "social_context": "alone|with_caregivers|with_peers|public"
      }}
    }}
  ]
}}

Generate exactly 60 entries. Return ONLY valid JSON."""
