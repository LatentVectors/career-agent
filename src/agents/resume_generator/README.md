# Overview
This agent is writes a high-quality resume for the user.

# State
**InputState**
- job_title: str
- job_description: str
- resume_page_target: float = 1.0
- feedback_loop_max_iterations: int = 4

**OutputState**
- resume: ResumeData
- resume_path: Path

# Nodes
**Read DB Content**
Read user information from the database using the db_manager. Get the user_id from the context. The invoking parent is responsible for passing in the context to the graph.

Reads:
    - context.user_id # From Context API

Returns:
    - user: User # From db/models
    - education: list[Education] # From db/models
    - credentials: list[Certification] # From db/models
    - experience: dict[int, Experience] # From db/models. The dict key is the experience ID.
    - candidate_responses: list[CandidateResponse] # From db/models

**Extract Skills and Accomplishments**
Use structured outputs to extract a list of accomplishments and a list of skills from the users experience. The extracted content should be grounded in the users experience and be stated in a way that best matches the language used in the target job description. The accomplishments returned by this node should be stand-alone bullet points for the resume and should follow all the best practices for writing high-quality resume bullet points. A later node will filter through these bullet points to select the best ones. Similarly, the skills will be filtered by the same node to highlight the most relevant content. Return all the skills the user experience demonstrates that are in the job description. 

Reads:
    - job_description
    - current_experience_id

Returns:
    - skills_and_accomplishments: dict[int, SkillsAndAccomplishments] # Reduce using dict update. The Key is the current_experience_id.

**Summarize Experience**
Generate a summary of the experience indicated by the current_experience_id. The summary will be used to help generate the professional summary, and should be grounded the provided experience and highlight how the candidate aligns with the provided job description.

Reads:
    - job_description
    - current_experience_id

Returns:
    - experience_summary: dict[int, str] # Reduce with dict update with current_experience_id as the key and the summarized experience as the value.

**Summarize Responses**
Generate a summary of the users candidate responses. The summary will be used to help generate the professional summary and should be grounded in the provided candidate responses and highlight how the candidate aligns with the provided job description. Candidate responses cover a wide range of topics, including strengths, weaknesses, interests, work-style, and other content that is not strictly related to any given position or project. This summary should take advantage of the unique aspect of this data to draw attention to or highlight that those less-tangible ways the user may align well with the target job description.

Reads:
    - job_description
    - candidate_responses

Returns:
    - responses_summary: str

**Create Professional Summary**
Generate a professional summary for the users resume. This summary should be grounded in the provided experience and responses summary to best align with the job description. This summary should highlight how the user is a unique candidate for the position and should avoid generic statements.

Defer: True

Reads:
    - job_description
    - experience_summary
    - responses_summary

Returns:
    - professional_summary: str

**Select Resume Content**
Review the generated resume content and select the most compelling experience, skills, and accomplishments to include in the final resume. If provided take into account the feedback, previous content, page length, and word count to refine the resume to meet the target page count. Beyond filtering experience, minor editing of accomplishments and refinement of the professional summary may also be used to generate the strongest possible resume for the target job description.

Defer: True

Reads:
    - user
    - education
    - credentials
    - job_title
    - job_description
    - skills_and_accomplishments
    - experience
    - professional_summary
    - resume_page_target
    - resume (if set)
    - resume_feedback (if set)
    - resume_page_length (if set)
    - word_count (if set)

Returns:
    - resume: ResumeData # See features/resume/types.py
    - word_count: int

**Generate Resume PDF**
Use the ResumeData to generate a PDF for the resume using one of the resume templates. After generating the resume, check its page_length.

Reads:
    - resume

Returns:
    - resume_path: Path
    - resume_page_length: float

**Provide Resume Feedback**
Review the current resume and provide feedback for the node that selects content to help it meet the target page-length requirement.

Reads:
    - resume
    - resume_page_length
    - resume_page_target
    - word_count

Returns:
    - resume_feedback: str
    - feedback_loop_iterations: int # Reduce to incrementing int.

# Edges
**Map Experience**
Map the users experience to the Extract Skills and Accomplishment and Summarize Experience nodes.

Reads:
    - experience

Sets:
    - current_experience_id

Returns:
    - list[Send] # To Extract Skills and Accomplishments or Summarize Experience.

**Route Feedback**
Determines if the resume meets the target page length requirements. If so, it routes to the END node. If not, it routes to the Provide Resume Feedback node. The resume meets the page length requirements when it is between (resume_page_target - 0.07) and resume_page_target pages long.

If the feedback_loop_iterations is greater than the feedback_loop_max_iterations, log a warning for the user and route to the END node.

Reads:
    - resume_page_target
    - resume_page_length
    - feedback_loop_iterations
    - feedback_loop_max_iterations

Returns:
    - Node.SELECT_RESUME_CONTENT | Node.END

# Graph

START -> read_db_content
read_db_content -> map_experience_edge[extract_skills_and_accomplishments, summarize_experience]
read_db_content -> summarize_responses
extract_skills_and_accomplishments -> select_resume_content
summarize_responses -> create_professional_summary
summarize_experience -> create_professional_summary
create_professional_summary -> select_resume_content
select_resume_content -> generate_resume_pdf
generate_resume_pdf -> route_feedback_edge[provide_resume_feedback, END]
provide_resume_feedback -> select_resume_content