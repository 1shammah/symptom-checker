# Use a fake User model to test only the controller logic
# Skips setting up a real database
# Helps to check the controller calls the right model methods
# Passes the correct info and handles success/errors correctly

import unittest
from unittest.mock import MagicMock
from controllers.symptom_controller import SymptomController
from models.symptom import Symptom

class TestSymptomController(unittest.TestCase):
    def setUp(self):
        # Use a fake Database to isolate controller logic
        self.fake_db = MagicMock()
        self.controller = SymptomController(self.fake_db)
        # Replace underlying model with a MagicMock
        self.fake_model = MagicMock()
        self.controller.model = self.fake_model

    ############# list_all_symptoms #############

    def test_list_all_symptoms_success(self):
        """ Should return a list of Symptom objects when model.get_all succeeds """
        
        fake_list = [
            Symptom(name="Headache"),
            Symptom(name="Fever", description="High temperature", severity=2)
        ]
        self.fake_model.get_all.return_value = fake_list

        result = self.controller.list_all_symptoms()

        self.assertEqual(result, fake_list)
        self.fake_model.get_all.assert_called_once()

    def test_list_all_symptoms_exception(self):   
        """Should return empty list when model.get_all raises an exception."""
        
        self.fake_model.get_all.side_effect = RuntimeError("fail")

        result = self.controller.list_all_symptoms()

        self.assertEqual(result, [])
        self.fake_model.get_all.assert_called_once()

     ############# get_symptoms_for_disease #############

    def test_get_symptoms_for_disease_success(self):
        """Should return symptom list when DB lookup succeeds."""
        
        expected = ["Cough", "Fever"]
        self.fake_db.get_symptoms_by_disease.return_value = expected

        result = self.controller.get_symptoms_for_disease("Flu")

        self.assertEqual(result, expected)
        self.fake_db.get_symptoms_by_disease.assert_called_once_with("Flu")

    def test_get_symptoms_for_disease_exception(self):
        """Should return empty list when DB lookup raises an exception."""
        
        self.fake_db.get_symptoms_by_disease.side_effect = KeyError("oops")

        result = self.controller.get_symptoms_for_disease("Flu")

        self.assertEqual(result, [])
        self.fake_db.get_symptoms_by_disease.assert_called_once_with("Flu")

    ############# get_diseases_for_symptom #############

    def test_get_diseases_for_symptom_success(self):
        """Should return disease list when DB lookup succeeds."""
        
        expected = ["Cold", "Allergy"]
        self.fake_db.get_diseases_by_symptom.return_value = expected

        result = self.controller.get_diseases_for_symptom("Sneezing")

        self.assertEqual(result, expected)
        self.fake_db.get_diseases_by_symptom.assert_called_once_with("Sneezing")

    def test_get_diseases_for_symptom_exception(self):
        """Should return empty list when DB lookup raises an exception."""
        
        self.fake_db.get_diseases_by_symptom.side_effect = ValueError("fail")

        result = self.controller.get_diseases_for_symptom("Sneezing")

        self.assertEqual(result, [])
        self.fake_db.get_diseases_by_symptom.assert_called_once_with("Sneezing")

    ############# get_precautions #############

    def test_get_precautions_success(self):
        """Should return list of precautions when DB lookup succeeds."""
        
        expected = ["Wash hands", "Rest"]
        self.fake_db.get_precautions_by_disease.return_value = expected

        result = self.controller.get_precautions("Flu")

        self.assertEqual(result, expected)
        self.fake_db.get_precautions_by_disease.assert_called_once_with("Flu")

    def test_get_precautions_not_found(self):
        """Should return None when DB returns None for missing disease."""
        
        self.fake_db.get_precautions_by_disease.return_value = None

        result = self.controller.get_precautions("Unknown")

        self.assertIsNone(result)
        self.fake_db.get_precautions_by_disease.assert_called_once_with("Unknown")

    def test_get_precautions_exception(self):
        """Should return None when DB lookup raises an exception."""
        
        self.fake_db.get_precautions_by_disease.side_effect = RuntimeError("error")

        result = self.controller.get_precautions("Flu")

        self.assertIsNone(result)
        self.fake_db.get_precautions_by_disease.assert_called_once_with("Flu")

    ############# get_description #############

    def test_get_description_success(self):
        """Should return description when DB lookup succeeds."""
        
        self.fake_db.get_description_by_symptom.return_value = "Dry cough"

        result = self.controller.get_description("Cough")

        self.assertEqual(result, "Dry cough")
        self.fake_db.get_description_by_symptom.assert_called_once_with("Cough")

    def test_get_description_not_found(self):
        """Should return None when DB returns None for missing symptom."""
        
        self.fake_db.get_description_by_symptom.return_value = None

        result = self.controller.get_description("Unknown")

        self.assertIsNone(result)
        self.fake_db.get_description_by_symptom.assert_called_once_with("Unknown")

    def test_get_description_exception(self):
        """Should return None when DB lookup raises an exception."""
        
        self.fake_db.get_description_by_symptom.side_effect = LookupError("fail")

        result = self.controller.get_description("Cough")

        self.assertIsNone(result)
        self.fake_db.get_description_by_symptom.assert_called_once_with("Cough")

    ############# get_severity #############

    def test_get_severity_success(self):
        """Should return severity when DB lookup succeeds."""
        
        self.fake_db.get_severity_by_symptom.return_value = "2"

        result = self.controller.get_severity("Fever")

        self.assertEqual(result, "2")
        self.fake_db.get_severity_by_symptom.assert_called_once_with("Fever")

    def test_get_severity_not_found(self):
        """Should return None when DB returns None for missing symptom."""
        
        self.fake_db.get_severity_by_symptom.return_value = None

        result = self.controller.get_severity("Unknown")

        self.assertIsNone(result)
        self.fake_db.get_severity_by_symptom.assert_called_once_with("Unknown")

    def test_get_severity_exception(self):
        """Should return None when DB lookup raises an exception."""
        
        self.fake_db.get_severity_by_symptom.side_effect = Exception("error")

        result = self.controller.get_severity("Fever")

        self.assertIsNone(result)
        self.fake_db.get_severity_by_symptom.assert_called_once_with("Fever")
    

if __name__ == "__main__":
    unittest.main()