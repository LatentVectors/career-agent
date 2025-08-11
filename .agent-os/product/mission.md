# Product Mission

## Pitch

Agentic is an AI career document assistant that helps job seekers turn their background and a target job description into tailored resumes, cover letters, and outreach messages by aligning their experience to the role’s actual requirements.

## Users

### Primary Customers

- Job Seekers: Individuals applying to specific roles who need high-quality, tailored documents quickly.
- Career Switchers: Candidates repositioning their experience toward a new role or industry.

### Secondary Customers

- Career Coaches: Professionals assisting candidates with personalized application materials.
- Recruiters/Hiring Managers: Consumers of improved, better-structured application content.

### User Personas

**Mid-career IC** (28-40 years old)
- Role: Software Engineer, Data Scientist, Product Manager
- Context: Applying to multiple roles; limited time to tailor each application
- Pain Points: Matching experience to requirements, articulating measurable impact
- Goals: Submit tailored applications faster; increase interview rate

**Early-career Graduate** (20-27 years old)
- Role: Entry-level technical or business roles
- Context: Limited formal experience; needs to translate projects/internships into outcomes
- Pain Points: Highlighting relevant skills; writing compelling narratives
- Goals: Create credible, concise documents aligned to JD keywords

## The Problem

### Manual tailoring is slow and inconsistent
Crafting role-specific resumes and cover letters takes hours per job and often misses what the role actually prioritizes. This reduces response rates and delays applications. Our Solution: structured extraction of role requirements and targeted experience summarization.

### Experience-to-requirements mapping is hard
Candidates struggle to map their past work to the JD’s bullets and language. Our Solution: requirement-aligned summaries and STAR-style narratives that directly reference the JD.

### Quality feedback loops are missing
Iterating on drafts with feedback is cumbersome. Our Solution: a human-in-the-loop feedback step that routes back into the writer for quick refinement.

## Differentiators

### Graph-native workflow with sub-agents
Unlike monolithic prompts, we use a LangGraph state machine with specialized sub-agents (experience summarizer, responses summarizer, resume generator) for clarity, modularity, and reuse.

### Requirement-first content generation
We explicitly extract JD requirements, then summarize experience and responses against them, improving relevance and keyword alignment.

### Deep user-context grounding
Beyond resumes and simple prompt tailoring, the agent ingests richer user-provided sources (candidate responses, experience documents, motivations, and related artifacts). This deeper corpus gives the agent a well-rounded understanding of the candidate, enabling highly personalized content across many contexts.

### Human-in-the-loop refinement
Integrated feedback node enables quick iteration on generated drafts for higher final quality.

### Local-first storage and reproducibility
SQLite + file storage under `data/` with VCR cassettes supports repeatable runs and offline workflows.

## Key Features

### Core Features
- Job Requirements Analysis: Extract and normalize requirements from job descriptions.
- Experience Summarization: Create requirement-aligned summaries from user experience.
- Cover Letter Generation: Produce tailored, structured letters with measurable outcomes.
- Resume Generation: Select content and render to PDF via HTML templates.
- Graph Visualization: Display agent graphs and optionally render mermaid PNGs.

### Collaboration & Feedback
- Feedback Loop: HITL step to capture and apply feedback to drafts.
- Evaluation Harness: Offline evals for datasets and experiments to measure quality over time.


