# Although the database has functions like get_all_users(), it’s better for separation of concerns to:

# Wrap admin-related DB logic in an AdminModel

# Let it handle things like:
# - get_all_users() ✅
# - promote_user_to_admin(user_id) 🟡 (Optional feature)
# - delete_user(email or id) 🟡 (If needed for admin control panel)
# - get_all_disease_stats() (if you want an admin-only view)
