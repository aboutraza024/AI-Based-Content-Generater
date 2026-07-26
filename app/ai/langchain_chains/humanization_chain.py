from langchain_core.prompts import ChatPromptTemplate

from app.ai.llm.azure_client import get_azure_llm
from app.ai.prompts.humanization_prompts import (
    POLISH_SYSTEM_PROMPT,
    POLISH_USER_PROMPT,
    HUMANIZE_TEXT_SYSTEM_PROMPT,
    HUMANIZE_TEXT_USER_PROMPT,
)
from app.core.logging import logger


class HumanizerChain:
    """Wraps the two LLM calls that make text sound more human."""

    def polish(self, language: str, region: str, target_audience: str, draft_content: str) -> str:
        """Used inside the full generation pipeline to polish a freshly drafted piece."""
        logger.info("Polishing the draft")
        prompt = ChatPromptTemplate.from_messages(
            [("system", POLISH_SYSTEM_PROMPT), ("user", POLISH_USER_PROMPT)]
        )
        chain = prompt | get_azure_llm(temperature=0.5)
        result = chain.invoke(
            {
                "language": language,
                "region": region,
                "target_audience": target_audience,
                "draft_content": draft_content,
            }
        )
        return self._as_text(result)

    def run(self, content_type: str, target_audience: str, tone: str, text: str) -> str:
        """Used by the standalone /humanize endpoint to rewrite any given text."""
        logger.info("Rewriting text with the humanizer")
        prompt = ChatPromptTemplate.from_messages(
            [("system", HUMANIZE_TEXT_SYSTEM_PROMPT), ("user", HUMANIZE_TEXT_USER_PROMPT)]
        )
        chain = prompt | get_azure_llm(temperature=0.5)
        result = chain.invoke(
            {
                "content_type": content_type,
                "target_audience": target_audience,
                "tone": tone,
                "text": text,
            }
        )
        return self._as_text(result)

    @staticmethod
    def _as_text(response) -> str:
        content = response.content
        return content.strip() if isinstance(content, str) else str(content).strip()


humanizer_chain = HumanizerChain()
