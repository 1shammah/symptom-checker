from dataclasses import dataclass
from typing import List, Optional
from models.database import Database

## test for removing white soace failed. two soaces were converetd to two underscores when I want one. issue in replace()
## have to use regex to remove all whitespace and replace with one underscore.
# import regular expressions as re

import re

# dataclass to represent a structured symptom object
@dataclass
class Symptom:
    name: str
    description:Optional[str] = None #optional because loaded via seprate query (get_description_by_symptom)
    severity: Optional[int] = None #optional because loaded via seprate query (get_severity_by_symptom)


# this model acts as an intermdiary layer betweeen the database and the controllers
# encapuslates logic for handling symptom-related operations in object-oriented way

class SymptomModel:

    def __init__(self, db: Database):
        """ 
        Initialise model with instance of the database class
        Args: 
            db (Database): instance of the database class for querying sumyptom data
        """

        self.db = db

    def get_all(self) -> List[Symptom]:
        """
        Retrieves all symptoms from db and constructs symptom object for each
        Returns :
            List[Symptom]: list of Symptom objects
        """

        try:
            rows = self.db.get_all_symptoms()
            symptoms = []
            for row in rows:
                name = row['symptom_name']
                description = row['description']
                severity = self.db.get_severity_by_symptom(name) #uses the get helper method because severity is in a different table
                symptoms.append(Symptom(name=name, description=description, severity=severity))
            return symptoms
        except Exception as e:
            print(f"Error fetching all symptoms: {e}")
            return []
            
    def get_by_name(self, name: str) -> Optional[Symptom]:
        """
        Fetch a single symptom by name
        
        Args:
            name (str): name of the symptom to fetch
        Returns:
            Symptom | None: Symptom object if found, None otherwise
        """

        try:
            #internally run SELECT description FROM symptoms WHERE symptom_name = ?
            description = self.db.get_description_by_symptom(name)

            #internally run SELECT severity_level FROM symptoms WHERE symptom_name = ?
            severity = self.db.get_severity_by_symptom(name)

            if description is not None and severity is not None: #could use isInstance but this is more readable
                return Symptom(name=name, description=description, severity=severity)
            return None
        except Exception as e:
            print(f"Error fetching symptom '{name}': {e}")
            return None
        
    def preprocess_symptoms(self, symptoms: List[str]) -> List[str]:
        """
        prepares a list of symptom names for the recommender ai
        inludes formatting for TF-IDF vectorization
        
        Args: 
            symptoms (List[str]): list of raw symptom strings to preprocess
            
        Returns:
            str: a clean, space-separated string of symptoms
        """

        try:
            cleaned_symptom_tokens = []

            # 1) Loop through every raw symptom input
            for raw_symptom in symptoms:
                
                # Only handle it if it's a string
                if isinstance(raw_symptom, str):
                    # Remove leading/trailing spaces and lowercase it
                    stripped = raw_symptom.strip().lower()

                    # If that results in an empty string, skip it entirely
                    if not stripped:
                        continue

                    # Collapse any run of whitespace (spaces, tabs, etc.)
                    # into a single underscore
                    collapsed = re.sub(r"\s+", "_", stripped)

                    # Collect the cleaned-up token
                    cleaned_symptom_tokens.append(collapsed)

            # 2) Remove duplicates; sorted() gives us alphabetical order
            unique_sorted_tokens = sorted(set(cleaned_symptom_tokens))

            # 3) Join them back into one string with single spaces
            result = " ".join(unique_sorted_tokens)

            return result

        except Exception as e:
            print(f"Error preprocessing symptoms: {e}")
            return ''