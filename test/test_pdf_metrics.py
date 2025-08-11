from __future__ import annotations

from pathlib import Path

from src.features.resume.utils import (
    compute_pdf_metrics,
    compute_resume_page_length,
    convert_html_to_pdf,
)


def test_compute_resume_page_length_rules() -> None:
    # Single page
    assert compute_resume_page_length([0.80]) == 0.80

    # Multiple pages
    assert compute_resume_page_length([0.97, 0.27]) == 1.27

    # Empty
    assert compute_resume_page_length([]) == 0.0


def test_uniform_margin_and_percentages_basic() -> None:
    # Build synthetic per-page extents to exercise margin and percentages logic
    # Page size 1000 x 1000, content box within 50px margins on left/right/top.
    # First page: content reaches bottom margin (min_y = 50) => 100% fill
    # Second page: content bottom at y=750 => 200/900 ~ 0.2222 fill
    extents = [
        {
            "min_x": 50.0,
            "max_x": 950.0,
            "min_y": 50.0,
            "max_y": 950.0,
            "page_width": 1000.0,
            "page_height": 1000.0,
        },
        {
            "min_x": 50.0,
            "max_x": 950.0,
            "min_y": 750.0,
            "max_y": 950.0,
            "page_width": 1000.0,
            "page_height": 1000.0,
        },
    ]

    # Import internals for targeted unit testing
    from src.features.resume.utils import (  # type: ignore  # noqa: PLC2701
        _compute_page_fill_percentages,
        _compute_uniform_margin,
    )

    margin = _compute_uniform_margin(extents)
    assert margin == 50.0

    percentages = _compute_page_fill_percentages(extents, margin)
    assert len(percentages) == 2
    assert percentages[0] == 1.0
    assert abs(percentages[1] - (200.0 / 900.0)) < 1e-6

    # Aggregate page length per spec
    total_len = compute_resume_page_length(percentages)
    assert abs(total_len - (1 + (200.0 / 900.0))) < 1e-6


def test_compute_pdf_metrics_smoke(tmp_path: Path) -> None:
    # Generate a simple single-page PDF via WeasyPrint
    html = """
    <html>
      <head>
        <style>
          @page { size: 600px 800px; margin: 50px; }
          body { font-family: Arial, sans-serif; }
          .block { height: 300px; background: #eee; }
        </style>
      </head>
      <body>
        <h1>Test Document</h1>
        <div class="block">Content Block</div>
        <p>Some text to ensure detectable layout.</p>
      </body>
    </html>
    """

    pdf_path = tmp_path / "sample.pdf"
    convert_html_to_pdf(html, pdf_path)

    metrics = compute_pdf_metrics(pdf_path)
    assert metrics.total_pages >= 1
    assert len(metrics.page_metrics) == metrics.total_pages
    for pm in metrics.page_metrics:
        assert 0.0 <= pm.percent_filled <= 1.0
        assert pm.margin >= 0.0
