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
          – Severity explained on a 1–7 scale.
          – Match score shown as a percentage.
          – Descriptive rationale naming matched symptom(s).
          – How many of your symptoms and how many of the disease’s symptoms matched.
          – Recommended precautions.
    """

    # ─── Sidebar & Title ───────────────────────────────────────────────────────
    render_sidebar(navigate_to)
    st.title("Symptom Checker")

    # ─── “How it works” Instruction Panel ─────────────────────────────────────
    st.markdown("""
<div style="background-color:#e7f3fe; border-left:4px solid #2196F3; padding:10px; margin-bottom:1rem;">
  <h3>How it works:</h3>
  <ol>
    <li>Select one or more symptoms you’re experiencing from the dropdown below (type to filter).</li>
    <li><em>Severity scale:</em> 1 = mild, 7 = most severe.</li>
    <li>Click <strong>Find Possible Diseases</strong> to run the AI model.</li>
    <li>Review possible diseases with:
      <ul>
        <li>Match percentage (AI-weighted)</li>
        <li>Rationale naming which symptom(s) drove the match</li>
        <li>Count-based match rates for your symptoms and for each disease’s full symptom list</li>
        <li>Symptom severities & descriptions</li>
        <li>Recommended precautions</li>
      </ul>
    </li>
  </ol>
</div>
""", unsafe_allow_html=True)

    # Prepare Symptom List 
    all_symptoms = symptom_ctrl.list_all_symptoms()
    symptom_map = {
        s.name: s.name.replace("_", " ").title()
        for s in all_symptoms
    }
    ui_labels   = list(symptom_map.values())
    inverse_map = {label: key for key, label in symptom_map.items()}

    # Symptom Selection Form
    with st.form("symptom_form"):
        selected_ui = st.multiselect(
            "Choose your symptoms",
            options=ui_labels,
            placeholder="Type to filter symptoms…",
            help="Start typing a symptom name to narrow the list"
        )
        if selected_ui:
            st.markdown("<strong>Selected Symptoms:</strong>", unsafe_allow_html=True)
            st.write(", ".join(selected_ui))

        submitted = st.form_submit_button("Find Possible Diseases")
        if submitted:
            if not selected_ui:
                st.error("Please select at least one symptom.")
            else:
                with st.spinner("Finding matching diseases…"):
                    selected_internal = [inverse_map[label] for label in selected_ui]
                    recs = recommender_ctrl.recommend_with_details(
                        selected_internal,
                        top_n=5
                    )
                    st.session_state.recommendations   = recs
                    st.session_state.selected_internal = selected_internal

    # Render Recommendations
    recommendations   = st.session_state.get("recommendations")
    selected_internal = st.session_state.get("selected_internal", [])

    if recommendations is not None:
        if not recommendations:
            st.warning("No diseases found for those symptoms.")
        else:
            st.subheader("Possible Diseases")
            for rec in recommendations:
                disease     = rec["disease"]
                pct_match   = f"{rec['score'] * 100:.0f}%"
                symptoms    = rec["symptoms"]
                precautions = rec.get("precautions", [])

                # Changed "match" to "confidence" for layperson clarity
                with st.expander(f"{disease} (confidence: {pct_match})", expanded=False):
                    # Determine which user symptoms matched
                    matched = set(symptoms).intersection(selected_internal)
                    count_matched    = len(matched)
                    total_selected   = len(selected_internal)

                    # Deduplicate the disease’s symptom list before counting
                    unique_disease_symptoms = set(symptoms)
                    total_disease    = len(unique_disease_symptoms)

                    # Simple count-based percentages
                    count_pct_user    = f"{(count_matched/total_selected*100):.0f}%"
                    count_pct_disease = f"{(count_matched/total_disease*100):.0f}%"

                    # Convert keys to user-friendly labels
                    matched_labels = [s.replace("_", " ").title() for s in matched]
                    if matched_labels:
                        # Build label string: "A", or "A and B", or "A, B and C"
                        if len(matched_labels) == 1:
                            symptom_text = matched_labels[0]
                        else:
                            symptom_text = ", ".join(matched_labels[:-1]) + " and " + matched_labels[-1]

                        # Lay-friendly confidence statement
                        st.markdown(
                            f"<em>You reported <strong>{symptom_text}</strong>. "
                            f"Our system is <strong>{pct_match}</strong> confident this indicates <strong>{disease}</strong>.</em>",
                            unsafe_allow_html=True
                        )
                        # Lay-friendly count reassurance
                        st.markdown(
                            f"<em>All {count_matched} of your {total_selected} selected symptoms match "
                            f"the typical indicators for {disease}, which is known to present with "
                            f"{total_disease} symptoms.</em>",
                            unsafe_allow_html=True
                        )

                    # List all associated symptoms with severity & descriptions
                    st.markdown("<strong>Associated Symptoms:</strong>", unsafe_allow_html=True)
                    for sym in sorted(unique_disease_symptoms):
                        sev  = symptom_ctrl.get_severity(sym)
                        desc = symptom_ctrl.get_description(sym)
                        label = sym.replace("_", " ").title()
                        line  = f"- {label}: severity {sev}"
                        if desc:
                            line += f"; {desc}"
                        st.write(line)

                    # List recommended precautions
                    st.markdown("<strong>Recommended Precautions:</strong>", unsafe_allow_html=True)
                    if precautions:
                        for p in precautions:
                            st.write(f"- {p}")
                    else:
                        st.write("_No specific precautions found._")
