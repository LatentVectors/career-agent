# Spec Summary (Lite)

Implement precise resume page length metrics by detecting per-page content extrema and inferring margins to compute the percentage of content area filled per page. Convert these percentages to a `resume_page_length` where value equals `(total pages - 1) + last page fill percentage` (e.g., 0.80; or 1.27 for pages 0.97 and 0.27). Integrate into the resume agent to improve convergence toward the target page length.
