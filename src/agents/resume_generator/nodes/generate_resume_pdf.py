from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.config import DATA_DIR, PROJECT_ROOT
from src.features.resume.utils import get_pdf_page_count, render_template_to_pdf
from src.logging_config import logger

from ..state import InternalState, PartialInternalState


def generate_resume_pdf(state: InternalState) -> PartialInternalState:
    """
    Generate a PDF resume from `ResumeData` using an HTML template and record its page length.

    Overview:
        Renders the current `state.resume` via a Jinja2 HTML template and converts it to PDF.
        Saves the file under the project's data directory and reports both the file path and
        the computed page length for feedback routing.

    Reads:
        - resume

    Returns:
        - resume_path: Path
        - resume_page_length: float

    Design contract:
        - If `resume` is missing, log a warning and return no changes.
        - Use a stable default template; if not present, fall back to the first available.
        - Save PDFs to `<DATA_DIR>/resumes/` with a descriptive filename.
        - Compute page length from the generated PDF and return it as a float.
    """
    logger.debug("NODE: resume_generator.generate_resume_pdf")

    if state.resume is None:
        logger.warning("No resume data available; skipping PDF generation.")
        return PartialInternalState()

    # Resolve templates directory and pick a template
    templates_dir = PROJECT_ROOT / "src" / "features" / "resume" / "templates"
    default_template = "resume_002.html"
    template_name = default_template
    try:
        # Prefer the default template if it exists, otherwise pick the first discovered template
        if not (templates_dir / default_template).exists():
            candidates = sorted(p.name for p in templates_dir.glob("*.html"))
            if candidates:
                template_name = candidates[0]
            else:
                raise FileNotFoundError(f"No resume templates found in {templates_dir}")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to resolve resume template: %s", exc)
        return PartialInternalState()

    # Compute output path
    output_dir = DATA_DIR / "resumes"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    name_part = _safe_slug(state.resume.name)
    title_part = _safe_slug(state.job_title or "")
    filename_bits = [bit for bit in [name_part, title_part, timestamp] if bit]
    output_filename = "_".join(filename_bits) + ".pdf"
    output_path = output_dir / output_filename

    # Render and generate PDF
    try:
        context = _resume_to_template_context(state)
        pdf_path: Path = render_template_to_pdf(
            template_name=template_name,
            context=context,
            output_path=output_path,
            templates_dir=templates_dir,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to generate resume PDF: %s", exc)
        return PartialInternalState()

    # Derive page length
    try:
        page_count = get_pdf_page_count(pdf_path)
        page_length = float(page_count)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to read PDF page count: %s", exc)
        return PartialInternalState(resume_path=pdf_path)

    logger.debug(
        "Resume PDF generated: path=%s pages=%s template=%s", pdf_path, page_count, template_name
    )
    return PartialInternalState(resume_path=pdf_path, resume_page_length=page_length)


def _safe_slug(value: str) -> str:
    """Return a filesystem-friendly slug for the provided value.

    Replaces non-alphanumeric characters with dashes and collapses repeats.
    """
    cleaned = [ch.lower() if ch.isalnum() else "-" for ch in value.strip()]
    # Collapse repeated dashes
    slug: list[str] = []
    for ch in cleaned:
        if ch == "-" and (not slug or slug[-1] == "-"):
            continue
        slug.append(ch)
    result = "".join(slug).strip("-")
    return result or "resume"


# TODO: This need to use the resume module but didn't.
def _resume_to_template_context(state: InternalState) -> dict[str, object]:
    """Convert `ResumeData` in state to a template context dict."""
    assert state.resume is not None
    resume = state.resume
    return {
        "name": resume.name,
        "title": resume.title,
        "email": resume.email,
        "phone": resume.phone,
        "linkedin_url": resume.linkedin_url,
        "professional_summary": resume.professional_summary,
        "experience": [
            {
                "title": exp.title,
                "company": exp.company,
                "location": exp.location,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "points": list(exp.points),
            }
            for exp in resume.experience
        ],
        "skills": list(resume.skills),
        "education": [
            {
                "degree": edu.degree,
                "major": edu.major,
                "institution": edu.institution,
                "grad_date": edu.grad_date,
            }
            for edu in resume.education
        ],
        "certifications": [
            {
                "title": cert.title,
                "date": cert.date,
            }
            for cert in resume.certifications
        ],
    }
