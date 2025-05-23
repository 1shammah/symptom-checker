
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
