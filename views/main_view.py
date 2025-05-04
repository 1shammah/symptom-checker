# get the buttons working like login view
# radio buttons look ugly, how about an invisible button
# remove navigation title from side bar
# better place holder text in the different views
# do i ever use the logout method or is it redundant?


import streamlit as st

from views.symptoms_view import show_symptom_checker_view
from views.user_view import show_profile_view
from views.admin_view import show_admin_dashboard_view

def show_main_view(navigate_to,
                   user_ctrl,
                   symptom_ctrl,
                   recommender_ctrl,
                   analytics_ctrl,
                   admin_ctrl):
    """
    Main multipage view with sidebar navigation.
    Shows different sub-pages depending on user role and choice.
    """

    # Flash welcome once right after login
    if st.session_state.pop("login_success", False):
        user = st.session_state.user
        st.success(f"Welcome, {user.name}!")

    # ----- Sidebar -----
    st.sidebar.title("Navigation")

    # Build menu items
    menu_items = [
        "Symptom Checker",
        "My Profile"
    ]
    # Only admins see the dashboard link
    if st.session_state.user.role == "Admin":
        menu_items.append("Admin Dashboard")

    # User picks a page
    choice = st.sidebar.radio("Go to", menu_items)

    st.sidebar.markdown("---")
    # Logout button at bottom
    if st.sidebar.button("Logout"):
        # clear session and go back to login
        for key in ["user", "logged_in", "current_page"]:
            st.session_state.pop(key, None)
        navigate_to("login")
        return  # stop rendering this page

    # ----- Page content -----
    if choice == "Symptom Checker":
        # placeholder or import your real symptom checker view
        show_symptom_checker_view(navigate_to, symptom_ctrl, recommender_ctrl)
    elif choice == "My Profile":
        # placeholder or import your real profile view
        show_profile_view(navigate_to, user_ctrl)
    elif choice == "Admin Dashboard":
        # placeholder or import your real admin dashboard view
        show_admin_dashboard_view(navigate_to, analytics_ctrl, admin_ctrl, user_ctrl)
    else:
        st.error(f"Unknown section: {choice}")

