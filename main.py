#!/usr/bin/env python3
"""
Med Scheduler Demo
Demonstrates AI-powered medication rescheduling when doses are missed
"""

import os
from datetime import time, timedelta
from engine.models import Medication, Schedule, MissedDose, Constraint
from engine.rule_loader import RuleLoader
from engine.optimizer import AIOptimizer
from engine.api_client import get_mock_drug_data


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_schedule(schedule: Schedule):
    """Print the current medication schedule"""
    print("\nCurrent Medication Schedule:")
    print("-" * 70)
    for med in schedule.medications:
        times_str = ", ".join([t.strftime("%I:%M %p") for t in med.scheduled_times])
        print(f"  • {med.name} ({med.dosage})")
        print(f"    Frequency: {med.frequency}")
        print(f"    Scheduled: {times_str}")
        if med.with_food:
            print(f"    ⚠ Take with food")
        if med.empty_stomach:
            print(f"    ⚠ Take on empty stomach")
        print()


def print_constraints(constraints):
    """Print active constraints"""
    if not constraints:
        print("\nNo specific constraints loaded.")
        return
    
    print("\nActive Constraints:")
    print("-" * 70)
    for c in constraints:
        print(f"  • {c.description}")


def print_proposal(proposal):
    """Print the rescheduling proposal"""
    print("\n" + "=" * 70)
    print("  RESCHEDULING RECOMMENDATION")
    print("=" * 70)
    
    print(f"\nMissed Dose:")
    print(f"  Medication: {proposal.missed_dose.medication_name}")
    print(f"  Was scheduled: {proposal.missed_dose.scheduled_time.strftime('%I:%M %p')}")
    print(f"  Current time:  {proposal.missed_dose.current_time.strftime('%I:%M %p')}")
    
    print(f"\n✓ Recommended Action:")
    if proposal.new_time:
        print(f"  Take dose at: {proposal.new_time.strftime('%I:%M %p')}")
    else:
        print(f"  Skip this dose")
    
    print(f"\n💡 Reasoning:")
    print(f"  {proposal.reasoning}")
    
    if proposal.warnings:
        print(f"\n⚠ Warnings:")
        for warning in proposal.warnings:
            print(f"  • {warning}")
    
    print("\n" + "=" * 70)


def create_demo_schedule():
    """Create a sample medication schedule"""
    
    # Create medications
    levothyroxine = Medication(
        name="Levothyroxine",
        dosage="100mcg",
        frequency="once daily",
        scheduled_times=[time(6, 0)],  # 6:00 AM
        with_food=False,
        empty_stomach=True,
        min_interval=timedelta(hours=24),
        max_daily_doses=1
    )
    
    metformin = Medication(
        name="Metformin",
        dosage="500mg",
        frequency="twice daily",
        scheduled_times=[time(8, 0), time(20, 0)],  # 8:00 AM, 8:00 PM
        with_food=True,
        empty_stomach=False,
        min_interval=timedelta(hours=8),
        max_daily_doses=2
    )
    
    lisinopril = Medication(
        name="Lisinopril",
        dosage="10mg",
        frequency="once daily",
        scheduled_times=[time(8, 0)],  # 8:00 AM
        with_food=False,
        empty_stomach=False,
        min_interval=timedelta(hours=24),
        max_daily_doses=1
    )
    
    # Load constraints from YAML
    loader = RuleLoader()
    constraints = loader.load_constraints()
    
    # Create schedule
    schedule = Schedule(
        medications=[levothyroxine, metformin, lisinopril],
        constraints=constraints
    )
    
    return schedule


def demo_scenario_1(optimizer, schedule):
    """Demo: Missed morning levothyroxine by 2 hours"""
    print_header("SCENARIO 1: Missed Morning Levothyroxine")
    
    print("\nSituation:")
    print("  Patient normally takes Levothyroxine at 6:00 AM on empty stomach.")
    print("  It's now 8:00 AM and they just woke up.")
    print("  They're supposed to take Metformin with breakfast at 8:00 AM.")
    print("  What should they do?")
    
    missed = MissedDose(
        medication_name="Levothyroxine",
        scheduled_time=time(6, 0),
        current_time=time(8, 0),
        reason="Overslept"
    )
    
    proposal = optimizer.reschedule_missed_dose(missed, schedule)
    print_proposal(proposal)


def demo_scenario_2(optimizer, schedule):
    """Demo: Missed evening metformin by several hours"""
    print_header("SCENARIO 2: Missed Evening Metformin")
    
    print("\nSituation:")
    print("  Patient was supposed to take Metformin at 8:00 PM with dinner.")
    print("  It's now 11:30 PM and they just remembered.")
    print("  Should they take it now before bed, or skip it?")
    
    missed = MissedDose(
        medication_name="Metformin",
        scheduled_time=time(20, 0),
        current_time=time(23, 30),
        reason="Forgot after dinner"
    )
    
    proposal = optimizer.reschedule_missed_dose(missed, schedule)
    print_proposal(proposal)


def demo_scenario_3(optimizer, schedule):
    """Demo: Missed lisinopril by just 1 hour"""
    print_header("SCENARIO 3: Missed Morning Lisinopril by 1 Hour")
    
    print("\nSituation:")
    print("  Patient takes Lisinopril at 8:00 AM daily.")
    print("  It's now 9:00 AM - just one hour late.")
    print("  This is a simple case - should be safe to take now.")
    
    missed = MissedDose(
        medication_name="Lisinopril",
        scheduled_time=time(8, 0),
        current_time=time(9, 0),
        reason="Morning rush"
    )
    
    proposal = optimizer.reschedule_missed_dose(missed, schedule)
    print_proposal(proposal)


def main():
    """Run the demo"""
    
    print_header("Med Scheduler v0.1.0 - Demo")
    print("\nThis demo shows how AI helps reschedule medications when doses are missed.")
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"\n✓ Gemini API key found - using AI-powered rescheduling")
    else:
        print(f"\n⚠ No Gemini API key found - using rule-based fallback")
        print(f"  To use AI: export GEMINI_API_KEY='your-key-here'")
        print(f"  Get a key at: https://makersuite.google.com/app/apikey")
    
    # Create demo schedule
    schedule = create_demo_schedule()
    print_schedule(schedule)
    
    # Load and print constraints
    loader = RuleLoader()
    constraints = loader.load_constraints()
    print_constraints(constraints)
    
    # Initialize optimizer
    optimizer = AIOptimizer(api_key=api_key)
    
    # Run demo scenarios
    input("\n\nPress Enter to see Scenario 1...")
    demo_scenario_1(optimizer, schedule)
    
    input("\n\nPress Enter to see Scenario 2...")
    demo_scenario_2(optimizer, schedule)
    
    input("\n\nPress Enter to see Scenario 3...")
    demo_scenario_3(optimizer, schedule)
    
    print("\n\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print("\nNext Steps:")
    print("  1. Get a Gemini API key: https://makersuite.google.com/app/apikey")
    print("  2. Set it: export GEMINI_API_KEY='your-key'")
    print("  3. Run the demo again to see AI-powered recommendations")
    print("  4. Explore the code in engine/ to understand how it works")
    print("  5. Add your own medications and constraints in data/ and rules/")
    print("\n")


if __name__ == "__main__":
    main()