from sklearn.feature_extraction.text import TfidfVectorizer             # for converting text to TF-IDF vectors
from sklearn.metrics.pairwise import cosine_similarity                  # for calculating similarity between vectors
from models.database import Database                                    # db helper with get_disesase_symptom_matrix()
from models.symptom import SymptomModel                                 # for preprocess_symptoms() method

class RecommenderModel:
    """
    Provides AI-driven disease recommendation
    Uses TF-IDF vectorisation of disease-symptom text
    and cosine similarity to compare with user-selected symptoms
    """

    def __init__(self, db: Database, symptom_model: SymptomModel):
        """
        Initialise with database helper and symptom model
        
        Args:
            db (Database): access to disease-symptom data via helper methods
            symptom_model (SymptomModel): handles symptom cleaning and preprocessing
        """
        self.db = db                                                    # store database instance
        self.symptom_model = symptom_model                              # store symptom preprocessing model
        self.vectorizer = None                                          # holds TF-IDF vectoriser          
        self.tfidf_matrix = None                                        # holds TF-IDF matrix of all diseases   
        self.disease_names = []                                         # holds ordered list of disease name

    def fit(self):
        """
        Train the TF-IDF vectoriser on all diseases

        Must be called once when the app starts, before any calls to recommend()
        """

        try:
            # Fetch each disease with its combined symptom string from the disease-symptom matrix. DataFrame of { disease: cleaned_symptom_string }
            matrix_dataframe = self.db.get_disease_symptom_matrix()

            # extract disease names in same order as the symptom documents
            self.disease_names = matrix_dataframe["disease"].tolist()

            # Raw symptom strings (space-joined) for each disease
            raw_documents = matrix_dataframe["symptom"].tolist()    

            # Clean each document using the same preprocessing as user input
            cleaned_documents = []
            
            for raw in raw_documents:
                # split into tokens then preprocess to a standard string
                tokens = raw.split()
                cleaned = self.symptom_model.preprocess_symptoms(tokens)
                cleaned_documents.append(cleaned)

            # Initialise the TF-IDF vectoriser with basic settings
            self.vectorizer = TfidfVectorizer(
                token_pattern=r"(?u)\b\w+\b",  # regex to match single words (alphanumeric)
                lowercase=True,                # ensure lowercase
                sublinear_tf=True,             # use sublinear term frequency scaling
                min_df=1,                      # include terms appearing in at least 1 document
            )

            # Fit vectoriser to cleaned documents and transform to TF-IDF matrix
            self.tfidf_matrix = self.vectorizer.fit_transform(cleaned_documents)

        except Exception as e:
            print(f"Error fitting recommender model: {e}")


    def recommend(self, selected_symptoms: list[str], top_n: int = 5) -> list[tuple[str, float]]:
        """
        Recommend top_n diseases for a list of user-selected symptoms.

        Args:
            selected_symptoms (list[str]): raw symptom names from the user interface
            top_n (int): number of recommendations to return

        Returns:
            list of (disease_name, similarity_score)
        """

         # 1) Guard against mis-typed inputs
        if not isinstance(selected_symptoms, list):
            raise TypeError("selected_symptoms must be a list of symptom strings")
        
        # ensure tf-idf vectoriser and matrix exist before recommending
        if self.vectorizer is None or self.tfidf_matrix is None:
            raise RuntimeError("RecommenderModel.fit() must be called before recommend()")

        try:
            # preprocess user symptoms into the same normalised format
            user_document = self.symptom_model.preprocess_symptoms(selected_symptoms)

            # vectorise the user document into TF-IDF space
            user_vector = self.vectorizer.transform([user_document])

            # calculate cosine similarity between user vector and all disease vectors
            similarity_scores =  cosine_similarity(user_vector, self.tfidf_matrix)[0]

            # Get indices of the top_n most similar diseases (highest similarity scores)
            ranked_indices = similarity_scores.argsort()[::-1][:top_n]

            # Map indices back to disease names and pair with scores
            recommendations = []
            for index in ranked_indices:
                disease = self.disease_names[index]                     # get disease name from the index
                score = float(similarity_scores[index])                 # get float similarity score
                recommendations.append((disease, score))                # append to the list (tuple of disease and score)
        
            return recommendations
        
        except Exception as e:
            print(f"Error recommending diseases: {e}")
            return []