import streamlit as st
from controllers.admin_controller import AdminController
from controllers.analytics_controller import AnalyticsController
from controllers.user_controller import UserController

def show_admin_dashboard_view(navigate_to, analytics_ctrl, admin_ctrl, user_ctrl):
    """
    Displays the admin dashboard page
    Allows admins to view and manage user data and analytics
    """

    st.write("page under cinstruction")