# views/common_view.py

import streamlit as st

def render_sidebar(navigate_to):
    """
    Renders the app sidebar with navigation buttons.
    Assumes st.session_state['user'] is set.
    """
    user = st.session_state.get("user")
    role = getattr(user, "role", "User") if user else "User"

    st.sidebar.markdown(f"**Logged in as:**  \n{user.name} ({role})")
    st.sidebar.markdown("---")

    # New “About” button
    st.sidebar.button("About", on_click=navigate_to, args=("main",))

    # Existing navigation
    st.sidebar.button("Symptom Checker", on_click=navigate_to, args=("symptom_checker",))
    st.sidebar.button("View Profile",     on_click=navigate_to, args=("profile",))
    if role == "Admin":
        st.sidebar.button("Admin Dashboard", on_click=navigate_to, args=("admin_dashboard",))

    st.sidebar.markdown("---")
    st.sidebar.button("Logout", on_click=navigate_to, args=("login",))
