# STREAMLIT FRONT END - JOB DESCRIPTION UPLOADER
import streamlit as st
import pickle
import uuid
import numpy as np
import os
import pymupdf #replaced fitz with pymupdf
import faiss

from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

#from langchain_community.document_loaders import PyPDFLoader
#from langchain_community.vectorstores import FAISS
#As langchain_community is getting sunset



# STREAMLIT

st.set_page_config(
    page_title="Job Description Uploader",
    page_icon="📄",
    layout="centered"
)


# BLUE BACKGROUND

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
    '<h1 style="color:brown;">Job Description Uploader</h1>',
    unsafe_allow_html=True
)

#st.title("Job Description Uploader")



# FILES


FAISS_FILE = "jobs.faiss"
METADATA_FILE = "job_desc.pkl"



# EMBEDDING MODEL


#model = SentenceTransformer(
#    "all-MiniLM-L6-v2"
#)

model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

# UPLOAD PDF


file = st.file_uploader(
    "Upload Job Description",
    type="pdf"
)


if file:

    
    # JOB TITLE
    

    title = st.text_input(
        "Job Title"
    )


    
    # SAVE
    

    if st.button("Save Job Description"):

        
        # Validate title
        

        if not title.strip():

            st.error(
                "Please enter a job title."
            )

            st.stop()


        
        # 1. SAVE UPLOADED PDF TEMPORARILY
        

        temp_file = "temp_job_description.pdf"

        try:

            with open(
                temp_file,
                "wb"
            ) as f:

                f.write(
                    file.getbuffer()
                )

        except Exception as e:

            st.error(
                f"Could not save uploaded PDF: {e}"
            )

            st.stop()


        
        # 2. LOAD PDF USING PyMuPDF
        

        try:

            pdf = pymupdf.open(
                temp_file
            )

            pages = []

            for page_number, page in enumerate(pdf):

                page_text = page.get_text()

                if page_text.strip():

                    pages.append(
                        page_text
                    )

            pdf.close()

        except Exception as e:

            st.error(
                f"Could not read PDF: {e}"
            )

            if os.path.exists(temp_file):

                os.remove(
                    temp_file
                )

            st.stop()


        
        # 3. EXTRACT TEXT
        

        text = "\n\n".join(
            pages
        )


        if not text.strip():

            st.error(
                "Could not extract text from PDF."
            )

            if os.path.exists(temp_file):

                os.remove(
                    temp_file
                )

            st.stop()


        
        # 4. CHUNK JOB DESCRIPTION
        

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = splitter.split_text(
            text
        )


        if not chunks:

            st.error(
                "No chunks were created."
            )

            if os.path.exists(temp_file):

                os.remove(
                    temp_file
                )

            st.stop()


        
        # 5. CREATE EMBEDDINGS
        

        try:

            embeddings = model.embed_documents(
                chunks
            )

            embeddings = np.asarray(
                embeddings,
                dtype="float32"
            )

        except Exception as e:

            st.error(
                f"Could not create embeddings: {e}"
            )

            if os.path.exists(temp_file):

                os.remove(
                    temp_file
                )

            st.stop()


        
        # 6. NORMALIZE EMBEDDINGS
        

        faiss.normalize_L2(
            embeddings
        )


        
        # 7. CREATE / LOAD FAISS INDEX
        

        if os.path.exists(
            FAISS_FILE
        ):

            try:

                index = faiss.read_index(
                    FAISS_FILE
                )

            except Exception as e:

                st.error(
                    f"Could not load FAISS index: {e}"
                )

                if os.path.exists(temp_file):

                    os.remove(
                        temp_file
                    )

                st.stop()


            
            # Check embedding dimension
            

            if index.d != embeddings.shape[1]:

                st.error(
                    "Embedding dimension does not match "
                    "the existing FAISS index."
                )

                if os.path.exists(temp_file):

                    os.remove(
                        temp_file
                    )

                st.stop()

        else:

            
            # Create a new FAISS index
            

            dimension = embeddings.shape[1]

            index = faiss.IndexFlatIP(
                dimension
            )


        
        # 8. ADD EMBEDDINGS TO FAISS
        

        start_index = index.ntotal

        index.add(
            embeddings
        )


        
        # 9. SAVE FAISS INDEX
        

        try:

            faiss.write_index(
                index,
                FAISS_FILE
            )

        except Exception as e:

            st.error(
                f"Could not save FAISS index: {e}"
            )

            if os.path.exists(temp_file):

                os.remove(
                    temp_file
                )

            st.stop()


        
        # 10. CREATE JOB ID
        

        job_id = str(
            uuid.uuid4()
        )


        
        # 11. LOAD EXISTING METADATA
        

        if os.path.exists(
            METADATA_FILE
        ):

            try:

                with open(
                    METADATA_FILE,
                    "rb"
                ) as f:

                    job_metadata = pickle.load(
                        f
                    )

            except Exception as e:

                st.error(
                    f"Could not load metadata: {e}"
                )

                if os.path.exists(temp_file):

                    os.remove(
                        temp_file
                    )

                st.stop()

        else:

            job_metadata = []


        
        # 12. SAVE CHUNKS + METADATA
        

        for i, chunk in enumerate(
            chunks
        ):

            job_metadata.append(
                {
                    "job_id": job_id,

                    "title": title,

                    "job_file": file.name,

                    "chunk_id": i,

                    # Global position of this vector
                    # inside the FAISS index
                    "faiss_index": start_index + i,

                    "text": chunk
                }
            )


        
        # 13. SAVE METADATA
        

        try:

            with open(
                METADATA_FILE,
                "wb"
            ) as f:

                pickle.dump(
                    job_metadata,
                    f
                )

        except Exception as e:

            st.error(
                f"Could not save metadata: {e}"
            )

            if os.path.exists(temp_file):

                os.remove(
                    temp_file
                )

            st.stop()


        
        # 14. DELETE TEMPORARY PDF
        

        if os.path.exists(
            temp_file
        ):

            os.remove(
                temp_file
            )


        
        # 15. SUCCESS
        

        #st.success(
        #    "Job description saved successfully!"
        #)

        #st.write(
        #    "Job ID:",
        #    job_id
        #)

        #st.write(
        #    "Title:",
        #    title
        #)

        #st.write(
        #    "Chunks:",
        #    len(chunks)
        #)
        st.markdown(
            '<p style="color:brown; font-weight:bold;">'
            'Job description saved successfully!'
            '</p>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<p style="color:brown;"><b>Job ID:</b> {job_id}</p>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<p style="color:brown;"><b>Title:</b> {title}</p>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<p style="color:brown;"><b>Chunks:</b> {len(chunks)}</p>',
            unsafe_allow_html=True
        )



        #st.write(os.getcwd())
        #st.write(os.listdir("."))
