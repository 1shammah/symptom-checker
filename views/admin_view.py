# views/admin_view.py

import streamlit as st
from controllers.admin_controller import AdminController
from controllers.analytics_controller import AnalyticsController
from views.common_view import render_sidebar

def show_admin_dashboard_view(navigate_to,
                              analytics_ctrl: AnalyticsController,
                              admin_ctrl: AdminController):
    """
    Admin Dashboard view:
      • Tab 1: User Management – promote, demote, delete accounts (paginated)
      • Tab 2: Analytics – read-only stats on diseases, symptoms, severities

    Uses only on_click callbacks for all buttons.
    """
    # Sidebar
    render_sidebar(navigate_to)
    current_user = st.session_state.get("user")
    record = st.session_state.db.get_user_by_email(current_user.email)
    db_role = record["role"] if (record and "role" in record.keys()) else ""
    if db_role.strip().lower() != "admin":
        navigate_to("main")
        return

    # Page Header & Tabs
    st.markdown("<h2>Admin Dashboard</h2>", unsafe_allow_html=True)
    tab_users, tab_analytics = st.tabs(["User Management", "Analytics"])

    # Tab for user management
    with tab_users:
        st.markdown("<h3>User Management</h3>", unsafe_allow_html=True)
        st.markdown("Below is the list of all accounts. Use the buttons to change roles or delete them.")

        #Fetch full user list
        users = admin_ctrl.list_users()

        #Overview table listing all users
        df_all = {
            "Name":   [u.name  for u in users],
            "Email":  [u.email for u in users],
            "Gender": [u.gender for u in users],
            "Role":   [u.role  for u in users],
        }
        st.dataframe(df_all, use_container_width=True)
        st.markdown("---")

        # page setup for the expanders
        total     = len(users)
        page_size = 5
        if "admin_page" not in st.session_state:
            st.session_state.admin_page = 0
        page     = st.session_state.admin_page
        max_page = (total - 1) // page_size if total else 0
        start    = page * page_size
        end      = min(start + page_size, total)

        # Page controls
        def go_prev():
            st.session_state.admin_page = max(page - 1, 0)
        def go_next():
            st.session_state.admin_page = min(page + 1, max_page)

        st.markdown(f"**Showing users {start+1}–{end} of {total}**")
        col1, col2 = st.columns(2)
        col1.button("‹ Previous", disabled=(page == 0), on_click=go_prev)
        col2.button("Next ›",      disabled=(page >= max_page), on_click=go_next)
        st.markdown("---")

        # Feedback messages
        msgs = st.session_state.pop("admin_msgs", [])
        for m in msgs:
            getattr(st, m["type"])(m["text"])

        # Scrollable box containing only the expanders
        st.markdown(
            "<div style='max-height:400px; overflow-y:auto; padding-right:10px;'>",
            unsafe_allow_html=True
        )

        # displaying one expander per user on this page
        for u in users[start:end]:
            open_flag = f"open_expander_{u.email}"
            expanded  = st.session_state.pop(open_flag, False)
            label     = f"{u.name} · {u.email} ({u.role})"

            with st.expander(label, expanded=expanded):
                st.write(f"**Gender:** {u.gender}")

                # Promote User to  Admin
                if u.role.lower() == "user":
                    def _promote(email=u.email):
                        ok = admin_ctrl.promote_user(email)
                        st.session_state.setdefault("admin_msgs", []).append({
                            "type": "success" if ok else "error",
                            "text":  f"{email} is now an Admin." if ok else f"Failed to promote {email}."
                        })
                        st.session_state[open_flag] = True

                    st.button(
                        "Promote to Admin",
                        key=f"promote_{u.email}",
                        on_click=_promote
                    )

                # Demote Admin to User (with immediate redirect for self)
                else:
                    def _demote(email=u.email):
                        ok = admin_ctrl.demote_user(email)
                        st.session_state.setdefault("admin_msgs", []).append({
                            "type": "success" if ok else "error",
                            "text":  f"{email} has been demoted to User." if ok else f"Failed to demote {email}."
                        })
                        st.session_state[open_flag] = True
                        if ok and email == current_user.email:
                            navigate_to("main")

                    st.button(
                        "Demote to User",
                        key=f"demote_{u.email}",
                        on_click=_demote
                    )

                # Delete Account with confirmation checkbox + single-click delete
                confirm_key = f"confirm_delete_{u.email}"
                open_flag   = f"open_expander_{u.email}"

                # Display the confirmation checkbox
                st.checkbox(
                    "I understand this action cannot be undone",
                    key=confirm_key
                )

                # Define the callback that actually deletes
                def _delete_user(email=u.email, name=u.name,
                                confirm_key=confirm_key, open_flag=open_flag):
                    # ensure the checkbox was ticked
                    if not st.session_state.get(confirm_key, False):
                        st.session_state.setdefault("admin_msgs", []).append({
                            "type": "error",
                            "text":  "Please confirm deletion to proceed."
                        })
                    else:
                        # look up their database record & delete
                        rec = st.session_state.db.get_user_by_email(email)
                        ok  = admin_ctrl.delete_user(rec["id"]) if rec else False
                        st.session_state.setdefault("admin_msgs", []).append({
                            "type": "warning" if ok else "error",
                            "text":  (f"Account deleted: {name}" if ok else f"Failed to delete {name}.")
                        })
                    # keep this expander open so they see the feedback
                    st.session_state[open_flag] = True

                # 3) Display the single-click Delete button
                st.button(
                    "Delete Account",
                    key=f"delete_{u.email}",
                    on_click=_delete_user
                )


        # Close scrollable box
        st.markdown("</div>", unsafe_allow_html=True)

    # Tab 2 for  Analytics
    with tab_analytics:
        #
        st.markdown("<h3>System Analytics</h3>", unsafe_allow_html=True)
        # Brief description in a paragraph tag
        st.markdown("<p>Read-only insights into diseases, symptoms, and severity.</p>", unsafe_allow_html=True)

        
        st.markdown("<h4>Most Common Diseases</h4>", unsafe_allow_html=True)
        # Fetch the top 10 diseases by prevalence; drop any duplicate rows
        df_diseases = analytics_ctrl.disease_prevalence(top_n=10).drop_duplicates()
        # Render the DataFrame in a scrollable, resizable table
        st.dataframe(df_diseases, use_container_width=True)

        # Repeat the pattern for symptoms
        st.markdown("<h4>Most Common Symptoms</h4>", unsafe_allow_html=True)
        df_symptoms = analytics_ctrl.symptom_prevalence(top_n=10).drop_duplicates()
        st.dataframe(df_symptoms, use_container_width=True)

        # Explain in another sub-heading
        st.markdown("<h4>Severity Level Distribution</h4>", unsafe_allow_html=True)
        # Get the distribution and remove any duplicates
        df_severity = analytics_ctrl.severity_distribution().drop_duplicates()
        
        # Set the ‘Severity Level’ column as the index so the bar chart labels correctly
        st.bar_chart(df_severity.set_index("Severity Level"))






