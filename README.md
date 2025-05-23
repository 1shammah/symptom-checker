AI-Powered Symptom Checker (MVP)

This project is a locally-run, AI-based symptom checker designed to recommend possible diseases based on user-inputted symptoms. The system is intended for offline use and aims to improve healthcare accessibility by allowing users to perform symptom checks without requiring an internet connection.

Features:
- Multi-page Streamlit user interface
- AI recommendation engine using TF-IDF and Cosine Similarity
- Secure user authentication with bcrypt password hashing
- Role-based access control (User and Admin)
- Local SQLite database with no cloud dependency
- Analytics dashboard for admins

Setup Instructions:

1. Clone the repository
2. Navigate into the project directory
3. Create a virtual environment:
   python -m venv venv
4. Activate the environment:
   - On Windows: venv\Scripts\activate
   - On Mac/Linux: source venv/bin/activate
5. Install dependencies:
   pip install -r requirements.txt
6. Run the app:
   streamlit run app.py

By default, the app loads a fresh database when run with reset=True. To preserve your data, set reset=False after initialisation.

This application is intended for educational and demonstration purposes. It does not provide clinical diagnoses or store sensitive health data.
