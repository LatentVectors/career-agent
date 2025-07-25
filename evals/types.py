from typing import List, NotRequired, Optional, TypedDict, Union


class EvaluationResult(TypedDict):
    """Evaluation for the evaluation run.

    See documentation for more details:
    https://docs.smith.langchain.com/reference/data_formats/feedback_data_format
    """

    key: str
    """A key describing the criteria of the feedback, eg 'correctness'."""
    score: NotRequired[Optional[bool | int | float | None]]
    """Numerical score associated with the feedback key."""
    value: NotRequired[Optional[str | None]]
    """Reserved for storing a value associated with the score. Useful for categorical feedback."""
    comment: NotRequired[Optional[str]]
    """Any comment or annotation associated with the record. This can be a justification for the score given."""


EvaluationResults = Union[EvaluationResult, List[EvaluationResult]]
