"""Main orchestrator for the consciousness generation pipeline."""

import asyncio
import json
from datetime import date, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..models.scenario import Scenario
from ..models.consciousness import DayFile
from .planner import HourPlanner
from .generator import ConsciousnessGenerator


class MonologueOrchestrator:
    """Orchestrates the complete consciousness generation pipeline."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.planner = HourPlanner()
        self.generator = ConsciousnessGenerator(api_key=api_key)
    
    async def generate_day(self, scenario: Scenario, target_date: date, 
                          timeline_data: Dict[str, Any], output_dir: Path,
                          max_concurrency: int = 8) -> DayFile:
        """Generate one day of consciousness monologue."""
        # Plan the day
        hour_plans = self.planner.plan_day(scenario, target_date, timeline_data)
        
        # Generate hour chunks with concurrency control
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def generate_hour_with_semaphore(hour_plan):
            async with semaphore:
                return await self.generator.generate_hour(hour_plan, scenario)
        
        # Generate all hours concurrently
        hour_chunks = await asyncio.gather(
            *[generate_hour_with_semaphore(plan) for plan in hour_plans],
            return_exceptions=True
        )
        
        # Handle any exceptions
        valid_chunks = []
        for i, chunk in enumerate(hour_chunks):
            if isinstance(chunk, Exception):
                print(f"Error generating hour {i}: {chunk}")
                # Create fallback chunk
                fallback_chunk = self.generator._create_fallback_hour_chunk(hour_plans[i])
                valid_chunks.append(fallback_chunk)
            else:
                valid_chunks.append(chunk)
        
        # Create day file
        day_file = DayFile(
            monologue_id=scenario.monologue_id,
            date=target_date.isoformat(),
            provenance={
                "model": self.generator.model,
                "prompt_version": "consciousness.v1",
                "temperature": str(self.generator.temperature),
                "seed": str(scenario.seed)
            },
            hour_chunks=valid_chunks
        )
        
        # Save to file
        await self._save_day_file(day_file, output_dir)
        
        return day_file
    
    async def generate_year(self, scenario: Scenario, year: int, 
                           timeline_data: Dict[str, Any], output_dir: Path,
                           max_concurrency: int = 8) -> List[DayFile]:
        """Generate one year of consciousness monologue."""
        # Calculate start and end dates for the year
        start_date = scenario.child_profile.birthdate + timedelta(days=365 * (year - 1))
        end_date = start_date + timedelta(days=365)
        
        # Generate each day
        day_files = []
        current_date = start_date
        
        while current_date < end_date:
            try:
                day_file = await self.generate_day(
                    scenario=scenario,
                    target_date=current_date,
                    timeline_data=timeline_data,
                    output_dir=output_dir,
                    max_concurrency=max_concurrency
                )
                day_files.append(day_file)
                print(f"Generated day: {current_date.isoformat()}")
            except Exception as e:
                print(f"Error generating day {current_date.isoformat()}: {e}")
            
            current_date += timedelta(days=1)
        
        return day_files
    
    async def _save_day_file(self, day_file: DayFile, output_dir: Path):
        """Save day file to disk."""
        # Create output directory structure
        year_dir = output_dir / f"year_{day_file.date[:4]}"
        month_dir = year_dir / f"month_{day_file.date[5:7]}"
        month_dir.mkdir(parents=True, exist_ok=True)
        
        # Save day file
        day_filename = f"day_{day_file.date}.json"
        day_path = month_dir / day_filename
        
        with open(day_path, 'w') as f:
            json.dump(day_file.model_dump(mode='json'), f, indent=2)
        
        # Update manifest
        await self._update_manifest(day_file, day_path, output_dir)
        
        print(f"Saved day file: {day_path}")
    
    async def _update_manifest(self, day_file: DayFile, day_path: Path, output_dir: Path):
        """Update the manifest file with day information."""
        manifest_path = output_dir / "manifest.jsonl"
        
        manifest_entry = {
            "monologue_id": day_file.monologue_id,
            "date": day_file.date,
            "file": str(day_path.relative_to(output_dir)),
            "minutes": len(day_file.hour_chunks) * 60,
            "provenance": day_file.provenance
        }
        
        with open(manifest_path, 'a') as f:
            f.write(json.dumps(manifest_entry) + '\n')
    
    async def generate_full_monologue(self, scenario: Scenario, 
                                    timeline_data: Dict[str, Any], 
                                    output_dir: Path,
                                    max_concurrency: int = 8) -> List[DayFile]:
        """Generate the complete 5-year monologue."""
        all_day_files = []
        
        for year in range(1, 6):
            print(f"Generating year {year}...")
            year_files = await self.generate_year(
                scenario=scenario,
                year=year,
                timeline_data=timeline_data,
                output_dir=output_dir,
                max_concurrency=max_concurrency
            )
            all_day_files.extend(year_files)
        
        return all_day_files
    
    def stitch_days(self, manifest_path: Path, output_path: Path, 
                   date_range: Optional[str] = None) -> None:
        """Stitch multiple days into a single file."""
        stitched_data = []
        
        with open(manifest_path, 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                
                # Apply date range filter if specified
                if date_range:
                    start_date, end_date = date_range.split('..')
                    if not (start_date <= entry['date'] <= end_date):
                        continue
                
                # Load day file
                day_file_path = manifest_path.parent / entry['file']
                with open(day_file_path, 'r') as day_f:
                    day_data = json.load(day_f)
                    stitched_data.append(day_data)
        
        # Save stitched file
        with open(output_path, 'w') as f:
            json.dump(stitched_data, f, indent=2)
        
        print(f"Stitched {len(stitched_data)} days to: {output_path}")
    
    def get_statistics(self, manifest_path: Path) -> Dict[str, Any]:
        """Get statistics about generated monologue."""
        total_minutes = 0
        total_days = 0
        date_range = None
        
        with open(manifest_path, 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                total_minutes += entry['minutes']
                total_days += 1
                
                if date_range is None:
                    date_range = [entry['date'], entry['date']]
                else:
                    date_range[1] = entry['date']
        
        return {
            "total_days": total_days,
            "total_minutes": total_minutes,
            "date_range": date_range,
            "estimated_tokens": total_minutes * 75  # Rough estimate
        } 