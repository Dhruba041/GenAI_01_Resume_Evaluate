import streamlit as st
import pickle
from evaluate_all_resume import compare_resumes_for_job

#Evaluate the results using LLM on run time - Slow to process

# BACKGROUND + STYLING


st.markdown(
    """
    <style>

    /* Main application background */
    .stApp {
        background-color: #dbeafe;
    }

    .main {
        background-color: #dbeafe;
    }

    /* All headings */
    h1, h2, h3, h4, h5, h6 {
        color: brown !important;
    }

    /* Labels */
    label {
        color: brown !important;
    }

    /* Normal text */
    p, span {
        color: brown;
    }

    /* Selectbox */
    div[data-baseweb="select"] {
        background-color: white !important;
    }

    div[data-baseweb="select"] * {
        color: brown !important;
    }

    /* Selectbox dropdown */
    ul[role="listbox"] {
        background-color: white !important;
    }

    ul[role="listbox"] li {
        color: brown !important;
    }

    /* --------------------------------------------------
       SUBMIT BUTTON
       -------------------------------------------------- */

    div[data-testid="stFormSubmitButton"] > button {
        background-color: #7c3aed !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 25px !important;
        font-weight: bold !important;
    }

    /* Force button text to white */
    div[data-testid="stFormSubmitButton"] > button p {
        color: white !important;
    }

    div[data-testid="stFormSubmitButton"] > button span {
        color: white !important;
    }

    /* Button hover */
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #6d28d9 !important;
        color: white !important;
    }

    div[data-testid="stFormSubmitButton"] > button:hover p {
        color: white !important;
    }

    div[data-testid="stFormSubmitButton"] > button:hover span {
        color: white !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        color: brown !important;
    }

    /* Warning */
    [data-testid="stAlert"] {
        color: brown !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)



# TITLE


st.markdown(
    '<h1 style="color:brown !important;">Result Display</h1>',
    unsafe_allow_html=True
)



# LOAD JOB DESCRIPTIONS


with open("job_desc.pkl", "rb") as f:
    jobs = pickle.load(f)


job_titles = list(dict.fromkeys(
    job["title"]
    for job in jobs
))



# JOB SELECTION + SUBMIT


with st.form("job_selection_form"):

    selected_title = st.selectbox(
        "Select Job Description",
        job_titles
    )

    submitted = st.form_submit_button(
        "Submit"
    )



# DISPLAY RESULTS ONLY AFTER SUBMIT


if submitted:

    selected_job = next(
        job
        for job in jobs
        if job["title"] == selected_title
    )

    # GET JOB ID
    job_id = selected_job["job_id"]

    # COMPARE RESUMES
    results_df = compare_resumes_for_job(job_id)


    
    # RESULTS
    

    st.markdown(
        '<h2 style="color:brown !important;">Resume Comparison Results</h2>',
        unsafe_allow_html=True
    )

    if results_df is not None and not results_df.empty:

        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No resume comparison results found for this job description."
        )