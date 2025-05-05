# views/user_view.py

import streamlit as st
import bcrypt
from controllers.user_controller import UserController
from views.common_view import render_sidebar

def show_profile_view(navigate_to, user_ctrl: UserController):
    """
    Displays the user profile page with:
      - Profile summary
      - Edit profile (with inline success message)
      - Change password
      - Delete account
    """
    # draw shared sidebar
    render_sidebar(navigate_to)

    # fetch database instance and current user
    db = st.session_state.db
    current_user = st.session_state.user
    record = db.get_user_by_email(current_user.email)
    if record is None:
        st.error("Error: user record not found. Please log in again.")
        navigate_to("login")
        return
    user_id = record["id"]

    # get fresh profile object
    profile = user_ctrl.get_profile(user_id)

    # --- Profile Summary ---
    st.markdown("<h2>Profile Summary</h2>", unsafe_allow_html=True)
    st.markdown(f"<strong>Name:</strong> {profile.name}", unsafe_allow_html=True)
    st.markdown(f"<strong>Email:</strong> {profile.email}", unsafe_allow_html=True)
    st.markdown(f"<strong>Gender:</strong> {profile.gender}", unsafe_allow_html=True)
    created_at = record["created_at"].split(" ")[0]
    st.markdown(f"<strong>Account Created:</strong> {created_at}", unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)

    # --- Edit Profile ---
    st.markdown("<h2>Edit Profile</h2>", unsafe_allow_html=True)

    def _handle_save():
        new_name = st.session_state.profile_name.strip()
        new_gender = st.session_state.profile_gender
        success = user_ctrl.update_profile(user_id, new_name, new_gender)
        if success:
            # update session so sidebar reflects changes
            st.session_state.user.name = new_name
            st.session_state.user.gender = new_gender
            # set a flag to show inline success after rerun
            st.session_state.profile_updated_inline = True
        else:
            st.session_state.profile_updated_error = True

    with st.form("profile_form"):
        st.text_input("Full Name", value=profile.name, key="profile_name")
        st.text_input("Email", value=profile.email, disabled=True)
        st.selectbox(
            "Gender",
            ["Other", "Male", "Female"],
            index=["Other", "Male", "Female"].index(profile.gender),
            key="profile_gender"
        )
        st.form_submit_button("Save Changes", on_click=_handle_save)

        # Inline success/error messages
        if st.session_state.pop("profile_updated_inline", False):
            st.success("Profile updated successfully.")
        if st.session_state.pop("profile_updated_error", False):
            st.error("Failed to update profile. Please try again.")

    st.markdown("<hr/>", unsafe_allow_html=True)

    # --- Change Password ---
    st.markdown("<h2>Change Password</h2>", unsafe_allow_html=True)

    def _handle_change_pw():
        old_pw     = st.session_state.cp_old_password
        new_pw     = st.session_state.cp_new_password
        confirm_pw = st.session_state.cp_confirm_password

        # Basic validations
        if not (old_pw and new_pw and confirm_pw):
            st.session_state.cp_error = "All fields are required."
            return
        if len(new_pw) < 8:
            st.session_state.cp_error = "New password must be at least 8 characters."
            return
        if new_pw != confirm_pw:
            st.session_state.cp_error = "New passwords do not match."
            return

        # Fetch stored hash from DB
        record      = st.session_state.db.get_user_by_id(user_id)
        stored_hash = record["password"]
        if not bcrypt.checkpw(old_pw.encode('utf-8'), stored_hash.encode('utf-8')):
            st.session_state.cp_error = "Current password is incorrect."
            return

        # Hash & update
        new_hashed = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        success    = st.session_state.db.update_user_password(user_id, new_hashed)
        if success:
            st.session_state.cp_success = True
        else:
            st.session_state.cp_error = "Failed to update password. Please try again."

    with st.form("password_form"):
        st.text_input("Current Password", type="password", key="cp_old_password")
        st.text_input("New Password",     type="password", key="cp_new_password")
        st.text_input("Confirm Password", type="password", key="cp_confirm_password")
        st.form_submit_button("Change Password", on_click=_handle_change_pw)

        if st.session_state.pop("cp_success", False):
            st.success("Password changed successfully.")
        if (msg := st.session_state.pop("cp_error", None)):
            st.error(msg)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # --- Danger Zone: Delete Account ---
    st.markdown("<h2 style='color:#C62828;'>Danger Zone: Delete Account</h2>", unsafe_allow_html=True)
    with st.expander("⚠️ I understand this action cannot be undone"):

        def _handle_delete():
            pw      = st.session_state.del_password
            confirm = st.session_state.del_confirm

            if not confirm:
                st.session_state.del_error = "Please check the confirmation box to proceed."
                return

            record      = st.session_state.db.get_user_by_id(user_id)
            stored_hash = record["password"]
            if not bcrypt.checkpw(pw.encode('utf-8'), stored_hash.encode('utf-8')):
                st.session_state.del_error = "Password is incorrect."
                return

            success = st.session_state.db.delete_user_by_id(user_id)
            if success:
                # clear session and navigate immediately
                for k in ("user", "login_success"):
                    st.session_state.pop(k, None)
                navigate_to("login")
                return
            else:
                st.session_state.del_error = "Failed to delete account. Please try again."

        with st.form("delete_form"):
            st.text_input("Enter Password to Confirm", type="password", key="del_password")
            st.checkbox("I confirm I want to permanently delete my account.", key="del_confirm")
            st.form_submit_button("Delete Account", on_click=_handle_delete)

            # only show deletion errors inline
            if (msg := st.session_state.pop("del_error", None)):
                st.error(msg)