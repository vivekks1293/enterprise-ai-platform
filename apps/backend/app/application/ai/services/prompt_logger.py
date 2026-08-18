
import logging

from app.domain.ai.models.chat_request import ChatRequest
from app.core.logging.logger import log_event

logger = logging.getLogger(__name__)


class PromptLogger:
    """
    Logs the prompt sent to the LLM.
    """

    @staticmethod
    def log(
        request: ChatRequest,
        *,
        context_item_count: int,
        duration_ms: float,
    ) -> None:
        """Logs prompt shape only; message contents are intentionally excluded."""

        estimated_input_size = sum(
            len(message.content)
            for message in request.messages
        )
        log_event(
            logger,
            "prompt.constructed",
            stage="prompt",
            message_count=len(request.messages),
            roles=[str(message.role) for message in request.messages],
            context_item_count=context_item_count,
            estimated_input_size=estimated_input_size,
            duration_ms=duration_ms,
        )