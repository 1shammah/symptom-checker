# views/common_view.py

import streamlit as st

def render_sidebar(navigate_to):
    """
    Renders the app sidebar with navigation buttons.
    Each time it runs, it:
      1. Reads st.session_state.user (must already be set by login)
      2. Queries the database for that user’s current 'role' field
      3. Syncs st.session_state.user.role to the DB’s value
      4. Displays “Admin Dashboard” link only when role == "admin"
    This ensures that manual DB edits or admin promotions take effect immediately.
    """
    # ─── 1) Grab the logged-in User object from session ─────────────────────
    user = st.session_state.get("user")
    if not user:
        # No user => no sidebar navigation
        return

    # ─── 2) Look up their “role” in SQLite ═══════════════════════════════════
    db     = st.session_state.db
    record = db.get_user_by_email(user.email)  # returns sqlite3.Row or None

    # Extract the 'role' column, defaulting to "User" if missing
    if record and "role" in record.keys():
        raw_role = record["role"]
    else:
        raw_role = "User"

    # ─── 3) Sync the in-memory User object so it never goes stale ───────────
    st.session_state.user.role = raw_role

    # Normalize for logic, and prepare title-cased display
    role         = raw_role.strip().lower()   # e.g. "Admin" -> "admin"
    display_role = role.title()               # "admin" -> "Admin"

    # ─── 4) Render the sidebar UI ────────────────────────────────────────────
    # Show who’s logged in, using the live display_role
    st.sidebar.markdown(
        f"<strong>Logged in as:</strong><br>{user.name} ({display_role})",
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")

    # Main navigation links (always shown)
    st.sidebar.button("About",            on_click=navigate_to, args=("main",))
    st.sidebar.button("Symptom Checker",  on_click=navigate_to, args=("symptom_checker",))
    st.sidebar.button("View Profile",     on_click=navigate_to, args=("profile",))

    # Admin-only link: only appears when the live role is "admin"
    if role == "admin":
        st.sidebar.button(
            "Admin Dashboard",
            on_click=navigate_to,
            args=("admin_dashboard",)
        )

    # Logout link (always shown)
    st.sidebar.markdown("---")
    st.sidebar.button("Logout", on_click=navigate_to, args=("login",))
