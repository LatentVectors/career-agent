# Agentic - AI Career Document Assistant

An intelligent AI agent that helps create personalized career-related documents and content using your work history, motivations, interests, and target job descriptions. The agent analyzes job requirements and your background to generate customized resumes, cover letters, LinkedIn messages, and other career documents.

## Features

- **Job Requirements Analysis**: Extracts and analyzes key requirements from job descriptions
- **Experience Summarization**: Summarizes your work experience to align with specific job requirements
- **Cover Letter Generation**: Creates personalized cover letters based on your experience and job requirements
- **Multi-Document Support**: Designed to generate various career documents (resumes, LinkedIn messages, HR communications)
- **Context-Aware**: Uses your motivations, interests, and interview preparation to create more personalized content
- **File-Based Storage**: Stores job descriptions, experience, and background information locally

## Setup

1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Set up environment variables:**
   Create a `.env` file in the project root with:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   LANGSMITH_API_KEY=your_langsmith_api_key_here
   LANGSMITH_PROJECT=your_project_name
   LANGSMITH_ENDPOINT=https://api.smith.langchain.com
   LANGSMITH_TRACING=true
   ```

## Usage

### Interactive Chat Mode
```bash
python cli.py chat
```
This starts an interactive session where you can:
- Select from saved job descriptions
- View your background information (experience, motivations, interview questions)
- Generate personalized cover letters based on your experience and the job requirements

### Save Job Descriptions
```bash
python cli.py save-job "Company Name"
```
Save a job description for future use. The system will prompt you to enter the job description.

### View Workflow Graph
```bash
python cli.py graph
```
Visualize the agent's workflow and decision-making process.

## Project Structure

```
src/
├── cli.py                    # CLI interface using Typer
├── config.py                 # Configuration and settings
├── graph.py                  # Main LangGraph workflow
├── state.py                  # State management and data models
├── nodes/                    # Graph nodes (agent logic)
│   ├── job_requirements.py   # Extract job requirements from descriptions
│   ├── summarize_experience_node.py  # Summarize work experience
│   └── write_cover_letter.py # Generate cover letters
├── agents/
│   └── experience_summarizer/  # Specialized agent for experience analysis
├── storage/                  # File-based data storage
│   ├── FileStorage.py        # File storage implementation
│   ├── parse_job.py         # Job description parsing
│   ├── parse_motivations_and_interests.py  # Background parsing
│   └── parse_interview_questions.py  # Interview Q&A parsing
└── tools.py                 # Tool registry (for future expansion)
```

## Architecture

The system is built around LangGraph with the following components:

1. **State Management** (`state.py`): Tracks conversation history, job requirements, experience summaries, and generated documents
2. **Nodes** (`nodes/`): Contains the agent logic for:
   - Extracting job requirements from descriptions
   - Summarizing work experience to align with job requirements
   - Generating personalized cover letters
3. **Graph** (`graph.py`): Orchestrates the workflow:
   - Extracts job requirements
   - Summarizes relevant experience
   - Generates cover letters
4. **Storage** (`storage/`): File-based storage for:
   - Job descriptions
   - Work experience
   - Motivations and interests
   - Interview questions and answers
5. **Experience Summarizer** (`agents/experience_summarizer/`): Specialized agent for analyzing and summarizing work experience against job requirements

## Data Storage

The system uses a file-based storage system in the `data/` directory:
- Job descriptions are stored as markdown files
- Experience entries are stored as individual markdown files
- Motivations, interests, and interview questions are stored in structured formats

## Current Capabilities

- **Job Analysis**: Extracts requirements, qualifications, company culture, and values from job descriptions
- **Experience Matching**: Identifies relevant experience that aligns with job requirements
- **Cover Letter Generation**: Creates personalized cover letters using STAR method summaries
- **Multi-Format Support**: Designed to generate various document types (currently cover letters, with resume and messaging support planned)

## Future Enhancements

- Resume generation with experience summaries
- LinkedIn profile optimization
- Interview answer preparation
- Email templates for networking and follow-ups
- ATS optimization for resumes and cover letters