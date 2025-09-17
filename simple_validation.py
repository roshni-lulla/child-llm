#!/usr/bin/env python3
"""Simple validation script for developmental appropriateness with optional LLM review."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from openai import OpenAI

PSYCHOLOGIST_SYSTEM = (
    "You are a licensed developmental psychologist. You evaluate 60-minute child consciousness JSON for a given hour. "
    "Judge age-appropriateness (language, motor, social-emotional, cognition) versus the provided age in weeks and year. "
    "Identify newborn leakage at older ages, missing age-typical behaviors (e.g., at 12 months: pointing, joint attention, first words, cruising), "
    "and incoherent or repetitive content. Then propose precise, minimal JSON edits by minute and field to correct issues. Return a STRICT JSON object only."
)

PSYCHOLOGIST_USER_TEMPLATE = (
    "TASK: Review the following monologue hour for developmental realism.\n"
    "CONSTRAINTS: Preserve schema; propose minimal content edits; do not change labels, minute indices, or structure.\n"
    "AGE: {age_weeks} weeks (Year {year})\n"
    "QUALITY CRITERIA: age-appropriate vocalizations/words, age-appropriate motor actions, social interaction (caregivers/peers), cognition (cause-effect, joint attention), variety across minutes.\n"
    "OUTPUT JSON SCHEMA:\n"
    "{{\n"
    "  \"summary\": {{\"score\": 0-100, \"verdict\": \"pass|partial|fail\", \"notes\": \"short rationale\"}},\n"
    "  \"issues\": [ {{\"type\": \"language|motor|social|cognition|variety\", \"minute\": int, \"description\": \"...\"}} ],\n"
    "  \"suggested_edits\": [ {{\"minute\": int, \"field\": \"sensory_perception|interoception|attention_focus|intention_motive|social_interaction|vocalization|motor_behavior|emotional_expression|environmental_learning|reflective_awareness\", \"new_value\": \"brief replacement text\"}} ]\n"
    "}}\n\n"
    "MONOLOGUE_JSON:\n{monologue}\n"
)

def validate_developmental_appropriateness(file_path: str, use_llm: bool = False, api_key: str = None, fix_content: bool = False) -> Dict[str, Any]:
    """Validate that generated content is developmentally appropriate; optionally call LLM for psychologist review and fixes."""
    with open(file_path, 'r') as f:
        data = json.load(f)

    date_str = data['date']
    birth_date = "2025-01-01"  # From scenario
    from datetime import datetime
    birth = datetime.strptime(birth_date, "%Y-%m-%d")
    target = datetime.strptime(date_str, "%Y-%m-%d")
    age_weeks = (target - birth).days // 7
    year = max(1, age_weeks // 52 + 1)

    results = {
        "file": file_path,
        "date": date_str,
        "age_weeks": age_weeks,
        "issues": [],
        "score": 100,
        "llm_review": None,
        "suggested_edits": [],
        "fixed_content": None,
        "fixes_applied": 0
    }

    # Simple checks
    results["issues"].extend(check_vocabulary_appropriateness(data, age_weeks))
    results["issues"].extend(check_behavioral_appropriateness(data, age_weeks))
    results["issues"].extend(check_content_variety(data))
    results["score"] = max(0, 100 - len(results["issues"]) * 10)

    # Optional LLM psychologist review and fixes
    if use_llm and api_key:
        client = OpenAI(api_key=api_key)
        user_prompt = PSYCHOLOGIST_USER_TEMPLATE.format(
            age_weeks=age_weeks,
            year=year,
            monologue=json.dumps(data, ensure_ascii=False)
        )
        # Add rate limiting
        import time
        time.sleep(2)  # 2 second delay between validation calls
        
        resp = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": PSYCHOLOGIST_SYSTEM},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=1500  # Further reduced to avoid rate limits
        )
        try:
            content = resp.choices[0].message.content
            llm_json = json.loads(content)
            results["llm_review"] = llm_json.get("summary", {})
            results["suggested_edits"] = llm_json.get("suggested_edits", [])
            
            # If LLM provides a score, blend conservatively
            llm_score = llm_json.get("summary", {}).get("score")
            if isinstance(llm_score, (int, float)):
                results["score"] = int((results["score"] + llm_score) / 2)
            
            # Apply fixes if requested
            if fix_content and results["suggested_edits"]:
                fixed_data = apply_psychologist_fixes(data, results["suggested_edits"], age_weeks, year)
                if fixed_data:
                    results["fixed_content"] = fixed_data
                    results["fixes_applied"] = len(results["suggested_edits"])
                    # Save fixed version
                    fixed_file_path = file_path.replace('.json', '_fixed.json')
                    with open(fixed_file_path, 'w') as f:
                        json.dump(fixed_data, f, indent=2)
                    results["fixed_file"] = fixed_file_path
                    
        except Exception as e:
            results["issues"].append(f"LLM review parse error: {e}")
            # keep simple score

    return results

# Existing simple checks below (unchanged)

def check_vocabulary_appropriateness(data: Dict[str, Any], age_weeks: int) -> List[str]:
    issues = []
    vocalizations = []
    for hour_chunk in data.get('hour_chunks', []):
        for entry in hour_chunk.get('entries', []):
            vocal = entry.get('consciousness_components', {}).get('vocalization', '')
            if vocal:
                vocalizations.append(vocal.lower())
    
    # Pre-linguistic sounds that are appropriate for newborns
    appropriate_sounds = {'coo', 'cooing', 'babble', 'babbling', 'gurgle', 'gurgling', 'cry', 'crying', 
                         'whimper', 'whimpering', 'giggle', 'giggling', 'laugh', 'laughing', 'yawn', 'yawning',
                         'murmur', 'murmuring', 'whine', 'whining', 'squeal', 'squealing', 'splash', 'splashing',
                         'mmm', 'ah', 'oh', 'eh', 'uh', 'none', 'silence', 'quiet'}
    
    if age_weeks <= 4:
        for vocal in vocalizations:
            words = vocal.split()
            for word in words:
                # Clean word of punctuation
                clean_word = ''.join(c for c in word if c.isalnum())
                if len(clean_word) > 2 and clean_word.isalpha() and clean_word not in appropriate_sounds:
                    issues.append(f"Newborn using inappropriate word '{clean_word}' - should only use pre-linguistic sounds")
                    break
    elif age_weeks <= 26:
        word_count = 0
        for vocal in vocalizations:
            words = vocal.split()
            for word in words:
                clean_word = ''.join(c for c in word if c.isalnum())
                if len(clean_word) > 2 and clean_word.isalpha() and clean_word not in appropriate_sounds:
                    word_count += 1
        if word_count > 15:  # More lenient for 6+ months
            issues.append(f"Too many complex words ({word_count}) for {age_weeks} weeks - should have fewer words")
    return issues

def check_behavioral_appropriateness(data: Dict[str, Any], age_weeks: int) -> List[str]:
    issues = []
    motor_behaviors = []
    for hour_chunk in data.get('hour_chunks', []):
        for entry in hour_chunk.get('entries', []):
            motor = entry.get('consciousness_components', {}).get('motor_behavior', '')
            if motor:
                motor_behaviors.append(motor.lower())
    if age_weeks < 40:
        for motor in motor_behaviors:
            if any(word in motor for word in ['walking', 'walk', 'steps', 'running']):
                issues.append(f"Walking behavior at {age_weeks} weeks - too early (typically after 40 weeks)")
    if age_weeks < 20:
        for motor in motor_behaviors:
            if any(word in motor for word in ['sitting', 'sit']):
                issues.append(f"Sitting behavior at {age_weeks} weeks - too early (typically after 20 weeks)")
    return issues

def check_content_variety(data: Dict[str, Any]) -> List[str]:
    issues = []
    vocalizations = []
    for hour_chunk in data.get('hour_chunks', []):
        for entry in hour_chunk.get('entries', []):
            vocal = entry.get('consciousness_components', {}).get('vocalization', '')
            if vocal:
                vocalizations.append(vocal)
    if len(vocalizations) > 0:
        unique_vocalizations = set(vocalizations)
        if len(unique_vocalizations) < len(vocalizations) * 0.3:
            issues.append(f"Content too repetitive - only {len(unique_vocalizations)} unique vocalizations out of {len(vocalizations)}")
    return issues


def apply_psychologist_fixes(data: Dict[str, Any], suggested_edits: List[Dict[str, Any]], age_weeks: int, year: int) -> Dict[str, Any]:
    """Apply psychologist-suggested fixes to the monologue data."""
    fixed_data = json.loads(json.dumps(data))  # Deep copy
    
    fixes_applied = 0
    for edit in suggested_edits:
        try:
            minute = edit.get("minute")
            field = edit.get("field")
            new_value = edit.get("new_value")
            
            if minute is None or field is None or new_value is None:
                continue
                
            # Find the hour chunk and minute entry
            for hour_chunk in fixed_data.get("hour_chunks", []):
                for entry in hour_chunk.get("entries", []):
                    if entry.get("minute") == minute:
                        if field in entry.get("consciousness_components", {}):
                            entry["consciousness_components"][field] = new_value
                            fixes_applied += 1
                        break
        except Exception as e:
            print(f"Warning: Could not apply fix {edit}: {e}")
            continue
    
    # Add metadata about fixes
    if "provenance" not in fixed_data:
        fixed_data["provenance"] = {}
    fixed_data["provenance"]["psychologist_fixes"] = {
        "applied": fixes_applied,
        "age_weeks": age_weeks,
        "year": year,
        "timestamp": datetime.now().isoformat()
    }
    
    return fixed_data


def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_validation.py <day_file.json> [--llm] [--fix]")
        sys.exit(1)
    file_path = sys.argv[1]
    use_llm = '--llm' in sys.argv
    fix_content = '--fix' in sys.argv
    api_key = os.getenv('OPENAI_API_KEY') if use_llm else None
    if not Path(file_path).exists():
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    print(f"🔍 Validating: {file_path}")
    print("=" * 50)
    results = validate_developmental_appropriateness(file_path, use_llm=use_llm, api_key=api_key, fix_content=fix_content)
    print(f"📅 Date: {results['date']}")
    print(f"👶 Age: {results['age_weeks']} weeks")
    print(f"📊 Score: {results['score']}/100")
    if results['issues']:
        print(f"\n⚠️  Issues found ({len(results['issues'])}):")
        for issue in results['issues']:
            print(f"  - {issue}")
    if results.get('llm_review'):
        print("\n🧠 LLM Psychologist Review:")
        print(json.dumps(results['llm_review'], indent=2))
        if results.get('suggested_edits'):
            print(f"\n🛠️ Suggested Edits ({len(results['suggested_edits'])} total):")
            print(json.dumps(results['suggested_edits'][:10], indent=2))
    if results.get('fixes_applied', 0) > 0:
        print(f"\n✅ Applied {results['fixes_applied']} psychologist fixes!")
        print(f"💾 Fixed content saved to: {results.get('fixed_file', 'N/A')}")
    if results['score'] >= 80:
        print("\n🎉 PASS: Content meets developmental standards")
    elif results['score'] >= 60:
        print("\n⚠️  PARTIAL: Some developmental issues found")
    else:
        print("\n❌ FAIL: Significant developmental issues found")

if __name__ == "__main__":
    main()
