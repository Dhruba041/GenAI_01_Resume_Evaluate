import streamlit as st
import pickle
import pandas as pd

#This will read results from pickle file and display it in a table format

with open("job_result.pkl", "rb") as f:
    job_result_df = pickle.load(f)

with open("resume_metadata.pkl", "rb") as f:
    resume_data = pickle.load(f)


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

    job_results = job_result_df[job_result_df["job_id"] == job_id]

    resume_metadata_df = pd.DataFrame(resume_data)

    resume_metadata_df = resume_metadata_df[
    ["unique_id", "resume_file"]].drop_duplicates(subset=["unique_id"])

    resume_metadata_df = resume_metadata_df.rename(
        columns={
            "unique_id": "resume_id"
        }
    )

    job_results = resume_metadata_df.merge(
        job_results,
        on="resume_id",
        how="left"
        )


    columns_to_drop = job_results.columns[[0,2]]
    job_results = job_results.drop(
            columns=columns_to_drop
        )


    if job_results.empty:
        st.warning(
            "No results found for the selected job description."
        )
    else:
        st.dataframe(
                    job_results,
                    use_container_width=True,
                    hide_index=True
                )