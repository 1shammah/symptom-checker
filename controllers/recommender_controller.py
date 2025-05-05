# controllers/recommender_controller.py

from typing import List, Tuple, Dict
from models.database import Database
from models.symptom import SymptomModel
from models.recommender import RecommenderModel

class RecommenderController:
    """
    Bridges the RecommenderModel with Streamlit.
    Trains on startup and exposes simple recommend methods.
    """

    def __init__(self, db: Database):
        self.db = db
        # SymptomModel handles cleaning/preprocessing of symptom tokens
        self.symptom_model = SymptomModel(db)
        # RecommenderModel applies TF-IDF, severity weighting, bigrams, and normalization
        self.model = RecommenderModel(db, self.symptom_model)

        # Build TF-IDF + weighted index once when the app starts
        self.model.fit()

    def recommend_diseases(
        self,
        selected_symptoms: List[str],
        top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Return a list of (disease, normalized_score) tuples.

        The `score` values are already normalized inside RecommenderModel.recommend()
        such that the highest score in the batch is 1.0 (100%).
        """
        try:
            # Call the model to get normalized similarity scores
            return self.model.recommend(selected_symptoms, top_n)
        except Exception as e:
            print(f"Error in recommend_diseases: {e}")
            return []

    def recommend_with_details(
        self,
        selected_symptoms: List[str],
        top_n: int = 5
    ) -> List[Dict[str, object]]:
        """
        Returns detailed recommendations with:
          - 'disease': the disease name
          - 'score': normalized similarity [0.0–1.0]
          - 'symptoms': list of associated symptoms
          - 'precautions': list of precautionary steps

        Note: The 'score' field here comes from the same normalized output
        of RecommenderModel.recommend(), so it reflects relative match percentages.
        """
        output = []
        try:
            # Get the normalized (disease, score) list
            raw = self.model.recommend(selected_symptoms, top_n)

            for disease, score in raw:
                # Fetch the full symptom list for this disease from the DB
                syms = self.db.get_symptoms_by_disease(disease)
                # Fetch precaution steps if any
                prec = self.db.get_precautions_by_disease(disease) or []

                output.append({
                    "disease": disease,
                    "score": score,
                    "symptoms": syms,
                    "precautions": prec
                })
        except Exception as e:
            print(f"Error in recommend_with_details: {e}")
        return output
