# models/recommender.py

from sklearn.feature_extraction.text import TfidfVectorizer             # for TF-IDF
from sklearn.metrics.pairwise import cosine_similarity                  # to compute similarity
from models.database import Database                                    # to fetch disease–symptom data :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
from models.symptom import SymptomModel                                 # for symptom cleaning

class RecommenderModel:
    """
    AI-driven disease recommendation using content-based filtering:
      • TF-IDF on weighted symptom “documents”
      • Cosine similarity for ranking
    """

    def __init__(self, db: Database, symptom_model: SymptomModel):
        self.db = db
        self.symptom_model = symptom_model
        self.vectorizer = None      # will hold our TF-IDF vectoriser
        self.tfidf_matrix = None    # will hold the TF-IDF matrix for all diseases
        self.disease_names = []     # parallel list of disease names
    
    def fit(self):
        """
        Build the TF-IDF index of all diseases.
        
        Steps:
          1. Fetch disease → space-joined symptom strings.
          2. Preprocess each string into tokens.
          3. Severity weighting: replicate each token by its severity level.
          4. Initialise TF-IDF with bigram support (1–2 grams).
          5. Fit & transform into a matrix.
        """
        try:
            # Load the disease–symptom matrix as a DataFrame
            df = self.db.get_disease_symptom_matrix() 

            # Keep the disease names in order
            self.disease_names = df["disease"].tolist()
            raw_docs        = df["symptom"].tolist()  # e.g. "fever cough fatigue …"

            cleaned_weighted_docs = []
            for raw in raw_docs:
                # Clean & normalize tokens
                tokens = raw.split()
                cleaned = self.symptom_model.preprocess_symptoms(tokens) # "fever cough fatigue"

                # Severity weighting: replicate tokens by severity
                weighted_tokens = []
                for token in cleaned.split():
                    # fetch severity from DB for each symptom
                    sev = self.db.get_severity_by_symptom(token)
                    try:
                        count = int(sev)
                    except (TypeError, ValueError):
                        count = 1  # default to 1 if missing/bad
                    # replicate the token 'count' times
                    weighted_tokens.extend([token] * count)
                
                # join back into a single “document” string
                cleaned_weighted_docs.append(" ".join(weighted_tokens))

            # Initialise TF-IDF to include unigrams & bigrams
            self.vectorizer = TfidfVectorizer(
                token_pattern=r"(?u)\b\w+\b",  
                lowercase=True,
                sublinear_tf=True,
                ngram_range=(1,2),   # allow bigrams like “joint pain”
                min_df=1
            )

            # Fit & transform into the TF-IDF matrix
            self.tfidf_matrix = self.vectorizer.fit_transform(cleaned_weighted_docs)

        except Exception as e:
            print(f"Error fitting recommender model: {e}")
    

    def recommend(self, selected_symptoms: list[str], top_n: int = 5) -> list[tuple[str, float]]:
        """
        Given user-selected symptoms, return top_n (disease, score) pairs.
        
        Also rescales scores so the top hit is 100%.
        """
        # Guard invalid input types (must be a list of strings)
        if not isinstance(selected_symptoms, list):
            raise TypeError("selected_symptoms must be a list of symptom strings")

        # Ensure fit() has been called
        if self.vectorizer is None or self.tfidf_matrix is None:
            raise RuntimeError("Call fit() before recommend()")

        # Preprocess user input
        user_doc   = self.symptom_model.preprocess_symptoms(selected_symptoms)
        user_vec   = self.vectorizer.transform([user_doc])

        # Compute cosine similarities
        scores     = cosine_similarity(user_vec, self.tfidf_matrix)[0]

        # Pick top_n indices
        ranked_idx = scores.argsort()[::-1][:top_n]
        top_scores = [scores[i] for i in ranked_idx]

        # Instead of normalizing, return raw cosine similarity scores
        recs = []
        for idx in ranked_idx:
            raw_score = float(scores[idx])
            recs.append((self.disease_names[idx], raw_score))
        return recs
