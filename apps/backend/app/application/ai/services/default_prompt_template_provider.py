from app.application.ai.ports.prompt_template_provider import (
    PromptTemplateProvider,
)


class DefaultPromptBuilder(PromptTemplateProvider):

    async def get_system_prompt(self) -> str:
        return """
You are an Enterprise AI Assistant.

You provide accurate, concise and professional responses.

Always answer in Markdown.

If you don't know the answer,
say you don't know instead of making up information.
""".strip()