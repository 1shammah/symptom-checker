#logic around symptom objects, filterring, scoring, matching etc
# fetch and structure symptom data from the database
# fetch by name or id
# combine symptom metadata (name, description, severity)
# search/filter symptoms
# preprocess for the recommender (lowercase,remove duplicates, join with spaces, etc)

from dataclasses import dataclass
from typing import List, Optional
from database import Database

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
            cleaned_symptoms = [
                s.strip().lower().replace(' ', '_') #replace spaces with underscores for TF-IDF vectorization
                for s in symptoms if s and isinstance(s, str)  #ensure no empty strings or non-string types are included. isinstance checks for str type
            ]
            return ' '.join(sorted(set(cleaned_symptoms))) #remove duplicates and sort the list

        except Exception as e:
            print(f"Error preprocessing symptoms: {e}")
            return ''