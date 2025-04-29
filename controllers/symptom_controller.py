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
        self.model = SymptomModel(db)

    def list_symptoms(self) -> List[Symptom]:
        """
        Retrieve all symptoms.
        Returns:
            List[Symptom]: list of Symptom objects, empty on error.
        """
        try:
        
            return self.model.get_all()
        
        except Exception as error:
            print(f"SymptomController.list_symptoms error: {error}")
            return []

    def get_symptom(self, name: str) -> Optional[Symptom]:
        """
        Retrieve a single symptom by name.
        Args:
            name (str): symptom name to fetch.
        Returns:
            Symptom or None: Symptom object if found, else None.
        """
        try:
        
            return self.model.get_by_name(name)
        
        except Exception as error:
            print(f"SymptomController.get_symptom error: {error}")
            return None

    def preprocess_symptoms(self, raw_symptoms: List[str]) -> str:
        """
        Prepare a list of raw symptom names for AI recommendation.
        Args:
            raw_symptoms (List[str]): raw input strings.
        Returns:
            str: cleaned, space-joined symptom string, or empty on error.
        """
        try:
        
            return self.model.preprocess_symptoms(raw_symptoms)
        
        except Exception as error:
            print(f"SymptomController.preprocess_symptoms error: {error}")
            return ""
