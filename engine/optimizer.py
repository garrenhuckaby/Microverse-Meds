"""
AI-powered optimizer for rescheduling medications
Uses Google Gemini API to reason through constraints
"""
import os
from typing import Optional
from datetime import time, datetime, timedelta
from .models import Schedule, MissedDose, RescheduleProposal

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Install with: pip install google-generativeai")


class AIOptimizer:
    """Uses AI to optimize medication schedules when doses are missed"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI optimizer
        
        Args:
            api_key: Gemini API key (or set GEMINI_API_KEY env variable)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if GEMINI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        elif not GEMINI_AVAILABLE:
            print("Gemini API not available - using rule-based fallback")
        elif not self.api_key:
            print("No API key provided - using rule-based fallback")
    
    def reschedule_missed_dose(
        self, 
        missed_dose: MissedDose, 
        schedule: Schedule
    ) -> RescheduleProposal:
        """
        Generate a rescheduling proposal for a missed dose
        
        Args:
            missed_dose: The missed dose event
            schedule: The complete medication schedule
            
        Returns:
            RescheduleProposal with new time and reasoning
        """
        if self.model and self.api_key:
            return self._ai_reschedule(missed_dose, schedule)
        else:
            return self._rule_based_reschedule(missed_dose, schedule)
    
    def _ai_reschedule(
        self, 
        missed_dose: MissedDose, 
        schedule: Schedule
    ) -> RescheduleProposal:
        """Use Gemini AI to generate rescheduling proposal"""
        
        # Get the medication
        med = schedule.get_medication(missed_dose.medication_name)
        if not med:
            return self._create_error_proposal(missed_dose, "Medication not found")
        
        # Get relevant constraints
        constraints = schedule.get_constraints_for_drug(missed_dose.medication_name)
        
        # Build the prompt
        prompt = self._build_prompt(missed_dose, med, schedule, constraints)
        
        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)
            
            # Parse the response
            return self._parse_ai_response(response.text, missed_dose)
            
        except Exception as e:
            print(f"AI API error: {e}")
            return self._rule_based_reschedule(missed_dose, schedule)
    
    def _build_prompt(self, missed_dose, med, schedule, constraints):
        """Build the prompt for the AI"""
        
        constraint_text = "\n".join([
            f"- {c.description}" for c in constraints
        ]) if constraints else "No specific constraints"
        
        other_meds = [m for m in schedule.medications if m.name != med.name]
        other_meds_text = "\n".join([
            f"- {m.name}: scheduled at {', '.join([t.strftime('%H:%M') for t in m.scheduled_times])}"
            for m in other_meds
        ]) if other_meds else "No other medications"
        
        prompt = f"""You are a medication scheduling assistant. A patient has missed a dose and needs help rescheduling.

MISSED DOSE:
- Medication: {missed_dose.medication_name}
- Was scheduled for: {missed_dose.scheduled_time.strftime('%H:%M')}
- Current time: {missed_dose.current_time.strftime('%H:%M')}
- Time elapsed: {self._time_difference(missed_dose.scheduled_time, missed_dose.current_time)}

MEDICATION DETAILS:
- Dosage: {med.dosage}
- Frequency: {med.frequency}
- With food: {med.with_food}
- Empty stomach: {med.empty_stomach}
- Minimum interval between doses: {med.min_interval}
- Max daily doses: {med.max_daily_doses}

CONSTRAINTS:
{constraint_text}

OTHER MEDICATIONS TODAY:
{other_meds_text}

Please recommend:
1. The best time to take the missed dose now
2. Whether any other scheduled doses need adjustment
3. Any warnings or precautions

Format your response as:
RECOMMENDED_TIME: HH:MM
REASONING: [your explanation]
WARNINGS: [any warnings, or "None"]
"""
        return prompt
    
    def _parse_ai_response(self, response_text: str, missed_dose: MissedDose) -> RescheduleProposal:
        """Parse the AI's response into a RescheduleProposal"""
        
        lines = response_text.strip().split('\n')
        new_time_str = None
        reasoning = ""
        warnings = []
        
        for line in lines:
            if line.startswith('RECOMMENDED_TIME:'):
                time_str = line.split(':', 1)[1].strip()
                # Parse HH:MM
                try:
                    hour, minute = map(int, time_str.split(':'))
                    new_time_str = time(hour, minute)
                except:
                    pass
            elif line.startswith('REASONING:'):
                reasoning = line.split(':', 1)[1].strip()
            elif line.startswith('WARNINGS:'):
                warning_text = line.split(':', 1)[1].strip()
                if warning_text.lower() != 'none':
                    warnings.append(warning_text)
        
        # If parsing failed, use current time
        if not new_time_str:
            new_time_str = missed_dose.current_time
            reasoning = "Take as soon as possible. " + reasoning
        
        return RescheduleProposal(
            missed_dose=missed_dose,
            new_time=new_time_str,
            reasoning=reasoning if reasoning else response_text[:200],
            warnings=warnings
        )
    
    def _rule_based_reschedule(
        self, 
        missed_dose: MissedDose, 
        schedule: Schedule
    ) -> RescheduleProposal:
        """Simple rule-based rescheduling as fallback"""
        
        med = schedule.get_medication(missed_dose.medication_name)
        if not med:
            return self._create_error_proposal(missed_dose, "Medication not found")
        
        # Simple logic: take now if within reasonable window
        time_diff = self._time_difference(missed_dose.scheduled_time, missed_dose.current_time)
        
        warnings = []
        reasoning = ""
        
        if time_diff.total_seconds() < 7200:  # Within 2 hours
            new_time = missed_dose.current_time
            reasoning = "Take the dose now. You're within the acceptable window."
        elif time_diff.total_seconds() < 14400:  # Within 4 hours
            new_time = missed_dose.current_time
            reasoning = "Take the dose now, but monitor for side effects."
            warnings.append("Dose is significantly delayed - contact provider if concerned")
        else:
            # Skip this dose
            new_time = None
            reasoning = "Skip this dose and take the next scheduled dose."
            warnings.append("More than 4 hours late - safer to skip and resume normal schedule")
        
        return RescheduleProposal(
            missed_dose=missed_dose,
            new_time=new_time or missed_dose.scheduled_time,
            reasoning=reasoning,
            warnings=warnings
        )
    
    @staticmethod
    def _time_difference(time1: time, time2: time) -> timedelta:
        """Calculate difference between two times"""
        # Convert to datetime for easier math
        today = datetime.today().date()
        dt1 = datetime.combine(today, time1)
        dt2 = datetime.combine(today, time2)
        return dt2 - dt1
    
    @staticmethod
    def _create_error_proposal(missed_dose: MissedDose, error: str) -> RescheduleProposal:
        """Create an error proposal"""
        return RescheduleProposal(
            missed_dose=missed_dose,
            new_time=missed_dose.current_time,
            reasoning=f"Error: {error}",
            warnings=["Unable to generate optimal schedule"]
        )