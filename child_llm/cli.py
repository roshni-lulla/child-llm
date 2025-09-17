"""Command-line interface for Child LLM consciousness generation."""

import json
import asyncio
from datetime import date
from pathlib import Path
from typing import Optional
import typer

from .models.scenario import Scenario
from .generators.timeline_generator import TimelineGenerator
from .generators.vocabulary_generator import VocabularyGenerator
from .generators.scenario_generator import ScenarioGenerator
from .pipeline.planner import HourPlanner
from .pipeline.orchestrator import MonologueOrchestrator

app = typer.Typer(help="Child LLM - Consciousness Monologue Generator")


@app.command()
def generate_timeline(
    scenario_path: Path = typer.Argument(..., help="Path to scenario JSON file"),
    output_path: Path = typer.Option(Path("master_timeline.json"), help="Output path for timeline")
):
    """Generate developmental timeline from scenario."""
    generator = TimelineGenerator()
    generator.generate_from_scenario(scenario_path, output_path)
    typer.echo(f"Timeline generated: {output_path}")


@app.command()
def generate_vocabulary(
    scenario_path: Path = typer.Argument(..., help="Path to scenario JSON file"),
    output_dir: Path = typer.Option(Path("vocabulary"), help="Output directory for vocabulary files")
):
    """Generate vocabulary bands from scenario."""
    generator = VocabularyGenerator()
    generator.generate_from_scenario(scenario_path, output_dir)
    typer.echo(f"Vocabulary bands generated in: {output_dir}")


@app.command()
def create_scenario(
    monologue_id: str = typer.Argument(..., help="Unique monologue identifier"),
    template: str = typer.Option("baseline", help="Template to use"),
    output_path: Path = typer.Option(Path("scenarios"), help="Output directory"),
    customizations: Optional[str] = typer.Option(None, help="JSON string of customizations")
):
    """Create a new scenario from template."""
    generator = ScenarioGenerator()
    
    # Parse customizations if provided
    custom_data = {}
    if customizations:
        try:
            custom_data = json.loads(customizations)
        except json.JSONDecodeError:
            typer.echo("Error: Invalid JSON in customizations")
            raise typer.Exit(1)
    
    scenario = generator.generate_custom_scenario(monologue_id, template, custom_data)
    
    output_path.mkdir(parents=True, exist_ok=True)
    scenario_file = output_path / f"{monologue_id}.json"
    generator.save_scenario(scenario, scenario_file)
    
    typer.echo(f"Scenario created: {scenario_file}")


@app.command()
def list_templates():
    """List available scenario templates."""
    generator = ScenarioGenerator()
    templates = generator.list_templates()
    
    typer.echo("Available templates:")
    for template in templates:
        typer.echo(f"  - {template}")


@app.command()
def generate_day(
    scenario_path: Path = typer.Argument(..., help="Path to scenario JSON file"),
    target_date: str = typer.Argument(..., help="Target date (YYYY-MM-DD)"),
    timeline_path: Path = typer.Option(Path("master_timeline.json"), help="Path to timeline file"),
    output_dir: Path = typer.Option(Path("output"), help="Output directory"),
    max_concurrency: int = typer.Option(8, help="Maximum concurrent generations")
):
    """Generate one day of consciousness monologue."""
    # Load scenario
    with open(scenario_path, 'r') as f:
        scenario_data = json.load(f)
    scenario = Scenario(**scenario_data)
    
    # Load timeline
    with open(timeline_path, 'r') as f:
        timeline_data = json.load(f)
    
    # Parse date
    try:
        date_obj = date.fromisoformat(target_date)
    except ValueError:
        typer.echo("Error: Invalid date format. Use YYYY-MM-DD")
        raise typer.Exit(1)
    
    # Create orchestrator and generate
    orchestrator = MonologueOrchestrator()
    
    # Run async generation
    asyncio.run(orchestrator.generate_day(
        scenario=scenario,
        target_date=date_obj,
        timeline_data=timeline_data,
        output_dir=output_dir,
        max_concurrency=max_concurrency
    ))
    
    typer.echo(f"Day generated: {output_dir}")


@app.command()
def generate_year(
    scenario_path: Path = typer.Argument(..., help="Path to scenario JSON file"),
    year: int = typer.Argument(..., help="Year to generate (1-5)"),
    timeline_path: Path = typer.Option(Path("master_timeline.json"), help="Path to timeline file"),
    output_dir: Path = typer.Option(Path("output"), help="Output directory"),
    max_concurrency: int = typer.Option(8, help="Maximum concurrent generations")
):
    """Generate one year of consciousness monologue."""
    # Load scenario
    with open(scenario_path, 'r') as f:
        scenario_data = json.load(f)
    scenario = Scenario(**scenario_data)
    
    # Load timeline
    with open(timeline_path, 'r') as f:
        timeline_data = json.load(f)
    
    # Validate year
    if year < 1 or year > 5:
        typer.echo("Error: Year must be between 1 and 5")
        raise typer.Exit(1)
    
    # Create orchestrator and generate
    orchestrator = MonologueOrchestrator()
    
    # Run async generation
    asyncio.run(orchestrator.generate_year(
        scenario=scenario,
        year=year,
        timeline_data=timeline_data,
        output_dir=output_dir,
        max_concurrency=max_concurrency
    ))
    
    typer.echo(f"Year {year} generated: {output_dir}")


@app.command()
def setup_project(
    project_dir: Path = typer.Option(Path("child_llm_project"), help="Project directory")
):
    """Set up a new Child LLM project with all necessary files."""
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (project_dir / "scenarios").mkdir(exist_ok=True)
    (project_dir / "timeline").mkdir(exist_ok=True)
    (project_dir / "vocabulary").mkdir(exist_ok=True)
    (project_dir / "output").mkdir(exist_ok=True)
    (project_dir / "runs").mkdir(exist_ok=True)
    
    # Generate baseline scenario
    scenario_gen = ScenarioGenerator()
    baseline_scenario = scenario_gen.generate_baseline_scenario("baseline_v1")
    scenario_gen.save_scenario(baseline_scenario, project_dir / "scenarios" / "baseline_v1.json")
    
    # Generate timeline
    timeline_gen = TimelineGenerator()
    timeline = timeline_gen.generate_timeline({"child_profile": {"name": "Ari"}})
    timeline_gen.save_timeline(timeline, project_dir / "timeline" / "master_timeline.json")
    
    # Generate vocabulary
    vocab_gen = VocabularyGenerator()
    vocab_bands = vocab_gen.generate_all_vocabulary_bands()
    vocab_gen.save_vocabulary_bands(vocab_bands, project_dir / "vocabulary")
    
    typer.echo(f"Project set up in: {project_dir}")
    typer.echo("Next steps:")
    typer.echo("1. Review and customize scenario in scenarios/baseline_v1.json")
    typer.echo("2. Generate a day: child_llm generate-day scenarios/baseline_v1.json 2025-01-01")


if __name__ == "__main__":
    app() 