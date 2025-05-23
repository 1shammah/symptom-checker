# views/login_view.py

import streamlit as st
import re
from controllers.user_controller import UserController

# Regex for basic email validation
EMAIL_PATTERN = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

def show_login_view(navigate_to, user_ctrl: UserController):
    """
    Display the login form.
    On successful login, we:
      1. Authenticate via user_ctrl.login_user()
      2. Store the returned User object in session_state.user
      3. Immediately re-fetch that user’s DB record (by email)
         to pull in the authoritative 'role' field (e.g. "Admin" vs "User")
      4. Save that role back onto session_state.user.role
    This guarantees that session_state.user.role always matches
    the database, even if you manually edit it.
    """

    # Ensure DB + controller are available in session
    if "db" not in st.session_state:
        from models.database import initialise_database
        st.session_state.db = initialise_database()
    if "user_controller" not in st.session_state:
        st.session_state.user_controller = UserController(st.session_state.db)
    user_ctrl = st.session_state.user_controller

    st.subheader("Log In")

    def on_login():
        """Callback when the user submits the login form."""
        email    = st.session_state.login_email
        password = st.session_state.login_password

        # Clear any old messages
        st.session_state.pop("login_error", None)
        st.session_state.pop("login_success", None)

        # Simple form validation
        if not (email and password):
            st.session_state.login_error = "All fields are required."
            return
        if not EMAIL_PATTERN.match(email):
            st.session_state.login_error = "Enter a valid email address."
            return

        # Attempt authentication
        user = user_ctrl.login_user(email=email, password=password)  # returns User object or None
        if user:
            # Store the authenticated User object
            st.session_state.user = user

            # Re-fetch the authoritative DB record so we get the true 'role'
            record = st.session_state.db.get_user_by_email(email)      # sqlite3.Row
            if record and "role" in record.keys():
                # Overwrite the in-memory user.role with the DB value
                st.session_state.user.role = record["role"]
                # Also store the user’s DB id for downstream CRUD operations
                st.session_state.user_id = record["id"]

            # Mark success and navigate to main page
            st.session_state.login_success = True
            st.session_state.current_page  = "main"
        else:
            st.session_state.login_error = "Invalid email or password."

    # The login form itself
    with st.form("login_form"):
        st.text_input("Email", placeholder="you@example.com", key="login_email")
        st.text_input("Password", type="password", placeholder="Your password", key="login_password")
        st.form_submit_button("Login", on_click=on_login)

    # Show any login errors
    if "login_error" in st.session_state:
        st.error(st.session_state.login_error)

    # Link to Register if needed
    st.markdown('<div class="alternate-option">', unsafe_allow_html=True)
    st.write("Don’t have an account?")
    st.button("Register now", on_click=navigate_to, args=("register",))
    st.markdown('</div>', unsafe_allow_html=True)