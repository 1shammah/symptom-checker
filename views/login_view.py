import streamlit as st
import re
from controllers.user_controller import UserController

# Regex for basic email validation
EMAIL_PATTERN = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

def show_login_view(navigate_to, user_ctrl: UserController):
    """
    Display the login form.
    Uses on_click + session_state to validate and navigate in one click.
    """

    # ensure one Database + controller per session
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

        # clear old messages
        st.session_state.pop("login_error", None)
        st.session_state.pop("login_success", None)

        # validations
        if not (email and password):
            st.session_state.login_error = "All fields are required."
            return
        if not EMAIL_PATTERN.match(email):
            st.session_state.login_error = "Enter a valid email address."
            return

        # attempt authentication
        user = user_ctrl.login_user(email=email, password=password)
        if user:
            st.session_state.user = user
            st.session_state.login_success = True
            # store user DB id for use in the user crud 
            record = st.session_state.db.get_user_by_email(email)
            if record:
                st.session_state.user_id = record["id"]
            # navigate to the main view immedialtely
            st.session_state.current_page = "main"

        else:
            st.session_state.login_error = "Invalid email or password."

    # the login form
    with st.form("login_form"):
        st.text_input("Email", placeholder="you@example.com", key="login_email")
        st.text_input("Password", type="password", placeholder="Your password", key="login_password")
        st.form_submit_button("Login", on_click=on_login)

    # show error if any
    if "login_error" in st.session_state:
        st.error(st.session_state.login_error)

    # fallback link for users without an account
    st.markdown('<div class="alternate-option">', unsafe_allow_html=True)
    st.write("Don’t have an account?")
    st.button("Register now", on_click=navigate_to, args=("register",))
    st.markdown('</div>', unsafe_allow_html=True)