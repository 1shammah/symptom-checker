import unittest
from unittest.mock import MagicMock
import pandas as pd
from controllers.analytics_controller import AnalyticsController
from pandas import DataFrame

class TestAnalyticsController(unittest.TestCase):
    def setUp(self):
        # Fake database not used directly by controller
        self.fake_db = MagicMock()

        # Create the controller
        self.controller = AnalyticsController(self.fake_db)

        # Stub out its model
        self.fake_model = MagicMock()
        self.controller.model = self.fake_model

        # Sample dataframe fixture
        self.sample_df = pd.DataFrame({
            "Symptom": ["A", "B"],
            "Frequency": [2, 3]
        })

    ############# disease_prevalence #############

    def test_disease_prevalence_success(self):
        """ Should call model.get_most_common_diseases with default top_n=10 """

        self.fake_model.get_most_common_diseases.return_value = self.sample_df

        result = self.controller.disease_prevalence()

        self.fake_model.get_most_common_diseases.assert_called_once_with(10)
        self.assertTrue(isinstance(result, DataFrame))
        self.assertFalse(result.empty)

    def test_disease_prevalence_error(self):
        """ Should return empty DataFrame on model.get_most_common_diseases has an error """

        self.fake_model.get_most_common_diseases.side_effect = RuntimeError
        result = self.controller.disease_prevalence()

        self.fake_model.get_most_common_diseases.assert_called_once_with(10)
        self.assertIsInstance(result, DataFrame)
        self.assertTrue(result.empty)

    ############## symptom_prevalence #############
    
    def test_symptom_prevalence_success(self):
        """Should return DataFrame when model.get_most_common_symptoms succeeds."""
        
        self.fake_model.get_most_common_symptoms.return_value = self.sample_df

        result = self.controller.symptom_prevalence()

        self.fake_model.get_most_common_symptoms.assert_called_once_with(10)
        self.assertIsInstance(result, DataFrame)
        self.assertFalse(result.empty)

    def test_symptom_prevalence_error(self):
        """Should return empty DataFrame on model error."""
        
        self.fake_model.get_most_common_symptoms.side_effect = Exception
        result = self.controller.symptom_prevalence()

        self.fake_model.get_most_common_symptoms.assert_called_once_with(10)
        self.assertTrue(result.empty)

    ############# symptom_frequency #############

    def test_symptom_frequency_success(self):
        """Should return DataFrame when model succeeds."""
        
        self.fake_model.get_symptom_frequency.return_value = self.sample_df

        result = self.controller.symptom_frequency()

        self.fake_model.get_symptom_frequency.assert_called_once_with(10)
        self.assertIsInstance(result, DataFrame)
        self.assertFalse(result.empty)

    def test_symptom_frequency_error(self):
        """Should return empty DataFrame on model error."""
        
        self.fake_model.get_symptom_frequency.side_effect = ValueError # represents an input error/ data validation error
        result = self.controller.symptom_frequency()

        self.fake_model.get_symptom_frequency.assert_called_once_with(10)
        self.assertTrue(result.empty)

    ############# severity_distribution #############

    def test_severity_distribution_success(self):
        """Should return DataFrame when model succeeds."""
        
        self.fake_model.get_symptom_severity_distribution.return_value = self.sample_df

        result = self.controller.severity_distribution()

        self.fake_model.get_symptom_severity_distribution.assert_called_once()
        self.assertIsInstance(result, DataFrame)
        self.assertFalse(result.empty)

    def test_severity_distribution_error(self):
        """Should return empty DataFrame on model error."""
        
        self.fake_model.get_symptom_severity_distribution.side_effect = RuntimeError
        result = self.controller.severity_distribution()

        self.fake_model.get_symptom_severity_distribution.assert_called_once()
        self.assertTrue(result.empty)
    
    ############# symptom_disease_matrix #############

    def test_symptom_disease_matrix_success(self):
        """Should return DataFrame when model succeeds."""
        
        self.fake_model.get_symptom_disease_matrix.return_value = self.sample_df

        result = self.controller.symptom_disease_matrix()

        self.fake_model.get_symptom_disease_matrix.assert_called_once()
        self.assertIsInstance(result, DataFrame)
        self.assertFalse(result.empty)

    def test_symptom_disease_matrix_error(self):
        """Should return empty DataFrame on model error."""
        
        self.fake_model.get_symptom_disease_matrix.side_effect = KeyError # represents a missing key when creating the matrix. missing column in DF
        result = self.controller.symptom_disease_matrix()

        self.fake_model.get_symptom_disease_matrix.assert_called_once()
        self.assertTrue(result.empty)

    ############# severity_mapping #############

    def test_severity_mapping_success(self):
        """Should return DataFrame when model succeeds."""
        
        self.fake_model.get_symptom_severity_mapping.return_value = self.sample_df

        result = self.controller.severity_mapping()

        self.fake_model.get_symptom_severity_mapping.assert_called_once()
        self.assertIsInstance(result, DataFrame)
        self.assertFalse(result.empty)

    def test_severity_mapping_error(self):
        """Should return empty DataFrame on model error."""
        
        self.fake_model.get_symptom_severity_mapping.side_effect = Exception #catches unexpected errors
        result = self.controller.severity_mapping()

        self.fake_model.get_symptom_severity_mapping.assert_called_once()
        self.assertTrue(result.empty)


if __name__ == "__main__":
    unittest.main()