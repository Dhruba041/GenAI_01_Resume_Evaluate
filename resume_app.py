import streamlit as st
import pymupdf
import faiss
import pickle
import numpy as np
import uuid
import os

from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings



# STREAMLIT


st.set_page_config(
    page_title="Resume Uploader",
    page_icon="📄",
    layout="centered"
)


# BACKGROUND

st.markdown(
    """
    <style>

    /* Main application background */
    .stApp {
        background-color: #dbeafe;
    }

    /* Main content area */
    .main {
        background-color: #dbeafe;
    }

    /* Title */
    h1 {
        color: #0f172a;
    }

    /* Labels */
    label {
        color: #0f172a !important;
    }

    /* Text input */
    input {
        background-color: white !important;
        color: #0f172a !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #bfdbfe;
        border-radius: 10px;
        padding: 10px;
    }

    /* Button */
    .stButton > button {
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }

    .stButton > button:hover {
        background-color: #1d4ed8;
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    '<h1 style="color:brown;">Resume Uploader</h1>',
    unsafe_allow_html=True
)


# EMBEDDING MODEL

model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

# FILES
path = "/mount/src/genai_01_resume_evaluate"

#FAISS_FILE = "resume.faiss"
#METADATA_FILE = "resume_metadata.pkl"

BASE_PATH = "/mount/src/genai_01_resume_evaluate"

FAISS_FILE = os.path.join(BASE_PATH, "resume.faiss")
METADATA_FILE = os.path.join(BASE_PATH, "resume_metadata.pkl")

# LOAD JOB DESCRIPTIONS

with open(
    "job_desc.pkl",
    "rb"
) as f:

    jobs = pickle.load(f)


# SELECT JOB DESCRIPTION

#job_titles = [
#    job["title"]
#    for job in jobs
#]

#selected_title = st.selectbox(
#    "Select Job Description",
#    job_titles
#)

# Get distinct job titles
#above code displyed multiple values of job title based on number of chunks
job_titles = list(dict.fromkeys(
    job["title"]
    for job in jobs
))

selected_title = st.selectbox(
    "Select Job Description",
    job_titles
)


selected_job = next(
    job
    for job in jobs
    if job["title"] == selected_title
)

job_id = selected_job["job_id"]

# UPLOAD RESUME

resume = st.file_uploader(
    "Upload Resume",
    type="pdf"
)


# SAVE RESUME

if resume:

    if st.button("Save Resume"):

        # GENERATE UNIQUE ID
        resume_id = str(
            uuid.uuid4()
        )

        unique_id = (
            f"{job_id}_{resume_id}"
        )

        # EXTRACT PDF TEXT USING PYMuPDF

        pdf_bytes = resume.read()

        pdf = pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        text = ""

        for page in pdf:

            text += page.get_text()


        pdf.close()


        if not text.strip():

            st.error(
                "Could not extract text from resume."
            )

            st.stop()

        # CHUNK RESUME

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = splitter.split_text(
            text
        )


        if not chunks:

            st.error(
                "No text chunks were created."
            )

            st.stop()

        # CREATE EMBEDDINGS

        #embeddings = model.encode(
        #    chunks,
        #    convert_to_numpy=True
        #)
        embeddings = model.embed_documents(
                chunks
        )

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        # LOAD / CREATE FAISS INDEX

        if os.path.exists(
            FAISS_FILE
        ):

            index = faiss.read_index(
                FAISS_FILE
            )

            # Check embedding dimensions
            if index.d != embeddings.shape[1]:

                st.error(
                    "Embedding dimension does not match "
                    "the existing FAISS index."
                )

                st.stop()

        else:

            index = faiss.IndexFlatL2(
                embeddings.shape[1]
            )

        # ADD EMBEDDINGS TO FAISS

        index.add(
            embeddings
        )

        # SAVE FAISS INDEX

        faiss.write_index(
            index,
            FAISS_FILE
        )

        # LOAD EXISTING METADATA

        if os.path.exists(
            METADATA_FILE
        ):

            with open(
                METADATA_FILE,
                "rb"
            ) as f:

                metadata = pickle.load(
                    f
                )

        else:

            metadata = []


        # SAVE CHUNK + EMBEDDING + METADATA

        for i, chunk in enumerate(chunks):

            metadata.append(
                {
                    "unique_id":
                        unique_id,

                    "job_id":
                        job_id,

                    "job_title":
                        selected_title,

                    "resume_id":
                        resume_id,

                    "resume_file":
                        resume.name,

                    "chunk_id":
                        i,

                    "text":
                        chunk,

                    "embedding":
                        embeddings[i].tolist()
                }
            )

        # SAVE METADATA

        with open(
            METADATA_FILE,
            "wb"
        ) as f:

            pickle.dump(
                metadata,
                f
            )

        # SUCCESS

        #st.success(
        #    "Resume successfully saved!"
        #)
        st.markdown(
            '<p style="color:brown; font-weight:bold;">'
            'Resume successfully saved!'
            '</p>',
            unsafe_allow_html=True
        )
