# Product Roadmap

## Phase 0: Already Completed

- [x] Main LangGraph orchestration with sub-agents (experience, responses, resume) `[L]`
- [x] Job requirements extraction and normalization `[M]`
- [x] Experience summarization aligned to requirements `[M]`
- [x] Cover letter generation with feedback loop `[M]`
- [x] Resume generator: content selection + HTML templates + PDF via WeasyPrint `[L]`
- [x] CLI commands: `graph`, `chat`, `resume generate` `[S]`
- [x] Database layer with SQLModel + SQLite and repository pattern `[M]`
- [x] File/data storage under `data/` with VCR cassettes for reproducibility `[S]`

## Phase 1: Output quality refinement

**Goal:** Higher-quality resumes and cover letters from existing workflows

**Success Criteria:** Measurable gains on evals for relevance, clarity, and specificity; fewer manual edits needed per document

### Features
- [ ] Improve prompts and response schemas for `job_requirements`, `summarize_experience`, and `write_cover_letter` `[M]`
- [ ] Expand HTML/PDF resume templates and fine-tune content selection `[M]`
- [ ] Strengthen requirement-to-experience mapping and STAR-style guidance `[M]`
- [ ] Add/expand eval datasets and evaluators; prefer evals over unit tests for LLM nodes `[M]`
- [ ] Enhance logging/trace metadata for easier debugging (LangSmith) `[S]`

### Dependencies
- LangGraph, LangChain, OpenAI models, WeasyPrint

## Phase 2: CLI ergonomics and speed

**Goal:** Faster, simpler CLI for generating documents for new positions

**Success Criteria:** Reduce steps/time to generate tailored docs; non-interactive flows work end-to-end

### Features
- [ ] Streamlined commands and flags for common flows (save JD → generate docs) `[S]`
- [ ] Non-interactive mode with sensible defaults and profile configs `[S]`
- [ ] Better agent discovery/selection (`graph`, `chat`, `resume`) with `--agent` shortcuts `[S]`
- [ ] Improved help, examples, and error messages `[S]`

### Dependencies
- Typer CLI, existing `src/cli.py`

## Phase 3: Expand content types

**Goal:** Support additional outreach surfaces

**Success Criteria:** Generate high-quality LinkedIn messages, cold-outreach emails, and follow-up emails grounded in JD and user context

### Features
- [ ] Add state + nodes for LinkedIn message, cold-outreach email, and follow-up email generation `[M]`
- [ ] Templates and tone/style controls per channel `[S]`
- [ ] Optional personalization snippets based on requirement coverage `[S]`

### Dependencies
- Existing graph and templating system

## Phase 4: Company research grounding

**Goal:** Enrich content with company-specific research

**Success Criteria:** Document generation accepts a company overview grounded in public sources (values, mission, industry, recent projects/milestones)

### Features
- [ ] Research sub-agent to gather/publicly reference company background with citations `[L]`
- [ ] Integrate company overview into resume/letter/message generation nodes `[M]`
- [ ] Caching of research artifacts for reuse across runs `[S]`

### Dependencies
- Research tooling (HTTP, scraping APIs as permitted), storage layer for artifacts

## Phase 5: Contact discovery enrichment

**Goal:** Identify key contacts (HR, hiring manager) to refine personalization

**Success Criteria:** Optionally include target contact roles/names/titles in generated outreach when available from public sources

### Features
- [ ] Specialized research agent for contact discovery (company site, LinkedIn, public directories) `[L]`
- [ ] Contact data structure and safe handling policies `[M]`
- [ ] Personalization templates conditioned on contact presence `[S]`

### Dependencies
- Research sub-agent; compliance guidelines; storage for discovered contacts

## Phase 6: React UI + FastAPI backend

**Goal:** Modern UX with API-driven backend

**Success Criteria:** Web UI supports the primary flows; backend exposes endpoints for running agents and managing artifacts

### Features
- [ ] FastAPI service exposing core operations (save JD, run agent, fetch artifacts) `[L]`
- [ ] React frontend for running workflows, viewing results, and downloads `[L]`
- [ ] Auth/session hooks (optional, later) `[M]`
- [ ] Packaging/deployment guides (Docker) `[M]`

### Dependencies
- FastAPI, React, build/deploy tooling
