"""Optimize content node for resume generation."""

from __future__ import annotations

from langgraph.runtime import Runtime

from src.context import AgentContext
from src.features.resume.types import ResumeData
from src.logging_config import logger
from src.models import OpenAIModels, get_model

from ..state import InternalState, PartialInternalState


def optimize_content(state: InternalState, runtime: Runtime[AgentContext]) -> PartialInternalState:
    """LLM-powered content refinement with feedback.

    Args:
        state: Current state containing resume_data and optimization tracking

    Returns:
        Updated state with optimized resume data and feedback
    """
    resume_data = state.resume_data
    job_title = state.job_title
    job_description = state.job_description
    optimization_attempts = state.optimization_attempts
    page_length = state.page_length

    logger.debug("NODE: resume_generator.optimize_content")
    logger.debug(
        f"Optimizing content for job title: {job_title} (attempt {optimization_attempts + 1})"
    )

    if not resume_data:
        logger.error("No resume data available for optimization")
        return {"optimization_attempts": optimization_attempts + 1}

    try:
        # Create optimization prompt
        prompt = _create_optimization_prompt(
            resume_data, job_title, job_description, optimization_attempts + 1
        )

        llm = get_model(OpenAIModels.gpt_4o_mini)
        response = llm.invoke(prompt)

        # Parse optimization suggestions
        optimization_suggestions = _parse_optimization_response(response.content)

        # Apply optimizations to resume data
        optimized_resume_data = _apply_optimizations(resume_data, optimization_suggestions)

        # Create feedback message
        feedback = _create_optimization_feedback(
            optimization_suggestions, optimization_attempts + 1
        )

        logger.debug(f"Applied {len(optimization_suggestions)} optimizations")

        return {
            "resume_data": optimized_resume_data,
            "optimization_attempts": optimization_attempts + 1,
            "is_optimizing": True,
            "optimization_feedback": feedback,
        }

    except Exception as e:
        logger.exception(f"Error optimizing content: {e}")
        return {
            "optimization_attempts": optimization_attempts + 1,
            "is_optimizing": True,
            "optimization_feedback": f"Error during optimization: {e}",
        }


def _create_optimization_prompt(
    resume_data: ResumeData, job_title: str, job_description: str, attempt: int
) -> str:
    """Create prompt for content optimization.

    Args:
        resume_data: Current resume data
        job_title: Target job title
        attempt: Current optimization attempt number

    Returns:
        Optimization prompt
    """
    return f"""
    You are optimizing a resume for a {job_title} position. The resume is currently too long and needs to be condensed to fit on one page.
    All changes must remain grounded in the provided job description (do not fabricate).
    
    Current Resume Content:
    {_format_resume_for_optimization(resume_data)}
    
    Job Description:
    {job_description}
    
    Optimization Guidelines (Attempt {attempt}/4):
    - Remove or condense the least relevant content for {job_title} position
    - Prioritize keeping quantifiable achievements and technical skills
    - Reduce verbose descriptions while maintaining impact
    - Focus on recent and most relevant experiences
    - Condense professional summary if too long
    - Remove redundant skills or experiences
    
    Provide specific suggestions in this format:
    1. [Section]: [Specific change] - [Reason]
    2. [Section]: [Specific change] - [Reason]
    ...
    
    Focus on the most impactful changes that will reduce content while maintaining quality.
    """


def _format_resume_for_optimization(resume_data: ResumeData) -> str:
    """Format resume data for optimization analysis.

    Args:
        resume_data: Resume data to format

    Returns:
        Formatted string representation
    """
    content = f"Name: {resume_data.name}\n"
    content += f"Title: {resume_data.title}\n"
    content += f"Professional Summary: {resume_data.professional_summary}\n\n"

    content += "Experience:\n"
    for exp in resume_data.experience:
        content += f"- {exp.title} at {exp.company} ({exp.start_date} - {exp.end_date})\n"
        for point in exp.points:
            content += f"  • {point}\n"
        content += "\n"

    content += f"Skills: {', '.join(resume_data.skills)}\n\n"

    content += "Education:\n"
    for edu in resume_data.education:
        content += f"- {edu.degree} in {edu.major} from {edu.institution} ({edu.grad_date})\n"

    content += "\nCertifications:\n"
    for cert in resume_data.certifications:
        content += f"- {cert.title} ({cert.date})\n"

    return content


def _parse_optimization_response(response_text: str) -> list[str]:
    """Parse optimization suggestions from LLM response.

    Args:
        response_text: Raw response text

    Returns:
        List of optimization suggestions
    """
    suggestions = []
    lines = response_text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if line and (line.startswith(("1.", "2.", "3.", "4.", "5.")) or ":" in line):
            # Clean up the suggestion
            if ". " in line:
                line = line.split(". ", 1)[1]
            suggestions.append(line)

    return suggestions


def _apply_optimizations(resume_data: ResumeData, suggestions: list[str]) -> ResumeData:
    """Apply optimization suggestions to resume data.

    Args:
        resume_data: Original resume data
        suggestions: List of optimization suggestions

    Returns:
        Optimized resume data
    """
    # Create a copy of the resume data
    optimized_data = ResumeData(
        name=resume_data.name,
        title=resume_data.title,
        email=resume_data.email,
        phone=resume_data.phone,
        linkedin_url=resume_data.linkedin_url,
        professional_summary=resume_data.professional_summary,
        experience=resume_data.experience.copy(),
        education=resume_data.education.copy(),
        skills=resume_data.skills.copy(),
        certifications=resume_data.certifications.copy(),
    )

    # Apply common optimizations based on suggestions
    for suggestion in suggestions:
        suggestion_lower = suggestion.lower()

        # Optimize professional summary
        if "summary" in suggestion_lower and len(optimized_data.professional_summary) > 200:
            # Truncate summary
            optimized_data.professional_summary = optimized_data.professional_summary[:200] + "..."

        # Optimize experience bullets
        if "experience" in suggestion_lower or "bullet" in suggestion_lower:
            for exp in optimized_data.experience:
                if len(exp.points) > 3:
                    # Keep only top 3 bullets
                    exp.points = exp.points[:3]

        # Optimize skills
        if "skill" in suggestion_lower and len(optimized_data.skills) > 10:
            # Keep only top 10 skills
            optimized_data.skills = optimized_data.skills[:10]

        # Remove older experiences if too many
        if "experience" in suggestion_lower and len(optimized_data.experience) > 3:
            optimized_data.experience = optimized_data.experience[:3]

    return optimized_data


def _create_optimization_feedback(suggestions: list[str], attempt: int) -> str:
    """Create feedback message about optimization.

    Args:
        suggestions: List of applied optimizations
        attempt: Current optimization attempt

    Returns:
        Feedback message
    """
    if not suggestions:
        return f"Optimization attempt {attempt}: No specific optimizations applied."

    feedback = f"Optimization attempt {attempt}: Applied {len(suggestions)} optimizations:\n"
    for i, suggestion in enumerate(suggestions[:3], 1):  # Show top 3
        feedback += f"• {suggestion}\n"

    if len(suggestions) > 3:
        feedback += f"... and {len(suggestions) - 3} more optimizations"

    return feedback
