#screen to upload files and respond to queries
import streamlit as st
from detect_intent import detect_intent
from llm_gpt import llm
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv() 
st.set_page_config(
    page_title="Resume AI Assistant",
    page_icon="🤖",
    layout="wide"
)

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]


if "OPENAI_API_KEY" not in st.secrets:

    st.error(
        "OpenAI API key is not configured. "
        "Please add OPENAI_API_KEY to Streamlit secrets."
    )

    st.stop()

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

# Custom CSS

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #00FFFF;
    }

    /* Assistant message */
    div[data-testid="stChatMessage"]:has(
        div[data-testid="stChatMessageAvatarAssistant"]
    ) {
        background-color: #00FFFF;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
    }

    /* Assistant text */
    div[data-testid="stChatMessage"]:has(
        div[data-testid="stChatMessageAvatarAssistant"]
    ) div[data-testid="stMarkdownContainer"] {
        color: #6B3E26 !important;
    }

    /* User message */
    div[data-testid="stChatMessage"]:has(
        div[data-testid="stChatMessageAvatarUser"]
    ) {
        background-color: #FFF3B0;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
    }

    /* User text */
    div[data-testid="stChatMessage"]:has(
        div[data-testid="stChatMessageAvatarUser"]
    ) div[data-testid="stMarkdownContainer"] {
        color: #003366 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #7CFC00;
    }

    /* Spinner */
    .stSpinner > div {
        color: #003366 !important;
    }

    .stSpinner svg {
        stroke: #003366 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)



# Session State Initialization

if "messages" not in st.session_state:
    st.session_state.messages = []

if "greeting_shown" not in st.session_state:
    st.session_state.greeting_shown = False

if "session_active" not in st.session_state:
    st.session_state.session_active = True

# Initial Greeting


if not st.session_state.greeting_shown:

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 Welcome to the Resume AI Assistant.\n\n"
                "I can help you with Job Description Upload, Resume Upload against Job and Resume Analysis\n\n"
                "Please Resume Upload, Job Description Upload, Resume Analysis as your choice.\n\n"
                "This assistant does not provide personal job recommendations.\n\n"
                "Please enter your choice below."
            )
        }
    )

    st.session_state.greeting_shown = True

# Display Chat History

for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]

    if role == "user":

        with st.chat_message("user"):

            st.markdown(
                f'<div style="color:#003366;">{content}</div>',
                unsafe_allow_html=True
            )

    elif role == "assistant":

        with st.chat_message("assistant"):

            st.markdown(
                f'<div style="color:#6B3E26;">{content}</div>',
                unsafe_allow_html=True
            )

# Chat Input

user_input = st.chat_input(
    "Ask Upload Job Description or Upload Resume or Evaluate Resume against Job"
    "Type 'clear' to clear chat or 'exit' to exit.",
    disabled=not st.session_state.session_active
)


# Process Chat Input

if user_input and st.session_state.session_active:
    command = user_input.strip().lower()
    if command == "exit":
        st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": user_input
                    }
                )
        st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": (
                            "Goodbye! 👋\n\n"
                            "Thank you for using the Resume AI Assistant.\n\n"
                            "This session is now inactive.\n\n"
                            "Please close the browser or refresh the page "
                            "to start a new session.\n\n"
                            "Have a great day!"
                        )
                    }
                )
        
               
        st.session_state.session_active = False
        
        st.rerun()

    else:
        intent_response = detect_intent(user_input)
        if intent_response == 'UPLOAD_JD':
            st.session_state["navigation_message"] = (
            "Taking you to the Job Description upload page..."
            )
            st.switch_page(
            "pages/jd_app.py"
            )
        elif  intent_response == 'UPLOAD_RESUME':
            st.session_state["navigation_message"] = (
            "Taking you to the Resume upload page..."
            )
            st.switch_page(
            "pages/resume_app.py"
            )
        elif intent_response == "EVALUATE_RESUME":
            st.session_state["navigation_message"] = (
            "Taking you to the Resume evaluation page..."
            )
            st.switch_page(
            "pages/evaluate_all_resume.py"
            )
        elif intent_response == "VIEW_RESULTS":
            st.session_state["navigation_message"] = (
            "Taking you to the Results page..."
            )
            st.switch_page(
            "pages/app_job_results.py"
            )


