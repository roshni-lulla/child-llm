"""Validator for consciousness entries."""

import re
from typing import Dict, List, Any, Tuple
from ..models.consciousness import MinuteEntry, ConsciousnessEntry


class ConsciousnessValidator:
    """Validates consciousness entries for quality and consistency."""
    
    def __init__(self):
        self.forbidden_words = [
            "quantum", "algorithm", "neural", "network", "consciousness",
            "substrate", "computation", "emergence", "phenomenology"
        ]
    
    def validate_minute_entry(self, entry: MinuteEntry, age_years: int) -> Tuple[bool, List[str]]:
        """Validate a single minute entry."""
        errors = []
        
        # Check sentence length
        components = entry.consciousness_components
        for field_name, text in components.model_dump().items():
            if len(text.split()) > self._get_max_sentence_length(age_years):
                errors.append(f"{field_name}: sentence too long for age {age_years}")
        
        # Check for forbidden words
        for field_name, text in components.model_dump().items():
            for word in self.forbidden_words:
                if word.lower() in text.lower():
                    errors.append(f"{field_name}: contains forbidden word '{word}'")
        
        # Check for age-inappropriate patterns
        age_errors = self._check_age_appropriateness(entry, age_years)
        errors.extend(age_errors)
        
        # Check for empty or very short entries
        for field_name, text in components.model_dump().items():
            if len(text.strip()) < 3:
                errors.append(f"{field_name}: too short")
        
        return len(errors) == 0, errors
    
    def _get_max_sentence_length(self, age_years: int) -> int:
        """Get maximum sentence length for age."""
        constraints = {
            0: 3, 1: 4, 2: 5, 3: 6, 4: 7, 5: 8
        }
        return constraints.get(age_years, 5)
    
    def _check_age_appropriateness(self, entry: MinuteEntry, age_years: int) -> List[str]:
        """Check if entry is appropriate for the child's age."""
        errors = []
        components = entry.consciousness_components
        
        # Check for future tense in early years
        if age_years <= 2:
            future_patterns = [
                r'\bwill\b', r'\bgoing to\b', r'\bshall\b',
                r'\bwould\b', r'\bcould\b', r'\bshould\b'
            ]
            for field_name, text in components.model_dump().items():
                for pattern in future_patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        errors.append(f"{field_name}: contains future tense (inappropriate for age {age_years})")
        
        # Check for complex reasoning in early years
        if age_years <= 2:
            complex_patterns = [
                r'\bbecause\b', r'\bif\s+.*\s+then\b', r'\bhowever\b',
                r'\balthough\b', r'\bdespite\b', r'\bnevertheless\b'
            ]
            for field_name, text in components.model_dump().items():
                for pattern in complex_patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        errors.append(f"{field_name}: contains complex reasoning (inappropriate for age {age_years})")
        
        # Check for abstract concepts in early years
        if age_years <= 3:
            abstract_patterns = [
                r'\bjustice\b', r'\bfreedom\b', r'\btruth\b', r'\bbeauty\b',
                r'\bphilosophy\b', r'\bmetaphysics\b', r'\bepistemology\b'
            ]
            for field_name, text in components.model_dump().items():
                for pattern in abstract_patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        errors.append(f"{field_name}: contains abstract concepts (inappropriate for age {age_years})")
        
        return errors
    
    def validate_hour_chunk(self, hour_chunk: Dict[str, Any], age_years: int) -> Tuple[bool, List[str]]:
        """Validate an hour chunk."""
        errors = []
        
        # Check that we have exactly 60 entries
        if len(hour_chunk.get("entries", [])) != 60:
            errors.append(f"Expected 60 entries, got {len(hour_chunk.get('entries', []))}")
        
        # Validate each entry
        for i, entry_data in enumerate(hour_chunk.get("entries", [])):
            try:
                entry = MinuteEntry(**entry_data)
                is_valid, entry_errors = self.validate_minute_entry(entry, age_years)
                if not is_valid:
                    errors.extend([f"Minute {i}: {error}" for error in entry_errors])
            except Exception as e:
                errors.append(f"Minute {i}: Invalid entry structure - {e}")
        
        return len(errors) == 0, errors
    
    def get_validation_summary(self, errors: List[str]) -> Dict[str, Any]:
        """Get a summary of validation errors."""
        error_types = {}
        for error in errors:
            error_type = error.split(":")[0] if ":" in error else "general"
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total_errors": len(errors),
            "error_types": error_types,
            "is_valid": len(errors) == 0
        } 