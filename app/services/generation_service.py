import asyncio
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.ai.langchain_chains.content_draft_chain import run_content_draft_chain
from app.ai.langchain_chains.humanization_chain import humanizer_chain
from app.ai.langchain_chains.meta_chain import run_meta_chain
from app.utils.humanization_linter import linter
from app.core.logging import logger

class GenerationService:
    async def generate_full_content_async(self, req: GenerateRequest) -> GenerateResponse:
        logger.info(f"Generating content for '{req.product_name}'")

        # First write the draft
        raw_draft = await asyncio.to_thread(
            run_content_draft_chain,
            language=req.language,
            region=req.region.value,
            content_type=req.content_type.value,
            product_name=req.product_name,
            target_audience=req.target_audience or "General Audience",
            tone=req.tone.value,
            sense=req.sense or "Standard intended topic coverage",
            word_count=req.word_count,
            confirmed_outline=req.confirmed_outline,
            competitor_summary=req.competitor_summary or ""
        )

        # Then polish it and write the meta tags at the same time
        async def do_humanize():
            return await asyncio.to_thread(
                humanizer_chain.polish,
                language=req.language,
                region=req.region.value,
                target_audience=req.target_audience or "General Audience",
                draft_content=raw_draft
            )

        async def do_meta():
            if req.include_meta:
                return await asyncio.to_thread(
                    run_meta_chain,
                    language=req.language,
                    region=req.region.value,
                    content_type=req.content_type.value,
                    product_name=req.product_name,
                    final_content=raw_draft[:1500]
                )
            return (None, [])

        humanized_draft, (meta_description, meta_tags) = await asyncio.gather(
            do_humanize(),
            do_meta()
        )

        # Quick cleanup pass for leftover semicolons, dashes, etc.
        final_content, lint_report = linter.clean(humanized_draft)

        actual_words = len(final_content.split())

        return GenerateResponse(
            final_content=final_content,
            raw_draft=raw_draft,
            lint_report=lint_report,
            meta_description=meta_description,
            meta_tags=meta_tags,
            word_count_actual=actual_words,
            success=True
        )

generation_service = GenerationService()
