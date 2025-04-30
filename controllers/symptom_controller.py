# Handles symptom-related operations between the Streamlit UI and SymptomModel
# Fetches lists of symptoms, individual symptom details, and preprocessing for AI input
# Separates business logic from views

from typing import List, Optional
from models.database import Database
from models.symptom import SymptomModel, Symptom

class SymptomController:
    def __init__(self, db: Database):
        """
        Initialise with a Database instance.
        Args:
            db (Database): provides helper methods and connection.
        """
        self.db = db
        self.model = SymptomModel(db)

    def list_all_symptoms(self) -> List[Symptom]:
        """
        Retrieve all symptoms.
        Returns: List[Symptom]. a list of Symptom objects, empty on error.
        """
        try:
        
            return self.model.get_all()
        
        except Exception as e:
            print(f"SymptomController.list_symptoms error: {e}")
            return []

    def get_symptoms_for_disease(self, disease_name: str) -> List[str]:
        """
        Retrieve names of all symptoms linked to a disease.
        Returns: List[str]: List of symptom names, empty list on error.
        """
        try:
            
            return self.db.get_symptoms_by_disease(disease_name)
        
        except Exception as e:
            print(f"SymptomController.get_symptoms_for_disease error: {e}")
            return []

    def get_diseases_for_symptom(self, symptom_name: str) -> List[str]:
        """
        Retrieve names of all diseases linked to a symptom.
        Returns: List[str]: List of disease names, empty list on error.
        """
        try:
            
            return self.db.get_diseases_by_symptom(symptom_name)
        
        except Exception as e:
            print(f"SymptomController.get_diseases_for_symptom error: {e}")
            return []
        
    def get_precautions(self, disease_name: str) -> Optional[List[str]]:
        """
        Retrieve precaution steps for a disease.
        Returns: List[str]: List of precautions, None on error.
        """
        try:
        
            return self.db.get_precautions_by_disease(disease_name)
        
        except Exception as e:
            print(f"SymptomController.get_precautions error: {e}")
            return None
        
    def get_description(self, symptom_name:str) -> Optional[str]:
        """
        Retrieve description of a specific symptom.
        Returns: str: Description of the symptom, None on error.
        """
        try:
        
            return self.db.get_description_by_symptom(symptom_name)
        
        except Exception as e:
            print(f"SymptomController.get_description error: {e}")
            return None

    def get_severity(self, symptom_name:str) -> Optional[str]:
        """
        Retrieve severity of a specific symptom.
        Returns: str: Severity of the symptom, None on error.
        """
        try:
        
            return self.db.get_severity_by_symptom(symptom_name)
        
        except Exception as e:
            print(f"SymptomController.get_severity error: {e}")
            return None