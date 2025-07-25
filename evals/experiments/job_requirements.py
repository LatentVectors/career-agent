from typing import Optional, TypedDict

import typer
from langchain.chat_models import init_chat_model
from langsmith import Client
from openevals.llm import create_llm_as_judge
from src.nodes.job_requirements import JobRequirements
from src.nodes.job_requirements import chain as job_requirements_chain

from evals.datasets.datasets.jobs import JOBS_DATASET_NAME, JobsInput

llm = init_chat_model("gpt-4.1", max_retries=3)


def evaluate_job_requirements(
    prefix: Optional[str] = typer.Option(
        None, "--prefix", help="The prefix to use for the experiment."
    ),
) -> None:
    """Evaluate the job requirements."""
    client = Client()
    result = client.evaluate(
        target,  # type: ignore[arg-type]
        data=JOBS_DATASET_NAME,
        evaluators=[hallucinations, completeness, faithfulness],  # type: ignore
        experiment_prefix=prefix,
    )

    print(result)


class TargetOutput(TypedDict):
    """The output of the target function."""

    requirements: list[str]
    """The job requirements."""


def target(inputs: JobsInput) -> TargetOutput:
    """
    Target function for the job description parsing experiment.
    """
    results = job_requirements_chain.invoke({"job_description": inputs["job_description"]})
    return {"requirements": JobRequirements.model_validate(results).requirements}


hallucinations_prompt = """
You are an expert data labeler evaluating model outputs for hallucinations. Your task is to assign a score based on the following rubric:

<Rubric>
  A response without hallucinations:
  - Contains only verifiable facts that are directly supported by the input context
  - Makes no unsupported claims or assumptions
  - Does not add speculative or imagined details
  - Maintains perfect accuracy in dates, numbers, and specific details
  - Appropriately indicates uncertainty when information is incomplete
</Rubric>

<Scoring>
  - 0.0: The response is completely hallucinated with no grounding in the input.
  - 0.25: About a quarter of the response is hallucinated.
  - 0.5: About half of the response is hallucinated.
  - 0.75: About three quarters of the response is hallucinated.
  - 1.0: The response has not hallucinations and is completely grounded in the input.
</Scoring>

<Instructions>
  - Read the input context thoroughly
  - Identify all claims made in the output
  - Cross-reference each claim with the input context
  - Note any unsupported or contradictory information
  - Consider the severity and quantity of hallucinations
  - If available, compare the output with the reference requirements. The reference requirements are the requirements that the model should have extracted from the input job description.
</Instructions>

<Reminder>
  Focus solely on factual accuracy and support from the input context. Do not consider style, grammar, or presentation in scoring. A shorter, factual response should score higher than a longer response with unsupported claims.
</Reminder>

<Return>
  Return a JSON object with the following fields:
  - score: The score for the hallucinations (0.0, 0.25, 0.5, 0.75, 1.0)
  - explanation: A brief, one- or two-sentence explanation for the score.
</Return>
Use the following context to help you evaluate for hallucinations in the output:

<Job Description>
{inputs}
</Job Description>

<Reference Requirements>
{reference_outputs}
</Reference Requirements>

<Requirements>
{outputs}
</Requirements>
"""

hallucinations = create_llm_as_judge(
    prompt=hallucinations_prompt,
    feedback_key="hallucinations",
    choices=[0.0, 0.25, 0.5, 0.75, 1.0],
    judge=llm,
)

completeness_prompt = """
You are an expert data labeler evaluating model outputs for completeness. Your task is to assign a score based on the following rubric:

<Rubric>
  A complete response:
  - Extracts ALL relevant job requirements from the input context, including requirements stated or implied in the company overview and position summary.
  - Includes both explicit requirements (directly stated) and implicit requirements (logically implied)
  - Captures requirements across all categories (technical skills, experience, education, certifications, etc.)
  - Does not miss any critical qualifications or prerequisites
  - Identifies both mandatory and preferred requirements
  - Includes soft skills, hard skills, and domain-specific knowledge
  - Includes all requirements in the provided reference requirements, if available. Any output that does not include all reference requirements cannot have a score of 1.0.
</Rubric>

<Scoring>
  - 0.0: No relevant requirements were extracted from the input.
  - 0.25: About a quarter of the relevant requirements were extracted.
  - 0.5: About half of the relevant requirements were extracted.
  - 0.75: About three quarters of the relevant requirements were extracted.
  - 1.0: All relevant requirements were properly extracted from the input. Not a single reference requirement is missing from the output.
</Scoring>

<Instructions>
  - Read the input job description thoroughly
  - Identify all stated and implied job requirements, including requirements stated or implied in the company overview and position summary.
  - Check if the output captures all requirements in the job description.
  - Verify that no critical qualifications are missing
  - Consider both explicit and implicit requirements
  - Evaluate coverage across technical, educational, soft skills, temperamental, experiential, time-zone, company culture, and other requirements
  - If available, compare the output with the reference requirements. To receive a score of 1.0, the output must include all reference requirements.
</Instructions>

<Reminder>
  Focus solely on the comprehensiveness of requirement extraction. Do not consider style, grammar, or presentation in scoring. A response that captures all requirements should score higher than one that misses critical qualifications, regardless of length.
</Reminder>

<Return>
  Return a JSON object with the following fields:
  - score: The score for completeness (0.0, 0.25, 0.5, 0.75, 1.0)
  - explanation: A brief, one- or two-sentence explanation for the score.
</Return>
Use the following context to help you evaluate for completeness in the output:

<Job Description>
{inputs}
</Job Description>

<Reference Requirements>
{reference_outputs}
</Reference Requirements>

<Requirements>
{outputs}
</Requirements>
"""

completeness = create_llm_as_judge(
    prompt=completeness_prompt,
    feedback_key="completeness",
    choices=[0.0, 0.25, 0.5, 0.75, 1.0],
    judge=llm,
)

faithfulness_prompt = """
You are an expert data labeler evaluating model outputs for faithfulness. Your task is to assign a score based on the following rubric:

<Rubric>
  A faithful response:
  - Preserves the original wording and phrasing from the input context
  - Maintains the exact terminology and industry-specific language used
  - Retains the precise intent and meaning of the original requirements
  - Uses the same level of specificity and detail as the source
  - Preserves technical terms, certifications, and qualification standards exactly as stated
  - Maintains the hierarchical structure and importance levels of requirements
</Rubric>

<Scoring>
  - 0.0: The extracted requirements are completely different from the input job description.
  - 0.25: About a quarter of the requirements preserve the original wording and intent.
  - 0.5: About half of the requirements preserve the original wording and intent.
  - 0.75: About three quarters of the requirements preserve the original wording and intent.
  - 1.0: The extracted requirements exactly match the input job description in wording and intent.
</Scoring>

<Instructions>
  - Read the input job description thoroughly
  - Compare each extracted requirement with the original text
  - When assessing faithfulness only consider the requirements that a present in the output requirements. Do not consider requirements that are missing from the output.
  - Check for preservation of exact terminology and phrasing
  - Verify that technical terms and certifications are unchanged
  - Evaluate whether the intent and meaning are preserved
  - Consider the importance of precise language for ATS systems
  - If available, compare the output with the reference requirements. To receive a score of 1.0, each output requirement should closely match one of the reference requirements.
</Instructions>

<Reminder>
  - Focus solely on the preservation of original wording and intent. This is critical for ATS compatibility and resume matching. Exact language preservation is more important than paraphrasing or summarization. The requirements must maintain the precise terminology that hiring managers and ATS systems expect.
  - When assessing faithfulness only consider the requirements that a present in the output requirements. Do not consider requirements that are missing from the output. A response can receive a score of 1.0 even if some of the requirements are missing from the output, so long as all the requirements that are present in the output are faithful to the input job description.
</Reminder>

<Return>
  Return a JSON object with the following fields:
  - score: The score for faithfulness (0.0, 0.25, 0.5, 0.75, 1.0)
  - explanation: A brief, one- or two-sentence explanation for the score.
</Return>
Use the following context to help you evaluate for faithfulness in the output:

<Job Description>
{inputs}
</Job Description>

<Reference Requirements>
{reference_outputs}
</Reference Requirements>

<Requirements>
{outputs}
</Requirements>
"""

faithfulness = create_llm_as_judge(
    prompt=faithfulness_prompt,
    feedback_key="faithfulness",
    choices=[0.0, 0.25, 0.5, 0.75, 1.0],
    judge=llm,
)
