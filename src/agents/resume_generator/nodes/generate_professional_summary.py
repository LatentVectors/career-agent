"""Generate professional summary node for resume generation."""

from __future__ import annotations

from langgraph.runtime import Runtime

from src.context import AgentContext
from src.logging_config import logger
from src.models import OpenAIModels, get_model

from ..state import InternalState, PartialInternalState


def generate_professional_summary(
    state: InternalState, runtime: Runtime[AgentContext]
) -> PartialInternalState:
    """Create professional summary from experiences and responses.

    Args:
        state: Current state containing experience_data, responses_data, and job_title

    Returns:
        Updated state with generated professional summary
    """
    logger.debug("NODE: resume_generator.generate_professional_summary")
    experience_data = state.experience_data or []
    responses_data = state.responses_data or []
    job_title = state.job_title
    job_description = state.job_description

    logger.debug(f"Generating professional summary for job title: {job_title}")

    if not experience_data and not responses_data:
        logger.warning("No experience or response data available for summary generation")
        return {"resume_data": {"professional_summary": ""}}

    # Prepare content for summary generation
    experience_summary = "\n".join(
        [
            f"• {exp.title} at {exp.company} ({exp.start_date} - {exp.end_date or 'Present'}): {exp.content[:200]}..."
            for exp in experience_data[:3]  # Use top 3 most recent experiences
        ]
    )

    response_summary = "\n".join(
        [
            f"• {resp.prompt[:100]}...: {resp.response[:200]}..."
            for resp in responses_data[:2]  # Use top 2 most relevant responses
        ]
    )

    combined_content = f"Target Job Title: {job_title}\n\nJob Description:\n{job_description}\n\n"
    if experience_summary:
        combined_content += f"Key Experiences:\n{experience_summary}\n\n"
    if response_summary:
        combined_content += f"Key Responses:\n{response_summary}"

    # Create prompt for professional summary
    prompt = f"""
    Create a compelling professional summary for a resume targeting a {job_title} position.
    
    Content to consider:
    {combined_content}
    
    Guidelines:
    - Write 2-3 sentences that highlight key qualifications and career objectives
    - Focus on relevant experience and skills for {job_title} position
    - Align with the job description where truthful (do not fabricate)
    - Use professional tone and action-oriented language
    - Include years of experience if applicable
    - Mention key achievements or specializations
    - Keep it concise but impactful
    
    Return only the professional summary text, no additional formatting.
    """

    try:
        llm = get_model(OpenAIModels.gpt_4o_mini)
        response = llm.invoke(prompt)

        # Clean up the response
        summary = response.content.strip()

        # Remove any extra formatting or quotes
        if summary.startswith('"') and summary.endswith('"'):
            summary = summary[1:-1]
        if summary.startswith("'") and summary.endswith("'"):
            summary = summary[1:-1]

        logger.debug(f"Generated professional summary: {len(summary)} characters")

        return {"resume_data": {"professional_summary": summary}}

    except Exception as e:
        logger.exception(f"Error generating professional summary: {e}")
        # Return empty summary on error
        return {"resume_data": {"professional_summary": ""}}
