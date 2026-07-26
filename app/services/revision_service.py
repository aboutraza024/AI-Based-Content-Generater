import asyncio
from app.schemas.revise import ReviseRequest, ReviseResponse
from app.ai.langchain_chains.revision_chain import run_revision_chain
from app.ai.langchain_chains.humanization_chain import run_humanization_chain
from app.ai.langchain_chains.meta_chain import run_meta_chain
from app.utils.humanization_linter import linter
from app.core.logging import logger

class RevisionService:
    async def revise_content_async(self, req: ReviseRequest) -> ReviseResponse:
        logger.info(f"[Async Pipeline] Revising content for '{req.product_name}'...")

        # 1. Revision Chain non-blocking
        revised_raw = await asyncio.to_thread(
            run_revision_chain,
            language=req.language,
            region=req.region.value,
            content_type=req.content_type.value,
            product_name=req.product_name,
            target_audience=req.target_audience or "General Audience",
            confirmed_outline=req.confirmed_outline,
            previous_content=req.previous_content,
            revision_feedback=req.revision_feedback
        )

        # 2. Parallel Humanization & Meta execution
        async def do_humanize():
            return await asyncio.to_thread(
                run_humanization_chain,
                language=req.language,
                region=req.region.value,
                target_audience=req.target_audience or "General Audience",
                draft_content=revised_raw
            )

        async def do_meta():
            if req.include_meta:
                return await asyncio.to_thread(
                    run_meta_chain,
                    language=req.language,
                    region=req.region.value,
                    content_type=req.content_type.value,
                    product_name=req.product_name,
                    final_content=revised_raw[:1500]
                )
            return (None, [])

        humanized_revised, (meta_description, meta_tags) = await asyncio.gather(
            do_humanize(),
            do_meta()
        )

        # 3. Fast Deterministic Mechanical Linter Pass
        final_revised, lint_report = linter.lint_and_clean(humanized_revised)

        actual_words = len(final_revised.split())

        return ReviseResponse(
            revised_content=final_revised,
            lint_report=lint_report,
            meta_description=meta_description,
            meta_tags=meta_tags,
            word_count_actual=actual_words,
            success=True
        )

revision_service = RevisionService()
