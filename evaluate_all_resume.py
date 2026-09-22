from evaluate_resume import evaluate_resume
import pandas as pd
import pickle

with open("resume_metadata.pkl", "rb") as f:
    resume_data = pickle.load(f)

#Compare all resume
def get_resumes_for_job(
    job_id
):

    resume_ids = list(
        dict.fromkeys(
            item["unique_id"]
            for item in resume_data
            if item["job_id"] == job_id
        )
    )

    return resume_ids


#job_id = evaluate_resume.get_job_id_by_title("Job Title", evaluate_resume.job_data)



def compare_resumes_for_job(
    job_id
):

    resume_ids = get_resumes_for_job(
            job_id)

    all_results = []

    for resume_id in resume_ids:

        result = evaluate_resume(
            job_id,
            resume_id
        )

        all_results.append(
            {
                "resume_id":
                    resume_id,

                "match_score":
                    result[
                        "match_score"
                    ],

                "matching_skills":
                    result[
                        "matching_skills"
                    ],

                "missing_skills":
                    result[
                        "missing_skills"
                    ],

                "recommendation":
                    result[
                        "hiring_recommendation"
                    ],

                "candidate_summary":
                    result[
                        "candidate_summary"
                    ],

                "strengths":
                    result[
                        "strengths"
                    ],

                "weaknesses":
                    result[
                        "weaknesses"
                    ],

                "justification":
                    result[
                        "justification"
                    ]
            }
        )

    results_df = pd.DataFrame(
            all_results)

    return results_df