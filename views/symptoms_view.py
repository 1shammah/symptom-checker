# views/symptoms_view.py

import streamlit as st
from controllers.symptom_controller import SymptomController
from controllers.recommender_controller import RecommenderController
from views.common_view import render_sidebar

def show_symptom_checker_view(
    navigate_to,
    symptom_ctrl: SymptomController,
    recommender_ctrl: RecommenderController
):
    """
    Displays the symptom checker interface.
    """
    # draw shared sidebar
    render_sidebar(navigate_to)

    # --- Main Content ---
    st.title("Symptom Checker")
    st.write("Page under construction. Select symptoms to get started.")
