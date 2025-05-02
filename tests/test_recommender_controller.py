import unittest
from unittest.mock import MagicMock, patch
from controllers.recommender_controller import RecommenderController
from typing import List, Tuple


class TestRecommenderController(unittest.TestCase):
    def setUp(self):
        
        # Patch out heavy TF-IDF fitting logic so it never runs in tests
        # Replaces RecommenderModel with a fake that does nothing so as to isolate controller

        patcher = patch(
            'controllers.recommender_controller.RecommenderModel.fit',
            return_value=None  # no-op for fit() method
        )
        patcher.start()
        # ensure we stop the patcher after each test
        self.addCleanup(patcher.stop)

        # replace Database so to never use real DB calls
        fake_db = MagicMock()

        # construct controller (which in __init__ will build and fit a real RecommenderModel)
        # override .model immediately after to keep tests fast and predictable
        self.controller = RecommenderController(fake_db)

        # replace its model with a fake to control .recommend()
        self.fake_model = MagicMock()
        self.controller.model = self.fake_model

        # sample recommendation list
        self.sample_recommendations: List[Tuple[str, float]] = [
            ("Influenza", 0.87),
            ("Common Cold", 0.42),
        ]

    ############# recommend_diseases() #############

    def test_recommend_diseases_success(self):
        """Should call model.recommend with symptoms and top_n, return its list."""
        
        self.fake_model.recommend.return_value = self.sample_recommendations

        result = self.controller.recommend_diseases(
            selected_symptoms=["fever", "cough"],
            top_n=2
        )

        self.fake_model.recommend.assert_called_once_with(
            ["fever", "cough"], 2
        )
        self.assertEqual(result, self.sample_recommendations)

    def test_recommend_diseases_empty_input(self):
        """Empty symptom list yields whatever model.recommend returns (could be empty)."""
        
        self.fake_model.recommend.return_value = []
        result = self.controller.recommend_diseases([], top_n=3)
        self.fake_model.recommend.assert_called_once_with([], 3)
        self.assertEqual(result, [])

    def test_recommend_diseases_exception(self):
        """If model.recommend raises exception, controller catches and returns empty list."""
        
        self.fake_model.recommend.side_effect = RuntimeError("AI error")

        result = self.controller.recommend_diseases(
            selected_symptoms=["x"],
            top_n=1
        )

        self.fake_model.recommend.assert_called_once_with(["x"], 1)
        self.assertEqual(result, [])

    def test_recommend_diseases_invalid_type(self):
        """Non-list selected_symptoms should produce TypeError from model."""
        
        self.fake_model.recommend.side_effect = TypeError("bad input")

        result = self.controller.recommend_diseases(
            selected_symptoms="not-a-list",  # wrong type
            top_n=1
        )

        self.fake_model.recommend.assert_called_once_with("not-a-list", 1)
        self.assertEqual(result, [])

    ############# recommend_with_details() #############

    def test_recommend_with_details_success(self):
        """Should return enriched dicts with disease, score, symptoms, precautions."""
        
        # model.recommend → disease names + scores
        self.fake_model.recommend.return_value = [("Flu", 0.95)]
        # replace DB helpers for details
        self.controller.db.get_symptoms_by_disease = MagicMock(return_value=["fever", "ache"])
        self.controller.db.get_precautions_by_disease = MagicMock(return_value=["rest", "fluids"])

        result = self.controller.recommend_with_details(
            selected_symptoms=["fever"], top_n=1
        )

        # check recommend call
        self.fake_model.recommend.assert_called_once_with(["fever"], 1)

        # ensure we fetched details from DB
        self.controller.db.get_symptoms_by_disease.assert_called_once_with("Flu")
        self.controller.db.get_precautions_by_disease.assert_called_once_with("Flu")

        # final structure
        expected = [{
            "disease": "Flu",
            "score": 0.95,
            "symptoms": ["fever", "ache"],
            "precautions": ["rest", "fluids"]
        }]
        self.assertEqual(result, expected)

    def test_recommend_with_details_empty(self):
        
        """Empty recommendations list yields empty list."""
        self.fake_model.recommend.return_value = []

        result = self.controller.recommend_with_details([], top_n=5)

        self.fake_model.recommend.assert_called_once_with([], 5)
        self.assertEqual(result, [])

    def test_recommend_with_details_model_error(self):
        """If model.recommend errors, controller returns empty list."""
        
        self.fake_model.recommend.side_effect = RuntimeError("AI fail")

        result = self.controller.recommend_with_details(["x"], top_n=1)

        self.fake_model.recommend.assert_called_once_with(["x"], 1)
        self.assertEqual(result, [])

    def test_recommend_with_details_db_error(self):
        """If fetching symptoms or precautions errors, controller returns empty list."""
        
        # model returns one hit
        self.fake_model.recommend.return_value = [("Malaria", 0.5)]
        # cause DB error on symptom lookup
        self.controller.db.get_symptoms_by_disease = MagicMock(side_effect=KeyError("no col"))
        self.controller.db.get_precautions_by_disease = MagicMock()

        result = self.controller.recommend_with_details(["headache"], top_n=1)

        # model called, then controller caught DB error
        self.fake_model.recommend.assert_called_once_with(["headache"], 1)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()