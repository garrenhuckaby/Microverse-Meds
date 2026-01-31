"""
Data models for the medication scheduler
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import time, timedelta


@dataclass
class Medication:
    """Represents a single medication with scheduling requirements"""
    name: str
    dosage: str
    frequency: str  # "daily", "twice daily", "every 8 hours", etc.
    scheduled_times: List[time]  # e.g., [time(8,0), time(20,0)]
    
    # Constraints
    with_food: Optional[bool] = None
    empty_stomach: Optional[bool] = None
    min_interval: Optional[timedelta] = None  # minimum time between doses
    max_daily_doses: int = 1
    
    # Interactions (list of drug names this interacts with)
    interacts_with: List[str] = field(default_factory=list)
    interaction_gap: Optional[timedelta] = None  # required gap if interactions exist
    
    def __repr__(self):
        return f"Medication({self.name}, {self.dosage}, {self.frequency})"


@dataclass
class Constraint:
    """Represents a scheduling constraint between medications"""
    type: str  # "time_gap", "food_requirement", "drug_interaction"
    drug_a: str
    drug_b: Optional[str] = None
    min_gap: Optional[timedelta] = None
    description: str = ""
    
    def __repr__(self):
        if self.drug_b:
            return f"Constraint({self.drug_a} <-> {self.drug_b}: {self.description})"
        return f"Constraint({self.drug_a}: {self.description})"


@dataclass
class Schedule:
    """A complete medication schedule with all constraints"""
    medications: List[Medication]
    constraints: List[Constraint]
    
    def get_medication(self, name: str) -> Optional[Medication]:
        """Find a medication by name"""
        for med in self.medications:
            if med.name.lower() == name.lower():
                return med
        return None
    
    def get_constraints_for_drug(self, drug_name: str) -> List[Constraint]:
        """Get all constraints involving a specific drug"""
        return [c for c in self.constraints 
                if c.drug_a.lower() == drug_name.lower() or 
                (c.drug_b and c.drug_b.lower() == drug_name.lower())]


@dataclass
class MissedDose:
    """Represents a missed dose event that needs rescheduling"""
    medication_name: str
    scheduled_time: time
    current_time: time
    reason: str = "Missed dose"
    
    def __repr__(self):
        return f"MissedDose({self.medication_name} at {self.scheduled_time}, now {self.current_time})"


@dataclass
class RescheduleProposal:
    """AI-generated proposal for rescheduling after a missed dose"""
    missed_dose: MissedDose
    new_time: time
    reasoning: str
    affected_medications: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def __repr__(self):
        return f"RescheduleProposal({self.missed_dose.medication_name} -> {self.new_time})"