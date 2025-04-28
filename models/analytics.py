# Your proposal mentions:
# 
# Symptom frequency
# Disease prevalence
# Severity distribution
# Correlations
# 
# These don’t live in the DB, they live in Pandas.
# 
# So AnalyticsModel is where you:
# 
# Load data (from DB or CSV)
# Run aggregations
# Return plots, stats, summaries
# 
# Use this model only for the Analytics View/Page
# 
# Functions might include:
# 
# get_symptom_frequency()
# get_most_common_diseases()
# get_average_severity_per_symptom()
# get_symptom_correlation_matrix() (Optional with SciPy)

# ANALYTICS MODEL
# ------------------------------------------------------------
# This model provides static analytics and statistical insights
# based on preloaded datasets only. It avoids tracking real-time
# user activity to maintain privacy and comply with ethical
# research constraints (e.g. Worktribe clearance not required).

# Current features include:
# - Symptom frequency analysis across diseases
# - Symptom severity distribution (from symptom_severity.csv)
# - Symptom co-occurrence patterns (e.g., common pairs)
# - Disease coverage insights (e.g., number of symptoms or precautions per disease)

# The model uses preprocessed data already stored in the SQLite DB
# via `database.py` and does NOT rely on user interaction logs.

# ------------------------------------------------------------
# FUTURE EXTENSIONS (if user history is later enabled):
# - Track most commonly selected symptoms in symptom checks
# - Identify most frequently predicted diseases
# - Analyse user roles, login frequency, and interaction volume
# - Timeline-based analytics (e.g., symptom trends over time)

# These features would rely on the `symptom_checks` table, which
# is already in place but currently unused.
# ------------------------------------------------------------

#logic for analytical summaries and insights
# uses helper methods in db for counting users, symptoms and disesases
# provides data for admin dashnoards or reporting 
# can be extended with visualiasation, charts or advanced insights


# logic for static analytics based on preloaded datasets
# operates on diseases, symptoms, severity and relationships
# does not use user symptom history due to ethical restrictions
# supports insights like common dieases, symptoms and severity distributions
# intended for use by admins in dashboard visualiastations
# uses pandas for data manipulation and analysis

import pandas as pd
from models.database import Database

class AnalyticsModel:

    def __init__(self, db: Database):
        """
        Initialise with db instance

        args:
            db (Database): Database instance for data access
        """
        self.db = db

    def get_most_common_diseases(self, top_n=10):
        """
        Returns the most common diseases in the database.

        Args:
            top_n (int): Number of top diseases to return

        Returns:
            pd.DataFrame: Disease and count o flinked symptoms
        """

        try:
            self.db.cur.execute("""
                SELECT diseases.disease_name, COUNT(symptom_disease.symptom_id) AS symptom_count
                FROM diseases
                JOIN symptom_disease ON diseases.id = symptom_disease.disease_id
                GROUP BY diseases.disease_name
                ORDER BY symptom_count DESC
                LIMIT ?;
            """, (top_n,))
            rows = self.db.cur.fetchall()
            return pd.DataFrame(rows, columns=["Disease", "Symptom Count"])
        except Exception as e:
            print(f"Error fetching common diseases: {e}")
            return pd.DataFrame()
        
    def get_most_common_symptoms(self, top_n=10):
        """
        Returns the most frequently associated symptoms across all diseases
        
        Args:
            top_n (int): Number of top symptoms to return.

        Returns:
            pd.DataFrame: Symptom and count of associated diseases
        """

        try:
            self.db.cur.execute("""
                SELECT symptoms.symptom_name, COUNT(symptom_disease.disease_id) AS disease_count
                FROM symptoms
                JOIN symptom_disease ON symptoms.id = symptom_disease.symptom_id
                GROUP BY symptoms.symptom_name
                ORDER BY disease_count DESC
                LIMIT ?;
            """, (top_n,))
            rows = self.db.cur.fetchall()
            return pd.DataFrame(rows, columns=["Symptom", "Disease Count"])
        except Exception as e:
            print(f"Error fetching common symptoms: {e}")
            return pd.DataFrame()
        

    def get_symptom_frequency(self, top_n=10):
        """
        Returns the frequency of each symptom based on how many diseases it's linked to.

        Args:
            top_n (int): Number of top symptoms to return.

        Returns:
            pd.DataFrame: Symptom and number of associated diseases.
        """

        try:
            self.db.cur.execute("""
                SELECT symptoms.symptom_name, COUNT(symptom_disease.disease_id) AS frequency
                FROM symptoms
                JOIN symptom_disease ON symptoms.id = symptom_disease.symptom_id
                GROUP BY symptoms.symptom_name
                ORDER BY frequency DESC
                LIMIT ?;
            """, (top_n,))
            rows = self.db.cur.fetchall()
            return pd.DataFrame(rows, columns=["Symptom", "Frequency"])
        except Exception as e:
            print(f"Error fetching symptom frequency: {e}")
            return pd.DataFrame()

        
    def get_symptom_severity_distribution(self):
        """
        Returns the distribution of symptom severity levels
        
        Returns:
            pd.DataFrame: Severity level and count of symptoms
        """

        try:
            self.db.cur.execute("""
                SELECT severity_level, COUNT(*) AS count
                FROM symptom_severity
                GROUP BY severity_level
                ORDER BY severity_level
            """)
            rows = self.db.cur.fetchall()
            return pd.DataFrame(rows, columns=["Severity Level", "Count"])
        except Exception as e:
            print(f"Error fetching severity distribution: {e}")
            return pd.DataFrame()
                                
    def get_symptom_disease_matrix(self):
        """
        Returns a matrix showing how many symptoms are linked to each disease
        
        Returns:
            pd.DataFrame: Cross-tab matrix of diseases and symptoms
        """

        try:
            self.db.cur.execute("""
                SELECT diseases.disease_name, symptoms.symptom_name
                FROM symptom_disease
                JOIN diseases ON symptom_disease.disease_id = diseases.id
                JOIN symptoms ON symptom_disease.symptom_id = symptoms.id
            """)
            rows = self.db.cur.fetchall()
            df = pd.DataFrame(rows, columns=["Disease", "Symptom"])
            matrix = pd.crosstab(df["Disease"], df["Symptom"])
            return matrix
        except Exception as e:
            print(f"Error generating symptom-disease matrix: {e}")
            return pd.DataFrame()
        
    def get_symptom_severity_mapping(self):
        """
        Returns all symptoms with their corresponding severity levels.

        Returns:
            pd.DataFrame: Symptom and severity.
        """
            
        try:
            self.db.cur.execute("""
                SELECT s.symptom_name, ss.severity_level
                FROM symptoms AS s
                JOIN symptom_severity AS ss
                ON s.id = ss.symptom_id
                
                -- Cast text to integer so ORDER BY works numerically
                
                ORDER BY CAST(ss.severity_level AS INTEGER) DESC
            """)
            rows = self.db.cur.fetchall()
            return pd.DataFrame(rows, columns=["Symptom", "Severity Level"])
        except Exception as e:
            print(f"Error fetching symptom severity mapping: {e}")
            return pd.DataFrame()
