"""Generate PDF node for resume generation."""

from __future__ import annotations

from pathlib import Path

from langgraph.runtime import Runtime

from src.config import DATA_DIR
from src.context import AgentContext
from src.features.resume.types import ResumeData
from src.features.resume.utils import get_pdf_page_count, render_template_to_pdf
from src.logging_config import logger

from ..state import InternalState, PartialInternalState


def generate_pdf(state: InternalState, runtime: Runtime[AgentContext]) -> PartialInternalState:
    """Create PDF and check page length.

    Args:
        state: Current state containing resume_data

    Returns:
        Updated state with PDF path and page length
    """
    resume_data = state.resume_data
    job_title = state.job_title
    optimization_attempts = state.optimization_attempts
    is_optimizing = state.is_optimizing
    best_page_length = state.best_page_length
    best_resume_data = state.best_resume_data
    best_pdf_path = state.best_pdf_path

    logger.debug("NODE: resume_generator.generate_pdf")
    logger.debug(f"Generating PDF for job title: {job_title}")

    if not resume_data:
        logger.error("No resume data available for PDF generation")
        return {"page_length": 0}

    try:
        # Convert ResumeData to context dict for template rendering
        context = _resume_to_template_context(resume_data)

        # Determine file naming
        user_name = resume_data.name.replace(" ", "_")
        safe_job_title = job_title.replace(" ", "_").replace("/", "_")

        if is_optimizing:
            # For optimization attempts, use draft naming
            filename = (
                f"Resume - {user_name} - {safe_job_title}_draft_{optimization_attempts + 1}.pdf"
            )
        else:
            # For initial generation, use standard naming
            filename = f"Resume - {user_name} - {safe_job_title}.pdf"

        # Resolve a unique PDF path (avoid overwriting existing files)
        pdf_path = _resolve_unique_path(Path(DATA_DIR) / filename)

        # Locate templates directory at src/features/resume/templates
        # __file__ → nodes/ → resume_generator/ → agents/ → src/
        templates_dir = Path(__file__).resolve().parents[3] / "features" / "resume" / "templates"

        # Generate PDF using default template
        render_template_to_pdf("resume_001.html", context, pdf_path, templates_dir)

        # Check page length using PDF reader; fall back to heuristic if needed
        try:
            estimated_pages = get_pdf_page_count(pdf_path)
        except Exception:
            estimated_pages = _estimate_page_length(resume_data)

        logger.debug(f"Generated PDF: {pdf_path} (estimated {estimated_pages} pages)")

        # Update best option tracking (prefer single page; otherwise, shortest)
        updates: dict[str, object] = {}
        selected_resume_data: ResumeData = resume_data
        selected_page_length: int = estimated_pages
        selected_pdf_path: str = str(pdf_path)

        should_update_best = False
        if best_page_length is None:
            should_update_best = True
        else:
            if estimated_pages < best_page_length:
                should_update_best = True
            elif estimated_pages == best_page_length and not is_optimizing:
                should_update_best = True

        if should_update_best:
            updates.update(
                {
                    "best_resume_data": resume_data,
                    "best_page_length": estimated_pages,
                    "best_pdf_path": str(pdf_path),
                }
            )
            best_resume_data = resume_data
            best_page_length = estimated_pages
            best_pdf_path = str(pdf_path)

        # Use best known option for outward-facing fields
        if best_resume_data is not None and best_page_length is not None:
            selected_resume_data = best_resume_data
            selected_page_length = best_page_length
            selected_pdf_path = best_pdf_path or selected_pdf_path

        # If optimizing and we reached a final selection (single page or attempts exhausted),
        # also write a final-named PDF copy for the selected content.
        if is_optimizing and (selected_page_length == 1 or optimization_attempts >= 4):
            final_filename = f"Resume - {user_name} - {safe_job_title}.pdf"
            final_pdf_path = _resolve_unique_path(Path(DATA_DIR) / final_filename)
            final_context = _resume_to_template_context(selected_resume_data)
            render_template_to_pdf("resume_001.html", final_context, final_pdf_path, templates_dir)
            selected_pdf_path = str(final_pdf_path)

        updates.update(
            {
                "page_length": selected_page_length,
                "resume_pdf_path": selected_pdf_path,
                "resume_text": str(selected_resume_data),
            }
        )

        # If attempts exhausted and still > 1 page, fallback to best prior draft
        if is_optimizing and optimization_attempts >= 4 and estimated_pages > 1:
            # Use previously tracked best option if available
            if best_resume_data is not None and best_page_length is not None:
                updates.update(
                    {
                        "resume_data": best_resume_data,
                        "page_length": best_page_length,
                        "resume_pdf_path": best_pdf_path or str(pdf_path),
                        "resume_text": str(best_resume_data),
                    }
                )

        return updates  # type: ignore[return-value]

    except Exception as e:
        logger.exception(f"Error generating PDF: {e}")
        return {"page_length": 0}


def _estimate_page_length(resume_data: ResumeData) -> int:
    """Estimate the number of pages in the resume.

    Args:
        resume_data: The resume data

    Returns:
        Estimated number of pages
    """
    # Simple estimation based on content length
    total_content = ""

    # Add professional summary
    total_content += resume_data.professional_summary + "\n"

    # Add experience content
    for exp in resume_data.experience:
        total_content += f"{exp.title} at {exp.company}\n"
        for point in exp.points:
            total_content += f"• {point}\n"

    # Add skills
    total_content += "Skills: " + ", ".join(resume_data.skills) + "\n"

    # Add education
    for edu in resume_data.education:
        total_content += f"{edu.degree} in {edu.major} from {edu.institution}\n"

    # Add certifications
    for cert in resume_data.certifications:
        total_content += f"{cert.title} ({cert.date})\n"

    # Rough estimation: ~500 characters per page
    char_count = len(total_content)
    estimated_pages = max(1, (char_count + 500) // 500)

    return estimated_pages


def _resolve_unique_path(target_path: Path) -> Path:
    """Resolve a unique file path by appending a numeric suffix if needed.

    Args:
        target_path: Desired file path

    Returns:
        A unique file path that does not currently exist
    """
    if not target_path.exists():
        return target_path

    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent
    counter = 1
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def _resume_to_template_context(resume_data: ResumeData) -> dict:
    """Build the Jinja2 template context from ResumeData."""
    return {
        "name": resume_data.name,
        "title": resume_data.title,
        "email": resume_data.email,
        "phone": resume_data.phone,
        "linkedin_url": resume_data.linkedin_url,
        "professional_summary": resume_data.professional_summary,
        "experience": [
            {
                "title": exp.title,
                "company": exp.company,
                "location": exp.location,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "points": exp.points,
            }
            for exp in resume_data.experience
        ],
        "skills": resume_data.skills,
        "education": [
            {
                "degree": edu.degree,
                "major": edu.major,
                "institution": edu.institution,
                "grad_date": edu.grad_date,
            }
            for edu in resume_data.education
        ],
        "certifications": [
            {
                "title": cert.title,
                "date": cert.date,
            }
            for cert in resume_data.certifications
        ],
    }
