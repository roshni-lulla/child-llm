"""Consciousness generator for 5-sentence monologue entries."""

import json
import os
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path

import openai
from openai import AsyncOpenAI

from ..models.consciousness import MinuteEntry, ConsciousnessEntry, HourChunk
from ..models.scenario import Scenario


class ConsciousnessGenerator:
    """Generates consciousness entries using OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.temperature = 0.6
        self.vocabulary_bands = {}  # Cache for vocabulary bands
    
    def _load_vocabulary_band(self, vocabulary_period: str) -> Dict[str, Any]:
        """Load vocabulary band for the given period."""
        if vocabulary_period in self.vocabulary_bands:
            return self.vocabulary_bands[vocabulary_period]
        
        # Parse vocabulary period (e.g., "1.1" -> year 1, period 1)
        try:
            year, period = vocabulary_period.split('.')
            filename = f"my_monologue/vocabulary/vocabulary_year_{year}_period_{period}.json"
            
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    vocab_data = json.load(f)
                    self.vocabulary_bands[vocabulary_period] = vocab_data
                    return vocab_data
            else:
                # Fallback for missing files
                return self._get_fallback_vocabulary(vocabulary_period)
        except Exception as e:
            print(f"Warning: Could not load vocabulary for period {vocabulary_period}: {e}")
            return self._get_fallback_vocabulary(vocabulary_period)
    
    def _get_fallback_vocabulary(self, vocabulary_period: str) -> Dict[str, Any]:
        """Get fallback vocabulary based on developmental stage."""
        try:
            year = int(vocabulary_period.split('.')[0])
            if year == 1:
                # Pre-linguistic stage for newborns
                return {
                    "language_characteristics": ["cooing", "crying", "babbling", "sound recognition"],
                    "forbidden_patterns": ["words", "sentences", "complex sounds", "abstract concepts"],
                    "core_vocabulary": [],  # No words for newborns
                    "developmental_stage": "pre-linguistic"
                }
            elif year == 2:
                # Early linguistic stage
                return {
                    "language_characteristics": ["50-200 words", "two-word combinations", "naming objects"],
                    "forbidden_patterns": ["complex sentences", "abstract reasoning", "future planning"],
                    "core_vocabulary": ["mama", "dada", "ball", "milk", "up", "down", "more", "no"],
                    "developmental_stage": "holophrastic"
                }
            else:
                # Default fallback
                return {
                    "language_characteristics": ["basic communication"],
                    "forbidden_patterns": ["complex language"],
                    "core_vocabulary": [],
                    "developmental_stage": "basic"
                }
        except:
            return {
                "language_characteristics": ["basic communication"],
                "forbidden_patterns": ["complex language"],
                "core_vocabulary": [],
                "developmental_stage": "basic"
            }
    
    async def generate_hour(self, hour_plan: Dict[str, Any], scenario: Scenario) -> HourChunk:
        """Generate one hour of consciousness monologue."""
        try:
            # Create prompt
            prompt = self._create_hour_prompt(hour_plan, scenario)
            
            # Call OpenAI API
            response = await self._call_openai(prompt)
            
            # Parse and validate response
            parsed_data = self._parse_hour_response(response, hour_plan)
            
            # Convert to MinuteEntry objects
            entries = []
            for entry_data in parsed_data["entries"]:
                components = entry_data["consciousness_components"]
                entry = MinuteEntry(
                    minute=entry_data["minute"],
                    consciousness_components=ConsciousnessEntry(
                        sensory_perception=components.get("sensory_perception", "quiet"),
                        interoception=components.get("interoception", "comfortable"),
                        attention_focus=components.get("attention_focus", "drifting"),
                        intention_motive=components.get("intention_motive", "resting"),
                        social_interaction=components.get("social_interaction", "alone"),
                        vocalization=components.get("vocalization", "silent"),
                        motor_behavior=components.get("motor_behavior", "still"),
                        emotional_expression=components.get("emotional_expression", "neutral"),
                        environmental_learning=components.get("environmental_learning", "observing"),
                        reflective_awareness=components.get("reflective_awareness", "basic")
                    ),
                    labels=entry_data.get("labels", {
                        "arousal_level": "medium",
                        "dominant_emotion": "neutral",
                        "cognitive_load": "minimal",
                        "social_context": "alone"
                    })
                )
                entries.append(entry)
            
            # Create state summary
            state_summary = {
                "sleep_state": hour_plan["sleep_state"],
                "dominant_emotions": hour_plan["developmental_context"]["dominant_emotions"],
                "vocabulary_period": hour_plan["developmental_context"]["vocabulary_period"],
                "context_tags": hour_plan["developmental_context"]["routine_tags"],
                "developmental_focus": hour_plan["developmental_context"]["cognitive_focus"]
            }

            return HourChunk(
                hour=hour_plan["hour"],
                state_summary=state_summary,
                entries=entries
            )
            
        except Exception as e:
            print(f"Error generating hour {hour_plan['hour']}: {e}")
            print(f"Falling back to generated content for hour {hour_plan['hour']}")
            # Create a fallback hour chunk with varied content
            return self._create_fallback_hour_chunk(hour_plan)
    
    def _create_hour_prompt(self, hour_plan: Dict[str, Any], scenario: Scenario) -> str:
        """Create prompt for generating one hour of consciousness, scaled 0–5 years."""
        hour = hour_plan["hour"]
        year = hour_plan.get("year", 1)
        
        # Caregiver names for realism
        caregiver_names = ", ".join([c.name for c in scenario.caregivers]) if getattr(scenario, "caregivers", None) else "caregivers"
        
        # Load vocabulary constraints for this developmental period
        vocabulary_period = hour_plan["developmental_context"]["vocabulary_period"]
        vocab_data = self._load_vocabulary_band(vocabulary_period)
        language_characteristics = vocab_data.get("language_characteristics", [])
        forbidden_patterns = vocab_data.get("forbidden_patterns", [])
        core_vocabulary = vocab_data.get("core_vocabulary", [])
        developmental_stage = vocab_data.get("developmental_stage", "basic")
        
        # Age-specific behavioral crib sheets (concise, by year)
        if year <= 1:
            age_guidelines = (
                "Focus: sensory integration, attachment. Include: feeding in arms/high chair, floor play, "
                "tummy time (early), cause–effect toys (later), object permanence search (later), pulling to stand/cruising/first steps (late year), "
                "gestures (point/show/wave), joint attention (look to caregiver then object), protowords/first words (late year)."
            )
            required_patterns = (
                "Across the hour (awake minutes): ≥4 pointing/showing or joint attention moments; ≥3 motor milestones (pull-to-stand/cruise/steps); "
                "≥4 language productions (protowords/first words or onomatopoeia); vary intents (request/protest/comment)."
            )
        elif year == 2:
            age_guidelines = (
                "Focus: two-word combinations, parallel play, climbing, symbolic play, stronger self-agency. Include snack/meals in high chair, playground, "
                "naps, simple pretend (feeding doll), simple problem-solving, frequent gestures and early phrases."
            )
            required_patterns = (
                "Across the hour: ≥5 two-word productions; ≥3 pretend/functional play acts; ≥3 motor challenges (climb/run/kick)."
            )
        elif year == 3:
            age_guidelines = (
                "Focus: sentences, why-questions, turn-taking, toilet training context, peer parallel-to-associative play. Include caregiver dialogue, "
                "simple narratives about events, rule-learning moments, brief frustration and recovery."
            )
            required_patterns = (
                "Across the hour: ≥6 sentence-like productions; ≥3 peer or caregiver turn-taking interactions; ≥2 problem-solving episodes."
            )
        elif year == 4:
            age_guidelines = (
                "Focus: multi-sentence, imaginative play, preschool routines, cooperative play beginnings. Include story sharing, planning actions, "
                "role-play with peers/caregivers, more complex emotions and regulation."
            )
            required_patterns = (
                "Across the hour: ≥6 multi-sentence moments; ≥3 cooperative or imaginative play scenes; ≥2 perspective-taking moments."
            )
        else:
            age_guidelines = (
                "Focus: rich narratives, early friendships, rule-based games, extended attention, curiosity. Include preschool/classroom-like moments, "
                "helping tasks, negotiation, simple explanations, pride in mastery."
            )
            required_patterns = (
                "Across the hour: ≥6 coherent narrative snippets; ≥3 peer interactions with turn-taking; ≥2 self-initiated plans and follow-through."
            )
        
        # Vocabulary constraints text
        if core_vocabulary:
            vocab_constraints = f"ALLOWED VOCABULARY (examples): {', '.join(core_vocabulary[:12])}"
        else:
            vocab_constraints = "NO WORDS ALLOWED - Use only pre-linguistic sounds (cooing, crying, babbling) except during sleep transitions."
        forbidden_text = f"FORBIDDEN: {', '.join(forbidden_patterns)}" if forbidden_patterns else ""
        
        # Build prompt
        prompt = f"""
You are generating structured JSON (valid JSON only) for 60 minutes of a child's inner monologue for hour {hour_plan['hour']}:00.

CONTEXT:
- Week {hour_plan['week']} of life | Year {year}
- Time: {hour_plan['hour']}:00 | Sleep state: {hour_plan['sleep_state']}
- Caregivers: {caregiver_names}
- Developmental Stage: {developmental_stage}
- Language Characteristics: {', '.join(language_characteristics)}

AGE-SPECIFIC BEHAVIORAL GUIDELINES:
{age_guidelines}

REQUIRED DISTRIBUTION (approximate):
{required_patterns}

VOCABULARY CONSTRAINTS:
{vocab_constraints}
{forbidden_text}

CONTENT RULES:
- Write RICH, DETAILED descriptions (3-12 words per field) that paint vivid pictures of the child's experience.
- Vary settings naturally (home rooms, outdoors/park, mealtime, bath, story) consistent with time of day.
- Use caregiver names where natural. Avoid newborn-only content unless sleeping.
- Ensure minutes are UNIQUE and coherent across the hour (no copy-paste).
- Include specific sensory details, emotional nuances, and developmental milestones.

EXAMPLES OF RICH CONTENT:
- sensory_perception: "mother's warm skin against cheek during feeding" (not "warm skin")
- interoception: "growing hunger pangs in empty tummy" (not "hungry")
- attention_focus: "bright red ball rolling across wooden floor" (not "red ball")
- social_interaction: "Maya's gentle lullaby while rocking in her arms" (not "Maya singing")
- vocalization: "excited babbling 'ba-ba-ba' while reaching for toy" (not "babbling")
- motor_behavior: "attempting to pull up on coffee table edge" (not "pulling up")

OUTPUT (valid JSON only):
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

Return ONLY the JSON object. Ensure exactly 60 entries (minutes 0–59) and valid JSON.
"""
        return prompt
    
    def _calculate_age_years(self, scenario: Scenario) -> int:
        """Calculate child's age in years."""
        # This would need to be calculated based on target date
        # For now, return a reasonable default
        return 1
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add rate limiting
                if attempt > 0:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=16000,  # Within model limit of 16,384 tokens
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                
                # Basic validation of response
                if not content or len(content) < 100:
                    raise ValueError("Response too short or empty")
                
                return content
                
            except Exception as e:
                print(f"OpenAI API attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def _parse_hour_response(self, response: str, hour_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Parse OpenAI response into structured data."""
        try:
            # Clean the response first
            response = response.strip()
            
            # Try to find JSON object boundaries
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
                raise ValueError("No valid JSON object found in response")
            
            # Extract just the JSON part
            json_str = response[start_idx:end_idx + 1]
            
            # Try to fix common truncation issues
            json_str = self._fix_truncated_json(json_str)
            
            data = json.loads(json_str)
            
            # Validate structure
            if "hour" not in data or "entries" not in data:
                raise ValueError("Invalid response structure")
            
            if len(data["entries"]) != 60:
                raise ValueError(f"Expected 60 entries, got {len(data['entries'])}")
            
            # Validate each entry
            for i, entry in enumerate(data["entries"]):
                if "minute" not in entry or "consciousness_components" not in entry:
                    raise ValueError(f"Invalid entry structure at minute {i}")
                
                components = entry["consciousness_components"]
                required_components = [
                    "sensory_perception", "interoception", "attention_focus", 
                    "intention_motive", "social_interaction", "vocalization",
                    "motor_behavior", "emotional_expression", "environmental_learning",
                    "reflective_awareness"
                ]
                
                for component in required_components:
                    if component not in components:
                        raise ValueError(f"Missing component {component} at minute {i}")
            
            return data
            
        except json.JSONDecodeError as e:
            # Log the problematic response for debugging
            print(f"JSON Parse Error: {e}")
            print(f"Response length: {len(response)}")
            print(f"Response preview: {response[:200]}...")
            raise ValueError(f"Invalid JSON response: {e}")
        except Exception as e:
            print(f"Parse Error: {e}")
            print(f"Response preview: {response[:200]}...")
            raise ValueError(f"Failed to parse response: {e}")
    
    def _fix_truncated_json(self, json_str: str) -> str:
        """Attempt to fix common JSON truncation issues."""
        try:
            # If JSON is valid, return as-is
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            pass
        
        # Try to fix common truncation patterns
        # Look for incomplete entries and close them
        if '"entries": [' in json_str:
            # Find the last complete entry
            entries_start = json_str.find('"entries": [')
            if entries_start != -1:
                # Try to find the last complete entry
                last_complete_entry = json_str.rfind('},')
                if last_complete_entry != -1:
                    # Close the entries array and main object
                    fixed_json = json_str[:last_complete_entry + 1] + ']}'
                    try:
                        json.loads(fixed_json)
                        return fixed_json
                    except json.JSONDecodeError:
                        pass
        
        # If all else fails, return original
        return json_str
    
    async def generate_day(self, scenario: Scenario, hour_plans: List[Dict[str, Any]]) -> List[HourChunk]:
        """Generate a full day of consciousness (24 hours)."""
        hour_chunks = []
        
        for hour_plan in hour_plans:
            try:
                hour_chunk = await self.generate_hour(hour_plan, scenario)
                hour_chunks.append(hour_chunk)
            except Exception as e:
                # Log error and continue with next hour
                print(f"Error generating hour {hour_plan['hour']}: {e}")
                # Create a fallback hour chunk
                fallback_chunk = self._create_fallback_hour_chunk(hour_plan)
                hour_chunks.append(fallback_chunk)
        
        return hour_chunks
    
    def _create_fallback_hour_chunk(self, hour_plan: Dict[str, Any]) -> HourChunk:
        """Create a fallback hour chunk when generation fails."""
        entries = []
        
        # Create varied fallback content based on hour and context
        hour = hour_plan["hour"]
        is_night = hour < 6 or hour > 20
        is_morning = 6 <= hour <= 12
        is_afternoon = 13 <= hour <= 17
        is_evening = 18 <= hour <= 20
        
        # Load vocabulary constraints for this period
        vocabulary_period = hour_plan["developmental_context"]["vocabulary_period"]
        vocab_data = self._load_vocabulary_band(vocabulary_period)
        core_vocabulary = vocab_data.get("core_vocabulary", [])
        developmental_stage = vocab_data.get("developmental_stage", "basic")
        
        # Determine appropriate vocalizations based on developmental stage
        if developmental_stage == "pre-linguistic" or not core_vocabulary:
            # Newborn - only pre-linguistic sounds
            pre_linguistic_vocalizations = ["gentle cooing", "content gurgling", "soft crying", "quiet babbling", 
                                           "satisfied sounds", "sleepy murmurs", "hungry cries", "comforted coos"]
        else:
            # Has vocabulary - can use simple words
            simple_words = [word for word in core_vocabulary if len(word) <= 4][:5]  # Simple words only
            pre_linguistic_vocalizations = [f"trying to say {word}" for word in simple_words] + ["babbling", "cooing"]
        
        # Developmentally appropriate content based on newborn activities
        feeding_content = {
            "sensory": [
                "mother's warm skin against cheek", "gentle lullaby voice", "soft breast texture", "warm milk scent",
                "caregiver's heartbeat", "soft blanket texture", "gentle rocking motion", "familiar voice patterns"
            ],
            "social": [
                "eye contact with caregiver", "responding to familiar voice", "calming touch", "bonding moment",
                "caregiver's loving gaze", "gentle talking", "soothing presence", "secure attachment"
            ],
            "motor": [
                "rooting reflex", "sucking motion", "hand grasping", "body relaxation",
                "gentle arm movements", "head turning", "mouth opening", "comfortable positioning"
            ],
            "emotional": [
                "content during feeding", "secure with caregiver", "satisfied and warm", "peaceful connection",
                "loved and protected", "calm and satisfied", "trusting and safe", "nurtured and cared for"
            ],
            "vocal": pre_linguistic_vocalizations
        }
        
        tummy_time_content = {
            "sensory": [
                "firm surface under chest", "different perspective of room", "gravity on body", "new visual angles",
                "texture of play mat", "caregiver's encouraging voice", "bright colors nearby", "gentle support"
            ],
            "social": [
                "caregiver encouraging voice", "gentle support touch", "facial expressions", "motivational sounds",
                "cheering and praise", "helping hands", "loving encouragement", "patient guidance"
            ],
            "motor": [
                "attempting to lift head", "pushing up with arms", "turning head side to side", "strengthening neck",
                "kicking legs", "reaching movements", "head control practice", "muscle building"
            ],
            "emotional": [
                "frustrated by effort", "determined to succeed", "tired but trying", "proud of progress",
                "challenged but motivated", "working hard", "feeling accomplished", "building confidence"
            ],
            "vocal": pre_linguistic_vocalizations
        }
        
        playtime_content = {
            "sensory": [
                "high-contrast black and white patterns", "gentle rattling sounds", "soft fabric textures", "bright colors",
                "musical mobile sounds", "different textures to touch", "visual stimulation", "auditory exploration"
            ],
            "social": [
                "caregiver's animated face", "singing and talking", "playful interactions", "responsive engagement",
                "mirror play", "peek-a-boo games", "social smiling", "interactive communication"
            ],
            "motor": [
                "reaching toward objects", "tracking with eyes", "hand-eye coordination", "exploratory movements",
                "grasping attempts", "visual tracking", "head turning", "body coordination"
            ],
            "emotional": [
                "excited by new stimuli", "curious about patterns", "engaged and alert", "delighted by interaction",
                "amused by games", "interested in exploration", "happy and playful", "enthusiastic learning"
            ],
            "vocal": pre_linguistic_vocalizations
        }
        
        sleep_content = {
            "sensory": [
                "soft blanket against skin", "gentle breathing sounds", "warm room temperature", "peaceful darkness",
                "comforting swaddle", "quiet environment", "familiar scents", "gentle lullabies"
            ],
            "social": [
                "caregiver's presence nearby", "soothing touch", "familiar voice", "secure environment",
                "loving watchfulness", "protective presence", "gentle care", "safe haven"
            ],
            "motor": [
                "gentle twitches", "hand-to-mouth movements", "self-soothing gestures", "relaxed body",
                "sleep movements", "comfortable positioning", "natural reflexes", "peaceful rest"
            ],
            "emotional": [
                "calm and peaceful", "secure and warm", "content and satisfied", "ready for rest",
                "loved and protected", "safe and comfortable", "trusting and relaxed", "nurtured and calm"
            ],
            "vocal": pre_linguistic_vocalizations
        }
        
        # Determine activity context based on time and sleep state
        is_feeding_time = hour in [2, 6, 10, 14, 18, 22]  # Typical newborn feeding schedule
        is_awake_time = 6 <= hour <= 22 and hour_plan["sleep_state"] == "awake"
        is_tummy_time = hour in [9, 15] and is_awake_time  # Brief tummy time sessions
        is_playtime = hour in [8, 16] and is_awake_time  # Sensory stimulation
        
        for minute in range(60):
            minute_variation = minute % 8  # 8 different variations
            
            # Select appropriate content based on context
            if is_feeding_time and is_awake_time:
                content = feeding_content
                activity = "feeding"
            elif is_tummy_time:
                content = tummy_time_content
                activity = "tummy time"
            elif is_playtime:
                content = playtime_content
                activity = "sensory play"
            else:
                content = sleep_content
                activity = "rest"
            
            entry = MinuteEntry(
                minute=minute,
                consciousness_components=ConsciousnessEntry(
                    sensory_perception=content["sensory"][minute_variation],
                    interoception="comfortable and secure" if activity != "tummy time" else "working hard",
                    attention_focus=f"focused on {activity}" if is_awake_time else "drifting peacefully",
                    intention_motive="seeking comfort" if activity == "feeding" else "exploring" if activity == "sensory play" else "resting",
                    social_interaction=content["social"][minute_variation],
                    vocalization=content["vocal"][minute_variation],
                    motor_behavior=content["motor"][minute_variation],
                    emotional_expression=content["emotional"][minute_variation],
                    environmental_learning=f"learning through {activity}" if is_awake_time else "consolidating experiences",
                    reflective_awareness="basic awareness of needs" if activity == "feeding" else "present moment focus"
                ),
                labels={
                    "arousal_level": "high" if activity == "tummy time" else "medium" if is_awake_time else "low",
                    "dominant_emotion": "content" if activity == "feeding" else "frustrated" if activity == "tummy time" else "calm",
                    "cognitive_load": "medium" if activity in ["tummy time", "sensory play"] else "minimal",
                    "social_context": "with_caregivers" if is_awake_time else "alone"
                }
            )
            entries.append(entry)
        
        # Create state summary
        state_summary = {
            "sleep_state": hour_plan["sleep_state"],
            "dominant_emotions": hour_plan["developmental_context"]["dominant_emotions"],
            "vocabulary_period": hour_plan["developmental_context"]["vocabulary_period"],
            "context_tags": hour_plan["developmental_context"]["routine_tags"],
            "developmental_focus": hour_plan["developmental_context"]["cognitive_focus"]
        }

        return HourChunk(
            hour=hour_plan["hour"],
            state_summary=state_summary,
            entries=entries
        ) 