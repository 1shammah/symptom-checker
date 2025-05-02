import streamlit as st
import pandas as pd

# Call the function that builds and populates the SQlite database
from models.database import initialise_database

# Call the controllers
from controllers.user_controller import UserController
from controllers.symptom_controller import SymptomController
from controllers.recommender_controller import RecommenderController
from controllers.analytics_controller import AnalyticsController
from controllers.admin_controller import AdminController

############# INITIAL SETUP #############

def main():    
    # Build the database (create tables, load CSV data). Happens once at app start.
    db = initialise_database()

    # Create one shared instance of each controller
    user_controller = UserController(db)
    symptom_controller = SymptomController(db)
    recommender_controller = RecommenderController(db)
    analytics_controller = AnalyticsController(db)
    admin_controller = AdminController(db)

if __name__ == "__main__":
    main()