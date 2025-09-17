"""Automated scenario generator with templates and customization."""

import json
from datetime import date, timedelta
from typing import List, Dict, Any
from pathlib import Path

from ..models.scenario import Scenario, ChildProfile, Caregiver, Environment, Timeline


class ScenarioGenerator:
    """Generates scenario configurations with templates and customization."""
    
    def __init__(self):
        self.templates = {
            "baseline": {
                "name": "Ari",
                "birthdate": "2025-01-01",
                "sex": "F",
                "personality": {"openness": 0.6, "conscientiousness": 0.4, "extraversion": 0.3, "agreeableness": 0.7, "neuroticism": 0.5},
                "temperament_tags": ["curious", "sensitive_to_noise"],
                "caregivers": [
                    {"name": "Maya", "relation": "mother"},
                    {"name": "Dev", "relation": "father"}
                ],
                "environment": {
                    "home_type": "apartment",
                    "city": "Seattle",
                    "timezone": "America/Los_Angeles",
                    "socioeconomic_status": "middle",
                    "cultural_background": "US"
                }
            },
            "introverted": {
                "name": "Sam",
                "birthdate": "2025-03-15",
                "sex": "M",
                "personality": {"openness": 0.7, "conscientiousness": 0.6, "extraversion": 0.2, "agreeableness": 0.8, "neuroticism": 0.4},
                "temperament_tags": ["shy", "observant", "sensitive_to_noise"],
                "caregivers": [
                    {"name": "Alex", "relation": "mother"},
                    {"name": "Jordan", "relation": "father"}
                ],
                "environment": {
                    "home_type": "house",
                    "city": "Portland",
                    "timezone": "America/Los_Angeles",
                    "socioeconomic_status": "upper_middle",
                    "cultural_background": "US"
                }
            },
            "extroverted": {
                "name": "Zoe",
                "birthdate": "2025-06-10",
                "sex": "F",
                "personality": {"openness": 0.8, "conscientiousness": 0.3, "extraversion": 0.9, "agreeableness": 0.6, "neuroticism": 0.3},
                "temperament_tags": ["social", "energetic", "adventurous"],
                "caregivers": [
                    {"name": "Maria", "relation": "mother"},
                    {"name": "Carlos", "relation": "father"}
                ],
                "environment": {
                    "home_type": "house",
                    "city": "Austin",
                    "timezone": "America/Chicago",
                    "socioeconomic_status": "middle",
                    "cultural_background": "US"
                }
            }
        }
    
    def generate_baseline_scenario(self, monologue_id: str = "baseline_v1") -> Scenario:
        """Generate a baseline scenario."""
        template = self.templates["baseline"]
        
        return Scenario(
            monologue_id=monologue_id,
            seed=12345,
            language="en-US",
            culture="US",
            child_profile=ChildProfile(
                name=template["name"],
                birthdate=date.fromisoformat(template["birthdate"]),
                sex=template["sex"],
                personality=template["personality"],
                temperament_tags=template["temperament_tags"]
            ),
            caregivers=[
                Caregiver(name=c["name"], relation=c["relation"])
                for c in template["caregivers"]
            ],
            environment=Environment(**template["environment"]),
            timeline=Timeline()
        )
    
    def generate_custom_scenario(self, 
                               monologue_id: str,
                               template_name: str = "baseline",
                               customizations: Dict[str, Any] = None) -> Scenario:
        """Generate a custom scenario from template with modifications."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name].copy()
        customizations = customizations or {}
        
        # Apply customizations
        for key, value in customizations.items():
            if key in template:
                if isinstance(template[key], dict):
                    template[key].update(value)
                else:
                    template[key] = value
        
        return Scenario(
            monologue_id=monologue_id,
            seed=customizations.get("seed", 12345),
            language=customizations.get("language", "en-US"),
            culture=customizations.get("culture", "US"),
            child_profile=ChildProfile(
                name=template["name"],
                birthdate=date.fromisoformat(template["birthdate"]),
                sex=template["sex"],
                personality=template["personality"],
                temperament_tags=template["temperament_tags"],
                special_needs=customizations.get("special_needs", [])
            ),
            caregivers=[
                Caregiver(name=c["name"], relation=c["relation"])
                for c in template["caregivers"]
            ],
            environment=Environment(**template["environment"]),
            timeline=Timeline(
                vocabulary_bands=customizations.get("vocabulary_bands", {}),
                milestones=customizations.get("milestones", []),
                scheduled_events=customizations.get("scheduled_events", [])
            ),
            style=customizations.get("style", {})
        )
    
    def generate_from_file(self, scenario_path: Path) -> Scenario:
        """Generate scenario from JSON file."""
        with open(scenario_path, 'r') as f:
            data = json.load(f)
        
        return Scenario(**data)
    
    def save_scenario(self, scenario: Scenario, output_path: Path):
        """Save scenario to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(scenario.model_dump(mode='json'), f, indent=2)
        
        print(f"Scenario saved to {output_path}")
    
    def create_scenario_template(self, template_name: str, output_dir: Path):
        """Create a scenario template file."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        scenario = self.generate_custom_scenario(f"{template_name}_template", template_name)
        
        output_path = output_dir / f"{template_name}_template.json"
        self.save_scenario(scenario, output_path)
    
    def list_templates(self) -> List[str]:
        """List available templates."""
        return list(self.templates.keys())
    
    def add_template(self, name: str, template_data: Dict[str, Any]):
        """Add a new template."""
        self.templates[name] = template_data
    
    def generate_all_templates(self, output_dir: Path):
        """Generate all template scenarios."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for template_name in self.templates:
            self.create_scenario_template(template_name, output_dir) 