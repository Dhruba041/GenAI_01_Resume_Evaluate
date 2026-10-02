from langchain.agents import create_agent
from llm_gpt import llm


VALID_INTENTS = {
    "UPLOAD_JD",
    "UPLOAD_RESUME",
    "EVALUATE_RESUME",
    "VIEW_RESULTS",
    "INVALID_INTENT",
}


def detect_intent(user_message: str) -> str:

    agent = create_agent(
        model=llm,
        system_prompt="""
        You are a routing assistant for an AI recruitment application.

        Determine the user's intent.

        You MUST return exactly ONE of these values:

        UPLOAD_JD
        UPLOAD_RESUME
        EVALUATE_RESUME
        VIEW_RESULTS
        INVALID_INTENT

        Rules:

        - User wants to upload a Job Description:
        UPLOAD_JD

        - User wants to upload a resume, CV, or candidate resume:
        UPLOAD_RESUME

        - User wants to compare/evaluate/match resumes against a JD:
        EVALUATE_RESUME

        - User wants to see candidate evaluation/results:
        VIEW_RESULTS

        - If the request does not match any of the above:
        INVALID_INTENT

        Examples:

        "I want to upload a job description"
        UPLOAD_JD

        "Upload my JD"
        UPLOAD_JD

        "I want to upload a resume"
        UPLOAD_RESUME

        "Upload candidate CV"
        UPLOAD_RESUME

        "Compare the candidates"
        EVALUATE_RESUME

        "Evaluate these resumes"
        EVALUATE_RESUME

        "Show me the results"
        VIEW_RESULTS

        Do not explain your answer.
        Return ONLY the intent value.
    """
    )

    # IMPORTANT:
    # create_agent expects a state dictionary.
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message,
                }
            ]
        }
    )

    # LangGraph returns the agent state.
    messages = response.get("messages", [])

    if not messages:
        return "INVALID_INTENT"

    # Last message is the agent's response.
    content = messages[-1].content

    # Normalize model output.
    intent = content.strip().upper()

    # Handle accidental formatting such as:
    # "UPLOAD_RESUME."
    # "`UPLOAD_RESUME`"
    # "upload resume"
    intent = intent.replace("`", "")
    intent = intent.replace(".", "")
    intent = intent.strip()

    # Handle common natural-language outputs.
    if intent in VALID_INTENTS:
        return intent

    if intent in {
        "UPLOAD RESUME",
        "UPLOAD CV",
        "UPLOAD CANDIDATE RESUME",
    }:
        return "UPLOAD_RESUME"

    if intent in {
        "UPLOAD JD",
        "UPLOAD JOB DESCRIPTION",
        "UPLOAD JOB DESCRIPTION PDF",
    }:
        return "UPLOAD_JD"

    if intent in {
        "EVALUATE RESUME",
        "EVALUATE RESUMES",
        "COMPARE CANDIDATES",
        "COMPARE RESUMES",
    }:
        return "EVALUATE_RESUME"

    if intent in {
        "VIEW RESULTS",
        "SHOW RESULTS",
        "SHOW EVALUATION",
    }:
        return "VIEW_RESULTS"

    return "INVALID_INTENT"
