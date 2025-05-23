# app.py

import streamlit as st
import pandas as pd

# Call the function that builds and populates the SQLite database
from models.database import initialise_database

# Call the controllers
from controllers.user_controller import UserController
from controllers.symptom_controller import SymptomController
from controllers.recommender_controller import RecommenderController
from controllers.analytics_controller import AnalyticsController
from controllers.admin_controller import AdminController

# Import the views here
from views.login_view import show_login_view
from views.register_view import show_register_view
from views.main_view import show_main_view
from views.symptoms_view import show_symptom_checker_view
from views.user_view import show_profile_view
from views.admin_view import show_admin_dashboard_view

def apply_custom_css():
    # Custom CSS to style the Streamlit app
    st.markdown("""
    <style>
    .main {
        background-color: #f8fcff;
    }
    .stButton button {
        background-color: #1E88E5;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #1565C0;
        box-shadow: 0 4px 8px rgba(30, 136, 229, 0.3);
        transform: translateY(-2px);
    }
    .success-message {
        background-color: #E8F5E9;
        color: #2E7D32;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2E7D32;
    }
    .error-message {
        background-color: #FFEBEE;
        color: #C62828;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #C62828;
    }
    .app-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .alternate-option {
        text-align: center;
        margin-top: 1.5rem;
    }
    .sidebar .stButton button {
        background-color: transparent !important;
        border: none !important;
        padding: 0.5rem 0 !important;
        text-align: left !important;
    }
    .sidebar .stButton button:hover {
        background-color: rgba(30, 136, 229, 0.1) !important;
    }
    /*  Admin scroll-box  */
    .user-scroll-box {
        max-height: 400px !important;
        overflow-y: auto !important;
        padding-right: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Navigation helper
def navigate_to(page: str):
    st.session_state.current_page = page
    return

def main():
    # Build the database (create tables, load CSV data). Once per app start 
    if "db" not in st.session_state:
        st.session_state.db = initialise_database()
    db = st.session_state.db

    # Create shared controller instances if not already in session 
    if "user_ctrl" not in st.session_state:
        st.session_state.user_ctrl        = UserController(db)
        st.session_state.symptom_ctrl     = SymptomController(db)
        st.session_state.recommender_ctrl = RecommenderController(db)
        st.session_state.analytics_ctrl   = AnalyticsController(db)
        st.session_state.admin_ctrl       = AdminController(db)

    # ─ Unpack controllers for easy local use ─
    user_ctrl        = st.session_state.user_ctrl
    symptom_ctrl     = st.session_state.symptom_ctrl
    recommender_ctrl = st.session_state.recommender_ctrl
    analytics_ctrl   = st.session_state.analytics_ctrl
    admin_ctrl       = st.session_state.admin_ctrl

    # Initialise routing state 
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"
    page = st.session_state.current_page

    # set page config (only on non-login/register pages) 
    if page not in ("login", "register"):
        st.set_page_config(
            page_title="AI Symptom Checker",
            page_icon="🩺",
            ##layout="wide",
        )

    # Inject site-wide CSS (buttons, header, etc.)
    apply_custom_css()

    # Always display the top header on every page 
    st.markdown(
        """
        <div class="app-header">
            <h1>AI Symptom Checker</h1>
        </div>
        <div style="width:100px;height:5px;
                    background-color:#1E88E5;
                    margin:0 auto;">
        </div>
        """,
        unsafe_allow_html=True
    )

    # Route to the correct view based on session_state.current_page
    if page == "login":
        show_login_view(navigate_to, user_ctrl)
    elif page == "register":
        show_register_view(navigate_to, user_ctrl)
    elif page == "main":
        show_main_view(navigate_to, user_ctrl, symptom_ctrl, recommender_ctrl, admin_ctrl, analytics_ctrl)
    elif page == "symptom_checker":
        show_symptom_checker_view(navigate_to, symptom_ctrl, recommender_ctrl)
    elif page == "profile":
        show_profile_view(navigate_to, user_ctrl)
    elif page == "admin_dashboard":
        show_admin_dashboard_view(navigate_to, analytics_ctrl, admin_ctrl)
    else:
        st.error(f"Unknown page: {page}.")
        st.error("Page not found.")

if __name__ == "__main__":
    main()
