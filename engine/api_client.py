"""
API client for fetching drug data from OpenFDA
"""
import requests
from typing import Dict, List, Optional
import json


class OpenFDAClient:
    """Client for interacting with OpenFDA API"""
    
    BASE_URL = "https://api.fda.gov/drug"
    
    def __init__(self):
        self.session = requests.Session()
    
    def search_drug(self, drug_name: str) -> Optional[Dict]:
        """
        Search for a drug in OpenFDA database
        
        Args:
            drug_name: Name of the drug to search for
            
        Returns:
            Drug information dict or None if not found
        """
        try:
            # Search in drug labels
            url = f"{self.BASE_URL}/label.json"
            params = {
                'search': f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
                'limit': 1
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                return data['results'][0]
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching drug data for {drug_name}: {e}")
            return None
    
    def get_drug_interactions(self, drug_name: str) -> List[str]:
        """
        Get drug interaction information
        
        Args:
            drug_name: Name of the drug
            
        Returns:
            List of interaction warnings
        """
        drug_data = self.search_drug(drug_name)
        
        if not drug_data:
            return []
        
        interactions = []
        
        # Check various interaction fields
        if 'drug_interactions' in drug_data:
            interactions.extend(drug_data['drug_interactions'])
        
        if 'warnings' in drug_data:
            interactions.extend(drug_data['warnings'])
        
        return interactions
    
    def get_dosage_info(self, drug_name: str) -> Optional[str]:
        """
        Get dosage and administration information
        
        Args:
            drug_name: Name of the drug
            
        Returns:
            Dosage information string or None
        """
        drug_data = self.search_drug(drug_name)
        
        if not drug_data:
            return None
        
        # Try to extract dosage info
        if 'dosage_and_administration' in drug_data:
            return drug_data['dosage_and_administration'][0] if drug_data['dosage_and_administration'] else None
        
        return None
    
    def get_food_interactions(self, drug_name: str) -> Optional[Dict]:
        """
        Determine if drug should be taken with/without food
        
        Args:
            drug_name: Name of the drug
            
        Returns:
            Dict with food interaction info or None
        """
        drug_data = self.search_drug(drug_name)
        
        if not drug_data:
            return None
        
        food_info = {
            'with_food': False,
            'empty_stomach': False,
            'notes': []
        }
        
        # Search in dosage instructions
        dosage = self.get_dosage_info(drug_name)
        if dosage:
            dosage_lower = dosage.lower()
            if 'with food' in dosage_lower or 'with meal' in dosage_lower:
                food_info['with_food'] = True
                food_info['notes'].append("Should be taken with food")
            elif 'empty stomach' in dosage_lower or 'before eating' in dosage_lower:
                food_info['empty_stomach'] = True
                food_info['notes'].append("Should be taken on empty stomach")
        
        return food_info


# Simple mock data for demo purposes (when API is down or for testing)
MOCK_DRUG_DATA = {
    'lisinopril': {
        'name': 'Lisinopril',
        'generic_name': 'lisinopril',
        'brand_name': 'Prinivil, Zestril',
        'interactions': ['NSAIDs may reduce effectiveness', 'Potassium supplements may cause hyperkalemia'],
        'with_food': False,
        'empty_stomach': False,
        'frequency': 'once daily',
    },
    'metformin': {
        'name': 'Metformin',
        'generic_name': 'metformin',
        'brand_name': 'Glucophage',
        'interactions': ['Alcohol may increase lactic acidosis risk'],
        'with_food': True,
        'empty_stomach': False,
        'frequency': 'twice daily',
    },
    'levothyroxine': {
        'name': 'Levothyroxine',
        'generic_name': 'levothyroxine',
        'brand_name': 'Synthroid',
        'interactions': ['Take 4 hours apart from calcium, iron supplements'],
        'with_food': False,
        'empty_stomach': True,
        'frequency': 'once daily',
    }
}


def get_mock_drug_data(drug_name: str) -> Optional[Dict]:
    """Get mock drug data for demo purposes"""
    return MOCK_DRUG_DATA.get(drug_name.lower())