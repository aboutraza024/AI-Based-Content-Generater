import asyncio

from app.schemas.humanize import HumanizeRequest, HumanizeResponse
from app.ai.langchain_chains.humanization_chain import humanizer_chain
from app.utils.humanization_linter import linter
from app.core.logging import logger


class HumanizeService:
    """Turns raw text into natural, human-sounding writing."""

    async def humanize(self, req: HumanizeRequest) -> HumanizeResponse:
        logger.info(f"Humanizing a {req.content_type.value} in a {req.tone.value} tone")

        rewritten = await asyncio.to_thread(
            humanizer_chain.run,
            content_type=req.content_type.value,
            target_audience=req.target_audience or "General Audience",
            tone=req.tone.value,
            text=req.text,
        )

        final_text, _ = linter.clean(rewritten)
        logger.info("Humanize finished")

        return HumanizeResponse(
            humanized_content=final_text,
            word_count_actual=len(final_text.split()),
            success=True,
        )


humanize_service = HumanizeService()
