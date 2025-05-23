# views/main_view.py

import streamlit as st
from controllers.user_controller import UserController
from controllers.admin_controller import AdminController
from controllers.symptom_controller import SymptomController
from controllers.recommender_controller import RecommenderController
from controllers.analytics_controller import AnalyticsController
from views.common_view import render_sidebar

def show_main_view(
    navigate_to,
    user_ctrl: UserController,
    symptom_ctrl: SymptomController,
    recommender_ctrl: RecommenderController,
    admin_ctrl: AdminController,
    analytics_ctrl: AnalyticsController
):
    """
    About / Overview page for viva: describes project goals, tech stack,
    AI approach, and navigation.
    """
    # draw shared sidebar (with the new “About” button)
    render_sidebar(navigate_to)

    # one-time welcome message
    if st.session_state.pop("login_success", False):
        user = st.session_state.get("user")
        st.success(f"Welcome, {user.name}! Feel free to explore the app using the sidebar.")

    # Main Content
    st.title("About the AI-Powered Symptom Checker")

    st.markdown("""
<div class="overview">
  <h3>Project Overview</h3>
  <p>The <strong>AI-Powered Symptom Checker</strong> is a privacy-first Streamlit application that
  lets users select symptoms from a dropdown and receive <strong>personalized disease
  recommendations</strong> via a <strong>content-based filtering</strong> approach (TF-IDF + cosine similarity).</p>

  <h3>Key Features</h3>
  <ul>
    <li><strong>AI-Driven Recommendations</strong>: Uses TF-IDF vectorisation of disease–symptom profiles and cosine similarity to rank the most likely diseases.</li>
    <li><strong>Content-Based Filtering</strong>: Matches your input to diseases whose symptom signatures are most similar.</li>
    <li><strong>Privacy by Design</strong>: Runs entirely on local <strong>SQLite</strong> and <strong>scikit-learn</strong>, with <strong>no user history</strong> stored.</li>
    <li><strong>User &amp; Admin Workflows</strong>:
      <ul>
        <li><strong>Users</strong>: register, log in, select symptoms, view top-n disease matches, and manage profiles.</li>
        <li><strong>Admins</strong>: manage user roles, delete accounts, and explore analytics on symptom frequency, disease prevalence, and severity distribution.</li>
      </ul>
    </li>
  </ul>

  <h3>Navigation</h3>
  <ul>
    <li><strong>About</strong>: Return to this overview page.</li>
    <li><strong>Symptom Checker</strong>: Input symptoms → get AI-backed disease suggestions.</li>
    <li><strong>View Profile</strong>: Update your details or change your password.</li>
    <li><strong>Admin Dashboard</strong> (Admin only): User management & analytics insights.</li>
  </ul>

  <h3>Architecture &amp; Tech Stack</h3>
  <ul>
    <li><strong>Frontend</strong>: Multi-page <strong>Streamlit</strong> app (login, register, symptom checker, profile, admin dashboard).</li>
    <li><strong>Backend</strong>: <strong>SQLite</strong> for data storage (diseases, symptoms, users, severity, precautions).</li>
    <li><strong>AI Model</strong>: Pandas for building the disease–symptom matrix; scikit-learn’s <code>TfidfVectorizer</code> and <code>cosine_similarity</code> for content-based disease recommendations.</li>
    <li><strong>Security</strong>: <strong>bcrypt</strong> password hashing; parameterized queries; role-based access control.</li>
  </ul>
</div>
""", unsafe_allow_html=True)
