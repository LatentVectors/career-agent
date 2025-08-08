"""Extract skills node for resume generation."""

from __future__ import annotations

from langgraph.runtime import Runtime

from src.context import AgentContext
from src.logging_config import logger
from src.models import OpenAIModels, get_model

from ..state import InternalState, PartialInternalState


def extract_skills(state: InternalState, runtime: Runtime[AgentContext]) -> PartialInternalState:
    """Extract and categorize skills from experiences and responses.

    Args:
        state: Current state containing experience_data and responses_data

    Returns:
        Updated state with extracted skills
    """
    logger.debug("NODE: resume_generator.extract_skills")
    experience_data = state.experience_data or []
    responses_data = state.responses_data or []
    job_title = state.job_title
    job_description = state.job_description

    logger.debug(f"Extracting skills for job title: {job_title}")

    if not experience_data and not responses_data:
        logger.warning("No experience or response data available for skill extraction")
        return {"resume_data": None}

    # Prepare content for skill extraction
    experience_content = "\n\n".join([exp.content for exp in experience_data])
    response_content = "\n\n".join([resp.response for resp in responses_data])

    combined_content = f"Job Title: {job_title}\n\nJob Description:\n{job_description}\n\n"
    if experience_content:
        combined_content += f"Experience Content:\n{experience_content}\n\n"
    if response_content:
        combined_content += f"Response Content:\n{response_content}"

    # Create prompt for skill extraction
    prompt = f"""
    Analyze the following content and extract relevant skills for a {job_title} position.
    Focus on technical skills, soft skills, tools, technologies, and methodologies.
    
    Content:
    {combined_content}
    
    Please extract and categorize skills in the following format:
    1. Technical Skills: [list of technical skills]
    2. Tools & Technologies: [list of tools and technologies]
    3. Soft Skills: [list of soft skills]
    4. Methodologies: [list of methodologies/frameworks]
    
    Return only the categorized skills, one per line, without numbering or bullet points.
    """

    try:
        llm = get_model(OpenAIModels.gpt_4o_mini)
        response = llm.invoke(prompt)

        # Parse the response to extract skills
        skills_text = response.content.strip()
        skills_list = []

        # Extract skills from the categorized response
        for line in skills_text.split("\n"):
            line = line.strip()
            if line and not line.startswith(("1.", "2.", "3.", "4.")):
                # Remove category prefixes if present
                if ": " in line:
                    line = line.split(": ", 1)[1]
                skills_list.append(line)

        # Remove duplicates and clean up
        unique_skills = list(set([skill.strip() for skill in skills_list if skill.strip()]))

        logger.info(f"Extracted {len(unique_skills)} unique skills")

        return {"resume_data": {"skills": unique_skills}}

    except Exception as e:
        logger.exception(f"Error extracting skills: {e}")
        # Return empty skills list on error
        return {"resume_data": {"skills": []}}
