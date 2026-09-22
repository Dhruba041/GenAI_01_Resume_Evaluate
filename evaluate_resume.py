#Evaluate Each Resume
from langchain_core.output_parsers import JsonOutputParser
import pickle

from llm import llm
from evaluation_prompt import evaluation_prompt

evaluation_chain = (
    evaluation_prompt
    | llm
    | JsonOutputParser()
)

with open("job_desc.pkl", "rb") as f:
    job_data = pickle.load(f)
#Load Resume
with open("resume_metadata.pkl", "rb") as f:
    resume_data = pickle.load(f)

def get_job_id_by_title(job_title, job_data):
    for job in job_data:
        if job.get("title", "").strip().lower() == job_title.strip().lower():
            return job.get("job_id")

    return None

#Function to map a FAISS result back to its original chunk
def get_job_chunk(
    index_position
):

    return job_data[
        index_position
    ]

#Function to map resume FAISS result back to its original chunk
def get_resume_chunk(
    index_position
):

    return resume_data[
        index_position
    ]

#Retrive Job Description chunks
def get_job_context(
    job_id
):

    selected_chunks = [
        item
        for item in job_data
        if item["job_id"] == job_id
    ]

    selected_chunks = sorted(
        selected_chunks,
        key=lambda x: x["chunk_id"]
    )

    context = "\n\n".join(
        item["text"]
        for item in selected_chunks
    )

    return context

#Retrive Resume Chunks
def get_resume_context(
    unique_id
):

    selected_chunks = [
        item
        for item in resume_data
        if item["unique_id"] == unique_id
    ]

    selected_chunks = sorted(
        selected_chunks,
        key=lambda x: x["chunk_id"]
    )

    context = "\n\n".join(
        item["text"]
        for item in selected_chunks
    )

    return context

#Fetch resume unique ID based on Job ID and Resume Name
def get_unique_id_by_job_and_resume(job_id, resume_file, resume_data):
    for resume in resume_data:
        if (
            resume.get("job_id") == job_id
            and resume.get("resume_file", "").strip().lower() == resume_file.strip().lower()
        ):
            return resume.get("unique_id")

    return None


def evaluate_resume(job_id, unique_id):

    job_context = get_job_context(job_id)

    resume_context = get_resume_context(unique_id)

    result = evaluation_chain.invoke({
        "job_context": job_context,
        "resume_context": resume_context
    })

    return result
