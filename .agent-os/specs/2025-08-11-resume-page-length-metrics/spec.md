# Spec Requirements Document

> Spec: Resume Page Length Metrics
> Created: 2025-08-11

## Overview

Improve resume page length measurement by computing the percentage of the content area filled on each PDF page using detected content extrema and margins, and use these percentages to set an accurate `resume_page_length` for the agent.

## User Stories

### Accurate page-length signal for resume agent

As a resume-generation agent, I want a page-length metric based on how much of the last page is actually filled, so that I can iteratively target a specific page length (e.g., 1.0 pages) more precisely than with raw page counts.

Detailed workflow: After generating a PDF, detect per-page content extrema and margins, compute a fill percentage per page, and convert these into a `resume_page_length` that reflects (total full pages) plus (last page fill percentage). Feed this into selection/feedback nodes to converge on the target.

### Tested PDF page metrics utilities

As a developer, I want unit-tested utilities that extract page dimensions, content extrema, margins, and per-page fill percentages, so that the metrics are robust and regressions are caught.

## Spec Scope

1. **Per-page extrema detection** - For each page, find the most extreme x- and y-coordinates of content.
2. **Margin and content-area computation** - Infer a uniform margin across all sides using minimum distance to edges; compute content area = page dimension − 2 × margin.
3. **Per-page fill percentage** - Use content extrema and content area to compute percent of content area filled on each page; return structured per-page metrics.
4. **Unit tests** - Add tests covering page length extraction and percentage calculations with deterministic PDFs.
5. **Resume agent integration** - Replace raw page count with percentage-based `resume_page_length`:
   - Example: single page 0.80 filled → `resume_page_length = 0.80`.
   - Example: two pages with 0.97 and 0.27 → `resume_page_length = 1.27`.
   - General rule: `(total pages - 1) + last page fill percentage`.

## Out of Scope

- Changing resume HTML/CSS templates or visual design.
- Database schema or external API changes.
- Non-PDF document types.

## Expected Deliverable

1. Utilities that, given a PDF resume, return per-page fill percentages and a computed `resume_page_length` per the rule above.
2. Unit tests for page length extraction and percentage calculations using generated test PDFs.


