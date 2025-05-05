# views/symptoms_view.py

import streamlit as st
from controllers.symptom_controller import SymptomController
from controllers.recommender_controller import RecommenderController
from views.common_view import render_sidebar

def show_symptom_checker_view(
    navigate_to,
    symptom_ctrl: SymptomController,
    recommender_ctrl: RecommenderController
):
    """
    Symptom Checker UI:
      • Step 1: Pick symptoms via a searchable dropdown (autocomplete).
      • Step 2: See your selected symptoms listed clearly.
      • Step 3: Click "Find Possible Diseases" to run the AI model.
      • Step 4: View results, with:
          – Symptoms deduplicated and displayed without underscores.
          – Severity explained on a 1–6 scale.
          – Match score shown as a percentage.
          – Recommended precautions.
    """
    # Draw the shared sidebar (navigation)
    render_sidebar(navigate_to)

    # Page header
    st.title("Symptom Checker")

    # 1) Beginner-friendly “How it works” panel, now explaining severity scale too:
    st.markdown("""
<div style="background-color:#e7f3fe; border-left:4px solid #2196F3; padding:10px; margin-bottom:1rem;">
  <h3>How it works:</h3>
  <ol>
    <li>Select one or more symptoms you’re experiencing from the dropdown below (type to filter).</li>
    <li><em>Severity scale:</em> 1 = mild, 6 = severe.</li>
    <li>Click <strong>Find Possible Diseases</strong> to run the AI model.</li>
    <li>Review possible diseases with match %, symptom severities, descriptions, and precautions.</li>
  </ol>
</div>
""", unsafe_allow_html=True)

    # 2) Load symptoms from the controller and prepare a mapping:
    all_symptoms = symptom_ctrl.list_all_symptoms()  # returns Symptom objects
    # Map internal names ("head_ache") → user-friendly labels ("Head Ache")
    symptom_map = {
        s.name: s.name.replace("_", " ").title()
        for s in all_symptoms
    }
    ui_labels   = list(symptom_map.values())
    # Reverse map for sending back to the recommender
    inverse_map = {label: key for key, label in symptom_map.items()}

    # 3) Symptom-selection form
    with st.form("symptom_form"):
        # placeholder makes it clear you can type to filter
        selected_ui = st.multiselect(
            "Choose your symptoms",
            options=ui_labels,
            placeholder="Type to filter symptoms…",
            help="Start typing a symptom name to narrow the list"
        )

        # show the selected symptoms under the dropdown
        if selected_ui:
            st.markdown("<strong>Selected Symptoms:</strong>", unsafe_allow_html=True)
            st.write(", ".join(selected_ui))

        submitted = st.form_submit_button("Find Possible Diseases")
        if submitted:
            if not selected_ui:
                st.error("Please select at least one symptom.")
            else:
                # Run the AI recommendation model
                with st.spinner("Finding matching diseases…"):
                    # Map back to internal symptom keys
                    selected_internal = [inverse_map[label] for label in selected_ui]
                    recs = recommender_ctrl.recommend_with_details(
                        selected_internal,
                        top_n=5
                    )
                    # Store for display below
                    st.session_state.recommendations = recs

    # Render results if available
    recommendations = st.session_state.get("recommendations")
    if recommendations is not None:
        if not recommendations:
            st.warning("No diseases found for those symptoms.")
        else:
            st.subheader("Possible Diseases")
            for rec in recommendations:
                disease     = rec["disease"]
                # convert match results from decimal to percentage
                pct_match   = f"{rec['score'] * 100:.0f}%"
                symptoms    = rec["symptoms"]
                precautions = rec.get("precautions", [])

                # Each disease in an expander
                with st.expander(f"{disease} (match: {pct_match})", expanded=False):
                    st.markdown("<strong>Associated Symptoms:</strong>", unsafe_allow_html=True)
                    # deduplicate symptoms with set()
                    for sym in sorted(set(symptoms)):
                        # severity comes from 1 to 6, explained above
                        sev  = symptom_ctrl.get_severity(sym)
                        desc = symptom_ctrl.get_description(sym)
                        # show label without underscores
                        label = sym.replace("_", " ").title()
                        line = f"- {label}: severity {sev}"
                        if desc:
                            line += f"; {desc}"
                        st.write(line)

                    st.markdown("<strong>Recommended Precautions:</strong>", unsafe_allow_html=True)
                    if precautions:
                        for p in precautions:
                            st.write(f"- {p}")
                    else:
                        st.write("_No specific precautions found._")
