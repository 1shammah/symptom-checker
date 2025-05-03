import  streamlit as st
import time
import re
from controllers.user_controller import UserController

# Define a regex pattern for validating email addresses
EMAIL_PATTERN = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

def show_login_view(navigate_to):
    """
    Display the login from and call UserController.login_user()
    On success redirect to the main page. (symptom checker)
    """

    # store user controller and DB in session state so it's created only once
    # and reused on every streamlit rerun, avoiding reinitialisation
    # and preserving state

    if "db" not in st.session_state:
        from models.database import initialise_database
        st.session_state.db = initialise_database()
    if "user_controller" not in st.session_state:
        st.session_state.user_controller = UserController(st.session_state.db)
    user_ctrl = st.session_state.user_controller

    st.subheader("Log In")

    # build the login form
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Login")

        if submitted:
            # validate inputs
            if not email or not password:
                st.error("Please enter both email and password.")
            # email regex validation
            elif not EMAIL_PATTERN.match(email):
                st.error("Invalid email format. Please enter a valid email address.")
            else: 
                # Authenticate user
                with st.spinner("Logging in..."):
                    time.sleep(1)
                    user = user_ctrl.login_user(email=email, password=password)
                if user:
                    st.markdown(f"<div class='success-message'> Welcome, {user.name}!</div>", unsafe_allow_html=True)
                    
                    # update store user dataclass in session state
                    st.session_state.user = user 
                    st.session_state.logged_in = True 

                    st.success("Redirecting to the main page...")
                    time.sleep(1.5)
                    navigate_to("main")    # subject to change depending on the app flow
                    return
                else:
                    st.markdown('<div class="error-message"> Invalid email or password. Please try again.</div>', unsafe_allow_html=True)
                    time.sleep(1)
    
    # link to the registration page    
    st.markdown('<div class="alternative-option">', unsafe_allow_html=True)
    st.write("Don't have an account?")
    st.button(
        "Register now",
        on_click=navigate_to,
        args=("register",)
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Disclaimer 
    with st.expander("About Health Symptom Checker", expanded=False):
        st.markdown("""
        This application is for demonstration purposes only and should not be considered a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
        """)
    