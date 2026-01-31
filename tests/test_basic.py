"""
Basic tests for the med scheduler
"""

import unittest
from datetime import time, timedelta
from engine.models import Medication, Schedule, MissedDose, Constraint
from engine.optimizer import AIOptimizer


class TestMedicationModel(unittest.TestCase):
    """Test the Medication data model"""
    
    def test_create_medication(self):
        """Test creating a basic medication"""
        med = Medication(
            name="Test Drug",
            dosage="100mg",
            frequency="once daily",
            scheduled_times=[time(8, 0)]
        )
        
        self.assertEqual(med.name, "Test Drug")
        self.assertEqual(med.dosage, "100mg")
        self.assertEqual(len(med.scheduled_times), 1)
    
    def test_medication_with_constraints(self):
        """Test medication with food constraints"""
        med = Medication(
            name="Test Drug",
            dosage="100mg",
            frequency="once daily",
            scheduled_times=[time(8, 0)],
            with_food=True,
            empty_stomach=False
        )
        
        self.assertTrue(med.with_food)
        self.assertFalse(med.empty_stomach)


class TestSchedule(unittest.TestCase):
    """Test the Schedule functionality"""
    
    def setUp(self):
        """Set up test medications and schedule"""
        self.med1 = Medication(
            name="Drug A",
            dosage="50mg",
            frequency="once daily",
            scheduled_times=[time(8, 0)]
        )
        
        self.med2 = Medication(
            name="Drug B",
            dosage="100mg",
            frequency="twice daily",
            scheduled_times=[time(8, 0), time(20, 0)]
        )
        
        self.schedule = Schedule(
            medications=[self.med1, self.med2],
            constraints=[]
        )
    
    def test_get_medication(self):
        """Test finding a medication by name"""
        found = self.schedule.get_medication("Drug A")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Drug A")
    
    def test_get_medication_not_found(self):
        """Test that non-existent medication returns None"""
        found = self.schedule.get_medication("Drug C")
        self.assertIsNone(found)


class TestMissedDose(unittest.TestCase):
    """Test missed dose handling"""
    
    def test_create_missed_dose(self):
        """Test creating a missed dose event"""
        missed = MissedDose(
            medication_name="Test Drug",
            scheduled_time=time(8, 0),
            current_time=time(10, 0),
            reason="Overslept"
        )
        
        self.assertEqual(missed.medication_name, "Test Drug")
        self.assertEqual(missed.scheduled_time, time(8, 0))
        self.assertEqual(missed.current_time, time(10, 0))


class TestOptimizer(unittest.TestCase):
    """Test the AI optimizer (rule-based fallback)"""
    
    def setUp(self):
        """Set up test schedule and optimizer"""
        self.med = Medication(
            name="Test Drug",
            dosage="100mg",
            frequency="once daily",
            scheduled_times=[time(8, 0)],
            min_interval=timedelta(hours=24)
        )
        
        self.schedule = Schedule(
            medications=[self.med],
            constraints=[]
        )
        
        # Create optimizer without API key (uses rule-based)
        self.optimizer = AIOptimizer(api_key=None)
    
    def test_reschedule_within_window(self):
        """Test rescheduling when within acceptable window"""
        missed = MissedDose(
            medication_name="Test Drug",
            scheduled_time=time(8, 0),
            current_time=time(9, 0)  # 1 hour late
        )
        
        proposal = self.optimizer.reschedule_missed_dose(missed, self.schedule)
        
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.missed_dose, missed)
        self.assertIsNotNone(proposal.reasoning)
    
    def test_reschedule_very_late(self):
        """Test rescheduling when very late"""
        missed = MissedDose(
            medication_name="Test Drug",
            scheduled_time=time(8, 0),
            current_time=time(18, 0)  # 10 hours late
        )
        
        proposal = self.optimizer.reschedule_missed_dose(missed, self.schedule)
        
        self.assertIsNotNone(proposal)
        self.assertTrue(len(proposal.warnings) > 0)


if __name__ == '__main__':
    unittest.main()