import streamlit as st



# PAGE CONFIG


st.set_page_config(
    page_title="Resume AI Assistant",
    page_icon="🤖",
    layout="wide"
)



# DEFINE PAGES


pages = {
    "home": st.Page(
        "app_gpt.py",
        title="AI Assistant",
        icon="🤖"
    ),

    "jd": st.Page(
        "pages/jd.py",
        title="Job Description",
        icon="📋"
    ),

    "resume": st.Page(
        "pages/resume.py",
        title="Resume Upload",
        icon="📄"
    ),

    "evaluate": st.Page(
        "pages/evaluate_all_resume.py",
        title="Evaluate Resumes",
        icon="🔍"
    ),

    "results": st.Page(
        "pages/view_results.py",
        title="Results",
        icon="📊"
    )
}



# MAKE PAGES AVAILABLE TO OTHER FILES


st.session_state["pages"] = pages



# NAVIGATION


pg = st.navigation(
    list(pages.values())
)



# RUN CURRENT PAGE


pg.run()
