"""
Loads and parses constraint rules from YAML files
"""
import yaml
from pathlib import Path
from typing import List, Dict
from datetime import timedelta
from .models import Constraint


class RuleLoader:
    """Loads scheduling rules and constraints from YAML files"""
    
    def __init__(self, rules_dir: str = "rules"):
        self.rules_dir = Path(rules_dir)
    
    def load_constraints(self) -> List[Constraint]:
        """
        Load all constraints from constraints.yaml
        
        Returns:
            List of Constraint objects
        """
        constraints_file = self.rules_dir / "constraints.yaml"
        
        if not constraints_file.exists():
            print(f"Warning: {constraints_file} not found")
            return []
        
        with open(constraints_file, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data or 'constraints' not in data:
            return []
        
        constraints = []
        for item in data['constraints']:
            constraint = Constraint(
                type=item.get('type', 'unknown'),
                drug_a=item.get('drug_a', ''),
                drug_b=item.get('drug_b'),
                min_gap=self._parse_timedelta(item.get('min_gap')),
                description=item.get('description', '')
            )
            constraints.append(constraint)
        
        return constraints
    
    def load_tags(self) -> Dict:
        """
        Load medication tags from tags.yaml
        
        Returns:
            Dictionary of tags
        """
        tags_file = self.rules_dir / "tags.yaml"
        
        if not tags_file.exists():
            print(f"Warning: {tags_file} not found")
            return {}
        
        with open(tags_file, 'r') as f:
            data = yaml.safe_load(f)
        
        return data if data else {}
    
    def load_sources(self) -> Dict:
        """
        Load API source configuration from sources.yaml
        
        Returns:
            Dictionary of API sources
        """
        sources_file = self.rules_dir / "sources.yaml"
        
        if not sources_file.exists():
            print(f"Warning: {sources_file} not found")
            return {}
        
        with open(sources_file, 'r') as f:
            data = yaml.safe_load(f)
        
        return data if data else {}
    
    @staticmethod
    def _parse_timedelta(time_str: str) -> timedelta:
        """
        Parse a time string like '2h', '30m', '1d' into timedelta
        
        Args:
            time_str: Time string (e.g., "2h", "30m", "1d")
            
        Returns:
            timedelta object
        """
        if not time_str:
            return None
        
        time_str = time_str.strip().lower()
        
        if time_str.endswith('h'):
            hours = int(time_str[:-1])
            return timedelta(hours=hours)
        elif time_str.endswith('m'):
            minutes = int(time_str[:-1])
            return timedelta(minutes=minutes)
        elif time_str.endswith('d'):
            days = int(time_str[:-1])
            return timedelta(days=days)
        else:
            # Assume hours if no unit
            return timedelta(hours=int(time_str))