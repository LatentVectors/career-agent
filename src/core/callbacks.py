from typing import Any, Optional
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from tenacity import RetryCallState

from .logging_config import logger


class LoggingCallbackHandler(BaseCallbackHandler):
    """Logging callback handler."""

    def on_retry(
        self,
        retry_state: RetryCallState,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run on a retry event.

        Args:
            retry_state (RetryCallState): The retry state.
            run_id (UUID): The run ID. This is the ID of the current run.
            parent_run_id (UUID): The parent run ID. This is the ID of the parent run.
            kwargs (Any): Additional keyword arguments.
        """

        logger.warning(
            (
                f"Retrying ({retry_state.attempt_number}): "
                f"run_id={run_id} "
                f"parent_run_id={parent_run_id} "
                f"idle_for={retry_state.idle_for} "
                f"upcoming_sleep={retry_state.upcoming_sleep}"
            )
        )
        logger.debug(f"Retry state: {retry_state}")
