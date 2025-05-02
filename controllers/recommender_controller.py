# Handles AI-based disease recommendation
# Separates TF-IDF + cosine similarity logic from streamlit
# Uses RecommenderMOdel for ranking disease symptom

from typing import List, Tuple, Dict
from models.database import Database
from models.symptom import SymptomModel
from models.recommender import RecommenderModel

class RecommenderController:
    def __init__(self, db: Database):
        """
        Initialise with a Database instance
        Train the TF-IDF vectoriseron startup

        Args:
            db (Database): provides data and helper methods  
        """

        self.db = db
        self.symptom_model = SymptomModel(db)
        self.model = RecommenderModel(db, self.symptom_model)
        
        # Build the TF-IDF index once when app starts
        self.model.fit()

    def recommend_diseases(
            self,
            selected_symptoms: List[str],
            top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Return the top_n (disease, score) tuples for the selected symptoms

        Args:
            selected_symptoms (List[str]): list of symptoms selected by the user
            top_n (int): number of top recommendations to return

        Returns:
            List of tuples (disease_name, similarity_score) 
            Empty list on error
        """
        try:
            
            return self.model.recommend(selected_symptoms, top_n)
        
        except Exception as e:
            print(f"RecommenderController.recommend_diseases error: {e}")
            return []
        
    def recommend_with_details(
            self,
            selected_symptoms: List[str],
            top_n: int = 5
    ) -> List[Dict[str, str]]:
        """
        Return recommendations along with full context:
        - disease name 
        - similarity score
        - list of associated symptoms
        - list of precaution steps

        Args:
            selected_symptoms: list of symptoms selected by the user
            top_n: number of top recommendations to return

        Returns:
            List of dictionaries with keys:
                'disease': str,
                'score': float,
                'symptoms': List[str],
                'precautions': List[str] or None
            Empty list on error
        """

        try:
            raw_recommendations = self.model.recommend(selected_symptoms, top_n)
            detailed_recommendations: List[Dict[str, object]] = []
            for disease_name, score in raw_recommendations:
                symptom_list = self.db.get_symptoms_by_disease(disease_name)
                precaution_list = self.db.get_precautions_by_disease(disease_name)
                detailed_recommendations.append({
                    'disease': disease_name,
                    'score': score,
                    'symptoms': symptom_list,
                    'precautions': precaution_list
                })
            return detailed_recommendations
        except Exception as e:
            print(f"RecommenderController.recommend_with_details error: {e}")
            return []