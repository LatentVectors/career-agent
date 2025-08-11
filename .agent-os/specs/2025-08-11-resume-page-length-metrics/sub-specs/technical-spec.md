# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-08-11-resume-page-length-metrics/spec.md

## Technical Requirements

- Per-page content extrema detection
  - For each page: compute the minimum/maximum x and y coordinates of rendered content.
  - Approach: use `pypdf` (PdfReader) page content and bounding boxes when available; fallback to parsing content stream operators (e.g., text showing and path painting) to infer bounds. Prefer libraries/utilities that expose layout boxes if available.
  - Output: for each page `i`, `extrema[i] = {min_x, max_x, min_y, max_y, page_width, page_height}`.

- Margin and content area calculation
  - For each page, compute distances to edges: `left = min_x - 0`, `right = page_width - max_x`, `bottom = min_y - 0`, `top = page_height - max_y`.
  - Margin assumption: all margins equal. Margin = `min(left, right, top, bottom)` across all pages.
  - Content area (height) = `page_height - 2 * margin`; content width not needed for vertical fill metric.

- Per-page fill percentage
  - Compute vertical content extent = `page_height - min_y - margin` (assuming origin is bottom-left per PDF spec; adjust only if validation reveals template-specific inversion).
  - Percentage filled per page = `clamp(vertical_extent / content_area_height, 0, 1)`.
  - Return per-page array of `{page_index, min_x, max_x, min_y, max_y, margin, content_area_height, percent_filled}`.

- Aggregate resume_page_length
  - If only one page: `resume_page_length = percent_filled_page_1`.
  - If multiple pages: `resume_page_length = (num_pages - 1) + percent_filled_last_page`.

## Pydantic Output Models

- Define immutable Pydantic models (Pydantic v2) to represent computed metrics. Models must be non-editable after creation.
  - `PDFMetrics`
    - Fields: `total_pages: int`, `page_metrics: list[PageMetric]`
  - `PageMetric`
    - Fields: `page_number: int`, `margin: float`, `min_x: float`, `max_x: float`, `min_y: float`, `max_y: float`, `percent_filled: float`
  - Immutability: set `model_config = ConfigDict(frozen=True)` in each model.

Example:

```python
from typing import List
from pydantic import BaseModel, ConfigDict

class PageMetric(BaseModel):
    model_config = ConfigDict(frozen=True)

    page_number: int
    margin: float
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    percent_filled: float  # 0.0 to 1.0

class PDFMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)

    total_pages: int
    page_metrics: List[PageMetric]
```

## Integration points

- Utilities in `src/features/resume/utils.py`:
  - Core analyzer returning models:
    - `compute_pdf_metrics(pdf_path: Path) -> PDFMetrics`  // orchestrates analysis and returns immutable models
  - Internal helpers (implementation detail; may be private):
    - `analyze_pdf_page_extents(pdf_path: Path) -> list[dict]`
    - `compute_uniform_margin(extents: list[dict]) -> float`
    - `compute_page_fill_percentages(extents: list[dict], margin: float) -> list[float]`
    - `compute_resume_page_length(percentages: list[float]) -> float`
- Update `src/agents/resume_generator/nodes/generate_resume_pdf.py`:
  - After generating the PDF, call `compute_pdf_metrics()`.
  - Derive `resume_page_length` from percentages per the rule above.
  - Remove the existing approach in favor of the new approach using `compute_pdf_metrics`.
- `src/agents/resume_generator/nodes/select_resume_content.py` continues to read `resume_page_length` (no API change).

## Performance criteria

- Analysis should complete within ~200ms for 2-3 page PDFs on typical laptops.

## External Dependencies (Conditional)

- If robust content bounding is not feasible with `pypdf` alone, consider `pdfminer.six` for layout analysis.
  - Library: `pdfminer.six` — layout analysis (`LAParams`) can extract text boxes and their coordinates.
  - Justification: Reliable content bounding without changing PDF generation.
  - Version: latest stable compatible with Python project.
