# Spec Requirements Document

> Spec: resume-template-cli-generator
> Created: 2025-08-11

## Overview

Implement a CLI command that generates new ATS-safe Jinja2 HTML resume templates from a natural-language description and an optional reference image, then renders them with dummy data for manual validation.

## User Stories

### Generate a template from a description
As a developer, I want to generate a new Jinja2 HTML resume template from a short description (and optional reference image), so that I can quickly create ATS-friendly variations tailored to different styles.

Detailed workflow: Run a CLI command, provide a description and optionally an image path; the tool prompts `gpt-4o` (multimodal when image provided) using the existing template prompt contract, returns HTML, and saves it to a staging directory.

### Render with dummy data for parser validation
As a developer, I want the tool to render the generated template with existing dummy resume profiles, so that I can manually test parsing quality with online ATS parsers.

Detailed workflow: After saving the HTML template, the command renders it with at least one `DUMMY_RESUME_DATA` profile into a standalone HTML file that can be uploaded to a parser, and optionally also saves a PDF preview.

### Keep generated assets separate from source
As a developer, I want generated templates saved outside the source tree, so that I can manually review and then copy approved templates into `src/features/resume/templates/`.

Detailed workflow: Output files are placed under `data/templates/generated/YYYYMMDD/<template_name>/` with clear filenames.

## Spec Scope

1. **CLI command to generate templates** - Add a subcommand under the `resume` CLI group to create a new HTML resume template from a description and optional image.
2. **Multimodal prompt assembly** - Use `gpt-4o` via LangChain multimodal input; include the image in the prompt only when provided.
3. **Template contract compliance** - Enforce the existing Jinja2 data contract and constraints defined in `src/features/resume/prompt.py`.
4. **Artifact saving** - Save: (a) raw template HTML, (b) rendered HTML populated with dummy data, and (c) optionally a PDF preview.
5. **Configurable options** - Allow overriding model, output directory, template name/slug, and choice of dummy profile.

## Out of Scope

- Automated ATS parser validation or scoring.
- Automatic promotion of generated templates into `src/features/resume/templates/`.
- Web UI or interactive TUI beyond standard CLI prompts/options.

## Expected Deliverable

1. Running the CLI with a description (and optional image) produces a valid Jinja2 template file plus a rendered HTML file under `data/templates/generated/...`.
2. The generated HTML uses only placeholders from the documented data contract and renders cleanly with at least one `DUMMY_RESUME_DATA` profile.
3. If a PDF option is enabled, a PDF preview is also saved without errors.
