# Handles analytics operations for the admin dashboard.
# Bridges Streamlit UI and AnalyticsModel.
# The methods return a pandas DataFrame for easy display

import pandas as pd
from models.database import Database
from models.analytics import AnalyticsModel

class AnalyticsController:
    def __init__(self, db: Database):
        """
        Initialise controller with a Database instance.

        Args:
            db (Database): provides connection and helper methods.
        """
        self.model = AnalyticsModel(db)

    def disease_prevalence(self, top_n: int = 10) -> pd.DataFrame:
        """
        Retrieve top_n diseases by symptom count.

        Args:
            top_n (int): how many top diseases to fetch.

        Returns:
            pd.DataFrame with columns ["Disease", "Symptom Count"], or empty on error.
        """
        try:
            
            return self.model.get_most_common_diseases(top_n)
        
        except Exception as e:
            print(f"AnalyticsController.get_disease_prevalence error: {e}")
            return pd.DataFrame()
        
    def symptom_prevalence(self, top_n: int = 10) -> pd.DataFrame:
        """
        Retrieve top_n symptoms by disease count.

        Args:
            top_n (int): how many top symptoms to fetch.

        Returns:
            pd.DataFrame with columns ["Symptom", "Disease Count"], or empty on error.
        """
        try:
            
            return self.model.get_most_common_symptoms(top_n)
        
        except Exception as e:
            print(f"AnalyticsController.get_symptom_prevalence error: {e}")
            return pd.DataFrame()
        
    def symptom_frequency(self, top_n: int = 10) -> pd.DataFrame:
        """
        Retrieve top_n symptoms by frequency across diseases.

        Args:
            top_n (int): how many top symptoms to fetch.

        Returns:
            pd.DataFrame with columns ["Symptom", "Frequency"], or empty on error.
        """
        try:
            
            return self.model.get_symptom_frequency(top_n)
        
        except Exception as e:
            print(f"AnalyticsController.get_symptom_frequency error: {e}")
            return pd.DataFrame()
        
    
    def severity_distribution(self) -> pd.DataFrame:
        """
        Retrieve distribution of all symptom severity levels.

        Returns:
            pd.DataFrame with columns ["Severity Level", "Count"], or empty on error.
        """
        try:
            
            return self.model.get_symptom_severity_distribution()
        
        except Exception as error:
            print(f"AnalyticsController.get_severity_distribution error: {error}")
            return pd.DataFrame()
        
    
    def symptom_disease_matrix(self) -> pd.DataFrame:
        """
        Retrieve cross-tab matrix of diseases vs. symptoms.

        Returns:
            pd.DataFrame where rows are diseases, columns are symptoms,
            values are counts, or empty on error.
        """
        try:
            
            return self.model.get_symptom_disease_matrix()
        
        except Exception as error:
            print(f"AnalyticsController.get_symptom_disease_matrix error: {error}")
            return pd.DataFrame()

    def severity_mapping(self) -> pd.DataFrame:
        """
        Retrieve mapping of each symptom to its severity level.

        Returns:
            pd.DataFrame with columns ["Symptom", "Severity Level"], or empty on error.
        """
        try:
            
            return self.model.get_symptom_severity_mapping()
        
        except Exception as error:
            print(f"AnalyticsController.get_severity_mapping error: {error}")
            return pd.DataFrame()