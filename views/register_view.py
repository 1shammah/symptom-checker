import streamlit as st
import re
from controllers.user_controller import UserController

# Regex for basic email validation
EMAIL_PATTERN = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

def show_register_view(navigate_to, user_ctrl: UserController):
    """
    Display registration form.
    Uses on_click callback and st.session_state to avoid double-click issues.
    """

    # ensure one DB + controller per session
    if "db" not in st.session_state:
        from models.database import initialise_database
        st.session_state.db = initialise_database()
    if "user_controller" not in st.session_state:
        st.session_state.user_controller = UserController(st.session_state.db)

    st.subheader("Register")

    def on_register():
        """Callback when the user submits the form."""
        name     = st.session_state.reg_name
        email    = st.session_state.reg_email
        password = st.session_state.reg_password
        confirm  = st.session_state.reg_confirm
        gender   = st.session_state.reg_gender

        # clear old messages
        st.session_state.pop("register_error", None)
        st.session_state.pop("register_success", None)

        # validations
        if not (name and email and password and confirm):
            st.session_state.register_error = "All fields are required."
            return
        if not EMAIL_PATTERN.match(email):
            st.session_state.register_error = "Enter a valid email address."
            return
        if len(password) < 8:
            st.session_state.register_error = "Password must be at least 8 characters."
            return
        if password != confirm:
            st.session_state.register_error = "Passwords do not match."
            return

        # attempt registration
        success = user_ctrl.register_user(
            name=name.strip(),
            email=email.strip().lower(),
            password=password,
            gender=gender
        )
        if success:
            st.session_state.register_success = True
        else:
            st.session_state.register_error = "Registration failed. Email may already be in use."

    # the registration form
    with st.form("register_form"):
        st.text_input("Full Name", key="reg_name")
        st.text_input("Email", placeholder="you@example.com", key="reg_email")
        st.text_input("Password", type="password", key="reg_password")
        st.text_input("Confirm Password", type="password", key="reg_confirm")
        st.selectbox("Gender", ["Other", "Male", "Female"], key="reg_gender")
        st.form_submit_button("Register", on_click=on_register)

    # show error if any
    if "register_error" in st.session_state:
        st.error(st.session_state.register_error)

    # on success, show one button that immediately navigates back
    if st.session_state.get("register_success"):
        st.success("Registration successful! Please log in.")
        st.button("Back to Login", on_click=navigate_to, args=("login",))
        return

    # fallback link for users who change their mind
    st.markdown('<div class="alternate-option">', unsafe_allow_html=True)
    st.write("Already have an account?")
    st.button("Back to Login", on_click=navigate_to, args=("login",))
    st.markdown('</div>', unsafe_allow_html=True)
