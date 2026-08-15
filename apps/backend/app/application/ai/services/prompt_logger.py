
import logging

from app.domain.ai.models.chat_request import ChatRequest

logger = logging.getLogger(__name__)


class PromptLogger:
    """
    Logs the prompt sent to the LLM.
    """

    @staticmethod
    def log(
        request: ChatRequest,
    ) -> None:

        logger.info("=" * 80)
        logger.info("PROMPT")
        logger.info("=" * 80)

        logger.info("Messages: %s", len(request.messages))

        for index, message in enumerate(
            request.messages,
            start=1,
        ):
            logger.info(
                "[%s] %s",
                index,
                message.role,
            )
            logger.info(message.content)
            logger.info("-" * 80)

        logger.info("=" * 80)