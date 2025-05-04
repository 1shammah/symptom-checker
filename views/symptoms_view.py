import streamlit as st
from controllers.symptom_controller import SymptomController
from controllers.recommender_controller import RecommenderController

def show_symptom_checker_view(navigate_to,
                              symptom_ctrl,
                              recommender_ctrl):
    """
    Displays the symptom checker interface
    With a dropdown and autocomplete of symptoms for the user to select
    Has a recommend/ check symptoms button that then leads users to a page 
    with the recommended diagnosis and treatment
    """

    st.write("page under construction")